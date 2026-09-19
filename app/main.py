from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.inscricao import router as inscricao_router
from app.routes.usuario import router as usuario_router

app = FastAPI(
    title="Módulo de Inscrição",
    version="0.1.0",
    description="API para gestão da catequese - módulo de inscrição.",
)

# CORS para permitir frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(inscricao_router, prefix="/api/v1")
app.include_router(usuario_router, prefix="/api/v1")
app.include_router(catequizando_router, prefix="/api/v1")

@app.get("/")
def root():
    return {
        "message": "API do módulo de inscrição no ar."
    }

def read_root():
    return {"message": "API da Catequese"}

@app.get("/health")
def health():
    return {
        "status": "ok"
    }