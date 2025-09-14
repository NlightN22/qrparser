import time
import uuid
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import JSONResponse


from qrparser.observability.logging import (
    set_request_context,
    clear_request_context,
    log_request_start,
    log_request_end,
)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for structured request logging with request ID."""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        req_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        request.state.request_id = req_id
        # prepare container for handler-provided extras
        request.state.extra_log = {}  # type: ignore[attr-defined]
        start = time.perf_counter()

        set_request_context(request_id=req_id, method=request.method, path=str(request.url.path))
        log_request_start(method=request.method, path=str(request.url.path), client=str(request.client))

        response: Optional[Response] = None
        status_code = 500
        try:
            response = await call_next(request)
            status_code = response.status_code
        except Exception:
            # re-raise after logging in finally
            raise
        finally:
            duration_ms = round((time.perf_counter() - start) * 1000, 2)
            extra = getattr(request.state, "extra_log", {}) or {}
            log_request_end(
                status=status_code,
                duration_ms=duration_ms,
                method=request.method,
                path=str(request.url.path),
                request_id=req_id,
                **extra,
            )
            # ensure the header is set for both success and error responses
            if response is not None:
                response.headers["X-Request-ID"] = req_id
            clear_request_context()

        # always return a Response (on exception the framework builds its own)
        if response is None:
            # very defensive fallback; usually not hit
            response = JSONResponse({"detail": "Internal Server Error"}, status_code=status_code)
            response.headers["X-Request-ID"] = req_id
        return response
