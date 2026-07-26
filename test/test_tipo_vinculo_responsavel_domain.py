# test/test_tipo_vinculo_responsavel_domain.py

import pytest

from domain.tipoVinculoResponsavel import TipoVinculoResponsavel


def test_tipo_vinculo_responsavel_criacao_valida():
    vinculo = TipoVinculoResponsavel(
        id=1,
        codigo="PAI",
        descricao="Pai",
    )

    assert vinculo.id == 1
    assert vinculo.codigo == "PAI"
    assert vinculo.descricao == "Pai"


def test_tipo_vinculo_responsavel_normaliza_codigo_e_descricao():
    vinculo = TipoVinculoResponsavel(
        id=1,
        codigo="  pai  ",
        descricao="  Pai  ",
    )

    assert vinculo.codigo == "PAI"
    assert vinculo.descricao == "Pai"


def test_tipo_vinculo_responsavel_nao_permite_id_nulo():
    with pytest.raises(ValueError, match=r"id do tipo de vínculo do responsável"):
        TipoVinculoResponsavel(
            id=None,
            codigo="PAI",
            descricao="Pai",
        )


def test_tipo_vinculo_responsavel_nao_permite_id_nao_inteiro():
    with pytest.raises(ValueError, match=r"id do tipo de vínculo do responsável deve ser um inteiro"):
        TipoVinculoResponsavel(
            id="1",
            codigo="PAI",
            descricao="Pai",
        )


def test_tipo_vinculo_responsavel_nao_permite_id_menor_ou_igual_a_zero():
    with pytest.raises(ValueError, match=r"id do tipo de vínculo do responsável deve ser maior que zero"):
        TipoVinculoResponsavel(
            id=0,
            codigo="PAI",
            descricao="Pai",
        )


def test_tipo_vinculo_responsavel_nao_permite_codigo_vazio():
    with pytest.raises(ValueError, match=r"código do tipo de vínculo do responsável"):
        TipoVinculoResponsavel(
            id=1,
            codigo="   ",
            descricao="Pai",
        )


def test_tipo_vinculo_responsavel_nao_permite_descricao_vazia():
    with pytest.raises(ValueError, match=r"descrição do tipo de vínculo do responsável"):
        TipoVinculoResponsavel(
            id=1,
            codigo="PAI",
            descricao="   ",
        )


def test_tipo_vinculo_responsavel_eh_retorna_true_para_mesmo_codigo():
    vinculo = TipoVinculoResponsavel(
        id=1,
        codigo="PAI",
        descricao="Pai",
    )

    assert vinculo.eh("PAI") is True


def test_tipo_vinculo_responsavel_eh_retorna_true_para_codigo_com_case_diferente_e_espacos():
    vinculo = TipoVinculoResponsavel(
        id=1,
        codigo="PAI",
        descricao="Pai",
    )

    assert vinculo.eh("  pai  ") is True


def test_tipo_vinculo_responsavel_eh_retorna_false_para_codigo_diferente():
    vinculo = TipoVinculoResponsavel(
        id=1,
        codigo="PAI",
        descricao="Pai",
    )

    assert vinculo.eh("MAE") is False


def test_tipo_vinculo_responsavel_eh_retorna_false_para_none():
    vinculo = TipoVinculoResponsavel(
        id=1,
        codigo="PAI",
        descricao="Pai",
    )

    assert vinculo.eh(None) is False


def test_tipo_vinculo_responsavel_eh_retorna_false_para_string_vazia():
    vinculo = TipoVinculoResponsavel(
        id=1,
        codigo="PAI",
        descricao="Pai",
    )

    assert vinculo.eh("") is False
    assert vinculo.eh("   ") is False