#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste completo da regra de vagas na criação de inscrição (com limpeza).

O que o script faz:
1. Cria uma etapa de teste.
2. Cria um local de encontro (se necessário).
3. Cria uma turma dessa etapa com vagas limitadas.
4. Lista inscrições existentes antes do teste.
5. Cria N inscrições novas (configurável) via API.
6. Busca cada inscrição criada e verifica o status.
7. Asserta que:
   - as primeiras inscrições têm status 'confirmada' (quando há vaga);
   - as últimas têm status 'lista_espera' (quando não há mais vaga).

Limpa as inscrições, turma e etapa no final.
"""

import requests
import time
import uuid
import os

from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

# ==============================
# CONFIGURAÇÕES
# ==============================

BASE_URL = "https://catequese-ttg8.onrender.com/api/v1"
NUM_INSCRICOES_PARA_TESTE = 7
VAGAS_TURMA = 5
API_TIMEOUT = 60

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL ou SUPABASE_SERVICE_KEY não foram carregados do .env")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# ==============================
# FUNÇÕES AUXILIARES - BANCO
# ==============================

def criar_etapa_teste():
    etapa_id = str(uuid.uuid4())
    payload = {
        "id": etapa_id,
        "nome": f"Etapa Teste {time.time()}",
        "descricao": "Etapa criada para teste automático de vagas",
        "ano_nasc_minimo": 2014,
        "ano_nasc_maximo": 2017,
    }

    result = (
        supabase
        .table("etapa")
        .insert(payload)
        .execute()
    )

    if not result.data:
        raise ValueError("Não foi possível criar a etapa de teste.")

    return etapa_id

def garantir_local_encontro():
    result = (
        supabase
        .table("local_encontro")
        .select("id")
        .limit(1)
        .execute()
    )

    if result.data and len(result.data) > 0:
        return result.data[0]["id"]

    local_id = 1
    payload = {
        "id": local_id,
        "codigo": "SEDE_TESTE",
        "nome_exibicao": "Paróquia - Salão Principal (Teste)",
    }

    result = (
        supabase
        .table("local_encontro")
        .insert(payload)
        .execute()
    )

    if not result.data:
        raise ValueError("Não foi possível criar o local de encontro de teste.")

    return local_id

def criar_turma_teste(etapa_id: str, local_encontro_id: int):
    turma_id = str(uuid.uuid4())
    payload = {
        "id": turma_id,
        "etapa_id": etapa_id,
        "nome_sistema": f"TURMA_TESTE_{int(time.time())}",
        "nome_exibicao": "Turma Teste",
        "vagas_totais": VAGAS_TURMA,
        "ativa": True,
        "local_encontro_id": local_encontro_id,
        "ano_nasc_minimo": 2014,
        "ano_nasc_maximo": 2017,
    }

    result = (
        supabase
        .table("turma")
        .insert(payload)
        .execute()
    )

    if not result.data:
        raise ValueError("Não foi possível criar a turma de teste.")

    return turma_id

def garantir_status_inscricao():
    status_codes = ['pendente_distribuicao', 'confirmada', 'lista_espera', 'cancelada']

    for codigo in status_codes:
        result = (
            supabase
            .table("status_inscricao")
            .select("id")
            .eq("codigo", codigo)
            .limit(1)
            .execute()
        )

        if not result.data or len(result.data) == 0:
            payload = {
                "codigo": codigo,
                "descricao": f"Status {codigo}",
            }

            result = (
                supabase
                .table("status_inscricao")
                .insert(payload)
                .execute()
            )

            if not result.data:
                raise ValueError(f"Não foi possível criar o status '{codigo}'.")

def garantir_tipo_vinculo():
    result = (
        supabase
        .table("tipo_vinculo_responsavel")
        .select("id")
        .limit(1)
        .execute()
    )

    if result.data and len(result.data) > 0:
        return result.data[0]["id"]

    payload = {
        "id": 1,
        "codigo": "PAI",
        "descricao": "Pai",
    }

    result = (
        supabase
        .table("tipo_vinculo_responsavel")
        .insert(payload)
        .execute()
    )

    if not result.data:
        raise ValueError("Não foi possível criar o tipo de vínculo de teste.")

    return 1

def contar_inscricoes_etapa(etapa_id: str) -> int:
    """
    Conta inscrições de uma etapa, excluindo canceladas.
    """
    # Busca ID do status cancelada
    result = (
        supabase
        .table("status_inscricao")
        .select("id")
        .eq("codigo", "cancelada")
        .limit(1)
        .execute()
    )

    status_cancelada_id = None
    if result.data and len(result.data) > 0:
        status_cancelada_id = result.data[0]["id"]

    # Conta inscrições
    query = (
        supabase
        .table("inscricao")
        .select("id", count="exact")
        .eq("etapa_id", etapa_id)
    )

    if status_cancelada_id:
        query = query.neq("status_id", status_cancelada_id)

    result = query.execute()

    return result.count if result.count is not None else 0

def obter_status_inscricao(inscricao_id: str) -> str:
    result = (
        supabase
        .table("inscricao")
        .select("""
            status:status_id (
                codigo
            )
        """)
        .eq("id", inscricao_id)
        .maybe_single()
        .execute()
    )

    if not result.data:
        return None

    return result.data["status"]["codigo"]

def limpar_inscricoes(ids_inscricoes: list):
    for inscricao_id in ids_inscricoes:
        try:
            (
                supabase
                .table("inscricao")
                .delete()
                .eq("id", inscricao_id)
                .execute()
            )
        except Exception:
            pass

def limpar_turma_teste(turma_id: str):
    (
        supabase
        .table("turma")
        .delete()
        .eq("id", turma_id)
        .execute()
    )

def limpar_etapa_teste(etapa_id: str):
    (
        supabase
        .table("etapa")
        .delete()
        .eq("id", etapa_id)
        .execute()
    )

# ==============================
# FUNÇÕES AUXILIARES - API
# ==============================

def listar_etapas():
    resp = requests.get(f"{BASE_URL}/etapas", timeout=API_TIMEOUT)
    resp.raise_for_status()
    return resp.json()

def listar_inscricoes():
    for tentativa in range(3):
        try:
            resp = requests.get(f"{BASE_URL}/inscricoes", timeout=API_TIMEOUT)
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.ReadTimeout:
            if tentativa == 2:
                raise
            print(f"  → Timeout na listagem. Tentando novamente ({tentativa + 1}/3)...")
            time.sleep(2)

def buscar_inscricao(inscricao_id: str):
    resp = requests.get(f"{BASE_URL}/inscricoes/{inscricao_id}", timeout=API_TIMEOUT)
    resp.raise_for_status()
    return resp.json()

def criar_inscricao_teste(etapa_id: str, indice: int):
    payload = {
        "catequizando_nome": f"Teste Vaga {indice}",
        "catequizando_data_nascimento": "2015-05-10",
        "catequizando_sacramentos": [],
        "etapa_id": etapa_id,
        "responsavel_nome": f"Responsável Teste {indice}",
        "responsavel_email": f"resp{indice}@teste.com",
        "responsavel_telefone": "11999999999",
        "responsavel_vinculo": 1,
    }

    resp = requests.post(f"{BASE_URL}/inscricoes", json=payload, timeout=API_TIMEOUT)

    if not resp.ok:
        print(f"Erro na API: {resp.status_code}")
        print(f"Corpo da resposta: {resp.text}")

    resp.raise_for_status()
    data = resp.json()
    return data["id"]

# ==============================
# TESTE
# ==============================

def main():
    print("=== Teste completo: verificação de vagas na inscrição (com limpeza) ===\n")

    etapa_id = None
    turma_id = None
    ids_inscricoes = []

    try:
        # 1. Garantir status e tipo de vínculo
        print("Garantindo status e tipo de vínculo...")
        garantir_status_inscricao()
        tipo_vinculo_id = garantir_tipo_vinculo()
        print(f"  → Tipo de vínculo ID: {tipo_vinculo_id}")

        # 2. Criar etapa de teste
        print("\nCriando etapa de teste...")
        etapa_id = criar_etapa_teste()
        print(f"  → Etapa criada: {etapa_id}")

        # 3. Garantir local de encontro
        print("\nGarantindo local de encontro...")
        local_encontro_id = garantir_local_encontro()
        print(f"  → Local de encontro ID: {local_encontro_id}")

        # 4. Criar turma de teste
        print("\nCriando turma de teste...")
        turma_id = criar_turma_teste(etapa_id, local_encontro_id)
        print(f"  → Turma criada: {turma_id}")
        print(f"  → Vagas totais: {VAGAS_TURMA}")

        # 5. Contar inscrições existentes antes do teste
        print("\nContando inscrições existentes na etapa...")
        total_inscricoes_antes = contar_inscricoes_etapa(etapa_id)
        print(f"  → Inscrições existentes na etapa: {total_inscricoes_antes}")

        # 6. Criar inscrições
        n_inscricoes = NUM_INSCRICOES_PARA_TESTE
        print(f"\nSerão criadas {n_inscricoes} inscrições para teste.")
        print(f"  → Vagas disponíveis: {VAGAS_TURMA}")
        print(f"  → Inscrições já existentes: {total_inscricoes_antes}")

        # Calcula quantas deveriam ser confirmada vs lista_espera
        vagas_restantes = max(0, VAGAS_TURMA - total_inscricoes_antes)
        esperadas_confirmada = min(n_inscricoes, vagas_restantes)
        esperadas_lista_espera = max(0, n_inscricoes - esperadas_confirmada)

        print(f"  → Esperado: {esperadas_confirmada} confirmada(s), {esperadas_lista_espera} em lista de espera\n")

        for i in range(1, n_inscricoes + 1):
            print(f"Criando inscrição {i}/{n_inscricoes}...")
            try:
                inscricao_id = criar_inscricao_teste(etapa_id, i)
                ids_inscricoes.append(inscricao_id)
                print(f"  → Inscrição criada: {inscricao_id}")
            except Exception as e:
                print(f"  → Erro ao criar inscrição {i}: {e}")
                print("Interrompendo teste.")
                return

            time.sleep(0.5)

        # 7. Verificar status de cada inscrição criada (na ordem de criação)
        print("\n=== Verificando status das inscrições ===\n")

        resultados = []
        for idx, inscricao_id in enumerate(ids_inscricoes, start=1):
            print(f"Buscando inscrição {idx}/{len(ids_inscricoes)}: {inscricao_id}...")
            try:
                detalhe = buscar_inscricao(inscricao_id)
                status_id = detalhe.get("status_id")

                status_codigo = obter_status_inscricao(inscricao_id)

                resultados.append({
                    "id": inscricao_id,
                    "status_id": status_id,
                    "status_codigo": status_codigo,
                    "indice": idx,
                })
                print(f"  → status_id = {status_id}, status = {status_codigo}")
            except Exception as e:
                print(f"  → Erro ao buscar inscrição: {e}")
                resultados.append({
                    "id": inscricao_id,
                    "status_id": None,
                    "status_codigo": None,
                    "indice": idx,
                    "erro": str(e),
                })

        # 8. Validar resultados
        print("\n=== Resultado ===\n")

        erros = []
        for r in resultados:
            if "erro" in r:
                erros.append(f"Inscrição {r['indice']} falhou ao buscar: {r['erro']}")
                continue

            idx = r["indice"]
            status = r["status_codigo"]

            if idx <= esperadas_confirmada:
                if status != "confirmada":
                    erros.append(
                        f"Inscrição {idx} deveria ser 'confirmada', mas está '{status}'."
                    )
            else:
                if status != "lista_espera":
                    erros.append(
                        f"Inscrição {idx} deveria ser 'lista_espera', mas está '{status}'."
                    )

        if erros:
            print("TESTE FALHOU:")
            for erro in erros:
                print(f"  - {erro}")
        else:
            print("TESTE APROVADO:")
            print(f"  - As primeiras {esperadas_confirmada} inscrições estão com status 'confirmada'.")
            if esperadas_lista_espera > 0:
                print(f"  - A(s) última(s) {esperadas_lista_espera} inscrição(ões) estão com status 'lista_espera'.")

        # 9. Resumo
        print("\n=== Resumo das inscrições criadas ===\n")
        for r in resultados:
            print(f"Inscrição {r['indice']} ({r['id']}): status_id = {r['status_id']}, status = {r['status_codigo']}")
            if "erro" in r:
                print(f"  Erro: {r['erro']}")

    finally:
        # Limpeza
        print("\n=== Limpeza ===")
        if ids_inscricoes:
            print(f"Limpando {len(ids_inscricoes)} inscrições...")
            limpar_inscricoes(ids_inscricoes)
        if turma_id:
            print(f"Limpando turma {turma_id}...")
            limpar_turma_teste(turma_id)
        if etapa_id:
            print(f"Limpando etapa {etapa_id}...")
            limpar_etapa_teste(etapa_id)
        print("Limpeza concluída.")

if __name__ == "__main__":
    main()