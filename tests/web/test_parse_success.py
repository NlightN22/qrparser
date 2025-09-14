# comments in English only
from __future__ import annotations

from pathlib import Path
from fastapi.testclient import TestClient


def test_parse_success_generates_expected_payload(client_ok: TestClient, tmp_path: Path, make_pdf):
    pdf_path = tmp_path / "sample.pdf"
    make_pdf(pdf_path, extra_bytes=32)

    files = {"file": ("sample.pdf", pdf_path.read_bytes(), "application/pdf")}
    resp = client_ok.post("/v1/parse", files=files, headers={"X-Request-ID": "req-123"})

    assert resp.status_code == 200
    data = resp.json()
    assert data["request_id"] == "req-123"
    assert data["file_name"] == "sample.pdf"
    assert data["codes"] == ["QR123", "https://example.com/x"]
    assert resp.headers.get("X-Request-ID") == "req-123"


def test_parse_generates_request_id_when_header_missing(client_ok: TestClient, tmp_path: Path, make_pdf):
    pdf_path = tmp_path / "x.pdf"
    make_pdf(pdf_path)

    files = {"file": ("x.pdf", pdf_path.read_bytes(), "application/pdf")}
    resp = client_ok.post("/v1/parse", files=files)

    assert resp.status_code == 200
    assert "X-Request-ID" in resp.headers
    assert resp.json()["request_id"] == resp.headers["X-Request-ID"]
