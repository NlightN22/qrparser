# comments in English only
from __future__ import annotations

from functools import lru_cache
from typing import Literal, Optional

from pydantic import AnyUrl, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    Designed for Docker/Kubernetes usage with sane defaults.
    """

    # --- App basics ---
    APP_NAME: str = Field(default="qrparser", description="Application name.")
    APP_ENV: Literal["dev", "staging", "prod", "test"] = Field(
        default="dev", description="Deployment environment."
    )
    DEBUG: bool = Field(default=False, description="Enable debug mode.")

    # --- Logging ---
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO", description="Root log level."
    )
    LOG_JSON: bool = Field(
        default=True, description="Emit logs in JSON format for structured logging."
    )

    # --- QR parsing behavior ---
    DECODE_SCALE: float = Field(
        default=3.0, ge=0.1, le=10.0, description="Primary resize scale factor."
    )
    FALLBACK_SCALE: float = Field(
        default=5.0, ge=0.1, le=10.0, description="Fallback resize scale factor."
    )
    MAX_PAGES: int = Field(
        default=50, ge=1, description="Max pages to scan in a PDF to prevent abuse."
    )
    CONCURRENCY: int = Field(
        default=4, ge=1, description="Worker threads/processes used for parsing."
    )

    # --- Accepted types (split by family) ---
    ALLOWED_MIME_PDF: tuple[str, ...] = Field(
        default=("application/pdf",),
        description="Accepted MIME types for PDF uploads.",
    )
    ALLOWED_MIME_IMG: tuple[str, ...] = Field(
        default=("image/png", "image/jpeg"),
        description="Accepted MIME types for image uploads.",
    )

    # --- Size limits (split by family) ---
    MAX_FILE_SIZE_MB_PDF: int = Field(
        default=10, ge=1, description="Max PDF size in megabytes."
    )
    MAX_FILE_SIZE_MB_IMG: int = Field(
        default=6, ge=1, description="Max image size in megabytes."
    )

    # --- HTTP service ---
    HTTP_HOST: str = Field(default="0.0.0.0", description="Bind host.")
    HTTP_PORT: int = Field(default=8000, ge=1, le=65535, description="Bind port.")
    HTTP_WORKERS: int = Field(
        default=1, ge=1, description="Number of workers for ASGI server."
    )
    CORS_ALLOW_ORIGINS: tuple[str, ...] = Field(
        default=("*",), description="Allowed CORS origins."
    )

    # --- Observability / health ---
    ENABLE_PROMETHEUS: bool = Field(
        default=False, description="Expose Prometheus metrics if True."
    )
    METRICS_PATH: str = Field(default="/metrics", description="Metrics endpoint path.")

    # --- Optional external hooks ---
    SENTRY_DSN: Optional[AnyUrl] = Field(
        default=None, description="Sentry DSN; if absent, Sentry is disabled."
    )

    model_config = SettingsConfigDict(
        env_prefix="QR_",              # env vars like QR_LOG_LEVEL, QR_HTTP_PORT, etc.
        env_file=(".env",),            # optional; ignored if file absent
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # --- Convenience computed views ---
    @property
    def ALL_ALLOWED_MIME(self) -> tuple[str, ...]:
        """Union of PDF and image MIME lists."""
        return tuple(self.ALLOWED_MIME_PDF) + tuple(self.ALLOWED_MIME_IMG)


@lru_cache(maxsize=1)
def _build_settings() -> Settings:
    """Internal cached builder."""
    return Settings()


def get_settings() -> Settings:
    """Public accessor of cached settings."""
    return _build_settings()


def reset_settings_cache() -> None:
    """Clear the settings cache (useful in tests after env changes)."""
    _build_settings.cache_clear()  # type: ignore[attr-defined]


# Optional convenience singleton; keep it only in this submodule.
settings = get_settings()
