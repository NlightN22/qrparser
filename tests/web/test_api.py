from fastapi.testclient import TestClient
import re

from qrparser.web.main import app

client = TestClient(app)


def test_health_check():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_docs_served():
    # /docs is Swagger UI
    resp = client.get("/docs")
    assert resp.status_code == 200
    # Content-Type should be HTML
    assert resp.headers["content-type"].startswith("text/html")
    # Check that Swagger UI assets marker exists
    assert "Swagger UI" in resp.text or "swagger-ui" in resp.text


def test_redoc_served():
    resp = client.get("/redoc")
    assert resp.status_code == 200
    assert resp.headers["content-type"].startswith("text/html")
    # ReDoc page has this marker
    assert "redoc" in resp.text.lower()


def test_openapi_json():
    resp = client.get("/openapi.json")
    assert resp.status_code == 200
    schema = resp.json()
    # Minimal sanity checks
    assert isinstance(schema, dict)
    assert "openapi" in schema and re.match(r"^3\.", schema["openapi"])
    assert "info" in schema and "title" in schema["info"]
    assert "paths" in schema and "/health" in schema["paths"]


def test_health_is_logged(caplog):
    caplog.set_level("INFO")
    resp = client.get("/health")
    assert resp.status_code == 200

    # grab only our request logger
    recs = [r for r in caplog.records if r.name == "qrparser.request" and isinstance(r.msg, dict)]

    # Expect at least request_start and request_end for /health
    starts = [r for r in recs if r.msg.get("event") == "request_start" and r.msg.get("path") == "/health"]
    ends = [r for r in recs if r.msg.get("event") == "request_end" and r.msg.get("path") == "/health"]

    assert starts, "Expected request_start log for /health"
    assert ends, "Expected request_end log for /health"

    # Optional: validate fields
    assert ends[0].msg.get("status") == 200
    assert ends[0].msg.get("method") == "GET"

def test_request_id_header_present():
    """Server must always return an X-Request-ID header."""
    resp = client.get("/health")
    assert resp.status_code == 200
    assert "X-Request-ID" in resp.headers
    assert resp.headers["X-Request-ID"]  # non-empty


def test_request_id_header_is_propagated():
    """If client provides X-Request-ID, server must echo the same value back."""
    given_id = "test-req-id-12345"
    resp = client.get("/health", headers={"X-Request-ID": given_id})
    assert resp.status_code == 200
    assert resp.headers.get("X-Request-ID") == given_id