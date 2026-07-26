# test/test_turma_domain.py

import pytest
from dataclasses import dataclass

from domain.turma import Turma


_SENTINELA = object()


@dataclass
class EtapaFake:
    id: str


@dataclass
class LocalEncontroFake:
    id: str
    nome: str


@dataclass
class CatequistaFake:
    id: str
    nome: str


@dataclass
class CatequizandoFake:
    id: str
    ano_nascimento: int


@dataclass
class InscricaoFake:
    etapa: object = None
    etapa_id: str | None = None
    catequizando: object = None


def criar_etapa(
    id: str = "etapa-1",
) -> EtapaFake:
    return EtapaFake(id=id)


def criar_local_encontro(
    id: str = "local-1",
    nome: str = "Sala 1",
) -> LocalEncontroFake:
    return LocalEncontroFake(
        id=id,
        nome=nome,
    )


def criar_catequista(
    id: str = "catq-1",
    nome: str = "Ana",
) -> CatequistaFake:
    return CatequistaFake(
        id=id,
        nome=nome,
    )


def criar_catequizando(
    id: str = "cat-1",
    ano_nascimento: int = 2015,
) -> CatequizandoFake:
    return CatequizandoFake(
        id=id,
        ano_nascimento=ano_nascimento,
    )


def criar_inscricao(
    etapa: object = None,
    etapa_id: str | None = None,
    catequizando: object = None,
) -> InscricaoFake:
    return InscricaoFake(
        etapa=etapa,
        etapa_id=etapa_id,
        catequizando=catequizando,
    )


def criar_turma(
    id: str = "turma-1",
    etapa: object = _SENTINELA,
    nome_sistema: str = "EUCARISTIA_SABADO_10",
    nome_exibicao: str | None = "Primeira Eucaristia - Sábado 10h",
    vagas_totais: int = 20,
    ativa: bool = True,
    local_encontro: object = _SENTINELA,
    ano_nasc_minimo: int | None = 2010,
    ano_nasc_maximo: int | None = 2018,
    catequistas: list | None = None,
) -> Turma:
    if etapa is _SENTINELA:
        etapa = criar_etapa()

    if local_encontro is _SENTINELA:
        local_encontro = criar_local_encontro()

    return Turma(
        id=id,
        etapa=etapa,
        nome_sistema=nome_sistema,
        nome_exibicao=nome_exibicao,
        vagas_totais=vagas_totais,
        ativa=ativa,
        local_encontro=local_encontro,
        ano_nasc_minimo=ano_nasc_minimo,
        ano_nasc_maximo=ano_nasc_maximo,
        catequistas=catequistas or [],
    )


def test_turma_criacao_valida():
    etapa = criar_etapa()
    local = criar_local_encontro()

    turma = criar_turma(
        etapa=etapa,
        local_encontro=local,
    )

    assert turma.id == "turma-1"
    assert turma.etapa == etapa
    assert turma.nome_sistema == "EUCARISTIA_SABADO_10"
    assert turma.nome_exibicao == "Primeira Eucaristia - Sábado 10h"
    assert turma.vagas_totais == 20
    assert turma.ativa is True
    assert turma.local_encontro == local
    assert turma.ano_nasc_minimo == 2010
    assert turma.ano_nasc_maximo == 2018
    assert turma.catequistas == []


def test_turma_normaliza_campos_textuais():
    turma = criar_turma(
        id="  turma-1  ",
        nome_sistema="  EUCARISTIA_SABADO_10  ",
        nome_exibicao="  Primeira Eucaristia - Sábado 10h  ",
    )

    assert turma.id == "turma-1"
    assert turma.nome_sistema == "EUCARISTIA_SABADO_10"
    assert turma.nome_exibicao == "Primeira Eucaristia - Sábado 10h"


def test_turma_normaliza_nome_exibicao_vazio_para_none():
    turma = criar_turma(nome_exibicao="   ")

    assert turma.nome_exibicao is None


def test_turma_nao_permite_id_vazio():
    with pytest.raises(ValueError, match=r"id da turma é obrigatório"):
        criar_turma(id="   ")


def test_turma_nao_permite_etapa_nula():
    with pytest.raises(ValueError, match=r"etapa da turma é obrigatória"):
        criar_turma(etapa=None)


def test_turma_nao_permite_nome_sistema_vazio():
    with pytest.raises(ValueError, match=r"nome de sistema da turma é obrigatório"):
        criar_turma(nome_sistema="   ")


def test_turma_nao_permite_local_encontro_nulo():
    with pytest.raises(ValueError, match=r"local de encontro da turma é obrigatório"):
        criar_turma(local_encontro=None)


def test_turma_nao_permite_vagas_totais_invalido():
    with pytest.raises(ValueError, match=r"vagas totais da turma deve ser um inteiro"):
        criar_turma(vagas_totais="20")


def test_turma_nao_permite_vagas_totais_negativo():
    with pytest.raises(ValueError, match=r"vagas totais da turma não pode ser negativa"):
        criar_turma(vagas_totais=-1)


def test_turma_nao_permite_ano_nasc_minimo_invalido():
    with pytest.raises(ValueError, match=r"ano de nascimento mínimo da turma deve ser um inteiro"):
        criar_turma(ano_nasc_minimo="2010")


def test_turma_nao_permite_ano_nasc_maximo_invalido():
    with pytest.raises(ValueError, match=r"ano de nascimento máximo da turma deve ser um inteiro"):
        criar_turma(ano_nasc_maximo="2018")


def test_turma_nao_permite_ano_minimo_maior_que_maximo():
    with pytest.raises(ValueError, match=r"ano de nascimento mínimo da turma não pode ser maior que o ano máximo"):
        criar_turma(
            ano_nasc_minimo=2019,
            ano_nasc_maximo=2018,
        )


def test_turma_remove_catequistas_duplicados_por_id():
    catequista_1 = criar_catequista(id="catq-1", nome="Ana")
    catequista_2 = criar_catequista(id="catq-1", nome="Ana")

    turma = criar_turma(catequistas=[catequista_1, catequista_2])

    assert len(turma.catequistas) == 1
    assert turma.catequistas[0].id == "catq-1"


def test_turma_nao_permite_item_nulo_na_lista_de_catequistas():
    with pytest.raises(ValueError, match=r"lista de catequistas da turma não pode conter itens nulos"):
        criar_turma(catequistas=[None])


def test_turma_tem_vaga_retorna_true_quando_inscricoes_confirmadas_menor_que_vagas():
    turma = criar_turma(vagas_totais=20)

    assert turma.tem_vaga(19) is True


def test_turma_tem_vaga_retorna_false_quando_inscricoes_confirmadas_igual_a_vagas():
    turma = criar_turma(vagas_totais=20)

    assert turma.tem_vaga(20) is False


def test_turma_tem_vaga_exige_inteiro():
    turma = criar_turma()

    with pytest.raises(ValueError, match=r"inscrições confirmadas deve ser um inteiro"):
        turma.tem_vaga("10")


def test_turma_tem_vaga_nao_permite_quantidade_negativa():
    turma = criar_turma()

    with pytest.raises(ValueError, match=r"inscrições confirmadas não pode ser negativa"):
        turma.tem_vaga(-1)


def test_turma_verifica_idade_especifica_retorna_true_quando_dentro_da_faixa():
    turma = criar_turma(
        ano_nasc_minimo=2010,
        ano_nasc_maximo=2018,
    )
    catequizando = criar_catequizando(ano_nascimento=2015)

    assert turma.verifica_idade_especifica(catequizando) is True


def test_turma_verifica_idade_especifica_retorna_false_quando_abaixo_do_minimo():
    turma = criar_turma(
        ano_nasc_minimo=2010,
        ano_nasc_maximo=2018,
    )
    catequizando = criar_catequizando(ano_nascimento=2009)

    assert turma.verifica_idade_especifica(catequizando) is False


def test_turma_verifica_idade_especifica_retorna_false_quando_acima_do_maximo():
    turma = criar_turma(
        ano_nasc_minimo=2010,
        ano_nasc_maximo=2018,
    )
    catequizando = criar_catequizando(ano_nascimento=2019)

    assert turma.verifica_idade_especifica(catequizando) is False


def test_turma_verifica_idade_especifica_retorna_false_para_none():
    turma = criar_turma()

    assert turma.verifica_idade_especifica(None) is False


def test_turma_verifica_sacramentos_especificos_retorna_true_quando_catequizando_for_valido():
    turma = criar_turma()
    catequizando = criar_catequizando()

    assert turma.verifica_sacramentos_especificos(catequizando) is True


def test_turma_verifica_sacramentos_especificos_retorna_false_para_none():
    turma = criar_turma()

    assert turma.verifica_sacramentos_especificos(None) is False


def test_turma_aceita_catequizando_retorna_true_quando_ativa_e_criterios_ok():
    turma = criar_turma(
        ativa=True,
        ano_nasc_minimo=2010,
        ano_nasc_maximo=2018,
    )
    catequizando = criar_catequizando(ano_nascimento=2015)

    assert turma.aceita_catequizando(catequizando) is True


def test_turma_aceita_catequizando_retorna_false_quando_turma_inativa():
    turma = criar_turma(ativa=False)
    catequizando = criar_catequizando()

    assert turma.aceita_catequizando(catequizando) is False


def test_turma_aceita_catequizando_retorna_false_quando_idade_invalida():
    turma = criar_turma(
        ativa=True,
        ano_nasc_minimo=2010,
        ano_nasc_maximo=2018,
    )
    catequizando = criar_catequizando(ano_nascimento=2008)

    assert turma.aceita_catequizando(catequizando) is False


def test_turma_aceita_catequizando_retorna_false_para_none():
    turma = criar_turma()

    assert turma.aceita_catequizando(None) is False


def test_turma_pode_catequizando_entrar_delega_para_aceita_catequizando():
    turma = criar_turma(
        ativa=True,
        ano_nasc_minimo=2010,
        ano_nasc_maximo=2018,
    )
    catequizando = criar_catequizando(ano_nascimento=2015)

    assert turma.pode_catequizando_entrar(catequizando) is True


def test_turma_pertence_a_mesma_etapa_retorna_true_quando_inscricao_tem_objeto_etapa_igual():
    etapa = criar_etapa(id="etapa-1")
    turma = criar_turma(etapa=etapa)
    inscricao = criar_inscricao(
        etapa=criar_etapa(id="etapa-1"),
        catequizando=criar_catequizando(),
    )

    assert turma.pertence_a_mesma_etapa(inscricao) is True


def test_turma_pertence_a_mesma_etapa_retorna_true_quando_inscricao_tem_etapa_id_igual():
    turma = criar_turma(etapa=criar_etapa(id="etapa-1"))
    inscricao = criar_inscricao(
        etapa=None,
        etapa_id="etapa-1",
        catequizando=criar_catequizando(),
    )

    assert turma.pertence_a_mesma_etapa(inscricao) is True


def test_turma_pertence_a_mesma_etapa_retorna_false_quando_etapas_diferentes():
    turma = criar_turma(etapa=criar_etapa(id="etapa-1"))
    inscricao = criar_inscricao(
        etapa=criar_etapa(id="etapa-2"),
        catequizando=criar_catequizando(),
    )

    assert turma.pertence_a_mesma_etapa(inscricao) is False


def test_turma_pertence_a_mesma_etapa_retorna_false_para_none():
    turma = criar_turma()

    assert turma.pertence_a_mesma_etapa(None) is False


def test_turma_pode_receber_retorna_true_quando_mesma_etapa_aceita_catequizando_e_tem_vaga():
    etapa = criar_etapa(id="etapa-1")
    catequizando = criar_catequizando(ano_nascimento=2015)

    turma = criar_turma(
        etapa=etapa,
        ativa=True,
        vagas_totais=20,
        ano_nasc_minimo=2010,
        ano_nasc_maximo=2018,
    )
    inscricao = criar_inscricao(
        etapa=etapa,
        catequizando=catequizando,
    )

    assert turma.pode_receber(inscricao, inscricoes_confirmadas=10) is True


def test_turma_pode_receber_retorna_false_quando_inscricao_for_none():
    turma = criar_turma()

    assert turma.pode_receber(None, inscricoes_confirmadas=0) is False


def test_turma_pode_receber_retorna_false_quando_inscricao_nao_tem_catequizando():
    turma = criar_turma()
    inscricao = criar_inscricao(
        etapa=criar_etapa(id="etapa-1"),
        catequizando=None,
    )

    assert turma.pode_receber(inscricao, inscricoes_confirmadas=0) is False


def test_turma_pode_receber_retorna_false_quando_nao_for_mesma_etapa():
    turma = criar_turma(etapa=criar_etapa(id="etapa-1"))
    inscricao = criar_inscricao(
        etapa=criar_etapa(id="etapa-2"),
        catequizando=criar_catequizando(),
    )

    assert turma.pode_receber(inscricao, inscricoes_confirmadas=0) is False


def test_turma_pode_receber_retorna_false_quando_turma_nao_aceita_catequizando():
    etapa = criar_etapa(id="etapa-1")
    turma = criar_turma(
        etapa=etapa,
        ativa=True,
        ano_nasc_minimo=2010,
        ano_nasc_maximo=2018,
    )
    inscricao = criar_inscricao(
        etapa=etapa,
        catequizando=criar_catequizando(ano_nascimento=2008),
    )

    assert turma.pode_receber(inscricao, inscricoes_confirmadas=0) is False


def test_turma_pode_receber_retorna_false_quando_nao_tem_vaga():
    etapa = criar_etapa(id="etapa-1")
    turma = criar_turma(
        etapa=etapa,
        ativa=True,
        vagas_totais=20,
    )
    inscricao = criar_inscricao(
        etapa=etapa,
        catequizando=criar_catequizando(),
    )

    assert turma.pode_receber(inscricao, inscricoes_confirmadas=20) is False


def test_turma_pertence_a_etapa_retorna_true_quando_ids_iguais():
    etapa = criar_etapa(id="etapa-1")
    turma = criar_turma(etapa=etapa)

    assert turma.pertence_a_etapa(criar_etapa(id="etapa-1")) is True


def test_turma_pertence_a_etapa_retorna_false_para_none():
    turma = criar_turma()

    assert turma.pertence_a_etapa(None) is False


def test_turma_esta_ativa_retorna_true_quando_ativa():
    turma = criar_turma(ativa=True)

    assert turma.esta_ativa() is True


def test_turma_esta_ativa_retorna_false_quando_inativa():
    turma = criar_turma(ativa=False)

    assert turma.esta_ativa() is False


def test_turma_quantidade_catequistas_retorna_total():
    turma = criar_turma(
        catequistas=[
            criar_catequista(id="catq-1"),
            criar_catequista(id="catq-2"),
        ]
    )

    assert turma.quantidade_catequistas() == 2