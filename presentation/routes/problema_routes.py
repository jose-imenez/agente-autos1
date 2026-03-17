"""
Presentation Layer - Rutas API.

Define los endpoints de la API RESTful con soporte para múltiples sesiones.
"""

from typing import Annotated, Optional
from datetime import datetime

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from pydantic import Field

from application.use_cases.analisis_use_cases import AnalizarProblemaUseCase
from domain.dtos.dtos import (
    ProblemaDTO,
    ResultadoAnalisisDTO,
    DecisionDTO,
    HistorialDecisionDTO,
)
from domain.entities.entities import ResultadoAnalisis
from presentation.controllers.problema_controller import ProblemaController
from infrastructure.logging.structured_logging import api_logger
from infrastructure.services.sesion_service import SesionService, SesionAnalisis
from infrastructure.services.llm_service import get_llm_service
from infrastructure.services.skills_loader import get_skills_loader
from infrastructure.services.skills_service import skills_service


# Instancias globales (en producción usar Dependency Injection)
_analizar_use_case: AnalizarProblemaUseCase = None
_historial_use_case: AnalizarProblemaUseCase = None
_sesion_service: SesionService = None


def set_use_cases(
    analizar: AnalizarProblemaUseCase,
    historial: AnalizarProblemaUseCase,
) -> None:
    """Inyecta los casos de uso en las rutas."""
    global _analizar_use_case, _historial_use_case, _sesion_service
    _analizar_use_case = analizar
    _historial_use_case = historial
    _sesion_service = SesionService(max_sesiones=10)


def get_sesion_service() -> SesionService:
    """Obtiene el servicio de sesiones."""
    global _sesion_service
    return _sesion_service


router = APIRouter(prefix="/api/v1", tags=["problemas"])
_controller = ProblemaController()


# ====================
# Endpoints Web
# ====================


@router.get("/", response_class=HTMLResponse)
async def home(request: Request) -> HTMLResponse:
    """Página principal de la aplicación."""
    api_logger.info("Acceso a página principal")
    return _controller.home(request)


# ====================
# Endpoints de Sesiones
# ====================


@router.post("/sesiones", summary="Crear sesión")
async def crear_sesion(nombre: Optional[str] = None) -> dict:
    """Crea una nueva sesión de análisis."""
    sesion = _sesion_service.crear_sesion(nombre)
    api_logger.info("Sesión creada", sesion_id=sesion.id)
    return {
        "id": sesion.id,
        "nombre": sesion.nombre,
        "created_at": sesion.created_at.isoformat(),
    }


@router.get("/sesiones", summary="Listar sesiones")
async def listar_sesiones() -> list[dict]:
    """Lista todas las sesiones."""
    sesiones = _sesion_service.listar_sesiones()
    return [
        {
            "id": s.id,
            "nombre": s.nombre,
            "problema_actual": s.problema_actual,
            "tiene_soluciones": len(s.soluciones) > 0,
            "created_at": s.created_at.isoformat(),
            "updated_at": s.updated_at.isoformat(),
        }
        for s in sesiones
    ]


@router.get("/sesiones/{sesion_id}", summary="Obtener sesión")
async def obtener_sesion(sesion_id: str) -> dict:
    """Obtiene una sesión específica."""
    sesion = _sesion_service.obtener_sesion(sesion_id)
    if not sesion:
        return {"error": "Sesión no encontrada"}, 404
    
    return {
        "id": sesion.id,
        "nombre": sesion.nombre,
        "problema_actual": sesion.problema_actual,
        "soluciones": [
            {
                "titulo": s.titulo,
                "descripcion": s.descripcion,
                "complejidad": s.complejidad,
                "categoria": s.categoria,
            }
            for s in sesion.soluciones
        ],
        "seleccion_usuario": sesion.seleccion_usuario,
        "created_at": sesion.created_at.isoformat(),
        "updated_at": sesion.updated_at.isoformat(),
    }


@router.put("/sesiones/{sesion_id}", summary="Renombrar sesión")
async def renombrar_sesion(sesion_id: str, nombre: str) -> dict:
    """Renombra una sesión."""
    resultado = _sesion_service.renombrar_sesion(sesion_id, nombre)
    if resultado:
        return {"status": "ok", "mensaje": "Sesión renombrada"}
    return {"error": "Sesión no encontrada"}, 404


@router.delete("/sesiones/{sesion_id}", summary="Eliminar sesión")
async def eliminar_sesion(sesion_id: str) -> dict:
    """Elimina una sesión."""
    resultado = _sesion_service.eliminar_sesion(sesion_id)
    if resultado:
        return {"status": "ok", "mensaje": "Sesión eliminada"}
    return {"error": "Sesión no encontrada"}, 404


# ====================
# Endpoints de Análisis
# ====================


@router.post(
    "/analizar",
    response_model=ResultadoAnalisisDTO,
    summary="Analizar problema",
    description="Analiza un problema y genera múltiples soluciones detalladas"
)
async def analizar_problema(
    sesion_id: Optional[str] = None,
    problema: Optional[ProblemaDTO] = None,
    texto: Optional[str] = None,
) -> ResultadoAnalisisDTO:
    """
    Analiza un problema y retorna múltiples soluciones.
    
    IMPORTANTE: Este endpoint solo acepta consultas sobre COCHES y sus precios.
    Cualquier otra consulta será rechazada.
    """
    # Procesar texto del problema
    texto_problema = texto
    if problema:
        texto_problema = problema.texto
    
    if not texto_problema:
        return {"error": "Se requiere texto o problema"}, 400
    
    # DETECCIÓN: Si no es sobre coches, rechazar inmediatamente
    loader = get_skills_loader()
    if not loader._es_query_coches(texto_problema):
        api_logger.info("Query rechazada - no es sobre coches", query=texto_problema[:50])
        
        # Obtener skill de no disponible
        result = loader.ejecutar_skill_auto(texto_problema)
        
        return ResultadoAnalisisDTO(
            problema_original=texto_problema,
            timestamp=datetime.now(),
            soluciones=[],
            razonamiento=result.get('instrucciones', 'Solo busco autos y precios.'),
            preguntas_aclaratorias=[],
        )
    
    # Es sobre coches - usar skills para generar respuesta
    api_logger.info("Query sobre coches - usando skills", query=texto_problema[:50])
    
    # Obtener skill relevante
    result = loader.ejecutar_skill_auto(texto_problema)
    
    # Usar LLM para generar respuesta basada en la skill
    llm = get_llm_service()
    
    # Construir prompt con la skill
    skill_name = result.get('skill', 'buscar_coche')
    skill_content = result.get('instrucciones', '')
    
    prompt = f"""Usa las siguientes instrucciones para responder:

{skill_content}

---

Usuario pregunta: {texto_problema}

Responde de manera natural y amigable siguiendo las instrucciones de arriba. Sé específico con precios, características y versiones si aplica."""
    
    respuesta = llm.generar(
        prompt=prompt,
        system_prompt="Eres un experto en autos y precios de vehículos. Respondes de manera amigable, detallada y útil.",
        temperature=0.7
    )
    
    # Si la respuesta indica error de API, usar contenido directo de la skill
    if "API Key no configurada" in respuesta.contenido or "Error al generar" in respuesta.contenido:
        # Generar respuesta directa basada en la skill
        razonamiento = _generar_respuesta_skill(texto_problema, skill_name, result.get('instrucciones', ''))
    else:
        razonamiento = respuesta.contenido
    
    return ResultadoAnalisisDTO(
        problema_original=texto_problema,
        timestamp=datetime.now(),
        soluciones=[],
        razonamiento=razonamiento,
        preguntas_aclaratorias=[],
    )


def _generar_respuesta_skill(query: str, skill_name: str, skill_content: str) -> str:
    """Genera una respuesta directa basada en la skill sin usar LLM."""
    
    query_lower = query.lower()
    
    if skill_name == "no_disponible":
        return skill_content
    
    # Para otras skills, generar respuesta basada en la query
    import re
    
    # Extraer marca del query
    marcas = ["toyota", "honda", "ford", "bmw", "mercedes", "audi", "chevrolet", "nissan", 
              "mazda", "volkswagen", "kia", "hyundai", "porsche", "tesla", "jeep", "subaru", "lexus"]
    marca_encontrada = None
    for marca in marcas:
        if marca in query_lower:
            marca_encontrada = marca.capitalize()
            break
    
    if not marca_encontrada:
        # Buscar cualquier palabra que parezca marca
        palabras = query_lower.split()
        for palabra in palabras:
            if len(palabra) > 3 and palabra not in ["cuánto", "cuenta", "precio", "cuesta", "dame", "busca"]:
                marca_encontrada = palabra.capitalize()
                break
    
    if not marca_encontrada:
        marca_encontrada = "el auto"
    
    # Generar respuesta según la skill
    if skill_name == "obtener_precios" or skill_name == "buscar_coche":
        return f"""## {marca_encontrada}

¡Encontré información sobre {marca_encontrada}!

### Precio de lista (aproximado)
Los precios varían según el modelo y versión:
- **Modelo base:** desde $20,000 USD
- **Versión intermedia:** $25,000 - $35,000 USD  
- **Top de línea:** $40,000+ USD

### Modelos populares
- Sedanes compactos
- SUVs medianos
- Trucks pickup

### ¿Qué modelo específico te interesa?

 Puedo darte información más precisa si me dices:
- ¿Qué modelo de {marca_encontrada}?
- ¿Año nuevo o usado?
- ¿Tu presupuesto?

---

**También puedo mostrarte otros colores o versiones si me dices cuáles!**"""
    
    elif skill_name == "comparar_coches":
        return f"""## Comparación de vehículos

Para hacer una comparación necesito saber **qué dos autos** quieres comparar.

Ejemplos:
- "Compara {marca_encontrada} vs Honda"
- "Toyota vs Ford"
- "BMW vs Mercedes"

**¿Cuáles dos autos quieres comparar?**"""
    
    return skill_content


# ====================
# Endpoints de Decisión
# ====================


@router.post(
    "/decision",
    summary="Guardar decisión",
    description="Guarda la solución seleccionada por el usuario"
)
async def guardar_decision(
    sesion_id: Optional[str] = None,
    indice_seleccionado: Optional[int] = None,
    request_data: Optional[dict] = None,
) -> dict:
    """Guarda la decisión del usuario en la sesión."""
    # Extraer datos
    if request_data:
        sesion_id = request_data.get("sesion_id", sesion_id)
        indice_seleccionado = request_data.get("indice_seleccionado", indice_seleccionado)
    
    if sesion_id and indice_seleccionado is not None:
        _sesion_service.actualizar_sesion(
            sesion_id,
            seleccion=indice_seleccionado,
        )
        api_logger.info(
            "Decisión guardada en sesión",
            sesion_id=sesion_id,
            solucion=indice_seleccionado,
        )
    
    # También guardar en historial global
    if request_data:
        problema = request_data.get("problema", "")
        decision = DecisionDTO(
            indice_seleccionado=indice_seleccionado or 0,
            notas=request_data.get("notas"),
        )
        _historial_use_case.guardar_decision(problema, decision)
    
    return {"status": "ok", "message": "Decisión guardada"}


@router.get(
    "/historial",
    response_model=list[HistorialDecisionDTO],
    summary="Obtener historial",
    description="Retorna el historial de decisiones del usuario"
)
async def obtener_historial(
    limite: Annotated[int, Field(ge=1, le=50)] = 10,
) -> list[HistorialDecisionDTO]:
    """Obtiene el historial de decisiones."""
    api_logger.info("Solicitud de historial", limite=limite)
    return _historial_use_case.obtener_historial(limite)


@router.delete(
    "/historial",
    summary="Limpiar historial",
    description="Elimina todo el historial de decisiones"
)
async def limpiar_historial() -> dict:
    """Limpia el historial de decisiones."""
    api_logger.info("Limpiando historial")
    _historial_use_case.limpiar_historial()
    return {"status": "ok", "message": "Historial limpiado"}


# ====================
# Health Check
# ====================


@router.get("/health")
async def health_check() -> dict:
    """Endpoint de verificación de salud de la API."""
    return {
        "status": "healthy",
        "service": "agente-ia-api",
        "version": "1.0.0",
    }


# ====================
# Endpoints de Skills
# ====================


@router.get("/skills/saludo", summary="Obtener saludo")
async def obtener_saludo() -> dict:
    """Retorna un mensaje de bienvenida del asistente."""
    api_logger.info("Solicitud de saludo")
    return skills_service.obtener_saludo()


@router.post("/skills/despedida", summary="Obtener despedida")
async def obtener_despedida(sesion_id: Optional[str] = None) -> dict:
    """Retorna un mensaje de despedida del asistente."""
    api_logger.info("Solicitud de despedida", sesion_id=sesion_id)
    return skills_service.registrar_fin_sesion(sesion_id)


# ====================
# Endpoints de Skills (nuevo sistema)
# ====================


@router.get("/skills", summary="Listar skills")
async def listar_skills() -> list:
    """Lista todas las skills disponibles."""
    api_logger.info("Solicitud de lista de skills")
    loader = get_skills_loader()
    return loader.listar_skills()


@router.get("/skills/{nombre_skill}", summary="Obtener skill")
async def obtener_skill(nombre_skill: str) -> dict:
    """Obtiene los detalles de una skill específica."""
    api_logger.info("Solicitud de skill", skill=nombre_skill)
    loader = get_skills_loader()
    skill = loader.obtener_skill(nombre_skill)
    
    if not skill:
        return {"error": f"Skill '{nombre_skill}' no encontrada"}
    
    return {
        "nombre": skill.nombre,
        "descripcion": skill.descripcion,
        "proveedor": skill.proveedor,
        "contenido": skill.contenido[:500] + "..." if len(skill.contenido) > 500 else skill.contenido,
    }


@router.post("/skills/buscar", summary="Buscar skills")
async def buscar_skills(query: str) -> list:
    """Busca skills por nombre o descripción."""
    api_logger.info("Búsqueda de skills", query=query)
    loader = get_skills_loader()
    return loader.buscar_skills(query)


@router.post("/skills/ejecutar", summary="Ejecutar skill")
async def ejecutar_skill(data: dict) -> dict:
    """Ejecuta una skill con el contexto dado."""
    nombre_skill = data.get("nombre_skill", "")
    contexto = data.get("contexto", "")
    
    api_logger.info("Ejecución de skill", skill=nombre_skill)
    loader = get_skills_loader()
    return loader.ejecutar_skill(nombre_skill, contexto)


# ====================
# Endpoints de LLM
# ====================


@router.get("/llm/status", summary="Estado del LLM")
async def estado_llm() -> dict:
    """Retorna el estado de la configuración del LLM."""
    llm = get_llm_service()
    return {
        "configurado": bool(llm.api_key and llm.api_key != "TU_API_KEY"),
        "proveedor": llm.provider,
        "modelo": llm.model,
    }


@router.post("/llm/generar", summary="Generar respuesta LLM")
async def generar_respuesta(data: dict) -> dict:
    """Genera una respuesta usando el LLM."""
    prompt = data.get("prompt", "")
    system_prompt = data.get("system_prompt")
    contexto = data.get("contexto")
    
    api_logger.info("Solicitud de generación LLM", prompt=prompt[:50])
    llm = get_llm_service()
    
    response = llm.generar(
        prompt=prompt,
        system_prompt=system_prompt,
        contexto=contexto,
    )
    
    return {
        "contenido": response.contenido,
        "modelo": response.modelo,
        "uso_tokens": response.uso_tokens,
    }


@router.post("/llm/asesor", summary="Generar respuesta de asesor")
async def generar_respuesta_asesor(data: dict) -> dict:
    """Genera una respuesta de asesor estratégico usando el LLM."""
    problema = data.get("problema", "")
    analisis_contextual = data.get("analisis_contextual")
    soluciones = data.get("soluciones")
    
    api_logger.info("Solicitud de asesor LLM", problema=problema[:50])
    llm = get_llm_service()
    
    respuesta = llm.generar_respuesta_asesor(
        problema=problema,
        analisis_contextual=analisis_contextual,
        soluciones=soluciones,
    )
    
    return {
        "respuesta": respuesta,
    }


# ====================
# Webhook para n8n
# ====================

from infrastructure.web_client import get_web_client


@router.get("/webhook/n8n")
async def webhook_n8n_get(marca: str = "", modelo: str = "", anio: str = ""):
    """Webhook GET para n8n - Ejemplo: /api/v1/webhook/n8n?marca=toyota&modelo=corolla"""
    if not marca and not modelo:
        return {"error": "Se requiere marca o modelo", "ejemplo": "/api/v1/webhook/n8n?marca=toyota&modelo=corolla"}
    
    web_client = get_web_client()
    resultado = web_client.buscar_precios_auto(marca, modelo, anio)
    
    return {
        "status": "success",
        "marca": marca,
        "modelo": modelo,
        "anio": anio,
        "fuente": "https://serpapi.com/search",
        "precios_nuevos": resultado.get("precios_nuevos", []),
        "precios_usados": resultado.get("precios_usados", []),
        "especificaciones": resultado.get("especificaciones", {}),
    }


@router.post("/webhook/n8n")
async def webhook_n8n_post(data: dict):
    """Webhook POST para n8n - Body: {"marca": "toyota", "modelo": "corolla"}"""
    marca = data.get("marca", "")
    modelo = data.get("modelo", "")
    anio = data.get("anio", "")
    
    if not marca and not modelo:
        return {"error": "Se requiere marca o modelo"}
    
    web_client = get_web_client()
    resultado = web_client.buscar_precios_auto(marca, modelo, anio)
    
    return {
        "status": "success",
        "marca": marca,
        "modelo": modelo,
        "anio": anio,
        "fuente": "https://serpapi.com/search",
        "precios_nuevos": resultado.get("precios_nuevos", []),
        "precios_usados": resultado.get("precios_usados", []),
        "especificaciones": resultado.get("especificaciones", {}),
    }


# ====================
# Endpoint principal del agente
# ====================


@router.post("/agente", summary="Ejecutar agente de coches")
async def ejecutar_agente(data: dict) -> dict:
    """
    Endpoint principal del agente.
    
    Detecta automáticamente si la query es sobre coches y ejecuta
    la skill apropiada, o devuelve mensaje de error si no es sobre coches.
    """
    query = data.get("query", "")
    
    if not query:
        return {"error": "Se requiere una query"}
    
    api_logger.info("Ejecutando agente", query=query[:50])
    
    loader = get_skills_loader()
    result = loader.ejecutar_skill_auto(query)
    
    return result
