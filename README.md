# Projeto Catequese

API em Python com FastAPI para gerenciamento do módulo de catequese.

## Estrutura do projeto

```text
projeto/
  app/
    domain/
    infra/
    repositories/
    services/
    test/
    main.py
```

## Requisitos

- Python 3.13
- pip

## Instalação

1. Criar e ativar o ambiente virtual.
2. Instalar as dependências:

```bash
pip install -r requirements.txt
```

## Execução local

Rodar a aplicação com:

```bash
uvicorn app.main:app --reload
```

A aplicação ficará disponível em:

- `http://127.0.0.1:8000/`
- `http://127.0.0.1:8000/docs`

## Testes

Para executar os testes:

```bash
pytest
```

## Variáveis de ambiente

Criar um arquivo `.env` local com as variáveis necessárias para integração com serviços externos, como Supabase.

Exemplo:

```env
SUPABASE_URL=...
SUPABASE_KEY=...
```

## Deploy

Para deploy no Render:

- Build Command:
  ```bash
  pip install -r requirements.txt
  ```

- Start Command:
  ```bash
  uvicorn app.main:app --host 0.0.0.0 --port $PORT
  ```
