# test/test_catequizando_responsavel_domain.py

import pytest
from datetime import date

from domain.catequizando import Catequizando
from domain.responsavel import Responsavel
from domain.tipoVinculoResponsavel import TipoVinculoResponsavel
from domain.catequizandoResponsavel import CatequizandoResponsavel


def criar_catequizando(
    id: str = "cat-1",
    nome: str = "João da Silva",
) -> Catequizando:
    return Catequizando(
        id=id,
        nome=nome,
        data_nascimento=date(2015, 7, 10),
    )


def criar_responsavel(
    id: str = "resp-1",
    nome: str = "Maria da Silva",
) -> Responsavel:
    return Responsavel(
        id=id,
        nome=nome,
        email="maria@example.com",
        telefone="11999999999",
    )


def criar_tipo_vinculo_pai() -> TipoVinculoResponsavel:
    return TipoVinculoResponsavel(
        id=1,
        codigo="PAI",
        descricao="Pai",
    )


def criar_tipo_vinculo_mae() -> TipoVinculoResponsavel:
    return TipoVinculoResponsavel(
        id=2,
        codigo="MAE",
        descricao="Mãe",
    )


def criar_tipo_vinculo_outro() -> TipoVinculoResponsavel:
    return TipoVinculoResponsavel(
        id=99,
        codigo="OUTRO",
        descricao="Outro",
    )


def criar_tipo_vinculo_proprio() -> TipoVinculoResponsavel:
    return TipoVinculoResponsavel(
        id=100,
        codigo="PROPRIO",
        descricao="O próprio catequizando",
    )


def test_catequizando_responsavel_criacao_valida_com_vinculo_pai():
    catequizando = criar_catequizando()
    responsavel = criar_responsavel()
    tipo_vinculo = criar_tipo_vinculo_pai()

    vinculo = CatequizandoResponsavel(
        catequizando=catequizando,
        responsavel=responsavel,
        tipo_vinculo=tipo_vinculo,
        descricao_outro=None,
    )

    assert vinculo.catequizando is catequizando
    assert vinculo.responsavel is responsavel
    assert vinculo.tipo_vinculo.codigo == "PAI"
    assert vinculo.descricao_outro is None
    assert vinculo.exige_descricao_outro() is False
    assert vinculo.eh_auto_responsavel() is False


def test_catequizando_responsavel_normaliza_descricao_outro():
    catequizando = criar_catequizando()
    responsavel = criar_responsavel()
    tipo_vinculo = criar_tipo_vinculo_outro()

    vinculo = CatequizandoResponsavel(
        catequizando=catequizando,
        responsavel=responsavel,
        tipo_vinculo=tipo_vinculo,
        descricao_outro="  Padrinho  ",
    )

    assert vinculo.descricao_outro == "Padrinho"


def test_catequizando_responsavel_exige_descricao_outro_quando_tipo_for_outro():
    catequizando = criar_catequizando()
    responsavel = criar_responsavel()
    tipo_vinculo = criar_tipo_vinculo_outro()

    with pytest.raises(ValueError, match=r"descricao_outro é obrigatória"):
        CatequizandoResponsavel(
            catequizando=catequizando,
            responsavel=responsavel,
            tipo_vinculo=tipo_vinculo,
            descricao_outro=None,
        )


def test_catequizando_responsavel_exige_descricao_outro_vazia_quando_tipo_for_outro():
    catequizando = criar_catequizando()
    responsavel = criar_responsavel()
    tipo_vinculo = criar_tipo_vinculo_outro()

    with pytest.raises(ValueError, match=r"descricao_outro é obrigatória"):
        CatequizandoResponsavel(
            catequizando=catequizando,
            responsavel=responsavel,
            tipo_vinculo=tipo_vinculo,
            descricao_outro="   ",
        )


def test_catequizando_responsavel_limpa_descricao_outro_quando_tipo_nao_for_outro():
    catequizando = criar_catequizando()
    responsavel = criar_responsavel()
    tipo_vinculo = criar_tipo_vinculo_pai()

    vinculo = CatequizandoResponsavel(
        catequizando=catequizando,
        responsavel=responsavel,
        tipo_vinculo=tipo_vinculo,
        descricao_outro="  Algum texto  ",
    )

    assert vinculo.descricao_outro is None


def test_catequizando_responsavel_nao_permite_catequizando_nulo():
    responsavel = criar_responsavel()
    tipo_vinculo = criar_tipo_vinculo_pai()

    with pytest.raises(ValueError, match=r"catequizando do vínculo"):
        CatequizandoResponsavel(
            catequizando=None,
            responsavel=responsavel,
            tipo_vinculo=tipo_vinculo,
        )


def test_catequizando_responsavel_nao_permite_responsavel_nulo():
    catequizando = criar_catequizando()
    tipo_vinculo = criar_tipo_vinculo_pai()

    with pytest.raises(ValueError, match=r"responsável do vínculo"):
        CatequizandoResponsavel(
            catequizando=catequizando,
            responsavel=None,
            tipo_vinculo=tipo_vinculo,
        )


def test_catequizando_responsavel_nao_permite_tipo_vinculo_nulo():
    catequizando = criar_catequizando()
    responsavel = criar_responsavel()

    with pytest.raises(ValueError, match=r"tipo de vínculo"):
        CatequizandoResponsavel(
            catequizando=catequizando,
            responsavel=responsavel,
            tipo_vinculo=None,
        )


def test_catequizando_responsavel_eh_auto_responsavel_retorna_true_quando_tipo_for_proprio():
    catequizando = criar_catequizando()
    responsavel = criar_responsavel()
    tipo_vinculo = criar_tipo_vinculo_proprio()

    vinculo = CatequizandoResponsavel(
        catequizando=catequizando,
        responsavel=responsavel,
        tipo_vinculo=tipo_vinculo,
    )

    assert vinculo.eh_auto_responsavel() is True


def test_catequizando_responsavel_eh_auto_responsavel_retorna_false_quando_tipo_nao_for_proprio():
    catequizando = criar_catequizando()
    responsavel = criar_responsavel()
    tipo_vinculo = criar_tipo_vinculo_mae()

    vinculo = CatequizandoResponsavel(
        catequizando=catequizando,
        responsavel=responsavel,
        tipo_vinculo=tipo_vinculo,
    )

    assert vinculo.eh_auto_responsavel() is False


def test_catequizando_responsavel_pertence_ao_catequizando_retorna_true():
    catequizando_1 = criar_catequizando(id="cat-1", nome="João da Silva")
    catequizando_2 = criar_catequizando(id="cat-2", nome="Pedro da Silva")
    responsavel = criar_responsavel()
    tipo_vinculo = criar_tipo_vinculo_pai()

    vinculo = CatequizandoResponsavel(
        catequizando=catequizando_1,
        responsavel=responsavel,
        tipo_vinculo=tipo_vinculo,
    )

    assert vinculo.pertence_ao_catequizando(catequizando_1) is True
    assert vinculo.pertence_ao_catequizando(catequizando_2) is False


def test_catequizando_responsavel_pertence_ao_catequizando_retorna_false_para_none():
    catequizando = criar_catequizando()
    responsavel = criar_responsavel()
    tipo_vinculo = criar_tipo_vinculo_pai()

    vinculo = CatequizandoResponsavel(
        catequizando=catequizando,
        responsavel=responsavel,
        tipo_vinculo=tipo_vinculo,
    )

    assert vinculo.pertence_ao_catequizando(None) is False


def test_catequizando_responsavel_pertence_ao_responsavel_retorna_true():
    catequizando = criar_catequizando()
    responsavel_1 = criar_responsavel(id="resp-1", nome="Maria da Silva")
    responsavel_2 = criar_responsavel(id="resp-2", nome="José da Silva")
    tipo_vinculo = criar_tipo_vinculo_pai()

    vinculo = CatequizandoResponsavel(
        catequizando=catequizando,
        responsavel=responsavel_1,
        tipo_vinculo=tipo_vinculo,
    )

    assert vinculo.pertence_ao_responsavel(responsavel_1) is True
    assert vinculo.pertence_ao_responsavel(responsavel_2) is False


def test_catequizando_responsavel_pertence_ao_responsavel_retorna_false_para_none():
    catequizando = criar_catequizando()
    responsavel = criar_responsavel()
    tipo_vinculo = criar_tipo_vinculo_pai()

    vinculo = CatequizandoResponsavel(
        catequizando=catequizando,
        responsavel=responsavel,
        tipo_vinculo=tipo_vinculo,
    )

    assert vinculo.pertence_ao_responsavel(None) is False