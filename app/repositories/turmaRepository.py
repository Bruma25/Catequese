# repositories/turmaRepository.py
from typing import Optional, Callable

from app.infra.supabaseClient import get_supabase
from app.domain.turma import Turma
from app.domain.etapa import Etapa
from app.domain.localEncontro import LocalEncontro
from app.domain.catequista import Catequista
from app.domain.sacramento import Sacramento


class TurmaRepository:
    def __init__(self):
        self.db = get_supabase()
        self.table = "turma"

    def buscar_por_id(self, turma_id: str) -> Optional[Turma]:
        result = (
            self.db.table(self.table)
            .select(
                """
                id,
                nome_sistema,
                nome_exibicao,
                vagas_totais,
                ativa,
                ano_nasc_minimo,
                ano_nasc_maximo,
                etapa:etapa(
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
                ),
                local_encontro:local_encontro(
                    id,
                    codigo,
                    nome_exibicao
                ),
                catequistas:turma_catequista(
                    catequista:catequista(
                        id,
                        nome,
                        email,
                        telefone,
                        usuario_id
                    )
                )
                """
            )
            .eq("id", turma_id)
            .maybe_single()
            .execute()
        )

        data = self._extrair_data_optional(result)
        if not data:
            return None

        return self._montar_turma(data)

    def salvar(self, turma: Turma) -> Turma:
        self._validar_turma(turma)

        payload = self._to_payload(turma, incluir_id=True)

        result = (
            self.db.table(self.table)
            .insert(payload)
            .execute()
        )

        data = self._extrair_primeira_linha(result)
        if not data:
            raise ValueError("Não foi possível salvar a turma.")

        self._sincronizar_catequistas(turma)

        turma_salva = self.buscar_por_id(turma.id)
        if turma_salva is None:
            raise ValueError("A turma foi salva, mas não pôde ser recarregada.")

        return turma_salva

    def editar(self, turma: Turma) -> Turma:
        self._validar_turma(turma)

        payload = self._to_payload(turma, incluir_id=False)

        result = (
            self.db.table(self.table)
            .update(payload)
            .eq("id", turma.id)
            .execute()
        )

        data = self._extrair_primeira_linha(result)
        if not data:
            raise ValueError("Não foi possível editar a turma.")

        self._sincronizar_catequistas(turma)

        turma_editada = self.buscar_por_id(turma.id)
        if turma_editada is None:
            raise ValueError("A turma foi editada, mas não pôde ser recarregada.")

        return turma_editada

    def apagar(self, turma_id: str) -> bool:
        self._apagar_relacoes_catequistas(turma_id)

        result = (
            self.db.table(self.table)
            .delete()
            .eq("id", turma_id)
            .execute()
        )

        return bool(self._extrair_lista(result))

    def _validar_turma(self, turma: Turma) -> None:
        if turma is None:
            raise ValueError("A turma é obrigatória.")

        if turma.etapa is None:
            raise ValueError("A turma deve possuir etapa.")

        if hasattr(turma, "validar_requisitos") and callable(turma.validar_requisitos):
            turma.validar_requisitos()

        etapa = getattr(turma, "etapa", None)
        if etapa and hasattr(etapa, "validar_requisitos") and callable(etapa.validar_requisitos):
            etapa.validar_requisitos()

    def _to_payload(self, turma: Turma, incluir_id: bool = True) -> dict:
        payload = {
            "etapa_id": turma.etapa.id,
            "nome_sistema": turma.nome_sistema,
            "nome_exibicao": turma.nome_exibicao,
            "vagas_totais": turma.vagas_totais,
            "ativa": turma.ativa,
            "local_encontro_id": turma.local_encontro.id if turma.local_encontro else None,
            "ano_nasc_minimo": turma.ano_nasc_minimo,
            "ano_nasc_maximo": turma.ano_nasc_maximo,
        }

        if incluir_id:
            payload["id"] = turma.id

        return payload

    def _montar_turma(self, data: dict) -> Turma:
        etapa = self._montar_etapa(data["etapa"])
        local_encontro = self._montar_local_encontro(data.get("local_encontro"))

        turma = Turma(
            id=data["id"],
            etapa=etapa,
            nome_sistema=data["nome_sistema"],
            nome_exibicao=data.get("nome_exibicao"),
            vagas_totais=data["vagas_totais"],
            ativa=data.get("ativa", True),
            local_encontro=local_encontro,
            ano_nasc_minimo=data.get("ano_nasc_minimo"),
            ano_nasc_maximo=data.get("ano_nasc_maximo"),
            catequistas=[],
        )

        self._reconstituir_catequistas(
            turma=turma,
            itens=data.get("catequistas", []),
        )

        if hasattr(turma, "validar_requisitos") and callable(turma.validar_requisitos):
            turma.validar_requisitos()

        return turma

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

    def _montar_local_encontro(self, data: Optional[dict]) -> Optional[LocalEncontro]:
        if not data:
            return None

        return LocalEncontro(
            id=data["id"],
            codigo=data["codigo"],
            nome_exibicao=data["nome_exibicao"],
        )

    def _reconstituir_catequistas(self, turma: Turma, itens: list[dict]) -> None:
        adicionar = self._obter_adicionador(turma, "adicionar_catequista")
        colecao = getattr(turma, "catequistas")

        for item in itens:
            catequista_data = item.get("catequista")
            if not catequista_data:
                continue

            catequista = Catequista(
                id=catequista_data["id"],
                nome=catequista_data["nome"],
                email=catequista_data.get("email"),
                telefone=catequista_data.get("telefone"),
                usuario=None,
            )

            if adicionar:
                adicionar(catequista)
            else:
                colecao.append(catequista)

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

            sacramento = Sacramento(
                id=sacramento_data["id"],
                codigo=sacramento_data["codigo"],
                nome_exibicao=sacramento_data["nome_exibicao"],
            )

            if adicionar:
                adicionar(sacramento)
            else:
                colecao.append(sacramento)

    def _obter_adicionador(self, alvo, nome_metodo: str) -> Optional[Callable]:
        metodo = getattr(alvo, nome_metodo, None)
        if callable(metodo):
            return metodo
        return None

    def _sincronizar_catequistas(self, turma: Turma) -> None:
        (
            self.db.table("turma_catequista")
            .delete()
            .eq("turma_id", turma.id)
            .execute()
        )

        if not turma.catequistas:
            return

        payload = [
            {
                "turma_id": turma.id,
                "catequista_id": catequista.id,
            }
            for catequista in turma.catequistas
        ]

        (
            self.db.table("turma_catequista")
            .insert(payload)
            .execute()
        )

    def _apagar_relacoes_catequistas(self, turma_id: str) -> None:
        (
            self.db.table("turma_catequista")
            .delete()
            .eq("turma_id", turma_id)
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