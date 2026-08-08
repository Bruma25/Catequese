#from fastapi import FastAPI
# app = FastAPI(
#     title="Módulo de Inscrição",
#     version="0.1.0",
#     description="API inicial do módulo de inscrição.",
# )
#
#
# @app.get("/")
# def root():
#     return {
#         "message": "API do módulo de inscrição no ar."
#     }
#
#
# @app.get("/health")
# def health():
#     return {
#         "status": "ok"
#     }
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.inscricao import router as inscricao_router

app = FastAPI(
    title="Módulo de Inscrição",
    version="0.1.0",
    description="API para gestão da catequese - módulo de inscrição",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configurar CORS para permitir acesso do frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especificar os domínios permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(inscricao_router, prefix="/api/v1", tags=["Inscrições"])


@app.get("/")
def root():
    return {
        "message": "API do módulo de inscrição no ar.",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health")
def health():
    return {
        "status": "ok"
    }