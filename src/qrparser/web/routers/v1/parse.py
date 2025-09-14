from __future__ import annotations
import os
import tempfile
from pathlib import Path

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status, Request

from ...schemas import ParseResponse, ErrorResponse
from ...dependencies import get_request_id, get_decoder
from qrparser.core.pdf_decoder import PdfBarcodeDecoder

from qrparser.config.settings import get_settings, Settings

router = APIRouter(prefix="/v1", tags=["parser"])


@router.post(
    "/parse",
    response_model=ParseResponse,
    responses={400: {"model": ErrorResponse}},
    summary="Parse QR codes from a PDF or image",
)
async def parse_image(
    request: Request,
    file: UploadFile = File(..., description="PDF or image to parse"),
    request_id: str = Depends(get_request_id),
    decoder = Depends(get_decoder),  # CompositeDecoder
    settings: Settings = Depends(get_settings),
) -> ParseResponse:
    content = await file.read()

    if not hasattr(request.state, "extra_log"):
        request.state.extra_log = {}
    request.state.extra_log.update(
        {
            "file_name": file.filename,
            "content_type": file.content_type,
            "file_size": len(content),
        }
    )

    mime = (file.content_type or "").lower()
    if mime not in settings.ALL_ALLOWED_MIME:
        request.state.extra_log["error"] = "unsupported_mime"
        raise HTTPException(status_code=400, detail="Unsupported file type")

    # Size check per family
    if mime == "application/pdf":
        max_bytes = settings.MAX_FILE_SIZE_MB_PDF * 1024 * 1024
    else:
        max_bytes = settings.MAX_FILE_SIZE_MB_IMG * 1024 * 1024

    if len(content) > max_bytes:
        request.state.extra_log.update(
            {"error": "file_too_large", "max_bytes": max_bytes}
        )
        kind = "PDF" if mime == "application/pdf" else "image"
        raise HTTPException(
            status_code=400,
            detail=f"File too large for {kind}. Max size is {max_bytes // (1024*1024)} MB",
        )

    tmp_path: Path | None = None
    try:
        suffix = ".pdf" if mime == "application/pdf" else Path(file.filename or "").suffix or ".bin"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(content)
            tmp_path = Path(tmp.name)

        codes = (
            decoder.extract_from_file(tmp_path, mime)  # note: uses CompositeDecoder
            if hasattr(decoder, "extract_from_file") and "mime" in decoder.extract_from_file.__code__.co_varnames
            else decoder.extract_from_pdf(tmp_path)  # backward compatibility if needed
        )

        request.state.extra_log["codes_found"] = len(codes)
        return ParseResponse(request_id=request_id, file_name=file.filename, codes=list(codes))

    except Exception:
        request.state.extra_log["error"] = "decode_failed"
        detail = "Invalid or unreadable file" if mime != "application/pdf" else "Invalid or unreadable PDF"
        raise HTTPException(status_code=400, detail=detail)
    finally:
        if tmp_path and tmp_path.exists():
            try: os.unlink(tmp_path)
            except OSError: pass