# comments in English only
from __future__ import annotations

from pathlib import Path
import pytest
from fastapi.testclient import TestClient

from qrparser.web.main import create_app
from qrparser.web.dependencies import get_decoder


class FakeDecoderOK:
    """Fake decoder that returns deterministic codes."""
    def extract_from_pdf(self, path: Path | str):
        return ["QR123", "https://example.com/x"]


class FakeDecoderFail:
    """Fake decoder that simulates unreadable/invalid PDF."""
    def extract_from_pdf(self, path: Path | str):
        raise RuntimeError("decode failed")


def _build_client(fake_decoder) -> TestClient:
    """Build FastAPI app and override decoder dependency."""
    app = create_app()
    app.dependency_overrides[get_decoder] = lambda: fake_decoder
    return TestClient(app)


@pytest.fixture
def client_ok() -> TestClient:
    """Client with successful fake decoder."""
    return _build_client(FakeDecoderOK())


@pytest.fixture
def client_fail() -> TestClient:
    """Client with failing fake decoder."""
    return _build_client(FakeDecoderFail())


@pytest.fixture
def client_ok_factory():
    """
    Factory fixture to build a client *after* the test sets env vars and resets settings.
    Usage:
        client = client_ok_factory()
    """
    def _factory() -> TestClient:
        return _build_client(FakeDecoderOK())
    return _factory


@pytest.fixture
def make_pdf():
    """Return a small helper to write a minimal-enough PDF file."""
    def _write_minimal_pdf(dst: Path, extra_bytes: int = 0) -> None:
        dst.write_bytes(b"%PDF-1.4\n" + (b"0" * max(0, extra_bytes)))
    return _write_minimal_pdf
