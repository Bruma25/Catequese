#!/usr/bin/python
# -*- coding: utf-8 -*-
from dataclasses import dataclass, field
from typing import List, Optional, TYPE_CHECKING

from app.domain.sacramento import Sacramento

if TYPE_CHECKING:
    from app.domain.catequizando import Catequizando
    from app.domain.turma import Turma


@dataclass
class Etapa:
    """
    Representa a fase da catequese (Primeira Eucaristia, Crisma, Catequese Adultos).
    Define requisitos gerais de idade e sacramentos.
    """
    id: str
    nome: str
    descricao: Optional[str] = None
    ano_nasc_minimo: Optional[int] = None
    ano_nasc_maximo: Optional[int] = None
    sacramentos_requeridos: List[Sacramento] = field(default_factory=list)
    sacramentos_proibidos: List[Sacramento] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.normalizar_campos()
        self.validar()

    def normalizar_campos(self) -> None:
        self.id = self._normalizar_texto_obrigatorio(self.id, "id")
        self.nome = self._normalizar_texto_obrigatorio(self.nome, "nome")
        self.descricao = self._normalizar_texto_opcional(self.descricao)

    def validar(self) -> None:
        if self.ano_nasc_minimo is not None and not isinstance(self.ano_nasc_minimo, int):
            raise ValueError("O ano de nascimento mínimo da etapa deve ser um inteiro.")

        if self.ano_nasc_maximo is not None and not isinstance(self.ano_nasc_maximo, int):
            raise ValueError("O ano de nascimento máximo da etapa deve ser um inteiro.")

        self.sacramentos_requeridos = self._remover_duplicados_por_id(self.sacramentos_requeridos)
        self.sacramentos_proibidos = self._remover_duplicados_por_id(self.sacramentos_proibidos)

        self.validar_requisitos()

    def validar_requisitos(self) -> None:
        if (
            self.ano_nasc_minimo is not None
            and self.ano_nasc_maximo is not None
            and self.ano_nasc_minimo > self.ano_nasc_maximo
        ):
            raise ValueError(
                "O ano de nascimento mínimo da etapa não pode ser maior que o ano máximo."
            )

        ids_requeridos = {s.id for s in self.sacramentos_requeridos}
        ids_proibidos = {s.id for s in self.sacramentos_proibidos}

        if ids_requeridos.intersection(ids_proibidos):
            raise ValueError(
                "Um mesmo sacramento não pode ser ao mesmo tempo requerido e proibido na etapa."
            )

    def aceita_catequizando(self, catequizando: "Catequizando") -> bool:
        if catequizando is None:
            return False

        if not self.verifica_idade(catequizando):
            return False

        if not self.verifica_sacramentos(catequizando):
            return False

        return True

    def verifica_idade(self, catequizando: "Catequizando") -> bool:
        """
        Verifica se o catequizando está dentro da faixa de ano de nascimento da etapa.
        Essa regra é geral e mais rígida: se reprovar aqui, não deve entrar na etapa.
        """
        if catequizando is None:
            return False

        ano = catequizando.ano_nascimento

        if self.ano_nasc_minimo is not None and ano < self.ano_nasc_minimo:
            return False

        if self.ano_nasc_maximo is not None and ano > self.ano_nasc_maximo:
            return False

        return True

    def verifica_sacramentos(self, catequizando: "Catequizando") -> bool:
        """
        Verifica se o catequizando:
        - Possui todos os sacramentos requeridos.
        - Não possui nenhum dos sacramentos proibidos.
        """
        if catequizando is None:
            return False

        for sac_req in self.sacramentos_requeridos:
            if not catequizando.possui_sacramento(sac_req):
                return False

        for sac_prob in self.sacramentos_proibidos:
            if catequizando.possui_sacramento(sac_prob):
                return False

        return True

    def listar_turmas_ativas(self, turmas: List["Turma"]) -> List["Turma"]:
        """
        Retorna apenas as turmas ativas desta etapa a partir de uma lista de turmas.
        Útil para o coordenador escolher turmas ao distribuir inscrições.
        """
        if turmas is None:
            return []

        return [
            turma for turma in turmas
            if turma is not None
            and turma.etapa is not None
            and turma.etapa.id == self.id
            and turma.ativa
        ]

    def pode_catequizando_entrar(self, catequizando: "Catequizando") -> bool:
        return self.aceita_catequizando(catequizando)

    def possui_sacramento_requerido(self, sacramento: Sacramento) -> bool:
        if sacramento is None:
            return False
        return any(s.id == sacramento.id for s in self.sacramentos_requeridos)

    def possui_sacramento_proibido(self, sacramento: Sacramento) -> bool:
        if sacramento is None:
            return False
        return any(s.id == sacramento.id for s in self.sacramentos_proibidos)

    def _remover_duplicados_por_id(self, sacramentos: List[Sacramento]) -> List[Sacramento]:
        unicos = []
        ids_adicionados = set()

        for sacramento in sacramentos:
            if sacramento is None:
                raise ValueError("A lista de sacramentos da etapa não pode conter itens nulos.")

            if sacramento.id in ids_adicionados:
                continue

            ids_adicionados.add(sacramento.id)
            unicos.append(sacramento)

        return unicos

    @staticmethod
    def _normalizar_texto_obrigatorio(valor: str, campo: str) -> str:
        texto = (valor or "").strip()
        if not texto:
            raise ValueError(f"O {campo} da etapa é obrigatório.")
        return texto

    @staticmethod
    def _normalizar_texto_opcional(valor: Optional[str]) -> Optional[str]:
        if valor is None:
            return None
        texto = valor.strip()
        return texto or None