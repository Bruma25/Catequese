# repositories/catequizandoRepository.py
from datetime import date
from typing import Optional
from uuid import uuid4

from infra.supabaseClient import get_supabase
from domain.catequizando import Catequizando
from domain.catequizandoResponsavel import CatequizandoResponsavel
from domain.historicoSacramental import HistoricoSacramental
from domain.responsavel import Responsavel
from domain.sacramento import Sacramento
from domain.tipoVinculoResponsavel import TipoVinculoResponsavel


class CatequizandoRepository:
    def __init__(self):
        self.db = get_supabase()
        self.table = "catequizando"

    def buscar_por_id(self, catequizando_id: str) -> Optional[Catequizando]:
        result = (
            self.db.table(self.table)
            .select(
                """
                id,
                nome,
                data_nascimento,
                endereco,
                telefone,
                email,
                observacoes,
                necessidade_especial,
                descricao_necessidade_especial,
                historico_sacramental(
                    id,
                    data_recebimento,
                    local,
                    observacoes,
                    sacramento(
                        id,
                        codigo,
                        nome_exibicao
                    )
                ),
                vinculos_responsaveis:catequizando_responsavel(
                    descricao_outro,
                    responsavel(
                        id,
                        nome,
                        email,
                        telefone,
                        usuario_id
                    ),
                    tipo_vinculo:tipo_vinculo_responsavel(
                        id,
                        codigo,
                        descricao
                    )
                )
                """
            )
            .eq("id", catequizando_id)
            .maybe_single()
            .execute()
        )

        data = self._extrair_data_optional(result)
        if not data:
            return None

        return self._from_row(data)

    def salvar(self, catequizando: Catequizando) -> Catequizando:
        payload = self._payload_catequizando(catequizando, incluir_id=True)

        result = (
            self.db.table(self.table)
            .insert(payload)
            .execute()
        )

        data = result.data[0] if result and result.data else None
        if not data:
            raise ValueError("Não foi possível salvar o catequizando.")

        return self._from_row(data)

    def editar(self, catequizando: Catequizando) -> Catequizando:
        payload = self._payload_catequizando(catequizando, incluir_id=False)

        result = (
            self.db.table(self.table)
            .update(payload)
            .eq("id", catequizando.id)
            .execute()
        )

        data = result.data[0] if result and result.data else None
        if not data:
            raise ValueError("Não foi possível editar o catequizando.")

        return self._from_row(data)

    def apagar(self, catequizando_id: str) -> bool:
        self.apagar_historico_sacramental(catequizando_id)
        self.apagar_vinculos_responsaveis(catequizando_id)

        result = (
            self.db.table(self.table)
            .delete()
            .eq("id", catequizando_id)
            .execute()
        )

        return bool(result.data)

    def salvar_com_dependencias(self, catequizando: Catequizando) -> Catequizando:
        self.salvar(catequizando)
        self.sincronizar_historico_sacramental(catequizando)
        self.sincronizar_vinculos_responsaveis(catequizando)
        return self.buscar_por_id(catequizando.id)

    def editar_totalmente_sincronizado(self, catequizando: Catequizando) -> Catequizando:
        self.editar(catequizando)
        self.sincronizar_historico_sacramental(catequizando)
        self.sincronizar_vinculos_responsaveis(catequizando)
        return self.buscar_por_id(catequizando.id)

    def sincronizar_historico_sacramental(self, catequizando: Catequizando) -> list[dict]:
        historicos = getattr(catequizando, "historico_sacramental", None)
        if historicos is None:
            historicos = getattr(catequizando, "historicos_sacramentais", [])

        historicos = historicos or []

        ids_atuais = [item.id for item in historicos if getattr(item, "id", None)]

        query_delete = (
            self.db.table("historico_sacramental")
            .delete()
            .eq("catequizando_id", catequizando.id)
        )

        if ids_atuais:
            query_delete = query_delete.not_.in_("id", ids_atuais)

        query_delete.execute()

        if not historicos:
            return []

        payload = []
        for item in historicos:
            historico_id = item.id if getattr(item, "id", None) else str(uuid4())

            payload.append({
                "id": historico_id,
                "catequizando_id": catequizando.id,
                "sacramento_id": item.sacramento.id,
                "data_recebimento": item.data_recebimento.isoformat() if item.data_recebimento else None,
                "local": item.local,
                "observacoes": item.observacoes,
            })

            if not getattr(item, "id", None):
                item.id = historico_id

        result = (
            self.db.table("historico_sacramental")
            .upsert(payload)
            .execute()
        )

        return result.data or []

    def sincronizar_vinculos_responsaveis(self, catequizando: Catequizando) -> list[dict]:
        vinculos = getattr(catequizando, "vinculos_responsaveis", None)
        if vinculos is None:
            vinculos = getattr(catequizando, "responsaveis", [])

        vinculos = vinculos or []

        self.apagar_vinculos_responsaveis(catequizando.id)

        if not vinculos:
            return []

        payload = []
        for vinculo in vinculos:
            vinculo.validar()

            payload.append({
                "catequizando_id": catequizando.id,
                "responsavel_id": vinculo.responsavel.id,
                "tipo_vinculo_id": vinculo.tipo_vinculo.id,
                "descricao_outro": vinculo.descricao_outro,
            })

        result = (
            self.db.table("catequizando_responsavel")
            .insert(payload)
            .execute()
        )

        return result.data or []

    def apagar_historico_sacramental(self, catequizando_id: str) -> bool:
        result = (
            self.db.table("historico_sacramental")
            .delete()
            .eq("catequizando_id", catequizando_id)
            .execute()
        )

        return result.data is not None

    def apagar_vinculos_responsaveis(self, catequizando_id: str) -> bool:
        result = (
            self.db.table("catequizando_responsavel")
            .delete()
            .eq("catequizando_id", catequizando_id)
            .execute()
        )

        return result.data is not None

    def _payload_catequizando(self, catequizando: Catequizando, incluir_id: bool = True) -> dict:
        payload = {
            "nome": catequizando.nome,
            "data_nascimento": catequizando.data_nascimento.isoformat() if catequizando.data_nascimento else None,
            "endereco": catequizando.endereco,
            "telefone": catequizando.telefone,
            "email": catequizando.email,
            "observacoes": catequizando.observacoes,
            "necessidade_especial": catequizando.necessidade_especial,
            "descricao_necessidade_especial": catequizando.descricao_necessidade_especial,
        }

        if incluir_id:
            payload["id"] = catequizando.id

        return payload

    def _extrair_data_optional(self, result):
        if result is None:
            return None

        if not hasattr(result, "data"):
            return None

        return result.data

    def _from_row(self, data: dict) -> Catequizando:
        catequizando = Catequizando(
            id=data["id"],
            nome=data["nome"],
            data_nascimento=date.fromisoformat(data["data_nascimento"]) if data.get("data_nascimento") else None,
            endereco=data.get("endereco"),
            telefone=data.get("telefone"),
            email=data.get("email"),
            observacoes=data.get("observacoes"),
            necessidade_especial=data.get("necessidade_especial", False),
            descricao_necessidade_especial=data.get("descricao_necessidade_especial"),
            vinculos_responsaveis=[],
            historico_sacramental=[],
        )

        for item in data.get("historico_sacramental", []):
            historico = self._montar_historico_sacramental(catequizando, item)
            catequizando.adicionar_historico_sacramental(historico)

        for item in data.get("vinculos_responsaveis", []):
            vinculo = self._montar_vinculo_responsavel(catequizando, item)
            catequizando.adicionar_vinculo_responsavel(vinculo)
            vinculo.responsavel.adicionar_vinculo(vinculo)

        return catequizando

    def _montar_historico_sacramental(self, catequizando: Catequizando, data: dict) -> HistoricoSacramental:
        sacramento_data = data["sacramento"]

        sacramento = Sacramento(
            id=sacramento_data["id"],
            codigo=sacramento_data["codigo"],
            nome_exibicao=sacramento_data["nome_exibicao"],
        )

        return HistoricoSacramental(
            id=data["id"],
            catequizando=catequizando,
            sacramento=sacramento,
            data_recebimento=date.fromisoformat(data["data_recebimento"]) if data.get("data_recebimento") else None,
            local=data.get("local"),
            observacoes=data.get("observacoes"),
        )

    def _montar_vinculo_responsavel(self, catequizando: Catequizando, data: dict) -> CatequizandoResponsavel:
        responsavel_data = data["responsavel"]
        tipo_vinculo_data = data["tipo_vinculo"]

        responsavel = Responsavel(
            id=responsavel_data["id"],
            nome=responsavel_data["nome"],
            email=responsavel_data.get("email"),
            telefone=responsavel_data.get("telefone"),
            usuario=None,
            vinculos=[],
        )

        tipo_vinculo = TipoVinculoResponsavel(
            id=tipo_vinculo_data["id"],
            codigo=tipo_vinculo_data["codigo"],
            descricao=tipo_vinculo_data["descricao"],
        )

        vinculo = CatequizandoResponsavel(
            catequizando=catequizando,
            responsavel=responsavel,
            tipo_vinculo=tipo_vinculo,
            descricao_outro=data.get("descricao_outro"),
        )

        vinculo.validar()
        return vinculo