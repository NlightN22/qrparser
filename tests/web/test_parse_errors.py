# comments in English only
from __future__ import annotations

from pathlib import Path
from fastapi.testclient import TestClient


def test_parse_handles_decoder_failure_as_400(client_fail: TestClient, tmp_path: Path, make_pdf):
    pdf_path = tmp_path / "bad.pdf"
    make_pdf(pdf_path)

    files = {"file": ("bad.pdf", pdf_path.read_bytes(), "application/pdf")}
    resp = client_fail.post("/v1/parse", files=files)

    assert resp.status_code == 400
    assert resp.json()["detail"] in {
        "Invalid or unreadable PDF",
        "Invalid PDF",
        "Invalid or unreadable file",
    }
