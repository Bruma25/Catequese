#!/usr/bin/python
# -*- coding: utf-8 -*-
from dataclasses import dataclass
from typing import Optional, TYPE_CHECKING

from app.domain.usuario import Usuario

if TYPE_CHECKING:
    from app.domain.etapa import Etapa


@dataclass
class CoordenadorEtapa:
    """
    Coordena uma etapa específica (ex.: Eucaristia).
    No futuro, acompanhará turmas da etapa e presenças.
    """
    id: str
    nome: str
    usuario: Optional[Usuario] = None
    email: Optional[str] = None
    telefone: Optional[str] = None
    etapa: Optional["Etapa"] = None

    def __post_init__(self) -> None:
        self.validar()

    def validar(self) -> None:
        if not self.id or not self.id.strip():
            raise ValueError("O id do coordenador de etapa é obrigatório.")

        if not self.nome or not self.nome.strip():
            raise ValueError("O nome do coordenador de etapa é obrigatório.")

        self.id = self.id.strip()
        self.nome = self.nome.strip()

        if self.email is not None:
            self.email = self.email.strip() or None

        if self.telefone is not None:
            self.telefone = self.telefone.strip() or None

    @property
    def tem_usuario(self) -> bool:
        """Indica se o coordenador possui um usuário de login associado."""
        return self.usuario is not None

    def pertence_ao_usuario(self, usuario: Optional[Usuario]) -> bool:
        """Retorna True se este coordenador estiver associado ao usuário informado."""
        if usuario is None or self.usuario is None:
            return False
        return self.usuario.id == usuario.id

    def esta_vinculado_a_etapa(self) -> bool:
        """Retorna True se o coordenador já estiver associado a uma etapa."""
        return self.etapa is not None