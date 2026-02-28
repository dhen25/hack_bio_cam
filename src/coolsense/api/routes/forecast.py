from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from coolsense.api.deps import get_orchestrator
from coolsense.api.schemas import ForecastResponse

router = APIRouter(prefix="/v1", tags=["forecast"])


@router.get("/forecast", response_model=ForecastResponse)
def get_forecast(
    horizon_hours: int = Query(default=6, ge=1, le=24),
    orchestrator=Depends(get_orchestrator),
) -> ForecastResponse:
    return ForecastResponse.model_validate(orchestrator.forecast(horizon_hours))
