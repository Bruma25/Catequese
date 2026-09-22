import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import App from './App.jsx'
import './index.css'


createRoot(document.getElementById('root')).render(
  <StrictMode>
    <App />
  </StrictMode>,
)

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <BrowserRouter basename="/Catequese">
      <App />
    </BrowserRouter>
  </React.StrictMode>,
)

from fastapi import FastAPI
from fastapi.security import OAuth2PasswordBearer

app = FastAPI(
    title="Catequese API",
    description="API para gestão da catequese",
    version="1.0.0",
    openapi_url="/api/v1/openapi.json",
    docs_url="/docs",
)

# Configurar OAuth2 para o Swagger
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

# Opcional: Adicionar esquema de segurança global
app.openapi_schema = None

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = app.openapi()

    # Adicionar componente de segurança
    openapi_schema["components"]["securitySchemes"] = {
        "Bearer": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "Insira o token JWT do Supabase: `Bearer <seu_token>`"
        }
    }

    # Aplicar segurança global (opcional)
    # openapi_schema["security"] = [{"Bearer": []}]

    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi