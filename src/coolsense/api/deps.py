from __future__ import annotations

from uuid import uuid4

from fastapi import Request
from fastapi import Header

from coolsense.api.errors import APIError
from coolsense.auth.api_key import is_api_key_valid
from coolsense.config.settings import get_settings
from coolsense.orchestrator.service import OrchestratorService
from coolsense.streaming.manager import WebSocketManager


def require_api_key(x_api_key: str | None = Header(default=None, alias="X-API-Key")) -> None:
    if not is_api_key_valid(x_api_key):
        raise APIError(
            status_code=401,
            code="UNAUTHORIZED",
            message="Missing or invalid API key",
            details={"hint": "Provide X-API-Key header"},
        )


def new_trace_id() -> str:
    return str(uuid4())


def get_orchestrator(request: Request):
    if not hasattr(request.app.state, "orchestrator"):
        request.app.state.ws_manager = WebSocketManager()
        request.app.state.orchestrator = OrchestratorService(
            settings=get_settings(),
            ws_manager=request.app.state.ws_manager,
        )
    return request.app.state.orchestrator
