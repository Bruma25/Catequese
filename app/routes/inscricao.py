from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from typing import Optional, List
from datetime import date
from app.repositories.inscricaoRepository import InscricaoRepository
from app.repositories.documentoInscricaoRepository import DocumentoInscricaoRepository
from app.services.servicoDocumentoInscricao import ServicoDocumentoInscricao
from app.infra.supabaseClient import get_supabase

router = APIRouter()


# --- Pydantic Models para Request/Response ---

class InscricaoCreate(BaseModel):
    catequizando_nome: str
    catequizando_data_nascimento: date
    catequizando_sacramentos: List[int]  # IDs dos sacramentos
    etapa_id: int
    responsavel_nome: str
    responsavel_email: Optional[str] = None
    responsavel_telefone: str
    responsavel_vinculo: int  # ID do tipo_vinculo_responsavel


class InscricaoResponse(BaseModel):
    id: int
    catequizando_nome: str
    etapa_id: int
    status_id: int
    responsavel_nome: str
    created_at: Optional[str] = None


class EtapaResponse(BaseModel):
    id: int
    nome: str
    ano_nascimento_min: int
    ano_nascimento_max: int
    sacramentos_requeridos: List[int]


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


@router.post("/inscricoes", response_model=InscricaoResponse)
def criar_inscricao(inscricao_data: InscricaoCreate):
    """
    Cria uma nova inscrição de catequizando.

    - Cria o registro do catequizando
    - Cria o vínculo com responsável
    - Cria a inscrição
    """
    try:
        supabase = get_supabase()

        # Usar o serviço de inscrição para criar tudo de uma vez
        from app.domain.servicoInscricao import ServicoInscricao
        servico = ServicoInscricao(supabase)

        # Preparar dados no formato esperado pelo serviço
        dados_inscricao = {
            "catequizando": {
                "nome": inscricao_data.catequizando_nome,
                "data_nascimento": inscricao_data.catequizando_data_nascimento.isoformat(),
                "sacramentos": inscricao_data.catequizando_sacramentos
            },
            "responsavel": {
                "nome": inscricao_data.responsavel_nome,
                "email": inscricao_data.responsavel_email,
                "telefone": inscricao_data.responsavel_telefone,
                "vinculo_id": inscricao_data.responsavel_vinculo
            },
            "etapa_id": inscricao_data.etapa_id
        }

        inscricao = servico.criar_inscricao(dados_inscricao)

        return InscricaoResponse(
            id=inscricao["id"],
            catequizando_nome=inscricao["catequizando_nome"],
            etapa_id=inscricao["etapa_id"],
            status_id=inscricao["status_id"],
            responsavel_nome=inscricao["responsavel_nome"],
            created_at=inscricao.get("created_at")
        )

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
def buscar_inscricao(inscricao_id: int):
    """Busca uma inscrição específica pelo ID."""
    try:
        repo = InscricaoRepository()
        inscricao = repo.buscar_por_id(str(inscricao_id))

        if not inscricao:
            raise HTTPException(status_code=404, detail="Inscriçº£o não encontrada")

        return InscricaoResponse(
            id=inscricao["id"],
            catequizando_nome=inscricao["catequizando_nome"],
            etapa_id=inscricao["etapa_id"],
            status_id=inscricao["status_id"],
            responsavel_nome=inscricao["responsavel_nome"],
            created_at=inscricao.get("created_at")
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar inscrição: {str(e)}")


@router.post("/inscricoes/{inscricao_id}/documentos")
def upload_documento(
        inscricao_id: int,
        file: UploadFile = File(...),
        tipo_documento: str = Form(...)
):
    """
    Faz upload de um documento para uma inscrição.

    - Upload para o bucket do Supabase Storage
    - Cria registro na tabela documento_inscricao
    """
    try:
        supabase = get_supabase()
        servico = ServicoDocumentoInscricao(supabase)

        # Ler o arquivo
        file_content = file.file.read()

        # Fazer upload e criar registro
        documento = servico.upload_documento(
            inscricao_id=inscricao_id,
            file_name=file.filename,
            file_content=file_content,
            tipo_documento=tipo_documento
        )

        return {
            "id": documento["id"],
            "inscricao_id": documento["inscricao_id"],
            "file_name": documento["file_name"],
            "tipo_documento": documento["tipo_documento"],
            "storage_path": documento["storage_path"]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao upload documento: {str(e)}")


@router.get("/inscricoes/{inscricao_id}/documentos")
def listar_documentos(inscricao_id: int):
    """Lista todos os documentos de uma inscrição."""
    try:
        repo = DocumentoInscricaoRepository()
        documentos = repo.listar_por_inscricao(inscricao_id)

        return [
            {
                "id": d["id"],
                "inscricao_id": d["inscricao_id"],
                "file_name": d["file_name"],
                "tipo_documento": d["tipo_documento"],
                "storage_path": d["storage_path"],
                "uploaded_at": d.get("uploaded_at")
            }
            for d in documentos
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao listar documentos: {str(e)}")