# test/test_coordenador_etapa_domain.py

import pytest
from dataclasses import dataclass

from domain.coordenadorEtapa import CoordenadorEtapa


@dataclass
class UsuarioFake:
    id: str


@dataclass
class EtapaFake:
    id: str
    nome: str


def criar_coordenador(
    id: str = "coord-1",
    nome: str = "Maria Aparecida",
    usuario=None,
    email: str | None = "maria@example.com",
    telefone: str | None = "11999999999",
    etapa=None,
) -> CoordenadorEtapa:
    return CoordenadorEtapa(
        id=id,
        nome=nome,
        usuario=usuario,
        email=email,
        telefone=telefone,
        etapa=etapa,
    )


def test_coordenador_etapa_criacao_valida():
    coordenador = criar_coordenador()

    assert coordenador.id == "coord-1"
    assert coordenador.nome == "Maria Aparecida"
    assert coordenador.email == "maria@example.com"
    assert coordenador.telefone == "11999999999"
    assert coordenador.usuario is None
    assert coordenador.etapa is None


def test_coordenador_etapa_normaliza_campos_textuais():
    coordenador = criar_coordenador(
        id="  coord-1  ",
        nome="  Maria Aparecida  ",
        email="   ",
        telefone="   ",
    )

    assert coordenador.id == "coord-1"
    assert coordenador.nome == "Maria Aparecida"
    assert coordenador.email is None
    assert coordenador.telefone is None


def test_coordenador_etapa_nao_permite_id_vazio():
    with pytest.raises(ValueError, match=r"id do coordenador de etapa"):
        criar_coordenador(id="   ")


def test_coordenador_etapa_nao_permite_nome_vazio():
    with pytest.raises(ValueError, match=r"nome do coordenador de etapa"):
        criar_coordenador(nome="   ")


def test_coordenador_etapa_tem_usuario_retorna_true_quando_associado():
    usuario = UsuarioFake(id="user-1")

    coordenador = criar_coordenador(usuario=usuario)

    assert coordenador.tem_usuario is True


def test_coordenador_etapa_tem_usuario_retorna_false_quando_nao_associado():
    coordenador = criar_coordenador(usuario=None)

    assert coordenador.tem_usuario is False


def test_coordenador_etapa_pertence_ao_usuario_retorna_true():
    usuario = UsuarioFake(id="user-1")

    coordenador = criar_coordenador(usuario=usuario)

    assert coordenador.pertence_ao_usuario(usuario) is True


def test_coordenador_etapa_pertence_ao_usuario_retorna_false_para_outro_usuario():
    usuario_1 = UsuarioFake(id="user-1")
    usuario_2 = UsuarioFake(id="user-2")

    coordenador = criar_coordenador(usuario=usuario_1)

    assert coordenador.pertence_ao_usuario(usuario_2) is False


def test_coordenador_etapa_pertence_ao_usuario_retorna_false_para_none():
    usuario = UsuarioFake(id="user-1")

    coordenador = criar_coordenador(usuario=usuario)

    assert coordenador.pertence_ao_usuario(None) is False


def test_coordenador_etapa_esta_vinculado_a_etapa_retorna_true():
    etapa = EtapaFake(id="etapa-1", nome="Eucaristia")

    coordenador = criar_coordenador(etapa=etapa)

    assert coordenador.esta_vinculado_a_etapa() is True


def test_coordenador_etapa_esta_vinculado_a_etapa_retorna_false():
    coordenador = criar_coordenador(etapa=None)

    assert coordenador.esta_vinculado_a_etapa() is False