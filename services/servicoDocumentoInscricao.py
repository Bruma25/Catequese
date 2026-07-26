# services/servicoDocumentoInscricao.py
import mimetypes
import uuid
from pathlib import Path
from typing import Any, Optional

from domain.documentoInscricao import DocumentoInscricao
from repositories.documentoInscricaoRepository import DocumentoInscricaoRepository
from services.servicoStorageSupabase import ServicoStorageSupabase


class ServicoDocumentoInscricao:
    def __init__(
        self,
        documento_repository: Optional[DocumentoInscricaoRepository] = None,
        storage_service: Optional[ServicoStorageSupabase] = None,
    ):
        self.documento_repository = documento_repository or DocumentoInscricaoRepository()
        self.storage_service = storage_service or ServicoStorageSupabase()

    def enviar_documento(
        self,
        inscricao_id: str,
        tipo_documento: str,
        caminho_arquivo_local: str,
        nome_original: Optional[str] = None,
        bucket: Optional[str] = None,
    ) -> DocumentoInscricao:
        caminho_local = self._resolver_caminho_local(caminho_arquivo_local)
        nome_original_final = self._resolver_nome_original(caminho_local, nome_original)
        mime_type = mimetypes.guess_type(nome_original_final)[0]
        tamanho_bytes = caminho_local.stat().st_size
        nome_arquivo = self._gerar_nome_arquivo(caminho_local)
        caminho_storage = self._montar_caminho_storage(inscricao_id, nome_arquivo)
        bucket_final = self._resolver_bucket(bucket)

        documento = self._criar_documento_pendente(
            inscricao_id=inscricao_id,
            tipo_documento=tipo_documento,
            nome_original=nome_original_final,
            nome_arquivo=nome_arquivo,
            caminho_storage=caminho_storage,
            bucket=bucket_final,
            mime_type=mime_type,
            tamanho_bytes=tamanho_bytes,
        )

        upload_realizado = False

        try:
            self.storage_service.upload_arquivo(
                caminho_storage=caminho_storage,
                arquivo=str(caminho_local),
                mime_type=mime_type,
                bucket=bucket_final,
                upsert=False,
            )
            upload_realizado = True

            return self.documento_repository.salvar(documento)

        except Exception:
            if upload_realizado:
                self._tentar_remover_arquivo_enviado(
                    caminho_storage=caminho_storage,
                    bucket=bucket_final,
                )
            raise

    def gerar_url_download(self, documento_id: str, expires_in: int = 3600) -> str:
        documento = self._buscar_documento_obrigatorio(documento_id)

        resposta = self.storage_service.gerar_url_assinada(
            caminho_storage=documento.caminho_storage,
            expires_in=expires_in,
            bucket=documento.bucket,
        )

        url = self._extrair_signed_url(resposta)
        if not url:
            raise ValueError("Não foi possível gerar a URL assinada do documento.")

        return url

    def apagar_documento(self, documento_id: str) -> bool:
        documento = self.documento_repository.buscar_por_id(documento_id)
        if not documento:
            return False

        self.storage_service.remover_arquivo(
            caminho_storage=documento.caminho_storage,
            bucket=documento.bucket,
        )

        return self.documento_repository.apagar(documento_id)

    def _resolver_caminho_local(self, caminho_arquivo_local: str) -> Path:
        caminho_local = Path((caminho_arquivo_local or "").strip())

        if not str(caminho_local):
            raise ValueError("O caminho do arquivo local é obrigatório.")

        if not caminho_local.exists():
            raise ValueError("Arquivo local não encontrado.")

        if not caminho_local.is_file():
            raise ValueError("O caminho informado não corresponde a um arquivo.")

        return caminho_local

    def _resolver_nome_original(self, caminho_local: Path, nome_original: Optional[str]) -> str:
        nome_resolvido = (nome_original or caminho_local.name).strip()
        if not nome_resolvido:
            raise ValueError("O nome original do arquivo é obrigatório.")
        return nome_resolvido

    def _resolver_bucket(self, bucket: Optional[str]) -> str:
        return (bucket or self.storage_service.bucket_padrao).strip()

    def _buscar_documento_obrigatorio(self, documento_id: str) -> DocumentoInscricao:
        documento = self.documento_repository.buscar_por_id(documento_id)
        if not documento:
            raise ValueError("Documento não encontrado.")
        return documento

    def _gerar_nome_arquivo(self, caminho_local: Path) -> str:
        extensao = caminho_local.suffix.lower()
        return f"{uuid.uuid4()}{extensao}"

    def _montar_caminho_storage(self, inscricao_id: str, nome_arquivo: str) -> str:
        inscricao_id_normalizado = (inscricao_id or "").strip()
        if not inscricao_id_normalizado:
            raise ValueError("inscricao_id é obrigatório.")

        nome_arquivo_normalizado = (nome_arquivo or "").strip()
        if not nome_arquivo_normalizado:
            raise ValueError("nome_arquivo é obrigatório.")

        return f"inscricoes/{inscricao_id_normalizado}/{nome_arquivo_normalizado}"

    def _criar_documento_pendente(
        self,
        inscricao_id: str,
        tipo_documento: str,
        nome_original: str,
        nome_arquivo: str,
        caminho_storage: str,
        bucket: str,
        mime_type: Optional[str],
        tamanho_bytes: int,
    ) -> DocumentoInscricao:
        documento = DocumentoInscricao(
            id=None,
            inscricao_id=inscricao_id,
            tipo_documento=tipo_documento,
            nome_original=nome_original,
            nome_arquivo=nome_arquivo,
            caminho_storage=caminho_storage,
            bucket=bucket,
            mime_type=mime_type,
            tamanho_bytes=tamanho_bytes,
        )

        documento.marcar_pendente()
        return documento

    def _tentar_remover_arquivo_enviado(
        self,
        caminho_storage: str,
        bucket: str,
    ) -> None:
        try:
            self.storage_service.remover_arquivo(
                caminho_storage=caminho_storage,
                bucket=bucket,
            )
        except Exception:
            pass

    def _extrair_signed_url(self, resposta: Any) -> Optional[str]:
        if resposta is None:
            return None

        if isinstance(resposta, str):
            return resposta

        if isinstance(resposta, dict):
            return (
                resposta.get("signedURL")
                or resposta.get("signedUrl")
                or resposta.get("signed_url")
            )

        if hasattr(resposta, "get"):
            return (
                resposta.get("signedURL")
                or resposta.get("signedUrl")
                or resposta.get("signed_url")
            )

        if hasattr(resposta, "data") and isinstance(resposta.data, dict):
            return (
                resposta.data.get("signedURL")
                or resposta.data.get("signedUrl")
                or resposta.data.get("signed_url")
            )

        return None