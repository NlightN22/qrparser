from __future__ import annotations

import time
import uuid
from fastapi import FastAPI, Request, Response

# your logger wiring
from qrparser.observability.logging import (
    setup_logging,
    set_request_context,
    clear_request_context,
    log_request_start,
    log_request_end,
    get_logger,
)

from . import routes


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

    # request logging middleware with request id
    @app.middleware("http")
    async def request_logging_middleware(request: Request, call_next):
        req_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        start = time.perf_counter()

        set_request_context(request_id=req_id, method=request.method, path=str(request.url.path))
        log_request_start(method=request.method, path=str(request.url.path), client=str(request.client))

        try:
            response: Response = await call_next(request)
        except Exception:
            duration_ms = (time.perf_counter() - start) * 1000
            log_request_end(status=500, duration_ms=round(duration_ms, 2))
            clear_request_context()
            raise

        duration_ms = (time.perf_counter() - start) * 1000
        log_request_end(status=response.status_code, duration_ms=round(duration_ms, 2))
        response.headers["X-Request-ID"] = req_id

        clear_request_context()
        return response

    app.include_router(routes.router)  # /health remains available
    return app


# ASGI app for uvicorn entrypoint
app = create_app()
