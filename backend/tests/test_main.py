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
