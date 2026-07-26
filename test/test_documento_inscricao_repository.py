#test_documento_inscricao_repository.py
import uuid
from datetime import date

import pytest

from infra.supabaseClient import get_supabase
from domain.documentoInscricao import DocumentoInscricao
from repositories.documentoInscricaoRepository import DocumentoInscricaoRepository


@pytest.fixture(scope="module")
def db():
    return get_supabase()


@pytest.fixture
def documento_repo():
    return DocumentoInscricaoRepository()


def _criar_dados_base(db):
    etapa_id = str(uuid.uuid4())
    catequizando_id = str(uuid.uuid4())
    responsavel_id = str(uuid.uuid4())
    inscricao_id = str(uuid.uuid4())

    status_result = (
        db.table("status_inscricao")
        .select("id, codigo, descricao")
        .limit(1)
        .execute()
    )

    if not status_result.data:
        raise ValueError("A tabela status_inscricao precisa ter ao menos 1 registro para este teste.")

    db.table("etapa").insert({
        "id": etapa_id,
        "nome": f"Etapa Teste Doc {etapa_id[:8]}",
        "descricao": "Etapa temporária para teste de documento de inscrição.",
        "ano_nasc_minimo": 2000,
        "ano_nasc_maximo": 2020,
    }).execute()

    db.table("catequizando").insert({
        "id": catequizando_id,
        "nome": f"Catequizando Teste {catequizando_id[:8]}",
        "data_nascimento": date(2015, 5, 20).isoformat(),
        "observacoes": None,
        "endereco": None,
        "telefone": None,
        "email": None,
        "necessidade_especial": False,
        "descricao_necessidade_especial": None,
    }).execute()

    db.table("responsavel").insert({
        "id": responsavel_id,
        "nome": f"Responsável Teste {responsavel_id[:8]}",
        "email": f"resp.{responsavel_id[:8]}@teste.com",
        "telefone": "11999999999",
        "usuario_id": None,
    }).execute()

    db.table("inscricao").insert({
        "id": inscricao_id,
        "catequizando_id": catequizando_id,
        "responsavel_id": responsavel_id,
        "etapa_id": etapa_id,
        "turma_id": None,
        "status_id": status_result.data[0]["id"],
        "termo_assinado": False,
        "data_inscricao": None,
        "quer_mesma_turma_que_irmao": False,
        "referencia_irmao": None,
        "observacao_responsavel": None,
        "override_idade": False,
        "motivo_override": None,
        "usuario_override_id": None,
    }).execute()

    return {
        "etapa_id": etapa_id,
        "catequizando_id": catequizando_id,
        "responsavel_id": responsavel_id,
        "inscricao_id": inscricao_id,
    }


def _limpar_dados_base(db, dados):
    try:
        db.table("inscricao").delete().eq("id", dados["inscricao_id"]).execute()
    except Exception:
        pass
    try:
        db.table("responsavel").delete().eq("id", dados["responsavel_id"]).execute()
    except Exception:
        pass
    try:
        db.table("catequizando").delete().eq("id", dados["catequizando_id"]).execute()
    except Exception:
        pass
    try:
        db.table("etapa").delete().eq("id", dados["etapa_id"]).execute()
    except Exception:
        pass


@pytest.fixture(scope="module")
def dados_temporarios(db):
    dados = _criar_dados_base(db)
    yield dados
    _limpar_dados_base(db, dados)


@pytest.fixture
def documento_temporario(db, dados_temporarios, documento_repo):
    documento = DocumentoInscricao(
        id=None,
        inscricao_id=dados_temporarios["inscricao_id"],
        tipo_documento="identidade",
        nome_original="rg_frente.pdf",
        nome_arquivo="rg_frente_2026.pdf",
        caminho_storage=f"inscricoes/{dados_temporarios['inscricao_id']}/rg_frente_2026.pdf",
        bucket="inscricao-documentos",
        mime_type="application/pdf",
        tamanho_bytes=245760,
        status_validacao="pendente",
        observacao_validacao=None,
    )

    documento_salvo = documento_repo.salvar(documento)

    yield documento_salvo

    try:
        db.table("documento_inscricao").delete().eq("id", documento_salvo.id).execute()
    except Exception:
        pass


class TestDocumentoInscricaoRepository:
    def test_salvar(self, documento_temporario):
        assert documento_temporario is not None
        assert isinstance(documento_temporario, DocumentoInscricao)
        assert documento_temporario.id is not None
        assert documento_temporario.inscricao_id is not None
        assert documento_temporario.tipo_documento == "identidade"
        assert documento_temporario.status_validacao == "pendente"

    def test_buscar_por_id(self, documento_temporario, documento_repo):
        encontrado = documento_repo.buscar_por_id(documento_temporario.id)

        assert encontrado is not None
        assert isinstance(encontrado, DocumentoInscricao)
        assert encontrado.id == documento_temporario.id
        assert encontrado.inscricao_id == documento_temporario.inscricao_id
        assert encontrado.nome_arquivo == documento_temporario.nome_arquivo
        assert encontrado.caminho_storage == documento_temporario.caminho_storage

    def test_listar_por_inscricao(self, documento_temporario, documento_repo, dados_temporarios):
        documentos = documento_repo.listar_por_inscricao(dados_temporarios["inscricao_id"])

        assert len(documentos) >= 1
        assert all(isinstance(doc, DocumentoInscricao) for doc in documentos)
        assert any(doc.id == documento_temporario.id for doc in documentos)

    def test_editar(self, documento_temporario, documento_repo):
        documento_temporario.status_validacao = "aprovado"
        documento_temporario.observacao_validacao = "Documento validado no teste de regressão."
        documento_temporario.nome_arquivo = "rg_frente_validado_2026.pdf"
        documento_temporario.caminho_storage = (
            f"inscricoes/{documento_temporario.inscricao_id}/rg_frente_validado_2026.pdf"
        )

        editado = documento_repo.editar(documento_temporario)

        assert editado is not None
        assert isinstance(editado, DocumentoInscricao)
        assert editado.id == documento_temporario.id
        assert editado.status_validacao == "aprovado"
        assert editado.observacao_validacao == "Documento validado no teste de regressão."
        assert editado.nome_arquivo == "rg_frente_validado_2026.pdf"

    def test_apagar(self, documento_repo, dados_temporarios):
        documento = DocumentoInscricao(
            id=None,
            inscricao_id=dados_temporarios["inscricao_id"],
            tipo_documento="identidade",
            nome_original="rg_outro.pdf",
            nome_arquivo="rg_outro_2026.pdf",
            caminho_storage=f"inscricoes/{dados_temporarios['inscricao_id']}/rg_outro_2026.pdf",
            bucket="inscricao-documentos",
            mime_type="application/pdf",
            tamanho_bytes=245760,
            status_validacao="pendente",
            observacao_validacao=None,
        )

        salvo = documento_repo.salvar(documento)
        assert salvo is not None
        assert isinstance(salvo, DocumentoInscricao)
        assert salvo.id is not None

        apagado = documento_repo.apagar(salvo.id)
        assert apagado is True

        encontrado = documento_repo.buscar_por_id(salvo.id)
        assert encontrado is None