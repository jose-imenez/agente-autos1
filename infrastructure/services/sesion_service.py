"""
Infraestructura - Servicio de Gestión de Sesiones.

Maneja múltiples sesiones de análisis independientes.
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from domain.dtos.dtos import ProblemaDTO, SolucionDTO


@dataclass
class SesionAnalisis:
    """Representa una sesión de análisis."""
    id: str
    nombre: str
    problema_actual: Optional[str] = None
    soluciones: list[SolucionDTO] = field(default_factory=list)
    seleccion_usuario: Optional[int] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


class SesionService:
    """
    Servicio de gestión de sesiones múltiples.
    
    Permite crear, eliminar y gestionar múltiples sesiones
    de análisis independientes.
    """
    
    def __init__(self, max_sesiones: int = 10):
        self._sesiones: dict[str, SesionAnalisis] = {}
        self._max_sesiones = max_sesiones
    
    def crear_sesion(self, nombre: Optional[str] = None) -> SesionAnalisis:
        """Crea una nueva sesión."""
        # Limpiar sesiones antiguas si llegamos al límite
        if len(self._sesiones) >= self._max_sesiones:
            sesiones_ord = sorted(
                self._sesiones.values(),
                key=lambda s: s.updated_at
            )
            for sesion in sesiones_ord[:len(self._sesiones) - self._max_sesiones + 1]:
                del self._sesiones[sesion.id]
        
        id_sesion = str(uuid.uuid4())
        nombre_sesion = nombre or f"Análisis {len(self._sesiones) + 1}"
        
        sesion = SesionAnalisis(
            id=id_sesion,
            nombre=nombre_sesion,
        )
        
        self._sesiones[id_sesion] = sesion
        return sesion
    
    def obtener_sesion(self, id_sesion: str) -> Optional[SesionAnalisis]:
        """Obtiene una sesión por su ID."""
        return self._sesiones.get(id_sesion)
    
    def listar_sesiones(self) -> list[SesionAnalisis]:
        """Lista todas las sesiones ordenadas por actualización."""
        return sorted(
            self._sesiones.values(),
            key=lambda s: s.updated_at,
            reverse=True
        )
    
    def actualizar_sesion(
        self,
        id_sesion: str,
        problema: Optional[str] = None,
        soluciones: Optional[list[SolucionDTO]] = None,
        seleccion: Optional[int] = None,
    ) -> Optional[SesionAnalisis]:
        """Actualiza una sesión con nuevos datos."""
        sesion = self._sesiones.get(id_sesion)
        if not sesion:
            return None
        
        if problema is not None:
            sesion.problema_actual = problema
        if soluciones is not None:
            sesion.soluciones = soluciones
        if seleccion is not None:
            sesion.seleccion_usuario = seleccion
        
        sesion.updated_at = datetime.now()
        return sesion
    
    def renombrar_sesion(self, id_sesion: str, nuevo_nombre: str) -> bool:
        """Renombra una sesión."""
        sesion = self._sesiones.get(id_sesion)
        if sesion:
            sesion.nombre = nuevo_nombre
            sesion.updated_at = datetime.now()
            return True
        return False
    
    def eliminar_sesion(self, id_sesion: str) -> bool:
        """Elimina una sesión."""
        if id_sesion in self._sesiones:
            del self._sesiones[id_sesion]
            return True
        return False
    
    def obtener_o_crear_sesion(self, id_sesion: Optional[str]) -> SesionAnalisis:
        """Obtiene una sesión existente o crea una nueva."""
        if id_sesion:
            sesion = self.obtener_sesion(id_sesion)
            if sesion:
                return sesion
        return self.crear_sesion()
