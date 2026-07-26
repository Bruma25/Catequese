#!/usr/bin/python
# -*- coding: utf-8 -*-

from dataclasses import dataclass
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from domain.catequizando import Catequizando
    from domain.responsavel import Responsavel
    from domain.tipoVinculoResponsavel import TipoVinculoResponsavel


@dataclass
class CatequizandoResponsavel:
    """
    Representa a relação entre catequizando e responsável.
    Ex.: pai, mãe, avó, tutor, outro, ou o próprio catequizando adulto.
    """
    catequizando: "Catequizando"
    responsavel: "Responsavel"
    tipo_vinculo: "TipoVinculoResponsavel"
    descricao_outro: Optional[str] = None

    def __post_init__(self) -> None:
        self.validar()

    def exige_descricao_outro(self) -> bool:
        """Retorna True quando o vínculo exige detalhamento textual."""
        return self.tipo_vinculo is not None and self.tipo_vinculo.eh("OUTRO")

    def validar(self) -> None:
        """
        Valida a consistência mínima do vínculo.
        - Catequizando, responsável e tipo de vínculo são obrigatórios.
        - Se tipo for OUTRO, exige descricao_outro.
        - Caso contrário, limpa descricao_outro por consistência.
        """
        if self.catequizando is None:
            raise ValueError("O catequizando do vínculo é obrigatório.")

        if self.responsavel is None:
            raise ValueError("O responsável do vínculo é obrigatório.")

        if self.tipo_vinculo is None:
            raise ValueError("O tipo de vínculo do responsável é obrigatório.")

        if self.descricao_outro is not None:
            self.descricao_outro = self.descricao_outro.strip() or None

        if self.exige_descricao_outro():
            if not self.descricao_outro:
                raise ValueError("descricao_outro é obrigatória quando o vínculo for OUTRO.")
        else:
            self.descricao_outro = None

    def eh_auto_responsavel(self) -> bool:
        """Retorna True quando o responsável é o próprio catequizando."""
        return self.tipo_vinculo is not None and self.tipo_vinculo.eh("PROPRIO")

    def pertence_ao_catequizando(self, catequizando: "Catequizando") -> bool:
        if catequizando is None:
            return False
        return self.catequizando.id == catequizando.id

    def pertence_ao_responsavel(self, responsavel: "Responsavel") -> bool:
        if responsavel is None:
            return False
        return self.responsavel.id == responsavel.id