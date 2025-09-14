from __future__ import annotations
import os
import tempfile
from pathlib import Path

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status

from ...schemas import ParseResponse, ErrorResponse
from ...dependencies import get_request_id, get_decoder
from qrparser.core.pdf_decoder import PdfBarcodeDecoder

from qrparser.config.settings import get_settings, Settings

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
    settings: Settings = Depends(get_settings),  # ✅ injected, respects reset_settings_cache()
) -> ParseResponse:
    # Read once for validation and then write to tmp
    content = await file.read()

    # MIME check (keep legacy message for existing tests)
    if file.content_type not in settings.ALLOWED_MIME:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Expected a PDF file",
        )

    # Size check using settings
    max_bytes = settings.MAX_FILE_SIZE_MB * 1024 * 1024
    if len(content) > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Max size is {settings.MAX_FILE_SIZE_MB} MB",
        )

    tmp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(content)
            tmp_path = Path(tmp.name)

        codes = decoder.extract_from_pdf(tmp_path)
        return ParseResponse(request_id=request_id, file_name=file.filename, codes=codes)

    except Exception:
        # Keep stable error for tests
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or unreadable PDF",
        )
    finally:
        if tmp_path and tmp_path.exists():
            try:
                os.unlink(tmp_path)
            except OSError:
                pass