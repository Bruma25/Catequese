# repositories/etapaRepository.py
from typing import Optional, Callable

from infra.supabaseClient import get_supabase
from domain.etapa import Etapa
from domain.sacramento import Sacramento


class EtapaRepository:
    def __init__(self):
        self.db = get_supabase()
        self.table = "etapa"

    def buscar_por_id(self, etapa_id: str) -> Optional[Etapa]:
        result = (
            self.db.table(self.table)
            .select(
                """
                id,
                nome,
                descricao,
                ano_nasc_minimo,
                ano_nasc_maximo,
                sacramentos_requeridos:etapa_sacramento_requerido(
                    sacramento:sacramento(
                        id,
                        codigo,
                        nome_exibicao
                    )
                ),
                sacramentos_proibidos:etapa_sacramento_proibido(
                    sacramento:sacramento(
                        id,
                        codigo,
                        nome_exibicao
                    )
                )
                """
            )
            .eq("id", etapa_id)
            .maybe_single()
            .execute()
        )

        data = self._extrair_data_optional(result)
        if not data:
            return None

        return self._montar_etapa(data)

    def salvar(self, etapa: Etapa) -> Etapa:
        self._validar_etapa(etapa)

        payload = self._to_payload(etapa, incluir_id=True)

        result = (
            self.db.table(self.table)
            .insert(payload)
            .execute()
        )

        data = self._extrair_primeira_linha(result)
        if not data:
            raise ValueError("Não foi possível salvar a etapa.")

        self._sincronizar_sacramentos_requeridos(etapa)
        self._sincronizar_sacramentos_proibidos(etapa)

        etapa_salva = self.buscar_por_id(etapa.id)
        if etapa_salva is None:
            raise ValueError("A etapa foi salva, mas não pôde ser recarregada.")

        return etapa_salva

    def editar(self, etapa: Etapa) -> Etapa:
        self._validar_etapa(etapa)

        payload = self._to_payload(etapa, incluir_id=False)

        result = (
            self.db.table(self.table)
            .update(payload)
            .eq("id", etapa.id)
            .execute()
        )

        data = self._extrair_primeira_linha(result)
        if not data:
            raise ValueError("Não foi possível editar a etapa.")

        self._sincronizar_sacramentos_requeridos(etapa)
        self._sincronizar_sacramentos_proibidos(etapa)

        etapa_editada = self.buscar_por_id(etapa.id)
        if etapa_editada is None:
            raise ValueError("A etapa foi editada, mas não pôde ser recarregada.")

        return etapa_editada

    def apagar(self, etapa_id: str) -> bool:
        self._apagar_relacoes_sacramentos(etapa_id)

        result = (
            self.db.table(self.table)
            .delete()
            .eq("id", etapa_id)
            .execute()
        )

        return bool(self._extrair_lista(result))

    def _validar_etapa(self, etapa: Etapa) -> None:
        if etapa is None:
            raise ValueError("A etapa é obrigatória.")

        if hasattr(etapa, "validar_requisitos") and callable(etapa.validar_requisitos):
            etapa.validar_requisitos()

    def _to_payload(self, etapa: Etapa, incluir_id: bool = True) -> dict:
        payload = {
            "nome": etapa.nome,
            "descricao": etapa.descricao,
            "ano_nasc_minimo": etapa.ano_nasc_minimo,
            "ano_nasc_maximo": etapa.ano_nasc_maximo,
        }

        if incluir_id:
            payload["id"] = etapa.id

        return payload

    def _montar_etapa(self, data: dict) -> Etapa:
        etapa = Etapa(
            id=data["id"],
            nome=data["nome"],
            descricao=data.get("descricao"),
            ano_nasc_minimo=data.get("ano_nasc_minimo"),
            ano_nasc_maximo=data.get("ano_nasc_maximo"),
            sacramentos_requeridos=[],
            sacramentos_proibidos=[],
        )

        self._reconstituir_sacramentos(
            etapa=etapa,
            itens=data.get("sacramentos_requeridos", []),
            nome_metodo_preferencial="adicionar_sacramento_requerido",
            colecao_fallback="sacramentos_requeridos",
        )

        self._reconstituir_sacramentos(
            etapa=etapa,
            itens=data.get("sacramentos_proibidos", []),
            nome_metodo_preferencial="adicionar_sacramento_proibido",
            colecao_fallback="sacramentos_proibidos",
        )

        if hasattr(etapa, "validar_requisitos") and callable(etapa.validar_requisitos):
            etapa.validar_requisitos()

        return etapa

    def _reconstituir_sacramentos(
        self,
        etapa: Etapa,
        itens: list[dict],
        nome_metodo_preferencial: str,
        colecao_fallback: str,
    ) -> None:
        adicionar = self._obter_adicionador(etapa, nome_metodo_preferencial)
        colecao = getattr(etapa, colecao_fallback)

        for item in itens:
            sacramento_data = item.get("sacramento")
            if not sacramento_data:
                continue

            sacramento = self._montar_sacramento(sacramento_data)

            if adicionar:
                adicionar(sacramento)
            else:
                colecao.append(sacramento)

    def _obter_adicionador(self, etapa: Etapa, nome_metodo: str) -> Optional[Callable]:
        metodo = getattr(etapa, nome_metodo, None)
        if callable(metodo):
            return metodo
        return None

    def _montar_sacramento(self, data: dict) -> Sacramento:
        return Sacramento(
            id=data["id"],
            codigo=data["codigo"],
            nome_exibicao=data["nome_exibicao"],
        )

    def _sincronizar_sacramentos_requeridos(self, etapa: Etapa) -> None:
        (
            self.db.table("etapa_sacramento_requerido")
            .delete()
            .eq("etapa_id", etapa.id)
            .execute()
        )

        if not etapa.sacramentos_requeridos:
            return

        payload = [
            {
                "etapa_id": etapa.id,
                "sacramento_id": sacramento.id,
            }
            for sacramento in etapa.sacramentos_requeridos
        ]

        (
            self.db.table("etapa_sacramento_requerido")
            .insert(payload)
            .execute()
        )

    def _sincronizar_sacramentos_proibidos(self, etapa: Etapa) -> None:
        (
            self.db.table("etapa_sacramento_proibido")
            .delete()
            .eq("etapa_id", etapa.id)
            .execute()
        )

        if not etapa.sacramentos_proibidos:
            return

        payload = [
            {
                "etapa_id": etapa.id,
                "sacramento_id": sacramento.id,
            }
            for sacramento in etapa.sacramentos_proibidos
        ]

        (
            self.db.table("etapa_sacramento_proibido")
            .insert(payload)
            .execute()
        )

    def _apagar_relacoes_sacramentos(self, etapa_id: str) -> None:
        (
            self.db.table("etapa_sacramento_requerido")
            .delete()
            .eq("etapa_id", etapa_id)
            .execute()
        )

        (
            self.db.table("etapa_sacramento_proibido")
            .delete()
            .eq("etapa_id", etapa_id)
            .execute()
        )

    def _extrair_primeira_linha(self, result) -> Optional[dict]:
        data = self._extrair_lista(result)
        return data[0] if data else None

    def _extrair_lista(self, result) -> list[dict]:
        if result is None or not hasattr(result, "data") or result.data is None:
            return []
        return result.data

    def _extrair_data_optional(self, result) -> Optional[dict]:
        if result is None or not hasattr(result, "data"):
            return None
        return result.data