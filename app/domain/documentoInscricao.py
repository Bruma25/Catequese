from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class DocumentoInscricao:
    id: Optional[str]
    inscricao_id: str
    tipo_documento: str
    nome_original: str
    nome_arquivo: str
    caminho_storage: str
    bucket: str = "inscricao-documentos"
    mime_type: Optional[str] = None
    tamanho_bytes: Optional[int] = None
    status_validacao: str = "pendente"
    observacao_validacao: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    TIPOS_DOCUMENTO_VALIDOS = {
        "identidade",
        "comprovante_batismo",
        "comprovante_eucaristia",
        "comprovante_crisma",
        "comprovante_outro_sacramento",
        "outro",
    }

    STATUS_VALIDACAO_PENDENTE = "pendente"
    STATUS_VALIDACAO_APROVADO = "aprovado"
    STATUS_VALIDACAO_REJEITADO = "rejeitado"

    STATUS_VALIDACAO_VALIDOS = {
        STATUS_VALIDACAO_PENDENTE,
        STATUS_VALIDACAO_APROVADO,
        STATUS_VALIDACAO_REJEITADO,
    }

    TIPOS_DOCUMENTO_SACRAMENTAIS = {
        "comprovante_batismo",
        "comprovante_eucaristia",
        "comprovante_crisma",
        "comprovante_outro_sacramento",
    }

    def __post_init__(self) -> None:
        self.normalizar_campos()
        self.validar()

    def normalizar_campos(self) -> None:
        self.id = self._normalizar_texto_opcional(self.id)
        self.inscricao_id = self._normalizar_texto_obrigatorio(
            self.inscricao_id,
            "inscricao_id"
        )
        self.tipo_documento = self._normalizar_texto_obrigatorio(
            self.tipo_documento,
            "tipo_documento"
        ).lower()
        self.nome_original = self._normalizar_texto_obrigatorio(
            self.nome_original,
            "nome_original"
        )
        self.nome_arquivo = self._normalizar_texto_obrigatorio(
            self.nome_arquivo,
            "nome_arquivo"
        )
        self.caminho_storage = self._normalizar_texto_obrigatorio(
            self.caminho_storage,
            "caminho_storage"
        )
        self.bucket = self._normalizar_texto_obrigatorio(
            self.bucket,
            "bucket"
        )
        self.mime_type = self._normalizar_texto_opcional(self.mime_type)
        self.status_validacao = self._normalizar_texto_obrigatorio(
            self.status_validacao,
            "status_validacao"
        ).lower()
        self.observacao_validacao = self._normalizar_texto_opcional(
            self.observacao_validacao
        )

    def validar(self) -> None:
        if self.tipo_documento not in self.TIPOS_DOCUMENTO_VALIDOS:
            raise ValueError(f"Tipo de documento inválido: {self.tipo_documento}.")

        if self.status_validacao not in self.STATUS_VALIDACAO_VALIDOS:
            raise ValueError(f"Status de validação inválido: {self.status_validacao}.")

        if self.tamanho_bytes is not None:
            if not isinstance(self.tamanho_bytes, int):
                raise ValueError("O tamanho do documento em bytes deve ser um inteiro.")
            if self.tamanho_bytes < 0:
                raise ValueError("O tamanho do documento em bytes não pode ser negativo.")

        if self.created_at is not None and not isinstance(self.created_at, datetime):
            raise ValueError("created_at deve ser um datetime válido.")

        if self.updated_at is not None and not isinstance(self.updated_at, datetime):
            raise ValueError("updated_at deve ser um datetime válido.")

        if (
            self.created_at is not None
            and self.updated_at is not None
            and self.updated_at < self.created_at
        ):
            raise ValueError("updated_at não pode ser anterior a created_at.")

        if self.esta_rejeitado() and not self.observacao_validacao:
            raise ValueError("Documento rejeitado deve possuir observação de validação.")

    def aprovar(self, observacao: Optional[str] = None) -> None:
        """
        Aprova o documento e registra observação opcional.
        """
        self._alterar_status_validacao(
            novo_status=self.STATUS_VALIDACAO_APROVADO,
            observacao=self._normalizar_texto_opcional(observacao),
            observacao_obrigatoria=False,
        )

    def rejeitar(self, observacao: str) -> None:
        """
        Rejeita o documento e exige observação.
        """
        self._alterar_status_validacao(
            novo_status=self.STATUS_VALIDACAO_REJEITADO,
            observacao=observacao,
            observacao_obrigatoria=True,
        )

    def marcar_pendente(self, observacao: Optional[str] = None) -> None:
        """
        Retorna o documento para pendência de validação.
        """
        self._alterar_status_validacao(
            novo_status=self.STATUS_VALIDACAO_PENDENTE,
            observacao=self._normalizar_texto_opcional(observacao),
            observacao_obrigatoria=False,
        )

    def esta_pendente(self) -> bool:
        return self.status_validacao == self.STATUS_VALIDACAO_PENDENTE

    def esta_aprovado(self) -> bool:
        return self.status_validacao == self.STATUS_VALIDACAO_APROVADO

    def esta_rejeitado(self) -> bool:
        return self.status_validacao == self.STATUS_VALIDACAO_REJEITADO

    def eh_documento_sacramental(self) -> bool:
        return self.tipo_documento in self.TIPOS_DOCUMENTO_SACRAMENTAIS

    def _alterar_status_validacao(
        self,
        novo_status: str,
        observacao: Optional[str],
        observacao_obrigatoria: bool,
    ) -> None:
        status_normalizado = self._normalizar_texto_obrigatorio(
            novo_status,
            "novo_status"
        ).lower()

        if status_normalizado not in self.STATUS_VALIDACAO_VALIDOS:
            raise ValueError(f"Status de validação inválido: {status_normalizado}.")

        if observacao_obrigatoria:
            texto_observacao = self._normalizar_texto_obrigatorio(
                observacao,
                "observacao"
            )
        else:
            texto_observacao = self._normalizar_texto_opcional(observacao)

        self.status_validacao = status_normalizado
        self.observacao_validacao = texto_observacao
        self._registrar_atualizacao()

        self.validar()

    def _registrar_atualizacao(self) -> None:
        agora = datetime.now()
        self.updated_at = agora

        if self.created_at is None:
            self.created_at = agora

    @staticmethod
    def _normalizar_texto_obrigatorio(valor: str, campo: str) -> str:
        texto = (valor or "").strip()
        if not texto:
            raise ValueError(f"{campo} é obrigatório.")
        return texto

    @staticmethod
    def _normalizar_texto_opcional(valor: Optional[str]) -> Optional[str]:
        if valor is None:
            return None
        texto = valor.strip()
        return texto or None