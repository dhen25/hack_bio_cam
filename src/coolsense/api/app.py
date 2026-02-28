from __future__ import annotations

import asyncio

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse

from coolsense.api.middleware import request_context_and_rate_limit, reset_rate_limits
from coolsense.api.errors import APIError, api_error_handler, unhandled_error_handler, validation_error_handler
from coolsense.api.routes.controls import router as controls_router
from coolsense.api.routes.events import router as events_router
from coolsense.api.routes.forecast import router as forecast_router
from coolsense.api.routes.health import router as health_router
from coolsense.api.routes.model import router as model_router
from coolsense.api.routes.state import router as state_router
from coolsense.api.routes.stream import router as stream_router
from coolsense.config.settings import get_settings
from coolsense.observability.metrics import get_metrics
from coolsense.orchestrator.loop import run_loop
from coolsense.orchestrator.service import OrchestratorService
from coolsense.streaming.manager import WebSocketManager

app = FastAPI(title="HypaSense Labs API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080", "http://127.0.0.1:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.middleware("http")(request_context_and_rate_limit)


app.add_exception_handler(APIError, api_error_handler)
app.add_exception_handler(RequestValidationError, validation_error_handler)
app.add_exception_handler(Exception, unhandled_error_handler)


@app.on_event("startup")
async def on_startup() -> None:
    settings = get_settings()
    reset_rate_limits()
    app.state.settings = settings
    app.state.ws_manager = WebSocketManager()
    app.state.orchestrator = OrchestratorService(settings=settings, ws_manager=app.state.ws_manager)
    app.state.stop_event = asyncio.Event()
    app.state.loop_task = asyncio.create_task(run_loop(app.state.orchestrator, app.state.stop_event))


@app.on_event("shutdown")
async def on_shutdown() -> None:
    app.state.stop_event.set()
    await app.state.loop_task


app.include_router(health_router)
app.include_router(state_router)
app.include_router(forecast_router)
app.include_router(events_router)
app.include_router(controls_router)
app.include_router(model_router)
app.include_router(stream_router)


@app.get("/metrics")
def metrics() -> PlainTextResponse:
    return PlainTextResponse(get_metrics().render_prometheus())

