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


def test_openapi_basic_metadata():
    resp = client.get("/openapi.json")
    assert resp.status_code == 200
    spec = resp.json()
    assert isinstance(spec, dict)
    assert re.match(r"^3\.", spec.get("openapi", ""))
    assert spec.get("info", {}).get("title") == "QR Parser Service"

def test_openapi_paths_exist():
    spec = client.get("/openapi.json").json()
    paths = spec.get("paths", {})
    assert "/health" in paths
    assert "/v1/parse" in paths

def test_health_response_schema_ref():
    spec = client.get("/openapi.json").json()
    get_health = spec["paths"]["/health"]["get"]
    ref = get_health["responses"]["200"]["content"]["application/json"]["schema"]["$ref"]
    assert ref.endswith("/HealthResponse")

def test_parse_request_and_responses():
    spec = client.get("/openapi.json").json()
    post_parse = spec["paths"]["/v1/parse"]["post"]

    # request body: multipart with 'file' as binary
    mf_schema = post_parse["requestBody"]["content"]["multipart/form-data"]["schema"]

    def _resolve(schema):
        # resolve single-level $ref if present
        if "$ref" in schema:
            ref = schema["$ref"]                       # e.g. "#/components/schemas/Body_parse_pdf_v1_parse_post"
            name = ref.split("/")[-1]
            return spec["components"]["schemas"][name]
        return schema

    resolved = _resolve(mf_schema)
    props = resolved.get("properties", {})
    assert "file" in props
    assert props["file"]["type"] == "string"
    assert props["file"]["format"] == "binary"

    # responses: 200 -> ParseResponse, 400 -> ErrorResponse
    ok_ref = post_parse["responses"]["200"]["content"]["application/json"]["schema"]["$ref"]
    bad_ref = post_parse["responses"]["400"]["content"]["application/json"]["schema"]["$ref"]
    assert ok_ref.endswith("/ParseResponse")
    assert bad_ref.endswith("/ErrorResponse")


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