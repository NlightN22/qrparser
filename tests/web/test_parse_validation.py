# comments in English only
from __future__ import annotations

from fastapi.testclient import TestClient


def test_parse_rejects_unsupported_content_type(client_ok: TestClient):
    files = {"file": ("note.txt", b"hello", "text/plain")}
    resp = client_ok.post("/v1/parse", files=files)

    assert resp.status_code == 400
    assert resp.json()["detail"] == "Unsupported file type"
