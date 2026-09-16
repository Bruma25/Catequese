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
from app.domain.localEncontro import LocalEncontro
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

    def buscar_turmas_por_etapa(self, etapa_id: str) -> List[Turma]:
        """
        Retorna todas as turmas de uma etapa.
        Usado para verificar vagas no ato da inscrição.
        """
        result = (
            self.db.table("turma")
            .select("""
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
                    ano_nasc_maximo
                ),
                local_encontro:local_encontro_id(
                    id,
                    codigo,
                    nome_exibicao
                )
            """)
            .eq("etapa_id", etapa_id)
            .execute()
        )

        data = self._extrair_lista(result)

        turmas = []
        for item in data:
            etapa = self._montar_etapa_simplificada(item["etapa"])
            local_encontro = self._montar_local_encontro(item.get("local_encontro"))

            turma = Turma(
                id=item["id"],
                etapa=etapa,
                nome_sistema=item["nome_sistema"],
                nome_exibicao=item.get("nome_exibicao"),
                vagas_totais=item["vagas_totais"],
                ativa=item.get("ativa", True),
                local_encontro=local_encontro,
                ano_nasc_minimo=item.get("ano_nasc_minimo"),
                ano_nasc_maximo=item.get("ano_nasc_maximo"),
                catequistas=[],
            )
            turmas.append(turma)

        return turmas

    def _montar_local_encontro(self, data: Optional[dict]) -> Optional[LocalEncontro]:
        if not data:
            return None

        from app.domain.localEncontro import LocalEncontro

        return LocalEncontro(
            id=data["id"],
            codigo=data["codigo"],
            nome_exibicao=data["nome_exibicao"],
        )

    def contar_inscricoes_por_etapa(
            self,
            etapa_id: str,
            excluir_status_codigo: Optional[str] = "cancelada",
    ) -> int:
        """
        Conta o número de inscrições de uma etapa,
        excluindo as que possuem o status com o código informado.
        Por padrão, exclui as canceladas.
        """
        # Primeiro busca o ID do status a excluir
        status_id_excluir = None
        if excluir_status_codigo:
            result = (
                self.db.table("status_inscricao")
                .select("id")
                .eq("codigo", excluir_status_codigo)
                .limit(1)
                .execute()
            )

            data = self._extrair_lista(result)
            if data and len(data) > 0:
                status_id_excluir = data[0]["id"]

        # Conta inscrições da etapa
        query = (
            self.db.table(self.table)
            .select("id", count="exact")
            .eq("etapa_id", etapa_id)
        )

        # Exclui pelo status_id se encontrou
        if status_id_excluir is not None:
            query = query.neq("status_id", status_id_excluir)

        result = query.execute()

        if result is None or not hasattr(result, "count") or result.count is None:
            return 0

        return result.count

    def buscar_dados_para_verificar_vagas(
            self,
            etapa_id: str,
            catequizando: Catequizando,
    ) -> tuple[List[Turma], int]:
        """
        Retorna:
          - lista de turmas da etapa;
          - total de inscrições da etapa (exceto canceladas).
        Usado pelo ServicoInscricao para verificar vagas no ato da inscrição.
        """
        turmas = self.buscar_turmas_por_etapa(etapa_id)
        total_inscricoes = self.contar_inscricoes_por_etapa(etapa_id, excluir_status_codigo="cancelada")

        return turmas, total_inscricoes

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
                local_encontro_id,
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
                    ano_nasc_maximo, 
                    local_encontro:local_encontro_id ( id, codigo, nome_exibicao )
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
            "local_encontro_id": inscricao.local_encontro_id,
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
            local_encontro_id=data.get("local_encontro_id"),
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

    def _montar_etapa_simplificada(self, data: dict) -> Etapa:
        """Versão simplificada para montar etapa sem sacramentos, usada em turmas."""
        return Etapa(
            id=data["id"],
            nome=data["nome"],
            descricao=data.get("descricao"),
            ano_nasc_minimo=data.get("ano_nasc_minimo"),
            ano_nasc_maximo=data.get("ano_nasc_maximo"),
            sacramentos_requeridos=[],
            sacramentos_proibidos=[],
        )

    def _montar_sacramento(self, data: dict) -> Sacramento:
        return Sacramento(
            id=data["id"],
            codigo=data["codigo"],
            nome_exibicao=data["nome_exibicao"],
        )

    def _montar_turma(self, data: Optional[dict], etapa: Etapa) -> Optional[Turma]:
        if not data:
            return None

        local_encontro = self._montar_local_encontro( data.get("local_encontro") )

        return Turma(
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
                turma_id,
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

        inscricoes = []
        for item in data:
            inscricoes.append({
                "id": item["id"],
                "catequizando_nome": item["catequizando"]["nome"] if item.get("catequizando") else None,
                "responsavel_nome": item["responsavel"]["nome"] if item.get("responsavel") else None,
                "etapa_id": item["etapa"]["id"] if item.get("etapa") else None,
                "status_id": item["status"]["id"] if item.get("status") else None,
                "turma_id": item.get("turma_id"),
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
                sacramentos_requeridos:etapa_sacramento_requerido (sacramento_id),
                sacramentos_proibidos:etapa_sacramento_proibido (sacramento_id)
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

            sacramentos_proibidos_ids = [
                sp["sacramento_id"]
                for sp in item.get("sacramentos_proibidos", [])
            ]

            etapas.append({
                "id": item["id"],
                "nome": item["nome"],
                "ano_nascimento_min": item.get("ano_nasc_minimo"),
                "ano_nascimento_max": item.get("ano_nasc_maximo"),
                "sacramentos_requeridos": sacramentos_ids,
                "sacramentos_proibidos": sacramentos_proibidos_ids
            })

        return etapas

    def buscar_inscricao_completa(self, inscricao_id: str) -> Optional[dict]:
        """Busca uma inscrição completa (com todos os relacionamentos)."""
        inscricao = self.buscar_por_id(inscricao_id)

        if not inscricao:
            return None

        return {
            "id": inscricao.id,
            "catequizando_nome": inscricao.catequizando.nome,
            "responsavel_nome": inscricao.responsavel.nome,
            "etapa_id": inscricao.etapa.id,
            "status_id": inscricao.status.id,
            "created_at": str(inscricao.data_inscricao) if inscricao.data_inscricao else None
        }

    def listar_por_etapa(self, etapa_id: str) -> List[dict]:
        """Lista todas as inscrições de uma etapa específica."""
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
                ),
                turma:turma_id (
                    id,
                    nome_sistema,
                    nome_exibicao
                )
            """)
            .eq("etapa_id", etapa_id)
            .order("data_inscricao", desc=True)
            .execute()
        )

        data = self._extrair_lista(result)

        inscricoes = []
        for item in data:
            inscricoes.append({
                "id": item["id"],
                "catequizando_nome": item["catequizando"]["nome"] if item.get("catequizando") else None,
                "responsavel_nome": item["responsavel"]["nome"] if item.get("responsavel") else None,
                "etapa_id": item["etapa"]["id"] if item.get("etapa") else None,
                "etapa_nome": item["etapa"]["nome"] if item.get("etapa") else None,
                "status_id": item["status"]["id"] if item.get("status") else None,
                "status_codigo": item["status"]["codigo"] if item.get("status") else None,
                "turma_id": item["turma"]["id"] if item.get("turma") else None,
                "turma_nome": item["turma"]["nome_exibicao"] if item.get("turma") else None,
                "termo_assinado": item.get("termo_assinado", False),
                "created_at": item.get("data_inscricao")
            })

        return inscricoes

    def listar_por_status(self, status_codigo: str) -> List[dict]:
        """Lista todas as inscrições com um status específico."""
        # Primeiro busca o ID do status
        result_status = (
            self.db.table("status_inscricao")
            .select("id")
            .eq("codigo", status_codigo)
            .limit(1)
            .execute()
        )

        data_status = self._extrair_lista(result_status)
        if not data_status or len(data_status) == 0:
            return []

        status_id = data_status[0]["id"]

        # Busca inscrições com esse status
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
                ),
                turma:turma_id (
                    id,
                    nome_sistema,
                    nome_exibicao
                )
            """)
            .eq("status_id", status_id)
            .order("data_inscricao", desc=True)
            .execute()
        )

        data = self._extrair_lista(result)

        inscricoes = []
        for item in data:
            inscricoes.append({
                "id": item["id"],
                "catequizando_nome": item["catequizando"]["nome"] if item.get("catequizando") else None,
                "responsavel_nome": item["responsavel"]["nome"] if item.get("responsavel") else None,
                "etapa_id": item["etapa"]["id"] if item.get("etapa") else None,
                "etapa_nome": item["etapa"]["nome"] if item.get("etapa") else None,
                "status_id": item["status"]["id"] if item.get("status") else None,
                "status_codigo": item["status"]["codigo"] if item.get("status") else None,
                "turma_id": item["turma"]["id"] if item.get("turma") else None,
                "turma_nome": item["turma"]["nome_exibicao"] if item.get("turma") else None,
                "termo_assinado": item.get("termo_assinado", False),
                "created_at": item.get("data_inscricao")
            })

        return inscricoes

    def listar_pendentes_distribuicao(self) -> List[dict]:
        """Lista todas as inscrições pendentes de distribuição em turma."""
        return self.listar_por_status("pendente_distribuicao")

    def contar_vagas_ocupadas_por_turma(self, turma_id: str) -> int:
        """Conta quantas inscrições confirmadas existem em uma turma."""
        # Busca status confirmada e lista de espera
        result_status = (
            self.db.table("status_inscricao")
            .select("id")
            .in_("codigo", ["confirmada", "lista_espera"])
            .execute()
        )

        data_status = self._extrair_lista(result_status)
        if not data_status:
            return 0

        status_ids = [s["id"] for s in data_status]

        result = (
            self.db.table(self.table)
            .select("id", count="exact")
            .eq("turma_id", turma_id)
            .in_("status_id", status_ids)
            .execute()
        )

        if result is None or not hasattr(result, "count") or result.count is None:
            return 0

        return result.count

    def buscar_com_detalhes_completos(self, inscricao_id: str) -> Optional[dict]:
        """Busca uma inscrição com todos os detalhes e relacionamentos."""
        inscricao = self.buscar_por_id_com_override_enriquecido(inscricao_id)

        if not inscricao:
            return None

        # Busca documentos da inscrição
        documentos = []
        try:
            from app.repositories.documentoInscricaoRepository import DocumentoInscricaoRepository
            repo_documentos = DocumentoInscricaoRepository()
            documentos_db = repo_documentos.listar_por_inscricao(inscricao_id)
            documentos = [
                {
                    "id": d.id,
                    "tipo_documento": d.tipo_documento,
                    "nome_original": d.nome_original,
                    "caminho_storage": d.caminho_storage,
                    "status_validacao": d.status_validacao,
                    "created_at": str(d.created_at) if d.created_at else None
                }
                for d in documentos_db
            ]
        except:
            pass

        return {
            "id": inscricao.id,
            "catequizando": {
                "id": inscricao.catequizando.id,
                "nome": inscricao.catequizando.nome,
                "data_nascimento": str(
                    inscricao.catequizando.data_nascimento) if inscricao.catequizando.data_nascimento else None,
                "observacoes": inscricao.catequizando.observacoes,
                "endereco": inscricao.catequizando.endereco,
                "telefone": inscricao.catequizando.telefone,
                "email": inscricao.catequizando.email,
                "necessidade_especial": inscricao.catequizando.necessidade_especial,
                "descricao_necessidade_especial": inscricao.catequizando.descricao_necessidade_especial
            },
            "responsavel": {
                "id": inscricao.responsavel.id,
                "nome": inscricao.responsavel.nome,
                "email": inscricao.responsavel.email,
                "telefone": inscricao.responsavel.telefone
            },
            "etapa": {
                "id": inscricao.etapa.id,
                "nome": inscricao.etapa.nome,
                "descricao": inscricao.etapa.descricao
            },
            "turma": {
                "id": inscricao.turma.id,
                "nome_sistema": inscricao.turma.nome_sistema,
                "nome_exibicao": inscricao.turma.nome_exibicao
            } if inscricao.turma else None,
            "status": {
                "id": inscricao.status.id,
                "codigo": inscricao.status.codigo,
                "descricao": inscricao.status.descricao
            },
            "termo_assinado": inscricao.termo_assinado,
            "data_inscricao": str(inscricao.data_inscricao) if inscricao.data_inscricao else None,
            "quer_mesma_turma_que_irmao": inscricao.quer_mesma_turma_que_irmao,
            "referencia_irmao": inscricao.referencia_irmao,
            "observacao_responsavel": inscricao.observacao_responsavel,
            "local_encontro_id": inscricao.local_encontro_id,
            "override_idade": inscricao.override_idade,
            "motivo_override": inscricao.motivo_override,
            "usuario_override": {
                "id": inscricao.usuario_override.id,
                "nome": inscricao.usuario_override.nome,
                "email": inscricao.usuario_override.email
            } if inscricao.usuario_override else None,
            "documentos": documentos
        }

    def atualizar_status(self, inscricao_id: str, status_id: int) -> Optional[Inscricao]:
        """Atualiza o status de uma inscrição."""
        inscricao = self.buscar_por_id(inscricao_id)

        if not inscricao:
            return None

        # Busca o novo status
        result = (
            self.db.table("status_inscricao")
            .select("*")
            .eq("id", status_id)
            .maybe_single()
            .execute()
        )

        data = self._extrair_data_optional(result)
        if not data:
            raise ValueError(f"Status {status_id} não encontrado")

        novo_status = StatusInscricao(
            id=data["id"],
            codigo=data["codigo"],
            descricao=data["descricao"]
        )

        inscricao.definir_status(novo_status)
        return self.editar(inscricao)

    def atribuir_turma(self, inscricao_id: str, turma_id: str) -> Optional[Inscricao]:
        """Atribui uma turma a uma inscrição."""
        from app.repositories.turmaRepository import TurmaRepository

        inscricao = self.buscar_por_id(inscricao_id)

        if not inscricao:
            return None

        repo_turma = TurmaRepository()

        # Busca a turma completa (com local_encontro)
        turma = repo_turma.buscar_por_id_completo(turma_id)

        if not turma:
            raise ValueError(f"Turma {turma_id} não encontrada")

        if turma.local_encontro is None:
            raise ValueError( "A turma encontrada não possui local de encontro carregado." )

        # Valida se a turma pertence à mesma etapa da inscrição
        if turma.etapa.id != inscricao.etapa.id:
            raise ValueError("A turma deve pertencer à mesma etapa da inscrição")

        inscricao.atribuir_turma(turma)

        status_distribuida= self._buscar_status_por_codigo("distribuida")
        if status_distribuida: inscricao.definir_status(status_distribuida)

        return self.editar(inscricao)

    def remover_turma(self, inscricao_id: str) -> Optional[Inscricao]:
        """Remove a turma de uma inscrição."""
        inscricao = self.buscar_por_id(inscricao_id)

        if not inscricao:
            return None

        inscricao.remover_turma()

        status_pendente = self._buscar_status_por_codigo("pendente_distribuicao")
        if status_pendente: inscricao.definir_status(status_pendente)

        return self.editar(inscricao)

    def _buscar_status_por_codigo(self, codigo: str) -> Optional[StatusInscricao]:
        """Busca um status pelo código."""
        result = ( self.db.table("status_inscricao") .select("*") .eq("codigo", codigo) .maybe_single() .execute() )

        data = self._extrair_data_optional(result)
        if not data:
            return None

        return StatusInscricao( id=data["id"], codigo=data["codigo"], descricao=data["descricao"], )