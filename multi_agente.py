"""
Multi-Agente con RAG y MCP para n8n
Arquitectura de agentes especializados
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from dotenv import load_dotenv
from pathlib import Path
import asyncio

# Cargar variables de entorno
env_path = Path(__file__).parent / ".env"
load_dotenv(env_path)

from infrastructure.web_client import get_web_client

# Crear app
app = FastAPI(
    title="Multi-Agente de Autos",
    description="Sistema Multi-Agente con RAG y MCP para n8n",
    version="2.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== MODELOS ====================

class ConsultaAuto(BaseModel):
    marca: Optional[str] = ""
    modelo: Optional[str] = ""
    anio: Optional[str] = ""
    presupuesto: Optional[str] = ""
    tipo: Optional[str] = ""  # sedan, suv, pickup, etc

class ConsultaComparar(BaseModel):
    auto1: str
    auto2: str

# ==================== AGENTES ESPECIALIZADOS ====================

class AgentePrecios:
    """Agente especializado en precios de autos"""
    
    async def ejecutar(self, consulta: ConsultaAuto) -> Dict:
        web = get_web_client()
        resultado = web.buscar_precios_auto(
            consulta.marca or "",
            consulta.modelo or "",
            consulta.anio or ""
        )
        
        return {
            "agente": "precios",
            "status": "success",
            "marca": consulta.marca,
            "modelo": consulta.modelo,
            "anio": consulta.anio,
            "precios_nuevos": resultado.get("precios_nuevos", [])[:5],
            "precios_usados": resultado.get("precios_usados", [])[:5],
            "especificaciones": resultado.get("especificaciones", {}),
            "fuente": "https://serpapi.com/search"
        }

class AgenteComparar:
    """Agente especializado en comparar autos"""
    
    async def ejecutar(self, consulta: ConsultaComparar) -> Dict:
        web = get_web_client()
        
        # Buscar ambos autos
        resultado1 = web.buscar_precios_auto(consulta.auto1.split()[0], " ".join(consulta.auto1.split()[1:]), "")
        resultado2 = web.buscar_precios_auto(consulta.auto2.split()[0], " ".join(consulta.auto2.split()[1:]), "")
        
        return {
            "agente": "comparar",
            "status": "success",
            "auto1": {
                "nombre": consulta.auto1,
                "precios": resultado1.get("precios_nuevos", [])[:3],
                "especificaciones": resultado1.get("especificaciones", {})
            },
            "auto2": {
                "nombre": consulta.auto2,
                "precios": resultado2.get("precios_nuevos", [])[:3],
                "especificaciones": resultado2.get("especificaciones", {})
            },
            "comparacion": {
                "recomendacion": "Compara precios y especificaciones antes de decidir"
            },
            "fuente": "https://serpapi.com/search"
        }

class AgenteRecomendaciones:
    """Agente especializado en recomendar autos según presupuesto"""
    
    async def ejecutar(self, consulta: ConsultaAuto) -> Dict:
        web = get_web_client()
        
        recomendaciones = []
        
        # Buscar autos en el presupuesto indicado
        presupuesto = consulta.presupuesto or "500000"
        
        # Buscar diferentes marcas
        marcas = ["toyota", "honda", "nissan", "ford", "chevrolet", "kia", "hyundai"]
        
        for marca in marcas[:5]:
            resultado = web.buscar_precios_auto(marca, "", "")
            precios = resultado.get("precios_nuevos", [])
            
            if precios:
                try:
                    precio = float(precios[0].get("precio", "0").replace("$", "").replace(",", "").replace(" MXN", ""))
                    if precio <= float(presupuesto):
                        recomendaciones.append({
                            "marca": marca,
                            "modelo": resultado.get("precios_nuevos", [{}])[0].get("version", "Varios"),
                            "precio": precios[0].get("precio"),
                            "fuente": precios[0].get("fuente")
                        })
                except:
                    pass
        
        return {
            "agente": "recomendaciones",
            "status": "success",
            "presupuesto": presupuesto,
            "recomendaciones": recomendaciones[:5],
            "mensaje": "Autos recomendados dentro de tu presupuesto",
            "fuente": "https://serpapi.com/search"
        }

class AgenteEspecificaciones:
    """Agente especializado en especificaciones técnicas"""
    
    async def ejecutar(self, consulta: ConsultaAuto) -> Dict:
        web = get_web_client()
        
        # Buscar especificaciones
        resultado = web.buscar_precios_auto(
            consulta.marca or "",
            consulta.modelo or "",
            consulta.anio or ""
        )
        
        specs = resultado.get("especificaciones", {})
        
        return {
            "agente": "especificaciones",
            "status": "success",
            "marca": consulta.marca,
            "modelo": consulta.modelo,
            "anio": consulta.anio,
            "especificaciones": {
                "motor": specs.get("motor", "Consultar"),
                "potencia": specs.get("potencia", "Consultar"),
                "consumo": specs.get("consumo", "Consultar")
            },
            "info_adicional": "Para más especificaciones, visita el concesionario",
            "fuente": "https://serpapi.com/search"
        }

# ==================== AGENTE ORQUESTADOR (MCP) ====================

class AgenteOrquestador:
    """
    Agente principal que coordina los demás agentes (Multi-Agent Orchestrator)
    Implementa patrón MCP (Model Context Protocol)
    """
    
    def __init__(self):
        self.agentes = {
            "precios": AgentePrecios(),
            "comparar": AgenteComparar(),
            "recomendaciones": AgenteRecomendaciones(),
            "especificaciones": AgenteEspecificaciones()
        }
    
    async def ejecutar(self, texto: str) -> Dict:
        """Analiza el texto y determina qué agente usar"""
        
        texto_lower = texto.lower()
        
        # Determinar tipo de consulta
        if "compar" in texto_lower:
            # Extraer autos a comparar
            partes = texto_lower.replace("vs", ",").replace("versus", ",").split(",")
            auto1 = partes[0].strip() if len(partes) > 0 else ""
            auto2 = partes[1].strip() if len(partes) > 1 else ""
            
            return await self.agentes["comparar"].ejecutar(
                ConsultaComparar(auto1=auto1, auto2=auto2)
            )
        
        elif "recomiend" in texto_lower or "presupuesto" in texto_lower:
            # Extraer presupuesto
            presupuesto = ""
            import re
            match = re.search(r'(\d+)', texto)
            if match:
                presupuesto = match.group(1)
            
            # Extraer marca si existe
            marcas = ["toyota", "honda", "nissan", "ford", "chevrolet", "kia", "hyundai", "mazda", "volkswagen"]
            marca = ""
            for m in marcas:
                if m in texto_lower:
                    marca = m
                    break
            
            return await self.agentes["recomendaciones"].ejecutar(
                ConsultaAuto(marca=marca, presupuesto=presupuesto)
            )
        
        elif "spec" in texto_lower or "caracter" in texto_lower or "motor" in texto_lower:
            # Extraer auto
            return await self.agentes["especificaciones"].ejecutar(
                ConsultaAuto(marca=self._extraer_marca(texto_lower), 
                           modelo=self._extraer_modelo(texto_lower),
                           anio=self._extraer_anio(texto))
        
        else:
            # Por defecto, agente de precios
            return await self.agentes["precios"].ejecutar(
                ConsultaAuto(marca=self._extraer_marca(texto_lower),
                           modelo=self._extraer_modelo(texto_lower),
                           anio=self._extraer_anio(texto))
    
    def _extraer_marca(self, texto: str) -> str:
        marcas = ["toyota", "honda", "nissan", "ford", "chevrolet", "kia", "hyundai", "mazda", "volkswagen", "bmw", "mercedes", "audi", "porsche", "tesla", "jeep"]
        for m in marcas:
            if m in texto:
                return m
        return ""
    
    def _extraer_modelo(self, texto: str) -> str:
        modelos = ["corolla", "civic", "accord", "corolla", "camry", "mustang", "camaro", "sentra", "altima", " civic", "jetta", "polo", "gol", "sail", "beat", "spark", "march", "versa", "note", "kick", "kicks", "hr-v", "cr-v", "rav4", "hilux", "frontier", "tacoma", "silverado", "sierra", "colorado", "bravos", "trax", "equinox", "traverse", "blazer", "esport", "sorento", "sportage", "telluride", "palisade", "santa fe", "tucson", "creta", "ioniq", "kona", "auris", "prius", "supra", "86", "brz", "wrx", "stinger", "niro", "optima", "k5", "stinger", "escalade", "xt5", "xt6", "navigator", "expedition", " Yukon", "tahoe", "suburban"]
        for m in modelos:
            if m in texto:
                return m
        return ""
    
    def _extraer_anio(self, texto: str) -> str:
        import re
        match = re.search(r'\b(202[0-9]|201[0-9])\b', texto)
        return match.group(1) if match else "2024"

# Instancias globales
agente_orquestador = AgenteOrquestador()

# ==================== ENDPOINTS ====================

@app.get("/")
def root():
    return {
        "service": "Multi-Agente de Autos con RAG y MCP",
        "version": "2.0.0",
        "agentes": {
            "/agente/precios": "Consulta precios de un auto",
            "/agente/comparar": "Compara dos autos",
            "/agente/recomendaciones": "Recomienda autos según presupuesto",
            "/agente/especificaciones": "Especificaciones técnicas",
            "/agente/orquestador": "Agente principal (auto-detecta)"
        },
        "ejemplo": {
            "precios": "/agente/precios?marca=toyota&modelo=corolla",
            "comparar": "/agente/comparar?auto1=toyota+corolla&auto2=honda+civic",
            "recomendaciones": "/agente/recomendaciones?presupuesto=500000",
            "orquestador": "/agente/orquestador?texto=cuanto+cuesta+el+toyota+corolla+2024"
        }
    }

@app.get("/health")
def health():
    return {"status": "healthy"}

# Agente de Precios
@app.get("/agente/precios")
async def agente_precios(
    marca: str = "", 
    modelo: str = "", 
    anio: str = ""
):
    resultado = await AgentePrecios().ejecutar(ConsultaAuto(marca=marca, modelo=modelo, anio=anio))
    return resultado

# Agente de Comparar
@app.get("/agente/comparar")
async def agente_comparar(auto1: str = "", auto2: str = ""):
    resultado = await AgenteComparar().ejecutar(ConsultaComparar(auto1=auto1, auto2=auto2))
    return resultado

# Agente de Recomendaciones
@app.get("/agente/recomendaciones")
async def agente_recomendaciones(presupuesto: str = "", marca: str = ""):
    resultado = await AgenteRecomendaciones().ejecutar(ConsultaAuto(presupuesto=presupuesto, marca=marca))
    return resultado

# Agente de Especificaciones
@app.get("/agente/especificaciones")
async def agente_especificaciones(marca: str = "", modelo: str = "", anio: str = ""):
    resultado = await AgenteEspecificaciones().ejecutar(ConsultaAuto(marca=marca, modelo=modelo, anio=anio))
    return resultado

# Agente Orquestador (MCP)
@app.get("/agente/orquestador")
async def agente_orquestador(texto: str = ""):
    if not texto:
        return {"error": "Se requiere parámetro 'texto'"}
    resultado = await agente_orquestador.ejecutar(texto)
    return resultado

# MCP Protocol Endpoint
@app.post("/mcp/ejecutar")
async def mcp_ejecutar(request: dict):
    """
    Endpoint MCP (Model Context Protocol)
    Ejecuta cualquier agente basado en el contexto
    """
    accion = request.get("accion", "")
    parametros = request.get("parametros", {})
    
    if accion == "precios":
        return await AgentePrecios().ejecutar(ConsultaAuto(**parametros))
    elif accion == "comparar":
        return await AgenteComparar().ejecutar(ConsultaComparar(**parametros))
    elif accion == "recomendaciones":
        return await AgenteRecomendaciones().ejecutar(ConsultaAuto(**parametros))
    elif accion == "especificaciones":
        return await AgenteEspecificaciones().ejecutar(ConsultaAuto(**parametros))
    else:
        # Usar orquestador
        return await agente_orquestador.ejecutar(parametros.get("texto", ""))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
