from __future__ import annotations
import uuid
from fastapi import Header, Request
from qrparser.core.pdf_decoder import PdfBarcodeDecoder, DecodeSettings

async def get_request_id(request: Request, x_request_id: str | None = Header(default=None)) -> str:
    """Return request-scoped Request ID from middleware, falling back to header/UUID."""
    rid = getattr(request.state, "request_id", None) or x_request_id
    if rid:
        return rid
    rid = str(uuid.uuid4())
    request.state.request_id = rid
    return rid

def get_decoder() -> PdfBarcodeDecoder:
    """Provide a stateless decoder instance per request."""
    return PdfBarcodeDecoder(DecodeSettings())
