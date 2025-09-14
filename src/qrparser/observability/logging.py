from __future__ import annotations

import logging
import os
import sys
from typing import Optional, Any, Dict

import structlog
from structlog.contextvars import bind_contextvars, clear_contextvars

# ---- ENV-настройки ----
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
LOG_DEST = os.getenv("LOG_DEST", "stdout")   # stdout|stderr|file
LOG_FILE = os.getenv("LOG_FILE", "logs/qrparser.log")
LOG_FORMAT = os.getenv("LOG_FORMAT", "json") # json|text

_LEVEL = getattr(logging, LOG_LEVEL, logging.INFO)

def _make_stream_handler() -> logging.Handler:
    if LOG_DEST == "file":
        os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
        return logging.FileHandler(LOG_FILE, encoding="utf-8")
    return logging.StreamHandler(sys.stdout if LOG_DEST == "stdout" else sys.stderr)

def setup_logging() -> None:
    """
    Инициализация один раз при старте приложения.
    Делает bridge: stdlib logging -> structlog, JSON-вывод, UTC-время.
    """
    root = logging.getLogger()
    root.handlers[:] = []
    root.setLevel(_LEVEL)
    h = _make_stream_handler()
    h.setFormatter(logging.Formatter("%(message)s"))
    root.addHandler(h)

    processors = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.TimeStamper(fmt="iso", utc=True),
    ]

    if LOG_FORMAT == "text":
        processors.append(structlog.dev.ConsoleRenderer())
    else:
        processors.append(structlog.processors.JSONRenderer(ensure_ascii=False))

    structlog.configure(
        processors=processors,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

def get_logger(name: Optional[str] = None) -> structlog.stdlib.BoundLogger:
    return structlog.get_logger(name or "qrparser")

def set_request_context(**ctx: Any) -> None:
    """
    bind_contextvars(request_id=..., span_id=..., tenant=..., user_id=..., ...)
    """
    if ctx:
        bind_contextvars(**ctx)

def clear_request_context() -> None:
    clear_contextvars()

def log_request_start(method: str, path: str, **extra: Any) -> None:
    get_logger("qrparser.request").info("request_start", method=method, path=path, **extra)

def log_request_end(status: int, duration_ms: float, **extra: Any) -> None:
    get_logger("qrparser.request").info("request_end", status=status, duration_ms=duration_ms, **extra)
