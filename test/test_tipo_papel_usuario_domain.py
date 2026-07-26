# test/test_tipo_papel_usuario_domain.py

import pytest

from domain.tipoPapelUsuario import TipoPapelUsuario


def test_tipo_papel_usuario_criacao_valida():
    papel = TipoPapelUsuario(
        id=1,
        codigo="CATEQUISTA",
        descricao="Catequista",
    )

    assert papel.id == 1
    assert papel.codigo == "CATEQUISTA"
    assert papel.descricao == "Catequista"


def test_tipo_papel_usuario_normaliza_codigo_e_descricao():
    papel = TipoPapelUsuario(
        id=1,
        codigo="  catequista  ",
        descricao="  Catequista  ",
    )

    assert papel.codigo == "CATEQUISTA"
    assert papel.descricao == "Catequista"


def test_tipo_papel_usuario_nao_permite_id_nulo():
    with pytest.raises(ValueError, match=r"id do tipo de papel do usuário"):
        TipoPapelUsuario(
            id=None,
            codigo="CATEQUISTA",
            descricao="Catequista",
        )


def test_tipo_papel_usuario_nao_permite_id_nao_inteiro():
    with pytest.raises(ValueError, match=r"id do tipo de papel do usuário deve ser um inteiro"):
        TipoPapelUsuario(
            id="1",
            codigo="CATEQUISTA",
            descricao="Catequista",
        )


def test_tipo_papel_usuario_nao_permite_id_menor_ou_igual_a_zero():
    with pytest.raises(ValueError, match=r"id do tipo de papel do usuário deve ser maior que zero"):
        TipoPapelUsuario(
            id=0,
            codigo="CATEQUISTA",
            descricao="Catequista",
        )


def test_tipo_papel_usuario_nao_permite_codigo_vazio():
    with pytest.raises(ValueError, match=r"código do tipo de papel do usuário"):
        TipoPapelUsuario(
            id=1,
            codigo="   ",
            descricao="Catequista",
        )


def test_tipo_papel_usuario_nao_permite_descricao_vazia():
    with pytest.raises(ValueError, match=r"descrição do tipo de papel do usuário"):
        TipoPapelUsuario(
            id=1,
            codigo="CATEQUISTA",
            descricao="   ",
        )


def test_tipo_papel_usuario_eh_retorna_true_para_mesmo_codigo():
    papel = TipoPapelUsuario(
        id=1,
        codigo="CATEQUISTA",
        descricao="Catequista",
    )

    assert papel.eh("CATEQUISTA") is True


def test_tipo_papel_usuario_eh_retorna_true_para_codigo_com_case_diferente_e_espacos():
    papel = TipoPapelUsuario(
        id=1,
        codigo="CATEQUISTA",
        descricao="Catequista",
    )

    assert papel.eh("  catequista  ") is True


def test_tipo_papel_usuario_eh_retorna_false_para_codigo_diferente():
    papel = TipoPapelUsuario(
        id=1,
        codigo="CATEQUISTA",
        descricao="Catequista",
    )

    assert papel.eh("RESPONSAVEL") is False


def test_tipo_papel_usuario_eh_retorna_false_para_none():
    papel = TipoPapelUsuario(
        id=1,
        codigo="CATEQUISTA",
        descricao="Catequista",
    )

    assert papel.eh(None) is False


def test_tipo_papel_usuario_eh_retorna_false_para_string_vazia():
    papel = TipoPapelUsuario(
        id=1,
        codigo="CATEQUISTA",
        descricao="Catequista",
    )

    assert papel.eh("") is False
    assert papel.eh("   ") is False