# comments in English only
from fastapi import APIRouter
from ..schemas import HealthResponse

router = APIRouter(tags=["meta"])

@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    return HealthResponse()
