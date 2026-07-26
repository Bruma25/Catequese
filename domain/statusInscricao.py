#!/usr/bin/python
# -*- coding: utf-8 -*-
from dataclasses import dataclass


@dataclass(frozen=True)
class StatusInscricao:
    """
    Representa o estado atual da inscrição.
    Ex.: 'PENDENTE_DISTRIBUICAO', 'CONFIRMADA', 'LISTA_ESPERA', 'CANCELADA'.
    """
    id: int
    codigo: str
    descricao: str

    def __post_init__(self) -> None:
        if self.id is None:
            raise ValueError("O id do status da inscrição é obrigatório.")

        if not isinstance(self.id, int):
            raise ValueError("O id do status da inscrição deve ser um inteiro.")

        if self.id <= 0:
            raise ValueError("O id do status da inscrição deve ser maior que zero.")

        if not self.codigo or not self.codigo.strip():
            raise ValueError("O código do status da inscrição é obrigatório.")

        if not self.descricao or not self.descricao.strip():
            raise ValueError("A descrição do status da inscrição é obrigatória.")

        object.__setattr__(self, "codigo", self.codigo.strip().upper())
        object.__setattr__(self, "descricao", self.descricao.strip())

    def eh(self, codigo: str) -> bool:
        """Retorna True se o status corresponde ao código informado."""
        if not codigo or not codigo.strip():
            return False
        return self.codigo == codigo.strip().upper()