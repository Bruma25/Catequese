#!/usr/bin/python
# -*- coding: utf-8 -*-
from dataclasses import dataclass
from datetime import date
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from app.domain.catequizando import Catequizando
    from app.domain.sacramento import Sacramento


@dataclass
class HistoricoSacramental:
    """Registra um sacramento recebido pelo catequizando, com data e local."""
    id: str
    catequizando: "Catequizando"
    sacramento: "Sacramento"
    data_recebimento: date
    local: Optional[str] = None
    observacoes: Optional[str] = None

    def __post_init__(self) -> None:
        self.validar()

    def validar(self) -> None:
        if not self.id or not self.id.strip():
            raise ValueError("O id do histórico sacramental é obrigatório.")

        if self.catequizando is None:
            raise ValueError("O catequizando do histórico sacramental é obrigatório.")

        if self.sacramento is None:
            raise ValueError("O sacramento do histórico sacramental é obrigatório.")

        if not isinstance(self.data_recebimento, date):
            raise ValueError("A data de recebimento deve ser um objeto date.")

        if self.data_recebimento > date.today():
            raise ValueError("A data de recebimento do sacramento não pode estar no futuro.")

        if self.data_recebimento < self.catequizando.data_nascimento:
            raise ValueError(
                "A data de recebimento do sacramento não pode ser anterior ao nascimento do catequizando."
            )

        if self.local is not None and not self.local.strip():
            self.local = None

        if self.observacoes is not None and not self.observacoes.strip():
            self.observacoes = None

    def eh_sacramento(self, sacramento: "Sacramento") -> bool:
        """Retorna True se este registro corresponde ao sacramento informado."""
        if sacramento is None:
            return False
        return self.sacramento.id == sacramento.id

    def pertence_ao_catequizando(self, catequizando: "Catequizando") -> bool:
        if catequizando is None:
            return False
        return self.catequizando.id == catequizando.id