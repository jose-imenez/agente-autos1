"""
Infraestructura - Servicio de Historial en memoria.

Implementa el almacenamiento de decisiones del usuario.
Para producción, esto debería usar una base de datos.
"""

from datetime import datetime

from domain.dtos.dtos import DecisionDTO, HistorialDecisionDTO
from domain.interfaces.ports import IHistorialService


class HistorialService(IHistorialService):
    """
    Servicio de gestión de historial de decisiones.
    
    Implementación en memoria (para desarrollo/producción usar Redis/DB).
    thread-safe mediante locking.
    """
    
    def __init__(self):
        self._historial: list[HistorialDecisionDTO] = []
        self._lock = __import__('threading').Lock()
    
    def guardar_decision(self, problema: str, decision: DecisionDTO) -> None:
        """
        Guarda una decisión en el historial.
        
        Args:
            problema: Texto del problema analizado
            decision: DTO con la decisión del usuario
        """
        with self._lock:
            entrada = HistorialDecisionDTO(
                problema=problema,
                solucion_seleccionada=f"Opción {decision.indice_seleccionado + 1}",
                timestamp=datetime.now(),
                notas=decision.notas,
            )
            self._historial.insert(0, entrada)
            
            # Mantener solo los últimos 50 registros
            if len(self._historial) > 50:
                self._historial = self._historial[:50]
    
    def obtener_historial(self, limite: int = 10) -> list[HistorialDecisionDTO]:
        """
        Obtiene el historial de decisiones.
        
        Args:
            limite: Número máximo de registros a retornar
            
        Returns:
            Lista de decisiones ordenadas por fecha (más reciente primero)
        """
        with self._lock:
            return self._historial[:limite].copy()
    
    def limpiar_historial(self) -> None:
        """Limpia todo el historial de decisiones."""
        with self._lock:
            self._historial.clear()
