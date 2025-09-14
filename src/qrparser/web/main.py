from __future__ import annotations

from fastapi import FastAPI
from qrparser.observability.logging import setup_logging, get_logger
from . import routes
from .middleware import RequestLoggingMiddleware


def create_app() -> FastAPI:
    # initialize structured logging once
    setup_logging()
    logger = get_logger(__name__)
    logger.info("Creating FastAPI application")

    app = FastAPI(
        title="QR Parser Service",
        description="Microservice for parsing QR codes from PDF files",
        version="0.1.0",
    )

    # add middleware for request logging
    app.add_middleware(RequestLoggingMiddleware)

    # include routes
    app.include_router(routes.router)

    return app


# ASGI app for uvicorn entrypoint
app = create_app()
