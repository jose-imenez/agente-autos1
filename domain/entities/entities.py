"""
Domain Layer - Entidades del núcleo del negocio.

Este módulo contiene las entidades fundamentales que representan
los conceptos del dominio de la aplicación.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


class ComplexityLevel(Enum):
    """Nivel de complejidad técnica de una solución."""
    BAJA = "baja"
    MEDIA = "media"
    ALTA = "alta"
    MUY_ALTA = "muy_alta"


class SolutionCategory(Enum):
    """Categorías de soluciones que puede generar el sistema."""
    ALIMENTACION = "alimentacion"
    REDES = "redes"
    DESARROLLO = "desarrollo"
    NEGOCIOS = "negocios"
    PERSONAL = "personal"
    TECNOLOGIA = "tecnologia"
    GENERAL = "general"


@dataclass
class Solucion:
    """
    Representa una solución alternativa generada para un problema.
    
    Attributes:
        titulo: Título identificador de la solución
        descripcion: Descripción detallada de la solución
        ventajas: Lista de ventajas de implementar esta solución
        desventajas: Lista de desventajas o riesgos
        complejidad: Nivel de complejidad técnica requerido
        categoria: Categoría a la que pertenece la solución
        recomendacion: Recomendación estratégica sobre cuándo usar esta solución
        tecnologias: Tecnologías o herramientas recomendadas (opcional)
    """
    titulo: str
    descripcion: str
    ventajas: list[str]
    desventajas: list[str]
    complejidad: ComplexityLevel
    categoria: SolutionCategory
    recomendacion: str
    tecnologias: list[str] = field(default_factory=list)


@dataclass
class ResultadoAnalisis:
    """
    Resultado completo del análisis de un problema.
    
    Attributes:
        problema_original: Texto original del problema analizado
        timestamp: Fecha y hora del análisis
        soluciones: Lista de soluciones alternativas generadas
        razonamiento: Explicación del proceso de análisis
        preguntas_aclaratorias: Preguntas si el problema es ambiguo
    """
    problema_original: str
    timestamp: datetime
    soluciones: list[Solucion]
    razonamiento: str
    preguntas_aclaratorias: list[str] = field(default_factory=list)


@dataclass  
class DecisionUsuario:
    """
    Registro de la decisión tomada por el usuario.
    
    Attributes:
        solucion_seleccionada: Solución elegida por el usuario
        timestamp: Cuándo se tomó la decisión
        notas: Notas opcionales del usuario
    """
    solucion_seleccionada: Solucion
    timestamp: datetime
    notas: Optional[str] = None


@dataclass
class Problema:
    """
    Entidad que representa el problema reportado por el usuario.
    
    Attributes:
        texto: Descripción textual del problema
        contexto: Contexto adicional proporcionado (opcional)
    """
    texto: str
    contexto: Optional[str] = None
