#app/routes/inscricao.py
from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Header, Query, Request
from pydantic import BaseModel, field_validator
from typing import Optional, List
from datetime import date, datetime
from pathlib import Path

from app.repositories.inscricaoRepository import InscricaoRepository
from app.repositories.documentoInscricaoRepository import DocumentoInscricaoRepository
from app.services.servicoDocumentoInscricao import ServicoDocumentoInscricao
from app.infra.supabaseClient import get_supabase
from app.repositories.catequizandoRepository import CatequizandoRepository
from app.repositories.responsavelRepository import ResponsavelRepository
import uuid
from app.domain.catequizando import Catequizando
from app.domain.responsavel import Responsavel
from app.domain.etapa import Etapa
from app.domain.statusInscricao import StatusInscricao
from app.domain.catequizandoResponsavel import CatequizandoResponsavel
from app.domain.tipoVinculoResponsavel import TipoVinculoResponsavel
from app.domain.servicoInscricao import ServicoInscricao

router = APIRouter()


# --- Pydantic Models para Request/Response ---

class InscricaoCreate(BaseModel):
    catequizando_nome: str
    catequizando_data_nascimento: date
    catequizando_sacramentos: List[int]
    etapa_id: str
    responsavel_nome: str
    responsavel_email: Optional[str] = None
    responsavel_telefone: str
    responsavel_vinculo: int
    local_encontro_id: Optional[int] = None
    referencia_irmao: Optional[str] = None
    quer_mesma_turma_que_irmao: bool = False
    observacao_responsavel: Optional[str] = None


class InscricaoResponse(BaseModel):
    id: str
    catequizando_nome: str
    etapa_id: str
    status_id: int
    responsavel_nome: str
    created_at: Optional[str] = None
    turma_id: Optional[str] = None


class EtapaResponse(BaseModel):
    id: str
    nome: str
    descricao: Optional[str] = None
    ano_nascimento_min: Optional[int] = None
    ano_nascimento_max: Optional[int] = None
    sacramentos_requeridos: List[int]
    sacramentos_proibidos: List[int] = []


class EtapaCreate(BaseModel):
    nome: str
    descricao: Optional[str] = None
    ano_nasc_minimo: Optional[int] = None
    ano_nasc_maximo: Optional[int] = None
    sacramentos_requeridos: List[int] = []
    sacramentos_proibidos: List[int] = []


class EtapaUpdate(BaseModel):
    nome: Optional[str] = None
    descricao: Optional[str] = None
    ano_nasc_minimo: Optional[int] = None
    ano_nasc_maximo: Optional[int] = None
    sacramentos_requeridos: List[int] = []
    sacramentos_proibidos: List[int] = []


class EtapaDetailResponse(BaseModel):
    id: str
    nome: str
    descricao: Optional[str] = None
    ano_nasc_minimo: Optional[int] = None
    ano_nasc_maximo: Optional[int] = None
    sacramentos_requeridos: List[int]
    sacramentos_proibidos: List[int]
    coordenador_etapa_id: Optional[str] = None


class SacramentoResponse(BaseModel):
    id: int
    codigo: str
    nome_exibicao: str
    ordem: Optional[int] = None


class TipoVinculoResponse(BaseModel):
    id: int
    codigo: str
    descricao: str


class LocalEncontroResponse(BaseModel):
    id: str
    codigo: str
    nome_exibicao: str


class CatequistaResponse(BaseModel):
    id: str
    nome: str
    email: Optional[str] = None
    telefone: Optional[str] = None


class TurmaResponse(BaseModel):
    id: str
    nome_sistema: str
    nome_exibicao: Optional[str] = None
    vagas_totais: int
    ativa: bool
    etapa_id: str
    etapa_nome: str
    local_encontro_id: Optional[str] = None
    ano_nasc_minimo: Optional[int] = None
    ano_nasc_maximo: Optional[int] = None


class TurmaCreate(BaseModel):
    etapa_id: str
    nome_sistema: str
    nome_exibicao: Optional[str] = None
    vagas_totais: int
    ativa: bool = True
    local_encontro_id: Optional[str] = None
    ano_nasc_minimo: Optional[int] = None
    ano_nasc_maximo: Optional[int] = None
    catequistas_ids: List[str] = []


class TurmaUpdate(BaseModel):
    nome_sistema: Optional[str] = None
    nome_exibicao: Optional[str] = None
    vagas_totais: Optional[int] = None
    ativa: Optional[bool] = None
    local_encontro_id: Optional[str] = None
    ano_nasc_minimo: Optional[int] = None
    ano_nasc_maximo: Optional[int] = None
    catequistas_ids: List[str] = []


class TurmaDetailResponse(BaseModel):
    id: str
    etapa_id: str
    etapa_nome: str
    nome_sistema: str
    nome_exibicao: Optional[str] = None
    vagas_totais: int
    ativa: bool
    local_encontro_id: Optional[str] = None
    local_encontro_nome: Optional[str] = None
    ano_nasc_minimo: Optional[int] = None
    ano_nasc_maximo: Optional[int] = None
    catequistas: List[CatequistaResponse] = []


class CatequizandoUpdate(BaseModel):
    nome: Optional[str] = None
    data_nascimento: Optional[date] = None
    observacoes: Optional[str] = None
    endereco: Optional[str] = None
    telefone: Optional[str] = None
    email: Optional[str] = None
    necessidade_especial: Optional[bool] = None
    descricao_necessidade_especial: Optional[str] = None

    @field_validator('data_nascimento', mode='before')
    @classmethod
    def parse_data_nascimento(cls, value):
        if value is None:
            return None
        if isinstance(value, date):
            return value
        if isinstance(value, str):
            return datetime.strptime(value, '%Y-%m-%d').date()
        return value


class AtribuirTurmaRequest(BaseModel):
    turma_id: str

#Etapas
@router.get("/etapas", response_model=List[EtapaResponse])
def listar_etapas():
    """Lista todas as etapas disponíveis para inscrição."""
    try:
        repo = InscricaoRepository()
        etapas = repo.listar_etapas()
        return [
            EtapaResponse(
                id=e["id"],
                nome=e["nome"],
                descricao=e.get("descricao"),
                ano_nascimento_min=e["ano_nascimento_min"],
                ano_nascimento_max=e["ano_nascimento_max"],
                sacramentos_requeridos=e.get("sacramentos_requeridos", []),
                sacramentos_proibidos=e.get("sacramentos_proibidos", [])
            )
            for e in etapas
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao listar etapas: {str(e)}")


@router.get("/etapas/{etapa_id}", response_model=EtapaDetailResponse)
def buscar_etapa(etapa_id: str):
    """Busca uma etapa específica pelo ID, incluindo sacramentos requeridos e proibidos."""
    try:
        from app.repositories.etapaRepository import EtapaRepository
        from app.infra.supabaseClient import get_supabase

        supabase = get_supabase()

        repo = EtapaRepository()
        etapa = repo.buscar_por_id(etapa_id)

        if not etapa:
            raise HTTPException(status_code=404, detail="Etapa não encontrada")

        # Buscar coordenador da etapa
        coord_result = (
            supabase
            .table("coordenador_etapa")
            .select("id, etapa_id")
            .eq("etapa_id", etapa_id)
            .execute()
        )

        coordenador_etapa_id = None
        if coord_result.data and len(coord_result.data) > 0:
            coordenador_etapa_id = coord_result.data[0]["id"]

        return EtapaDetailResponse(
            id=etapa.id,
            nome=etapa.nome,
            descricao=etapa.descricao,
            ano_nasc_minimo=etapa.ano_nasc_minimo,
            ano_nasc_maximo=etapa.ano_nasc_maximo,
            sacramentos_requeridos=[s.id for s in etapa.sacramentos_requeridos],
            sacramentos_proibidos=[s.id for s in etapa.sacramentos_proibidos],
            coordenador_etapa_id=coordenador_etapa_id
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar etapa: {str(e)}")


@router.post("/etapas", response_model=EtapaDetailResponse)
def criar_etapa(etapa_data: EtapaCreate):
    """Cria uma nova etapa com sacramentos requeridos e proibidos."""
    try:
        from app.repositories.etapaRepository import EtapaRepository
        from app.domain.etapa import Etapa
        from app.domain.sacramento import Sacramento
        from app.infra.supabaseClient import get_supabase
        import uuid

        supabase = get_supabase()

        sacramentos_requeridos = []
        if etapa_data.sacramentos_requeridos:
            for sac_id in etapa_data.sacramentos_requeridos:
                sac_db = (
                    supabase
                    .table("sacramento")
                    .select("*")
                    .eq("id", sac_id)
                    .maybe_single()
                    .execute()
                )
                if sac_db.data:
                    sacramentos_requeridos.append(
                        Sacramento(
                            id=sac_db.data["id"],
                            codigo=sac_db.data["codigo"],
                            nome_exibicao=sac_db.data["nome_exibicao"]
                        )
                    )

        sacramentos_proibidos = []
        if etapa_data.sacramentos_proibidos:
            for sac_id in etapa_data.sacramentos_proibidos:
                sac_db = (
                    supabase
                    .table("sacramento")
                    .select("*")
                    .eq("id", sac_id)
                    .maybe_single()
                    .execute()
                )
                if sac_db.data:
                    sacramentos_proibidos.append(
                        Sacramento(
                            id=sac_db.data["id"],
                            codigo=sac_db.data["codigo"],
                            nome_exibicao=sac_db.data["nome_exibicao"]
                        )
                    )

        etapa = Etapa(
            id=str(uuid.uuid4()),
            nome=etapa_data.nome,
            descricao=etapa_data.descricao,
            ano_nasc_minimo=etapa_data.ano_nasc_minimo,
            ano_nasc_maximo=etapa_data.ano_nasc_maximo,
            sacramentos_requeridos=sacramentos_requeridos,
            sacramentos_proibidos=sacramentos_proibidos
        )

        repo = EtapaRepository()
        etapa_salva = repo.salvar(etapa)

        return EtapaDetailResponse(
            id=etapa_salva.id,
            nome=etapa_salva.nome,
            descricao=etapa_salva.descricao,
            ano_nasc_minimo=etapa_salva.ano_nasc_minimo,
            ano_nasc_maximo=etapa_salva.ano_nasc_maximo,
            sacramentos_requeridos=[s.id for s in etapa_salva.sacramentos_requeridos],
            sacramentos_proibidos=[s.id for s in etapa_salva.sacramentos_proibidos],
            coordenador_etapa_id=None
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao criar etapa: {str(e)}")


@router.put("/etapas/{etapa_id}", response_model=EtapaDetailResponse)
def editar_etapa(etapa_id: str, etapa_data: EtapaUpdate):
    """Edita uma etapa existente, atualizando sacramentos requeridos e proibidos."""
    try:
        from app.repositories.etapaRepository import EtapaRepository
        from app.domain.etapa import Etapa
        from app.domain.sacramento import Sacramento
        from app.infra.supabaseClient import get_supabase

        supabase = get_supabase()

        repo = EtapaRepository()
        etapa_existente = repo.buscar_por_id(etapa_id)

        if not etapa_existente:
            raise HTTPException(status_code=404, detail="Etapa não encontrada")

        sacramentos_requeridos = []
        if etapa_data.sacramentos_requeridos:
            for sac_id in etapa_data.sacramentos_requeridos:
                sac_db = (
                    supabase
                    .table("sacramento")
                    .select("*")
                    .eq("id", sac_id)
                    .maybe_single()
                    .execute()
                )
                if sac_db.data:
                    sacramentos_requeridos.append(
                        Sacramento(
                            id=sac_db.data["id"],
                            codigo=sac_db.data["codigo"],
                            nome_exibicao=sac_db.data["nome_exibicao"]
                        )
                    )

        sacramentos_proibidos = []
        if etapa_data.sacramentos_proibidos:
            for sac_id in etapa_data.sacramentos_proibidos:
                sac_db = (
                    supabase
                    .table("sacramento")
                    .select("*")
                    .eq("id", sac_id)
                    .maybe_single()
                    .execute()
                )
                if sac_db.data:
                    sacramentos_proibidos.append(
                        Sacramento(
                            id=sac_db.data["id"],
                            codigo=sac_db.data["codigo"],
                            nome_exibicao=sac_db.data["nome_exibicao"]
                        )
                    )

        etapa = Etapa(
            id=etapa_id,
            nome=etapa_data.nome if etapa_data.nome is not None else etapa_existente.nome,
            descricao=etapa_data.descricao if etapa_data.descricao is not None else etapa_existente.descricao,
            ano_nasc_minimo=etapa_data.ano_nasc_minimo if etapa_data.ano_nasc_minimo is not None else etapa_existente.ano_nasc_minimo,
            ano_nasc_maximo=etapa_data.ano_nasc_maximo if etapa_data.ano_nasc_maximo is not None else etapa_existente.ano_nasc_maximo,
            sacramentos_requeridos=sacramentos_requeridos,
            sacramentos_proibidos=sacramentos_proibidos
        )

        etapa_editada = repo.editar(etapa)

        return EtapaDetailResponse(
            id=etapa_editada.id,
            nome=etapa_editada.nome,
            descricao=etapa_editada.descricao,
            ano_nasc_minimo=etapa_editada.ano_nasc_minimo,
            ano_nasc_maximo=etapa_editada.ano_nasc_maximo,
            sacramentos_requeridos=[s.id for s in etapa_editada.sacramentos_requeridos],
            sacramentos_proibidos=[s.id for s in etapa_editada.sacramentos_proibidos],
            coordenador_etapa_id=None
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao editar etapa: {str(e)}")


@router.delete("/etapas/{etapa_id}")
def excluir_etapa(etapa_id: str):
    """Exclui uma etapa e suas relações com sacramentos."""
    try:
        from app.repositories.etapaRepository import EtapaRepository

        repo = EtapaRepository()
        etapa_existente = repo.buscar_por_id(etapa_id)

        if not etapa_existente:
            raise HTTPException(status_code=404, detail="Etapa não encontrada")

        sucesso = repo.apagar(etapa_id)

        if not sucesso:
            raise HTTPException(status_code=500, detail="Não foi possível excluir a etapa")

        return {"message": "Etapa excluída com sucesso"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao excluir etapa: {str(e)}")


@router.put("/etapas/{etapa_id}/coordenador")
def atribuir_coordenador_etapa(etapa_id: str, coordenador_id: Optional[str] = Query(None)):
    """
    Atribui ou remove um coordenador de uma etapa.
    Um coordenador só pode estar vinculado a uma etapa.
    """
    try:
        supabase = get_supabase()

        # Verificar se etapa existe
        etapa_db = (
            supabase
            .table("etapa")
            .select("id")
            .eq("id", etapa_id)
            .execute()
        )

        if not etapa_db.data or len(etapa_db.data) == 0:
            raise HTTPException(status_code=404, detail="Etapa não encontrada")

        # Se coordenador_id for None, remover coordenador da etapa
        if coordenador_id is None:
            # Buscar coordenador atualmente vinculado a esta etapa
            coord_atual = (
                supabase
                .table("coordenador_etapa")
                .select("id")
                .eq("etapa_id", etapa_id)
                .execute()
            )

            if coord_atual.data and len(coord_atual.data) > 0:
                # Remover etapa_id do coordenador
                supabase.table("coordenador_etapa").update({
                    "etapa_id": None
                }).eq("id", coord_atual.data[0]["id"]).execute()

            return {"message": "Coordenador removido da etapa com sucesso"}

        # Verificar se coordenador existe
        coord_db = (
            supabase
            .table("coordenador_etapa")
            .select("id")
            .eq("id", coordenador_id)
            .execute()
        )

        if not coord_db.data or len(coord_db.data) == 0:
            raise HTTPException(status_code=404, detail="Coordenador não encontrado")

        # Verificar se coordenador já está vinculado a outra etapa
        coord_com_etapa = (
            supabase
            .table("coordenador_etapa")
            .select("id, etapa_id")
            .eq("id", coordenador_id)
            .execute()
        )

        if coord_com_etapa.data and len(coord_com_etapa.data) > 0:
            etapa_atual = coord_com_etapa.data[0].get("etapa_id")

            if etapa_atual and etapa_atual != etapa_id:
                raise HTTPException(
                    status_code=400,
                    detail="Este coordenador já está vinculado a outra etapa"
                )

        # Verificar se já existe outro coordenador nesta etapa
        outro_coord = (
            supabase
            .table("coordenador_etapa")
            .select("id")
            .eq("etapa_id", etapa_id)
            .neq("id", coordenador_id)
            .execute()
        )

        if outro_coord.data and len(outro_coord.data) > 0:
            # Remover etapa_id do coordenador anterior
            supabase.table("coordenador_etapa").update({
                "etapa_id": None
            }).eq("id", outro_coord.data[0]["id"]).execute()

        # Atualizar coordenador da etapa
        update_result = (
            supabase
            .table("coordenador_etapa")
            .update({"etapa_id": etapa_id})
            .eq("id", coordenador_id)
            .execute()
        )

        return {"message": "Coordenador atribuído à etapa com sucesso"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao atribuir coordenador: {str(e)}")


# Sacrametnos, tipos de vínculos, locais, catequistas
@router.get("/sacramentos", response_model=List[SacramentoResponse])
def listar_sacramentos():
    """Lista todos os sacramentos disponíveis."""
    try:
        supabase = get_supabase()

        resultado = (
            supabase
            .table("sacramento")
            .select("id, codigo, nome_exibicao, ordem")
            .order("ordem")
            .execute()
        )

        return [
            SacramentoResponse(
                id=s["id"],
                codigo=s["codigo"],
                nome_exibicao=s["nome_exibicao"],
                ordem=s["ordem"]
            )
            for s in resultado.data
        ]

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao listar sacramentos: {str(e)}"
        )


@router.get("/tipos-vinculo", response_model=List[TipoVinculoResponse])
def listar_tipos_vinculo():
    """Lista os tipos de vínculo disponíveis para o responsável."""
    try:
        supabase = get_supabase()

        resultado = (
            supabase
            .table("tipo_vinculo_responsavel")
            .select("id, codigo, descricao")
            .order("id")
            .execute()
        )

        return [
            TipoVinculoResponse(
                id=v["id"],
                codigo=v["codigo"],
                descricao=v["descricao"]
            )
            for v in resultado.data
        ]

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao listar tipos de vínculo: {str(e)}"
        )


@router.get("/locais-encontro", response_model=List[LocalEncontroResponse])
def listar_locais_encontro():
    """Lista todos os locais de encontro."""
    try:
        supabase = get_supabase()

        resultado = (
            supabase
            .table("local_encontro")
            .select("id, codigo, nome_exibicao")
            .order("nome_exibicao")
            .execute()
        )

        return [
            LocalEncontroResponse(
                id=str(l["id"]),
                codigo=l["codigo"],
                nome_exibicao=l["nome_exibicao"]
            )
            for l in resultado.data
        ]

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao listar locais de encontro: {str(e)}"
        )


@router.get("/catequistas", response_model=List[CatequistaResponse])
def listar_catequistas():
    """Lista todos os catequistas."""
    try:
        supabase = get_supabase()

        resultado = (
            supabase
            .table("catequista")
            .select("id, nome, email, telefone")
            .order("nome")
            .execute()
        )

        return [
            CatequistaResponse(
                id=c["id"],
                nome=c["nome"],
                email=c.get("email"),
                telefone=c.get("telefone")
            )
            for c in resultado.data
        ]

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao listar catequistas: {str(e)}"
        )

#Minhas turmas
@router.get("/minhas-turmas", response_model=List[TurmaResponse])
async def listar_minhas_turmas():
    """
    Lista TODAS as turmas.
    O frontend filtra baseado no perfil do usuário.
    """
    try:
        supabase = get_supabase()

        # BUSCAR TODAS AS TURMAS
        turmas_result = (
            supabase
            .table("turma")
            .select("""
                id,
                nome_sistema,
                nome_exibicao,
                vagas_totais,
                ativa,
                etapa_id,
                local_encontro_id,
                ano_nasc_minimo,
                ano_nasc_maximo
            """)
            .order("nome_sistema")
            .execute()
        )

        turmas = turmas_result.data or []

        # Format response
        response = [
            TurmaResponse(
                id=t["id"],
                nome_sistema=t["nome_sistema"],
                nome_exibicao=t.get("nome_exibicao"),
                vagas_totais=t["vagas_totais"],
                ativa=t.get("ativa", True),
                etapa_id=t["etapa_id"],
                etapa_nome="",
                local_encontro_id=str(t.get("local_encontro_id")) if t.get("local_encontro_id") else None,
                ano_nasc_minimo=t.get("ano_nasc_minimo"),
                ano_nasc_maximo=t.get("ano_nasc_maximo")
            )
            for t in turmas
        ]

        print(f"✅ Listar minas turmas: {len(response)} turmas retornadas")

        return response

    except Exception as e:
        print(f"❌ ERRO: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Erro ao listar minhas turmas: {str(e)}")


# Turmas - Lista Geral
@router.get("/turmas", response_model=List[TurmaResponse])
def listar_turmas():
    """Lista todas as turmas."""
    try:
        from app.repositories.turmaRepository import TurmaRepository

        repo = TurmaRepository()

        supabase = get_supabase()
        result = (
            supabase
            .table("turma")
            .select("*")
            .order("nome_sistema")
            .execute()
        )

        turmas = []
        for t in result.data:
            turmas.append({
                "id": t["id"],
                "nome_sistema": t["nome_sistema"],
                "nome_exibicao": t.get("nome_exibicao"),
                "vagas_totais": t["vagas_totais"],
                "ativa": t.get("ativa", True),
                "etapa_id": t["etapa_id"],
                "etapa_nome": "",
                "local_encontro_id": str(t.get("local_encontro_id")) if t.get("local_encontro_id") else None,
                "ano_nasc_minimo": t.get("ano_nasc_minimo"),
                "ano_nasc_maximo": t.get("ano_nasc_maximo")
            })

        return turmas

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao listar turmas: {str(e)}")


# Turmas - Endpoints específicos
@router.get("/turmas/{turma_id}/catequizandos")
def listar_catequizandos_por_turma(turma_id: str):
    """
    Lista todos os catequizandos de uma turma com dados completos.
    """
    try:
        supabase = get_supabase()

        # 1. Buscar inscrições da turma (SEM order aninhado)
        inscricoes_result = (
            supabase
            .table("inscricao")
            .select("""
                id,
                termo_assinado,
                data_inscricao,
                status:status_id (
                    id,
                    codigo
                ),
                catequizando:catequizando_id (
                    id,
                    nome,
                    data_nascimento,
                    telefone,
                    email,
                    observacoes,
                    necessidade_especial,
                    descricao_necessidade_especial,
                    historico_sacramental:historico_sacramental (
                        sacramento:sacramento (
                            id,
                            codigo,
                            nome_exibicao
                        )
                    ),
                    vinculos_responsaveis:catequizando_responsavel (
                        responsavel:responsavel (
                            id,
                            nome,
                            telefone,
                            email
                        ),
                        tipo_vinculo:tipo_vinculo_responsavel (
                            codigo,
                            descricao
                        )
                    )
                ),
                documentos:documento_inscricao (
                    id,
                    tipo_documento,
                    status_validacao
                )
            """)
            .eq("turma_id", turma_id)
            .execute()
        )

        inscricoes = inscricoes_result.data or []

        # Ordenar em Python
        inscricoes.sort(key=lambda x: x["catequizando"]["nome"])

        # 2. Format response
        catequizandos = []
        for inscricao in inscricoes:
            catequizando_data = inscricao["catequizando"]

            # Sacramentos
            sacramentos = []
            for item in catequizando_data.get("historico_sacramental", []):
                sacramento = item.get("sacramento")
                if sacramento:
                    sacramentos.append({
                        "id": sacramento["id"],
                        "codigo": sacramento["codigo"],
                        "nome_exibicao": sacramento["nome_exibicao"]
                    })

            # Responsáveis
            responsaveis = []
            for vinculo in catequizando_data.get("vinculos_responsaveis", []):
                responsavel = vinculo.get("responsavel")
                tipo_vinculo = vinculo.get("tipo_vinculo")
                if responsavel:
                    responsaveis.append({
                        "id": responsavel["id"],
                        "nome": responsavel["nome"],
                        "telefone": responsavel.get("telefone"),
                        "email": responsavel.get("email"),
                        "tipo_vinculo": tipo_vinculo["descricao"] if tipo_vinculo else None
                    })

            # Documentos
            documentos = inscricao.get("documentos", [])

            catequizandos.append({
                "inscricao_id": inscricao["id"],
                "id": catequizando_data["id"],
                "nome": catequizando_data["nome"],
                "data_nascimento": catequizando_data["data_nascimento"],
                "telefone": catequizando_data.get("telefone"),
                "email": catequizando_data.get("email"),
                "observacoes": catequizando_data.get("observacoes"),
                "necessidade_especial": catequizando_data.get("necessidade_especial", False),
                "descricao_necessidade_especial": catequizando_data.get("descricao_necessidade_especial"),
                "sacramentos": sacramentos,
                "responsaveis": responsaveis,
                "documentos": [
                    {
                        "id": d["id"],
                        "tipo_documento": d["tipo_documento"],
                        "status_validacao": d["status_validacao"]
                    }
                    for d in documentos
                ],
                "status_inscricao": inscricao["status"]["codigo"] if inscricao.get("status") else None,
                "termo_assinado": inscricao.get("termo_assinado", False)
            })

        return {"turma_id": turma_id, "catequizandos": catequizandos, "total": len(catequizandos)}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao listar catequizandos: {str(e)}")


@router.get("/turmas/{turma_id}/exportar")
def exportar_catequizandos_turma(turma_id: str, campos: Optional[str] = None):
    """
    Exporta lista de catequizandos em CSV com campos selecionados.
    Campos disponíveis: nome, data_nascimento, idade, telefone, email, responsaveis, sacramentos, documentos, observacoes, necessidade_especial
    """
    try:
        from fastapi.responses import StreamingResponse
        import csv
        import io

        # 1. Definir campos a exportar
        todos_campos = {
            "nome": "Nome",
            "data_nascimento": "Data Nascimento",
            "idade": "Idade",
            "telefone": "Telefone",
            "email": "Email",
            "responsaveis": "Responsáveis",
            "sacramentos": "Sacramentos",
            "documentos": "Documentos",
            "observacoes": "Observações",
            "necessidade_especial": "Necessidade Especial"
        }

        # Se campos não informado, exportar todos
        if not campos:
            campos_selecionados = list(todos_campos.keys())
        else:
            campos_selecionados = [c.strip() for c in campos.split(",") if c.strip() in todos_campos.keys()]

        # 2. Buscar catequizandos (SEM order aninhado)
        supabase = get_supabase()

        inscricoes_result = (
            supabase
            .table("inscricao")
            .select("""
                id,
                catequizando:catequizando_id (
                    id,
                    nome,
                    data_nascimento,
                    telefone,
                    email,
                    observacoes,
                    necessidade_especial,
                    descricao_necessidade_especial,
                    historico_sacramental:historico_sacramental (
                        sacramento:sacramento (
                            codigo,
                            nome_exibicao
                        )
                    ),
                    vinculos_responsaveis:catequizando_responsavel (
                        responsavel:responsavel (
                            nome,
                            telefone,
                            email
                        ),
                        tipo_vinculo:tipo_vinculo_responsavel (
                            descricao
                        )
                    )
                ),
                documentos:documento_inscricao (
                    tipo_documento,
                    status_validacao
                )
            """)
            .eq("turma_id", turma_id)
            .execute()
        )

        inscricoes = inscricoes_result.data or []
        # Ordenar em Python
        inscricoes.sort(key=lambda x: x["catequizando"]["nome"])

        # 3. Criar CSV
        output = io.StringIO()
        fieldnames = [todos_campos[c] for c in campos_selecionados]

        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()

        from datetime import date
        hoje = date.today()

        for inscricao in inscricoes:
            catequizando_data = inscricao["catequizando"]

            # Calcular idade
            data_nasc = date.fromisoformat(catequizando_data["data_nascimento"])
            idade = hoje.year - data_nasc.year - ((hoje.month, hoje.day) < (data_nasc.month, data_nasc.day))

            # Responsáveis
            responsaveis_nomes = []
            for vinculo in catequizando_data.get("vinculos_responsaveis", []):
                resp = vinculo.get("responsavel")
                tipo = vinculo.get("tipo_vinculo", {}).get("descricao", "")
                if resp:
                    responsaveis_nomes.append(f"{resp['nome']} ({tipo})")

            # Sacramentos
            sacramentos_nomes = []
            for item in catequizando_data.get("historico_sacramental", []):
                sac = item.get("sacramento")
                if sac:
                    sacramentos_nomes.append(sac["nome_exibicao"])

            # Documentos
            docs_status = []
            for doc in inscricao.get("documentos", []):
                status = "✅" if doc["status_validacao"] == "aprovado" else "⏳" if doc[
                                                                                      "status_validacao"] == "pendente" else "❌"
                docs_status.append(f"{doc['tipo_documento']}: {status}")

            row = {}

            if "nome" in campos_selecionados:
                row["Nome"] = catequizando_data["nome"]

            if "data_nascimento" in campos_selecionados:
                row["Data Nascimento"] = catequizando_data["data_nascimento"]

            if "idade" in campos_selecionados:
                row["Idade"] = idade

            if "telefone" in campos_selecionados:
                row["Telefone"] = catequizando_data.get("telefone", "")

            if "email" in campos_selecionados:
                row["Email"] = catequizando_data.get("email", "")

            if "responsaveis" in campos_selecionados:
                row["Responsáveis"] = "; ".join(responsaveis_nomes)

            if "sacramentos" in campos_selecionados:
                row["Sacramentos"] = "; ".join(sacramentos_nomes)

            if "documentos" in campos_selecionados:
                row["Documentos"] = "; ".join(docs_status)

            if "observacoes" in campos_selecionados:
                row["Observações"] = catequizando_data.get("observacoes", "") or ""

            if "necessidade_especial" in campos_selecionados:
                row["Necessidade Especial"] = "Sim" if catequizando_data.get("necessidade_especial") else "Não"

            writer.writerow(row)

        output.seek(0)

        # 4. Buscar nome da turma para nome do arquivo
        turma_result = (
            supabase
            .table("turma")
            .select("nome_exibicao, nome_sistema")
            .eq("id", turma_id)
            .maybe_single()
            .execute()
        )

        turma_nome = turma_result.data.get("nome_exibicao") or turma_result.data.get(
            "nome_sistema") or "turma" if turma_result.data else "turma"
        nome_arquivo = f"{turma_nome.replace(' ', '_')}.csv"

        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={nome_arquivo}"}
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao exportar: {str(e)}")


@router.get("/turmas/{turma_id}/vagas-ocupadas")
def contar_vagas_ocupadas(turma_id: str):
    """Conta quantas inscrições confirmadas existem em uma turma."""
    try:
        repo = InscricaoRepository()
        ocupadas = repo.contar_vagas_ocupadas_por_turma(turma_id)

        return {
            "turma_id": turma_id,
            "vagas_ocupadas": ocupadas
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao contar vagas ocupadas: {str(e)}")


# Turma Individual - CRUD
@router.get("/turmas/{turma_id}", response_model=TurmaDetailResponse)
def buscar_turma(turma_id: str):
    """Busca uma turma específica pelo ID."""
    try:
        from app.repositories.turmaRepository import TurmaRepository

        repo = TurmaRepository()
        turma = repo.buscar_por_id(turma_id)

        if not turma:
            raise HTTPException(status_code=404, detail="Turma não encontrada")

        return TurmaDetailResponse(
            id=turma.id,
            etapa_id=turma.etapa.id,
            etapa_nome=turma.etapa.nome,
            nome_sistema=turma.nome_sistema,
            nome_exibicao=turma.nome_exibicao,
            vagas_totais=turma.vagas_totais,
            ativa=turma.ativa,
            local_encontro_id=str(turma.local_encontro.id) if turma.local_encontro else None,
            local_encontro_nome=turma.local_encontro.nome_exibicao if turma.local_encontro else None,
            ano_nasc_minimo=turma.ano_nasc_minimo,
            ano_nasc_maximo=turma.ano_nasc_maximo,
            catequistas=[
                CatequistaResponse(
                    id=c.id,
                    nome=c.nome,
                    email=c.email,
                    telefone=c.telefone
                )
                for c in turma.catequistas
            ]
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar turma: {str(e)}")


@router.post("/turmas", response_model=TurmaDetailResponse)
def criar_turma(turma_data: TurmaCreate):
    """Cria uma nova turma."""
    try:
        from app.repositories.turmaRepository import TurmaRepository
        from app.domain.turma import Turma
        from app.domain.etapa import Etapa
        from app.domain.localEncontro import LocalEncontro
        from app.domain.catequista import Catequista
        from app.infra.supabaseClient import get_supabase
        import uuid

        supabase = get_supabase()

        etapa_db = (
            supabase
            .table("etapa")
            .select("*")
            .eq("id", turma_data.etapa_id)
            .maybe_single()
            .execute()
        )

        if not etapa_db.data:
            raise HTTPException(status_code=400, detail=f"Etapa {turma_data.etapa_id} não encontrada")

        etapa = Etapa(
            id=etapa_db.data["id"],
            nome=etapa_db.data["nome"],
            descricao=etapa_db.data.get("descricao"),
            ano_nasc_minimo=etapa_db.data.get("ano_nasc_minimo"),
            ano_nasc_maximo=etapa_db.data.get("ano_nasc_maximo"),
            sacramentos_requeridos=[],
            sacramentos_proibidos=[]
        )

        local_encontro = None
        if turma_data.local_encontro_id:
            local_db = (
                supabase
                .table("local_encontro")
                .select("*")
                .eq("id", turma_data.local_encontro_id)
                .maybe_single()
                .execute()
            )

            if local_db.data:
                local_encontro = LocalEncontro(
                    id=local_db.data["id"],
                    codigo=local_db.data["codigo"],
                    nome_exibicao=local_db.data["nome_exibicao"]
                )

        catequistas = []
        if turma_data.catequistas_ids:
            for cat_id in turma_data.catequistas_ids:
                cat_db = (
                    supabase
                    .table("catequista")
                    .select("*")
                    .eq("id", cat_id)
                    .maybe_single()
                    .execute()
                )

                if cat_db.data:
                    catequistas.append(
                        Catequista(
                            id=cat_db.data["id"],
                            nome=cat_db.data["nome"],
                            email=cat_db.data.get("email"),
                            telefone=cat_db.data.get("telefone"),
                            usuario=None
                        )
                    )

        turma = Turma(
            id=str(uuid.uuid4()),
            etapa=etapa,
            nome_sistema=turma_data.nome_sistema,
            nome_exibicao=turma_data.nome_exibicao,
            vagas_totais=turma_data.vagas_totais,
            ativa=turma_data.ativa,
            local_encontro=local_encontro,
            ano_nasc_minimo=turma_data.ano_nasc_minimo,
            ano_nasc_maximo=turma_data.ano_nasc_maximo,
            catequistas=catequistas
        )

        repo = TurmaRepository()
        turma_salva = repo.salvar(turma)

        return TurmaDetailResponse(
            id=turma_salva.id,
            etapa_id=turma_salva.etapa.id,
            etapa_nome=turma_salva.etapa.nome,
            nome_sistema=turma_salva.nome_sistema,
            nome_exibicao=turma_salva.nome_exibicao,
            vagas_totais=turma_salva.vagas_totais,
            ativa=turma_salva.ativa,
            local_encontro_id=str(turma_salva.local_encontro.id) if turma_salva.local_encontro else None,
            local_encontro_nome=turma_salva.local_encontro.nome_exibicao if turma_salva.local_encontro else None,
            ano_nasc_minimo=turma_salva.ano_nasc_minimo,
            ano_nasc_maximo=turma_salva.ano_nasc_maximo,
            catequistas=[
                CatequistaResponse(
                    id=c.id,
                    nome=c.nome,
                    email=c.email,
                    telefone=c.telefone
                )
                for c in turma_salva.catequistas
            ]
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao criar turma: {str(e)}")


@router.put("/turmas/{turma_id}", response_model=TurmaDetailResponse)
def editar_turma(turma_id: str, turma_data: TurmaUpdate):
    """Edita uma turma existente."""
    try:
        from app.repositories.turmaRepository import TurmaRepository
        from app.domain.turma import Turma
        from app.domain.etapa import Etapa
        from app.domain.localEncontro import LocalEncontro
        from app.domain.catequista import Catequista
        from app.infra.supabaseClient import get_supabase

        supabase = get_supabase()

        repo = TurmaRepository()
        turma_existente = repo.buscar_por_id(turma_id)

        if not turma_existente:
            raise HTTPException(status_code=404, detail="Turma não encontrada")

        local_encontro = turma_existente.local_encontro
        if turma_data.local_encontro_id and turma_data.local_encontro_id != (
                local_encontro.id if local_encontro else None):
            local_db = (
                supabase
                .table("local_encontro")
                .select("*")
                .eq("id", turma_data.local_encontro_id)
                .maybe_single()
                .execute()
            )

            if local_db.data:
                local_encontro = LocalEncontro(
                    id=local_db.data["id"],
                    codigo=local_db.data["codigo"],
                    nome_exibicao=local_db.data["nome_exibicao"]
                )

        catequistas = []
        if turma_data.catequistas_ids:
            for cat_id in turma_data.catequistas_ids:
                cat_db = (
                    supabase
                    .table("catequista")
                    .select("*")
                    .eq("id", cat_id)
                    .maybe_single()
                    .execute()
                )

                if cat_db.data:
                    catequistas.append(
                        Catequista(
                            id=cat_db.data["id"],
                            nome=cat_db.data["nome"],
                            email=cat_db.data.get("email"),
                            telefone=cat_db.data.get("telefone"),
                            usuario=None
                        )
                    )

        turma = Turma(
            id=turma_id,
            etapa=turma_existente.etapa,
            nome_sistema=turma_data.nome_sistema if turma_data.nome_sistema is not None else turma_existente.nome_sistema,
            nome_exibicao=turma_data.nome_exibicao if turma_data.nome_exibicao is not None else turma_existente.nome_exibicao,
            vagas_totais=turma_data.vagas_totais if turma_data.vagas_totais is not None else turma_existente.vagas_totais,
            ativa=turma_data.ativa if turma_data.ativa is not None else turma_existente.ativa,
            local_encontro=local_encontro,
            ano_nasc_minimo=turma_data.ano_nasc_minimo if turma_data.ano_nasc_minimo is not None else turma_existente.ano_nasc_minimo,
            ano_nasc_maximo=turma_data.ano_nasc_maximo if turma_data.ano_nasc_maximo is not None else turma_existente.ano_nasc_maximo,
            catequistas=catequistas
        )

        turma_editada = repo.editar(turma)

        return TurmaDetailResponse(
            id=turma_editada.id,
            etapa_id=turma_editada.etapa.id,
            etapa_nome=turma_editada.etapa.nome,
            nome_sistema=turma_editada.nome_sistema,
            nome_exibicao=turma_editada.nome_exibicao,
            vagas_totais=turma_editada.vagas_totais,
            ativa=turma_editada.ativa,
            local_encontro_id=str(turma_editada.local_encontro.id) if turma_editada.local_encontro else None,
            local_encontro_nome=turma_editada.local_encontro.nome_exibicao if turma_editada.local_encontro else None,
            ano_nasc_minimo=turma_editada.ano_nasc_minimo,
            ano_nasc_maximo=turma_editada.ano_nasc_maximo,
            catequistas=[
                CatequistaResponse(
                    id=c.id,
                    nome=c.nome,
                    email=c.email,
                    telefone=c.telefone
                )
                for c in turma_editada.catequistas
            ]
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao editar turma: {str(e)}")


@router.delete("/turmas/{turma_id}")
def excluir_turma(turma_id: str):
    """Exclui uma turma."""
    try:
        from app.repositories.turmaRepository import TurmaRepository

        repo = TurmaRepository()
        turma_existente = repo.buscar_por_id(turma_id)

        if not turma_existente:
            raise HTTPException(status_code=404, detail="Turma não encontrada")

        sucesso = repo.apagar(turma_id)

        if not sucesso:
            raise HTTPException(status_code=500, detail="Não foi possível excluir a turma")

        return {"message": "Turma excluída com sucesso"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao excluir turma: {str(e)}")


# Inscrições
@router.post("/inscricoes", response_model=InscricaoResponse)
def criar_inscricao(inscricao_data: InscricaoCreate, authorization: Optional[str] = Header(None)):
    """
    Cria uma nova inscrição de catequizando.
    """
    try:
        supabase = get_supabase()

        # 1. Buscar usuário logado via token
        usuario_id = None

        if authorization and authorization.startswith("Bearer "):
            token = authorization.replace("Bearer ", "")

            try:
                user_data = supabase.auth.get_user(token)
                usuario_id = user_data.user.id
            except:
                raise HTTPException(status_code=401, detail="Usuário não autenticado")

        if not usuario_id:
            raise HTTPException(status_code=401, detail="Usuário não autenticado")

        # 2. Buscar responsável existente pelo usuario_id
        repo_responsavel = ResponsavelRepository()
        responsavel_existente = repo_responsavel.buscar_por_usuario_id(usuario_id)

        if responsavel_existente:
            responsavel_salvo = responsavel_existente

            if responsavel_salvo.nome != inscricao_data.responsavel_nome:
                responsavel_salvo.nome = inscricao_data.responsavel_nome
                responsavel_salvo.email = inscricao_data.responsavel_email
                responsavel_salvo.telefone = inscricao_data.responsavel_telefone
                repo_responsavel.editar(responsavel_salvo)
        else:
            from app.domain.usuario import Usuario

            responsavel_novo = Responsavel(
                id=str(uuid.uuid4()),
                nome=inscricao_data.responsavel_nome,
                email=inscricao_data.responsavel_email,
                telefone=inscricao_data.responsavel_telefone,
                usuario=Usuario(id=usuario_id, nome="", email=""),
                vinculos=[],
            )

            responsavel_salvo = repo_responsavel.salvar(responsavel_novo)

        etapa_db = (
            supabase
            .table("etapa")
            .select("*")
            .eq("id", inscricao_data.etapa_id)
            .maybe_single()
            .execute()
        )

        if not etapa_db.data:
            raise HTTPException(status_code=400, detail=f"Etapa {inscricao_data.etapa_id} não encontrada")

        etapa_data = etapa_db.data

        etapa = Etapa(
            id=etapa_data["id"],
            nome=etapa_data["nome"],
            descricao=etapa_data.get("descricao"),
            ano_nasc_minimo=etapa_data.get("ano_nasc_minimo"),
            ano_nasc_maximo=etapa_data.get("ano_nasc_maximo"),
            sacramentos_requeridos=[],
            sacramentos_proibidos=[],
        )

        from app.domain.historicoSacramental import HistoricoSacramental
        from app.domain.sacramento import Sacramento

        catequizando_novo = Catequizando(
            id=str(uuid.uuid4()),
            nome=inscricao_data.catequizando_nome,
            data_nascimento=inscricao_data.catequizando_data_nascimento,
            observacoes=None,
            endereco=None,
            telefone=None,
            email=None,
            necessidade_especial=False,
            descricao_necessidade_especial=None,
            vinculos_responsaveis=[],
            historico_sacramental=[],
        )

        repo_catequizando = CatequizandoRepository()
        catequizando_salvo = repo_catequizando.salvar(catequizando_novo)

        for sacramento_id in inscricao_data.catequizando_sacramentos:
            sacramento_db = (
                supabase
                .table("sacramento")
                .select("*")
                .eq("id", sacramento_id)
                .maybe_single()
                .execute()
            )

            if sacramento_db.data:
                sacramento = Sacramento(
                    id=sacramento_db.data["id"],
                    codigo=sacramento_db.data["codigo"],
                    nome_exibicao=sacramento_db.data["nome_exibicao"],
                )

                historico = HistoricoSacramental(
                    id=str(uuid.uuid4()),
                    catequizando=catequizando_salvo,
                    sacramento=sacramento,
                    data_recebimento=date.today(),
                    local=None,
                    observacoes=None,
                )

                catequizando_salvo.adicionar_historico_sacramental(historico)

        repo_catequizando.sincronizar_historico_sacramental(catequizando_salvo)

        tipo_vinculo_db = (
            supabase
            .table("tipo_vinculo_responsavel")
            .select("*")
            .eq("id", inscricao_data.responsavel_vinculo)
            .maybe_single()
            .execute()
        )

        if not tipo_vinculo_db.data:
            raise HTTPException(
                status_code=400,
                detail=f"Tipo de vínculo {inscricao_data.responsavel_vinculo} não encontrado"
            )

        tipo_vinculo = TipoVinculoResponsavel(
            id=tipo_vinculo_db.data["id"],
            codigo=tipo_vinculo_db.data["codigo"],
            descricao=tipo_vinculo_db.data["descricao"],
        )

        vinculo = CatequizandoResponsavel(
            catequizando=catequizando_salvo,
            responsavel=responsavel_salvo,
            tipo_vinculo=tipo_vinculo,
            descricao_outro=None,
        )
        vinculo.validar()

        catequizando_salvo.adicionar_vinculo_responsavel(vinculo)
        responsavel_salvo.adicionar_vinculo(vinculo)

        repo_catequizando.sincronizar_vinculos_responsaveis(catequizando_salvo)

        status_db = (
            supabase
            .table("status_inscricao")
            .select("*")
            .eq("codigo", "pendente_distribuicao")
            .maybe_single()
            .execute()
        )

        if not status_db.data:
            raise HTTPException(status_code=500, detail="Status 'pendente_distribuicao' não encontrado")

        status = StatusInscricao(
            id=status_db.data["id"],
            codigo=status_db.data["codigo"],
            descricao=status_db.data["descricao"],
        )

        if not responsavel_salvo.pode_responder_por(catequizando_salvo):
            raise HTTPException(
                status_code=400,
                detail="O responsável informado não possui vínculo com o catequizando."
            )

        if not etapa.aceita_catequizando(catequizando_salvo):
            raise HTTPException(
                status_code=400,
                detail="O catequizando não atende aos requisitos da etapa."
            )

        repo_inscricao = InscricaoRepository()
        turmas, total_inscricoes = repo_inscricao.buscar_dados_para_verificar_vagas(
            etapa_id=etapa.id,
            catequizando=catequizando_salvo,
        )

        status_confirmada_db = (
            supabase
            .table("status_inscricao")
            .select("*")
            .eq("codigo", "confirmada")
            .maybe_single()
            .execute()
        )

        status_lista_espera_db = (
            supabase
            .table("status_inscricao")
            .select("*")
            .eq("codigo", "lista_espera")
            .maybe_single()
            .execute()
        )

        if not status_confirmada_db.data or not status_lista_espera_db.data:
            raise HTTPException(
                status_code=500,
                detail="Status 'confirmada' ou 'lista_espera' não encontrados"
            )

        status_confirmada = StatusInscricao(
            id=status_confirmada_db.data["id"],
            codigo=status_confirmada_db.data["codigo"],
            descricao=status_confirmada_db.data["descricao"],
        )

        status_lista_espera = StatusInscricao(
            id=status_lista_espera_db.data["id"],
            codigo=status_lista_espera_db.data["codigo"],
            descricao=status_lista_espera_db.data["descricao"],
        )

        servico = ServicoInscricao(
            status_pendente_distribuicao=status,
            status_confirmada=status_confirmada,
            status_lista_espera=status_lista_espera,
        )

        inscricao = servico.criar_inscricao(
            id_inscricao=str(uuid.uuid4()),
            catequizando=catequizando_salvo,
            responsavel=responsavel_salvo,
            etapa=etapa,
            turmas=turmas,
            total_inscricoes_etapa=total_inscricoes,
            referencia_irmao=inscricao_data.referencia_irmao,
            quer_mesma_turma_que_irmao=inscricao_data.quer_mesma_turma_que_irmao,
            observacao_responsavel=inscricao_data.observacao_responsavel,
            local_encontro_id=inscricao_data.local_encontro_id,
        )

        inscricao_salva = repo_inscricao.salvar(inscricao)

        return InscricaoResponse(
            id=inscricao_salva.id,
            catequizando_nome=inscricao_salva.catequizando.nome,
            etapa_id=inscricao_salva.etapa.id,
            status_id=inscricao_salva.status.id,
            responsavel_nome=inscricao_salva.responsavel.nome,
            created_at=str(inscricao_salva.data_inscricao) if inscricao_salva.data_inscricao else None,
            turma_id=str(inscricao_salva.turma.id) if inscricao_salva.turma else None
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao criar inscrição: {str(e)}")


@router.post("/inscricoes/{inscricao_id}/documentos")
def upload_documento(inscricao_id: str, file: UploadFile = File(...), tipo_documento: str = Form(...)):
    """Faz upload de um documento para uma inscrição."""
    try:
        import tempfile
        import os

        with tempfile.NamedTemporaryFile(delete=False,
                                         suffix=Path(file.filename).suffix if file.filename else "") as tmp:
            tmp.write(file.file.read())
            tmp_path = tmp.name

        try:
            servico = ServicoDocumentoInscricao()

            documento = servico.enviar_documento(
                inscricao_id=inscricao_id,
                tipo_documento=tipo_documento,
                caminho_arquivo_local=tmp_path,
                nome_original=file.filename,
            )

            return {
                "id": documento.id,
                "inscricao_id": documento.inscricao_id,
                "file_name": documento.nome_original,
                "tipo_documento": documento.tipo_documento,
                "storage_path": documento.caminho_storage
            }
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao upload documento: {str(e)}")


@router.get("/inscricoes", response_model=List[InscricaoResponse])
def listar_inscricoes():
    """Lista todas as inscrições."""
    try:
        repo = InscricaoRepository()
        inscricoes = repo.listar_todos()

        return [
            InscricaoResponse(
                id=i["id"],
                catequizando_nome=i["catequizando_nome"],
                etapa_id=i["etapa_id"],
                status_id=i["status_id"],
                responsavel_nome=i["responsavel_nome"],
                created_at=i.get("created_at"),
                turma_id=i.get("turma_id")
            )
            for i in inscricoes
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao listar inscrições: {str(e)}")


@router.get("/inscricoes/pendentes-distribuicao", response_model=List[InscricaoResponse])
def listar_pendentes_distribuicao():
    """Lista inscrições pendentes de distribuição em turma."""
    try:
        repo = InscricaoRepository()
        inscricoes = repo.listar_pendentes_distribuicao()

        return [
            InscricaoResponse(
                id=item["id"],
                catequizando_nome=item["catequizando_nome"],
                etapa_id=item["etapa_id"],
                status_id=item["status_id"],
                responsavel_nome=item["responsavel_nome"],
                created_at=item.get("created_at"),
            )
            for item in inscricoes
        ]

    except Exception as erro:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao listar pendentes de distribuição: {erro}",
        )


@router.get("/inscricoes/etapa/{etapa_id}", response_model=List[InscricaoResponse])
def listar_inscricoes_por_etapa(etapa_id: str):
    """Lista todas as inscrições de uma etapa específica."""
    try:
        repo = InscricaoRepository()
        inscricoes = repo.listar_por_etapa(etapa_id)

        return [
            InscricaoResponse(
                id=i["id"],
                catequizando_nome=i["catequizando_nome"],
                etapa_id=i["etapa_id"],
                status_id=i["status_id"],
                responsavel_nome=i["responsavel_nome"],
                created_at=i.get("created_at")
            )
            for i in inscricoes
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao listar inscrições por etapa: {str(e)}")


@router.get("/inscricoes/status/{status_codigo}", response_model=List[InscricaoResponse])
def listar_inscricoes_por_status(status_codigo: str):
    """Lista todas as inscrições com um status específico."""
    try:
        repo = InscricaoRepository()
        inscricoes = repo.listar_por_status(status_codigo)

        return [
            InscricaoResponse(
                id=i["id"],
                catequizando_nome=i["catequizando_nome"],
                etapa_id=i["etapa_id"],
                status_id=i["status_id"],
                responsavel_nome=i["responsavel_nome"],
                created_at=i.get("created_at")
            )
            for i in inscricoes
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao listar inscrições por status: {str(e)}")


@router.get("/inscricoes/{inscricao_id}/completa")
def buscar_inscricao_completa(inscricao_id: str):
    """Busca uma inscrição com todos os detalhes e relacionamentos."""
    try:
        repo = InscricaoRepository()
        inscricao = repo.buscar_com_detalhes_completos(inscricao_id)

        if not inscricao:
            raise HTTPException(status_code=404, detail="Inscrição não encontrada")

        return inscricao
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar inscrição completa: {str(e)}")


@router.get("/inscricoes/{inscricao_id}", response_model=InscricaoResponse)
def buscar_inscricao(inscricao_id: str):
    """Busca uma inscrição específica pelo ID."""
    try:
        repo = InscricaoRepository()
        inscricao = repo.buscar_por_id(inscricao_id)

        if not inscricao:
            raise HTTPException(status_code=404, detail="Inscrição não encontrada")

        return InscricaoResponse(
            id=inscricao.id,
            catequizando_nome=inscricao.catequizando.nome,
            etapa_id=inscricao.etapa.id,
            status_id=inscricao.status.id,
            responsavel_nome=inscricao.responsavel.nome,
            created_at=str(inscricao.data_inscricao) if inscricao.data_inscricao else None,
            turma_id=str(inscricao.turma.id) if inscricao.turma else None
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar inscrição: {str(e)}")


@router.get("/inscricoes/{inscricao_id}/documentos")
def listar_documentos(inscricao_id: str):
    """Lista todos os documentos de uma inscrição."""
    try:
        repo = DocumentoInscricaoRepository()
        documentos = repo.listar_por_inscricao(inscricao_id)

        return [
            {
                "id": d.id,
                "inscricao_id": d.inscricao_id,
                "file_name": d.nome_original,
                "tipo_documento": d.tipo_documento,
                "storage_path": d.caminho_storage,
                "uploaded_at": str(d.created_at) if d.created_at else None,
                "status_validacao": d.status_validacao,
                "observacao_validacao": d.observacao_validacao
            }
            for d in documentos
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao listar documentos: {str(e)}")


@router.put("/inscricoes/{inscricao_id}/status")
def atualizar_status_inscricao(inscricao_id: str, status_id: int):
    """Atualiza o status de uma inscrição."""
    try:
        repo = InscricaoRepository()
        inscricao = repo.atualizar_status(inscricao_id, status_id)

        if not inscricao:
            raise HTTPException(status_code=404, detail="Inscrição não encontrada")

        return {
            "message": "Status atualizado com sucesso",
            "inscricao_id": inscricao.id,
            "novo_status_id": inscricao.status.id,
            "novo_status_codigo": inscricao.status.codigo
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao atualizar status: {str(e)}")


@router.put("/inscricoes/{inscricao_id}/turma")
def atribuir_turma_inscricao(inscricao_id: str, dados: AtribuirTurmaRequest):
    """Atribui uma turma a uma inscrição."""
    try:
        repo = InscricaoRepository()
        inscricao = repo.atribuir_turma(inscricao_id, dados.turma_id)

        if not inscricao:
            raise HTTPException(status_code=404, detail="Inscrição não encontrada")

        return {
            "message": "Turma atribuída com sucesso",
            "inscricao_id": inscricao.id,
            "turma_id": inscricao.turma.id if inscricao.turma else None,
            "turma_nome": inscricao.turma.nome_exibicao if inscricao.turma else None,
            "status_id": inscricao.status.id,
            "status_codigo": inscricao.status.codigo
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao atribuir turma: {str(e)}")


@router.delete("/inscricoes/{inscricao_id}/turma")
def remover_turma_inscricao(inscricao_id: str):
    """Remove a turma de uma inscrição."""
    try:
        repo = InscricaoRepository()
        inscricao = repo.remover_turma(inscricao_id)

        if not inscricao:
            raise HTTPException(status_code=404, detail="Inscrição não encontrada")

        return {
            "message": "Turma removida com sucesso",
            "inscricao_id": inscricao.id,
            "status_id": inscricao.status.id,
            "status_codigo": inscricao.status.codigo
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao remover turma: {str(e)}")


@router.get("/inscricoes/contar-por-turma/{turma_id}")
def contar_inscricoes_por_turma(turma_id: str):
    """Conta quantas inscrições (qualquer status) existem para uma turma específica."""
    try:
        repo = InscricaoRepository()
        count = repo.contar_inscricoes_por_turma(turma_id)

        return {"count": count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao contar inscrições: {str(e)}")


@router.delete("/inscricoes/{inscricao_id}")
def excluir_inscricao(inscricao_id: str):
    """Exclui uma inscrição e o catequizando (se não tiver outras inscrições)."""
    try:
        from app.repositories.inscricaoRepository import InscricaoRepository
        from app.repositories.catequizandoRepository import CatequizandoRepository

        repo = InscricaoRepository()
        repo_catequizando = CatequizandoRepository()

        # Buscar inscrição para saber o catequizando_id
        inscricao_existente = repo.buscar_por_id(inscricao_id)

        if not inscricao_existente:
            raise HTTPException(status_code=404, detail="Inscrição não encontrada")

        catequizando_id = inscricao_existente.catequizando.id

        # Excluir inscrição
        sucesso = repo.apagar(inscricao_id)

        if not sucesso:
            raise HTTPException(status_code=500, detail="Não foi possível excluir a inscrição")

        from app.infra.supabaseClient import get_supabase
        supabase = get_supabase()

        result = (
            supabase
            .table("inscricao")
            .select("id", count="exact")
            .eq("catequizando_id", catequizando_id)
            .execute()
        )

        outras_inscricoes = result.count or 0

        if outras_inscricoes == 0:
            repo_catequizando.apagar(catequizando_id)

        return {"message": "Inscrição excluída com sucesso"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao excluir inscrição: {str(e)}")


# Documentos
@router.delete("/documentos/{documento_id}")
def excluir_documento(documento_id: str):
    """Exclui um documento de inscrição."""
    try:
        from app.services.servicoDocumentoInscricao import ServicoDocumentoInscricao

        servico = ServicoDocumentoInscricao()
        documento = servico.excluir_documento(documento_id)

        return {
            "message": "Documento excluído com sucesso",
            "documento_id": documento.id
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao excluir documento: {str(e)}")


@router.put("/documentos/{documento_id}/status")
def atualizar_status_documento(documento_id: str, status_validacao: str, observacao_validacao: Optional[str] = None):
    """Aprova ou rejeita um documento."""
    try:
        from app.services.servicoDocumentoInscricao import ServicoDocumentoInscricao

        servico = ServicoDocumentoInscricao()
        documento = servico.atualizar_status_documento(
            documento_id=documento_id,
            status_validacao=status_validacao,
            observacao_validacao=observacao_validacao
        )

        return {
            "message": "Status do documento atualizado com sucesso",
            "documento_id": documento.id,
            "status_validacao": documento.status_validacao
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao atualizar status do documento: {str(e)}")


# Catequizando (Path específico)
@router.get("/catequizandos/{catequizando_id}")
def buscar_catequizando(catequizando_id: str):
    """Busca dados de um catequizando específico."""
    try:
        repo = CatequizandoRepository()
        catequizando = repo.buscar_por_id(catequizando_id)

        if not catequizando:
            raise HTTPException(status_code=404, detail="Catequizando não encontrado")

        return {
            "id": catequizando.id,
            "nome": catequizando.nome,
            "data_nascimento": catequizando.data_nascimento.isoformat() if catequizando.data_nascimento else None,
            "endereco": catequizando.endereco,
            "telefone": catequizando.telefone,
            "email": catequizando.email,
            "observacoes": catequizando.observacoes,
            "necessidade_especial": catequizando.necessidade_especial,
            "descricao_necessidade_especial": catequizando.descricao_necessidade_especial
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/catequizandos/{catequizando_id}")
def editar_catequizando(catequizando_id: str, dados: CatequizandoUpdate):
    """Edita dados de um catequizando."""
    try:
        repo = CatequizandoRepository()

        # Verificar se existe
        catequizando_existente = repo.buscar_por_id(catequizando_id)
        if not catequizando_existente:
            raise HTTPException(status_code=404, detail="Catequizando não encontrado")

        # Converter para dict e remover None
        update_data = {k: v for k, v in dados.dict().items() if v is not None}

        # Editar parcialmente
        catequizando_atualizado = repo.editar_parcial(catequizando_id, update_data)

        return {
            "message": "Catequizando atualizado com sucesso",
            "id": catequizando_atualizado.id,
            "nome": catequizando_atualizado.nome
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/inscricoes/verificar-vagas-etapa/{etapa_id}")
def verificar_vagas_etapa(etapa_id: str):
    """
    Verifica se há vagas disponíveis em uma etapa.
    Retorna:
    - total_vagas: soma de vagas_totais de todas as turmas ativas da etapa
    - total_inscricoes: soma de inscrições confirmadas na etapa
    - vagas_disponiveis: total_vagas - total_inscricoes
    - sem_vagas: True se vagas_disponiveis <= 0
    """
    try:
        supabase = get_supabase()

        # 1. Buscar todas as turmas ativas da etapa
        turmas_result = (
            supabase
            .table("turma")
            .select("id, vagas_totais")
            .eq("etapa_id", etapa_id)
            .eq("ativa", True)
            .execute()
        )

        turmas = turmas_result.data or []
        total_vagas = sum(t.get("vagas_totais", 0) for t in turmas)

        # 2. Contar inscrições confirmadas na etapa
        repo = InscricaoRepository()
        total_inscricoes = repo.contar_inscricoes_por_etapa(etapa_id)

        # 3. Calcular vagas disponíveis
        vagas_disponiveis = total_vagas - total_inscricoes
        sem_vagas = vagas_disponiveis <= 0

        return {
            "etapa_id": etapa_id,
            "total_vagas": total_vagas,
            "total_inscricoes": total_inscricoes,
            "vagas_disponiveis": vagas_disponiveis,
            "sem_vagas": sem_vagas
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao verificar vagas: {str(e)}")