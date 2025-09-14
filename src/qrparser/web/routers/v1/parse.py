from __future__ import annotations
import os
import tempfile
from pathlib import Path

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status
from ...schemas import ParseResponse, ErrorResponse
from ...dependencies import get_request_id, get_decoder
from qrparser.core.pdf_decoder import PdfBarcodeDecoder

router = APIRouter(prefix="/v1", tags=["parser"])

@router.post(
    "/parse",
    response_model=ParseResponse,
    responses={400: {"model": ErrorResponse}},
    summary="Parse QR codes from a PDF",
)
async def parse_pdf(
    file: UploadFile = File(..., description="PDF file to parse"),
    request_id: str = Depends(get_request_id),
    decoder: PdfBarcodeDecoder = Depends(get_decoder),
) -> ParseResponse:
    if file.content_type not in ("application/pdf", "application/octet-stream"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Expected a PDF file")

    tmp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(await file.read())
            tmp_path = Path(tmp.name)

        codes = decoder.extract_from_pdf(tmp_path)
        return ParseResponse(request_id=request_id, file_name=file.filename, codes=codes)
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or unreadable PDF")
    finally:
        if tmp_path and tmp_path.exists():
            try: os.unlink(tmp_path)
            except OSError: pass
