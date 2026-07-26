### Teste catequizando_repository
import uuid
from datetime import date

from infra.supabaseClient import get_supabase
from domain.catequizando import Catequizando
from domain.catequizandoResponsavel import CatequizandoResponsavel
from domain.historicoSacramental import HistoricoSacramental
from domain.responsavel import Responsavel
from domain.sacramento import Sacramento
from domain.tipoVinculoResponsavel import TipoVinculoResponsavel
from domain.usuario import Usuario
from repositories.catequizandoRepository import CatequizandoRepository
from repositories.responsavelRepository import ResponsavelRepository
from repositories.usuarioRepository import UsuarioRepository


def test_catequizando_repository_salvar_e_editar_totalmente_sincronizado():
    db = get_supabase()

    catequizandoRepo = CatequizandoRepository()
    responsavelRepo = ResponsavelRepository()
    usuarioRepo = UsuarioRepository()

    catequizando_id = str(uuid.uuid4())
    responsavel_1_id = str(uuid.uuid4())
    responsavel_2_id = str(uuid.uuid4())

    auth_resp_1_id = None
    auth_resp_2_id = None

    usuario_resp_1_criado = False
    usuario_resp_2_criado = False
    responsavel_1_criado = False
    responsavel_2_criado = False
    catequizando_criado = False

    try:
        sacramentos_result = (
            db.table("sacramento")
            .select("*")
            .limit(2)
            .execute()
        )
        sacramentos_data = sacramentos_result.data or []
        assert len(sacramentos_data) >= 2

        sacramento_1 = Sacramento(
            id=sacramentos_data[0]["id"],
            codigo=sacramentos_data[0]["codigo"],
            nome_exibicao=sacramentos_data[0]["nome_exibicao"],
        )
        sacramento_2 = Sacramento(
            id=sacramentos_data[1]["id"],
            codigo=sacramentos_data[1]["codigo"],
            nome_exibicao=sacramentos_data[1]["nome_exibicao"],
        )

        tipos_vinculo_result = (
            db.table("tipo_vinculo_responsavel")
            .select("*")
            .limit(2)
            .execute()
        )
        tipos_vinculo_data = tipos_vinculo_result.data or []
        assert len(tipos_vinculo_data) >= 2

        tipo_vinculo_1 = TipoVinculoResponsavel(
            id=tipos_vinculo_data[0]["id"],
            codigo=tipos_vinculo_data[0]["codigo"],
            descricao=tipos_vinculo_data[0]["descricao"],
        )
        tipo_vinculo_2 = TipoVinculoResponsavel(
            id=tipos_vinculo_data[1]["id"],
            codigo=tipos_vinculo_data[1]["codigo"],
            descricao=tipos_vinculo_data[1]["descricao"],
        )

        auth_resp_1 = db.auth.admin.create_user({
            "email": f"resp1.cateq.{uuid.uuid4()}@example.com",
            "password": "SenhaTeste@123",
            "email_confirm": True,
            "user_metadata": {"nome": "Responsável 1"},
        })
        auth_resp_1_id = auth_resp_1.user.id

        usuario_resp_1 = Usuario(
            id=auth_resp_1_id,
            nome="Usuário Responsável 1",
            email=auth_resp_1.user.email,
            papeis=[],
        )
        usuarioRepo.salvar(usuario_resp_1)
        usuario_resp_1_criado = True

        responsavel_1 = Responsavel(
            id=responsavel_1_id,
            nome="Responsável Um",
            email=auth_resp_1.user.email,
            telefone="11999990011",
            usuario=usuario_resp_1,
            vinculos=[],
        )
        responsavel_1 = responsavelRepo.salvar(responsavel_1)
        responsavel_1_criado = True

        auth_resp_2 = db.auth.admin.create_user({
            "email": f"resp2.cateq.{uuid.uuid4()}@example.com",
            "password": "SenhaTeste@123",
            "email_confirm": True,
            "user_metadata": {"nome": "Responsável 2"},
        })
        auth_resp_2_id = auth_resp_2.user.id

        usuario_resp_2 = Usuario(
            id=auth_resp_2_id,
            nome="Usuário Responsável 2",
            email=auth_resp_2.user.email,
            papeis=[],
        )
        usuarioRepo.salvar(usuario_resp_2)
        usuario_resp_2_criado = True

        responsavel_2 = Responsavel(
            id=responsavel_2_id,
            nome="Responsável Dois",
            email=auth_resp_2.user.email,
            telefone="11999990022",
            usuario=usuario_resp_2,
            vinculos=[],
        )
        responsavel_2 = responsavelRepo.salvar(responsavel_2)
        responsavel_2_criado = True

        catequizando = Catequizando(
            id=catequizando_id,
            nome="Catequizando Teste Sincronizado",
            data_nascimento=date(2015, 5, 10),
            endereco="Rua Teste, 123",
            telefone="11988887777",
            email="catequizando.sincronizado@example.com",
            observacoes="Observação inicial",
            necessidade_especial=False,
            descricao_necessidade_especial=None,
            vinculos_responsaveis=[],
            historico_sacramental=[],
        )

        historico_1 = HistoricoSacramental(
            id=str(uuid.uuid4()),
            catequizando=catequizando,
            sacramento=sacramento_1,
            data_recebimento=date(2020, 1, 10),
            local="Paróquia A",
            observacoes="Recebido normalmente",
        )
        catequizando.adicionar_historico_sacramental(historico_1)

        vinculo_1 = CatequizandoResponsavel(
            catequizando=catequizando,
            responsavel=responsavel_1,
            tipo_vinculo=tipo_vinculo_1,
            descricao_outro=None,
        )
        vinculo_1.validar()
        catequizando.adicionar_vinculo_responsavel(vinculo_1)
        responsavel_1.adicionar_vinculo(vinculo_1)

        salvo = catequizandoRepo.salvar_com_dependencias(catequizando)
        catequizando_criado = True

        assert salvo is not None
        assert isinstance(salvo, Catequizando)
        assert salvo.id == catequizando_id
        assert salvo.nome == "Catequizando Teste Sincronizado"
        assert len(salvo.historico_sacramental) == 1
        assert len(salvo.vinculos_responsaveis) == 1
        assert salvo.historico_sacramental[0].sacramento.id == sacramento_1.id
        assert salvo.vinculos_responsaveis[0].responsavel.id == responsavel_1_id
        assert salvo.vinculos_responsaveis[0].tipo_vinculo.id == tipo_vinculo_1.id

        buscado = catequizandoRepo.buscar_por_id(catequizando_id)

        assert buscado is not None
        assert isinstance(buscado, Catequizando)
        assert buscado.id == catequizando_id
        assert buscado.nome == "Catequizando Teste Sincronizado"
        assert len(buscado.historico_sacramental) == 1
        assert len(buscado.vinculos_responsaveis) == 1
        assert buscado.historico_sacramental[0].sacramento.id == sacramento_1.id
        assert buscado.vinculos_responsaveis[0].responsavel.id == responsavel_1_id

        buscado.nome = "Catequizando Teste Sincronizado Editado"
        buscado.observacoes = "Observação editada"

        buscado.historico_sacramental.clear()
        historico_2 = HistoricoSacramental(
            id=str(uuid.uuid4()),
            catequizando=buscado,
            sacramento=sacramento_2,
            data_recebimento=date(2021, 2, 15),
            local="Paróquia B",
            observacoes="Novo histórico após edição",
        )
        buscado.adicionar_historico_sacramental(historico_2)

        buscado.vinculos_responsaveis.clear()
        vinculo_2 = CatequizandoResponsavel(
            catequizando=buscado,
            responsavel=responsavel_2,
            tipo_vinculo=tipo_vinculo_2,
            descricao_outro=None,
        )
        vinculo_2.validar()
        buscado.adicionar_vinculo_responsavel(vinculo_2)
        responsavel_2.adicionar_vinculo(vinculo_2)

        editado = catequizandoRepo.editar_totalmente_sincronizado(buscado)

        assert editado is not None
        assert isinstance(editado, Catequizando)
        assert editado.id == catequizando_id
        assert editado.nome == "Catequizando Teste Sincronizado Editado"
        assert editado.observacoes == "Observação editada"
        assert len(editado.historico_sacramental) == 1
        assert len(editado.vinculos_responsaveis) == 1
        assert editado.historico_sacramental[0].sacramento.id == sacramento_2.id
        assert editado.vinculos_responsaveis[0].responsavel.id == responsavel_2_id
        assert editado.vinculos_responsaveis[0].tipo_vinculo.id == tipo_vinculo_2.id

        buscado_editado = catequizandoRepo.buscar_por_id(catequizando_id)

        assert buscado_editado is not None
        assert isinstance(buscado_editado, Catequizando)
        assert buscado_editado.id == catequizando_id
        assert buscado_editado.nome == "Catequizando Teste Sincronizado Editado"
        assert buscado_editado.observacoes == "Observação editada"
        assert len(buscado_editado.historico_sacramental) == 1
        assert len(buscado_editado.vinculos_responsaveis) == 1
        assert buscado_editado.historico_sacramental[0].sacramento.id == sacramento_2.id
        assert buscado_editado.vinculos_responsaveis[0].responsavel.id == responsavel_2_id

        resultado_apagar = catequizandoRepo.apagar(catequizando_id)
        assert resultado_apagar is True

        catequizando_criado = False

        buscado_apos_apagar = catequizandoRepo.buscar_por_id(catequizando_id)
        assert buscado_apos_apagar is None

    finally:
        if catequizando_criado:
            try:
                catequizandoRepo.apagar(catequizando_id)
            except Exception:
                pass

        if responsavel_1_criado:
            try:
                responsavelRepo.apagar(responsavel_1_id)
            except Exception:
                pass

        if responsavel_2_criado:
            try:
                responsavelRepo.apagar(responsavel_2_id)
            except Exception:
                pass

        if usuario_resp_1_criado and auth_resp_1_id is not None:
            try:
                usuarioRepo.apagar(auth_resp_1_id)
            except Exception:
                pass

        if usuario_resp_2_criado and auth_resp_2_id is not None:
            try:
                usuarioRepo.apagar(auth_resp_2_id)
            except Exception:
                pass

        if auth_resp_1_id is not None:
            try:
                db.auth.admin.delete_user(auth_resp_1_id)
            except Exception:
                pass

        if auth_resp_2_id is not None:
            try:
                db.auth.admin.delete_user(auth_resp_2_id)
            except Exception:
                pass