from __future__ import annotations

from fastapi.testclient import TestClient

from mits_validator.api import app

client = TestClient(app)


def test_health() -> None:
    """Test the health endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "version" in data
    assert isinstance(data["version"], str)
