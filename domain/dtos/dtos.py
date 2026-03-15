"""
Capa de dominio - Data Transfer Objects (DTOs).

Los DTOs definen la estructura de datos que se transfiere entre capas,
permitiendo decoupling entre la lógica de dominio y las interfaces.
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime


class ProblemaDTO(BaseModel):
    """
    DTO para recibir un problema del cliente.
    
    Validation:
        - texto: Entre 5 y 500 caracteres
    """
    texto: str = Field(..., min_length=5, max_length=500, description="Descripción del problema")
    contexto: Optional[str] = Field(None, max_length=200, description="Contexto adicional")
    
    @field_validator('texto')
    @classmethod
    def texto_no_vacio(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("El texto no puede estar vacío")
        return v


class SolucionDTO(BaseModel):
    """
    DTO que representa una solución para el cliente.
    """
    titulo: str
    descripcion: str
    ventajas: list[str]
    desventajas: list[str]
    complejidad: str
    categoria: str
    recomendacion: str
    tecnologias: list[str] = []


class ResultadoAnalisisDTO(BaseModel):
    """
    DTO de respuesta para el análisis de problemas.
    """
    problema_original: str
    timestamp: datetime
    soluciones: list[SolucionDTO]
    razonamiento: str
    preguntas_aclaratorias: list[str] = []
    
    model_config = {"from_attributes": True}


class DecisionDTO(BaseModel):
    """DTO para registrar una decisión del usuario."""
    indice_seleccionado: int = Field(..., ge=0, description="Índice de la solución seleccionada")
    notas: Optional[str] = Field(None, max_length=500, description="Notas opcionales")


class HistorialDecisionDTO(BaseModel):
    """DTO para el historial de decisiones."""
    problema: str
    solucion_seleccionada: str
    timestamp: datetime
    notas: Optional[str] = None


class ErrorRespuestaDTO(BaseModel):
    """DTO estándar para respuestas de error."""
    error: str
    detalle: Optional[str] = None
    codigo: str
    timestamp: datetime = Field(default_factory=datetime.now)
