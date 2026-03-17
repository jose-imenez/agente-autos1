"""
Multi-Agente con RAG y MCP
Simplificado para Render
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from dotenv import load_dotenv
from pathlib import Path

env_path = Path(__file__).parent / ".env"
load_dotenv(env_path)

from infrastructure.web_client import get_web_client

app = FastAPI(title="Multi-Agente de Autos")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Consulta(BaseModel):
    marca: Optional[str] = ""
    modelo: Optional[str] = ""
    anio: Optional[str] = ""
    presupuesto: Optional[str] = ""
    auto1: Optional[str] = ""
    auto2: Optional[str] = ""

@app.get("/")
def root():
    return {
        "service": "Multi-Agente de Autos",
        "version": "2.0.0",
        "endpoints": [
            "/agente/precios?marca=toyota&modelo=corolla",
            "/agente/comparar?auto1=toyota&auto2=honda", 
            "/agente/recomendaciones?presupuesto=500000",
            "/agente/orquestador?texto=cuanto+cuesta+toyota"
        ]
    }

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/agente/precios")
def agente_precios(marca: str = "", modelo: str = "", anio: str = ""):
    web = get_web_client()
    resultado = web.buscar_precios_auto(marca, modelo, anio)
    return {
        "agente": "precios",
        "marca": marca,
        "modelo": modelo,
        "precios_nuevos": resultado.get("precios_nuevos", [])[:5],
        "precios_usados": resultado.get("precios_usados", [])[:5],
        "especificaciones": resultado.get("especificaciones", {}),
        "fuente": "https://serpapi.com/search"
    }

@app.get("/agente/comparar")
def agente_comparar(auto1: str = "", auto2: str = ""):
    web = get_web_client()
    
    parts1 = auto1.split() if auto1 else []
    parts2 = auto2.split() if auto2 else []
    
    marca1 = parts1[0] if parts1 else ""
    modelo1 = " ".join(parts1[1:]) if len(parts1) > 1 else ""
    marca2 = parts2[0] if parts2 else ""
    modelo2 = " ".join(parts2[1:]) if len(parts2) > 1 else ""
    
    r1 = web.buscar_precios_auto(marca1, modelo1, "")
    r2 = web.buscar_precios_auto(marca2, modelo2, "")
    
    return {
        "agente": "comparar",
        "auto1": {"nombre": auto1, "precios": r1.get("precios_nuevos", [])[:3]},
        "auto2": {"nombre": auto2, "precios": r2.get("precios_nuevos", [])[:3]},
        "fuente": "https://serpapi.com/search"
    }

@app.get("/agente/recomendaciones")
def agente_recomendaciones(presupuesto: str = "500000"):
    web = get_web_client()
    recomendaciones = []
    
    marcas = ["toyota", "honda", "nissan", "ford", "chevrolet", "kia", "hyundai"]
    
    for marca in marcas:
        resultado = web.buscar_precios_auto(marca, "", "")
        precios = resultado.get("precios_nuevos", [])
        
        if precios:
            try:
                p = precios[0].get("precio", "$0").replace("$", "").replace(",", "").replace(" MXN", "").replace(" ", "")
                if p.isdigit() and int(p) <= int(presupuesto):
                    recomendaciones.append({
                        "marca": marca,
                        "precio": precios[0].get("precio"),
                        "fuente": precios[0].get("fuente")
                    })
            except:
                pass
    
    return {
        "agente": "recomendaciones",
        "presupuesto": presupuesto,
        "recomendaciones": recomendaciones[:5],
        "fuente": "https://serpapi.com/search"
    }

@app.get("/agente/orquestador")
def agente_orquestador(texto: str = ""):
    t = texto.lower()
    
    if "compar" in t:
        partes = t.replace("vs", " ").replace("versus", " ").split()
        if len(partes) >= 2:
            auto1 = partes[0]
            auto2 = partes[1]
            return agente_comparar(auto1, auto2)
    
    if "recomiend" in t or "presupuesto" in t or "presupuest" in t:
        import re
        nums = re.findall(r'\d+', texto)
        presupuesto = nums[0] if nums else "500000"
        return agente_recomendaciones(presupuesto)
    
    # Extraer marca y modelo
    marcas = ["toyota", "honda", "nissan", "ford", "chevrolet", "kia", "hyundai", "mazda", "bmw"]
    marca = ""
    for m in marcas:
        if m in t:
            marca = m
            break
    
    import re
    nums = re.findall(r'\d{4}', texto)
    anio = nums[0] if nums else ""
    
    return agente_precios(marca, "", anio)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
