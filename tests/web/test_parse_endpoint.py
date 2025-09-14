# comments in English only
from __future__ import annotations

from fastapi.testclient import TestClient

from qrparser.web.main import create_app
from qrparser.web.dependencies import get_decoder
from qrparser.config.settings import reset_settings_cache 


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


def test_parse_rejects_file_too_large(monkeypatch):
    # Set max size to 1 MB for this test
    monkeypatch.setenv("QR_MAX_FILE_SIZE_MB", "1")
    reset_settings_cache()  # must be before app/client creation

    client = make_client(FakeDecoderOK())

    # Build a fake PDF just over 1 MB
    content = b"%PDF-1.7\n" + b"0" * (1 * 1024 * 1024 + 1)
    files = {"file": ("big.pdf", content, "application/pdf")}

    resp = client.post("/v1/parse", files=files)

    assert resp.status_code == 400
    assert resp.json()["detail"] == "File too large. Max size is 1 MB"


def test_parse_allows_file_at_size_limit(monkeypatch):
    # Set max size to 1 MB
    monkeypatch.setenv("QR_MAX_FILE_SIZE_MB", "1")
    reset_settings_cache()  # must be before app/client creation

    client = make_client(FakeDecoderOK())

    # Build a fake PDF just under the 1 MB limit
    content = b"%PDF-1.7\n" + b"0" * (1 * 1024 * 1024 - 10)
    files = {"file": ("ok.pdf", content, "application/pdf")}

    resp = client.post("/v1/parse", files=files)

    assert resp.status_code == 200
    body = resp.json()
    # basic sanity checks
    assert resp.headers.get("X-Request-ID")
    assert "codes" in body
