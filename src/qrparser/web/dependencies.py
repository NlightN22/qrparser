# src/qrparser/web/dependencies.py
from __future__ import annotations
import uuid
from fastapi import Header

async def get_request_id(x_request_id: str | None = Header(default=None)) -> str:
    """Return X-Request-ID header value or generate a new UUID."""
    # We rely on middleware to also echo X-Request-ID in responses.
    return x_request_id or str(uuid.uuid4())
