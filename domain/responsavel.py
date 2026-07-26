#!/usr/bin/python
# -*- coding: utf-8 -*-
from dataclasses import dataclass, field
from typing import List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from domain.usuario import Usuario
    from domain.catequizando import Catequizando
    from domain.catequizandoResponsavel import CatequizandoResponsavel


@dataclass
class Responsavel:
    """
    Representa uma pessoa responsável por um ou mais catequizandos.
    Pode estar ligada a um Usuario, se tiver acesso ao sistema.
    """
    id: str
    nome: str
    email: Optional[str] = None
    telefone: Optional[str] = None
    usuario: Optional["Usuario"] = None
    vinculos: List["CatequizandoResponsavel"] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.normalizar_campos()
        self.validar()

    def normalizar_campos(self) -> None:
        self.id = self._normalizar_texto_obrigatorio(self.id, "id")
        self.nome = self._normalizar_texto_obrigatorio(self.nome, "nome")
        self.email = self._normalizar_texto_opcional(self.email)
        self.telefone = self._normalizar_texto_opcional(self.telefone)

    def validar(self) -> None:
        if self.usuario is not None and getattr(self.usuario, "id", None) is None:
            raise ValueError("O usuário do responsável deve possuir id válido.")

    def listar_catequizandos(self) -> List["Catequizando"]:
        catequizandos = []
        ids_adicionados = set()

        for vinculo in self.vinculos:
            catequizando = getattr(vinculo, "catequizando", None)
            catequizando_id = getattr(catequizando, "id", None)

            if catequizando is None or catequizando_id is None:
                continue

            if catequizando_id in ids_adicionados:
                continue

            ids_adicionados.add(catequizando_id)
            catequizandos.append(catequizando)

        return catequizandos

    def quantidade_catequizandos(self) -> int:
        return len(self.listar_catequizandos())

    def possui_usuario(self) -> bool:
        return self.usuario is not None

    def pertence_ao_usuario(self, usuario: Optional["Usuario"]) -> bool:
        if usuario is None or self.usuario is None:
            return False
        return self.usuario.id == usuario.id

    def possui_vinculo_com(self, catequizando: Optional["Catequizando"]) -> bool:
        if catequizando is None:
            return False

        catequizando_id = getattr(catequizando, "id", None)
        if catequizando_id is None:
            return False

        return any(
            getattr(getattr(vinculo, "catequizando", None), "id", None) == catequizando_id
            for vinculo in self.vinculos
        )

    def pode_responder_por(self, catequizando: Optional["Catequizando"]) -> bool:
        return self.possui_vinculo_com(catequizando)

    def adicionar_vinculo(self, vinculo: "CatequizandoResponsavel") -> None:
        if vinculo is None:
            raise ValueError("O vínculo informado é obrigatório.")

        if getattr(vinculo, "responsavel", None) is None:
            raise ValueError("O vínculo deve possuir responsável.")

        if vinculo.responsavel.id != self.id:
            raise ValueError("O vínculo informado não pertence a este responsável.")

        catequizando = getattr(vinculo, "catequizando", None)
        if catequizando is None or getattr(catequizando, "id", None) is None:
            raise ValueError("O vínculo deve possuir catequizando válido.")

        if self.possui_vinculo_com(catequizando):
            raise ValueError("Este responsável já possui vínculo com o catequizando informado.")

        self.vinculos.append(vinculo)

    def remover_vinculo(self, catequizando: "Catequizando") -> None:
        if catequizando is None or getattr(catequizando, "id", None) is None:
            raise ValueError("O catequizando informado é obrigatório.")

        vinculos_restantes = [
            vinculo
            for vinculo in self.vinculos
            if getattr(getattr(vinculo, "catequizando", None), "id", None) != catequizando.id
        ]

        if len(vinculos_restantes) == len(self.vinculos):
            raise ValueError("Este responsável não possui vínculo com o catequizando informado.")

        self.vinculos = vinculos_restantes

    @staticmethod
    def _normalizar_texto_obrigatorio(valor: str, campo: str) -> str:
        texto = (valor or "").strip()
        if not texto:
            raise ValueError(f"O {campo} do responsável é obrigatório.")
        return texto

    @staticmethod
    def _normalizar_texto_opcional(valor: Optional[str]) -> Optional[str]:
        if valor is None:
            return None
        texto = valor.strip()
        return texto or None