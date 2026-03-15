from pydantic import BaseModel


class Problema(BaseModel):
    texto: str


class ResultadoAnalisis(BaseModel):
    opciones: list[str]
