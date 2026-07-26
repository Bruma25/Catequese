#repositories/documentoInscricaoRepository
from datetime import datetime
from typing import Any, List, Optional
import uuid

from infra.supabaseClient import get_supabase
from domain.documentoInscricao import DocumentoInscricao


class DocumentoInscricaoRepository:
    def __init__(self):
        self.db = get_supabase()
        self.table = "documento_inscricao"

    def salvar(self, documento: DocumentoInscricao) -> DocumentoInscricao:
        if not documento.id:
            documento.id = str(uuid.uuid4())

        payload = self._to_payload(documento, incluir_id=True)

        resposta = (
            self.db.table(self.table)
            .insert(payload)
            .select("*")
            .execute()
        )

        data = self._extrair_primeira_linha(resposta)
        if not data:
            raise ValueError("Não foi possível salvar o documento da inscrição.")

        return self._from_row(data)

    def buscar_por_id(self, documento_id: str) -> Optional[DocumentoInscricao]:
        resposta = (
            self.db.table(self.table)
            .select("*")
            .eq("id", documento_id)
            .maybe_single()
            .execute()
        )

        data = self._extrair_data_optional(resposta)
        if not data:
            return None

        return self._from_row(data)

    def listar_por_inscricao(self, inscricao_id: str) -> List[DocumentoInscricao]:
        resposta = (
            self.db.table(self.table)
            .select("*")
            .eq("inscricao_id", inscricao_id)
            .order("created_at")
            .execute()
        )

        return [self._from_row(row) for row in self._extrair_lista(resposta)]

    def editar(self, documento: DocumentoInscricao) -> DocumentoInscricao:
        if not documento.id:
            raise ValueError("DocumentoInscricao sem id não pode ser editado.")

        payload = self._to_payload(documento, incluir_id=False)

        resposta = (
            self.db.table(self.table)
            .update(payload)
            .eq("id", documento.id)
            .select("*")
            .execute()
        )

        data = self._extrair_primeira_linha(resposta)
        if not data:
            raise ValueError("Não foi possível editar o documento da inscrição.")

        return self._from_row(data)

    def apagar(self, documento_id: str) -> bool:
        resposta = (
            self.db.table(self.table)
            .delete()
            .eq("id", documento_id)
            .select("id")
            .execute()
        )

        return bool(self._extrair_lista(resposta))

    def _to_payload(self, documento: DocumentoInscricao, incluir_id: bool = True) -> dict[str, Any]:
        payload = {
            "inscricao_id": documento.inscricao_id,
            "tipo_documento": documento.tipo_documento,
            "nome_original": documento.nome_original,
            "nome_arquivo": documento.nome_arquivo,
            "caminho_storage": documento.caminho_storage,
            "bucket": documento.bucket,
            "mime_type": documento.mime_type,
            "tamanho_bytes": documento.tamanho_bytes,
            "status_validacao": documento.status_validacao,
            "observacao_validacao": documento.observacao_validacao,
        }

        if incluir_id:
            payload["id"] = documento.id

        return payload

    def _from_row(self, row: dict[str, Any]) -> DocumentoInscricao:
        return DocumentoInscricao(
            id=row.get("id"),
            inscricao_id=row.get("inscricao_id"),
            tipo_documento=row.get("tipo_documento"),
            nome_original=row.get("nome_original"),
            nome_arquivo=row.get("nome_arquivo"),
            caminho_storage=row.get("caminho_storage"),
            bucket=row.get("bucket") or "inscricao-documentos",
            mime_type=row.get("mime_type"),
            tamanho_bytes=row.get("tamanho_bytes"),
            status_validacao=row.get("status_validacao") or "pendente",
            observacao_validacao=row.get("observacao_validacao"),
            created_at=self._parse_datetime(row.get("created_at")),
            updated_at=self._parse_datetime(row.get("updated_at")),
        )

    def _extrair_primeira_linha(self, result) -> Optional[dict[str, Any]]:
        data = self._extrair_lista(result)
        return data[0] if data else None

    def _extrair_lista(self, result) -> List[dict[str, Any]]:
        if result is None or not hasattr(result, "data") or result.data is None:
            return []

        return result.data

    def _extrair_data_optional(self, result) -> Optional[dict[str, Any]]:
        if result is None or not hasattr(result, "data"):
            return None

        return result.data

    def _parse_datetime(self, valor: Any) -> Optional[datetime]:
        if valor is None:
            return None

        if isinstance(valor, datetime):
            return valor

        return datetime.fromisoformat(valor.replace("Z", "+00:00"))