# test/test_etapa_domain.py

import pytest
from dataclasses import dataclass

from app.domain.etapa import Etapa


@dataclass
class SacramentoFake:
    id: str
    nome: str


@dataclass
class CatequizandoFake:
    id: str
    ano_nascimento: int
    sacramentos: list

    def possui_sacramento(self, sacramento) -> bool:
        if sacramento is None:
            return False
        return any(item.id == sacramento.id for item in self.sacramentos)


@dataclass
class EtapaFake:
    id: str


@dataclass
class TurmaFake:
    id: str
    etapa: object
    ativa: bool


def criar_sacramento(
    id: str = "sac-1",
    nome: str = "Batismo",
) -> SacramentoFake:
    return SacramentoFake(
        id=id,
        nome=nome,
    )


def criar_catequizando(
    id: str = "cat-1",
    ano_nascimento: int = 2015,
    sacramentos: list | None = None,
) -> CatequizandoFake:
    return CatequizandoFake(
        id=id,
        ano_nascimento=ano_nascimento,
        sacramentos=sacramentos or [],
    )


def criar_etapa(
    id: str = "etapa-1",
    nome: str = "Primeira Eucaristia",
    descricao: str | None = "Etapa inicial",
    ano_nasc_minimo: int | None = 2010,
    ano_nasc_maximo: int | None = 2018,
    sacramentos_requeridos: list | None = None,
    sacramentos_proibidos: list | None = None,
) -> Etapa:
    return Etapa(
        id=id,
        nome=nome,
        descricao=descricao,
        ano_nasc_minimo=ano_nasc_minimo,
        ano_nasc_maximo=ano_nasc_maximo,
        sacramentos_requeridos=sacramentos_requeridos or [],
        sacramentos_proibidos=sacramentos_proibidos or [],
    )


def criar_turma(
    id: str = "turma-1",
    etapa: object | None = None,
    ativa: bool = True,
) -> TurmaFake:
    return TurmaFake(
        id=id,
        etapa=etapa,
        ativa=ativa,
    )


def test_etapa_criacao_valida():
    etapa = criar_etapa()

    assert etapa.id == "etapa-1"
    assert etapa.nome == "Primeira Eucaristia"
    assert etapa.descricao == "Etapa inicial"
    assert etapa.ano_nasc_minimo == 2010
    assert etapa.ano_nasc_maximo == 2018
    assert etapa.sacramentos_requeridos == []
    assert etapa.sacramentos_proibidos == []


def test_etapa_normaliza_campos_textuais():
    etapa = criar_etapa(
        id="  etapa-1  ",
        nome="  Primeira Eucaristia  ",
        descricao="  Etapa inicial  ",
    )

    assert etapa.id == "etapa-1"
    assert etapa.nome == "Primeira Eucaristia"
    assert etapa.descricao == "Etapa inicial"


def test_etapa_normaliza_descricao_vazia_para_none():
    etapa = criar_etapa(descricao="   ")

    assert etapa.descricao is None


def test_etapa_nao_permite_id_vazio():
    with pytest.raises(ValueError, match=r"id da etapa é obrigatório"):
        criar_etapa(id="   ")


def test_etapa_nao_permite_nome_vazio():
    with pytest.raises(ValueError, match=r"nome da etapa é obrigatório"):
        criar_etapa(nome="   ")


def test_etapa_nao_permite_ano_nasc_minimo_invalido():
    with pytest.raises(ValueError, match=r"ano de nascimento mínimo da etapa deve ser um inteiro"):
        criar_etapa(ano_nasc_minimo="2010")


def test_etapa_nao_permite_ano_nasc_maximo_invalido():
    with pytest.raises(ValueError, match=r"ano de nascimento máximo da etapa deve ser um inteiro"):
        criar_etapa(ano_nasc_maximo="2018")


def test_etapa_validar_requisitos_nao_permite_ano_minimo_maior_que_maximo():
    with pytest.raises(ValueError, match=r"ano de nascimento mínimo da etapa não pode ser maior que o ano máximo"):
        criar_etapa(
            ano_nasc_minimo=2019,
            ano_nasc_maximo=2018,
        )


def test_etapa_remove_sacramentos_repetidos_por_id():
    batismo_1 = criar_sacramento(id="batismo", nome="Batismo")
    batismo_2 = criar_sacramento(id="batismo", nome="Batismo")

    etapa = criar_etapa(
        sacramentos_requeridos=[batismo_1, batismo_2],
    )

    assert len(etapa.sacramentos_requeridos) == 1
    assert etapa.sacramentos_requeridos[0].id == "batismo"


def test_etapa_nao_permite_item_nulo_na_lista_de_sacramentos_requeridos():
    with pytest.raises(ValueError, match=r"lista de sacramentos da etapa não pode conter itens nulos"):
        criar_etapa(sacramentos_requeridos=[None])


def test_etapa_nao_permite_item_nulo_na_lista_de_sacramentos_proibidos():
    with pytest.raises(ValueError, match=r"lista de sacramentos da etapa não pode conter itens nulos"):
        criar_etapa(sacramentos_proibidos=[None])


def test_etapa_validar_requisitos_nao_permite_sacramento_requerido_e_proibido_ao_mesmo_tempo():
    batismo = criar_sacramento(id="batismo", nome="Batismo")

    with pytest.raises(
        ValueError,
        match=r"mesmo sacramento não pode ser ao mesmo tempo requerido e proibido",
    ):
        criar_etapa(
            sacramentos_requeridos=[batismo],
            sacramentos_proibidos=[batismo],
        )


def test_etapa_verifica_idade_retorna_true_quando_dentro_da_faixa():
    etapa = criar_etapa(ano_nasc_minimo=2010, ano_nasc_maximo=2018)
    catequizando = criar_catequizando(ano_nascimento=2015)

    assert etapa.verifica_idade(catequizando) is True


def test_etapa_verifica_idade_retorna_false_quando_abaixo_do_minimo():
    etapa = criar_etapa(ano_nasc_minimo=2010, ano_nasc_maximo=2018)
    catequizando = criar_catequizando(ano_nascimento=2009)

    assert etapa.verifica_idade(catequizando) is False


def test_etapa_verifica_idade_retorna_false_quando_acima_do_maximo():
    etapa = criar_etapa(ano_nasc_minimo=2010, ano_nasc_maximo=2018)
    catequizando = criar_catequizando(ano_nascimento=2019)

    assert etapa.verifica_idade(catequizando) is False


def test_etapa_verifica_idade_retorna_false_para_none():
    etapa = criar_etapa()

    assert etapa.verifica_idade(None) is False


def test_etapa_verifica_sacramentos_retorna_true_quando_atende_requisitos():
    batismo = criar_sacramento(id="batismo", nome="Batismo")
    etapa = criar_etapa(
        sacramentos_requeridos=[batismo],
        sacramentos_proibidos=[],
    )
    catequizando = criar_catequizando(sacramentos=[batismo])

    assert etapa.verifica_sacramentos(catequizando) is True


def test_etapa_verifica_sacramentos_retorna_false_quando_falta_sacramento_requerido():
    batismo = criar_sacramento(id="batismo", nome="Batismo")
    etapa = criar_etapa(sacramentos_requeridos=[batismo])
    catequizando = criar_catequizando(sacramentos=[])

    assert etapa.verifica_sacramentos(catequizando) is False


def test_etapa_verifica_sacramentos_retorna_false_quando_possui_sacramento_proibido():
    crisma = criar_sacramento(id="crisma", nome="Crisma")
    etapa = criar_etapa(sacramentos_proibidos=[crisma])
    catequizando = criar_catequizando(sacramentos=[crisma])

    assert etapa.verifica_sacramentos(catequizando) is False


def test_etapa_verifica_sacramentos_retorna_false_para_none():
    etapa = criar_etapa()

    assert etapa.verifica_sacramentos(None) is False


def test_etapa_aceita_catequizando_retorna_true_quando_idade_e_sacramentos_ok():
    batismo = criar_sacramento(id="batismo", nome="Batismo")
    etapa = criar_etapa(
        ano_nasc_minimo=2010,
        ano_nasc_maximo=2018,
        sacramentos_requeridos=[batismo],
    )
    catequizando = criar_catequizando(
        ano_nascimento=2015,
        sacramentos=[batismo],
    )

    assert etapa.aceita_catequizando(catequizando) is True


def test_etapa_aceita_catequizando_retorna_false_quando_idade_invalida():
    etapa = criar_etapa(
        ano_nasc_minimo=2010,
        ano_nasc_maximo=2018,
    )
    catequizando = criar_catequizando(ano_nascimento=2008)

    assert etapa.aceita_catequizando(catequizando) is False


def test_etapa_aceita_catequizando_retorna_false_quando_sacramentos_invalidos():
    batismo = criar_sacramento(id="batismo", nome="Batismo")
    etapa = criar_etapa(
        ano_nasc_minimo=2010,
        ano_nasc_maximo=2018,
        sacramentos_requeridos=[batismo],
    )
    catequizando = criar_catequizando(
        ano_nascimento=2015,
        sacramentos=[],
    )

    assert etapa.aceita_catequizando(catequizando) is False


def test_etapa_aceita_catequizando_retorna_false_para_none():
    etapa = criar_etapa()

    assert etapa.aceita_catequizando(None) is False


def test_etapa_pode_catequizando_entrar_delega_para_aceita_catequizando():
    batismo = criar_sacramento(id="batismo", nome="Batismo")
    etapa = criar_etapa(
        ano_nasc_minimo=2010,
        ano_nasc_maximo=2018,
        sacramentos_requeridos=[batismo],
    )
    catequizando = criar_catequizando(
        ano_nascimento=2015,
        sacramentos=[batismo],
    )

    assert etapa.pode_catequizando_entrar(catequizando) is True


def test_etapa_possui_sacramento_requerido_retorna_true_quando_existir():
    batismo = criar_sacramento(id="batismo", nome="Batismo")
    etapa = criar_etapa(sacramentos_requeridos=[batismo])

    assert etapa.possui_sacramento_requerido(batismo) is True


def test_etapa_possui_sacramento_requerido_retorna_false_para_none():
    etapa = criar_etapa()

    assert etapa.possui_sacramento_requerido(None) is False


def test_etapa_possui_sacramento_proibido_retorna_true_quando_existir():
    crisma = criar_sacramento(id="crisma", nome="Crisma")
    etapa = criar_etapa(sacramentos_proibidos=[crisma])

    assert etapa.possui_sacramento_proibido(crisma) is True


def test_etapa_possui_sacramento_proibido_retorna_false_para_none():
    etapa = criar_etapa()

    assert etapa.possui_sacramento_proibido(None) is False


def test_etapa_listar_turmas_ativas_retorna_apenas_turmas_ativas_da_mesma_etapa():
    etapa = criar_etapa(id="etapa-1")
    outra_etapa = EtapaFake(id="etapa-2")

    turma_1 = criar_turma(id="turma-1", etapa=etapa, ativa=True)
    turma_2 = criar_turma(id="turma-2", etapa=etapa, ativa=False)
    turma_3 = criar_turma(id="turma-3", etapa=outra_etapa, ativa=True)
    turma_4 = criar_turma(id="turma-4", etapa=None, ativa=True)

    turmas = etapa.listar_turmas_ativas([turma_1, turma_2, turma_3, turma_4, None])

    assert turmas == [turma_1]


def test_etapa_listar_turmas_ativas_retorna_lista_vazia_para_none():
    etapa = criar_etapa()

    assert etapa.listar_turmas_ativas(None) == []