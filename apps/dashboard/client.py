from __future__ import annotations

import json
import os
from typing import Any
from urllib.parse import urlparse

import httpx
from websocket import create_connection


class CoolSenseClient:
    def __init__(self) -> None:
        self.base_url = os.getenv("COOLSENSE_API_BASE_URL", "http://localhost:8000").rstrip("/")
        self.api_key = os.getenv("COOLSENSE_API_KEY")
        self._headers = {"X-API-Key": self.api_key} if self.api_key else {}

    def _get(self, path: str, **params) -> dict[str, Any]:
        response = httpx.get(f"{self.base_url}{path}", params=params, headers=self._headers, timeout=5.0)
        response.raise_for_status()
        return response.json()

    def current_state(self) -> dict[str, Any]:
        return self._get("/v1/state/current")

    def history(self, limit: int = 120) -> list[dict[str, Any]]:
        return self._get("/v1/state/history", limit=limit)

    def forecast(self, horizon_hours: int = 6) -> dict[str, Any]:
        return self._get("/v1/forecast", horizon_hours=horizon_hours)

    def inject_event(self, event_type: str, magnitude: float = 1.0) -> dict[str, Any]:
        response = httpx.post(
            f"{self.base_url}/v1/events/inject",
            json={"type": event_type, "magnitude": magnitude},
            headers=self._headers,
            timeout=5.0,
        )
        response.raise_for_status()
        return response.json()

    def ws_snapshot(self) -> dict[str, Any] | None:
        parsed = urlparse(self.base_url)
        scheme = "wss" if parsed.scheme == "https" else "ws"
        ws_url = f"{scheme}://{parsed.netloc}/v1/stream"
        if self.api_key:
            ws_url = f"{ws_url}?api_key={self.api_key}"
        try:
            ws = create_connection(ws_url, timeout=2)
            raw = ws.recv()
            ws.close()
            return json.loads(raw)
        except Exception:
            return None
