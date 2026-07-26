#test/test_usuario_repository.py
import uuid

from infra.supabaseClient import get_supabase
from domain.usuario import Usuario
from domain.tipoPapelUsuario import TipoPapelUsuario
from repositories.usuarioRepository import UsuarioRepository


def test_usuario_repository_crud_basico():
    db = get_supabase()
    repo = UsuarioRepository()

    auth_user_id = None
    usuario_criado = False

    try:
        auth_response = db.auth.admin.create_user({
            "email": f"usuario.crud.{uuid.uuid4()}@example.com",
            "password": "SenhaTeste@123",
            "email_confirm": True,
            "user_metadata": {"nome": "Usuário Teste CRUD"},
        })
        auth_user_id = auth_response.user.id

        novo = Usuario(
            id=auth_user_id,
            nome="Usuário Teste CRUD",
            email=auth_response.user.email,
            papeis=[],
        )

        resultado_salvar = repo.salvar(novo)
        usuario_criado = True

        assert resultado_salvar is not None
        assert isinstance(resultado_salvar, Usuario)
        assert resultado_salvar.id == auth_user_id
        assert resultado_salvar.nome == "Usuário Teste CRUD"
        assert resultado_salvar.email == auth_response.user.email
        assert resultado_salvar.papeis == []

        buscado = repo.buscar_por_id(auth_user_id)

        assert buscado is not None
        assert isinstance(buscado, Usuario)
        assert buscado.id == auth_user_id
        assert buscado.nome == "Usuário Teste CRUD"
        assert buscado.email == auth_response.user.email
        assert buscado.papeis == []

        novo.nome = "Usuário Teste CRUD Editado"

        resultado_editar = repo.editar(novo)

        assert resultado_editar is not None
        assert isinstance(resultado_editar, Usuario)
        assert resultado_editar.id == auth_user_id
        assert resultado_editar.nome == "Usuário Teste CRUD Editado"
        assert resultado_editar.email == auth_response.user.email
        assert resultado_editar.papeis == []

        buscado_editado = repo.buscar_por_id(auth_user_id)

        assert buscado_editado is not None
        assert isinstance(buscado_editado, Usuario)
        assert buscado_editado.id == auth_user_id
        assert buscado_editado.nome == "Usuário Teste CRUD Editado"
        assert buscado_editado.email == auth_response.user.email
        assert buscado_editado.papeis == []

        resultado_apagar = repo.apagar(auth_user_id)
        assert resultado_apagar is True

        usuario_criado = False

        buscado_apos_apagar = repo.buscar_por_id(auth_user_id)
        assert buscado_apos_apagar is None

    finally:
        if usuario_criado and auth_user_id is not None:
            try:
                (
                    db.table("usuario_papel")
                    .delete()
                    .eq("usuario_id", auth_user_id)
                    .execute()
                )
            except Exception:
                pass

            try:
                repo.apagar(auth_user_id)
            except Exception:
                pass

        if auth_user_id is not None:
            try:
                db.auth.admin.delete_user(auth_user_id)
            except Exception:
                pass


def test_usuario_repository_busca_com_papeis():
    db = get_supabase()
    repo = UsuarioRepository()

    auth_user_id = None
    usuario_criado = False

    try:
        papeis_result = (
            db.table("tipo_papel_usuario")
            .select("*")
            .limit(2)
            .execute()
        )
        papeis_data = papeis_result.data or []

        assert len(papeis_data) >= 2, (
            "A tabela tipo_papel_usuario precisa ter ao menos 2 registros para este teste."
        )

        papel_1 = TipoPapelUsuario(
            id=papeis_data[0]["id"],
            codigo=papeis_data[0]["codigo"],
            descricao=papeis_data[0]["descricao"],
        )

        papel_2 = TipoPapelUsuario(
            id=papeis_data[1]["id"],
            codigo=papeis_data[1]["codigo"],
            descricao=papeis_data[1]["descricao"],
        )

        auth_response = db.auth.admin.create_user({
            "email": f"usuario.papeis.{uuid.uuid4()}@example.com",
            "password": "SenhaTeste@123",
            "email_confirm": True,
            "user_metadata": {"nome": "Usuário Teste Papéis"},
        })
        auth_user_id = auth_response.user.id

        usuario = Usuario(
            id=auth_user_id,
            nome="Usuário Teste Papéis",
            email=auth_response.user.email,
            papeis=[papel_1],
        )

        salvo = repo.salvar_com_papeis(usuario)
        usuario_criado = True

        assert salvo is not None
        assert isinstance(salvo, Usuario)
        assert salvo.id == auth_user_id
        assert salvo.nome == "Usuário Teste Papéis"
        assert salvo.email == auth_response.user.email
        assert len(salvo.papeis) == 1
        assert salvo.papeis[0].id == papel_1.id
        assert salvo.papeis[0].codigo == papel_1.codigo
        assert salvo.papeis[0].descricao == papel_1.descricao

        buscado = repo.buscar_por_id(auth_user_id)

        assert buscado is not None
        assert isinstance(buscado, Usuario)
        assert buscado.id == auth_user_id
        assert buscado.nome == "Usuário Teste Papéis"
        assert buscado.email == auth_response.user.email
        assert len(buscado.papeis) == 1
        assert buscado.papeis[0].id == papel_1.id
        assert buscado.papeis[0].codigo == papel_1.codigo

        usuario.nome = "Usuário Teste Papéis Editado"
        usuario.papeis = [papel_1, papel_2]

        editado = repo.editar_com_papeis(usuario)

        assert editado is not None
        assert isinstance(editado, Usuario)
        assert editado.id == auth_user_id
        assert editado.nome == "Usuário Teste Papéis Editado"
        assert editado.email == auth_response.user.email
        assert len(editado.papeis) == 2

        papeis_ids = {papel.id for papel in editado.papeis}
        assert papel_1.id in papeis_ids
        assert papel_2.id in papeis_ids

        buscado_editado = repo.buscar_por_id(auth_user_id)

        assert buscado_editado is not None
        assert isinstance(buscado_editado, Usuario)
        assert buscado_editado.id == auth_user_id
        assert buscado_editado.nome == "Usuário Teste Papéis Editado"
        assert buscado_editado.email == auth_response.user.email
        assert len(buscado_editado.papeis) == 2

        papeis_ids_buscados = {papel.id for papel in buscado_editado.papeis}
        assert papel_1.id in papeis_ids_buscados
        assert papel_2.id in papeis_ids_buscados

        resultado_apagar = repo.apagar(auth_user_id)
        assert resultado_apagar is True

        usuario_criado = False

        buscado_apos_apagar = repo.buscar_por_id(auth_user_id)
        assert buscado_apos_apagar is None

    finally:
        if usuario_criado and auth_user_id is not None:
            try:
                (
                    db.table("usuario_papel")
                    .delete()
                    .eq("usuario_id", auth_user_id)
                    .execute()
                )
            except Exception:
                pass

            try:
                repo.apagar(auth_user_id)
            except Exception:
                pass

        if auth_user_id is not None:
            try:
                db.auth.admin.delete_user(auth_user_id)
            except Exception:
                pass