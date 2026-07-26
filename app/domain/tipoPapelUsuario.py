#!/usr/bin/python
# -*- coding: utf-8 -*-

from dataclasses import dataclass

@dataclass(frozen=True)
class TipoPapelUsuario:
    """
    Representa um tipo de papel que um usuário pode exercer.
    Ex.: 'COORDENADOR_GERAL', 'CATEQUISTA', 'RESPONSAVEL'.
    """
    id: int
    codigo: str
    descricao: str

    def __post_init__(self) -> None:
        if self.id is None:
            raise ValueError("O id do tipo de papel do usuário é obrigatório.")

        if not isinstance(self.id, int):
            raise ValueError("O id do tipo de papel do usuário deve ser um inteiro.")

        if self.id <= 0:
            raise ValueError("O id do tipo de papel do usuário deve ser maior que zero.")

        if not self.codigo or not self.codigo.strip():
            raise ValueError("O código do tipo de papel do usuário é obrigatório.")

        if not self.descricao or not self.descricao.strip():
            raise ValueError("A descrição do tipo de papel do usuário é obrigatória.")

        object.__setattr__(self, "codigo", self.codigo.strip().upper())
        object.__setattr__(self, "descricao", self.descricao.strip())

    def eh(self, codigo: str) -> bool:
        """Retorna True se o tipo de papel corresponde ao código informado."""
        if not codigo or not codigo.strip():
            return False
        return self.codigo == codigo.strip().upper()