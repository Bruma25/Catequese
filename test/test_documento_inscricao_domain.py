# test/test_documento_inscricao_domain.py

import pytest
from datetime import datetime, timedelta

from domain.documentoInscricao import DocumentoInscricao


def criar_documento(
    id: str | None = "doc-1",
    inscricao_id: str = "insc-1",
    tipo_documento: str = "identidade",
    nome_original: str = "rg.pdf",
    nome_arquivo: str = "abc123.pdf",
    caminho_storage: str = "inscricoes/doc-1/abc123.pdf",
    bucket: str = "inscricao-documentos",
    mime_type: str | None = "application/pdf",
    tamanho_bytes: int | None = 1024,
    status_validacao: str = "pendente",
    observacao_validacao: str | None = None,
    created_at: datetime | None = None,
    updated_at: datetime | None = None,
) -> DocumentoInscricao:
    return DocumentoInscricao(
        id=id,
        inscricao_id=inscricao_id,
        tipo_documento=tipo_documento,
        nome_original=nome_original,
        nome_arquivo=nome_arquivo,
        caminho_storage=caminho_storage,
        bucket=bucket,
        mime_type=mime_type,
        tamanho_bytes=tamanho_bytes,
        status_validacao=status_validacao,
        observacao_validacao=observacao_validacao,
        created_at=created_at,
        updated_at=updated_at,
    )


def test_documento_criacao_valida():
    documento = criar_documento()

    assert documento.id == "doc-1"
    assert documento.inscricao_id == "insc-1"
    assert documento.tipo_documento == "identidade"
    assert documento.nome_original == "rg.pdf"
    assert documento.nome_arquivo == "abc123.pdf"
    assert documento.caminho_storage == "inscricoes/doc-1/abc123.pdf"
    assert documento.bucket == "inscricao-documentos"
    assert documento.mime_type == "application/pdf"
    assert documento.tamanho_bytes == 1024
    assert documento.status_validacao == "pendente"
    assert documento.observacao_validacao is None
    assert documento.created_at is None
    assert documento.updated_at is None


def test_documento_normaliza_campos_textuais():
    documento = criar_documento(
        id="  doc-1  ",
        inscricao_id="  insc-1  ",
        tipo_documento="  IDENTIDADE  ",
        nome_original="  rg.pdf  ",
        nome_arquivo="  abc123.pdf  ",
        caminho_storage="  inscricoes/doc-1/abc123.pdf  ",
        bucket="  inscricao-documentos  ",
        mime_type="  application/pdf  ",
        status_validacao="  PENDENTE  ",
        observacao_validacao="  observacao inicial  ",
    )

    assert documento.id == "doc-1"
    assert documento.inscricao_id == "insc-1"
    assert documento.tipo_documento == "identidade"
    assert documento.nome_original == "rg.pdf"
    assert documento.nome_arquivo == "abc123.pdf"
    assert documento.caminho_storage == "inscricoes/doc-1/abc123.pdf"
    assert documento.bucket == "inscricao-documentos"
    assert documento.mime_type == "application/pdf"
    assert documento.status_validacao == "pendente"
    assert documento.observacao_validacao == "observacao inicial"


def test_documento_normaliza_textos_opcionais_vazios_para_none():
    documento = criar_documento(
        id="   ",
        mime_type="   ",
        observacao_validacao="   ",
    )

    assert documento.id is None
    assert documento.mime_type is None
    assert documento.observacao_validacao is None


def test_documento_exige_inscricao_id():
    with pytest.raises(ValueError, match=r"inscricao_id é obrigatório"):
        criar_documento(inscricao_id="   ")


def test_documento_exige_tipo_documento():
    with pytest.raises(ValueError, match=r"tipo_documento é obrigatório"):
        criar_documento(tipo_documento="   ")


def test_documento_exige_nome_original():
    with pytest.raises(ValueError, match=r"nome_original é obrigatório"):
        criar_documento(nome_original="   ")


def test_documento_exige_nome_arquivo():
    with pytest.raises(ValueError, match=r"nome_arquivo é obrigatório"):
        criar_documento(nome_arquivo="   ")


def test_documento_exige_caminho_storage():
    with pytest.raises(ValueError, match=r"caminho_storage é obrigatório"):
        criar_documento(caminho_storage="   ")


def test_documento_exige_bucket():
    with pytest.raises(ValueError, match=r"bucket é obrigatório"):
        criar_documento(bucket="   ")


def test_documento_exige_status_validacao():
    with pytest.raises(ValueError, match=r"status_validacao é obrigatório"):
        criar_documento(status_validacao="   ")


def test_documento_nao_permite_tipo_documento_invalido():
    with pytest.raises(ValueError, match=r"Tipo de documento inválido"):
        criar_documento(tipo_documento="cpf")


def test_documento_nao_permite_status_validacao_invalido():
    with pytest.raises(ValueError, match=r"Status de validação inválido"):
        criar_documento(status_validacao="em_analise")


def test_documento_nao_permite_tamanho_bytes_negativo():
    with pytest.raises(ValueError, match=r"tamanho do documento em bytes não pode ser negativo"):
        criar_documento(tamanho_bytes=-1)


def test_documento_nao_permite_tamanho_bytes_nao_inteiro():
    with pytest.raises(ValueError, match=r"tamanho do documento em bytes deve ser um inteiro"):
        criar_documento(tamanho_bytes="1024")


def test_documento_nao_permite_created_at_invalido():
    with pytest.raises(ValueError, match=r"created_at deve ser um datetime válido"):
        criar_documento(created_at="2026-01-01")


def test_documento_nao_permite_updated_at_invalido():
    with pytest.raises(ValueError, match=r"updated_at deve ser um datetime válido"):
        criar_documento(updated_at="2026-01-01")


def test_documento_nao_permite_updated_at_anterior_a_created_at():
    created_at = datetime(2026, 1, 10, 10, 0, 0)
    updated_at = created_at - timedelta(minutes=1)

    with pytest.raises(ValueError, match=r"updated_at não pode ser anterior a created_at"):
        criar_documento(created_at=created_at, updated_at=updated_at)


def test_documento_rejeitado_exige_observacao_na_criacao():
    with pytest.raises(ValueError, match=r"Documento rejeitado deve possuir observação de validação"):
        criar_documento(
            status_validacao="rejeitado",
            observacao_validacao="   ",
        )


def test_documento_aprovar_sem_observacao():
    documento = criar_documento(
        status_validacao="pendente",
        observacao_validacao="observacao anterior",
    )

    documento.aprovar()

    assert documento.status_validacao == "aprovado"
    assert documento.observacao_validacao is None
    assert documento.esta_aprovado() is True
    assert documento.esta_pendente() is False
    assert documento.esta_rejeitado() is False
    assert documento.updated_at is not None
    assert documento.created_at is not None


def test_documento_aprovar_com_observacao():
    documento = criar_documento()

    documento.aprovar("  Documento legível e válido  ")

    assert documento.status_validacao == "aprovado"
    assert documento.observacao_validacao == "Documento legível e válido"
    assert documento.esta_aprovado() is True
    assert documento.updated_at is not None
    assert documento.created_at is not None


def test_documento_rejeitar_exige_observacao():
    documento = criar_documento()

    with pytest.raises(ValueError, match=r"observacao é obrigatório"):
        documento.rejeitar("   ")


def test_documento_rejeitar_com_observacao():
    documento = criar_documento()

    documento.rejeitar("  Arquivo ilegível  ")

    assert documento.status_validacao == "rejeitado"
    assert documento.observacao_validacao == "Arquivo ilegível"
    assert documento.esta_rejeitado() is True
    assert documento.esta_aprovado() is False
    assert documento.esta_pendente() is False
    assert documento.updated_at is not None
    assert documento.created_at is not None


def test_documento_marcar_pendente_sem_observacao():
    documento = criar_documento(
        status_validacao="aprovado",
        observacao_validacao="validado",
    )

    documento.marcar_pendente()

    assert documento.status_validacao == "pendente"
    assert documento.observacao_validacao is None
    assert documento.esta_pendente() is True
    assert documento.updated_at is not None
    assert documento.created_at is not None


def test_documento_marcar_pendente_com_observacao():
    documento = criar_documento(
        status_validacao="rejeitado",
        observacao_validacao="Arquivo ilegível",
    )

    documento.marcar_pendente("  Reenviado para nova análise  ")

    assert documento.status_validacao == "pendente"
    assert documento.observacao_validacao == "Reenviado para nova análise"
    assert documento.esta_pendente() is True
    assert documento.updated_at is not None
    assert documento.created_at is not None


def test_documento_transicoes_atualizam_updated_at():
    created_at = datetime(2026, 1, 10, 10, 0, 0)
    updated_at = datetime(2026, 1, 10, 10, 5, 0)
    documento = criar_documento(
        created_at=created_at,
        updated_at=updated_at,
    )

    documento.aprovar("ok")

    assert documento.created_at == created_at
    assert documento.updated_at is not None
    assert documento.updated_at >= updated_at


def test_documento_transicoes_definem_created_at_quando_ausente():
    documento = criar_documento(
        created_at=None,
        updated_at=None,
    )

    documento.rejeitar("Arquivo corrompido")

    assert documento.created_at is not None
    assert documento.updated_at is not None
    assert documento.updated_at >= documento.created_at


def test_documento_esta_pendente():
    documento = criar_documento(status_validacao="pendente")

    assert documento.esta_pendente() is True
    assert documento.esta_aprovado() is False
    assert documento.esta_rejeitado() is False


def test_documento_esta_aprovado():
    documento = criar_documento(
        status_validacao="aprovado",
        observacao_validacao="ok",
    )

    assert documento.esta_pendente() is False
    assert documento.esta_aprovado() is True
    assert documento.esta_rejeitado() is False


def test_documento_esta_rejeitado():
    documento = criar_documento(
        status_validacao="rejeitado",
        observacao_validacao="ilegível",
    )

    assert documento.esta_pendente() is False
    assert documento.esta_aprovado() is False
    assert documento.esta_rejeitado() is True


@pytest.mark.parametrize(
    "tipo_documento",
    [
        "comprovante_batismo",
        "comprovante_eucaristia",
        "comprovante_crisma",
        "comprovante_outro_sacramento",
    ],
)
def test_documento_reconhece_documento_sacramental(tipo_documento):
    documento = criar_documento(tipo_documento=tipo_documento)

    assert documento.eh_documento_sacramental() is True


@pytest.mark.parametrize(
    "tipo_documento",
    [
        "identidade",
        "outro",
    ],
)
def test_documento_reconhece_documento_nao_sacramental(tipo_documento):
    documento = criar_documento(tipo_documento=tipo_documento)

    assert documento.eh_documento_sacramental() is False


def test_documento_aprovar_remove_observacao_quando_recebe_texto_vazio():
    documento = criar_documento(
        status_validacao="rejeitado",
        observacao_validacao="Arquivo ilegível",
    )

    documento.aprovar("   ")

    assert documento.status_validacao == "aprovado"
    assert documento.observacao_validacao is None


def test_documento_marcar_pendente_remove_observacao_quando_recebe_texto_vazio():
    documento = criar_documento(
        status_validacao="rejeitado",
        observacao_validacao="Arquivo ilegível",
    )

    documento.marcar_pendente("   ")

    assert documento.status_validacao == "pendente"
    assert documento.observacao_validacao is None