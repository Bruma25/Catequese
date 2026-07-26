# test/test_servico_inscricao.py
import pytest
from dataclasses import dataclass
from typing import Optional

from domain.servicoInscricao import ServicoInscricao
from domain.statusInscricao import StatusInscricao

@dataclass
class CatequizandoFake:
    id: str
    ano_nascimento: int
    sacramentos_ids: set[int]

    def possui_sacramento(self, sacramento) -> bool:
        return sacramento.id in self.sacramentos_ids


@dataclass
class ResponsavelFake:
    id: str
    vinculos: set[str]

    def pode_responder_por(self, catequizando: CatequizandoFake) -> bool:
        return catequizando.id in self.vinculos


@dataclass
class EtapaFake:
    id: str
    ano_nasc_minimo: int | None = None
    ano_nasc_maximo: int | None = None
    sacramentos_requeridos_ids: set[int] | None = None
    sacramentos_proibidos_ids: set[int] | None = None

    def __post_init__(self):
        if self.sacramentos_requeridos_ids is None:
            self.sacramentos_requeridos_ids = set()
        if self.sacramentos_proibidos_ids is None:
            self.sacramentos_proibidos_ids = set()

    def aceita_catequizando(self, catequizando: CatequizandoFake) -> bool:
        if not self._verifica_idade(catequizando):
            return False
        if not self._verifica_sacramentos(catequizando):
            return False
        return True

    def pode_catequizando_entrar(self, catequizando: CatequizandoFake) -> bool:
        return self.aceita_catequizando(catequizando)

    def _verifica_idade(self, catequizando: CatequizandoFake) -> bool:
        ano = catequizando.ano_nascimento
        if self.ano_nasc_minimo is not None and ano < self.ano_nasc_minimo:
            return False
        if self.ano_nasc_maximo is not None and ano > self.ano_nasc_maximo:
            return False
        return True

    def _verifica_sacramentos(self, catequizando: CatequizandoFake) -> bool:
        for sac_id in self.sacramentos_requeridos_ids:
            if sac_id not in catequizando.sacramentos_ids:
                return False
        for sac_id in self.sacramentos_proibidos_ids:
            if sac_id in catequizando.sacramentos_ids:
                return False
        return True


@dataclass
class TurmaFake:
    id: str
    etapa: EtapaFake
    ativa: bool = True
    ano_nasc_minimo: int | None = None
    ano_nasc_maximo: int | None = None
    vagas_totais: int = 10
    bloqueia_mesmo_com_override: bool = False

    def pertence_a_etapa(self, etapa: EtapaFake) -> bool:
        if etapa is None:
            return False
        return self.etapa.id == etapa.id

    def esta_ativa(self) -> bool:
        return self.ativa is True

    def tem_vaga(self, inscricoes_confirmadas: int) -> bool:
        return inscricoes_confirmadas < self.vagas_totais

    def verifica_idade_especifica(self, catequizando: CatequizandoFake) -> bool:
        ano = catequizando.ano_nascimento
        if self.ano_nasc_minimo is not None and ano < self.ano_nasc_minimo:
            return False
        if self.ano_nasc_maximo is not None and ano > self.ano_nasc_maximo:
            return False
        return True

    def aceita_catequizando_sem_restricao_etaria(self, catequizando: CatequizandoFake) -> bool:
        if catequizando is None:
            return False
        if not self.esta_ativa():
            return False
        if self.bloqueia_mesmo_com_override:
            return False
        return True

    def aceita_catequizando(self, catequizando: CatequizandoFake) -> bool:
        if not self.aceita_catequizando_sem_restricao_etaria(catequizando):
            return False
        if not self.verifica_idade_especifica(catequizando):
            return False
        return True


@dataclass
class UsuarioFake:
    id: str


@dataclass
class InscricaoFake:
    id: str
    catequizando: CatequizandoFake
    responsavel: ResponsavelFake
    etapa: EtapaFake
    status: StatusInscricao
    termo_assinado: bool = False
    turma: Optional[TurmaFake] = None
    observacao_responsavel: Optional[str] = None
    quer_mesma_turma_que_irmao: bool = False
    referencia_irmao: Optional[str] = None
    override_idade: bool = False
    motivo_override: Optional[str] = None
    usuario_override: Optional[UsuarioFake] = None

    STATUS_PENDENTE_DISTRIBUICAO = "PENDENTE_DISTRIBUICAO"
    STATUS_CONFIRMADA = "CONFIRMADA"
    STATUS_LISTA_ESPERA = "LISTA_ESPERA"

    def registrar_observacao_responsavel(self, observacao: Optional[str]) -> None:
        if observacao is None:
            self.observacao_responsavel = None
            return
        texto = observacao.strip()
        self.observacao_responsavel = texto or None

    def marcar_preferencia_irmao(self, referencia: str) -> None:
        texto = (referencia or "").strip()
        if not texto:
            raise ValueError("A referência do irmão é obrigatória.")
        self.quer_mesma_turma_que_irmao = True
        self.referencia_irmao = texto

    def possui_override_idade(self) -> bool:
        return self.override_idade

    def registrar_override(self, usuario, motivo) -> None:
        texto = (motivo or "").strip()
        if not texto:
            raise ValueError("O motivo do override de idade é obrigatório.")
        if usuario is None:
            raise ValueError("O usuário autorizador do override de idade é obrigatório.")
        self.override_idade = True
        self.motivo_override = texto
        self.usuario_override = usuario

    def limpar_override_idade(self) -> None:
        self.override_idade = False
        self.motivo_override = None
        self.usuario_override = None

    def atribuir_turma(self, turma: TurmaFake) -> None:
        if turma is None:
            raise ValueError("A turma informada para a inscrição é obrigatória.")
        if turma.etapa.id != self.etapa.id:
            raise ValueError("A turma da inscrição deve pertencer à mesma etapa da inscrição.")
        self.turma = turma

    def confirmar(self) -> None:
        self.status = criar_status("CONFIRMADA", "Inscrição confirmada")

    def colocar_em_lista_espera(self) -> None:
        self.status = criar_status("LISTA_ESPERA", "Aguardando vaga")

    def pode_ser_distribuida_para(self, turma: TurmaFake) -> bool:
        if turma is None:
            return False
        if self.catequizando is None:
            return False
        if not turma.pertence_a_etapa(self.etapa):
            return False
        if not self.etapa.aceita_catequizando(self.catequizando):
            return False
        if not turma.aceita_catequizando(self.catequizando):
            return False
        return True

    def pode_ser_distribuida_para_com_override_idade(self, turma: TurmaFake) -> bool:
        if turma is None:
            return False
        if self.catequizando is None:
            return False
        if not turma.pertence_a_etapa(self.etapa):
            return False
        if not self.etapa.aceita_catequizando(self.catequizando):
            return False
        if not turma.aceita_catequizando_sem_restricao_etaria(self.catequizando):
            return False
        return True


def criar_status(
    codigo: str = "PENDENTE_DISTRIBUICAO",
    descricao: str = "Pendente de distribuição em turma",
) -> StatusInscricao:
    return StatusInscricao(
        id=1,
        codigo=codigo,
        descricao=descricao,
    )


def criar_servico() -> ServicoInscricao:
    return ServicoInscricao(
        status_pendente_distribuicao=criar_status("PENDENTE_DISTRIBUICAO"),
    )


def criar_catequizando(
    id: str = "cat-1",
    ano_nascimento: int = 2014,
    sacramentos_ids: set[int] | None = None,
) -> CatequizandoFake:
    return CatequizandoFake(
        id=id,
        ano_nascimento=ano_nascimento,
        sacramentos_ids=sacramentos_ids or set(),
    )


def criar_responsavel(
    id: str = "resp-1",
    vinculos: set[str] | None = None,
) -> ResponsavelFake:
    return ResponsavelFake(
        id=id,
        vinculos=vinculos or {"cat-1"},
    )


def criar_etapa(
    id: str = "etapa-1",
    ano_nasc_minimo: int | None = None,
    ano_nasc_maximo: int | None = None,
    sacramentos_requeridos_ids: set[int] | None = None,
    sacramentos_proibidos_ids: set[int] | None = None,
) -> EtapaFake:
    return EtapaFake(
        id=id,
        ano_nasc_minimo=ano_nasc_minimo,
        ano_nasc_maximo=ano_nasc_maximo,
        sacramentos_requeridos_ids=sacramentos_requeridos_ids or set(),
        sacramentos_proibidos_ids=sacramentos_proibidos_ids or set(),
    )


def criar_turma(
    id: str = "turma-1",
    etapa=None,
    ativa: bool = True,
    ano_nasc_minimo: int | None = None,
    ano_nasc_maximo: int | None = None,
    vagas_totais: int = 10,
    bloqueia_mesmo_com_override: bool = False,
) -> TurmaFake:
    return TurmaFake(
        id=id,
        etapa=etapa or criar_etapa(),
        ativa=ativa,
        ano_nasc_minimo=ano_nasc_minimo,
        ano_nasc_maximo=ano_nasc_maximo,
        vagas_totais=vagas_totais,
        bloqueia_mesmo_com_override=bloqueia_mesmo_com_override,
    )


def test_servico_inscricao_criacao_valida():
    servico = criar_servico()

    assert servico.status_pendente_distribuicao.codigo == "PENDENTE_DISTRIBUICAO"


def test_servico_inscricao_nao_permite_status_pendente_nulo():
    with pytest.raises(ValueError, match=r"status pendente de distribuição é obrigatório"):
        ServicoInscricao(status_pendente_distribuicao=None)


def test_sugerir_etapas_para_catequizando_retorna_apenas_etapas_elegiveis():
    servico = criar_servico()

    etapa_elegivel = criar_etapa(
        id="etapa-1",
        ano_nasc_minimo=2012,
        ano_nasc_maximo=2016,
    )
    etapa_inelegivel = criar_etapa(
        id="etapa-2",
        ano_nasc_minimo=2010,
        ano_nasc_maximo=2012,
    )

    catequizando = criar_catequizando(ano_nascimento=2014)

    etapas_sugeridas = servico.sugerir_etapas_para_catequizando(
        catequizando=catequizando,
        etapas=[etapa_elegivel, etapa_inelegivel],
    )

    assert etapas_sugeridas == [etapa_elegivel]


def test_sugerir_etapas_para_catequizando_retorna_lista_vazia_para_none():
    servico = criar_servico()
    catequizando = criar_catequizando()

    assert servico.sugerir_etapas_para_catequizando(
        catequizando=catequizando,
        etapas=None,
    ) == []


def test_sugerir_etapas_para_catequizando_nao_permite_catequizando_nulo():
    servico = criar_servico()

    with pytest.raises(ValueError, match=r"catequizando para sugestão de etapas é obrigatório"):
        servico.sugerir_etapas_para_catequizando(
            catequizando=None,
            etapas=[],
        )


def test_criar_inscricao_valida():
    servico = criar_servico()
    catequizando = criar_catequizando()
    responsavel = criar_responsavel(vinculos={"cat-1"})
    etapa = criar_etapa(ano_nasc_minimo=2012, ano_nasc_maximo=2016)

    inscricao = servico.criar_inscricao(
        id_inscricao="insc-1",
        catequizando=catequizando,
        responsavel=responsavel,
        etapa=etapa,
    )

    assert inscricao.id == "insc-1"
    assert inscricao.catequizando == catequizando
    assert inscricao.responsavel == responsavel
    assert inscricao.etapa == etapa
    assert inscricao.status.codigo == "PENDENTE_DISTRIBUICAO"


def test_criar_inscricao_nao_permite_responsavel_sem_vinculo():
    servico = criar_servico()
    catequizando = criar_catequizando()
    responsavel = criar_responsavel(vinculos={"cat-2"})
    etapa = criar_etapa()

    with pytest.raises(ValueError, match=r"responsável informado não possui vínculo com o catequizando"):
        servico.criar_inscricao(
            id_inscricao="insc-1",
            catequizando=catequizando,
            responsavel=responsavel,
            etapa=etapa,
        )


def test_criar_inscricao_nao_permite_catequizando_inelegivel():
    servico = criar_servico()
    catequizando = criar_catequizando(ano_nascimento=2010)
    responsavel = criar_responsavel(vinculos={"cat-1"})
    etapa = criar_etapa(ano_nasc_minimo=2012, ano_nasc_maximo=2016)

    with pytest.raises(ValueError, match=r"catequizando não atende aos requisitos da etapa"):
        servico.criar_inscricao(
            id_inscricao="insc-1",
            catequizando=catequizando,
            responsavel=responsavel,
            etapa=etapa,
        )


def test_criar_inscricao_nao_permite_catequizando_nulo():
    servico = criar_servico()
    responsavel = criar_responsavel()
    etapa = criar_etapa()

    with pytest.raises(ValueError, match=r"catequizando da inscrição é obrigatório"):
        servico.criar_inscricao(
            id_inscricao="insc-1",
            catequizando=None,
            responsavel=responsavel,
            etapa=etapa,
        )


def test_criar_inscricao_nao_permite_responsavel_nulo():
    servico = criar_servico()
    catequizando = criar_catequizando()
    etapa = criar_etapa()

    with pytest.raises(ValueError, match=r"responsável da inscrição é obrigatório"):
        servico.criar_inscricao(
            id_inscricao="insc-1",
            catequizando=catequizando,
            responsavel=None,
            etapa=etapa,
        )


def test_criar_inscricao_nao_permite_etapa_nula():
    servico = criar_servico()
    catequizando = criar_catequizando()
    responsavel = criar_responsavel()

    with pytest.raises(ValueError, match=r"etapa da inscrição é obrigatória"):
        servico.criar_inscricao(
            id_inscricao="insc-1",
            catequizando=catequizando,
            responsavel=responsavel,
            etapa=None,
        )


def test_criar_inscricao_registra_observacao_responsavel():
    servico = criar_servico()
    catequizando = criar_catequizando()
    responsavel = criar_responsavel(vinculos={"cat-1"})
    etapa = criar_etapa()

    inscricao = servico.criar_inscricao(
        id_inscricao="insc-1",
        catequizando=catequizando,
        responsavel=responsavel,
        etapa=etapa,
        observacao_responsavel="  Observação importante  ",
    )

    assert inscricao.observacao_responsavel == "Observação importante"


def test_criar_inscricao_marca_preferencia_irmao_quando_informada():
    servico = criar_servico()
    catequizando = criar_catequizando()
    responsavel = criar_responsavel(vinculos={"cat-1"})
    etapa = criar_etapa()

    inscricao = servico.criar_inscricao(
        id_inscricao="insc-1",
        catequizando=catequizando,
        responsavel=responsavel,
        etapa=etapa,
        referencia_irmao="  irmão-123  ",
    )

    assert inscricao.quer_mesma_turma_que_irmao is True
    assert inscricao.referencia_irmao == "irmão-123"


def test_distribuir_inscricao_em_turma_valida_confirma_quando_ha_vaga():
    servico = criar_servico()
    etapa = criar_etapa()
    turma = criar_turma(etapa=etapa, ativa=True, vagas_totais=10)
    catequizando = criar_catequizando(ano_nascimento=2014)
    responsavel = criar_responsavel(vinculos={"cat-1"})

    inscricao = servico.criar_inscricao(
        id_inscricao="insc-1",
        catequizando=catequizando,
        responsavel=responsavel,
        etapa=etapa,
    )

    servico.distribuir_inscricao_em_turma(
        inscricao=inscricao,
        turma=turma,
        numero_confirmadas=5,
    )

    assert inscricao.turma == turma
    assert inscricao.status.codigo == "CONFIRMADA"


def test_distribuir_inscricao_em_turma_coloca_em_lista_espera_quando_sem_vaga():
    servico = criar_servico()
    etapa = criar_etapa()
    turma = criar_turma(etapa=etapa, ativa=True, vagas_totais=2)
    catequizando = criar_catequizando(ano_nascimento=2014)
    responsavel = criar_responsavel(vinculos={"cat-1"})

    inscricao = servico.criar_inscricao(
        id_inscricao="insc-1",
        catequizando=catequizando,
        responsavel=responsavel,
        etapa=etapa,
    )

    servico.distribuir_inscricao_em_turma(
        inscricao=inscricao,
        turma=turma,
        numero_confirmadas=2,
    )

    assert inscricao.turma == turma
    assert inscricao.status.codigo == "LISTA_ESPERA"


def test_distribuir_inscricao_em_turma_nao_permite_turma_de_outra_etapa():
    servico = criar_servico()
    etapa_inscricao = criar_etapa(id="etapa-1")
    etapa_turma = criar_etapa(id="etapa-2")
    turma = criar_turma(etapa=etapa_turma)
    catequizando = criar_catequizando()
    responsavel = criar_responsavel(vinculos={"cat-1"})

    inscricao = servico.criar_inscricao(
        id_inscricao="insc-1",
        catequizando=catequizando,
        responsavel=responsavel,
        etapa=etapa_inscricao,
    )

    with pytest.raises(ValueError, match=r"turma informada não pertence à etapa da inscrição"):
        servico.distribuir_inscricao_em_turma(
            inscricao=inscricao,
            turma=turma,
            numero_confirmadas=5,
        )


def test_distribuir_inscricao_em_turma_nao_permite_turma_inativa():
    servico = criar_servico()
    etapa = criar_etapa()
    turma = criar_turma(etapa=etapa, ativa=False)
    catequizando = criar_catequizando()
    responsavel = criar_responsavel(vinculos={"cat-1"})

    inscricao = servico.criar_inscricao(
        id_inscricao="insc-1",
        catequizando=catequizando,
        responsavel=responsavel,
        etapa=etapa,
    )

    with pytest.raises(ValueError, match=r"Não é possível distribuir inscrição em turma inativa"):
        servico.distribuir_inscricao_em_turma(
            inscricao=inscricao,
            turma=turma,
            numero_confirmadas=5,
        )


def test_distribuir_inscricao_em_turma_exige_termo_assinado_quando_flag_true():
    servico = criar_servico()
    etapa = criar_etapa()
    turma = criar_turma(etapa=etapa, ativa=True)
    catequizando = criar_catequizando()
    responsavel = criar_responsavel(vinculos={"cat-1"})

    inscricao = servico.criar_inscricao(
        id_inscricao="insc-1",
        catequizando=catequizando,
        responsavel=responsavel,
        etapa=etapa,
    )
    inscricao.termo_assinado = False

    with pytest.raises(ValueError, match=r"inscrição precisa ter termo assinado antes da distribuição"):
        servico.distribuir_inscricao_em_turma(
            inscricao=inscricao,
            turma=turma,
            numero_confirmadas=5,
            exigir_termo_assinado=True,
        )


def test_distribuir_inscricao_em_turma_marca_override_quando_so_idade_da_turma_impede():
    servico = criar_servico()
    etapa = criar_etapa(
        ano_nasc_minimo=2010,
        ano_nasc_maximo=2016,
    )
    turma = criar_turma(
        etapa=etapa,
        ativa=True,
        ano_nasc_minimo=2012,
        ano_nasc_maximo=2016,
    )
    catequizando = criar_catequizando(ano_nascimento=2010)
    responsavel = criar_responsavel(vinculos={"cat-1"})
    usuario = UsuarioFake(id="user-1")

    inscricao = servico.criar_inscricao(
        id_inscricao="insc-1",
        catequizando=catequizando,
        responsavel=responsavel,
        etapa=etapa,
    )

    servico.distribuir_inscricao_em_turma(
        inscricao=inscricao,
        turma=turma,
        numero_confirmadas=5,
        usuario_override=usuario,
        motivo_override="  Exceção aprovada  ",
    )

    assert inscricao.turma == turma
    assert inscricao.possui_override_idade() is True
    assert inscricao.motivo_override == "Exceção aprovada"
    assert inscricao.usuario_override == usuario
    assert inscricao.status.codigo == "CONFIRMADA"


def test_distribuir_inscricao_em_turma_limpa_override_existente_quando_distribuicao_normal():
    servico = criar_servico()
    etapa = criar_etapa(
        ano_nasc_minimo=2010,
        ano_nasc_maximo=2016,
    )
    turma = criar_turma(
        etapa=etapa,
        ativa=True,
        ano_nasc_minimo=2010,
        ano_nasc_maximo=2016,
    )
    catequizando = criar_catequizando(ano_nascimento=2012)
    responsavel = criar_responsavel(vinculos={"cat-1"})

    inscricao = servico.criar_inscricao(
        id_inscricao="insc-1",
        catequizando=catequizando,
        responsavel=responsavel,
        etapa=etapa,
    )
    inscricao.override_idade = True
    inscricao.motivo_override = "Motivo antigo"
    inscricao.usuario_override = UsuarioFake(id="user-antigo")

    servico.distribuir_inscricao_em_turma(
        inscricao=inscricao,
        turma=turma,
        numero_confirmadas=1,
    )

    assert inscricao.possui_override_idade() is False
    assert inscricao.motivo_override is None
    assert inscricao.usuario_override is None
    assert inscricao.turma == turma
    assert inscricao.status.codigo == "CONFIRMADA"


def test_distribuir_inscricao_em_turma_nao_permite_override_sem_usuario():
    servico = criar_servico()
    etapa = criar_etapa(
        ano_nasc_minimo=2010,
        ano_nasc_maximo=2016,
    )
    turma = criar_turma(
        etapa=etapa,
        ativa=True,
        ano_nasc_minimo=2012,
        ano_nasc_maximo=2016,
    )
    catequizando = criar_catequizando(ano_nascimento=2010)
    responsavel = criar_responsavel(vinculos={"cat-1"})

    inscricao = servico.criar_inscricao(
        id_inscricao="insc-1",
        catequizando=catequizando,
        responsavel=responsavel,
        etapa=etapa,
    )

    with pytest.raises(ValueError, match=r"usuário autorizador do override de idade é obrigatório"):
        servico.distribuir_inscricao_em_turma(
            inscricao=inscricao,
            turma=turma,
            numero_confirmadas=5,
            usuario_override=None,
            motivo_override="Exceção aprovada",
        )


def test_distribuir_inscricao_em_turma_nao_permite_override_sem_motivo():
    servico = criar_servico()
    etapa = criar_etapa(
        ano_nasc_minimo=2010,
        ano_nasc_maximo=2016,
    )
    turma = criar_turma(
        etapa=etapa,
        ativa=True,
        ano_nasc_minimo=2012,
        ano_nasc_maximo=2016,
    )
    catequizando = criar_catequizando(ano_nascimento=2010)
    responsavel = criar_responsavel(vinculos={"cat-1"})
    usuario = UsuarioFake(id="user-1")

    inscricao = servico.criar_inscricao(
        id_inscricao="insc-1",
        catequizando=catequizando,
        responsavel=responsavel,
        etapa=etapa,
    )

    with pytest.raises(ValueError, match=r"motivo do override de idade é obrigatório"):
        servico.distribuir_inscricao_em_turma(
            inscricao=inscricao,
            turma=turma,
            numero_confirmadas=5,
            usuario_override=usuario,
            motivo_override=None,
        )


def test_distribuir_inscricao_em_turma_rejeita_quando_incompatibilidade_nao_e_so_etaria():
    servico = criar_servico()
    etapa = criar_etapa(
        ano_nasc_minimo=2010,
        ano_nasc_maximo=2016,
    )
    turma = criar_turma(
        etapa=etapa,
        ativa=True,
        ano_nasc_minimo=2012,
        ano_nasc_maximo=2016,
        bloqueia_mesmo_com_override=True,
    )
    catequizando = criar_catequizando(ano_nascimento=2010)
    responsavel = criar_responsavel(vinculos={"cat-1"})
    usuario = UsuarioFake(id="user-1")

    inscricao = servico.criar_inscricao(
        id_inscricao="insc-1",
        catequizando=catequizando,
        responsavel=responsavel,
        etapa=etapa,
    )

    with pytest.raises(
        ValueError,
        match=r"não pode ser distribuída para a turma informada, mesmo com exceção de idade",
    ):
        servico.distribuir_inscricao_em_turma(
            inscricao=inscricao,
            turma=turma,
            numero_confirmadas=5,
            usuario_override=usuario,
            motivo_override="Exceção aprovada",
        )


def test_distribuir_inscricao_em_turma_nao_permite_numero_confirmadas_negativo():
    servico = criar_servico()
    etapa = criar_etapa()
    turma = criar_turma(etapa=etapa)
    catequizando = criar_catequizando()
    responsavel = criar_responsavel(vinculos={"cat-1"})

    inscricao = servico.criar_inscricao(
        id_inscricao="insc-1",
        catequizando=catequizando,
        responsavel=responsavel,
        etapa=etapa,
    )

    with pytest.raises(ValueError, match=r"número de inscrições confirmadas não pode ser negativo"):
        servico.distribuir_inscricao_em_turma(
            inscricao=inscricao,
            turma=turma,
            numero_confirmadas=-1,
        )


def test_distribuir_inscricao_em_turma_nao_permite_inscricao_nula():
    servico = criar_servico()
    turma = criar_turma()

    with pytest.raises(ValueError, match=r"inscrição a distribuir é obrigatória"):
        servico.distribuir_inscricao_em_turma(
            inscricao=None,
            turma=turma,
            numero_confirmadas=5,
        )


def test_distribuir_inscricao_em_turma_nao_permite_turma_nula():
    servico = criar_servico()
    etapa = criar_etapa()
    catequizando = criar_catequizando()
    responsavel = criar_responsavel(vinculos={"cat-1"})

    inscricao = servico.criar_inscricao(
        id_inscricao="insc-1",
        catequizando=catequizando,
        responsavel=responsavel,
        etapa=etapa,
    )

    with pytest.raises(ValueError, match=r"turma para distribuição é obrigatória"):
        servico.distribuir_inscricao_em_turma(
            inscricao=inscricao,
            turma=None,
            numero_confirmadas=5,
        )