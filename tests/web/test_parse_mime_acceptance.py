# comments in English only
from __future__ import annotations

from fastapi.testclient import TestClient

from qrparser.web.main import create_app
from qrparser.web.dependencies import get_decoder


class AnyDecoderOK:
    """Fake decoder that returns distinct values for PDF vs images."""
    def extract_from_pdf(self, path):
        return ["OK_PDF"]

    # IMPORTANT: explicit (path, mime) signature so the endpoint picks this branch
    def extract_from_file(self, path, mime):
        return ["OK_IMG"]


def _make_client() -> TestClient:
    app = create_app()
    app.dependency_overrides[get_decoder] = lambda: AnyDecoderOK()
    return TestClient(app)


def test_accepts_png():
    client = _make_client()
    content = b"\x89PNG\r\n\x1a\n" + b"\x00" * 32
    files = {"file": ("code.png", content, "image/png")}
    resp = client.post("/v1/parse", files=files)

    assert resp.status_code == 200
    body = resp.json()
    assert body["file_name"] == "code.png"
    assert body["codes"] == ["OK_IMG"]


def test_accepts_jpeg():
    client = _make_client()
    content = b"\xFF\xD8\xFF" + b"\x00" * 32
    files = {"file": ("code.jpg", content, "image/jpeg")}
    resp = client.post("/v1/parse", files=files)

    assert resp.status_code == 200
    body = resp.json()
    assert body["file_name"] == "code.jpg"
    assert body["codes"] == ["OK_IMG"]


def test_rejects_gif():
    client = _make_client()
    content = b"GIF89a" + b"\x00" * 16
    files = {"file": ("code.gif", content, "image/gif")}
    resp = client.post("/v1/parse", files=files)

    assert resp.status_code == 400
    assert resp.json()["detail"] == "Unsupported file type"
