from domain.entities.problema import Problema, ResultadoAnalisis
from domain.interfaces.analizador_interface import IAnalizadorService


class AnalizadorService(IAnalizadorService):
    def analizar(self, problema: Problema) -> ResultadoAnalisis:
        texto = problema.texto.lower()

        if "comer" in texto:
            opciones = [
                "Revisar qué hay en casa.",
                "Pedir comida a domicilio.",
                "Salir a un restaurante."
            ]
        elif "red" in texto:
            opciones = [
                "Diseñar topología en estrella.",
                "Implementar VLANs.",
                "Configurar DHCP automático."
            ]
        else:
            opciones = [
                "Analizar mejor el problema.",
                "Evaluar recursos disponibles.",
                "Tomar decisión basada en eficiencia."
            ]

        return ResultadoAnalisis(opciones=opciones)
