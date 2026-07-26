# repositories/usuario_repository.py
from typing import Optional

from domain.usuario import Usuario
from domain.tipoPapelUsuario import TipoPapelUsuario
from infra.supabaseClient import get_supabase


class UsuarioRepository:
    def __init__(self):
        self.db = get_supabase()
        self.table = "usuario"

    def salvar(self, usuario: Usuario) -> Usuario:
        payload = self._to_payload(usuario, incluir_id=True)

        result = (
            self.db.table(self.table)
            .insert(payload)
            .execute()
        )

        data = result.data[0] if result and result.data else None
        if not data:
            raise ValueError("Não foi possível salvar o usuário.")

        usuario_salvo = self.buscar_por_id(usuario.id)
        if usuario_salvo is None:
            raise ValueError("O usuário foi salvo, mas não pôde ser recarregado.")

        return usuario_salvo

    def editar(self, usuario: Usuario) -> Usuario:
        payload = self._to_payload(usuario, incluir_id=False)

        result = (
            self.db.table(self.table)
            .update(payload)
            .eq("id", usuario.id)
            .execute()
        )

        data = result.data[0] if result and result.data else None
        if not data:
            raise ValueError("Não foi possível editar o usuário.")

        usuario_editado = self.buscar_por_id(usuario.id)
        if usuario_editado is None:
            raise ValueError("O usuário foi editado, mas não pôde ser recarregado.")

        return usuario_editado

    def apagar(self, usuario_id: str) -> bool:
        result = (
            self.db.table(self.table)
            .delete()
            .eq("id", usuario_id)
            .execute()
        )

        return bool(result.data)

    def buscar_por_id(self, usuario_id: str) -> Optional[Usuario]:
        result = (
            self.db.table(self.table)
            .select("""
                id,
                nome,
                email,
                usuario_papel(
                    papel_id,
                    tipo_papel_usuario(
                        id,
                        codigo,
                        descricao
                    )
                )
            """)
            .eq("id", usuario_id)
            .maybe_single()
            .execute()
        )

        data = self._extrair_data_optional(result)
        if not data:
            return None

        return self._montar_usuario(data)

    def buscar_por_email(self, email: str) -> Optional[Usuario]:
        result = (
            self.db.table(self.table)
            .select("""
                id,
                nome,
                email,
                usuario_papel(
                    papel_id,
                    tipo_papel_usuario(
                        id,
                        codigo,
                        descricao
                    )
                )
            """)
            .eq("email", email)
            .maybe_single()
            .execute()
        )

        data = self._extrair_data_optional(result)
        if not data:
            return None

        return self._montar_usuario(data)

    def definir_papeis(self, usuario: Usuario) -> Usuario:
        (
            self.db.table("usuario_papel")
            .delete()
            .eq("usuario_id", usuario.id)
            .execute()
        )

        if usuario.papeis:
            payload = [
                {
                    "usuario_id": usuario.id,
                    "papel_id": papel.id,
                }
                for papel in usuario.papeis
            ]

            (
                self.db.table("usuario_papel")
                .insert(payload)
                .execute()
            )

        usuario_atualizado = self.buscar_por_id(usuario.id)
        if usuario_atualizado is None:
            raise ValueError("Os papéis foram definidos, mas o usuário não pôde ser recarregado.")

        return usuario_atualizado

    def salvar_com_papeis(self, usuario: Usuario) -> Usuario:
        self.salvar(usuario)
        return self.definir_papeis(usuario)

    def editar_com_papeis(self, usuario: Usuario) -> Usuario:
        self.editar(usuario)
        return self.definir_papeis(usuario)

    def _to_payload(self, usuario: Usuario, incluir_id: bool = True) -> dict:
        payload = {
            "nome": usuario.nome,
            "email": usuario.email,
        }

        if incluir_id:
            payload["id"] = usuario.id

        return payload

    def _montar_usuario(self, data: dict) -> Usuario:
        papeis = self._mapear_papeis(data.get("usuario_papel", []))

        return Usuario(
            id=data["id"],
            nome=data.get("nome"),
            email=data.get("email"),
            papeis=papeis,
        )

    def _mapear_papeis(self, usuario_papel_data):
        papeis = []

        for item in usuario_papel_data:
            papel_data = item.get("tipo_papel_usuario")
            if papel_data is None:
                continue

            papeis.append(
                TipoPapelUsuario(
                    id=papel_data["id"],
                    codigo=papel_data["codigo"],
                    descricao=papel_data["descricao"],
                )
            )

        return papeis

    def _extrair_data_optional(self, result):
        if result is None:
            return None

        if not hasattr(result, "data"):
            return None

        return result.data