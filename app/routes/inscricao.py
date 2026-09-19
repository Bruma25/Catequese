from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from typing import Optional, List
from datetime import date
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
    nome:str
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

# --- Endpoints ---

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

        repo = EtapaRepository()
        etapa = repo.buscar_por_id(etapa_id)

        if not etapa:
            raise HTTPException(status_code=404, detail="Etapa não encontrada")

        return EtapaDetailResponse(
            id=etapa.id,
            nome=etapa.nome,
            descricao=etapa.descricao,
            ano_nasc_minimo=etapa.ano_nasc_minimo,
            ano_nasc_maximo=etapa.ano_nasc_maximo,
            sacramentos_requeridos=[s.id for s in etapa.sacramentos_requeridos],
            sacramentos_proibidos=[s.id for s in etapa.sacramentos_proibidos]
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
            sacramentos_proibidos=[s.id for s in etapa_salva.sacramentos_proibidos]
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
            sacramentos_proibidos=[s.id for s in etapa_editada.sacramentos_proibidos]
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


@router.post("/inscricoes", response_model=InscricaoResponse)
def criar_inscricao(inscricao_data: InscricaoCreate):
    """
    Cria uma nova inscrição de catequizando.
    """
    try:
        supabase = get_supabase()

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

        responsavel_novo = Responsavel(
            id=str(uuid.uuid4()),
            nome=inscricao_data.responsavel_nome,
            email=inscricao_data.responsavel_email,
            telefone=inscricao_data.responsavel_telefone,
            usuario=None,
            vinculos=[],
        )

        repo_catequizando = CatequizandoRepository()
        repo_responsavel = ResponsavelRepository()

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

        responsavel_salvo = repo_responsavel.salvar(responsavel_novo)

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
            turma_id=str(inscricao_salva.turma.id) if inscricao_salva.turma else None  # ✅ ADICIONADO
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao criar inscrição: {str(e)}")


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
                turma_id=i.get("turma_id")  # ✅ ADICIONADO
            )
            for i in inscricoes
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao listar inscrições: {str(e)}")


@router.get(
    "/inscricoes/pendentes-distribuicao",
    response_model=List[InscricaoResponse],
)
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
            turma_id=str(inscricao.turma.id) if inscricao.turma else None  # ✅ ADICIONADO
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar inscrição: {str(e)}")


@router.post("/inscricoes/{inscricao_id}/documentos")
def upload_documento(
        inscricao_id: str,
        file: UploadFile = File(...),
        tipo_documento: str = Form(...)
):
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
                "observacao_validacao": d.observacao_validacao  # ✅ ADICIONADO
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
def atribuir_turma_inscricao(inscricao_id: str, turma_id: str):
    """Atribui uma turma a uma inscrição."""
    try:
        repo = InscricaoRepository()
        inscricao = repo.atribuir_turma(inscricao_id, turma_id)

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

@router.get("/inscricoes/contar-por-turma/{turma_id}")
def contar_inscricoes_por_turma(turma_id: str):
    """Conta quantas inscrições (qualquer status) existem para uma turma específica."""
    try:
        repo = InscricaoRepository()
        count = repo.contar_inscricoes_por_turma(turma_id)

        return {"count": count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao contar inscrições: {str(e)}")

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