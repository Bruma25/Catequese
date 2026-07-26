#test/test_servicos.py
import uuid
from datetime import date, datetime

import pytest

from app.infra.supabaseClient import get_supabase

from app.domain.responsavel import Responsavel
from app.domain.catequizando import Catequizando
from app.domain.etapa import Etapa
from app.domain.inscricao import Inscricao
from app.domain.statusInscricao import StatusInscricao
from app.domain.documentoInscricao import DocumentoInscricao

from app.repositories.responsavelRepository import ResponsavelRepository
from app.repositories.catequizandoRepository import CatequizandoRepository
from app.repositories.etapaRepository import EtapaRepository
from app.repositories.inscricaoRepository import InscricaoRepository

from app.services.servicoDocumentoInscricao import ServicoDocumentoInscricao


def garantir_status_inicial() -> StatusInscricao:
    db = get_supabase()

    resposta = (
        db.table("status_inscricao")
        .select("*")
        .eq("codigo", "pendente_distribuicao")
        .execute()
    )

    if resposta.data:
        row = resposta.data[0]
    else:
        insert_resp = (
            db.table("status_inscricao")
            .insert({
                "id": str(uuid.uuid4()),
                "codigo": "pendente_distribuicao",
                "descricao": "Pendente de distribuição",
            })
            .execute()
        )
        row = insert_resp.data[0]

    return StatusInscricao(
        id=row["id"],
        codigo=row["codigo"],
        descricao=row["descricao"],
    )


def criar_massa_minima_inscricao():
    responsavel_repo = ResponsavelRepository()
    catequizando_repo = CatequizandoRepository()
    etapa_repo = EtapaRepository()
    inscricao_repo = InscricaoRepository()

    responsavel_salvo = responsavel_repo.salvar(
        Responsavel(
            id=str(uuid.uuid4()),
            nome=f"Responsável Teste {uuid.uuid4().hex[:8]}",
            email=f"responsavel_{uuid.uuid4().hex[:8]}@teste.com",
            telefone="11999999999",
            usuario=None,
            vinculos=[],
        )
    )

    catequizando_salvo = catequizando_repo.salvar(
        Catequizando(
            id=str(uuid.uuid4()),
            nome=f"Catequizando Teste {uuid.uuid4().hex[:8]}",
            data_nascimento=date(2015, 5, 20),
            endereco="Rua Teste, 456",
            telefone="11988888888",
            email=f"catequizando_{uuid.uuid4().hex[:8]}@teste.com",
            observacoes="Criado para teste autocontido",
            necessidade_especial=False,
            descricao_necessidade_especial=None,
            vinculos_responsaveis=[],
            historico_sacramental=[],
        )
    )

    etapa_salva = etapa_repo.salvar(
        Etapa(
            id=str(uuid.uuid4()),
            nome=f"Etapa Teste {uuid.uuid4().hex[:8]}",
            descricao="Etapa criada para teste autocontido",
            ano_nasc_minimo=2010,
            ano_nasc_maximo=2018,
            sacramentos_requeridos=[],
            sacramentos_proibidos=[],
        )
    )

    status_inicial = garantir_status_inicial()

    inscricao_salva = inscricao_repo.salvar(
        Inscricao(
            id=str(uuid.uuid4()),
            catequizando=catequizando_salvo,
            responsavel=responsavel_salvo,
            etapa=etapa_salva,
            status=status_inicial,
            data_inscricao=datetime.now(),
            turma=None,
            termo_assinado=False,
            quer_mesma_turma_que_irmao=False,
            referencia_irmao=None,
            observacao_responsavel="Inscrição criada para teste autocontido",
            override_idade=False,
            motivo_override=None,
            usuario_override=None,
        )
    )

    return {
        "responsavel_repo": responsavel_repo,
        "catequizando_repo": catequizando_repo,
        "etapa_repo": etapa_repo,
        "inscricao_repo": inscricao_repo,
        "responsavel_salvo": responsavel_salvo,
        "catequizando_salvo": catequizando_salvo,
        "etapa_salva": etapa_salva,
        "status_inicial": status_inicial,
        "inscricao_salva": inscricao_salva,
    }


def limpar_massa_minima_inscricao(massa: dict):
    inscricao_salva = massa.get("inscricao_salva")
    etapa_salva = massa.get("etapa_salva")
    catequizando_salvo = massa.get("catequizando_salvo")
    responsavel_salvo = massa.get("responsavel_salvo")

    if inscricao_salva and getattr(inscricao_salva, "id", None):
        try:
            massa["inscricao_repo"].apagar(inscricao_salva.id)
        except Exception:
            pass

    if etapa_salva and getattr(etapa_salva, "id", None):
        try:
            massa["etapa_repo"].apagar(etapa_salva.id)
        except Exception:
            pass

    if catequizando_salvo and getattr(catequizando_salvo, "id", None):
        try:
            massa["catequizando_repo"].apagar(catequizando_salvo.id)
        except Exception:
            pass

    if responsavel_salvo and getattr(responsavel_salvo, "id", None):
        try:
            massa["responsavel_repo"].apagar(responsavel_salvo.id)
        except Exception:
            pass


@pytest.fixture
def service():
    return ServicoDocumentoInscricao()


@pytest.fixture
def massa_minima():
    massa = criar_massa_minima_inscricao()
    try:
        yield massa
    finally:
        limpar_massa_minima_inscricao(massa)


@pytest.fixture
def arquivo_pdf_temporario(tmp_path):
    arquivo = tmp_path / "documento_teste.pdf"
    arquivo.write_bytes(b"%PDF-1.4\n%teste regressivo servico documento inscricao\n")
    return arquivo


@pytest.fixture
def documento_enviado(service, massa_minima, arquivo_pdf_temporario):
    documento = service.enviar_documento(
        inscricao_id=massa_minima["inscricao_salva"].id,
        tipo_documento="identidade",
        caminho_arquivo_local=str(arquivo_pdf_temporario),
        nome_original="documento_teste_regressivo.pdf",
        bucket="inscricao-documentos",
    )

    try:
        yield documento
    finally:
        if documento is not None and getattr(documento, "id", None) is not None:
            try:
                service.apagar_documento(documento.id)
            except Exception:
                pass


def test_enviar_documento_fluxo_completo(service, massa_minima, documento_enviado):
    inscricao_salva = massa_minima["inscricao_salva"]

    assert inscricao_salva is not None
    assert inscricao_salva.id is not None

    assert documento_enviado is not None
    assert isinstance(documento_enviado, DocumentoInscricao)
    assert documento_enviado.id is not None
    assert documento_enviado.inscricao_id == inscricao_salva.id
    assert documento_enviado.tipo_documento == "identidade"
    assert documento_enviado.nome_original == "documento_teste_regressivo.pdf"
    assert documento_enviado.nome_arquivo is not None
    assert documento_enviado.caminho_storage is not None
    assert documento_enviado.bucket == "inscricao-documentos"
    assert documento_enviado.status_validacao == "pendente"
    assert documento_enviado.mime_type == "application/pdf"
    assert documento_enviado.tamanho_bytes is not None
    assert documento_enviado.tamanho_bytes >= 0

    documentos = service.documento_repository.listar_por_inscricao(inscricao_salva.id)

    assert documentos is not None
    assert len(documentos) >= 1
    assert all(isinstance(doc, DocumentoInscricao) for doc in documentos)
    assert any(doc.id == documento_enviado.id for doc in documentos)

    url_assinada = service.gerar_url_download(
        documento_id=documento_enviado.id,
        expires_in=3600,
    )

    assert url_assinada is not None
    assert isinstance(url_assinada, str)
    assert len(url_assinada) > 0


def test_servico_documento_inscricao_apagar_documento(service, massa_minima, arquivo_pdf_temporario):
    documento = service.enviar_documento(
        inscricao_id=massa_minima["inscricao_salva"].id,
        tipo_documento="identidade",
        caminho_arquivo_local=str(arquivo_pdf_temporario),
        nome_original="documento_teste_apagar.pdf",
        bucket="inscricao-documentos",
    )

    assert documento is not None
    assert isinstance(documento, DocumentoInscricao)
    assert documento.id is not None

    try:
        documento_encontrado = service.documento_repository.buscar_por_id(documento.id)
        assert documento_encontrado is not None
        assert isinstance(documento_encontrado, DocumentoInscricao)
        assert documento_encontrado.id == documento.id

        apagado = service.apagar_documento(documento.id)
        assert apagado is True

        documento = None

        documento_apos_exclusao = service.documento_repository.buscar_por_id(documento_encontrado.id)
        assert documento_apos_exclusao is None
    finally:
        if documento is not None and getattr(documento, "id", None) is not None:
            try:
                service.apagar_documento(documento.id)
            except Exception:
                pass