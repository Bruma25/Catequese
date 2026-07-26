# test/test_responsavel_domain.py

import pytest
from dataclasses import dataclass

from domain.responsavel import Responsavel


@dataclass
class UsuarioFake:
    id: str


@dataclass
class CatequizandoFake:
    id: str
    nome: str


@dataclass
class VinculoFake:
    responsavel: object
    catequizando: object


def criar_usuario(id: str = "user-1") -> UsuarioFake:
    return UsuarioFake(id=id)


def criar_catequizando(
    id: str = "cat-1",
    nome: str = "João",
) -> CatequizandoFake:
    return CatequizandoFake(
        id=id,
        nome=nome,
    )


def criar_responsavel(
    id: str = "resp-1",
    nome: str = "Maria",
    email: str | None = "maria@email.com",
    telefone: str | None = "11999999999",
    usuario: object | None = None,
    vinculos: list | None = None,
) -> Responsavel:
    return Responsavel(
        id=id,
        nome=nome,
        email=email,
        telefone=telefone,
        usuario=usuario,
        vinculos=vinculos or [],
    )


def criar_vinculo(
    responsavel: object,
    catequizando: object,
) -> VinculoFake:
    return VinculoFake(
        responsavel=responsavel,
        catequizando=catequizando,
    )


def test_responsavel_criacao_valida():
    usuario = criar_usuario()

    responsavel = criar_responsavel(usuario=usuario)

    assert responsavel.id == "resp-1"
    assert responsavel.nome == "Maria"
    assert responsavel.email == "maria@email.com"
    assert responsavel.telefone == "11999999999"
    assert responsavel.usuario == usuario
    assert responsavel.vinculos == []


def test_responsavel_normaliza_campos_textuais():
    responsavel = criar_responsavel(
        id="  resp-1  ",
        nome="  Maria  ",
        email="  maria@email.com  ",
        telefone="  11999999999  ",
    )

    assert responsavel.id == "resp-1"
    assert responsavel.nome == "Maria"
    assert responsavel.email == "maria@email.com"
    assert responsavel.telefone == "11999999999"


def test_responsavel_normaliza_email_e_telefone_vazios_para_none():
    responsavel = criar_responsavel(
        email="   ",
        telefone="   ",
    )

    assert responsavel.email is None
    assert responsavel.telefone is None


def test_responsavel_nao_permite_id_vazio():
    with pytest.raises(ValueError, match=r"id do responsável é obrigatório"):
        criar_responsavel(id="   ")


def test_responsavel_nao_permite_nome_vazio():
    with pytest.raises(ValueError, match=r"nome do responsável é obrigatório"):
        criar_responsavel(nome="   ")


def test_responsavel_nao_permite_usuario_sem_id_valido():
    @dataclass
    class UsuarioSemId:
        id: object = None

    with pytest.raises(ValueError, match=r"usuário do responsável deve possuir id válido"):
        criar_responsavel(usuario=UsuarioSemId())


def test_responsavel_possui_usuario_retorna_true_quando_houver_usuario():
    responsavel = criar_responsavel(usuario=criar_usuario())

    assert responsavel.possui_usuario() is True


def test_responsavel_possui_usuario_retorna_false_quando_nao_houver_usuario():
    responsavel = criar_responsavel(usuario=None)

    assert responsavel.possui_usuario() is False


def test_responsavel_pertence_ao_usuario_retorna_true_quando_ids_iguais():
    usuario = criar_usuario(id="user-1")
    responsavel = criar_responsavel(usuario=usuario)

    assert responsavel.pertence_ao_usuario(usuario) is True


def test_responsavel_pertence_ao_usuario_retorna_false_quando_usuario_for_none():
    responsavel = criar_responsavel(usuario=criar_usuario())

    assert responsavel.pertence_ao_usuario(None) is False


def test_responsavel_pertence_ao_usuario_retorna_false_quando_responsavel_nao_tiver_usuario():
    usuario = criar_usuario(id="user-1")
    responsavel = criar_responsavel(usuario=None)

    assert responsavel.pertence_ao_usuario(usuario) is False


def test_responsavel_pertence_ao_usuario_retorna_false_quando_ids_diferentes():
    responsavel = criar_responsavel(usuario=criar_usuario(id="user-1"))
    outro_usuario = criar_usuario(id="user-2")

    assert responsavel.pertence_ao_usuario(outro_usuario) is False


def test_responsavel_listar_catequizandos_retorna_lista_sem_duplicidade():
    responsavel = criar_responsavel()
    catequizando = criar_catequizando(id="cat-1", nome="João")

    vinculo_1 = criar_vinculo(responsavel, catequizando)
    vinculo_2 = criar_vinculo(responsavel, catequizando)

    responsavel.vinculos.extend([vinculo_1, vinculo_2])

    catequizandos = responsavel.listar_catequizandos()

    assert len(catequizandos) == 1
    assert catequizandos[0] == catequizando


def test_responsavel_listar_catequizandos_ignora_vinculos_sem_catequizando_valido():
    responsavel = criar_responsavel()

    @dataclass
    class CatequizandoSemId:
        id: object = None

    responsavel.vinculos.extend([
        criar_vinculo(responsavel, None),
        criar_vinculo(responsavel, CatequizandoSemId()),
    ])

    assert responsavel.listar_catequizandos() == []


def test_responsavel_quantidade_catequizandos_considera_lista_sem_duplicidade():
    responsavel = criar_responsavel()
    catequizando_1 = criar_catequizando(id="cat-1", nome="João")
    catequizando_2 = criar_catequizando(id="cat-2", nome="Ana")

    responsavel.vinculos.extend([
        criar_vinculo(responsavel, catequizando_1),
        criar_vinculo(responsavel, catequizando_1),
        criar_vinculo(responsavel, catequizando_2),
    ])

    assert responsavel.quantidade_catequizandos() == 2


def test_responsavel_possui_vinculo_com_retorna_true_quando_houver_vinculo():
    responsavel = criar_responsavel()
    catequizando = criar_catequizando()

    responsavel.vinculos.append(criar_vinculo(responsavel, catequizando))

    assert responsavel.possui_vinculo_com(catequizando) is True


def test_responsavel_possui_vinculo_com_retorna_false_quando_nao_houver_vinculo():
    responsavel = criar_responsavel()
    catequizando = criar_catequizando()

    assert responsavel.possui_vinculo_com(catequizando) is False


def test_responsavel_possui_vinculo_com_retorna_false_para_none():
    responsavel = criar_responsavel()

    assert responsavel.possui_vinculo_com(None) is False


def test_responsavel_pode_responder_por_delega_para_possui_vinculo():
    responsavel = criar_responsavel()
    catequizando = criar_catequizando()

    responsavel.vinculos.append(criar_vinculo(responsavel, catequizando))

    assert responsavel.pode_responder_por(catequizando) is True


def test_responsavel_adicionar_vinculo_com_sucesso():
    responsavel = criar_responsavel()
    catequizando = criar_catequizando()
    vinculo = criar_vinculo(responsavel, catequizando)

    responsavel.adicionar_vinculo(vinculo)

    assert len(responsavel.vinculos) == 1
    assert responsavel.vinculos[0] == vinculo


def test_responsavel_adicionar_vinculo_exige_vinculo():
    responsavel = criar_responsavel()

    with pytest.raises(ValueError, match=r"vínculo informado é obrigatório"):
        responsavel.adicionar_vinculo(None)


def test_responsavel_adicionar_vinculo_exige_responsavel_no_vinculo():
    responsavel = criar_responsavel()
    catequizando = criar_catequizando()
    vinculo = criar_vinculo(None, catequizando)

    with pytest.raises(ValueError, match=r"vínculo deve possuir responsável"):
        responsavel.adicionar_vinculo(vinculo)


def test_responsavel_adicionar_vinculo_exige_mesmo_responsavel():
    responsavel = criar_responsavel(id="resp-1")
    outro_responsavel = criar_responsavel(id="resp-2")
    catequizando = criar_catequizando()
    vinculo = criar_vinculo(outro_responsavel, catequizando)

    with pytest.raises(ValueError, match=r"vínculo informado não pertence a este responsável"):
        responsavel.adicionar_vinculo(vinculo)


def test_responsavel_adicionar_vinculo_exige_catequizando_valido():
    responsavel = criar_responsavel()
    vinculo = criar_vinculo(responsavel, None)

    with pytest.raises(ValueError, match=r"vínculo deve possuir catequizando válido"):
        responsavel.adicionar_vinculo(vinculo)


def test_responsavel_adicionar_vinculo_nao_permite_duplicidade():
    responsavel = criar_responsavel()
    catequizando = criar_catequizando()

    responsavel.adicionar_vinculo(criar_vinculo(responsavel, catequizando))

    with pytest.raises(ValueError, match=r"já possui vínculo com o catequizando informado"):
        responsavel.adicionar_vinculo(criar_vinculo(responsavel, catequizando))


def test_responsavel_remover_vinculo_com_sucesso():
    responsavel = criar_responsavel()
    catequizando_1 = criar_catequizando(id="cat-1", nome="João")
    catequizando_2 = criar_catequizando(id="cat-2", nome="Ana")

    vinculo_1 = criar_vinculo(responsavel, catequizando_1)
    vinculo_2 = criar_vinculo(responsavel, catequizando_2)

    responsavel.vinculos.extend([vinculo_1, vinculo_2])

    responsavel.remover_vinculo(catequizando_1)

    assert len(responsavel.vinculos) == 1
    assert responsavel.vinculos[0] == vinculo_2


def test_responsavel_remover_vinculo_exige_catequizando_valido():
    responsavel = criar_responsavel()

    with pytest.raises(ValueError, match=r"catequizando informado é obrigatório"):
        responsavel.remover_vinculo(None)


def test_responsavel_remover_vinculo_quando_nao_houver_relacao():
    responsavel = criar_responsavel()
    catequizando = criar_catequizando()

    with pytest.raises(ValueError, match=r"não possui vínculo com o catequizando informado"):
        responsavel.remover_vinculo(catequizando)