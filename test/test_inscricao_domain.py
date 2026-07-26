# test/test_inscricao_domain.py

import pytest
from dataclasses import dataclass
from datetime import datetime

from app.domain.inscricao import Inscricao
from app.domain.statusInscricao import StatusInscricao


_SENTINELA = object()


@dataclass
class CatequizandoFake:
    id: str
    ano_nascimento: int = 2015


@dataclass
class ResponsavelFake:
    id: str


@dataclass
class EtapaFake:
    id: str

    def aceita_catequizando(self, catequizando) -> bool:
        return catequizando is not None and catequizando.ano_nascimento >= 2010


@dataclass
class TurmaFake:
    id: str
    etapa: object
    aceita_resultado: bool = True

    def pertence_a_etapa(self, etapa) -> bool:
        return etapa is not None and self.etapa.id == etapa.id

    def aceita_catequizando(self, catequizando) -> bool:
        return self.aceita_resultado and catequizando is not None


@dataclass
class UsuarioFake:
    id: str


def criar_status(
    id: int = 1,
    codigo: str = "pendente_distribuicao",
    descricao: str = "Pendente de distribuição em turma",
) -> StatusInscricao:
    return StatusInscricao(
        id=id,
        codigo=codigo,
        descricao=descricao,
    )


def criar_catequizando(
    id: str = "cat-1",
    ano_nascimento: int = 2015,
) -> CatequizandoFake:
    return CatequizandoFake(
        id=id,
        ano_nascimento=ano_nascimento,
    )


def criar_responsavel(id: str = "resp-1") -> ResponsavelFake:
    return ResponsavelFake(id=id)


def criar_etapa(id: str = "etapa-1") -> EtapaFake:
    return EtapaFake(id=id)


def criar_turma(
    id: str = "turma-1",
    etapa: object | None = None,
    aceita_resultado: bool = True,
) -> TurmaFake:
    return TurmaFake(
        id=id,
        etapa=etapa or criar_etapa(),
        aceita_resultado=aceita_resultado,
    )


def criar_usuario(id: str = "user-1") -> UsuarioFake:
    return UsuarioFake(id=id)


def criar_inscricao(
    id: str = "insc-1",
    catequizando: object = _SENTINELA,
    responsavel: object = _SENTINELA,
    etapa: object = _SENTINELA,
    status: object = _SENTINELA,
    data_inscricao: datetime | None = None,
    turma: object | None = None,
    termo_assinado: bool = False,
    quer_mesma_turma_que_irmao: bool = False,
    referencia_irmao: str | None = None,
    observacao_responsavel: str | None = None,
    override_idade: bool = False,
    motivo_override: str | None = None,
    usuario_override: object | None = None,
) -> Inscricao:
    if catequizando is _SENTINELA:
        catequizando = criar_catequizando()

    if responsavel is _SENTINELA:
        responsavel = criar_responsavel()

    if etapa is _SENTINELA:
        etapa = criar_etapa()

    if status is _SENTINELA:
        status = criar_status()

    return Inscricao(
        id=id,
        catequizando=catequizando,
        responsavel=responsavel,
        etapa=etapa,
        status=status,
        data_inscricao=data_inscricao,
        turma=turma,
        termo_assinado=termo_assinado,
        quer_mesma_turma_que_irmao=quer_mesma_turma_que_irmao,
        referencia_irmao=referencia_irmao,
        observacao_responsavel=observacao_responsavel,
        override_idade=override_idade,
        motivo_override=motivo_override,
        usuario_override=usuario_override,
    )


def test_inscricao_criacao_valida():
    status = criar_status()
    inscricao = criar_inscricao(status=status)

    assert inscricao.id == "insc-1"
    assert inscricao.status == status
    assert inscricao.termo_assinado is False
    assert inscricao.turma is None
    assert inscricao.override_idade is False


def test_inscricao_normaliza_campos_textuais():
    inscricao = criar_inscricao(
        id="  insc-1  ",
        referencia_irmao="  irmao-123  ",
        observacao_responsavel="  observacao  ",
    )

    assert inscricao.id == "insc-1"
    assert inscricao.referencia_irmao is None
    assert inscricao.observacao_responsavel == "observacao"


def test_inscricao_nao_permite_id_vazio():
    with pytest.raises(ValueError, match=r"id da inscrição é obrigatório"):
        criar_inscricao(id="   ")


def test_inscricao_nao_permite_catequizando_nulo():
    with pytest.raises(ValueError, match=r"catequizando da inscrição é obrigatório"):
        criar_inscricao(catequizando=None)


def test_inscricao_nao_permite_responsavel_nulo():
    with pytest.raises(ValueError, match=r"responsável da inscrição é obrigatório"):
        criar_inscricao(responsavel=None)


def test_inscricao_nao_permite_etapa_nula():
    with pytest.raises(ValueError, match=r"etapa da inscrição é obrigatória"):
        criar_inscricao(etapa=None)


def test_inscricao_nao_permite_status_nulo():
    with pytest.raises(ValueError, match=r"status da inscrição é obrigatório"):
        criar_inscricao(status=None)


def test_inscricao_nao_permite_status_invalido():
    status = criar_status(codigo="desconhecido", descricao="Inválido")

    with pytest.raises(ValueError, match=r"Status da inscrição inválido"):
        criar_inscricao(status=status)


def test_inscricao_nao_permite_status_que_nao_seja_status_inscricao():
    with pytest.raises(ValueError, match=r"status da inscrição deve ser um StatusInscricao válido"):
        criar_inscricao(status="PENDENTE_DISTRIBUICAO")


def test_inscricao_exige_referencia_quando_quer_mesma_turma_que_irmao():
    with pytest.raises(ValueError, match=r"referência do irmão é obrigatória"):
        criar_inscricao(
            quer_mesma_turma_que_irmao=True,
            referencia_irmao="   ",
        )


def test_inscricao_limpa_referencia_quando_nao_ha_preferencia_irmao():
    inscricao = criar_inscricao(
        quer_mesma_turma_que_irmao=False,
        referencia_irmao="irmao-1",
    )

    assert inscricao.referencia_irmao is None


def test_inscricao_exige_motivo_e_usuario_quando_override_ativo():
    with pytest.raises(ValueError, match=r"motivo do override de idade é obrigatório"):
        criar_inscricao(
            override_idade=True,
            motivo_override="   ",
            usuario_override=criar_usuario(),
        )

    with pytest.raises(ValueError, match=r"usuário autorizador do override de idade é obrigatório"):
        criar_inscricao(
            override_idade=True,
            motivo_override="Exceção pastoral",
            usuario_override=None,
        )


def test_inscricao_limpa_override_quando_override_inativo():
    inscricao = criar_inscricao(
        override_idade=False,
        motivo_override="Exceção pastoral",
        usuario_override=criar_usuario(),
    )

    assert inscricao.motivo_override is None
    assert inscricao.usuario_override is None


def test_inscricao_nao_permite_turma_de_outra_etapa():
    etapa_1 = criar_etapa(id="etapa-1")
    etapa_2 = criar_etapa(id="etapa-2")
    turma = criar_turma(etapa=etapa_2)

    with pytest.raises(ValueError, match=r"turma da inscrição deve pertencer à mesma etapa"):
        criar_inscricao(
            etapa=etapa_1,
            turma=turma,
        )


def test_inscricao_assinar_termo_define_termo_e_data():
    inscricao = criar_inscricao(data_inscricao=None)

    inscricao.assinar_termo()

    assert inscricao.termo_assinado is True
    assert inscricao.data_inscricao is not None


def test_inscricao_assinar_termo_nao_sobrescreve_data_existente():
    data = datetime(2026, 1, 10, 10, 0, 0)
    inscricao = criar_inscricao(data_inscricao=data)

    inscricao.assinar_termo()

    assert inscricao.data_inscricao == data


def test_inscricao_definir_status_atualiza_status():
    novo_status = criar_status(
        id=2,
        codigo="confirmada",
        descricao="Inscrição confirmada",
    )
    inscricao = criar_inscricao()

    inscricao.definir_status(novo_status)

    assert inscricao.status == novo_status


def test_inscricao_definir_status_exige_status_valido():
    inscricao = criar_inscricao()

    with pytest.raises(ValueError, match=r"novo status da inscrição é obrigatório"):
        inscricao.definir_status(None)

    with pytest.raises(ValueError, match=r"novo status da inscrição deve ser um StatusInscricao válido"):
        inscricao.definir_status("CONFIRMADA")


def test_inscricao_confirmar_atualiza_status():
    inscricao = criar_inscricao()

    inscricao.confirmar()

    assert inscricao.status.eh("confirmada") is True


def test_inscricao_colocar_em_lista_espera_atualiza_status():
    inscricao = criar_inscricao()

    inscricao.colocar_em_lista_espera()

    assert inscricao.status.eh("lista_espera") is True


def test_inscricao_marcar_pendente_distribuicao_atualiza_status():
    inscricao = criar_inscricao(
        status=criar_status(
            id=2,
            codigo="confirmada",
            descricao="Inscrição confirmada",
        )
    )

    inscricao.marcar_pendente_distribuicao()

    assert inscricao.status.eh("pendente_distribuicao") is True


def test_inscricao_atribuir_turma_com_sucesso():
    etapa = criar_etapa(id="etapa-1")
    turma = criar_turma(etapa=etapa)
    inscricao = criar_inscricao(etapa=etapa)

    inscricao.atribuir_turma(turma)

    assert inscricao.turma == turma


def test_inscricao_atribuir_turma_exige_turma_valida():
    inscricao = criar_inscricao()

    with pytest.raises(ValueError, match=r"turma informada para a inscrição é obrigatória"):
        inscricao.atribuir_turma(None)


def test_inscricao_atribuir_turma_exige_mesma_etapa():
    etapa_1 = criar_etapa(id="etapa-1")
    etapa_2 = criar_etapa(id="etapa-2")
    turma = criar_turma(etapa=etapa_2)
    inscricao = criar_inscricao(etapa=etapa_1)

    with pytest.raises(ValueError, match=r"turma da inscrição deve pertencer à mesma etapa"):
        inscricao.atribuir_turma(turma)


def test_inscricao_remover_turma():
    etapa = criar_etapa()
    turma = criar_turma(etapa=etapa)
    inscricao = criar_inscricao(etapa=etapa, turma=turma)

    inscricao.remover_turma()

    assert inscricao.turma is None


def test_inscricao_pode_ser_distribuida_para_retorna_true_quando_compativel():
    etapa = criar_etapa(id="etapa-1")
    catequizando = criar_catequizando(ano_nascimento=2015)
    turma = criar_turma(etapa=etapa, aceita_resultado=True)
    inscricao = criar_inscricao(
        catequizando=catequizando,
        etapa=etapa,
    )

    assert inscricao.pode_ser_distribuida_para(turma) is True


def test_inscricao_pode_ser_distribuida_para_retorna_false_quando_turma_for_none():
    inscricao = criar_inscricao()

    assert inscricao.pode_ser_distribuida_para(None) is False


def test_inscricao_pode_ser_distribuida_para_retorna_false_quando_turma_for_outra_etapa():
    etapa_1 = criar_etapa(id="etapa-1")
    etapa_2 = criar_etapa(id="etapa-2")
    turma = criar_turma(etapa=etapa_2)
    inscricao = criar_inscricao(etapa=etapa_1)

    assert inscricao.pode_ser_distribuida_para(turma) is False


def test_inscricao_pode_ser_distribuida_para_retorna_false_quando_etapa_nao_aceita():
    etapa = criar_etapa(id="etapa-1")
    catequizando = criar_catequizando(ano_nascimento=2008)
    turma = criar_turma(etapa=etapa, aceita_resultado=True)
    inscricao = criar_inscricao(
        catequizando=catequizando,
        etapa=etapa,
    )

    assert inscricao.pode_ser_distribuida_para(turma) is False


def test_inscricao_pode_ser_distribuida_para_retorna_false_quando_turma_nao_aceita():
    etapa = criar_etapa(id="etapa-1")
    catequizando = criar_catequizando(ano_nascimento=2015)
    turma = criar_turma(etapa=etapa, aceita_resultado=False)
    inscricao = criar_inscricao(
        catequizando=catequizando,
        etapa=etapa,
    )

    assert inscricao.pode_ser_distribuida_para(turma) is False


def test_inscricao_registrar_override_com_sucesso():
    inscricao = criar_inscricao()
    usuario = criar_usuario()

    inscricao.registrar_override(usuario=usuario, motivo="  Exceção pastoral  ")

    assert inscricao.override_idade is True
    assert inscricao.motivo_override == "Exceção pastoral"
    assert inscricao.usuario_override == usuario


def test_inscricao_registrar_override_exige_usuario_e_motivo():
    inscricao = criar_inscricao()
    usuario = criar_usuario()

    with pytest.raises(ValueError, match=r"motivo do override de idade é obrigatório"):
        inscricao.registrar_override(usuario=usuario, motivo="   ")

    with pytest.raises(ValueError, match=r"usuário autorizador do override de idade é obrigatório"):
        inscricao.registrar_override(usuario=None, motivo="Exceção pastoral")


def test_inscricao_marcar_override_idade_delega_para_registrar_override():
    inscricao = criar_inscricao()
    usuario = criar_usuario()

    inscricao.marcar_override_idade(motivo="  Exceção pastoral  ", usuario=usuario)

    assert inscricao.override_idade is True
    assert inscricao.motivo_override == "Exceção pastoral"
    assert inscricao.usuario_override == usuario


def test_inscricao_limpar_override_idade():
    inscricao = criar_inscricao()
    usuario = criar_usuario()

    inscricao.registrar_override(usuario=usuario, motivo="Exceção pastoral")
    inscricao.limpar_override_idade()

    assert inscricao.override_idade is False
    assert inscricao.motivo_override is None
    assert inscricao.usuario_override is None


def test_inscricao_marcar_preferencia_irmao_com_sucesso():
    inscricao = criar_inscricao()

    inscricao.marcar_preferencia_irmao("  irmao-123  ")

    assert inscricao.quer_mesma_turma_que_irmao is True
    assert inscricao.referencia_irmao == "irmao-123"


def test_inscricao_marcar_preferencia_irmao_exige_referencia():
    inscricao = criar_inscricao()

    with pytest.raises(ValueError, match=r"referência do irmão é obrigatória"):
        inscricao.marcar_preferencia_irmao("   ")


def test_inscricao_limpar_preferencia_irmao():
    inscricao = criar_inscricao()
    inscricao.marcar_preferencia_irmao("irmao-123")

    inscricao.limpar_preferencia_irmao()

    assert inscricao.quer_mesma_turma_que_irmao is False
    assert inscricao.referencia_irmao is None


def test_inscricao_registrar_observacao_responsavel():
    inscricao = criar_inscricao()

    inscricao.registrar_observacao_responsavel("  observacao importante  ")
    assert inscricao.observacao_responsavel == "observacao importante"

    inscricao.registrar_observacao_responsavel("   ")
    assert inscricao.observacao_responsavel is None

    inscricao.registrar_observacao_responsavel(None)
    assert inscricao.observacao_responsavel is None


def test_inscricao_pertence_ao_catequizando():
    inscricao = criar_inscricao(catequizando=criar_catequizando(id="cat-1"))

    assert inscricao.pertence_ao_catequizando(criar_catequizando(id="cat-1")) is True
    assert inscricao.pertence_ao_catequizando(criar_catequizando(id="cat-2")) is False
    assert inscricao.pertence_ao_catequizando(None) is False


def test_inscricao_pertence_ao_responsavel():
    inscricao = criar_inscricao(responsavel=criar_responsavel(id="resp-1"))

    assert inscricao.pertence_ao_responsavel(criar_responsavel(id="resp-1")) is True
    assert inscricao.pertence_ao_responsavel(criar_responsavel(id="resp-2")) is False
    assert inscricao.pertence_ao_responsavel(None) is False


def test_inscricao_pertence_a_etapa():
    inscricao = criar_inscricao(etapa=criar_etapa(id="etapa-1"))

    assert inscricao.pertence_a_etapa(criar_etapa(id="etapa-1")) is True
    assert inscricao.pertence_a_etapa(criar_etapa(id="etapa-2")) is False
    assert inscricao.pertence_a_etapa(None) is False


def test_inscricao_possui_turma_e_override():
    etapa = criar_etapa()
    turma = criar_turma(etapa=etapa)
    inscricao = criar_inscricao(etapa=etapa, turma=turma)

    assert inscricao.possui_turma() is True
    assert inscricao.possui_override_idade() is False

    inscricao.registrar_override(usuario=criar_usuario(), motivo="Exceção pastoral")

    assert inscricao.possui_override_idade() is True