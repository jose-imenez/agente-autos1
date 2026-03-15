"""
Application Layer - Casos de Uso.

Implementa los casos de uso de la aplicación siguiendo
los principios de Clean Architecture.
"""

from typing import Optional

from domain.dtos.dtos import (
    ProblemaDTO,
    ResultadoAnalisisDTO,
    SolucionDTO,
    DecisionDTO,
    HistorialDecisionDTO,
)
from domain.entities.entities import Problema, Solucion
from domain.interfaces.ports import IAnalizadorService, IHistorialService
from infrastructure.logging.structured_logging import service_logger


class AnalizarProblemaUseCase:
    """
    Caso de uso para analizar un problema y generar soluciones.
    
    Implementa el patrón de caso de uso con inyección de dependencias.
    """
    
    def __init__(
        self,
        analizador_service: IAnalizadorService,
        historial_service: IHistorialService,
    ):
        self._analizador = analizador_service
        self._historial = historial_service
    
    def execute(
        self, 
        problema_dto: ProblemaDTO,
        soluciones_previas: Optional[list] = None
    ) -> ResultadoAnalisisDTO:
        """
        Ejecuta el análisis del problema.
        
        Args:
            problema_dto: DTO con los datos del problema
            soluciones_previas: Lista de soluciones previas para evitar duplicados
            
        Returns:
            DTO con el resultado del análisis
        """
        service_logger.info(
            "Iniciando análisis de problema",
            longitud_texto=len(problema_dto.texto),
            soluciones_previas=len(soluciones_previas) if soluciones_previas else 0,
        )
        
        # Convertir DTO a entidad de dominio
        problema = Problema(
            texto=problema_dto.texto,
            contexto=problema_dto.contexto,
        )
        
        # Ejecutar análisis con soluciones previas
        resultado = self._analizador.analizar(problema, soluciones_previas)
        
        # Convertir resultado a DTO
        soluciones_dto = [
            SolucionDTO(
                titulo=sol.titulo,
                descripcion=sol.descripcion,
                ventajas=sol.ventajas,
                desventajas=sol.desventajas,
                complejidad=sol.complejidad.value,
                categoria=sol.categoria.value,
                recomendacion=sol.recomendacion,
                tecnologias=sol.tecnologias,
            )
            for sol in resultado.soluciones
        ]
        
        service_logger.info(
            "Análisis completado",
            num_soluciones=len(soluciones_dto),
            tiene_preguntas=len(resultado.preguntas_aclaratorias) > 0,
        )
        
        return ResultadoAnalisisDTO(
            problema_original=resultado.problema_original,
            timestamp=resultado.timestamp,
            soluciones=soluciones_dto,
            razonamiento=resultado.razonamiento,
            preguntas_aclaratorias=resultado.preguntas_aclaratorias,
        )
    
    def obtener_historial(self, limite: int = 10) -> list[HistorialDecisionDTO]:
        """Obtiene el historial de decisiones."""
        return self._historial.obtener_historial(limite)
    
    def guardar_decision(
        self,
        problema: str,
        decision: DecisionDTO,
    ) -> None:
        """Guarda una decisión del usuario."""
        self._historial.guardar_decision(problema, decision)
        
        service_logger.info(
            "Decisión guardada",
            problema=problema[:50],
            solucion=decision.indice_seleccionado,
        )
    
    def limpiar_historial(self) -> None:
        """Limpia el historial."""
        self._historial.limpiar_historial()
        service_logger.info("Historial limpiado")
