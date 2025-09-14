# comments in English only
from __future__ import annotations

from pathlib import Path
from fastapi.testclient import TestClient
from qrparser.config.settings import reset_settings_cache


def test_parse_rejects_file_too_large(tmp_path: Path, monkeypatch, client_ok_factory):
    # Configure PDF size limit to 1 MB and rebuild settings/app
    monkeypatch.setenv("QR_MAX_FILE_SIZE_MB_PDF", "1")
    reset_settings_cache()

    client: TestClient = client_ok_factory()

    # Fake PDF just over 1 MB
    content = b"%PDF-1.7\n" + b"0" * (1 * 1024 * 1024 + 1)
    files = {"file": ("big.pdf", content, "application/pdf")}

    resp = client.post("/v1/parse", files=files)
    assert resp.status_code == 400
    assert resp.json()["detail"] == "File too large for PDF. Max size is 1 MB"


def test_parse_allows_file_at_size_limit(tmp_path: Path, monkeypatch, client_ok_factory):
    # Configure PDF size limit to 1 MB and rebuild settings/app
    monkeypatch.setenv("QR_MAX_FILE_SIZE_MB_PDF", "1")
    reset_settings_cache()

    client: TestClient = client_ok_factory()

    # Fake PDF just under the limit
    content = b"%PDF-1.7\n" + b"0" * (1 * 1024 * 1024 - 10)
    files = {"file": ("ok.pdf", content, "application/pdf")}

    resp = client.post("/v1/parse", files=files)
    assert resp.status_code == 200
    body = resp.json()
    assert resp.headers.get("X-Request-ID")
    assert "codes" in body
