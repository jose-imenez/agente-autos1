"""
Punto de entrada principal de la aplicación.

Configura la aplicación FastAPI con todas las dependencias
y componentes necesarios.
"""

import os
import logging
from contextlib import asynccontextmanager
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from application.use_cases.analisis_use_cases import AnalizarProblemaUseCase
from domain.interfaces.ports import IAnalizadorService, IHistorialService
from infrastructure.errors.error_handlers import configurar_manejo_errores
from infrastructure.logging.structured_logging import (
    configurar_logging,
    app_logger,
)
from infrastructure.services.analizador_ia_service import AnalizadorIAAvanzado
from infrastructure.services.historial_service import HistorialService
from infrastructure.services.llm_service import get_llm_service
from infrastructure.services.skills_loader import get_skills_loader
from presentation.routes.problema_routes import router, set_use_cases


# Cargar variables de entorno desde .env
env_path = Path(__file__).parent / ".env"
load_dotenv(env_path)

# Configurar logging estructurado
configurar_logging(nivel="INFO")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestor del ciclo de vida de la aplicación."""
    # Inicio
    app_logger.info(
        "Iniciando aplicación",
        version="1.0.0",
        environment="development",
    )
    
    # Inicializar servicios (Inyección de dependencias manual)
    from infrastructure.services.motor_analisis_estrategico import MotorAnalisisEstrategico
    analizador_service: IAnalizadorService = MotorAnalisisEstrategico()
    historial_service: IHistorialService = HistorialService()
    
    # Inicializar servicios de LLM y Skills
    llm_service = get_llm_service()
    skills_loader = get_skills_loader()
    
    # Crear caso de uso
    analizar_use_case = AnalizarProblemaUseCase(
        analizador_service=analizador_service,
        historial_service=historial_service,
    )
    
    # Inyectar en rutas
    set_use_cases(analizar_use_case, analizar_use_case)
    
    app_logger.info(
        "Servicios inicializados",
        servicios=["MotorAnalisisEstrategico", "HistorialService", "LLMService", "SkillsLoader"],
    )
    
    yield
    
    # Cierre
    app_logger.info("Cerrando aplicación")


# Crear aplicación FastAPI
app = FastAPI(
    title="Agente IA - API de Análisis",
    description="API REST para análisis inteligente de problemas con generación de soluciones",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# Configurar manejo de errores
configurar_manejo_errores(app)

# Montar archivos estáticos
static_path = Path("presentation/static")
if static_path.exists():
    app.mount("/static", StaticFiles(directory=str(static_path)), name="static")

# Incluir rutas
app.include_router(router)


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Página principal - redirige a la aplicación."""
    from fastapi.templating import Jinja2Templates
    templates = Jinja2Templates(directory="presentation/templates")
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/favicon.ico")
async def favicon():
    """Serve favicon."""
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/static/favicon.ico")


# ====================
# Webhook para n8n
# ====================

from infrastructure.web_client import get_web_client


@app.post("/webhook/n8n")
async def webhook_n8n(request: Request):
    """
    Webhook para n8n - Obtiene precios de autos en tiempo real.
    Envía un JSON con: {"marca": "toyota", "modelo": "corolla", "anio": "2024"}
    """
    try:
        body = await request.json()
    except:
        body = {}
    
    marca = body.get("marca", "")
    modelo = body.get("modelo", "")
    anio = body.get("anio", "")
    
    if not marca:
        marca = request.query_params.get("marca", "")
        modelo = request.query_params.get("modelo", modelo)
        anio = request.query_params.get("anio", anio)
    
    if not marca and not modelo:
        return JSONResponse(
            status_code=400,
            content={"error": "Se requiere marca o modelo", "ejemplo": {"marca": "toyota", "modelo": "corolla"}}
        )
    
    web_client = get_web_client()
    resultado = web_client.buscar_precios_auto(marca, modelo, anio)
    
    return {
        "status": "success",
        "marca": marca,
        "modelo": modelo,
        "anio": anio,
        "fuente": "https://serpapi.com/search",
        "timestamp": resultado.get("busqueda", {}).get("timestamp"),
        "precios_nuevos": resultado.get("precios_nuevos", []),
        "precios_usados": resultado.get("precios_usados", []),
        "especificaciones": resultado.get("especificaciones", {}),
    }


@app.get("/webhook/n8n")
async def webhook_n8n_get(marca: str = "", modelo: str = "", anio: str = ""):
    """Webhook GET para n8n - Ejemplo: /webhook/n8n?marca=toyota&modelo=corolla"""
    if not marca and not modelo:
        return JSONResponse(
            status_code=400,
            content={"error": "Se requiere marca o modelo", "ejemplo": "/webhook/n8n?marca=toyota&modelo=corolla"}
        )
    
    web_client = get_web_client()
    resultado = web_client.buscar_precios_auto(marca, modelo, anio)
    
    return {
        "status": "success",
        "marca": marca,
        "modelo": modelo,
        "anio": anio,
        "fuente": "https://serpapi.com/search",
        "timestamp": resultado.get("busqueda", {}).get("timestamp"),
        "precios_nuevos": resultado.get("precios_nuevos", []),
        "precios_usados": resultado.get("precios_usados", []),
        "especificaciones": resultado.get("especificaciones", {}),
    }


if __name__ == "__main__":
    import uvicorn
    
    app_logger.info(
        "Iniciando servidor",
        host="0.0.0.0",
        port=8000,
    )
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
