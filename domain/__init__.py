"""
Domain Layer - Exports.

Exporta las entidades, DTOs e interfaces del dominio.
"""

from domain.entities.entities import (
    Problema,
    Solucion,
    ResultadoAnalisis,
    DecisionUsuario,
    ComplexityLevel,
    SolutionCategory,
)

from domain.dtos.dtos import (
    ProblemaDTO,
    SolucionDTO,
    ResultadoAnalisisDTO,
    DecisionDTO,
    HistorialDecisionDTO,
    ErrorRespuestaDTO,
)

from domain.interfaces.ports import (
    IAnalizadorService,
    IHistorialService,
    IProveedorLogger,
)

__all__ = [
    # Entidades
    "Problema",
    "Solucion", 
    "ResultadoAnalisis",
    "DecisionUsuario",
    "ComplexityLevel",
    "SolutionCategory",
    # DTOs
    "ProblemaDTO",
    "SolucionDTO", 
    "ResultadoAnalisisDTO",
    "DecisionDTO",
    "HistorialDecisionDTO",
    "ErrorRespuestaDTO",
    # Puertos
    "IAnalizadorService",
    "IHistorialService",
    "IProveedorLogger",
]
