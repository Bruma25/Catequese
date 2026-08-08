# repositories/inscricaoRepository.py
from datetime import datetime, date
from typing import Optional, Any, List

from app.domain.catequizando import Catequizando
from app.domain.responsavel import Responsavel
from app.domain.etapa import Etapa
from app.domain.inscricao import Inscricao
from app.domain.statusInscricao import StatusInscricao
from app.domain.turma import Turma
from app.domain.usuario import Usuario
from app.domain.sacramento import Sacramento
from app.repositories.usuarioRepository import UsuarioRepository
from app.infra.supabaseClient import get_supabase


class InscricaoRepository:
    def __init__(self):
        self.db = get_supabase()
        self.table = "inscricao"
        self.usuarioRepository = UsuarioRepository()

    def salvar(self, inscricao: Inscricao) -> Inscricao:
        self._validar_inscricao_para_persistencia(inscricao)

        payload = self._to_payload(inscricao, incluir_id=True)

        result = (
            self.db.table(self.table)
            .insert(payload)
            .execute()
        )

        data = self._extrair_primeira_linha(result)
        if not data:
            raise ValueError("Não foi possível salvar a inscrição.")

        inscricao_salva = self.buscar_por_id(inscricao.id)
        if inscricao_salva is None:
            raise ValueError("A inscrição foi salva, mas não pôde ser recarregada.")

        return inscricao_salva

    def editar(self, inscricao: Inscricao) -> Inscricao:
        self._validar_inscricao_para_persistencia(inscricao)

        payload = self._to_payload(inscricao, incluir_id=False)

        result = (
            self.db.table(self.table)
            .update(payload)
            .eq("id", inscricao.id)
            .execute()
        )

        data = self._extrair_primeira_linha(result)
        if not data:
            raise ValueError("Não foi possível editar a inscrição.")

        inscricao_editada = self.buscar_por_id(inscricao.id)
        if inscricao_editada is None:
            raise ValueError("A inscrição foi editada, mas não pôde ser recarregada.")

        return inscricao_editada

    def apagar(self, inscricao_id: str) -> bool:
        result = (
            self.db.table(self.table)
            .delete()
            .eq("id", inscricao_id)
            .execute()
        )

        return bool(self._extrair_lista(result))

    def buscar_por_id(self, inscricao_id: str) -> Optional[Inscricao]:
        return self._buscar_por_id(inscricao_id=inscricao_id, enriquecer_override=False)

    def buscar_por_id_com_override_enriquecido(self, inscricao_id: str) -> Optional[Inscricao]:
        return self._buscar_por_id(inscricao_id=inscricao_id, enriquecer_override=True)

    def _buscar_por_id(self, inscricao_id: str, enriquecer_override: bool) -> Optional[Inscricao]:
        result = (
            self.db.table(self.table)
            .select("""
                id,
                termo_assinado,
                data_inscricao,
                quer_mesma_turma_que_irmao,
                referencia_irmao,
                observacao_responsavel,
                override_idade,
                motivo_override,
                catequizando:catequizando_id (
                    id,
                    nome,
                    data_nascimento,
                    observacoes,
                    endereco,
                    telefone,
                    email,
                    necessidade_especial,
                    descricao_necessidade_especial
                ),
                responsavel:responsavel_id (
                    id,
                    nome,
                    email,
                    telefone,
                    usuario_id
                ),
                etapa:etapa_id (
                    id,
                    nome,
                    descricao,
                    ano_nasc_minimo,
                    ano_nasc_maximo,
                    sacramentos_requeridos:etapa_sacramento_requerido (
                        sacramento:sacramento (
                            id,
                            codigo,
                            nome_exibicao
                        )
                    ),
                    sacramentos_proibidos:etapa_sacramento_proibido (
                        sacramento:sacramento (
                            id,
                            codigo,
                            nome_exibicao
                        )
                    )
                ),
                turma:turma_id (
                    id,
                    nome_sistema,
                    nome_exibicao,
                    vagas_totais,
                    ativa,
                    ano_nasc_minimo,
                    ano_nasc_maximo
                ),
                status:status_id (
                    id,
                    codigo,
                    descricao
                ),
                usuario_override:usuario_override_id (
                    id,
                    nome,
                    email
                )
            """)
            .eq("id", inscricao_id)
            .maybe_single()
            .execute()
        )

        data = self._extrair_data_optional(result)
        if not data:
            return None

        return self._montar_inscricao(data, enriquecer_override=enriquecer_override)

    def _to_payload(self, inscricao: Inscricao, incluir_id: bool = True) -> dict:
        payload = {
            "catequizando_id": inscricao.catequizando.id,
            "responsavel_id": inscricao.responsavel.id,
            "etapa_id": inscricao.etapa.id,
            "turma_id": inscricao.turma.id if inscricao.turma else None,
            "status_id": inscricao.status.id,
            "termo_assinado": inscricao.termo_assinado,
            "data_inscricao": self._datetime_to_iso(inscricao.data_inscricao),
            "quer_mesma_turma_que_irmao": inscricao.quer_mesma_turma_que_irmao,
            "referencia_irmao": inscricao.referencia_irmao,
            "observacao_responsavel": inscricao.observacao_responsavel,
            "override_idade": inscricao.override_idade,
            "motivo_override": inscricao.motivo_override,
            "usuario_override_id": inscricao.usuario_override.id if inscricao.usuario_override else None,
        }

        if incluir_id:
            payload["id"] = inscricao.id

        return payload

    def _validar_inscricao_para_persistencia(self, inscricao: Inscricao) -> None:
        if inscricao is None:
            raise ValueError("A inscrição é obrigatória.")

        if inscricao.catequizando is None:
            raise ValueError("A inscrição deve possuir catequizando.")

        if inscricao.responsavel is None:
            raise ValueError("A inscrição deve possuir responsável.")

        if inscricao.etapa is None:
            raise ValueError("A inscrição deve possuir etapa.")

        if inscricao.status is None:
            raise ValueError("A inscrição deve possuir status.")

        if hasattr(inscricao, "turma") and inscricao.turma is not None:
            if hasattr(inscricao.turma, "etapa") and inscricao.turma.etapa is not None:
                if inscricao.turma.etapa.id != inscricao.etapa.id:
                    raise ValueError("A turma da inscrição deve pertencer à mesma etapa da inscrição.")

    def _montar_inscricao(self, data: dict, enriquecer_override: bool) -> Inscricao:
        catequizando = self._montar_catequizando(data["catequizando"])
        responsavel = self._montar_responsavel(data["responsavel"])
        etapa = self._montar_etapa(data["etapa"])
        turma = self._montar_turma(data.get("turma"), etapa)
        status = self._montar_status(data["status"])
        usuario_override = self._montar_usuario_override(
            data.get("usuario_override"),
            enriquecer_override=enriquecer_override,
        )

        return Inscricao(
            id=data["id"],
            catequizando=catequizando,
            responsavel=responsavel,
            etapa=etapa,
            status=status,
            data_inscricao=self._parse_datetime(data.get("data_inscricao")),
            turma=turma,
            termo_assinado=data.get("termo_assinado", False),
            quer_mesma_turma_que_irmao=data.get("quer_mesma_turma_que_irmao", False),
            referencia_irmao=data.get("referencia_irmao"),
            observacao_responsavel=data.get("observacao_responsavel"),
            override_idade=data.get("override_idade", False),
            motivo_override=data.get("motivo_override"),
            usuario_override=usuario_override,
        )

    def _montar_catequizando(self, data: dict) -> Catequizando:
        return Catequizando(
            id=data["id"],
            nome=data["nome"],
            data_nascimento=self._parse_date(data["data_nascimento"]),
            observacoes=data.get("observacoes"),
            endereco=data.get("endereco"),
            telefone=data.get("telefone"),
            email=data.get("email"),
            necessidade_especial=data.get("necessidade_especial", False),
            descricao_necessidade_especial=data.get("descricao_necessidade_especial"),
        )

    def _montar_responsavel(self, data: dict) -> Responsavel:
        return Responsavel(
            id=data["id"],
            nome=data["nome"],
            email=data.get("email"),
            telefone=data.get("telefone"),
            usuario=None,
            vinculos=[],
        )

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

        for item in data.get("sacramentos_requeridos", []):
            sacramento_data = item.get("sacramento")
            if not sacramento_data:
                continue

            sacramento = self._montar_sacramento(sacramento_data)
            adicionar = getattr(etapa, "adicionar_sacramento_requerido", None)
            if callable(adicionar):
                adicionar(sacramento)
            else:
                etapa.sacramentos_requeridos.append(sacramento)

        for item in data.get("sacramentos_proibidos", []):
            sacramento_data = item.get("sacramento")
            if not sacramento_data:
                continue

            sacramento = self._montar_sacramento(sacramento_data)
            adicionar = getattr(etapa, "adicionar_sacramento_proibido", None)
            if callable(adicionar):
                adicionar(sacramento)
            else:
                etapa.sacramentos_proibidos.append(sacramento)

        if hasattr(etapa, "validar_requisitos") and callable(etapa.validar_requisitos):
            etapa.validar_requisitos()

        return etapa

    def _montar_sacramento(self, data: dict) -> Sacramento:
        return Sacramento(
            id=data["id"],
            codigo=data["codigo"],
            nome_exibicao=data["nome_exibicao"],
        )

    def _montar_turma(self, data: Optional[dict], etapa: Etapa) -> Optional[Turma]:
        if not data:
            return None

        return Turma(
            id=data["id"],
            etapa=etapa,
            nome_sistema=data["nome_sistema"],
            nome_exibicao=data.get("nome_exibicao"),
            vagas_totais=data["vagas_totais"],
            ativa=data.get("ativa", True),
            local_encontro=None,
            ano_nasc_minimo=data.get("ano_nasc_minimo"),
            ano_nasc_maximo=data.get("ano_nasc_maximo"),
            catequistas=[],
        )

    def _montar_status(self, data: dict) -> StatusInscricao:
        return StatusInscricao(
            id=data["id"],
            codigo=data["codigo"],
            descricao=data["descricao"],
        )

    def _montar_usuario_override(self, data: Optional[dict], enriquecer_override: bool) -> Optional[Usuario]:
        if not data:
            return None

        if enriquecer_override:
            return self.usuarioRepository.buscar_por_id(data["id"])

        return Usuario(
            id=data["id"],
            nome=data.get("nome"),
            email=data.get("email"),
            papeis=[],
        )

    def _extrair_primeira_linha(self, result) -> Optional[dict[str, Any]]:
        data = self._extrair_lista(result)
        return data[0] if data else None

    def _extrair_lista(self, result) -> list[dict[str, Any]]:
        if result is None or not hasattr(result, "data") or result.data is None:
            return []
        return result.data

    def _extrair_data_optional(self, result) -> Optional[dict]:
        if result is None or not hasattr(result, "data"):
            return None
        return result.data

    def _parse_date(self, valor):
        if valor is None:
            return None

        if isinstance(valor, date):
            return valor

        return date.fromisoformat(valor)

    def _parse_datetime(self, valor):
        if valor is None:
            return None

        if isinstance(valor, datetime):
            return valor

        return datetime.fromisoformat(valor.replace("Z", "+00:00"))

    def _datetime_to_iso(self, valor):
        if valor is None:
            return None

        if isinstance(valor, datetime):
            return valor.isoformat()

        return valor

    def listar_todos(self) -> List[dict]:
        """Lista todas as inscrições (apenas dados básicos, sem enriquecimento completo)."""
        result = (
            self.db.table(self.table)
            .select("""
                id,
                termo_assinado,
                data_inscricao,
                catequizando:catequizando_id (
                    id,
                    nome
                ),
                responsavel:responsavel_id (
                    id,
                    nome
                ),
                etapa:etapa_id (
                    id,
                    nome
                ),
                status:status_id (
                    id,
                    codigo
                )
            """)
            .execute()
        )

        data = self._extrair_lista(result)

        # Transformar para formato simplificado
        inscricoes = []
        for item in data:
            inscricoes.append({
                "id": item["id"],
                "catequizando_nome": item["catequizando"]["nome"] if item.get("catequizando") else None,
                "responsavel_nome": item["responsavel"]["nome"] if item.get("responsavel") else None,
                "etapa_id": item["etapa"]["id"] if item.get("etapa") else None,
                "status_id": item["status"]["id"] if item.get("status") else None,
                "created_at": item.get("data_inscricao")
            })

        return inscricoes

    def listar_etapas(self) -> List[dict]:
        """Lista todas as etapas disponíveis."""
        result = (
            self.db.table("etapa")
            .select("""
                id,
                nome,
                descricao,
                ano_nasc_minimo,
                ano_nasc_maximo,
                sacramentos_requeridos:etapa_sacramento_requerido (
                    sacramento_id
                )
            """)
            .order("nome")
            .execute()
        )

        data = self._extrair_lista(result)

        etapas = []
        for item in data:
            sacramentos_ids = [
                sr["sacramento_id"]
                for sr in item.get("sacramentos_requeridos", [])
            ]

            etapas.append({
                "id": item["id"],
                "nome": item["nome"],
                "ano_nascimento_min": item.get("ano_nasc_minimo"),
                "ano_nascimento_max": item.get("ano_nasc_maximo"),
                "sacramentos_requeridos": sacramentos_ids
            })

        return etapas

    def buscar_inscricao_completa(self, inscricao_id: str) -> Optional[dict]:
        """Busca uma inscrição completa (com todos os relacionamentos)."""
        inscricao = self.buscar_por_id(inscricao_id)

        if not inscricao:
            return None

        # Extrair dados em formato simplificado para API
        return {
            "id": inscricao.id,
            "catequizando_nome": inscricao.catequizando.nome,
            "responsavel_nome": inscricao.responsavel.nome,
            "etapa_id": inscricao.etapa.id,
            "status_id": inscricao.status.id,
            "created_at": str(inscricao.data_inscricao) if inscricao.data_inscricao else None
        }