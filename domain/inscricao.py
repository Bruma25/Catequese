from dataclasses import dataclass
from datetime import datetime
from typing import Optional, TYPE_CHECKING

from domain.statusInscricao import StatusInscricao

if TYPE_CHECKING:
    from domain.catequizando import Catequizando
    from domain.responsavel import Responsavel
    from domain.etapa import Etapa
    from domain.turma import Turma
    from domain.usuario import Usuario


@dataclass
class Inscricao:
    """
    Representa a inscrição em uma etapa (e, posteriormente, em turma).
    Guarda status, preferências, exceções e consentimento (termo).
    """
    id: str
    catequizando: "Catequizando"
    responsavel: "Responsavel"
    etapa: "Etapa"
    status: StatusInscricao
    data_inscricao: Optional[datetime] = None

    turma: Optional["Turma"] = None
    termo_assinado: bool = False

    quer_mesma_turma_que_irmao: bool = False
    referencia_irmao: Optional[str] = None
    observacao_responsavel: Optional[str] = None

    override_idade: bool = False
    motivo_override: Optional[str] = None
    usuario_override: Optional["Usuario"] = None

    STATUS_PENDENTE_DISTRIBUICAO = "PENDENTE_DISTRIBUICAO"
    STATUS_CONFIRMADA = "CONFIRMADA"
    STATUS_LISTA_ESPERA = "LISTA_ESPERA"
    STATUS_CANCELADA = "CANCELADA"

    STATUS_DESCRICOES = {
        STATUS_PENDENTE_DISTRIBUICAO: "Pendente de distribuição em turma",
        STATUS_CONFIRMADA: "Inscrição confirmada",
        STATUS_LISTA_ESPERA: "Aguardando vaga",
        STATUS_CANCELADA: "Inscrição cancelada",
    }

    STATUS_VALIDOS = set(STATUS_DESCRICOES.keys())

    def __post_init__(self) -> None:
        self.normalizar_campos()
        self.validar()

    def normalizar_campos(self) -> None:
        self.id = self._normalizar_texto_obrigatorio(self.id, "id")
        self.referencia_irmao = self._normalizar_texto_opcional(self.referencia_irmao)
        self.observacao_responsavel = self._normalizar_texto_opcional(self.observacao_responsavel)
        self.motivo_override = self._normalizar_texto_opcional(self.motivo_override)

    def validar(self) -> None:
        if self.catequizando is None:
            raise ValueError("O catequizando da inscrição é obrigatório.")

        if self.responsavel is None:
            raise ValueError("O responsável da inscrição é obrigatório.")

        if self.etapa is None:
            raise ValueError("A etapa da inscrição é obrigatória.")

        if self.status is None:
            raise ValueError("O status da inscrição é obrigatório.")

        if not isinstance(self.status, StatusInscricao):
            raise ValueError("O status da inscrição deve ser um StatusInscricao válido.")

        if self.codigo_status() not in self.STATUS_VALIDOS:
            raise ValueError(f"Status da inscrição inválido: {self.codigo_status()}.")

        if self.quer_mesma_turma_que_irmao:
            if not self.referencia_irmao:
                raise ValueError(
                    "A referência do irmão é obrigatória quando houver preferência de mesma turma."
                )
        else:
            self.referencia_irmao = None

        if self.override_idade:
            if not self.motivo_override:
                raise ValueError("O motivo do override de idade é obrigatório.")

            if self.usuario_override is None:
                raise ValueError("O usuário autorizador do override de idade é obrigatório.")
        else:
            self.motivo_override = None
            self.usuario_override = None

        if self.turma is not None and self.turma.etapa.id != self.etapa.id:
            raise ValueError("A turma da inscrição deve pertencer à mesma etapa da inscrição.")

    def codigo_status(self) -> str:
        return self.status.codigo

    def _novo_status(self, codigo: str) -> StatusInscricao:
        codigo_normalizado = self._normalizar_texto_obrigatorio(codigo, "codigo_status").upper()

        if codigo_normalizado not in self.STATUS_VALIDOS:
            raise ValueError(f"Status da inscrição inválido: {codigo_normalizado}.")

        id_atual = getattr(self.status, "id", None)
        if not isinstance(id_atual, int) or id_atual <= 0:
            id_atual = 1

        return StatusInscricao(
            id=id_atual,
            codigo=codigo_normalizado,
            descricao=self.STATUS_DESCRICOES[codigo_normalizado],
        )

    def assinar_termo(self) -> None:
        """
        Marca o termo como assinado.
        Pode registrar a data de inscrição se ainda não estiver definida.
        """
        self.termo_assinado = True

        if self.data_inscricao is None:
            self.data_inscricao = datetime.now()

    def definir_status(self, status: StatusInscricao) -> None:
        """
        Atualiza o status da inscrição.
        Mantido por compatibilidade; prefira os métodos explícitos de transição.
        """
        if status is None:
            raise ValueError("O novo status da inscrição é obrigatório.")

        if not isinstance(status, StatusInscricao):
            raise ValueError("O novo status da inscrição deve ser um StatusInscricao válido.")

        if status.codigo not in self.STATUS_VALIDOS:
            raise ValueError(f"Status da inscrição inválido: {status.codigo}.")

        self.status = status

    def confirmar(self) -> None:
        self.status = self._novo_status(self.STATUS_CONFIRMADA)

    def colocar_em_lista_espera(self) -> None:
        self.status = self._novo_status(self.STATUS_LISTA_ESPERA)

    def marcar_pendente_distribuicao(self) -> None:
        self.status = self._novo_status(self.STATUS_PENDENTE_DISTRIBUICAO)

    def atribuir_turma(self, turma: "Turma") -> None:
        """
        Define a turma da inscrição.
        Deve ser usado pelo coordenador ou serviço de distribuição.
        """
        if turma is None:
            raise ValueError("A turma informada para a inscrição é obrigatória.")

        if turma.etapa.id != self.etapa.id:
            raise ValueError("A turma da inscrição deve pertencer à mesma etapa da inscrição.")

        self.turma = turma

    def remover_turma(self) -> None:
        """Remove a turma atualmente atribuída à inscrição."""
        self.turma = None

    def pode_ser_distribuida_para(self, turma: "Turma") -> bool:
        """
        Verifica se a inscrição é compatível com a turma.
        Não decide vaga; encapsula apenas parte da regra de distribuição.
        """
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

    def pode_ser_distribuida_para_com_override_idade(self, turma: "Turma") -> bool:
        """
        Verifica se a inscrição pode ser distribuída para a turma
        admitindo exceção apenas na faixa etária específica da turma.
        Requisitos da etapa continuam rígidos.
        """
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

    def registrar_override(self, usuario: "Usuario", motivo: str) -> None:
        texto_motivo = self._normalizar_texto_opcional(motivo)

        if not texto_motivo:
            raise ValueError("O motivo do override de idade é obrigatório.")

        if usuario is None:
            raise ValueError("O usuário autorizador do override de idade é obrigatório.")

        self.override_idade = True
        self.motivo_override = texto_motivo
        self.usuario_override = usuario

    def marcar_override_idade(self, motivo: str, usuario: "Usuario") -> None:
        self.registrar_override(usuario=usuario, motivo=motivo)

    def limpar_override_idade(self) -> None:
        """Remove as informações de override de idade."""
        self.override_idade = False
        self.motivo_override = None
        self.usuario_override = None

    def marcar_preferencia_irmao(self, referencia: str) -> None:
        texto_referencia = self._normalizar_texto_opcional(referencia)

        if not texto_referencia:
            raise ValueError("A referência do irmão é obrigatória.")

        self.quer_mesma_turma_que_irmao = True
        self.referencia_irmao = texto_referencia

    def limpar_preferencia_irmao(self) -> None:
        """Remove a preferência de mesma turma com irmão."""
        self.quer_mesma_turma_que_irmao = False
        self.referencia_irmao = None

    def registrar_observacao_responsavel(self, observacao: Optional[str]) -> None:
        self.observacao_responsavel = self._normalizar_texto_opcional(observacao)

    def pertence_ao_catequizando(self, catequizando: "Catequizando") -> bool:
        if catequizando is None:
            return False
        return self.catequizando.id == catequizando.id

    def pertence_ao_responsavel(self, responsavel: "Responsavel") -> bool:
        if responsavel is None:
            return False
        return self.responsavel.id == responsavel.id

    def pertence_a_etapa(self, etapa: "Etapa") -> bool:
        if etapa is None:
            return False
        return self.etapa.id == etapa.id

    def possui_turma(self) -> bool:
        return self.turma is not None

    def possui_override_idade(self) -> bool:
        return self.override_idade

    @staticmethod
    def _normalizar_texto_obrigatorio(valor: str, campo: str) -> str:
        texto = (valor or "").strip()
        if not texto:
            if campo == "id":
                raise ValueError("O id da inscrição é obrigatório.")
            raise ValueError(f"O campo {campo} da inscrição é obrigatório.")
        return texto

    @staticmethod
    def _normalizar_texto_opcional(valor: Optional[str]) -> Optional[str]:
        if valor is None:
            return None
        texto = valor.strip()
        return texto or None