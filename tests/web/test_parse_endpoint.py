# comments in English only
from __future__ import annotations

from fastapi.testclient import TestClient

from qrparser.web.main import create_app
from qrparser.web.dependencies import get_decoder


class FakeDecoderOK:
    """Fake decoder that returns deterministic codes."""
    def extract_from_pdf(self, path):
        return ["QR123", "https://example.com/x"]


class FakeDecoderFail:
    """Fake decoder that simulates unreadable/invalid PDF."""
    def extract_from_pdf(self, path):
        raise RuntimeError("decode failed")


def make_client(fake_decoder) -> TestClient:
    """Build app and override decoder dependency."""
    app = create_app()
    app.dependency_overrides[get_decoder] = lambda: fake_decoder
    return TestClient(app)


def test_parse_success_generates_expected_payload(tmp_path):
    client = make_client(FakeDecoderOK())
    pdf_path = tmp_path / "sample.pdf"
    # Minimal PDF header bytes are enough for the handler (decoder is faked)
    pdf_path.write_bytes(b"%PDF-1.4\n% minimal test file\n")

    files = {"file": ("sample.pdf", pdf_path.read_bytes(), "application/pdf")}
    resp = client.post("/v1/parse", files=files, headers={"X-Request-ID": "req-123"})

    assert resp.status_code == 200
    data = resp.json()
    assert data["request_id"] == "req-123"
    assert data["file_name"] == "sample.pdf"
    assert data["codes"] == ["QR123", "https://example.com/x"]
    # Middleware must echo X-Request-ID back
    assert resp.headers.get("X-Request-ID") == "req-123"


def test_parse_generates_request_id_when_header_missing(tmp_path):
    client = make_client(FakeDecoderOK())
    pdf_path = tmp_path / "x.pdf"
    pdf_path.write_bytes(b"%PDF-1.4\n")

    files = {"file": ("x.pdf", pdf_path.read_bytes(), "application/pdf")}
    resp = client.post("/v1/parse", files=files)

    assert resp.status_code == 200
    assert "X-Request-ID" in resp.headers
    assert resp.json()["request_id"] == resp.headers["X-Request-ID"]


def test_parse_rejects_non_pdf_content_type():
    client = make_client(FakeDecoderOK())
    files = {"file": ("note.txt", b"hello", "text/plain")}
    resp = client.post("/v1/parse", files=files)

    assert resp.status_code == 400
    assert resp.json()["detail"] == "Expected a PDF file"


def test_parse_handles_decoder_failure_as_400(tmp_path):
    client = make_client(FakeDecoderFail())
    pdf_path = tmp_path / "bad.pdf"
    pdf_path.write_bytes(b"%PDF-1.4\n")

    files = {"file": ("bad.pdf", pdf_path.read_bytes(), "application/pdf")}
    resp = client.post("/v1/parse", files=files)

    assert resp.status_code == 400
    assert resp.json()["detail"] in {"Invalid or unreadable PDF", "Invalid PDF"}
