from __future__ import annotations

import asyncio
import os

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from starlette.websockets import WebSocketState

from coolsense.auth.api_key import is_api_key_valid
from coolsense.observability.metrics import get_metrics

router = APIRouter(tags=["stream"])


@router.websocket("/v1/stream")
async def stream_snapshots(websocket: WebSocket) -> None:
    api_key = websocket.query_params.get("api_key")
    read_requires_auth = os.getenv("COOLSENSE_READ_REQUIRES_AUTH", "false").lower() in {"1", "true", "yes"}
    if read_requires_auth and not is_api_key_valid(api_key):
        await websocket.close(code=1008, reason="UNAUTHORIZED")
        return

    manager = websocket.app.state.ws_manager
    await manager.connect(websocket)
    get_metrics().websocket_connections += 1
    try:
        while True:
            latest = websocket.app.state.orchestrator.current()
            if latest is not None:
                await websocket.send_json(latest)
            await asyncio.sleep(2)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        get_metrics().websocket_connections = max(0, get_metrics().websocket_connections - 1)
    except Exception:
        if websocket.client_state == WebSocketState.CONNECTED:
            await websocket.close(code=1011, reason="INTERNAL_ERROR")
        manager.disconnect(websocket)
        get_metrics().websocket_connections = max(0, get_metrics().websocket_connections - 1)
