#test/test_storage_policies.py
import os
import uuid
import pytest
from supabase import create_client
from app.infra.supabaseClient import get_supabase

pytestmark = pytest.mark.integration

BUCKET = "inscricao-documentos"

png_minimo = (
    b"\x89PNG\r\n\x1a\n"
    b"\x00\x00\x00\rIHDR"
    b"\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00"
    b"\x90wS\xde"
    b"\x00\x00\x00\x0cIDAT\x08\xd7c\xf8\x0f\x00\x01\x01\x01\x00"
    b"\x18\xdd\x8d\xb1"
    b"\x00\x00\x00\x00IEND\xaeB`\x82"
)


def _require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        pytest.skip(f"Variável de ambiente ausente: {name}")
    return value


def criar_client_autenticado(email: str, password: str):
    supabase_url = _require_env("SUPABASE_URL")
    supabase_anon_key = _require_env("SUPABASE_ANON_KEY")

    client = create_client(supabase_url, supabase_anon_key)
    auth_result = client.auth.sign_in_with_password({
        "email": email,
        "password": password
    })
    assert auth_result is not None
    assert auth_result.session is not None
    return client


def try_create_signed_url(client, bucket: str, path: str):
    try:
        result = client.storage.from_(bucket).create_signed_url(path, 60)
        return True, result
    except Exception as e:
        return False, e


def try_remove(client, bucket: str, path: str):
    try:
        result = client.storage.from_(bucket).remove([path])
        return True, result
    except Exception as e:
        return False, e


@pytest.fixture
def supabase_admin():
    return get_supabase()


def test_storage_rls_dono_e_coordenador_geral(supabase_admin):
    senha = "SenhaTeste@123"

    email_a = f"usera.{uuid.uuid4()}@example.com"
    email_b = f"userb.{uuid.uuid4()}@example.com"
    email_coord = f"coord.{uuid.uuid4()}@example.com"

    auth_a_id = None
    auth_b_id = None
    auth_coord_id = None

    path_a = f"teste-politicas/{uuid.uuid4()}/arquivo-a.png"

    try:
        auth_a = supabase_admin.auth.admin.create_user({
            "email": email_a,
            "password": senha,
            "email_confirm": True,
            "user_metadata": {"nome": "Usuário A"},
        })
        auth_a_id = auth_a.user.id

        auth_b = supabase_admin.auth.admin.create_user({
            "email": email_b,
            "password": senha,
            "email_confirm": True,
            "user_metadata": {"nome": "Usuário B"},
        })
        auth_b_id = auth_b.user.id

        auth_coord = supabase_admin.auth.admin.create_user({
            "email": email_coord,
            "password": senha,
            "email_confirm": True,
            "user_metadata": {"nome": "Coordenador Geral"},
        })
        auth_coord_id = auth_coord.user.id

        supabase_admin.table("usuario").insert([
            {"id": auth_a_id, "nome": "Usuário A", "email": email_a},
            {"id": auth_b_id, "nome": "Usuário B", "email": email_b},
            {"id": auth_coord_id, "nome": "Coordenador Geral", "email": email_coord},
        ]).execute()

        papel = (
            supabase_admin.table("tipo_papel_usuario")
            .select("*")
            .eq("codigo", "coordenador_geral")
            .limit(1)
            .execute()
        )
        papel_data = papel.data or []
        assert len(papel_data) == 1, "Papel coordenador_geral não encontrado."

        papel_id = papel_data[0]["id"]

        supabase_admin.table("usuario_papel").insert({
            "usuario_id": auth_coord_id,
            "papel_id": papel_id
        }).execute()

        conferencia_join = (
            supabase_admin.table("usuario_papel")
            .select("usuario_id, papel_id, tipo_papel_usuario:papel_id(id, codigo, descricao)")
            .eq("usuario_id", auth_coord_id)
            .execute()
        )
        join_data = conferencia_join.data or []
        assert len(join_data) == 1
        assert join_data[0]["usuario_id"] == auth_coord_id
        assert join_data[0]["papel_id"] == papel_id
        assert join_data[0]["tipo_papel_usuario"]["codigo"] == "coordenador_geral"

        client_a = criar_client_autenticado(email_a, senha)
        client_b = criar_client_autenticado(email_b, senha)
        client_coord = criar_client_autenticado(email_coord, senha)

        upload_a = client_a.storage.from_(BUCKET).upload(
            path_a,
            png_minimo,
            {"content-type": "image/png"}
        )
        assert upload_a is not None

        ok_a, result_a = try_create_signed_url(client_a, BUCKET, path_a)
        assert ok_a is True, f"Usuário A deveria ler o próprio arquivo, mas falhou: {result_a}"

        ok_b_leitura, result_b_leitura = try_create_signed_url(client_b, BUCKET, path_a)
        assert ok_b_leitura is False, (
            f"Usuário B não deveria ler o arquivo de A, mas conseguiu: {result_b_leitura}"
        )

        ok_coord_leitura, result_coord_leitura = try_create_signed_url(client_coord, BUCKET, path_a)
        assert ok_coord_leitura is True, (
            f"Coordenador deveria ler o arquivo de A, mas falhou: {result_coord_leitura}"
        )

        ok_b_delete_exec, _ = try_remove(client_b, BUCKET, path_a)
        assert ok_b_delete_exec is True

        ok_a_apos_b, result_a_apos_b = try_create_signed_url(client_a, BUCKET, path_a)
        assert ok_a_apos_b is True, (
            f"Arquivo deveria continuar acessível após tentativa de exclusão por B: {result_a_apos_b}"
        )

        ok_coord_delete_exec, _ = try_remove(client_coord, BUCKET, path_a)
        assert ok_coord_delete_exec is True

        ok_a_apos_coord, result_a_apos_coord = try_create_signed_url(client_a, BUCKET, path_a)
        assert ok_a_apos_coord is False, (
            f"Arquivo não deveria existir/acessível após exclusão pelo coordenador: {result_a_apos_coord}"
        )

    finally:
        try:
            supabase_admin.storage.from_(BUCKET).remove([path_a])
        except Exception:
            pass

        try:
            if auth_coord_id:
                supabase_admin.table("usuario_papel").delete().eq("usuario_id", auth_coord_id).execute()
        except Exception:
            pass

        try:
            if auth_a_id:
                supabase_admin.table("usuario").delete().eq("id", auth_a_id).execute()
            if auth_b_id:
                supabase_admin.table("usuario").delete().eq("id", auth_b_id).execute()
            if auth_coord_id:
                supabase_admin.table("usuario").delete().eq("id", auth_coord_id).execute()
        except Exception:
            pass

        try:
            if auth_a_id:
                supabase_admin.auth.admin.delete_user(auth_a_id)
            if auth_b_id:
                supabase_admin.auth.admin.delete_user(auth_b_id)
            if auth_coord_id:
                supabase_admin.auth.admin.delete_user(auth_coord_id)
        except Exception:
            pass