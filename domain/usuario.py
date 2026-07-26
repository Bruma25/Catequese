#!/usr/bin/python
# -*- coding: utf-8 -*-

from dataclasses import dataclass, field
from typing import List, Optional

from domain.tipoPapelUsuario import TipoPapelUsuario

@dataclass
class Usuario:
    """
    Representa o usuário logado no sistema (ligado ao auth.users do Supabase).
    Serve de base para saber se ele pode agir como responsável, catequista, coordenador etc.
    """
    id: str
    nome: str
    email: str
    papeis: List[TipoPapelUsuario] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.validar()

    def validar(self) -> None:
        if not self.id or not self.id.strip():
            raise ValueError("O id do usuário é obrigatório.")

        if not self.nome or not self.nome.strip():
            raise ValueError("O nome do usuário é obrigatório.")

        if not self.email or not self.email.strip():
            raise ValueError("O e-mail do usuário é obrigatório.")

        self.id = self.id.strip()
        self.nome = self.nome.strip()
        self.email = self.email.strip().lower()

        if "@" not in self.email:
            raise ValueError("O e-mail do usuário deve ser válido.")

        self._normalizar_papeis()
        self._validar_papeis_sem_duplicidade()

    def _normalizar_papeis(self) -> None:
        papeis_normalizados = []

        for papel in self.papeis:
            if papel is None:
                raise ValueError("A lista de papéis do usuário não pode conter itens nulos.")
            papeis_normalizados.append(papel)

        self.papeis = papeis_normalizados

    def _validar_papeis_sem_duplicidade(self) -> None:
        codigos = set()

        for papel in self.papeis:
            codigo = papel.codigo.strip().lower()
            if codigo in codigos:
                raise ValueError(f"O papel '{papel.codigo}' já foi associado ao usuário.")
            codigos.add(codigo)

    def tem_papel(self, codigo_papel: str) -> bool:
        """Retorna True se o usuário possui um papel com o código informado."""
        if not codigo_papel or not codigo_papel.strip():
            return False

        return any(papel.eh(codigo_papel) for papel in self.papeis)

    def adicionar_papel(self, papel: TipoPapelUsuario) -> None:
        if papel is None:
            raise ValueError("O papel informado é obrigatório.")

        if self.tem_papel(papel.codigo):
            raise ValueError(f"O usuário já possui o papel '{papel.codigo}'.")

        self.papeis.append(papel)

    def remover_papel(self, codigo_papel: str) -> None:
        if not codigo_papel or not codigo_papel.strip():
            raise ValueError("O código do papel é obrigatório.")

        codigo_normalizado = codigo_papel.strip().lower()

        self.papeis = [
            papel
            for papel in self.papeis
            if papel.codigo.strip().lower() != codigo_normalizado
        ]

    def listar_codigos_papeis(self) -> List[str]:
        return [papel.codigo for papel in self.papeis]

    @property
    def quantidade_papeis(self) -> int:
        return len(self.papeis)

    @property
    def possui_papeis(self) -> bool:
        return len(self.papeis) > 0