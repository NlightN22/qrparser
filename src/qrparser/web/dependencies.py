from __future__ import annotations
import uuid
from fastapi import Header
from qrparser.core.pdf_decoder import PdfBarcodeDecoder, DecodeSettings

async def get_request_id(x_request_id: str | None = Header(default=None)) -> str:
    """Return X-Request-ID header value or generate a new UUID."""
    return x_request_id or str(uuid.uuid4())

def get_decoder() -> PdfBarcodeDecoder:
    """Provide a stateless decoder instance per request."""
    # If you want custom tuning, pass DecodeSettings(scale=..., fallback_scale=...)
    return PdfBarcodeDecoder(DecodeSettings())
