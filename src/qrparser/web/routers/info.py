from fastapi import APIRouter

router = APIRouter(tags=["meta"])

@router.get("/info")
async def info() -> dict:
    return {"name": "qrparser", "version": "0.1.0"}
