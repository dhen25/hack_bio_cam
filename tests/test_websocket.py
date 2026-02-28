from fastapi.testclient import TestClient

from coolsense.api.app import app


def test_websocket_smoke_receives_snapshot() -> None:
    with TestClient(app) as client:
        with client.websocket_connect("/v1/stream") as ws:
            payload = ws.receive_json()
            assert "timestamp" in payload
