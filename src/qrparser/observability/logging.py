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
    Configure stdlib logging to flow through structlog, so that *all* logs
    (including uvicorn) are rendered in the same JSON/text format.
    """
    root = logging.getLogger()
    root.handlers[:] = []
    root.setLevel(_LEVEL)

    # Choose output stream/handler (stdout|stderr|file)
    handler = _make_stream_handler()

    # Renderer for stdlib logs (must match structlog's renderer)
    if LOG_FORMAT == "text":
        renderer = structlog.dev.ConsoleRenderer()
    else:
        renderer = structlog.processors.JSONRenderer(ensure_ascii=False)

    # ProcessorFormatter will run on stdlib log records
    formatter = structlog.stdlib.ProcessorFormatter(
        processor=renderer,
        foreign_pre_chain=[
            structlog.stdlib.add_log_level,
            structlog.processors.TimeStamper(fmt="iso", utc=True),
        ],
    )
    handler.setFormatter(formatter)
    root.addHandler(handler)

    # Configure structlog so that its events are handed off to ProcessorFormatter
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.stdlib.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.TimeStamper(fmt="iso", utc=True),
            # Hand off to logging's ProcessorFormatter:
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    # Let uvicorn loggers propagate to root so they get our formatter
    for name in ("uvicorn", "uvicorn.error", "uvicorn.access", "uvicorn.asgi", "uvicorn.lifespan"):
        lg = logging.getLogger(name)
        lg.handlers = []         # no own handlers
        lg.propagate = True      # bubble up to root
        lg.setLevel(_LEVEL)

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
