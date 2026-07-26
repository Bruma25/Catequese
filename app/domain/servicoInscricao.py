from typing import List, Optional

from app.domain.catequizando import Catequizando
from app.domain.responsavel import Responsavel
from app.domain.etapa import Etapa
from app.domain.inscricao import Inscricao
from app.domain.turma import Turma
from app.domain.statusInscricao import StatusInscricao
from app.domain.usuario import Usuario


class ServicoInscricao:
    def __init__(
        self,
        status_pendente_distribuicao: StatusInscricao,
    ):
        if status_pendente_distribuicao is None:
            raise ValueError("O status pendente de distribuição é obrigatório.")

        self.status_pendente_distribuicao = status_pendente_distribuicao

    def sugerir_etapas_para_catequizando(
        self,
        catequizando: Catequizando,
        etapas: List[Etapa]
    ) -> List[Etapa]:
        """
        Retorna apenas as etapas em que o catequizando pode entrar.
        """
        if catequizando is None:
            raise ValueError("O catequizando para sugestão de etapas é obrigatório.")

        if etapas is None:
            return []

        return [
            etapa for etapa in etapas
            if etapa is not None and etapa.pode_catequizando_entrar(catequizando)
        ]

    def criar_inscricao(
        self,
        id_inscricao: str,
        catequizando: Catequizando,
        responsavel: Responsavel,
        etapa: Etapa,
        referencia_irmao: Optional[str] = None,
        observacao_responsavel: Optional[str] = None,
    ) -> Inscricao:
        """
        Cria uma inscrição em uma etapa, validando:
        - se o responsável pode responder pelo catequizando;
        - se o catequizando atende aos requisitos gerais da etapa.
        """
        if catequizando is None:
            raise ValueError("O catequizando da inscrição é obrigatório.")

        if responsavel is None:
            raise ValueError("O responsável da inscrição é obrigatório.")

        if etapa is None:
            raise ValueError("A etapa da inscrição é obrigatória.")

        if not responsavel.pode_responder_por(catequizando):
            raise ValueError("O responsável informado não possui vínculo com o catequizando.")

        if not etapa.aceita_catequizando(catequizando):
            raise ValueError("O catequizando não atende aos requisitos da etapa.")

        inscricao = Inscricao(
            id=id_inscricao,
            catequizando=catequizando,
            responsavel=responsavel,
            etapa=etapa,
            status=self.status_pendente_distribuicao,
        )

        inscricao.registrar_observacao_responsavel(observacao_responsavel)

        if referencia_irmao is not None:
            inscricao.marcar_preferencia_irmao(referencia_irmao)

        return inscricao

    def distribuir_inscricao_em_turma(
        self,
        inscricao: Inscricao,
        turma: Turma,
        numero_confirmadas: int,
        usuario_override: Optional[Usuario] = None,
        motivo_override: Optional[str] = None,
        exigir_termo_assinado: bool = False,
    ) -> None:
        """
        Distribui a inscrição em uma turma:
        - a etapa continua rígida em idade e sacramentos;
        - a turma continua rígida em suas regras próprias;
        - a única exceção permitida é a faixa etária específica da turma,
          mediante autorização e motivo.
        """
        if inscricao is None:
            raise ValueError("A inscrição a distribuir é obrigatória.")

        if turma is None:
            raise ValueError("A turma para distribuição é obrigatória.")

        if numero_confirmadas < 0:
            raise ValueError("O número de inscrições confirmadas não pode ser negativo.")

        if exigir_termo_assinado and not inscricao.termo_assinado:
            raise ValueError("A inscrição precisa ter termo assinado antes da distribuição.")

        if not turma.pertence_a_etapa(inscricao.etapa):
            raise ValueError("A turma informada não pertence à etapa da inscrição.")

        if not turma.esta_ativa():
            raise ValueError("Não é possível distribuir inscrição em turma inativa.")

        if inscricao.pode_ser_distribuida_para(turma):
            if inscricao.possui_override_idade():
                inscricao.limpar_override_idade()
        else:
            if not inscricao.pode_ser_distribuida_para_com_override_idade(turma):
                raise ValueError(
                    "A inscrição não pode ser distribuída para a turma informada, mesmo com exceção de idade."
                )

            if turma.verifica_idade_especifica(inscricao.catequizando):
                raise ValueError(
                    "A inscrição é compatível com a turma sem necessidade de override de idade."
                )

            inscricao.registrar_override(
                usuario=usuario_override,
                motivo=motivo_override,
            )

        inscricao.atribuir_turma(turma)

        if turma.tem_vaga(numero_confirmadas):
            inscricao.confirmar()
        else:
            inscricao.colocar_em_lista_espera()