# test/test_sacramento_domain.py

import pytest

from app.domain.sacramento import Sacramento


def test_sacramento_criacao_valida():
    sacramento = Sacramento(
        id=1,
        codigo="BATISMO",
        nome_exibicao="Batismo",
    )

    assert sacramento.id == 1
    assert sacramento.codigo == "BATISMO"
    assert sacramento.nome_exibicao == "Batismo"


def test_sacramento_normaliza_codigo_e_nome_exibicao():
    sacramento = Sacramento(
        id=1,
        codigo="  batismo  ",
        nome_exibicao="  Batismo  ",
    )

    assert sacramento.codigo == "BATISMO"
    assert sacramento.nome_exibicao == "Batismo"


def test_sacramento_nao_permite_id_nulo():
    with pytest.raises(ValueError, match=r"id do sacramento"):
        Sacramento(
            id=None,
            codigo="BATISMO",
            nome_exibicao="Batismo",
        )


def test_sacramento_nao_permite_id_nao_inteiro():
    with pytest.raises(ValueError, match=r"id do sacramento deve ser um inteiro"):
        Sacramento(
            id="1",
            codigo="BATISMO",
            nome_exibicao="Batismo",
        )


def test_sacramento_nao_permite_id_menor_ou_igual_a_zero():
    with pytest.raises(ValueError, match=r"id do sacramento deve ser maior que zero"):
        Sacramento(
            id=0,
            codigo="BATISMO",
            nome_exibicao="Batismo",
        )


def test_sacramento_nao_permite_codigo_vazio():
    with pytest.raises(ValueError, match=r"código do sacramento"):
        Sacramento(
            id=1,
            codigo="   ",
            nome_exibicao="Batismo",
        )


def test_sacramento_nao_permite_nome_exibicao_vazio():
    with pytest.raises(ValueError, match=r"nome de exibição do sacramento"):
        Sacramento(
            id=1,
            codigo="BATISMO",
            nome_exibicao="   ",
        )


def test_sacramento_eh_retorna_true_para_mesmo_codigo():
    sacramento = Sacramento(
        id=1,
        codigo="BATISMO",
        nome_exibicao="Batismo",
    )

    assert sacramento.eh("BATISMO") is True


def test_sacramento_eh_retorna_true_para_codigo_com_case_diferente_e_espacos():
    sacramento = Sacramento(
        id=1,
        codigo="BATISMO",
        nome_exibicao="Batismo",
    )

    assert sacramento.eh("  batismo  ") is True


def test_sacramento_eh_retorna_false_para_codigo_diferente():
    sacramento = Sacramento(
        id=1,
        codigo="BATISMO",
        nome_exibicao="Batismo",
    )

    assert sacramento.eh("EUCARISTIA") is False


def test_sacramento_eh_retorna_false_para_none():
    sacramento = Sacramento(
        id=1,
        codigo="BATISMO",
        nome_exibicao="Batismo",
    )

    assert sacramento.eh(None) is False


def test_sacramento_eh_retorna_false_para_string_vazia():
    sacramento = Sacramento(
        id=1,
        codigo="BATISMO",
        nome_exibicao="Batismo",
    )

    assert sacramento.eh("") is False
    assert sacramento.eh("   ") is False