# test/test_status_inscricao_domain.py

import pytest

from domain.statusInscricao import StatusInscricao


def test_status_inscricao_criacao_valida():
    status = StatusInscricao(
        id=1,
        codigo="PENDENTE_DISTRIBUICAO",
        descricao="Pendente de distribuição",
    )

    assert status.id == 1
    assert status.codigo == "PENDENTE_DISTRIBUICAO"
    assert status.descricao == "Pendente de distribuição"


def test_status_inscricao_normaliza_codigo_e_descricao():
    status = StatusInscricao(
        id=1,
        codigo="  pendente_distribuicao  ",
        descricao="  Pendente de distribuição  ",
    )

    assert status.codigo == "PENDENTE_DISTRIBUICAO"
    assert status.descricao == "Pendente de distribuição"


def test_status_inscricao_nao_permite_id_nulo():
    with pytest.raises(ValueError, match=r"id do status da inscrição"):
        StatusInscricao(
            id=None,
            codigo="PENDENTE_DISTRIBUICAO",
            descricao="Pendente de distribuição",
        )


def test_status_inscricao_nao_permite_id_nao_inteiro():
    with pytest.raises(ValueError, match=r"id do status da inscrição deve ser um inteiro"):
        StatusInscricao(
            id="1",
            codigo="PENDENTE_DISTRIBUICAO",
            descricao="Pendente de distribuição",
        )


def test_status_inscricao_nao_permite_id_menor_ou_igual_a_zero():
    with pytest.raises(ValueError, match=r"id do status da inscrição deve ser maior que zero"):
        StatusInscricao(
            id=0,
            codigo="PENDENTE_DISTRIBUICAO",
            descricao="Pendente de distribuição",
        )


def test_status_inscricao_nao_permite_codigo_vazio():
    with pytest.raises(ValueError, match=r"código do status da inscrição"):
        StatusInscricao(
            id=1,
            codigo="   ",
            descricao="Pendente de distribuição",
        )


def test_status_inscricao_nao_permite_descricao_vazia():
    with pytest.raises(ValueError, match=r"descrição do status da inscrição"):
        StatusInscricao(
            id=1,
            codigo="PENDENTE_DISTRIBUICAO",
            descricao="   ",
        )


def test_status_inscricao_eh_retorna_true_para_mesmo_codigo():
    status = StatusInscricao(
        id=1,
        codigo="PENDENTE_DISTRIBUICAO",
        descricao="Pendente de distribuição",
    )

    assert status.eh("PENDENTE_DISTRIBUICAO") is True


def test_status_inscricao_eh_retorna_true_para_codigo_com_case_diferente_e_espacos():
    status = StatusInscricao(
        id=1,
        codigo="PENDENTE_DISTRIBUICAO",
        descricao="Pendente de distribuição",
    )

    assert status.eh("  pendente_distribuicao  ") is True


def test_status_inscricao_eh_retorna_false_para_codigo_diferente():
    status = StatusInscricao(
        id=1,
        codigo="PENDENTE_DISTRIBUICAO",
        descricao="Pendente de distribuição",
    )

    assert status.eh("CONFIRMADA") is False


def test_status_inscricao_eh_retorna_false_para_none():
    status = StatusInscricao(
        id=1,
        codigo="PENDENTE_DISTRIBUICAO",
        descricao="Pendente de distribuição",
    )

    assert status.eh(None) is False


def test_status_inscricao_eh_retorna_false_para_string_vazia():
    status = StatusInscricao(
        id=1,
        codigo="PENDENTE_DISTRIBUICAO",
        descricao="Pendente de distribuição",
    )

    assert status.eh("") is False
    assert status.eh("   ") is False