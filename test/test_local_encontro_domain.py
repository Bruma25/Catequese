# test/test_local_encontro_domain.py

import pytest

from app.domain.localEncontro import LocalEncontro


def test_local_encontro_criacao_valida():
    local = LocalEncontro(
        id=1,
        codigo="SALA_1",
        nome_exibicao="Sala 1 - Subsolo",
    )

    assert local.id == 1
    assert local.codigo == "SALA_1"
    assert local.nome_exibicao == "Sala 1 - Subsolo"


def test_local_encontro_normaliza_codigo_e_nome_exibicao():
    local = LocalEncontro(
        id=1,
        codigo="  sala_1  ",
        nome_exibicao="  Sala 1 - Subsolo  ",
    )

    assert local.codigo == "SALA_1"
    assert local.nome_exibicao == "Sala 1 - Subsolo"


def test_local_encontro_nao_permite_id_nulo():
    with pytest.raises(ValueError, match=r"id do local de encontro"):
        LocalEncontro(
            id=None,
            codigo="SALA_1",
            nome_exibicao="Sala 1 - Subsolo",
        )


def test_local_encontro_nao_permite_id_nao_inteiro():
    with pytest.raises(ValueError, match=r"id do local de encontro deve ser um inteiro"):
        LocalEncontro(
            id="1",
            codigo="SALA_1",
            nome_exibicao="Sala 1 - Subsolo",
        )


def test_local_encontro_nao_permite_id_menor_ou_igual_a_zero():
    with pytest.raises(ValueError, match=r"id do local de encontro deve ser maior que zero"):
        LocalEncontro(
            id=0,
            codigo="SALA_1",
            nome_exibicao="Sala 1 - Subsolo",
        )


def test_local_encontro_nao_permite_codigo_vazio():
    with pytest.raises(ValueError, match=r"código do local de encontro"):
        LocalEncontro(
            id=1,
            codigo="   ",
            nome_exibicao="Sala 1 - Subsolo",
        )


def test_local_encontro_nao_permite_nome_exibicao_vazio():
    with pytest.raises(ValueError, match=r"nome de exibição do local de encontro"):
        LocalEncontro(
            id=1,
            codigo="SALA_1",
            nome_exibicao="   ",
        )


def test_local_encontro_eh_retorna_true_para_mesmo_codigo():
    local = LocalEncontro(
        id=1,
        codigo="SALA_1",
        nome_exibicao="Sala 1 - Subsolo",
    )

    assert local.eh("SALA_1") is True


def test_local_encontro_eh_retorna_true_para_codigo_com_case_diferente_e_espacos():
    local = LocalEncontro(
        id=1,
        codigo="SALA_1",
        nome_exibicao="Sala 1 - Subsolo",
    )

    assert local.eh("  sala_1  ") is True


def test_local_encontro_eh_retorna_false_para_codigo_diferente():
    local = LocalEncontro(
        id=1,
        codigo="SALA_1",
        nome_exibicao="Sala 1 - Subsolo",
    )

    assert local.eh("IGREJA") is False


def test_local_encontro_eh_retorna_false_para_none():
    local = LocalEncontro(
        id=1,
        codigo="SALA_1",
        nome_exibicao="Sala 1 - Subsolo",
    )

    assert local.eh(None) is False


def test_local_encontro_eh_retorna_false_para_string_vazia():
    local = LocalEncontro(
        id=1,
        codigo="SALA_1",
        nome_exibicao="Sala 1 - Subsolo",
    )

    assert local.eh("") is False
    assert local.eh("   ") is False