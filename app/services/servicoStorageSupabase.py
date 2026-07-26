#services/servicoStorageSupabase.py
from pathlib import Path
from typing import Any, BinaryIO, Optional, Union

from app.infra.supabaseClient import get_supabase


class ServicoStorageSupabase:
    def __init__(self, bucket_padrao: str = "inscricao-documentos"):
        self.client = get_supabase()
        self.bucket_padrao = bucket_padrao

    def upload_arquivo(
        self,
        caminho_storage: str,
        arquivo: Union[str, Path, BinaryIO],
        mime_type: Optional[str] = None,
        bucket: Optional[str] = None,
        upsert: bool = False,
        cache_control: str = "3600",
    ) -> Any:
        bucket_final = self._resolver_bucket(bucket)
        arquivo_normalizado = self._normalizar_arquivo_upload(arquivo)
        file_options = self._montar_file_options(
            mime_type=mime_type,
            upsert=upsert,
            cache_control=cache_control,
        )

        return (
            self.client.storage
            .from_(bucket_final)
            .upload(
                path=caminho_storage,
                file=arquivo_normalizado,
                file_options=file_options,
            )
        )

    def gerar_url_assinada(
        self,
        caminho_storage: str,
        expires_in: int = 3600,
        bucket: Optional[str] = None,
    ) -> Any:
        bucket_final = self._resolver_bucket(bucket)

        return (
            self.client.storage
            .from_(bucket_final)
            .create_signed_url(caminho_storage, expires_in)
        )

    def remover_arquivo(
        self,
        caminho_storage: str,
        bucket: Optional[str] = None,
    ) -> Any:
        bucket_final = self._resolver_bucket(bucket)

        return (
            self.client.storage
            .from_(bucket_final)
            .remove([caminho_storage])
        )

    def _resolver_bucket(self, bucket: Optional[str]) -> str:
        return bucket or self.bucket_padrao

    def _montar_file_options(
        self,
        mime_type: Optional[str],
        upsert: bool,
        cache_control: str,
    ) -> dict[str, str]:
        file_options = {
            "cache-control": cache_control,
            "upsert": "true" if upsert else "false",
        }

        if mime_type:
            file_options["content-type"] = mime_type

        return file_options

    @staticmethod
    def _normalizar_arquivo_upload(arquivo: Union[str, Path, BinaryIO]) -> Union[str, BinaryIO]:
        if isinstance(arquivo, Path):
            return str(arquivo)

        if isinstance(arquivo, str):
            return arquivo

        if hasattr(arquivo, "read"):
            return arquivo

        raise TypeError(
            "arquivo deve ser um caminho (str | Path) ou um arquivo binário aberto"
        )