# test/test_etapa_repository.py
import uuid

from infra.supabaseClient import get_supabase
from domain.etapa import Etapa
from domain.sacramento import Sacramento
from repositories.etapaRepository import EtapaRepository


def test_etapa_repository_crud_basico():
    repo = EtapaRepository()

    etapa_id = str(uuid.uuid4())
    etapa_criada = False

    try:
        nova_etapa = Etapa(
            id=etapa_id,
            nome="Etapa Teste Básica",
            descricao="Etapa criada para teste básico do repositório",
            ano_nasc_minimo=2010,
            ano_nasc_maximo=2016,
            sacramentos_requeridos=[],
            sacramentos_proibidos=[],
        )

        resultado_salvar = repo.salvar(nova_etapa)
        etapa_criada = True

        assert resultado_salvar is not None
        assert isinstance(resultado_salvar, Etapa)
        assert resultado_salvar.id == etapa_id
        assert resultado_salvar.nome == "Etapa Teste Básica"
        assert resultado_salvar.descricao == "Etapa criada para teste básico do repositório"
        assert resultado_salvar.ano_nasc_minimo == 2010
        assert resultado_salvar.ano_nasc_maximo == 2016
        assert resultado_salvar.sacramentos_requeridos == []
        assert resultado_salvar.sacramentos_proibidos == []

        buscada = repo.buscar_por_id(etapa_id)

        assert buscada is not None
        assert isinstance(buscada, Etapa)
        assert buscada.id == etapa_id
        assert buscada.nome == "Etapa Teste Básica"
        assert buscada.descricao == "Etapa criada para teste básico do repositório"
        assert buscada.ano_nasc_minimo == 2010
        assert buscada.ano_nasc_maximo == 2016
        assert buscada.sacramentos_requeridos == []
        assert buscada.sacramentos_proibidos == []

        nova_etapa.nome = "Etapa Teste Básica Editada"
        nova_etapa.descricao = "Descrição alterada no teste básico"
        nova_etapa.ano_nasc_minimo = 2009
        nova_etapa.ano_nasc_maximo = 2017

        resultado_editar = repo.editar(nova_etapa)

        assert resultado_editar is not None
        assert isinstance(resultado_editar, Etapa)
        assert resultado_editar.id == etapa_id
        assert resultado_editar.nome == "Etapa Teste Básica Editada"
        assert resultado_editar.descricao == "Descrição alterada no teste básico"
        assert resultado_editar.ano_nasc_minimo == 2009
        assert resultado_editar.ano_nasc_maximo == 2017
        assert resultado_editar.sacramentos_requeridos == []
        assert resultado_editar.sacramentos_proibidos == []

        buscada_editada = repo.buscar_por_id(etapa_id)

        assert buscada_editada is not None
        assert isinstance(buscada_editada, Etapa)
        assert buscada_editada.id == etapa_id
        assert buscada_editada.nome == "Etapa Teste Básica Editada"
        assert buscada_editada.descricao == "Descrição alterada no teste básico"
        assert buscada_editada.ano_nasc_minimo == 2009
        assert buscada_editada.ano_nasc_maximo == 2017
        assert buscada_editada.sacramentos_requeridos == []
        assert buscada_editada.sacramentos_proibidos == []

        resultado_apagar = repo.apagar(etapa_id)
        assert resultado_apagar is True

        etapa_criada = False

        buscada_apos_apagar = repo.buscar_por_id(etapa_id)
        assert buscada_apos_apagar is None

    finally:
        if etapa_criada:
            try:
                repo.apagar(etapa_id)
            except Exception:
                pass


def test_etapa_repository_busca_enriquecida():
    db = get_supabase()
    repo = EtapaRepository()

    etapa_id = str(uuid.uuid4())
    etapa_criada = False

    try:
        sacramento_result = (
            db.table("sacramento")
            .select("*")
            .limit(3)
            .execute()
        )
        sacramentos_data = sacramento_result.data or []

        assert len(sacramentos_data) >= 2, "A tabela sacramento precisa ter pelo menos 2 registros."

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

        nova_etapa = Etapa(
            id=etapa_id,
            nome="Etapa Teste Enriquecida",
            descricao="Etapa criada para teste enriquecido do repositório",
            ano_nasc_minimo=2010,
            ano_nasc_maximo=2016,
            sacramentos_requeridos=[sacramento_1],
            sacramentos_proibidos=[sacramento_2],
        )

        resultado_salvar = repo.salvar(nova_etapa)
        etapa_criada = True

        assert resultado_salvar is not None
        assert isinstance(resultado_salvar, Etapa)
        assert resultado_salvar.id == etapa_id
        assert resultado_salvar.nome == "Etapa Teste Enriquecida"
        assert resultado_salvar.descricao == "Etapa criada para teste enriquecido do repositório"
        assert resultado_salvar.ano_nasc_minimo == 2010
        assert resultado_salvar.ano_nasc_maximo == 2016

        assert len(resultado_salvar.sacramentos_requeridos) == 1
        assert resultado_salvar.sacramentos_requeridos[0].id == sacramento_1.id
        assert resultado_salvar.sacramentos_requeridos[0].codigo == sacramento_1.codigo
        assert resultado_salvar.sacramentos_requeridos[0].nome_exibicao == sacramento_1.nome_exibicao

        assert len(resultado_salvar.sacramentos_proibidos) == 1
        assert resultado_salvar.sacramentos_proibidos[0].id == sacramento_2.id
        assert resultado_salvar.sacramentos_proibidos[0].codigo == sacramento_2.codigo
        assert resultado_salvar.sacramentos_proibidos[0].nome_exibicao == sacramento_2.nome_exibicao

        buscada = repo.buscar_por_id(etapa_id)

        assert buscada is not None
        assert isinstance(buscada, Etapa)
        assert buscada.id == etapa_id
        assert buscada.nome == "Etapa Teste Enriquecida"
        assert buscada.descricao == "Etapa criada para teste enriquecido do repositório"
        assert buscada.ano_nasc_minimo == 2010
        assert buscada.ano_nasc_maximo == 2016

        assert len(buscada.sacramentos_requeridos) == 1
        assert buscada.sacramentos_requeridos[0].id == sacramento_1.id
        assert buscada.sacramentos_requeridos[0].codigo == sacramento_1.codigo
        assert buscada.sacramentos_requeridos[0].nome_exibicao == sacramento_1.nome_exibicao

        assert len(buscada.sacramentos_proibidos) == 1
        assert buscada.sacramentos_proibidos[0].id == sacramento_2.id
        assert buscada.sacramentos_proibidos[0].codigo == sacramento_2.codigo
        assert buscada.sacramentos_proibidos[0].nome_exibicao == sacramento_2.nome_exibicao

        nova_etapa.nome = "Etapa Teste Enriquecida Editada"
        nova_etapa.descricao = "Descrição alterada no teste enriquecido"
        nova_etapa.ano_nasc_minimo = 2009
        nova_etapa.ano_nasc_maximo = 2017
        nova_etapa.sacramentos_requeridos = [sacramento_2]
        nova_etapa.sacramentos_proibidos = [sacramento_1]

        resultado_editar = repo.editar(nova_etapa)

        assert resultado_editar is not None
        assert isinstance(resultado_editar, Etapa)
        assert resultado_editar.id == etapa_id
        assert resultado_editar.nome == "Etapa Teste Enriquecida Editada"
        assert resultado_editar.descricao == "Descrição alterada no teste enriquecido"
        assert resultado_editar.ano_nasc_minimo == 2009
        assert resultado_editar.ano_nasc_maximo == 2017

        assert len(resultado_editar.sacramentos_requeridos) == 1
        assert resultado_editar.sacramentos_requeridos[0].id == sacramento_2.id
        assert resultado_editar.sacramentos_requeridos[0].codigo == sacramento_2.codigo
        assert resultado_editar.sacramentos_requeridos[0].nome_exibicao == sacramento_2.nome_exibicao

        assert len(resultado_editar.sacramentos_proibidos) == 1
        assert resultado_editar.sacramentos_proibidos[0].id == sacramento_1.id
        assert resultado_editar.sacramentos_proibidos[0].codigo == sacramento_1.codigo
        assert resultado_editar.sacramentos_proibidos[0].nome_exibicao == sacramento_1.nome_exibicao

        buscada_editada = repo.buscar_por_id(etapa_id)

        assert buscada_editada is not None
        assert isinstance(buscada_editada, Etapa)
        assert buscada_editada.id == etapa_id
        assert buscada_editada.nome == "Etapa Teste Enriquecida Editada"
        assert buscada_editada.descricao == "Descrição alterada no teste enriquecido"
        assert buscada_editada.ano_nasc_minimo == 2009
        assert buscada_editada.ano_nasc_maximo == 2017

        assert len(buscada_editada.sacramentos_requeridos) == 1
        assert buscada_editada.sacramentos_requeridos[0].id == sacramento_2.id
        assert buscada_editada.sacramentos_requeridos[0].codigo == sacramento_2.codigo
        assert buscada_editada.sacramentos_requeridos[0].nome_exibicao == sacramento_2.nome_exibicao

        assert len(buscada_editada.sacramentos_proibidos) == 1
        assert buscada_editada.sacramentos_proibidos[0].id == sacramento_1.id
        assert buscada_editada.sacramentos_proibidos[0].codigo == sacramento_1.codigo
        assert buscada_editada.sacramentos_proibidos[0].nome_exibicao == sacramento_1.nome_exibicao

        resultado_apagar = repo.apagar(etapa_id)
        assert resultado_apagar is True

        etapa_criada = False

        buscada_apos_apagar = repo.buscar_por_id(etapa_id)
        assert buscada_apos_apagar is None

    finally:
        if etapa_criada:
            try:
                repo.apagar(etapa_id)
            except Exception:
                pass