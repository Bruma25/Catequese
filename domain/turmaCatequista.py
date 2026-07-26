#!/usr/bin/python
# -*- coding: utf-8 -*-

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from domain.turma import Turma
    from domain.catequista import Catequista


@dataclass
class TurmaCatequista:
    """
    Representa a associação entre uma turma e um catequista.
    Cada instância indica que um catequista atua em uma turma específica.
    """
    turma: "Turma"
    catequista: "Catequista"

    def __post_init__(self) -> None:
        self.validar()

    def validar(self) -> None:
        if self.turma is None:
            raise ValueError("A turma do vínculo com catequista é obrigatória.")

        if self.catequista is None:
            raise ValueError("O catequista do vínculo com turma é obrigatório.")

    def pertence_a_turma(self, turma: "Turma") -> bool:
        if turma is None:
            return False
        return self.turma.id == turma.id

    def pertence_ao_catequista(self, catequista: "Catequista") -> bool:
        if catequista is None:
            return False
        return self.catequista.id == catequista.id