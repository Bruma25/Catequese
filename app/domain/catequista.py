#!/usr/bin/python
# -*- coding: utf-8 -*-

from dataclasses import dataclass
from typing import Optional

from app.domain.usuario import Usuario


@dataclass
class Catequista:
    """
    Representa o catequista.
    - Pode estar ligado a turmas (via relacionamento Turma–Catequista).
    - Pode acumular papel de responsável ou coordenador.
    """
    id: str
    nome: str
    email: Optional[str] = None
    telefone: Optional[str] = None
    usuario: Optional[Usuario] = None

    def __post_init__(self) -> None:
        self.validar()

    def validar(self) -> None:
        if not self.id or not self.id.strip():
            raise ValueError("O id do catequista é obrigatório.")

        if not self.nome or not self.nome.strip():
            raise ValueError("O nome do catequista é obrigatório.")

        self.nome = self.nome.strip()

        if self.email is not None:
            self.email = self.email.strip() or None

        if self.telefone is not None:
            self.telefone = self.telefone.strip() or None

    @property
    def tem_usuario(self) -> bool:
        """Indica se este catequista possui um usuário de login associado."""
        return self.usuario is not None

    def pertence_ao_usuario(self, usuario: Optional[Usuario]) -> bool:
        if usuario is None or self.usuario is None:
            return False
        return self.usuario.id == usuario.id

    def associar_usuario(self, usuario: Usuario) -> None:
        if usuario is None:
            raise ValueError("O usuário informado é obrigatório.")
        self.usuario = usuario

    def remover_usuario(self) -> None:
        self.usuario = None