# test/test_turma_catequista_domain.py

import pytest
from dataclasses import dataclass

from domain.turmaCatequista import TurmaCatequista


@dataclass
class TurmaFake:
    id: str
    nome_sistema: str


@dataclass
class CatequistaFake:
    id: str
    nome: str


def criar_turma(
    id: str = "turma-1",
    nome_sistema: str = "EUCARISTIA_SABADO_10",
) -> TurmaFake:
    return TurmaFake(
        id=id,
        nome_sistema=nome_sistema,
    )


def criar_catequista(
    id: str = "catq-1",
    nome: str = "Ana",
) -> CatequistaFake:
    return CatequistaFake(
        id=id,
        nome=nome,
    )


def test_turma_catequista_criacao_valida():
    turma = criar_turma()
    catequista = criar_catequista()

    vinculo = TurmaCatequista(
        turma=turma,
        catequista=catequista,
    )

    assert vinculo.turma == turma
    assert vinculo.catequista == catequista


def test_turma_catequista_nao_permite_turma_nula():
    catequista = criar_catequista()

    with pytest.raises(ValueError, match=r"turma do vínculo com catequista"):
        TurmaCatequista(
            turma=None,
            catequista=catequista,
        )


def test_turma_catequista_nao_permite_catequista_nulo():
    turma = criar_turma()

    with pytest.raises(ValueError, match=r"catequista do vínculo com turma"):
        TurmaCatequista(
            turma=turma,
            catequista=None,
        )


def test_turma_catequista_pertence_a_turma_retorna_true():
    turma_1 = criar_turma(id="turma-1")
    turma_2 = criar_turma(id="turma-2")
    catequista = criar_catequista()

    vinculo = TurmaCatequista(
        turma=turma_1,
        catequista=catequista,
    )

    assert vinculo.pertence_a_turma(turma_1) is True
    assert vinculo.pertence_a_turma(turma_2) is False


def test_turma_catequista_pertence_a_turma_retorna_false_para_none():
    turma = criar_turma()
    catequista = criar_catequista()

    vinculo = TurmaCatequista(
        turma=turma,
        catequista=catequista,
    )

    assert vinculo.pertence_a_turma(None) is False


def test_turma_catequista_pertence_ao_catequista_retorna_true():
    turma = criar_turma()
    catequista_1 = criar_catequista(id="catq-1", nome="Ana")
    catequista_2 = criar_catequista(id="catq-2", nome="Carlos")

    vinculo = TurmaCatequista(
        turma=turma,
        catequista=catequista_1,
    )

    assert vinculo.pertence_ao_catequista(catequista_1) is True
    assert vinculo.pertence_ao_catequista(catequista_2) is False


def test_turma_catequista_pertence_ao_catequista_retorna_false_para_none():
    turma = criar_turma()
    catequista = criar_catequista()

    vinculo = TurmaCatequista(
        turma=turma,
        catequista=catequista,
    )

    assert vinculo.pertence_ao_catequista(None) is False