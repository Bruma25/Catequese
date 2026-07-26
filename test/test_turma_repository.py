#/test/test_turma_repository.py
import uuid

from app.infra.supabaseClient import get_supabase
from app.domain.etapa import Etapa
from app.domain.localEncontro import LocalEncontro
from app.domain.catequista import Catequista
from app.domain.turma import Turma
from app.repositories.etapaRepository import EtapaRepository
from app.repositories.turmaRepository import TurmaRepository


def test_turma_repository_crud_basico_sem_catequistas():
    db = get_supabase()
    etapa_repo = EtapaRepository()
    turma_repo = TurmaRepository()

    etapa_id = str(uuid.uuid4())
    turma_id = str(uuid.uuid4())

    etapa_criada = False
    turma_criada = False

    try:
        local_result = (
            db.table("local_encontro")
            .select("*")
            .limit(1)
            .execute()
        )
        locais = local_result.data or []
        assert len(locais) > 0, "A tabela local_encontro precisa ter ao menos 1 registro."

        local_encontro = LocalEncontro(
            id=locais[0]["id"],
            codigo=locais[0]["codigo"],
            nome_exibicao=locais[0]["nome_exibicao"],
        )

        etapa = Etapa(
            id=etapa_id,
            nome="Etapa Base para Turma Sem Catequista",
            descricao="Etapa criada dentro do teste automático básico da turma",
            ano_nasc_minimo=2010,
            ano_nasc_maximo=2016,
            sacramentos_requeridos=[],
            sacramentos_proibidos=[],
        )

        resultado_etapa = etapa_repo.salvar(etapa)
        etapa_criada = True

        assert resultado_etapa is not None
        assert isinstance(resultado_etapa, Etapa)
        assert resultado_etapa.id == etapa_id
        assert resultado_etapa.nome == "Etapa Base para Turma Sem Catequista"
        assert resultado_etapa.descricao == "Etapa criada dentro do teste automático básico da turma"
        assert resultado_etapa.ano_nasc_minimo == 2010
        assert resultado_etapa.ano_nasc_maximo == 2016
        assert resultado_etapa.sacramentos_requeridos == []
        assert resultado_etapa.sacramentos_proibidos == []

        etapa = resultado_etapa

        nova_turma = Turma(
            id=turma_id,
            etapa=etapa,
            nome_sistema="TURMA_TESTE_SEM_CATEQUISTA_A",
            nome_exibicao="Turma Teste Sem Catequista A",
            vagas_totais=25,
            ativa=True,
            local_encontro=local_encontro,
            ano_nasc_minimo=2012,
            ano_nasc_maximo=2015,
            catequistas=[],
        )

        resultado_salvar = turma_repo.salvar(nova_turma)
        turma_criada = True

        assert resultado_salvar is not None
        assert isinstance(resultado_salvar, Turma)
        assert resultado_salvar.id == turma_id
        assert resultado_salvar.etapa.id == etapa_id
        assert resultado_salvar.nome_sistema == "TURMA_TESTE_SEM_CATEQUISTA_A"
        assert resultado_salvar.nome_exibicao == "Turma Teste Sem Catequista A"
        assert resultado_salvar.vagas_totais == 25
        assert resultado_salvar.ativa is True
        assert resultado_salvar.local_encontro.id == local_encontro.id
        assert resultado_salvar.ano_nasc_minimo == 2012
        assert resultado_salvar.ano_nasc_maximo == 2015
        assert resultado_salvar.catequistas == []

        buscada = turma_repo.buscar_por_id(turma_id)

        assert buscada is not None
        assert isinstance(buscada, Turma)
        assert buscada.id == turma_id
        assert buscada.nome_sistema == "TURMA_TESTE_SEM_CATEQUISTA_A"
        assert buscada.nome_exibicao == "Turma Teste Sem Catequista A"
        assert buscada.vagas_totais == 25
        assert buscada.ativa is True
        assert buscada.ano_nasc_minimo == 2012
        assert buscada.ano_nasc_maximo == 2015

        assert buscada.etapa is not None
        assert buscada.etapa.id == etapa.id
        assert buscada.etapa.nome == etapa.nome
        assert buscada.etapa.descricao == etapa.descricao
        assert buscada.etapa.ano_nasc_minimo == etapa.ano_nasc_minimo
        assert buscada.etapa.ano_nasc_maximo == etapa.ano_nasc_maximo

        assert buscada.local_encontro is not None
        assert buscada.local_encontro.id == local_encontro.id
        assert buscada.local_encontro.codigo == local_encontro.codigo
        assert buscada.local_encontro.nome_exibicao == local_encontro.nome_exibicao

        assert buscada.catequistas == []

        assert buscada.tem_vaga(10) is True
        assert buscada.tem_vaga(25) is False

        nova_turma.nome_sistema = "TURMA_TESTE_SEM_CATEQUISTA_B"
        nova_turma.nome_exibicao = "Turma Teste Sem Catequista B"
        nova_turma.vagas_totais = 30
        nova_turma.ativa = False
        nova_turma.ano_nasc_minimo = 2011
        nova_turma.ano_nasc_maximo = 2016

        resultado_editar = turma_repo.editar(nova_turma)

        assert resultado_editar is not None
        assert isinstance(resultado_editar, Turma)
        assert resultado_editar.id == turma_id
        assert resultado_editar.nome_sistema == "TURMA_TESTE_SEM_CATEQUISTA_B"
        assert resultado_editar.nome_exibicao == "Turma Teste Sem Catequista B"
        assert resultado_editar.vagas_totais == 30
        assert resultado_editar.ativa is False
        assert resultado_editar.ano_nasc_minimo == 2011
        assert resultado_editar.ano_nasc_maximo == 2016
        assert resultado_editar.catequistas == []

        buscada_editada = turma_repo.buscar_por_id(turma_id)

        assert buscada_editada is not None
        assert isinstance(buscada_editada, Turma)
        assert buscada_editada.id == turma_id
        assert buscada_editada.nome_sistema == "TURMA_TESTE_SEM_CATEQUISTA_B"
        assert buscada_editada.nome_exibicao == "Turma Teste Sem Catequista B"
        assert buscada_editada.vagas_totais == 30
        assert buscada_editada.ativa is False
        assert buscada_editada.ano_nasc_minimo == 2011
        assert buscada_editada.ano_nasc_maximo == 2016
        assert buscada_editada.catequistas == []

        resultado_apagar_turma = turma_repo.apagar(turma_id)
        assert resultado_apagar_turma is True

        turma_criada = False

        buscada_apos_apagar = turma_repo.buscar_por_id(turma_id)
        assert buscada_apos_apagar is None

        resultado_apagar_etapa = etapa_repo.apagar(etapa_id)
        assert resultado_apagar_etapa is True

        etapa_criada = False

        etapa_apos_apagar = etapa_repo.buscar_por_id(etapa_id)
        assert etapa_apos_apagar is None

    finally:
        if turma_criada:
            try:
                turma_repo.apagar(turma_id)
            except Exception:
                pass

        if etapa_criada:
            try:
                etapa_repo.apagar(etapa_id)
            except Exception:
                pass


def test_turma_repository_busca_com_catequistas():
    db = get_supabase()
    etapa_repo = EtapaRepository()
    turma_repo = TurmaRepository()

    etapa_id = str(uuid.uuid4())
    catequista_id = str(uuid.uuid4())
    turma_id = str(uuid.uuid4())

    etapa_criada = False
    catequista_criado = False
    turma_criada = False

    try:
        local_result = (
            db.table("local_encontro")
            .select("*")
            .limit(1)
            .execute()
        )
        locais = local_result.data or []
        assert len(locais) > 0, "A tabela local_encontro precisa ter ao menos 1 registro."

        local_encontro = LocalEncontro(
            id=locais[0]["id"],
            codigo=locais[0]["codigo"],
            nome_exibicao=locais[0]["nome_exibicao"],
        )

        etapa = Etapa(
            id=etapa_id,
            nome="Etapa Base para Turma Com Catequista",
            descricao="Etapa criada dentro do teste com catequista",
            ano_nasc_minimo=2010,
            ano_nasc_maximo=2016,
            sacramentos_requeridos=[],
            sacramentos_proibidos=[],
        )

        resultado_etapa = etapa_repo.salvar(etapa)
        etapa_criada = True

        assert resultado_etapa is not None
        assert isinstance(resultado_etapa, Etapa)
        assert resultado_etapa.id == etapa_id

        etapa = resultado_etapa

        resultado_catequista = (
            db.table("catequista")
            .insert({
                "id": catequista_id,
                "nome": "Catequista Teste Turma",
                "email": "catequista.turma@example.com",
                "telefone": "11999990001",
                "usuario_id": None,
            })
            .execute()
        )
        catequista_criado = True

        assert resultado_catequista.data is not None
        assert len(resultado_catequista.data) == 1
        assert resultado_catequista.data[0]["id"] == catequista_id

        catequista = Catequista(
            id=catequista_id,
            nome="Catequista Teste Turma",
            email="catequista.turma@example.com",
            telefone="11999990001",
            usuario=None,
        )

        nova_turma = Turma(
            id=turma_id,
            etapa=etapa,
            nome_sistema="TURMA_TESTE_COM_CATEQUISTA",
            nome_exibicao="Turma Teste Com Catequista",
            vagas_totais=20,
            ativa=True,
            local_encontro=local_encontro,
            ano_nasc_minimo=2012,
            ano_nasc_maximo=2015,
            catequistas=[catequista],
        )

        resultado_salvar = turma_repo.salvar(nova_turma)
        turma_criada = True

        assert resultado_salvar is not None
        assert isinstance(resultado_salvar, Turma)
        assert resultado_salvar.id == turma_id
        assert resultado_salvar.etapa.id == etapa_id
        assert resultado_salvar.local_encontro.id == local_encontro.id
        assert len(resultado_salvar.catequistas) == 1
        assert resultado_salvar.catequistas[0].id == catequista_id

        buscada = turma_repo.buscar_por_id(turma_id)

        assert buscada is not None
        assert isinstance(buscada, Turma)
        assert buscada.id == turma_id
        assert buscada.nome_sistema == "TURMA_TESTE_COM_CATEQUISTA"
        assert buscada.nome_exibicao == "Turma Teste Com Catequista"
        assert buscada.vagas_totais == 20
        assert buscada.ativa is True

        assert buscada.etapa is not None
        assert buscada.etapa.id == etapa.id
        assert buscada.local_encontro is not None
        assert buscada.local_encontro.id == local_encontro.id

        assert len(buscada.catequistas) == 1
        catequista_buscado = buscada.catequistas[0]
        assert catequista_buscado.id == catequista_id
        assert catequista_buscado.nome == "Catequista Teste Turma"
        assert catequista_buscado.email == "catequista.turma@example.com"
        assert catequista_buscado.telefone == "11999990001"

        resultado_apagar_turma = turma_repo.apagar(turma_id)
        assert resultado_apagar_turma is True

        turma_criada = False

        buscada_apos_apagar = turma_repo.buscar_por_id(turma_id)
        assert buscada_apos_apagar is None

        resultado_apagar_catequista = (
            db.table("catequista")
            .delete()
            .eq("id", catequista_id)
            .execute()
        )
        assert resultado_apagar_catequista.data is not None
        catequista_criado = False

        resultado_apagar_etapa = etapa_repo.apagar(etapa_id)
        assert resultado_apagar_etapa is True

        etapa_criada = False

        etapa_apos_apagar = etapa_repo.buscar_por_id(etapa_id)
        assert etapa_apos_apagar is None

    finally:
        if turma_criada:
            try:
                turma_repo.apagar(turma_id)
            except Exception:
                pass

        if catequista_criado:
            try:
                (
                    db.table("catequista")
                    .delete()
                    .eq("id", catequista_id)
                    .execute()
                )
            except Exception:
                pass

        if etapa_criada:
            try:
                etapa_repo.apagar(etapa_id)
            except Exception:
                pass