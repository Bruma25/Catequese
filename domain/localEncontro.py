#!/usr/bin/python
# -*- coding: utf-8 -*-
from dataclasses import dataclass


@dataclass(frozen=True)
class LocalEncontro:
    """
    Representa o local onde a turma se reúne.
    Ex.: 'SALA_1', 'SALAO_PAROQUIAL', 'IGREJA'.
    """
    id: int
    codigo: str
    nome_exibicao: str

    def __post_init__(self) -> None:
        if self.id is None:
            raise ValueError("O id do local de encontro é obrigatório.")

        if not isinstance(self.id, int):
            raise ValueError("O id do local de encontro deve ser um inteiro.")

        if self.id <= 0:
            raise ValueError("O id do local de encontro deve ser maior que zero.")

        if not self.codigo or not self.codigo.strip():
            raise ValueError("O código do local de encontro é obrigatório.")

        if not self.nome_exibicao or not self.nome_exibicao.strip():
            raise ValueError("O nome de exibição do local de encontro é obrigatório.")

        object.__setattr__(self, "codigo", self.codigo.strip().upper())
        object.__setattr__(self, "nome_exibicao", self.nome_exibicao.strip())

    def eh(self, codigo: str) -> bool:
        """Retorna True se este local corresponde ao código informado."""
        if not codigo or not codigo.strip():
            return False
        return self.codigo == codigo.strip().upper()