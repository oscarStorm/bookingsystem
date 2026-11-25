"""HTTP seam: GET /health is the service's liveness endpoint (used by Render
health checks). It must answer 200 without requiring a database connection.
"""

from fastapi.testclient import TestClient

from app.main import app


def test_health_returns_200_ok():
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
