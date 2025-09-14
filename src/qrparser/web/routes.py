# src/qrparser/web/routes.py
from __future__ import annotations

from fastapi import APIRouter, UploadFile, File, Depends
from .dependencies import get_request_id
from .schemas import HealthResponse, ParseResponse, ErrorResponse

router = APIRouter()

@router.get("/health", response_model=HealthResponse, tags=["meta"])
async def health_check() -> HealthResponse:
    return HealthResponse()

@router.post(
    "/v1/parse",
    response_model=ParseResponse,
    responses={400: {"model": ErrorResponse}},
    tags=["parser"],
    summary="Parse QR codes from a PDF",
)
async def parse_pdf(
    file: UploadFile = File(..., description="PDF file to parse"),
    request_id: str = Depends(get_request_id),
) -> ParseResponse:
    # Stub: implement real decoding in the next step
    return ParseResponse(request_id=request_id, file_name=file.filename, codes=[])
