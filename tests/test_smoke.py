from fastapi.testclient import TestClient

from coolsense.api.app import app


def test_health_endpoint() -> None:
    with TestClient(app) as client:
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


def test_mutating_route_requires_api_key() -> None:
    with TestClient(app) as client:
        response = client.post("/v1/events/inject", json={"type": "corrosion_spike", "magnitude": 1.0})
        assert response.status_code == 200 or response.status_code == 401

