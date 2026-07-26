#!/usr/bin/python
# -*- coding: utf-8 -*-
from dataclasses import dataclass, field
from typing import List, Optional, TYPE_CHECKING

from app.domain.localEncontro import LocalEncontro

if TYPE_CHECKING:
    from app.domain.etapa import Etapa
    from app.domain.catequista import Catequista
    from app.domain.catequizando import Catequizando
    from app.domain.inscricao import Inscricao


@dataclass
class Turma:
    """
    Representa uma turma específica de uma etapa.
    Guarda vagas, faixa etária específica e local de encontros.
    """
    id: str
    etapa: "Etapa"
    nome_sistema: str
    nome_exibicao: Optional[str]
    vagas_totais: int
    ativa: bool
    local_encontro: LocalEncontro
    ano_nasc_minimo: Optional[int] = None
    ano_nasc_maximo: Optional[int] = None
    catequistas: List["Catequista"] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.normalizar_campos()
        self.validar()

    def normalizar_campos(self) -> None:
        self.id = self._normalizar_texto_obrigatorio(self.id, "id")
        self.nome_sistema = self._normalizar_texto_obrigatorio(
            self.nome_sistema,
            "nome_sistema",
        )
        self.nome_exibicao = self._normalizar_texto_opcional(self.nome_exibicao)

    def validar(self) -> None:
        if self.etapa is None:
            raise ValueError("A etapa da turma é obrigatória.")

        if self.local_encontro is None:
            raise ValueError("O local de encontro da turma é obrigatório.")

        if not isinstance(self.vagas_totais, int):
            raise ValueError("A quantidade de vagas totais da turma deve ser um inteiro.")

        if self.vagas_totais < 0:
            raise ValueError("A quantidade de vagas totais da turma não pode ser negativa.")

        if self.ano_nasc_minimo is not None and not isinstance(self.ano_nasc_minimo, int):
            raise ValueError("O ano de nascimento mínimo da turma deve ser um inteiro.")

        if self.ano_nasc_maximo is not None and not isinstance(self.ano_nasc_maximo, int):
            raise ValueError("O ano de nascimento máximo da turma deve ser um inteiro.")

        if (
            self.ano_nasc_minimo is not None
            and self.ano_nasc_maximo is not None
            and self.ano_nasc_minimo > self.ano_nasc_maximo
        ):
            raise ValueError("O ano de nascimento mínimo da turma não pode ser maior que o ano máximo.")

        self.catequistas = self._remover_catequistas_duplicados(self.catequistas)

    def _remover_catequistas_duplicados(self, catequistas: List["Catequista"]) -> List["Catequista"]:
        unicos = []
        ids_adicionados = set()

        for catequista in catequistas:
            if catequista is None:
                raise ValueError("A lista de catequistas da turma não pode conter itens nulos.")

            if catequista.id in ids_adicionados:
                continue

            ids_adicionados.add(catequista.id)
            unicos.append(catequista)

        return unicos

    def tem_vaga(self, inscricoes_confirmadas: int) -> bool:
        """
        Retorna True se o número de inscrições confirmadas for menor que as vagas totais.
        """
        if not isinstance(inscricoes_confirmadas, int):
            raise ValueError("A quantidade de inscrições confirmadas deve ser um inteiro.")

        if inscricoes_confirmadas < 0:
            raise ValueError("A quantidade de inscrições confirmadas não pode ser negativa.")

        return inscricoes_confirmadas < self.vagas_totais

    def verifica_idade_especifica(self, catequizando: "Catequizando") -> bool:
        """
        Verifica se o catequizando se encaixa na faixa de ano de nascimento
        específica da turma (se houver).
        Se ano_nasc_minimo/maximo forem None, considera que não há restrição extra.
        """
        if catequizando is None:
            return False

        ano = catequizando.ano_nascimento

        if self.ano_nasc_minimo is not None and ano < self.ano_nasc_minimo:
            return False

        if self.ano_nasc_maximo is not None and ano > self.ano_nasc_maximo:
            return False

        return True

    def verifica_sacramentos_especificos(self, catequizando: "Catequizando") -> bool:
        """
        Ponto de extensão para requisitos específicos por turma.
        Por enquanto, retorna sempre True (sem regra extra).
        """
        if catequizando is None:
            return False

        return True

    def aceita_catequizando_sem_restricao_etaria(self, catequizando: "Catequizando") -> bool:
        """
        Aplica apenas os critérios rígidos próprios da turma que não podem
        ser excepcionalizados por override de idade.
        """
        if catequizando is None:
            return False

        if not self.esta_ativa():
            return False

        if not self.verifica_sacramentos_especificos(catequizando):
            return False

        return True

    def aceita_catequizando(self, catequizando: "Catequizando") -> bool:
        """
        Aplica os critérios próprios da turma.
        Não checa requisitos gerais da etapa e não checa vaga.
        """
        if not self.aceita_catequizando_sem_restricao_etaria(catequizando):
            return False

        if not self.verifica_idade_especifica(catequizando):
            return False

        return True

    def pode_catequizando_entrar(self, catequizando: "Catequizando") -> bool:
        return self.aceita_catequizando(catequizando)

    def pertence_a_mesma_etapa(self, inscricao: "Inscricao") -> bool:
        if inscricao is None:
            return False

        etapa_inscricao = getattr(inscricao, "etapa", None)
        if etapa_inscricao is not None and getattr(etapa_inscricao, "id", None) is not None:
            return self.etapa.id == etapa_inscricao.id

        etapa_id_inscricao = getattr(inscricao, "etapa_id", None)
        if etapa_id_inscricao is not None:
            return self.etapa.id == etapa_id_inscricao

        return False

    def pode_receber(self, inscricao: "Inscricao", inscricoes_confirmadas: int = 0) -> bool:
        """
        Verifica se a turma pode receber a inscrição:
        - precisa estar na mesma etapa;
        - precisa aceitar o catequizando pelos critérios próprios;
        - precisa ter vaga.
        """
        if inscricao is None:
            return False

        catequizando = getattr(inscricao, "catequizando", None)
        if catequizando is None:
            return False

        if not self.pertence_a_mesma_etapa(inscricao):
            return False

        if not self.aceita_catequizando(catequizando):
            return False

        if not self.tem_vaga(inscricoes_confirmadas):
            return False

        return True

    def pertence_a_etapa(self, etapa: "Etapa") -> bool:
        if etapa is None:
            return False
        return self.etapa.id == etapa.id

    def esta_ativa(self) -> bool:
        return self.ativa is True

    def quantidade_catequistas(self) -> int:
        return len(self.catequistas)

    @staticmethod
    def _normalizar_texto_obrigatorio(valor: str, campo: str) -> str:
        texto = (valor or "").strip()
        if not texto:
            if campo == "id":
                raise ValueError("O id da turma é obrigatório.")
            if campo == "nome_sistema":
                raise ValueError("O nome de sistema da turma é obrigatório.")
            raise ValueError(f"O campo {campo} da turma é obrigatório.")
        return texto

    @staticmethod
    def _normalizar_texto_opcional(valor: Optional[str]) -> Optional[str]:
        if valor is None:
            return None
        texto = valor.strip()
        return texto or None