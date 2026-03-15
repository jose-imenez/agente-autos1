"""
Logging Estructurado para la Aplicación.
"""

import json
import logging
import sys
from datetime import datetime
from enum import Enum
from typing import Any
from pathlib import Path


class LogLevel(str, Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class JsonFormatter(logging.Formatter):
    """Formateador que convierte logs a JSON estructurado."""

    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Contexto adicional
        if hasattr(record, "context"):
            log_data["context"] = record.context

        # Excepciones
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_data, ensure_ascii=False)


class StructuredLogger:
    """Logger estructurado que produce salida en formato JSON."""

    def __init__(self, name: str):
        self._logger = logging.getLogger(name)
        self._logger.setLevel(logging.DEBUG)

        if not self._logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            handler.setFormatter(JsonFormatter())
            self._logger.addHandler(handler)

    # Reserved keys in LogRecord that cannot be overwritten
    RESERVED_KEYS = {
        "args", "asctime", "created", "exc_info", "exc_text", "filename",
        "funcName", "levelname", "levelno", "lineno", "module", "msecs",
        "message", "msg", "name", "pathname", "process", "processName",
        "relativeCreated", "stack_info", "thread", "threadName", "tsinfo",
    }

    def _log(self, nivel: LogLevel, mensaje: str, **kwargs: Any) -> None:
        # Filter out reserved keys to avoid LogRecord conflicts
        filtered_kwargs = {k: v for k, v in kwargs.items() if k not in self.RESERVED_KEYS}
        extra = {"context": filtered_kwargs} if filtered_kwargs else {}
        getattr(self._logger, nivel.value.lower())(mensaje, extra=extra)

    def info(self, mensaje: str, **kwargs: Any) -> None:
        self._log(LogLevel.INFO, mensaje, **kwargs)

    def warning(self, mensaje: str, **kwargs: Any) -> None:
        self._log(LogLevel.WARNING, mensaje, **kwargs)

    def error(self, mensaje: str, exc: Exception | None = None, **kwargs: Any) -> None:
        if exc:
            kwargs["exception"] = {
                "type": type(exc).__name__,
                "message": str(exc),
            }
        self._log(LogLevel.ERROR, mensaje, **kwargs)

    def debug(self, mensaje: str, **kwargs: Any) -> None:
        self._log(LogLevel.DEBUG, mensaje, **kwargs)

    def critical(self, mensaje: str, **kwargs: Any) -> None:
        self._log(LogLevel.CRITICAL, mensaje, **kwargs)


def configurar_logging(
    nivel: str = "INFO",
    log_file: Path | None = None,
) -> None:
    nivel_numeric = getattr(logging, nivel.upper(), logging.INFO)

    handlers: list[logging.Handler] = []

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(JsonFormatter())
    handlers.append(console_handler)

    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(JsonFormatter())
        handlers.append(file_handler)

    logging.basicConfig(
        level=nivel_numeric,
        handlers=handlers,
    )

    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.error").setLevel(logging.INFO)

    logger = logging.getLogger(__name__)
    logger.info(f"Logging configurado - Nivel: {nivel}")


# Instancias globales
app_logger = StructuredLogger("agente_ia")
api_logger = StructuredLogger("agente_ia.api")
service_logger = StructuredLogger("agente_ia.services")