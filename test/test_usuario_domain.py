# test/test_usuario_domain.py

import pytest

from app.domain.usuario import Usuario
from app.domain.tipoPapelUsuario import TipoPapelUsuario


def criar_papel_responsavel() -> TipoPapelUsuario:
    return TipoPapelUsuario(
        id=1,
        codigo="RESPONSAVEL",
        descricao="Responsável",
    )


def criar_papel_catequista() -> TipoPapelUsuario:
    return TipoPapelUsuario(
        id=2,
        codigo="CATEQUISTA",
        descricao="Catequista",
    )


def criar_papel_coordenador() -> TipoPapelUsuario:
    return TipoPapelUsuario(
        id=3,
        codigo="COORDENADOR",
        descricao="Coordenador",
    )


def test_usuario_criacao_valida_sem_papeis():
    usuario = Usuario(
        id="user-1",
        nome="Maria da Silva",
        email="maria@example.com",
    )

    assert usuario.id == "user-1"
    assert usuario.nome == "Maria da Silva"
    assert usuario.email == "maria@example.com"
    assert usuario.papeis == []
    assert usuario.quantidade_papeis == 0
    assert usuario.possui_papeis is False


def test_usuario_criacao_valida_com_papeis():
    papel_responsavel = criar_papel_responsavel()
    papel_catequista = criar_papel_catequista()

    usuario = Usuario(
        id="user-1",
        nome="Maria da Silva",
        email="maria@example.com",
        papeis=[papel_responsavel, papel_catequista],
    )

    assert usuario.quantidade_papeis == 2
    assert usuario.possui_papeis is True
    assert usuario.tem_papel("RESPONSAVEL") is True
    assert usuario.tem_papel("CATEQUISTA") is True
    assert usuario.tem_papel("COORDENADOR") is False


def test_usuario_normaliza_id_nome_e_email():
    usuario = Usuario(
        id="  user-1  ",
        nome="  Maria da Silva  ",
        email="  MARIA@EXAMPLE.COM  ",
    )

    assert usuario.id == "user-1"
    assert usuario.nome == "Maria da Silva"
    assert usuario.email == "maria@example.com"


def test_usuario_nao_permite_id_vazio():
    with pytest.raises(ValueError, match=r"id do usuário"):
        Usuario(
            id="   ",
            nome="Maria da Silva",
            email="maria@example.com",
        )


def test_usuario_nao_permite_nome_vazio():
    with pytest.raises(ValueError, match=r"nome do usuário"):
        Usuario(
            id="user-1",
            nome="   ",
            email="maria@example.com",
        )


def test_usuario_nao_permite_email_vazio():
    with pytest.raises(ValueError, match=r"e-mail do usuário"):
        Usuario(
            id="user-1",
            nome="Maria da Silva",
            email="   ",
        )


def test_usuario_nao_permite_email_invalido():
    with pytest.raises(ValueError, match=r"e-mail do usuário deve ser válido"):
        Usuario(
            id="user-1",
            nome="Maria da Silva",
            email="maria.example.com",
        )


def test_usuario_tem_papel_retorna_false_para_codigo_vazio():
    papel_responsavel = criar_papel_responsavel()

    usuario = Usuario(
        id="user-1",
        nome="Maria da Silva",
        email="maria@example.com",
        papeis=[papel_responsavel],
    )

    assert usuario.tem_papel("") is False
    assert usuario.tem_papel("   ") is False


def test_usuario_adicionar_papel():
    papel_responsavel = criar_papel_responsavel()
    papel_catequista = criar_papel_catequista()

    usuario = Usuario(
        id="user-1",
        nome="Maria da Silva",
        email="maria@example.com",
        papeis=[papel_responsavel],
    )

    usuario.adicionar_papel(papel_catequista)

    assert usuario.quantidade_papeis == 2
    assert usuario.tem_papel("RESPONSAVEL") is True
    assert usuario.tem_papel("CATEQUISTA") is True
    assert usuario.listar_codigos_papeis() == ["RESPONSAVEL", "CATEQUISTA"]


def test_usuario_nao_permite_adicionar_papel_nulo():
    usuario = Usuario(
        id="user-1",
        nome="Maria da Silva",
        email="maria@example.com",
    )

    with pytest.raises(ValueError, match=r"papel informado é obrigatório"):
        usuario.adicionar_papel(None)


def test_usuario_nao_permite_adicionar_papel_duplicado():
    papel_responsavel = criar_papel_responsavel()

    usuario = Usuario(
        id="user-1",
        nome="Maria da Silva",
        email="maria@example.com",
        papeis=[papel_responsavel],
    )

    with pytest.raises(ValueError, match=r"já possui o papel"):
        usuario.adicionar_papel(papel_responsavel)


def test_usuario_nao_permite_papeis_duplicados_na_criacao():
    papel_responsavel_1 = criar_papel_responsavel()
    papel_responsavel_2 = TipoPapelUsuario(
        id=99,
        codigo="RESPONSAVEL",
        descricao="Responsável duplicado",
    )

    with pytest.raises(ValueError, match=r"já foi associado ao usuário"):
        Usuario(
            id="user-1",
            nome="Maria da Silva",
            email="maria@example.com",
            papeis=[papel_responsavel_1, papel_responsavel_2],
        )


def test_usuario_nao_permite_lista_de_papeis_com_item_nulo():
    with pytest.raises(ValueError, match=r"não pode conter itens nulos"):
        Usuario(
            id="user-1",
            nome="Maria da Silva",
            email="maria@example.com",
            papeis=[None],
        )


def test_usuario_remover_papel():
    papel_responsavel = criar_papel_responsavel()
    papel_catequista = criar_papel_catequista()

    usuario = Usuario(
        id="user-1",
        nome="Maria da Silva",
        email="maria@example.com",
        papeis=[papel_responsavel, papel_catequista],
    )

    usuario.remover_papel("RESPONSAVEL")

    assert usuario.quantidade_papeis == 1
    assert usuario.tem_papel("RESPONSAVEL") is False
    assert usuario.tem_papel("CATEQUISTA") is True
    assert usuario.listar_codigos_papeis() == ["CATEQUISTA"]


def test_usuario_remover_papel_com_codigo_vazio_lanca_erro():
    papel_responsavel = criar_papel_responsavel()

    usuario = Usuario(
        id="user-1",
        nome="Maria da Silva",
        email="maria@example.com",
        papeis=[papel_responsavel],
    )

    with pytest.raises(ValueError, match=r"código do papel é obrigatório"):
        usuario.remover_papel("   ")


def test_usuario_listar_codigos_papeis():
    papel_responsavel = criar_papel_responsavel()
    papel_coordenador = criar_papel_coordenador()

    usuario = Usuario(
        id="user-1",
        nome="Maria da Silva",
        email="maria@example.com",
        papeis=[papel_responsavel, papel_coordenador],
    )

    assert usuario.listar_codigos_papeis() == ["RESPONSAVEL", "COORDENADOR"]