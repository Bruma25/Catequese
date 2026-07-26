# test/test_catequista_domain.py

import pytest
from dataclasses import dataclass

from domain.catequista import Catequista


@dataclass
class UsuarioFake:
    id: str


def criar_usuario() -> UsuarioFake:
    return UsuarioFake(id="user-1")


def test_catequista_criacao_valida_sem_usuario():
    catequista = Catequista(
        id="catq-1",
        nome="Maria Aparecida",
        email="maria@example.com",
        telefone="11999999999",
        usuario=None,
    )

    assert catequista.id == "catq-1"
    assert catequista.nome == "Maria Aparecida"
    assert catequista.email == "maria@example.com"
    assert catequista.telefone == "11999999999"
    assert catequista.usuario is None
    assert catequista.tem_usuario is False


def test_catequista_criacao_valida_com_usuario():
    usuario = criar_usuario()

    catequista = Catequista(
        id="catq-1",
        nome="Maria Aparecida",
        usuario=usuario,
    )

    assert catequista.usuario == usuario
    assert catequista.tem_usuario is True
    assert catequista.pertence_ao_usuario(usuario) is True


def test_catequista_normaliza_campos_textuais_opcionais():
    catequista = Catequista(
        id="catq-1",
        nome="  Maria Aparecida  ",
        email="   ",
        telefone="   ",
    )

    assert catequista.nome == "Maria Aparecida"
    assert catequista.email is None
    assert catequista.telefone is None


def test_catequista_nao_permite_id_vazio():
    with pytest.raises(ValueError, match="id do catequista"):
        Catequista(
            id="   ",
            nome="Maria Aparecida",
        )


def test_catequista_nao_permite_nome_vazio():
    with pytest.raises(ValueError, match="nome do catequista"):
        Catequista(
            id="catq-1",
            nome="   ",
        )


def test_catequista_pertence_ao_usuario_retorna_false_sem_usuario_associado():
    usuario = criar_usuario()

    catequista = Catequista(
        id="catq-1",
        nome="Maria Aparecida",
        usuario=None,
    )

    assert catequista.pertence_ao_usuario(usuario) is False


def test_catequista_pertence_ao_usuario_retorna_false_para_none():
    usuario = criar_usuario()

    catequista = Catequista(
        id="catq-1",
        nome="Maria Aparecida",
        usuario=usuario,
    )

    assert catequista.pertence_ao_usuario(None) is False


def test_catequista_pertence_ao_usuario_retorna_false_para_outro_usuario():
    usuario_1 = criar_usuario()
    usuario_2 = UsuarioFake(id="user-2")

    catequista = Catequista(
        id="catq-1",
        nome="Maria Aparecida",
        usuario=usuario_1,
    )

    assert catequista.pertence_ao_usuario(usuario_2) is False


def test_catequista_associar_usuario():
    usuario = criar_usuario()

    catequista = Catequista(
        id="catq-1",
        nome="Maria Aparecida",
    )

    catequista.associar_usuario(usuario)

    assert catequista.usuario == usuario
    assert catequista.tem_usuario is True
    assert catequista.pertence_ao_usuario(usuario) is True


def test_catequista_nao_permite_associar_usuario_nulo():
    catequista = Catequista(
        id="catq-1",
        nome="Maria Aparecida",
    )

    with pytest.raises(ValueError, match="usuário informado é obrigatório"):
        catequista.associar_usuario(None)


def test_catequista_remover_usuario():
    usuario = criar_usuario()

    catequista = Catequista(
        id="catq-1",
        nome="Maria Aparecida",
        usuario=usuario,
    )

    catequista.remover_usuario()

    assert catequista.usuario is None
    assert catequista.tem_usuario is False