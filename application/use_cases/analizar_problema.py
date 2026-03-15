from domain.entities.problema import Problema, ResultadoAnalisis
from domain.interfaces.analizador_interface import IAnalizadorService


class AnalizarProblemaUseCase:
    def __init__(self, analizador_service: IAnalizadorService):
        self._analizador_service = analizador_service

    def execute(self, problema: Problema) -> ResultadoAnalisis:
        return self._analizador_service.analizar(problema)
