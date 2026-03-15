"""
Domain Layer - Interfaces (Puertos).

Define los contratos que deben implementar los servicios de infraestructura.
Siguiendo el patrón de Puertos y Adaptadores (Hexagonal Architecture).
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional

from domain.entities.entities import ResultadoAnalisis, Problema, Solucion
from domain.dtos.dtos import DecisionDTO, HistorialDecisionDTO


class IAnalizadorService(ABC):
    """
    Puerto para el servicio de análisis de problemas.
    
    Define la interfaz que debe implementar cualquier analizador
    de problemas (actualmente el servicio de IA).
    """
    
    @abstractmethod
    def analizar(
        self, 
        problema: Problema,
        soluciones_previas: Optional[list[Solucion]] = None
    ) -> ResultadoAnalisis:
        """
        Analiza un problema y genera soluciones alternativas.
        
        Args:
            problema: Entidad problema a analizar
            soluciones_previas: Lista de soluciones ya generadas en sesiones anteriores
            
        Returns:
            ResultadoAnalisis con las soluciones generadas (sin duplicados)
        """
        pass


class IHistorialService(ABC):
    """
    Puerto para el servicio de gestión de historial.
    
    Define la interfaz para persistir y recuperar decisiones
    del usuario.
    """
    
    @abstractmethod
    def guardar_decision(self, problema: str, decision: DecisionDTO) -> None:
        """Guarda una decisión del usuario."""
        pass
    
    @abstractmethod
    def obtener_historial(self, limite: int = 10) -> list[HistorialDecisionDTO]:
        """Obtiene el historial de decisiones."""
        pass
    
    @abstractmethod
    def limpiar_historial(self) -> None:
        """Limpia todo el historial."""
        pass


class IProveedorLogger(ABC):
    """
    Puerto para servicios de logging.
    
    Permite inyectar diferentes implementaciones de logging.
    """
    
    @abstractmethod
    def info(self, mensaje: str, **kwargs) -> None:
        pass
    
    @abstractmethod
    def warning(self, mensaje: str, **kwargs) -> None:
        pass
    
    @abstractmethod
    def error(self, mensaje: str, exc: Exception | None = None, **kwargs) -> None:
        pass
    
    @abstractmethod
    def debug(self, mensaje: str, **kwargs) -> None:
        pass
