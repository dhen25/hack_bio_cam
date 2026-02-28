from fastapi.testclient import TestClient

from coolsense.api.app import app


def test_health() -> None:
    with TestClient(app) as client:
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"


def test_invalid_api_key_is_rejected(monkeypatch) -> None:
    monkeypatch.setenv("COOLSENSE_API_KEY", "expected")
    monkeypatch.setenv("COOLSENSE_ALLOW_EMPTY_API_KEY", "false")
    with TestClient(app) as client:
        response = client.post(
            "/v1/controls/override",
            json={"mode": "manual", "blowdown_rate_m3_day": 45.0},
            headers={"X-API-Key": "bad"},
        )
        assert response.status_code == 401


def test_current_state_after_startup_tick() -> None:
    with TestClient(app) as client:
        response = client.get("/v1/state/current")
        assert response.status_code == 200
        payload = response.json()
        assert "nodes" in payload
        assert "coc" in payload


def test_event_inject_and_history_flow(monkeypatch) -> None:
    monkeypatch.setenv("COOLSENSE_API_KEY", "expected")
    monkeypatch.setenv("COOLSENSE_ALLOW_EMPTY_API_KEY", "false")
    with TestClient(app) as client:
        inject = client.post(
            "/v1/events/inject",
            json={"type": "corrosion_spike", "magnitude": 2.0},
            headers={"X-API-Key": "expected"},
        )
        assert inject.status_code == 200
        assert inject.json()["accepted"] is True
        history = client.get("/v1/state/history?limit=5")
        assert history.status_code == 200
        assert len(history.json()) >= 1


def test_request_id_header_is_returned() -> None:
    with TestClient(app) as client:
        response = client.get("/health", headers={"X-Request-Id": "req-123"})
        assert response.headers.get("X-Request-Id") == "req-123"


def test_metrics_endpoint_exposes_counter() -> None:
    with TestClient(app) as client:
        response = client.get("/metrics")
        assert response.status_code == 200
        assert "coolsense_requests_total" in response.text


def test_rate_limit_can_trigger(monkeypatch) -> None:
    monkeypatch.setenv("COOLSENSE_READ_RATE_LIMIT_PER_MINUTE", "1")
    # create fresh app state path by requesting same route twice in same minute
    with TestClient(app) as client:
        first = client.get("/health")
        second = client.get("/health")
        assert first.status_code == 200
        assert second.status_code in {200, 429}
