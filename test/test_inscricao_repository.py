#test/test_inscrição_repository.py
import uuid
from datetime import date, datetime

from app.infra.supabaseClient import get_supabase
from app.domain.catequizando import Catequizando
from app.domain.responsavel import Responsavel
from app.domain.etapa import Etapa
from app.domain.inscricao import Inscricao
from app.domain.statusInscricao import StatusInscricao
from app.domain.usuario import Usuario
from app.domain.tipoPapelUsuario import TipoPapelUsuario
from app.repositories.catequizandoRepository import CatequizandoRepository
from app.repositories.responsavelRepository import ResponsavelRepository
from app.repositories.etapaRepository import EtapaRepository
from app.repositories.inscricaoRepository import InscricaoRepository
from app.repositories.usuarioRepository import UsuarioRepository


def test_inscricao_repository_busca_override_enriquecido():
    db = get_supabase()

    catequizandoRepo = CatequizandoRepository()
    responsavelRepo = ResponsavelRepository()
    etapaRepo = EtapaRepository()
    inscricaoRepo = InscricaoRepository()
    usuarioRepo = UsuarioRepository()

    catequizando_id = str(uuid.uuid4())
    responsavel_id = str(uuid.uuid4())
    etapa_id = str(uuid.uuid4())
    inscricao_id = str(uuid.uuid4())

    auth_responsavel_id = None
    auth_override_id = None

    usuario_responsavel_criado = False
    usuario_override_criado = False
    responsavel_criado = False
    catequizando_criado = False
    vinculo_criado = False
    etapa_criada = False
    inscricao_criada = False

    try:
        status_result = (
            db.table("status_inscricao")
            .select("*")
            .eq("codigo", "pendente_distribuicao")
            .limit(1)
            .execute()
        )
        status_data = status_result.data or []
        assert len(status_data) == 1

        status = StatusInscricao(
            id=status_data[0]["id"],
            codigo=status_data[0]["codigo"],
            descricao=status_data[0]["descricao"],
        )

        papel_result = (
            db.table("tipo_papel_usuario")
            .select("*")
            .eq("codigo", "coordenador_geral")
            .limit(1)
            .execute()
        )
        papel_data = papel_result.data or []
        assert len(papel_data) == 1

        papel_coordenador_geral = TipoPapelUsuario(
            id=papel_data[0]["id"],
            codigo=papel_data[0]["codigo"],
            descricao=papel_data[0]["descricao"],
        )

        auth_resp = db.auth.admin.create_user({
            "email": f"responsavel.inscricao.{uuid.uuid4()}@example.com",
            "password": "SenhaTeste@123",
            "email_confirm": True,
            "user_metadata": {"nome": "Responsável Auth Teste"},
        })
        auth_responsavel_id = auth_resp.user.id

        usuario_responsavel = Usuario(
            id=auth_responsavel_id,
            nome="Responsável Auth Teste",
            email=auth_resp.user.email,
            papeis=[],
        )
        usuarioRepo.salvar(usuario_responsavel)
        usuario_responsavel_criado = True

        responsavel = Responsavel(
            id=responsavel_id,
            nome="Responsável Teste Override",
            email=auth_resp.user.email,
            telefone="11999990002",
            usuario=usuario_responsavel,
            vinculos=[],
        )
        responsavel = responsavelRepo.salvar(responsavel)
        responsavel_criado = True

        catequizando = Catequizando(
            id=catequizando_id,
            nome="Catequizando Teste Override",
            data_nascimento=date(2015, 4, 10),
            observacoes="Teste de inscrição com override",
            endereco="Rua Teste, 100",
            telefone="11999990001",
            email="catequizando.override@example.com",
            necessidade_especial=False,
            descricao_necessidade_especial=None,
            vinculos_responsaveis=[],
            historico_sacramental=[],
        )
        catequizando = catequizandoRepo.salvar(catequizando)
        catequizando_criado = True

        tipo_vinculo_result = (
            db.table("tipo_vinculo_responsavel")
            .select("*")
            .limit(1)
            .execute()
        )
        tipos_vinculo = tipo_vinculo_result.data or []
        assert len(tipos_vinculo) >= 1

        (
            db.table("catequizando_responsavel")
            .insert({
                "catequizando_id": catequizando_id,
                "responsavel_id": responsavel_id,
                "tipo_vinculo_id": tipos_vinculo[0]["id"],
                "descricao_outro": None,
            })
            .execute()
        )
        vinculo_criado = True

        etapa = Etapa(
            id=etapa_id,
            nome="Etapa Teste Override",
            descricao="Etapa criada para teste enriquecido de inscrição",
            ano_nasc_minimo=2010,
            ano_nasc_maximo=2016,
            sacramentos_requeridos=[],
            sacramentos_proibidos=[],
        )
        etapa = etapaRepo.salvar(etapa)
        etapa_criada = True

        auth_override = db.auth.admin.create_user({
            "email": f"override.inscricao.{uuid.uuid4()}@example.com",
            "password": "SenhaTeste@123",
            "email_confirm": True,
            "user_metadata": {"nome": "Coordenador Geral Teste"},
        })
        auth_override_id = auth_override.user.id

        usuario_override = Usuario(
            id=auth_override_id,
            nome="Coordenador Geral Teste",
            email=auth_override.user.email,
            papeis=[papel_coordenador_geral],
        )
        usuarioRepo.salvar(usuario_override)
        usuario_override_criado = True
        usuarioRepo.definir_papeis(usuario_override)

        nova_inscricao = Inscricao(
            id=inscricao_id,
            catequizando=catequizando,
            responsavel=responsavel,
            etapa=etapa,
            status=status,
            data_inscricao=datetime.now(),
            turma=None,
            termo_assinado=True,
            quer_mesma_turma_que_irmao=False,
            referencia_irmao=None,
            observacao_responsavel="Observação do responsável",
            override_idade=True,
            motivo_override="Distribuição autorizada fora da faixa da turma",
            usuario_override=usuario_override,
        )

        resultado_salvar = inscricaoRepo.salvar(nova_inscricao)
        inscricao_criada = True

        assert resultado_salvar is not None
        assert isinstance(resultado_salvar, Inscricao)
        assert resultado_salvar.id == inscricao_id
        assert resultado_salvar.override_idade is True
        assert resultado_salvar.usuario_override is not None
        assert resultado_salvar.usuario_override.id == auth_override_id

        buscada_normal = inscricaoRepo.buscar_por_id(inscricao_id)

        assert buscada_normal is not None
        assert isinstance(buscada_normal, Inscricao)
        assert buscada_normal.usuario_override is not None
        assert buscada_normal.usuario_override.id == auth_override_id
        assert buscada_normal.usuario_override.nome == "Coordenador Geral Teste"
        assert buscada_normal.usuario_override.email == auth_override.user.email
        assert buscada_normal.usuario_override.papeis == []

        buscada_enriquecida = inscricaoRepo.buscar_por_id_com_override_enriquecido(inscricao_id)

        assert buscada_enriquecida is not None
        assert isinstance(buscada_enriquecida, Inscricao)
        assert buscada_enriquecida.usuario_override is not None
        assert buscada_enriquecida.usuario_override.id == auth_override_id
        assert buscada_enriquecida.usuario_override.nome == "Coordenador Geral Teste"
        assert buscada_enriquecida.usuario_override.email == auth_override.user.email
        assert len(buscada_enriquecida.usuario_override.papeis) == 1
        assert buscada_enriquecida.usuario_override.papeis[0].id == papel_coordenador_geral.id
        assert buscada_enriquecida.usuario_override.papeis[0].codigo == papel_coordenador_geral.codigo
        assert buscada_enriquecida.usuario_override.papeis[0].descricao == papel_coordenador_geral.descricao

        resultado_apagar = inscricaoRepo.apagar(inscricao_id)
        assert resultado_apagar is True

        inscricao_criada = False

        buscada_apos_apagar = inscricaoRepo.buscar_por_id(inscricao_id)
        assert buscada_apos_apagar is None

    finally:
        if inscricao_criada:
            try:
                inscricaoRepo.apagar(inscricao_id)
            except Exception:
                pass

        if vinculo_criado:
            try:
                (
                    db.table("catequizando_responsavel")
                    .delete()
                    .eq("catequizando_id", catequizando_id)
                    .eq("responsavel_id", responsavel_id)
                    .execute()
                )
            except Exception:
                pass

        if etapa_criada:
            try:
                etapaRepo.apagar(etapa_id)
            except Exception:
                pass

        if responsavel_criado:
            try:
                responsavelRepo.apagar(responsavel_id)
            except Exception:
                pass

        if catequizando_criado:
            try:
                catequizandoRepo.apagar(catequizando_id)
            except Exception:
                pass

        if usuario_override_criado and auth_override_id is not None:
            try:
                (
                    db.table("usuario_papel")
                    .delete()
                    .eq("usuario_id", auth_override_id)
                    .execute()
                )
            except Exception:
                pass

            try:
                usuarioRepo.apagar(auth_override_id)
            except Exception:
                pass

        if usuario_responsavel_criado and auth_responsavel_id is not None:
            try:
                usuarioRepo.apagar(auth_responsavel_id)
            except Exception:
                pass

        if auth_override_id is not None:
            try:
                db.auth.admin.delete_user(auth_override_id)
            except Exception:
                pass

        if auth_responsavel_id is not None:
            try:
                db.auth.admin.delete_user(auth_responsavel_id)
            except Exception:
                pass