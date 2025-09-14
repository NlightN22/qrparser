# tests/web/test_parse_integration.py
from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from qrparser.web.main import create_app


def make_client() -> TestClient:
    # Use the real application with real dependencies (no overrides)
    app = create_app()
    return TestClient(app)


@pytest.mark.integration
def test_parse_integration_with_fixture_pdf():
    """Full-stack check: send a real PDF file to /v1/parse and verify payload."""
    client = make_client()

    fixture = Path(__file__).resolve().parents[1] / "fixtures" / "test2.pdf"
    if not fixture.exists():
        pytest.skip("Fixture tests/fixtures/test2.pdf is missing")

    files = {
        "file": ("test2.pdf", fixture.read_bytes(), "application/pdf"),
    }
    req_id = "it-parse-001"
    resp = client.post("/v1/parse", files=files, headers={"X-Request-ID": req_id})

    assert resp.status_code == 200, resp.text

    data = resp.json()
    # Request ID must be echoed back by middleware and payload
    assert resp.headers.get("X-Request-ID") == req_id
    assert data["request_id"] == req_id
    assert data["file_name"] == "test2.pdf"

    # Validate decoded codes contain the expected QR from the fixture
    expected_code = "(01)04640550671068(21)e,rXo8KJ*.Bl2(91)EE11(92)39aSrIK/T4UOgsjCzC1Ni/u5DVIcJLmDkOhVzZdYwhM="
    assert isinstance(data["codes"], list)
    assert expected_code in data["codes"], f"Expected QR code {expected_code} not found in {data['codes']}"


@pytest.mark.integration
def test_parse_integration_with_corrupted_pdf_returns_400():
    """Full-stack check: corrupted PDF content should yield 400 with an error detail."""
    client = make_client()

    files = {
        "file": ("bad.pdf", b"not a real pdf content", "application/pdf"),
    }
    resp = client.post("/v1/parse", files=files)

    assert resp.status_code == 400, resp.text
    payload = resp.json()
    assert payload.get("detail") in {"Invalid or unreadable PDF", "Invalid PDF"}

    # Server must still supply a request id in the response headers
    assert "X-Request-ID" in resp.headers and resp.headers["X-Request-ID"]
