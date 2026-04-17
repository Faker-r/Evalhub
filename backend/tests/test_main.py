import uuid

from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)


def test_health_check():
    """Test the health check endpoint at /api/health."""
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_root_endpoint():
    """Test the root endpoint at /."""
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()
    assert "Evalhub" in response.json()["message"]


def test_response_contains_trace_id_header():
    response = client.get("/api/health")
    trace_id = response.headers.get("x-trace-id")
    assert trace_id is not None
    uuid.UUID(trace_id)


def test_request_trace_id_is_echoed_back():
    response = client.get("/api/health", headers={"x-trace-id": "custom-trace-abc"})
    assert response.headers.get("x-trace-id") == "custom-trace-abc"
