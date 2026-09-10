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
    catequizando_sacramentos: List[int]  # IDs dos sacramentos
    etapa_id: str
    responsavel_nome: str
    responsavel_email: Optional[str] = None
    responsavel_telefone: str
    responsavel_vinculo: int  # ID do tipo_vinculo_responsavel


class InscricaoResponse(BaseModel):
    id: str
    catequizando_nome: str
    etapa_id: str
    status_id: int
    responsavel_nome: str
    created_at: Optional[str] = None


class EtapaResponse(BaseModel):
    id: str
    nome: str
    ano_nascimento_min: Optional[int] = None
    ano_nascimento_max: Optional[int] = None
    sacramentos_requeridos: List[int]

class SacramentoResponse(BaseModel):
    id: int
    codigo: str
    nome_exibicao: str
    ordem: Optional[int] = None


class TipoVinculoResponse(BaseModel):
    id: int
    codigo: str
    descricao: str

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
                ano_nascimento_min=e["ano_nascimento_min"],
                ano_nascimento_max=e["ano_nascimento_max"],
                sacramentos_requeridos=e["sacramentos_requeridos"]
            )
            for e in etapas
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao listar etapas: {str(e)}")

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

@router.post("/inscricoes", response_model=InscricaoResponse)
def criar_inscricao(inscricao_data: InscricaoCreate):
    """
    Cria uma nova inscrição de catequizando.

    Fluxo:
    1. Cria catequizando no banco
    2. Cria responsável no banco
    3. Cria vínculo entre eles
    4. Busca etapa e status
    5. Valida regras de domínio
    6. Cria e salva inscrição
    """
    try:
        supabase = get_supabase()

        # 1. Buscar etapa no banco
        etapa_db = supabase.table("etapa").select("*").eq("id", inscricao_data.etapa_id).maybe_single().execute()

        if not etapa_db.data:
            raise HTTPException(status_code=400, detail=f"Etapa {inscricao_data.etapa_id} não encontrada")

        etapa_data = etapa_db.data

        # Buscar sacramentos requeridos da etapa
        sacramentos_req = supabase.table("etapa_sacramento_requerido").select("sacramento_id").eq("etapa_id",
                                                                                                  inscricao_data.etapa_id).execute()
        sacramentos_ids = [s["sacramento_id"] for s in sacramentos_req.data] if sacramentos_req.data else []

        etapa = Etapa(
            id=etapa_data["id"],
            nome=etapa_data["nome"],
            descricao=etapa_data.get("descricao"),
            ano_nasc_minimo=etapa_data.get("ano_nasc_minimo"),
            ano_nasc_maximo=etapa_data.get("ano_nasc_maximo"),
            sacramentos_requeridos=[],  # TODO: buscar sacramentos se necessário
            sacramentos_proibidos=[],
        )

        # 2. Criar catequizando (sem ID ainda, o banco vai gerar)
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

        # 3. Criar responsável (sem ID ainda)
        responsavel_novo = Responsavel(
            id=str(uuid.uuid4()),
            nome=inscricao_data.responsavel_nome,
            email=inscricao_data.responsavel_email,
            telefone=inscricao_data.responsavel_telefone,
            usuario=None,
            vinculos=[],
        )

        # 4. Salvar catequizando e responsável
        repo_catequizando = CatequizandoRepository()
        repo_responsavel = ResponsavelRepository()

        # Salvar catequizando
        catequizando_salvo = repo_catequizando.salvar(catequizando_novo)

        # Salvar responsável
        responsavel_salvo = repo_responsavel.salvar(responsavel_novo)

        # 5. Criar vínculo entre responsável e catequizando
        # Buscar tipo de vínculo (ex: "pai", "mae", "outro")
        tipo_vinculo_db = supabase.table("tipo_vinculo_responsavel").select("*").eq("id",
                                                                                    inscricao_data.responsavel_vinculo).maybe_single().execute()

        if not tipo_vinculo_db.data:
            raise HTTPException(status_code=400,
                                detail=f"Tipo de vínculo {inscricao_data.responsavel_vinculo} não encontrado")

        tipo_vinculo = TipoVinculoResponsavel(
            id=tipo_vinculo_db.data["id"],
            codigo=tipo_vinculo_db.data["codigo"],
            descricao=tipo_vinculo_db.data["descricao"],
        )

        # Criar vínculo
        vinculo = CatequizandoResponsavel(
            catequizando=catequizando_salvo,
            responsavel=responsavel_salvo,
            tipo_vinculo=tipo_vinculo,
            descricao_outro=None,
        )
        vinculo.validar()

        # Adicionar vínculo ao catequizando
        catequizando_salvo.adicionar_vinculo_responsavel(vinculo)
        responsavel_salvo.adicionar_vinculo(vinculo)

        # Sincronizar vínculo no banco
        repo_catequizando.sincronizar_vinculos_responsaveis(catequizando_salvo)

        # 6. Buscar status "pendente de distribuição"
        status_db = supabase.table("status_inscricao").select("*").eq("codigo",
                                                                      "pendente_distribuicao").maybe_single().execute()

        if not status_db.data:
            raise HTTPException(status_code=500, detail="Status 'pendente_distribuicao' não encontrado")

        status = StatusInscricao(
            id=status_db.data["id"],
            codigo=status_db.data["codigo"],
            descricao=status_db.data["descricao"],
        )

        # 7. Validar regras de domínio
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

        # 8. Criar serviço e inscrever
        servico = ServicoInscricao(status_pendente_distribuicao=status)

        inscricao = servico.criar_inscricao(
            id_inscricao=str(uuid.uuid4()),
            catequizando=catequizando_salvo,
            responsavel=responsavel_salvo,
            etapa=etapa,
            referencia_irmao=None,
            observacao_responsavel=None,
        )

        # 9. Salvar inscrição no banco
        repo_inscricao = InscricaoRepository()
        inscricao_salva = repo_inscricao.salvar(inscricao)

        return InscricaoResponse(
            id=inscricao_salva.id,
            catequizando_nome=inscricao_salva.catequizando.nome,
            etapa_id=inscricao_salva.etapa.id,
            status_id=inscricao_salva.status.id,
            responsavel_nome=inscricao_salva.responsavel.nome,
            created_at=str(inscricao_salva.data_inscricao) if inscricao_salva.data_inscricao else None
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
                created_at=i.get("created_at")
            )
            for i in inscricoes
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao listar inscrições: {str(e)}")


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
            created_at=str(inscricao.data_inscricao) if inscricao.data_inscricao else None
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
    """
    Faz upload de um documento para uma inscrição.
    """
    try:
        import tempfile
        import os

        # 1. Salvar arquivo temporariamente
        with tempfile.NamedTemporaryFile(delete=False,
                                         suffix=Path(file.filename).suffix if file.filename else "") as tmp:
            tmp.write(file.file.read())
            tmp_path = tmp.name

        try:
            # 2. Usar o serviço para enviar
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
            # 3. Limpar arquivo temporário
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
                "uploaded_at": str(d.created_at) if d.created_at else None
            }
            for d in documentos
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao listar documentos: {str(e)}")