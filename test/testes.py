import os
import tempfile
import uuid
from datetime import date, datetime

from infra.supabaseClient import get_supabase

from domain.responsavel import Responsavel
from domain.catequizando import Catequizando
from domain.etapa import Etapa
from domain.inscricao import Inscricao
from domain.statusInscricao import StatusInscricao

from repositories.responsavelRepository import ResponsavelRepository
from repositories.catequizandoRepository import CatequizandoRepository
from repositories.etapaRepository import EtapaRepository
from repositories.inscricaoRepository import InscricaoRepository

from services.servicoDocumentoInscricao import ServicoDocumentoInscricao


def garantir_status_inicial() -> StatusInscricao:
    db = get_supabase()

    resposta = (
        db.table("status_inscricao")
        .select("*")
        .eq("codigo", "pendente_distribuicao")
        .execute()
    )

    if resposta.data:
        row = resposta.data[0]
    else:
        insert_resp = (
            db.table("status_inscricao")
            .insert({
                "id": str(uuid.uuid4()),
                "codigo": "pendente_distribuicao",
                "descricao": "Pendente de distribuição"
            })
            .execute()
        )
        row = insert_resp.data[0]

    return StatusInscricao(
        id=row["id"],
        codigo=row["codigo"],
        descricao=row["descricao"]
    )


def main():
    responsavel_repo = ResponsavelRepository()
    catequizando_repo = CatequizandoRepository()
    etapa_repo = EtapaRepository()
    inscricao_repo = InscricaoRepository()
    service = ServicoDocumentoInscricao()

    responsavel_salvo = None
    catequizando_salvo = None
    etapa_salva = None
    status_inicial = None
    inscricao_salva = None
    documento_salvo = None
    caminho_temporario = None

    print("=== TESTE MANUAL AUTOCONTIDO: ServicoDocumentoInscricao ===\n")

    try:
        print("1. Criando responsável...")
        responsavel = Responsavel(
            id=str(uuid.uuid4()),
            nome=f"Responsável Teste {uuid.uuid4().hex[:8]}",
            email=f"responsavel_{uuid.uuid4().hex[:8]}@teste.com",
            telefone="11999999999",
            usuario=None,
            vinculos=[]
        )
        responsavel_result = responsavel_repo.salvar(responsavel)
        print(responsavel_result)

        responsavel_row = responsavel_result[0]
        responsavel_salvo = Responsavel(
            id=responsavel_row["id"],
            nome=responsavel_row["nome"],
            email=responsavel_row.get("email"),
            telefone=responsavel_row.get("telefone"),
            usuario=None,
            vinculos=[]
        )
        print()

        print("2. Criando catequizando...")
        catequizando = Catequizando(
            id=str(uuid.uuid4()),
            nome=f"Catequizando Teste {uuid.uuid4().hex[:8]}",
            data_nascimento=date(2015, 5, 20),
            endereco="Rua Teste, 456",
            telefone="11988888888",
            email=f"catequizando_{uuid.uuid4().hex[:8]}@teste.com",
            observacoes="Criado para teste autocontido",
            necessidade_especial=False,
            descricao_necessidade_especial=None,
            vinculos_responsaveis=[],
            historico_sacramental=[]
        )
        catequizando_result = catequizando_repo.salvar(catequizando)
        print(catequizando_result)

        catequizando_row = catequizando_result[0]
        catequizando_salvo = Catequizando(
            id=catequizando_row["id"],
            nome=catequizando_row["nome"],
            data_nascimento=date.fromisoformat(catequizando_row["data_nascimento"]),
            endereco=catequizando_row.get("endereco"),
            telefone=catequizando_row.get("telefone"),
            email=catequizando_row.get("email"),
            observacoes=catequizando_row.get("observacoes"),
            necessidade_especial=catequizando_row.get("necessidade_especial", False),
            descricao_necessidade_especial=catequizando_row.get("descricao_necessidade_especial"),
            vinculos_responsaveis=[],
            historico_sacramental=[]
        )
        print()

        print("3. Criando etapa...")
        etapa = Etapa(
            id=str(uuid.uuid4()),
            nome=f"Etapa Teste {uuid.uuid4().hex[:8]}",
            descricao="Etapa criada para teste autocontido",
            ano_nasc_minimo=2010,
            ano_nasc_maximo=2018,
            sacramentos_requeridos=[],
            sacramentos_proibidos=[]
        )
        etapa_result = etapa_repo.salvar(etapa)
        print(etapa_result)

        etapa_row = etapa_result[0]
        etapa_salva = Etapa(
            id=etapa_row["id"],
            nome=etapa_row["nome"],
            descricao=etapa_row.get("descricao"),
            ano_nasc_minimo=etapa_row.get("ano_nasc_minimo"),
            ano_nasc_maximo=etapa_row.get("ano_nasc_maximo"),
            sacramentos_requeridos=[],
            sacramentos_proibidos=[]
        )
        print()

        print("4. Garantindo status inicial...")
        status_inicial = garantir_status_inicial()
        print(status_inicial)
        print()

        print("5. Criando inscrição...")
        inscricao = Inscricao(
            id=str(uuid.uuid4()),
            catequizando=catequizando_salvo,
            responsavel=responsavel_salvo,
            etapa=etapa_salva,
            status=status_inicial,
            data_inscricao=datetime.now(),
            turma=None,
            termo_assinado=False,
            quer_mesma_turma_que_irmao=False,
            referencia_irmao=None,
            observacao_responsavel="Inscrição criada para teste autocontido",
            override_idade=False,
            motivo_override=None,
            usuario_override=None
        )
        inscricao_result = inscricao_repo.salvar(inscricao)
        print(inscricao_result)

        inscricao_row = inscricao_result[0]
        inscricao_salva = Inscricao(
            id=inscricao_row["id"],
            catequizando=catequizando_salvo,
            responsavel=responsavel_salvo,
            etapa=etapa_salva,
            status=status_inicial,
            data_inscricao=datetime.fromisoformat(inscricao_row["data_inscricao"]) if inscricao_row.get("data_inscricao") else None,
            turma=None,
            termo_assinado=inscricao_row.get("termo_assinado", False),
            quer_mesma_turma_que_irmao=inscricao_row.get("quer_mesma_turma_que_irmao", False),
            referencia_irmao=inscricao_row.get("referencia_irmao"),
            observacao_responsavel=inscricao_row.get("observacao_responsavel"),
            override_idade=inscricao_row.get("override_idade", False),
            motivo_override=inscricao_row.get("motivo_override"),
            usuario_override=None
        )
        print()

        print("6. Criando arquivo temporário PDF...")
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp:
            temp.write(b"%PDF-1.4\n%teste manual autocontido documento inscricao\n")
            caminho_temporario = temp.name

        print(f"Arquivo temporário criado: {caminho_temporario}")
        print()

        print("7. Enviando documento...")
        documento_salvo = service.enviar_documento(
            inscricao_id=inscricao_salva.id,
            tipo_documento="identidade",
            caminho_arquivo_local=caminho_temporario,
            nome_original="documento_teste_autocontido.pdf",
            bucket="inscricao-documentos",
        )
        print("Documento salvo com sucesso.")
        print(documento_salvo)
        print()

        print("8. Gerando URL assinada...")
        url_assinada = service.gerar_url_download(
            documento_id=documento_salvo.id,
            expires_in=3600,
        )
        print("URL assinada gerada com sucesso.")
        print(url_assinada)
        print()

        print("=== TESTE MANUAL FINALIZADO COM SUCESSO ===")

    finally:
        print("\n9. Limpando dados de teste...")

        if documento_salvo is not None and getattr(documento_salvo, "id", None) is not None:
            try:
                apagado_documento = service.apagar_documento(documento_salvo.id)
                print(f"Documento removido do storage e do banco: {apagado_documento}")
            except Exception as e:
                print(f"Erro ao apagar documento: {e}")

        if inscricao_salva is not None and getattr(inscricao_salva, "id", None) is not None:
            try:
                inscricao_repo.apagar(inscricao_salva.id)
                print("Inscrição removida.")
            except Exception as e:
                print(f"Erro ao apagar inscrição: {e}")

        if etapa_salva is not None and getattr(etapa_salva, "id", None) is not None:
            try:
                etapa_repo.apagar(etapa_salva.id)
                print("Etapa removida.")
            except Exception as e:
                print(f"Erro ao apagar etapa: {e}")

        if catequizando_salvo is not None and getattr(catequizando_salvo, "id", None) is not None:
            try:
                catequizando_repo.apagar(catequizando_salvo.id)
                print("Catequizando removido.")
            except Exception as e:
                print(f"Erro ao apagar catequizando: {e}")

        if responsavel_salvo is not None and getattr(responsavel_salvo, "id", None) is not None:
            try:
                responsavel_repo.apagar(responsavel_salvo.id)
                print("Responsável removido.")
            except Exception as e:
                print(f"Erro ao apagar responsável: {e}")

        if caminho_temporario and os.path.exists(caminho_temporario):
            os.remove(caminho_temporario)
            print("Arquivo temporário local removido.")

        print("\n=== LIMPEZA FINALIZADA ===")


if __name__ == "__main__":
    main()