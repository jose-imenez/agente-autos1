"""
Manejo Centralizado de Errores.

Provee un sistema de manejo de excepciones global para la aplicación.
"""

import logging
from datetime import datetime
from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError

from domain.dtos.dtos import ErrorRespuestaDTO


logger = logging.getLogger(__name__)


class AppException(Exception):
    """Excepción base de la aplicación."""
    
    def __init__(
        self,
        mensaje: str,
        codigo: str = "APP_ERROR",
        detalle: str | None = None,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
    ):
        self.mensaje = mensaje
        self.codigo = codigo
        self.detalle = detalle
        self.status_code = status_code
        super().__init__(mensaje)


class ValidationException(AppException):
    """Excepción para errores de validación."""
    
    def __init__(self, mensaje: str, detalle: str | None = None):
        super().__init__(
            mensaje=mensaje,
            codigo="VALIDATION_ERROR",
            detalle=detalle,
            status_code=status.HTTP_400_BAD_REQUEST,
        )


class NotFoundException(AppException):
    """Excepción para recursos no encontrados."""
    
    def __init__(self, recurso: str, identificador: str | None = None):
        mensaje = f"{recurso} no encontrado"
        if identificador:
            mensaje += f": {identificador}"
        super().__init__(
            mensaje=mensaje,
            codigo="NOT_FOUND",
            status_code=status.HTTP_404_NOT_FOUND,
        )


class BusinessException(AppException):
    """Excepción para errores de negocio."""
    
    def __init__(self, mensaje: str, detalle: str | None = None):
        super().__init__(
            mensaje=mensaje,
            codigo="BUSINESS_ERROR",
            detalle=detalle,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )


def crear_respuesta_error(
    mensaje: str,
    codigo: str,
    detalle: str | None = None,
) -> ErrorRespuestaDTO:
    """Factory para crear respuestas de error estandarizadas."""
    return ErrorRespuestaDTO(
        error=mensaje,
        detalle=detalle,
        codigo=codigo,
        timestamp=datetime.now(),
    )


async def app_exception_handler(
    request: Request, 
    exc: AppException
) -> JSONResponse:
    """Maneja excepciones de la aplicación."""
    logger.warning(
        f"Excepción de aplicación: {exc.codigo} - {exc.mensaje}",
        extra={"path": request.url.path, "detalle": exc.detalle},
    )
    
    respuesta = crear_respuesta_error(
        mensaje=exc.mensaje,
        codigo=exc.codigo,
        detalle=exc.detalle,
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=respuesta.model_dump(),
    )


async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError | ValidationError,
) -> JSONResponse:
    """Maneja errores de validación de Pydantic/FastAPI."""
    errores = exc.errors()
    
    detalles = []
    for error in errores:
        campo = " -> ".join(str(loc) for loc in error["loc"])
        detalles.append(f"{campo}: {error['msg']}")
    
    logger.warning(
        f"Error de validación: {detalles}",
        extra={"path": request.url.path},
    )
    
    respuesta = crear_respuesta_error(
        mensaje="Error de validación en los datos enviados",
        codigo="VALIDATION_ERROR",
        detalle="; ".join(detalles),
    )
    
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=respuesta.model_dump(),
    )


async def generic_exception_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    """Maneja excepciones no controladas."""
    logger.error(
        f"Error no manejado: {type(exc).__name__}: {str(exc)}",
        exc_info=True,
        extra={"path": request.url.path},
    )
    
    respuesta = crear_respuesta_error(
        mensaje="Error interno del servidor",
        codigo="INTERNAL_ERROR",
        detalle="Contacta al administrador si el problema persiste",
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=respuesta.model_dump(),
    )


def configurar_manejo_errores(app: FastAPI) -> None:
    """
    Configura el manejo centralizado de errores.
    
    Args:
        app: Instancia de FastAPI
    """
    app.add_exception_handler(AppException, app_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(ValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, generic_exception_handler)
    
    logger.info("Manejo de errores configurado")
