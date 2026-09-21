# app/routes/usuario.py
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from pydantic import BaseModel
import uuid

from app.repositories.usuarioRepository import UsuarioRepository
from app.domain.tipoPapelUsuario import TipoPapelUsuario
from app.infra.supabaseClient import get_supabase

router = APIRouter(prefix="/usuarios", tags=["usuarios"])


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


class AtualizarPapeisRequest(BaseModel):
    papeis_ids: List[int]


class UsuarioCreate(BaseModel):
    nome: str
    email: str
    papeis_ids: List[int] = []


class UsuarioUpdate(BaseModel):
    nome: Optional[str] = None
    email: Optional[str] = None
    papeis_ids: Optional[List[int]] = None


# --- Endpoints ---

@router.get("/me", response_model=UsuarioResponse)
def buscar_usuario_atual():
    """
    Busca informações do usuário autenticado.
    Requer autenticação via Supabase Auth.
    """
    return UsuarioResponse(
        id="temp",
        nome="Usuário Teste",
        email="teste@exemplo.com",
        papeis=[]
    )


@router.get("/tipos-papel", response_model=List[PapelResponse])
def listar_papeis():
    """
    Lista todos os tipos de papel disponíveis.
    """
    try:
        supabase = get_supabase()

        result = (
            supabase
            .table("tipo_papel_usuario")
            .select("id, codigo, descricao")
            .order("descricao")
            .execute()
        )

        return [
            PapelResponse(
                id=p["id"],
                codigo=p["codigo"],
                descricao=p["descricao"]
            )
            for p in result.data
        ]

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao listar papéis: {str(e)}")


@router.get("", response_model=List[UsuarioResponse])
def listar_usuarios():
    """
    Lista todos os usuários com seus papéis.
    """
    try:
        supabase = get_supabase()

        result = (
            supabase
            .table("usuario")
            .select("id, nome, email, created_at, updated_at")
            .order("nome")
            .execute()
        )

        usuarios = []
        for item in result.data:
            usuario_id = item.get("id")

            if not usuario_id or not isinstance(usuario_id, str):
                continue

            papeis_result = (
                supabase
                .table("usuario_papel")
                .select("""
                    papel_id,
                    tipo_papel_usuario(
                        id,
                        codigo,
                        descricao
                    )
                """)
                .eq("usuario_id", usuario_id)
                .execute()
            )

            papeis = []
            for papel_item in papeis_result.data or []:
                papel_data = papel_item.get("tipo_papel_usuario")
                if papel_data:
                    papeis.append({
                        "id": papel_data["id"],
                        "codigo": papel_data["codigo"],
                        "descricao": papel_data["descricao"]
                    })

            usuarios.append(
                UsuarioResponse(
                    id=usuario_id,
                    nome=item["nome"],
                    email=item["email"],
                    papeis=papeis
                )
            )

        return usuarios

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao listar usuários: {str(e)}")


@router.post("", response_model=UsuarioResponse)
def criar_usuario(dados: UsuarioCreate):
    """
    Cria um novo usuário com papéis opcionais.
    Apenas coordenador geral pode usar este endpoint.
    """
    try:
        supabase = get_supabase()
        repo = UsuarioRepository()

        # 1. Verificar se email já existe
        usuario_existente = repo.buscar_por_email(dados.email)
        if usuario_existente:
            raise HTTPException(
                status_code=400,
                detail=f"Email '{dados.email}' já está em uso"
            )

        # 2. Criar usuário no Supabase Auth
        auth_result = supabase.auth.admin.create_user({
            "email": dados.email,
            "password": "senha_temporaria_123",
            "email_confirm": True,
            "user_metadata": {
                "nome": dados.nome
            }
        })

        if not auth_result.user:
            raise HTTPException(status_code=500, detail="Não foi possível criar o usuário no Auth")

        usuario_id = auth_result.user.id

        # 3. Verificar se já existe na tabela usuario
        usuario_na_tabela = repo.buscar_por_id(usuario_id)

        if usuario_na_tabela:
            # Usuário já existe, apenas atualiza dados e papéis
            update_data = {
                "nome": dados.nome,
                "email": dados.email
            }

            supabase.table("usuario").update(update_data).eq("id", usuario_id).execute()

            # Atualizar papéis
            supabase.table("usuario_papel").delete().eq("usuario_id", usuario_id).execute()

            if dados.papeis_ids:
                papeis_payload = [
                    {"usuario_id": usuario_id, "papel_id": papel_id}
                    for papel_id in dados.papeis_ids
                ]
                supabase.table("usuario_papel").insert(papeis_payload).execute()

            # Buscar usuário atualizado
            usuario = repo.buscar_por_id(usuario_id)

            return UsuarioResponse(
                id=usuario.id,
                nome=usuario.nome,
                email=usuario.email,
                papeis=[
                    {"id": p.id, "codigo": p.codigo, "descricao": p.descricao}
                    for p in usuario.papeis
                ]
            )

        # 4. Criar na tabela usuario (usuário novo)
        result = (
            supabase
            .table("usuario")
            .insert({
                "id": usuario_id,
                "nome": dados.nome,
                "email": dados.email
            })
            .execute()
        )

        if not result.data:
            # Rollback: excluir do Auth
            supabase.auth.admin.delete_user(usuario_id)
            raise HTTPException(status_code=500, detail="Não foi possível criar o usuário na tabela")

        # 5. Atribuir papéis
        if dados.papeis_ids:
            papeis_payload = [
                {"usuario_id": usuario_id, "papel_id": papel_id}
                for papel_id in dados.papeis_ids
            ]

            supabase.table("usuario_papel").insert(papeis_payload).execute()

        # 6. Buscar usuário criado
        usuario = repo.buscar_por_id(usuario_id)

        if not usuario:
            raise HTTPException(status_code=500, detail="Usuário criado mas não pôde ser buscado")

        return UsuarioResponse(
            id=usuario.id,
            nome=usuario.nome,
            email=usuario.email,
            papeis=[
                {"id": p.id, "codigo": p.codigo, "descricao": p.descricao}
                for p in usuario.papeis
            ]
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao criar usuário: {str(e)}")


@router.get("/{usuario_id}", response_model=UsuarioResponse)
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


@router.put("/{usuario_id}", response_model=UsuarioResponse)
def editar_usuario(usuario_id: str, dados: UsuarioUpdate):
    """
    Edita um usuário existente (nome, email e papéis).
    Apenas coordenador geral pode usar este endpoint.
    """
    try:
        supabase = get_supabase()
        repo = UsuarioRepository()

        # Verificar se usuário existe
        usuario_existente = repo.buscar_por_id(usuario_id)
        if not usuario_existente:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")

        # Atualizar dados básicos
        update_data = {}
        if dados.nome is not None:
            update_data["nome"] = dados.nome
        if dados.email is not None:
            update_data["email"] = dados.email

        if update_data:
            supabase.table("usuario").update(update_data).eq("id", usuario_id).execute()

        # Atualizar papéis se fornecidos
        if dados.papeis_ids is not None:
            # Buscar papéis atuais
            papeis_atuais_result = (
                supabase
                .table("usuario_papel")
                .select("papel_id")
                .eq("usuario_id", usuario_id)
                .execute()
            )
            papeis_atuais_ids = [p["papel_id"] for p in papeis_atuais_result.data or []]

            # Remover papéis antigos
            supabase.table("usuario_papel").delete().eq("usuario_id", usuario_id).execute()

            # Adicionar novos papéis
            if dados.papeis_ids:
                papeis_payload = [
                    {"usuario_id": usuario_id, "papel_id": papel_id}
                    for papel_id in dados.papeis_ids
                ]
                supabase.table("usuario_papel").insert(papeis_payload).execute()

            # Criar registros nas tabelas específicas
            # Papel 2 = CATEQUISTA
            if 2 in dados.papeis_ids and 2 not in papeis_atuais_ids:
                catequista_existente = (
                    supabase
                    .table("catequista")
                    .select("id")
                    .eq("usuario_id", usuario_id)
                    .maybe_single()
                    .execute()
                )

                if not catequista_existente.data:
                    supabase.table("catequista").insert({
                        "id": str(uuid.uuid4()),
                        "usuario_id": usuario_id,
                        "nome": usuario_existente.nome,
                        "email": usuario_existente.email,
                        "telefone": None
                    }).execute()

            # Papel 3 = COORDENADOR_ETAPA
            if 3 in dados.papeis_ids and 3 not in papeis_atuais_ids:
                coord_existente = (
                    supabase
                    .table("coordenador_etapa")
                    .select("id")
                    .eq("usuario_id", usuario_id)
                    .maybe_single()
                    .execute()
                )

                if not coord_existente.data:
                    supabase.table("coordenador_etapa").insert({
                        "id": str(uuid.uuid4()),
                        "usuario_id": usuario_id,
                        "nome": usuario_existente.nome,
                        "email": usuario_existente.email,
                        "telefone": None
                    }).execute()

            # Remover das tabelas específicas quando remover papel
            # Remover de catequista se papel 2 foi removido
            if 2 not in dados.papeis_ids and 2 in papeis_atuais_ids:
                supabase.table("catequista").delete().eq("usuario_id", usuario_id).execute()

            # Remover de coordenador_etapa se papel 3 foi removido
            if 3 not in dados.papeis_ids and 3 in papeis_atuais_ids:
                supabase.table("coordenador_etapa").delete().eq("usuario_id", usuario_id).execute()

        # Buscar usuário atualizado
        usuario_atualizado = repo.buscar_por_id(usuario_id)

        return UsuarioResponse(
            id=usuario_atualizado.id,
            nome=usuario_atualizado.nome,
            email=usuario_atualizado.email,
            papeis=[
                {
                    "id": papel.id,
                    "codigo": papel.codigo,
                    "descricao": papel.descricao
                }
                for papel in usuario_atualizado.papeis
            ]
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao editar usuário: {str(e)}")


@router.delete("/{usuario_id}")
def excluir_usuario(usuario_id: str):
    """
    Exclui um usuário e seus papéis associados.
    Apenas coordenador geral pode usar este endpoint.
    """
    try:
        supabase = get_supabase()
        repo = UsuarioRepository()

        # Verificar se usuário existe
        usuario = repo.buscar_por_id(usuario_id)
        if not usuario:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")

        # Remover papéis associados
        supabase.table("usuario_papel").delete().eq("usuario_id", usuario_id).execute()

        # Excluir usuário
        supabase.table("usuario").delete().eq("id", usuario_id).execute()

        return {"message": "Usuário excluído com sucesso"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao excluir usuário: {str(e)}")


@router.get("/{usuario_id}/papeis", response_model=List[PapelResponse])
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


@router.put("/{usuario_id}/papeis", response_model=List[PapelResponse])
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