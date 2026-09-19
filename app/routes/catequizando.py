# routes/catequizando.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from datetime import date, datetime

from app.repositories.catequizandoRepository import CatequizandoRepository
from app.infra.supabaseClient import get_supabase

router = APIRouter()


class CatequizandoUpdate(BaseModel):
    nome: Optional[str] = None
    data_nascimento: Optional[str] = None  # ✅ String no formato YYYY-MM-DD
    observacoes: Optional[str] = None
    endereco: Optional[str] = None
    telefone: Optional[str] = None
    email: Optional[str] = None
    necessidade_especial: Optional[bool] = None
    descricao_necessidade_especial: Optional[str] = None


@router.get("/{catequizando_id}")
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


@router.put("/{catequizando_id}")
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

        # Converter string date para date object
        if 'data_nascimento' in update_data and update_data['data_nascimento']:
            update_data['data_nascimento'] = datetime.strptime(update_data['data_nascimento'], '%Y-%m-%d').date()

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