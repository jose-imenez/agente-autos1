from abc import ABC, abstractmethod
from ..entities.problema import Problema, ResultadoAnalisis


class IAnalizadorService(ABC):
    @abstractmethod
    def analizar(self, problema: Problema) -> ResultadoAnalisis:
        pass
