#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para popular o banco com dados iniciais da catequese.
Executar: python -m app.scripts.popular_banco_inicial
"""

from app.infra.supabaseClient import get_supabase
from uuid import uuid4


def criar_sacramentos():
    """Cria os sacramentos básicos."""
    supabase = get_supabase()

    # IDs inteiros, no UUIDs
    sacramentos = [
        {"id": 1, "codigo": "BATISMO", "nome_exibicao": "Batismo", "ordem": 1},
        {"id": 2, "codigo": "EUCARISTIA", "nome_exibicao": "Eucaristia", "ordem": 2},
        {"id": 3, "codigo": "CRISMA", "nome_exibicao": "Crisma", "ordem": 3},
    ]

    result = supabase.table("sacramento").upsert(sacramentos, on_conflict="id").execute()
    print(f"✅ {len(result.data)} sacramentos criados")
    return result.data


def criar_etapas(sacramentos):
    """Cria as etapas da catequese."""
    supabase = get_supabase()

    # IDs inteiros dos sacramentos
    batismo_id = 1
    eucaristia_id = 2

    etapas = [
        {
            "id": str(uuid4()),  # Etapa usa UUID
            "nome": "Primeira Eucaristia",
            "descricao": "Preparação para a Primeira Eucaristia",
            "ano_nasc_minimo": 2014,
            "ano_nasc_maximo": 2016,
        },
        {
            "id": str(uuid4()),
            "nome": "Crisma",
            "descricao": "Preparação para o Sacramento da Crisma",
            "ano_nasc_minimo": 2008,
            "ano_nasc_maximo": 2012,
        },
        {
            "id": str(uuid4()),
            "nome": "Catequese Adultos",
            "descricao": "Catequese para adultos e jovens",
            "ano_nasc_minimo": 1990,
            "ano_nasc_maximo": 2007,
        },
    ]

    result = supabase.table("etapa").upsert(etapas).execute()
    print(f"✅ {len(result.data)} etapas criadas")

    # Criar sacramentos requeridos para cada etapa
    etapa_eucaristia = next((e for e in etapas if e["nome"] == "Primeira Eucaristia"), None)
    etapa_crisma = next((e for e in etapas if e["nome"] == "Crisma"), None)

    sacramentos_requeridos = []

    if etapa_eucaristia:
        sacramentos_requeridos.append({
            "etapa_id": etapa_eucaristia["id"],
            "sacramento_id": batismo_id,  # Inteiro
        })

    if etapa_crisma:
        sacramentos_requeridos.append({
            "etapa_id": etapa_crisma["id"],
            "sacramento_id": batismo_id,  # Inteiro
        })
        sacramentos_requeridos.append({
            "etapa_id": etapa_crisma["id"],
            "sacramento_id": eucaristia_id,  # Inteiro
        })

    if sacramentos_requeridos:
        # Usar insert em vez de upsert, j谩 que n茫o tem id
        result = supabase.table("etapa_sacramento_requerido").insert(sacramentos_requeridos).execute()
        print(f"✅ {len(result.data)} sacramentos requeridos criados")


def criar_status_inscricao():
    """Cria os status de inscrição."""
    supabase = get_supabase()

    # IDs inteiros
    status_list = [
        {"id": 1, "codigo": "pendente_distribuicao", "descricao": "Pendente de distribuição em turma"},
        {"id": 2, "codigo": "distribuida", "descricao": "Distribuída em turma"},
        {"id": 3, "codigo": "confirmada", "descricao": "Inscrição confirmada"},
        {"id": 4, "codigo": "lista_espera", "descricao": "Em lista de espera"},
        {"id": 5, "codigo": "cancelada", "descricao": "Inscrição cancelada"},
    ]

    result = supabase.table("status_inscricao").upsert(status_list, on_conflict="id").execute()
    print(f"✅ {len(result.data)} status de inscrição criados")
    return result.data


def criar_tipos_vinculo():
    """Cria os tipos de vínculo responsável."""
    supabase = get_supabase()

    # IDs inteiros
    vinculos = [
        {"id": 1, "codigo": "pai", "descricao": "Pai"},
        {"id": 2, "codigo": "mae", "descricao": "Mãe"},
        {"id": 3, "codigo": "responsavel_legal", "descricao": "Responsável Legal"},
        {"id": 4, "codigo": "outro", "descricao": "Outro"},
    ]

    result = supabase.table("tipo_vinculo_responsavel").upsert(vinculos, on_conflict="id").execute()
    print(f"✅ {len(result.data)} tipos de vínculo criados")
    return result.data


def criar_tipo_papel_usuario():
    """Cria os papéis de usuário."""
    supabase = get_supabase()

    # IDs inteiros
    papeis = [
        {"id": 1, "codigo": "responsavel", "descricao": "Responsável por catequizando"},
        {"id": 2, "codigo": "catequista", "descricao": "Catequista"},
        {"id": 3, "codigo": "coordenador_etapa", "descricao": "Coordenador de etapa"},
        {"id": 4, "codigo": "coordenador_geral", "descricao": "Coordenador geral"},
    ]

    result = supabase.table("tipo_papel_usuario").upsert(papeis, on_conflict="id").execute()
    print(f"✅ {len(result.data)} papéis de usuário criados")
    return result.data


def main():
    print("🚀 Populando banco de dados inicial...\n")
    
    try:
        sacramentos = criar_sacramentos()
        criar_etapas(sacramentos)
        criar_status_inscricao()
        criar_tipos_vinculo()
        criar_tipo_papel_usuario()
        
        print("\n✅ Banco populada com sucesso!")
        print("\nAgora você pode testar o endpoint POST /api/v1/inscricoes")
        
    except Exception as e:
        print(f"\n❌ Erro ao popular banco: {e}")
        raise


if __name__ == "__main__":
    main()