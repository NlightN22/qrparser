import time
import uuid
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

from qrparser.observability.logging import (
    set_request_context,
    clear_request_context,
    log_request_start,
    log_request_end,
)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for structured request logging with request ID."""

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        req_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        request.state.request_id = req_id
        start = time.perf_counter()

        set_request_context(
            request_id=req_id,
            method=request.method,
            path=str(request.url.path),
        )
        log_request_start(
            method=request.method,
            path=str(request.url.path),
            client=str(request.client),
        )

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
