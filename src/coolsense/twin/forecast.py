from __future__ import annotations

from datetime import datetime, timedelta, timezone

from coolsense.api.schemas import ForecastPoint, ForecastResponse


def forecast_from_history(recent_history: list[dict], horizon_hours: int) -> ForecastResponse:
    horizon_hours = max(1, min(24, horizon_hours))
    now = datetime.now(timezone.utc)
    if not recent_history:
        points = [
            ForecastPoint(
                timestamp=now + timedelta(hours=i + 1),
                predicted_cu_ppb=0.0,
                predicted_zn_ppb=0.0,
                predicted_chlorine_mgL=0.0,
                predicted_turbidity_node4=0.0,
                compliant=True,
            )
            for i in range(horizon_hours)
        ]
        return ForecastResponse(horizon_hours=horizon_hours, points=points)

    latest = recent_history[-1]
    points = []
    for i in range(horizon_hours):
        points.append(
            ForecastPoint(
                timestamp=now + timedelta(hours=i + 1),
                predicted_cu_ppb=float(latest.get("cu_ppb", 0.0)),
                predicted_zn_ppb=float(latest.get("zn_ppb", 0.0)),
                predicted_chlorine_mgL=float(latest.get("chlorine_mgL", 0.0)),
                predicted_turbidity_node4=float(latest.get("turbidity_node4", 0.0)),
                compliant=bool(latest.get("compliant", True)),
            )
        )
    return ForecastResponse(horizon_hours=horizon_hours, points=points)
