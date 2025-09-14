from fastapi import APIRouter
from .health import router as health_router
from .info import router as info_router
from .v1.parse import router as v1_parse_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(info_router)
api_router.include_router(v1_parse_router)
