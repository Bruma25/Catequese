# test/test_catequizando_domain.py

import pytest
from datetime import date

from domain.catequizando import Catequizando
from domain.sacramento import Sacramento
from domain.historicoSacramental import HistoricoSacramental
from domain.responsavel import Responsavel
from domain.tipoVinculoResponsavel import TipoVinculoResponsavel
from domain.catequizandoResponsavel import CatequizandoResponsavel


def criar_catequizando() -> Catequizando:
    return Catequizando(
        id="cat-1",
        nome="João da Silva",
        data_nascimento=date(2015, 7, 10),
        endereco="Rua A, 123",
        telefone="11999999999",
        email="joao@example.com",
        observacoes="Observação de teste",
        necessidade_especial=False,
        descricao_necessidade_especial=None,
    )


def criar_responsavel() -> Responsavel:
    return Responsavel(
        id="resp-1",
        nome="Maria da Silva",
        email="maria@example.com",
        telefone="11888888888",
        usuario=None,
        vinculos=[],
    )


def criar_tipo_vinculo_pai() -> TipoVinculoResponsavel:
    return TipoVinculoResponsavel(
        id=1,
        codigo="PAI",
        descricao="Pai",
    )


def criar_sacramento_batismo() -> Sacramento:
    return Sacramento(
        id=1,
        codigo="BATISMO",
        nome_exibicao="Batismo",
    )


def criar_sacramento_eucaristia() -> Sacramento:
    return Sacramento(
        id=2,
        codigo="EUCARISTIA",
        nome_exibicao="Eucaristia",
    )


def test_catequizando_criacao_valida():
    catequizando = criar_catequizando()

    assert catequizando.id == "cat-1"
    assert catequizando.nome == "João da Silva"
    assert catequizando.ano_nascimento == 2015
    assert catequizando.tem_necessidade_especial() is False
    assert catequizando.descricao_necessidade_especial is None
    assert catequizando.vinculos_responsaveis == []
    assert catequizando.historico_sacramental == []


def test_catequizando_idade_atual():
    catequizando = criar_catequizando()

    assert catequizando.idade_atual(date(2026, 7, 9)) == 10
    assert catequizando.idade_atual(date(2026, 7, 10)) == 11
    assert catequizando.idade_atual(date(2026, 7, 11)) == 11


def test_catequizando_idade_em_data_anterior_ao_nascimento_lanca_erro():
    catequizando = criar_catequizando()

    with pytest.raises(ValueError, match="data de referência"):
        catequizando.idade_em(date(2015, 7, 9))


def test_catequizando_nao_permite_nome_vazio():
    with pytest.raises(ValueError, match="nome do catequizando"):
        Catequizando(
            id="cat-1",
            nome="   ",
            data_nascimento=date(2015, 7, 10),
        )


def test_catequizando_nao_permite_data_nascimento_no_futuro():
    with pytest.raises(ValueError, match="não pode estar no futuro"):
        Catequizando(
            id="cat-1",
            nome="João",
            data_nascimento=date(2100, 1, 1),
        )


def test_catequizando_exige_descricao_quando_necessidade_especial_true():
    with pytest.raises(ValueError, match="descrição da necessidade especial"):
        Catequizando(
            id="cat-1",
            nome="João",
            data_nascimento=date(2015, 7, 10),
            necessidade_especial=True,
            descricao_necessidade_especial="   ",
        )


def test_catequizando_remove_descricao_se_necessidade_especial_false():
    catequizando = Catequizando(
        id="cat-1",
        nome="João",
        data_nascimento=date(2015, 7, 10),
        necessidade_especial=False,
        descricao_necessidade_especial="Texto que deve ser limpo",
    )

    assert catequizando.descricao_necessidade_especial is None


def test_catequizando_adiciona_historico_e_verifica_sacramento():
    catequizando = criar_catequizando()
    batismo = criar_sacramento_batismo()

    historico = HistoricoSacramental(
        id="hist-1",
        catequizando=catequizando,
        sacramento=batismo,
        data_recebimento=date(2016, 8, 15),
        local="Paróquia São José",
        observacoes="Batizado em teste",
    )

    catequizando.adicionar_historico_sacramental(historico)

    assert catequizando.possui_sacramento(batismo) is True
    assert len(catequizando.historico_sacramental) == 1
    assert catequizando.listar_sacramentos() == [batismo]


def test_catequizando_nao_adiciona_historico_de_outro_catequizando():
    catequizando_1 = criar_catequizando()
    catequizando_2 = Catequizando(
        id="cat-2",
        nome="Pedro",
        data_nascimento=date(2014, 5, 20),
    )
    batismo = criar_sacramento_batismo()

    historico = HistoricoSacramental(
        id="hist-1",
        catequizando=catequizando_2,
        sacramento=batismo,
        data_recebimento=date(2016, 8, 15),
        local="Paróquia São José",
        observacoes=None,
    )

    with pytest.raises(ValueError, match="histórico informado não pertence"):
        catequizando_1.adicionar_historico_sacramental(historico)


def test_catequizando_nao_adiciona_sacramento_duplicado():
    catequizando = criar_catequizando()
    batismo = criar_sacramento_batismo()

    historico_1 = HistoricoSacramental(
        id="hist-1",
        catequizando=catequizando,
        sacramento=batismo,
        data_recebimento=date(2016, 8, 15),
        local="Paróquia São José",
        observacoes=None,
    )

    historico_2 = HistoricoSacramental(
        id="hist-2",
        catequizando=catequizando,
        sacramento=batismo,
        data_recebimento=date(2017, 1, 10),
        local="Paróquia São José",
        observacoes=None,
    )

    catequizando.adicionar_historico_sacramental(historico_1)

    with pytest.raises(ValueError, match="já está registrado"):
        catequizando.adicionar_historico_sacramental(historico_2)


def test_catequizando_adiciona_vinculo_responsavel():
    catequizando = criar_catequizando()
    responsavel = criar_responsavel()
    tipo_vinculo = criar_tipo_vinculo_pai()

    vinculo = CatequizandoResponsavel(
        catequizando=catequizando,
        responsavel=responsavel,
        tipo_vinculo=tipo_vinculo,
        descricao_outro=None,
    )

    catequizando.adicionar_vinculo_responsavel(vinculo)

    assert catequizando.possui_responsavel() is True
    assert catequizando.possui_responsavel(responsavel) is True
    assert len(catequizando.vinculos_responsaveis) == 1
    assert catequizando.listar_responsaveis() == [responsavel]


def test_catequizando_nao_adiciona_vinculo_de_outro_catequizando():
    catequizando_1 = criar_catequizando()
    catequizando_2 = Catequizando(
        id="cat-2",
        nome="Pedro",
        data_nascimento=date(2014, 5, 20),
    )
    responsavel = criar_responsavel()
    tipo_vinculo = criar_tipo_vinculo_pai()

    vinculo = CatequizandoResponsavel(
        catequizando=catequizando_2,
        responsavel=responsavel,
        tipo_vinculo=tipo_vinculo,
        descricao_outro=None,
    )

    with pytest.raises(ValueError, match="vínculo informado não pertence"):
        catequizando_1.adicionar_vinculo_responsavel(vinculo)


def test_catequizando_nao_adiciona_responsavel_duplicado():
    catequizando = criar_catequizando()
    responsavel = criar_responsavel()
    tipo_vinculo = criar_tipo_vinculo_pai()

    vinculo_1 = CatequizandoResponsavel(
        catequizando=catequizando,
        responsavel=responsavel,
        tipo_vinculo=tipo_vinculo,
        descricao_outro=None,
    )

    vinculo_2 = CatequizandoResponsavel(
        catequizando=catequizando,
        responsavel=responsavel,
        tipo_vinculo=tipo_vinculo,
        descricao_outro=None,
    )

    catequizando.adicionar_vinculo_responsavel(vinculo_1)

    with pytest.raises(ValueError, match="já está vinculado"):
        catequizando.adicionar_vinculo_responsavel(vinculo_2)


def test_catequizando_listar_sacramentos_sem_duplicidade():
    catequizando = criar_catequizando()
    batismo = criar_sacramento_batismo()
    eucaristia = criar_sacramento_eucaristia()

    historico_1 = HistoricoSacramental(
        id="hist-1",
        catequizando=catequizando,
        sacramento=batismo,
        data_recebimento=date(2016, 8, 15),
        local="Paróquia São José",
        observacoes=None,
    )

    historico_2 = HistoricoSacramental(
        id="hist-2",
        catequizando=catequizando,
        sacramento=eucaristia,
        data_recebimento=date(2024, 5, 1),
        local="Paróquia São José",
        observacoes=None,
    )

    catequizando.adicionar_historico_sacramental(historico_1)
    catequizando.adicionar_historico_sacramental(historico_2)

    sacramentos = catequizando.listar_sacramentos()

    assert len(sacramentos) == 2
    assert batismo in sacramentos
    assert eucaristia in sacramentos