"""
Agente de Autos con RAG y Búsqueda Web
Listo para conectar con n8n cloud

Este módulo expone endpoints REST para consultar precios de autos.
"""

import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from dotenv import load_dotenv
from pathlib import Path

# Cargar variables de entorno
env_path = Path(__file__).parent / ".env"
load_dotenv(env_path)

# Importar servicios
from infrastructure.web_client import get_web_client

# Crear app
app = FastAPI(
    title="Agente de Autos API",
    description="API para buscar precios de autos en tiempo real",
    version="1.0.0"
)

# CORS para n8n
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modelos
class ConsultaAuto(BaseModel):
    marca: Optional[str] = ""
    modelo: Optional[str] = ""
    anio: Optional[str] = ""

# Endpoints

@app.get("/")
def root():
    return {
        "status": "ok",
        "service": "Agente de Autos",
        "version": "1.0.0",
        "endpoints": {
            "GET /": "Información del servicio",
            "GET /precio": "Consulta precios - params: marca, modelo, anio",
            "POST /precio": "Consulta precios - body: {marca, modelo, anio}",
            "GET /health": "Health check"
        }
    }

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.get("/precio")
def precio_get(marca: str = "", modelo: str = "", anio: str = ""):
    """Consulta precios de autos - GET"""
    if not marca and not modelo:
        return {"error": "Se requiere marca o modelo"}
    
    web = get_web_client()
    resultado = web.buscar_precios_auto(marca, modelo, anio)
    
    return {
        "status": "success",
        "query": {"marca": marca, "modelo": modelo, "anio": anio},
        "fuente": "https://serpapi.com/search",
        "precios_nuevos": resultado.get("precios_nuevos", [])[:5],
        "precios_usados": resultado.get("precios_usados", [])[:5],
        "especificaciones": resultado.get("especificaciones", {}),
    }

@app.post("/precio")
def precio_post(consulta: ConsultaAuto):
    """Consulta precios de autos - POST"""
    web = get_web_client()
    resultado = web.buscar_precios_auto(
        consulta.marca or "",
        consulta.modelo or "",
        consulta.anio or ""
    )
    
    return {
        "status": "success",
        "query": {"marca": consulta.marca, "modelo": consulta.modelo, "anio": consulta.anio},
        "fuente": "https://serpapi.com/search",
        "precios_nuevos": resultado.get("precios_nuevos", [])[:5],
        "precios_usados": resultado.get("precios_usados", [])[:5],
        "especificaciones": resultado.get("especificaciones", {}),
    }

# Para ejecutar localmente
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
