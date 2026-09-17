from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from pydantic import BaseModel

from app.repositories.usuarioRepository import UsuarioRepository
from app.domain.usuario import Usuario
from app.domain.tipoPapelUsuario import TipoPapelUsuario
from app.infra.supabaseClient import get_supabase

router = APIRouter()


# --- Pydantic Models ---

class UsuarioResponse(BaseModel):
    id: str
    nome: str
    email: str
    papeis: List[dict] = []


class PapelResponse(BaseModel):
    id: int
    codigo: str
    descricao: str


class UsuarioPapeisResponse(BaseModel):
    usuario_id: str
    papeis: List[PapelResponse]


class AtualizarPapeisRequest(BaseModel):
    papeis_ids: List[int]


# --- Endpoints ---

@router.get("/usuarios/me", response_model=UsuarioResponse)
def buscar_usuario_atual():
    """
    Busca informações do usuário autenticado.
    Requer autenticação via Supabase Auth.
    """
    # TODO: Implementar autenticação JWT do Supabase
    # Por enquanto, retorna dados fixos para teste
    return UsuarioResponse(
        id="temp",
        nome="Usuário Teste",
        email="teste@exemplo.com",
        papeis=[]
    )


@router.get("/usuarios/{usuario_id}/papeis", response_model=List[PapelResponse])
def buscar_papeis_usuario(usuario_id: str):
    """
    Busca todos os papéis de um usuário específico.
    """
    try:
        repo = UsuarioRepository()
        usuario = repo.buscar_por_id(usuario_id)

        if not usuario:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")

        return [
            PapelResponse(
                id=papel.id,
                codigo=papel.codigo,
                descricao=papel.descricao
            )
            for papel in usuario.papeis
        ]

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar papéis: {str(e)}")


@router.put("/usuarios/{usuario_id}/papeis", response_model=List[PapelResponse])
def atualizar_papeis_usuario(usuario_id: str, dados: AtualizarPapeisRequest):
    """
    Atualiza os papéis de um usuário.
    Apenas coordenador geral pode usar este endpoint.
    """
    try:
        supabase = get_supabase()
        repo = UsuarioRepository()

        # Verificar se usuário existe
        usuario = repo.buscar_por_id(usuario_id)
        if not usuario:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")

        # Buscar papéis válidos
        papeis_validos = []
        for papel_id in dados.papeis_ids:
            papel_db = (
                supabase
                .table("tipo_papel_usuario")
                .select("*")
                .eq("id", papel_id)
                .maybe_single()
                .execute()
            )

            if not papel_db.data:
                raise HTTPException(
                    status_code=400,
                    detail=f"Papel {papel_id} não encontrado"
                )

            papeis_validos.append(
                TipoPapelUsuario(
                    id=papel_db.data["id"],
                    codigo=papel_db.data["codigo"],
                    descricao=papel_db.data["descricao"]
                )
            )

        # Atualizar papéis do usuário
        usuario.papeis = papeis_validos
        usuario_atualizado = repo.definir_papeis(usuario)

        return [
            PapelResponse(
                id=papel.id,
                codigo=papel.codigo,
                descricao=papel.descricao
            )
            for papel in usuario_atualizado.papeis
        ]

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao atualizar papéis: {str(e)}")


@router.get("/usuarios/{usuario_id}", response_model=UsuarioResponse)
def buscar_usuario(usuario_id: str):
    """
    Busca informações de um usuário específico.
    Apenas coordenador geral pode usar este endpoint.
    """
    try:
        repo = UsuarioRepository()
        usuario = repo.buscar_por_id(usuario_id)

        if not usuario:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")

        return UsuarioResponse(
            id=usuario.id,
            nome=usuario.nome,
            email=usuario.email,
            papeis=[
                {
                    "id": papel.id,
                    "codigo": papel.codigo,
                    "descricao": papel.descricao
                }
                for papel in usuario.papeis
            ]
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar usuário: {str(e)}")


@router.get("/usuarios", response_model=List[UsuarioResponse])
def listar_usuarios():
    """
    Lista todos os usuários.
    Apenas coordenador geral pode usar este endpoint.
    """
    try:
        repo = UsuarioRepository()
        result = (
            repo.db
            .table("usuario")
            .select("""
                id,
                nome,
                email,
                usuario_papel(
                    papel_id,
                    tipo_papel_usuario(
                        id,
                        codigo,
                        descricao
                    )
                )
            """)
            .execute()
        )

        usuarios = []
        for item in result.data:
            papeis = []
            for papel_item in item.get("usuario_papel", []):
                papel_data = papel_item.get("tipo_papel_usuario")
                if papel_data:
                    papeis.append({
                        "id": papel_data["id"],
                        "codigo": papel_data["codigo"],
                        "descricao": papel_data["descricao"]
                    })

            usuarios.append(
                UsuarioResponse(
                    id=item["id"],
                    nome=item["nome"],
                    email=item["email"],
                    papeis=papeis
                )
            )

        return usuarios

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao listar usuários: {str(e)}")