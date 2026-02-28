from __future__ import annotations

from datetime import datetime, timedelta, timezone

from coolsense.config.defaults import DEFAULT_PERMIT_LIMITS
from coolsense.api.schemas import ForecastPoint, ForecastResponse


def _safe_iso(ts: str | None, fallback: datetime) -> datetime:
    if not ts:
        return fallback
    try:
        return datetime.fromisoformat(ts)
    except ValueError:
        return fallback


def _project(history: list[dict], key: str, hours_ahead: int) -> float:
    if not history:
        return 0.0
    if len(history) == 1:
        return float(history[-1].get(key, 0.0))

    window = history[-min(30, len(history)) :]
    first = window[0]
    last = window[-1]
    first_ts = _safe_iso(first.get("timestamp"), datetime.now(timezone.utc))
    last_ts = _safe_iso(last.get("timestamp"), datetime.now(timezone.utc))
    delta_hours = max((last_ts - first_ts).total_seconds() / 3600.0, 1e-6)

    first_val = float(first.get(key, 0.0))
    last_val = float(last.get(key, 0.0))
    slope_per_hour = (last_val - first_val) / delta_hours
    projected = last_val + slope_per_hour * float(hours_ahead)
    return max(0.0, projected)


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

    points = []
    for i in range(horizon_hours):
        step = i + 1
        cu = _project(recent_history, "cu_ppb", step)
        zn = _project(recent_history, "zn_ppb", step)
        cl2 = _project(recent_history, "chlorine_mgL", step)
        turb = _project(recent_history, "turbidity_node4", step)
        compliant = (
            cu <= DEFAULT_PERMIT_LIMITS["cu_ppb"]
            and zn <= DEFAULT_PERMIT_LIMITS["zn_ppb"]
            and cl2 <= DEFAULT_PERMIT_LIMITS["trc_mgL"]
            and turb <= DEFAULT_PERMIT_LIMITS["turbidity_ntu"]
        )
        points.append(
            ForecastPoint(
                timestamp=now + timedelta(hours=step),
                predicted_cu_ppb=cu,
                predicted_zn_ppb=zn,
                predicted_chlorine_mgL=cl2,
                predicted_turbidity_node4=turb,
                compliant=compliant,
            )
        )
    return ForecastResponse(horizon_hours=horizon_hours, points=points)
