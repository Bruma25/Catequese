#!/usr/bin/python
# -*- coding: utf-8 -*-
from dataclasses import dataclass, field
from datetime import date
from typing import List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from domain.sacramento import Sacramento
    from domain.responsavel import Responsavel
    from domain.historicoSacramental import HistoricoSacramental
    from domain.catequizandoResponsavel import CatequizandoResponsavel


@dataclass
class Catequizando:
    """
    Representa o catequizando.
    Centraliza dados pessoais, vínculos com responsáveis e sacramentos recebidos.
    """
    id: str
    nome: str
    data_nascimento: date
    endereco: Optional[str] = None
    telefone: Optional[str] = None
    email: Optional[str] = None
    observacoes: Optional[str] = None
    necessidade_especial: bool = False
    descricao_necessidade_especial: Optional[str] = None
    vinculos_responsaveis: List["CatequizandoResponsavel"] = field(default_factory=list)
    historico_sacramental: List["HistoricoSacramental"] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.validar()

    def validar(self) -> None:
        if not self.id or not self.id.strip():
            raise ValueError("O id do catequizando é obrigatório.")

        if not self.nome or not self.nome.strip():
            raise ValueError("O nome do catequizando é obrigatório.")

        if not isinstance(self.data_nascimento, date):
            raise ValueError("A data de nascimento deve ser um objeto date.")

        if self.data_nascimento > date.today():
            raise ValueError("A data de nascimento não pode estar no futuro.")

        if not self.necessidade_especial:
            self.descricao_necessidade_especial = None

        elif not self.descricao_necessidade_especial or not self.descricao_necessidade_especial.strip():
            raise ValueError(
                "A descrição da necessidade especial é obrigatória quando necessidade_especial=True."
            )

    @property
    def ano_nascimento(self) -> int:
        return self.data_nascimento.year

    def idade_em(self, data_referencia: date) -> int:
        if not isinstance(data_referencia, date):
            raise ValueError("A data de referência deve ser um objeto date.")

        if data_referencia < self.data_nascimento:
            raise ValueError("A data de referência não pode ser anterior ao nascimento.")

        idade = data_referencia.year - self.data_nascimento.year
        if (data_referencia.month, data_referencia.day) < (self.data_nascimento.month, self.data_nascimento.day):
            idade -= 1
        return idade

    def idade_atual(self, hoje: Optional[date] = None) -> int:
        return self.idade_em(hoje or date.today())

    def possui_sacramento(self, sacramento: "Sacramento") -> bool:
        if sacramento is None:
            return False

        return any(item.eh_sacramento(sacramento) for item in self.historico_sacramental)

    def listar_sacramentos(self) -> List["Sacramento"]:
        sacramentos: List["Sacramento"] = []
        ids_adicionados = set()

        for item in self.historico_sacramental:
            sacramento = item.sacramento
            if sacramento.id in ids_adicionados:
                continue
            ids_adicionados.add(sacramento.id)
            sacramentos.append(sacramento)

        return sacramentos

    def tem_necessidade_especial(self) -> bool:
        return self.necessidade_especial

    def listar_responsaveis(self) -> List["Responsavel"]:
        responsaveis: List["Responsavel"] = []
        ids_adicionados = set()

        for vinculo in self.vinculos_responsaveis:
            responsavel = vinculo.responsavel
            if responsavel.id in ids_adicionados:
                continue
            ids_adicionados.add(responsavel.id)
            responsaveis.append(responsavel)

        return responsaveis

    def possui_responsavel(self, responsavel: Optional["Responsavel"] = None) -> bool:
        if responsavel is None:
            return len(self.vinculos_responsaveis) > 0

        return any(v.responsavel.id == responsavel.id for v in self.vinculos_responsaveis)

    def adicionar_vinculo_responsavel(self, vinculo: "CatequizandoResponsavel") -> None:
        if vinculo is None:
            raise ValueError("O vínculo informado é obrigatório.")

        if vinculo.catequizando is None or vinculo.catequizando.id != self.id:
            raise ValueError("O vínculo informado não pertence a este catequizando.")

        if self.possui_responsavel(vinculo.responsavel):
            raise ValueError("O responsável informado já está vinculado a este catequizando.")

        self.vinculos_responsaveis.append(vinculo)

    def adicionar_historico_sacramental(self, historico: "HistoricoSacramental") -> None:
        if historico is None:
            raise ValueError("O histórico informado é obrigatório.")

        if historico.catequizando is None or historico.catequizando.id != self.id:
            raise ValueError("O histórico informado não pertence a este catequizando.")

        if self.possui_sacramento(historico.sacramento):
            raise ValueError("O sacramento informado já está registrado para este catequizando.")

        self.historico_sacramental.append(historico)

    def possui_sacramento_por_codigo(self, codigo: str) -> bool:
        codigo_normalizado = codigo.strip().lower()
        return any(
            item.sacramento.codigo.strip().lower() == codigo_normalizado
            for item in self.historico_sacramental
        )