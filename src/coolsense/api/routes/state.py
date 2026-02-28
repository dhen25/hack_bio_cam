from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, Query

from coolsense.api.deps import get_orchestrator
from coolsense.api.schemas import ForecastResponse, HistoryPoint, SystemState

router = APIRouter(prefix="/v1/state", tags=["state"])


@router.get("/current", response_model=SystemState)
async def get_current_state(orchestrator=Depends(get_orchestrator)) -> SystemState:
    current = orchestrator.current()
    if not current:
        await orchestrator.tick()
        current = orchestrator.current()
    return SystemState.model_validate(current["state"])


@router.get("/history", response_model=list[HistoryPoint])
def get_history(
    limit: int = Query(default=50, ge=1, le=500),
    since_ts: datetime | None = Query(default=None),
    orchestrator=Depends(get_orchestrator),
) -> list[HistoryPoint]:
    items = orchestrator.history_points(limit=limit, since_ts=since_ts.isoformat() if since_ts else None)
    return [
        HistoryPoint(
            timestamp=item["timestamp"],
            coc=item["coc"],
            cu_ppb=item["cu_ppb"],
            zn_ppb=item["zn_ppb"],
            chlorine_mgL=item["chlorine_mgL"],
            turbidity_node4=item["turbidity_node4"],
            ph_node4=item["ph_node4"],
            compliant=item["compliant"],
            recommendation=item["recommendation"],
        )
        for item in items
    ]


@router.get("/forecast", response_model=ForecastResponse)
def get_forecast(
    horizon_hours: int = Query(default=6, ge=1, le=24),
    orchestrator=Depends(get_orchestrator),
) -> ForecastResponse:
    return ForecastResponse.model_validate(orchestrator.forecast(horizon_hours))
