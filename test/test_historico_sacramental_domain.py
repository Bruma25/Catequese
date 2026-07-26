# test/test_historico_sacramental_domain.py

import pytest
from datetime import date

from app.domain.catequizando import Catequizando
from app.domain.historicoSacramental import HistoricoSacramental
from app.domain.sacramento import Sacramento


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


def test_historico_sacramental_criacao_valida():
    catequizando = criar_catequizando()
    batismo = criar_sacramento_batismo()

    historico = HistoricoSacramental(
        id="hist-1",
        catequizando=catequizando,
        sacramento=batismo,
        data_recebimento=date(2016, 8, 15),
        local="Paróquia São José",
        observacoes="Batizado na missa das 10h",
    )

    assert historico.id == "hist-1"
    assert historico.catequizando == catequizando
    assert historico.sacramento == batismo
    assert historico.data_recebimento == date(2016, 8, 15)
    assert historico.local == "Paróquia São José"
    assert historico.observacoes == "Batizado na missa das 10h"


def test_historico_sacramental_limpa_local_e_observacoes_vazios():
    catequizando = criar_catequizando()
    batismo = criar_sacramento_batismo()

    historico = HistoricoSacramental(
        id="hist-1",
        catequizando=catequizando,
        sacramento=batismo,
        data_recebimento=date(2016, 8, 15),
        local="   ",
        observacoes="   ",
    )

    assert historico.local is None
    assert historico.observacoes is None


def test_historico_sacramental_nao_permite_id_vazio():
    catequizando = criar_catequizando()
    batismo = criar_sacramento_batismo()

    with pytest.raises(ValueError, match="id do histórico sacramental"):
        HistoricoSacramental(
            id="   ",
            catequizando=catequizando,
            sacramento=batismo,
            data_recebimento=date(2016, 8, 15),
        )


def test_historico_sacramental_nao_permite_catequizando_nulo():
    batismo = criar_sacramento_batismo()

    with pytest.raises(ValueError, match="catequizando do histórico sacramental"):
        HistoricoSacramental(
            id="hist-1",
            catequizando=None,
            sacramento=batismo,
            data_recebimento=date(2016, 8, 15),
        )


def test_historico_sacramental_nao_permite_sacramento_nulo():
    catequizando = criar_catequizando()

    with pytest.raises(ValueError, match="sacramento do histórico sacramental"):
        HistoricoSacramental(
            id="hist-1",
            catequizando=catequizando,
            sacramento=None,
            data_recebimento=date(2016, 8, 15),
        )


def test_historico_sacramental_nao_permite_data_no_futuro():
    catequizando = criar_catequizando()
    batismo = criar_sacramento_batismo()

    with pytest.raises(ValueError, match="não pode estar no futuro"):
        HistoricoSacramental(
            id="hist-1",
            catequizando=catequizando,
            sacramento=batismo,
            data_recebimento=date(2100, 1, 1),
        )


def test_historico_sacramental_nao_permite_data_anterior_ao_nascimento():
    catequizando = criar_catequizando()
    batismo = criar_sacramento_batismo()

    with pytest.raises(ValueError, match="anterior ao nascimento"):
        HistoricoSacramental(
            id="hist-1",
            catequizando=catequizando,
            sacramento=batismo,
            data_recebimento=date(2015, 7, 9),
        )


def test_historico_sacramental_eh_sacramento_retorna_true_para_mesmo_sacramento():
    catequizando = criar_catequizando()
    batismo = criar_sacramento_batismo()

    historico = HistoricoSacramental(
        id="hist-1",
        catequizando=catequizando,
        sacramento=batismo,
        data_recebimento=date(2016, 8, 15),
    )

    assert historico.eh_sacramento(batismo) is True


def test_historico_sacramental_eh_sacramento_retorna_false_para_sacramento_diferente():
    catequizando = criar_catequizando()
    batismo = criar_sacramento_batismo()
    eucaristia = criar_sacramento_eucaristia()

    historico = HistoricoSacramental(
        id="hist-1",
        catequizando=catequizando,
        sacramento=batismo,
        data_recebimento=date(2016, 8, 15),
    )

    assert historico.eh_sacramento(eucaristia) is False


def test_historico_sacramental_eh_sacramento_retorna_false_para_none():
    catequizando = criar_catequizando()
    batismo = criar_sacramento_batismo()

    historico = HistoricoSacramental(
        id="hist-1",
        catequizando=catequizando,
        sacramento=batismo,
        data_recebimento=date(2016, 8, 15),
    )

    assert historico.eh_sacramento(None) is False


def test_historico_sacramental_pertence_ao_catequizando_retorna_true():
    catequizando = criar_catequizando()
    batismo = criar_sacramento_batismo()

    historico = HistoricoSacramental(
        id="hist-1",
        catequizando=catequizando,
        sacramento=batismo,
        data_recebimento=date(2016, 8, 15),
    )

    assert historico.pertence_ao_catequizando(catequizando) is True


def test_historico_sacramental_pertence_ao_catequizando_retorna_false_para_outro():
    catequizando_1 = criar_catequizando()
    catequizando_2 = Catequizando(
        id="cat-2",
        nome="Pedro da Silva",
        data_nascimento=date(2014, 5, 20),
    )
    batismo = criar_sacramento_batismo()

    historico = HistoricoSacramental(
        id="hist-1",
        catequizando=catequizando_1,
        sacramento=batismo,
        data_recebimento=date(2016, 8, 15),
    )

    assert historico.pertence_ao_catequizando(catequizando_2) is False


def test_historico_sacramental_pertence_ao_catequizando_retorna_false_para_none():
    catequizando = criar_catequizando()
    batismo = criar_sacramento_batismo()

    historico = HistoricoSacramental(
        id="hist-1",
        catequizando=catequizando,
        sacramento=batismo,
        data_recebimento=date(2016, 8, 15),
    )

    assert historico.pertence_ao_catequizando(None) is False