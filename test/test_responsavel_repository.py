### Teste responsavelRepository.py
import uuid

from domain.responsavel import Responsavel
from repositories.responsavelRepository import ResponsavelRepository


def test_responsavel_repository_crud():
    repo = ResponsavelRepository()

    responsavel_id = str(uuid.uuid4())
    responsavel = Responsavel(
        id=responsavel_id,
        nome="Maria da Silva",
        email="maria.teste@example.com",
        telefone="11999999999",
        usuario=None,
        vinculos=[],
    )

    try:
        salvo = repo.salvar(responsavel)

        assert salvo is not None
        assert isinstance(salvo, Responsavel)
        assert salvo.id == responsavel_id
        assert salvo.nome == "Maria da Silva"
        assert salvo.email == "maria.teste@example.com"
        assert salvo.telefone == "11999999999"
        assert salvo.usuario is None

        buscado = repo.buscar_por_id(responsavel_id)

        assert buscado is not None
        assert isinstance(buscado, Responsavel)
        assert buscado.id == responsavel_id
        assert buscado.nome == "Maria da Silva"
        assert buscado.email == "maria.teste@example.com"
        assert buscado.telefone == "11999999999"

        buscado.nome = "Maria da Silva Editada"
        buscado.email = "maria.editada@example.com"
        buscado.telefone = "11888888888"

        editado = repo.editar(buscado)

        assert editado is not None
        assert isinstance(editado, Responsavel)
        assert editado.id == responsavel_id
        assert editado.nome == "Maria da Silva Editada"
        assert editado.email == "maria.editada@example.com"
        assert editado.telefone == "11888888888"

        buscado_apos_edicao = repo.buscar_por_id(responsavel_id)

        assert buscado_apos_edicao is not None
        assert isinstance(buscado_apos_edicao, Responsavel)
        assert buscado_apos_edicao.id == responsavel_id
        assert buscado_apos_edicao.nome == "Maria da Silva Editada"
        assert buscado_apos_edicao.email == "maria.editada@example.com"
        assert buscado_apos_edicao.telefone == "11888888888"

        apagado = repo.apagar(responsavel_id)
        assert apagado is True

        buscado_apos_exclusao = repo.buscar_por_id(responsavel_id)
        assert buscado_apos_exclusao is None

    finally:
        try:
            repo.apagar(responsavel_id)
        except Exception:
            pass