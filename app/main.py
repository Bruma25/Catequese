from fastapi import FastAPI

app = FastAPI(
    title="Módulo de Inscrição",
    version="0.1.0",
    description="API inicial do módulo de inscrição.",
)


@app.get("/")
def root():
    return {
        "message": "API do módulo de inscrição no ar."
    }


@app.get("/health")
def health():
    return {
        "status": "ok"
    }