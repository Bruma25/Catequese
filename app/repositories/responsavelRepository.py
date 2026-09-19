# repositories/responsavelRepository.py
from typing import Optional

from app.infra.supabaseClient import get_supabase
from app.domain.responsavel import Responsavel
from app.domain.usuario import Usuario


class ResponsavelRepository:
    def __init__(self):
        self.db = get_supabase()
        self.table = "responsavel"

    def buscar_por_id(self, responsavel_id: str) -> Optional[Responsavel]:
        result = (
            self.db.table(self.table)
            .select("*")
            .eq("id", responsavel_id)
            .maybe_single()
            .execute()
        )

        data = result.data if result else None
        if not data:
            return None

        return self._from_row(data)

    # ✅ NOVO MÉTODO ADICIONADO
    def buscar_por_usuario_id(self, usuario_id: str) -> Optional[Responsavel]:
        """
        Busca responsável vinculado a um usuário específico.
        """
        result = (
            self.db.table(self.table)
            .select("""
                id,
                usuario_id,
                nome,
                email,
                telefone
            """)
            .eq("usuario_id", usuario_id)
            .maybe_single()
            .execute()
        )

        data = result.data if result else None
        if not data:
            return None

        return self._from_row(data)

    def salvar(self, responsavel: Responsavel) -> Responsavel:
        payload = self._to_payload(responsavel, incluir_id=True)

        result = (
            self.db.table(self.table)
            .insert(payload)
            .execute()
        )

        data = result.data[0] if result and result.data else None
        if not data:
            raise ValueError("Não foi possível salvar o responsável.")

        return self._from_row(data)

    def editar(self, responsavel: Responsavel) -> Responsavel:
        payload = self._to_payload(responsavel, incluir_id=False)

        result = (
            self.db.table(self.table)
            .update(payload)
            .eq("id", responsavel.id)
            .execute()
        )

        data = result.data[0] if result and result.data else None
        if not data:
            raise ValueError("Não foi possível editar o responsável.")

        return self._from_row(data)

    def apagar(self, responsavel_id: str) -> bool:
        result = (
            self.db.table(self.table)
            .delete()
            .eq("id", responsavel_id)
            .execute()
        )

        return bool(result.data)

    def _to_payload(self, responsavel: Responsavel, incluir_id: bool = True) -> dict:
        payload = {
            "usuario_id": responsavel.usuario.id if responsavel.usuario else None,
            "nome": responsavel.nome,
            "email": responsavel.email,
            "telefone": responsavel.telefone,
        }

        if incluir_id:
            payload["id"] = responsavel.id

        return payload

    def _from_row(self, data: dict) -> Responsavel:
        # ✅ Criar usuário se tiver usuario_id
        usuario = None
        if data.get("usuario_id"):
            usuario = Usuario(
                id=data["usuario_id"],
                nome=data.get("nome", ""),
                email=data.get("email", "")
            )

        return Responsavel(
            id=data["id"],
            nome=data["nome"],
            email=data.get("email"),
            telefone=data.get("telefone"),
            usuario=usuario,
            vinculos=[],
        )