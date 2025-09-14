# src/qrparser/web/schemas/__init__.py
from __future__ import annotations
from typing import List, Literal
from pydantic import BaseModel, Field

class HealthResponse(BaseModel):
    status: Literal["ok"] = "ok"

    model_config = {
        "json_schema_extra": {"examples": [{"status": "ok"}]}
    }

class ParseResponse(BaseModel):
    request_id: str = Field(..., description="Correlation ID of the request")
    file_name: str = Field(..., description="Original uploaded filename")
    codes: List[str] = Field(default_factory=list, description="Decoded QR values")

    model_config = {
        "json_schema_extra": {
            "examples": [{
                "request_id": "a1b2c3d4-0000-1111-2222-333344445555",
                "file_name": "sample.pdf",
                "codes": ["QR123", "https://example.com/x"]
            }]
        }
    }

class ErrorResponse(BaseModel):
    detail: str

    model_config = {
        "json_schema_extra": {"examples": [{"detail": "Invalid PDF"}]}
    }
