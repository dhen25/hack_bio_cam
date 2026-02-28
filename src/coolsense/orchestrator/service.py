from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from coolsense.optimizer.inference import infer_recommendations, load_model
from coolsense.observability.metrics import get_metrics
from coolsense.providers.simulator import SimulatorProvider
from coolsense.storage.ring_buffer import RingBuffer
from coolsense.streaming.manager import WebSocketManager
from coolsense.twin.forecast import forecast_from_history
from coolsense.twin.state import compute_system_state


class OrchestratorService:
    def __init__(self, settings: dict[str, Any], ws_manager: WebSocketManager | None = None) -> None:
        self.settings = settings
        self.provider = SimulatorProvider()
        self.history = RingBuffer(maxlen=int(settings.get("history_size", 500)))
        self.mode = settings.get("mode", "auto")
        self.last_tick_ts: str | None = None
        self.ws_manager = ws_manager or WebSocketManager()

        self.model = None
        self.model_stats: dict[str, Any] | None = None
        try:
            self.model, self.model_stats = load_model(settings.get("model_path", "coolsense_model.pt"))
            self.model_loaded = True
        except FileNotFoundError:
            self.model_loaded = False

    async def tick(self) -> dict[str, Any]:
        get_metrics().ticks_total += 1
        nodes = self.provider.read_all_nodes()
        state = compute_system_state(nodes)

        recommendation = None
        if self.model_loaded and self.model and self.model_stats:
            recommendation = infer_recommendations(state, self.model, self.model_stats)
            if self.mode == "auto":
                self.provider.simulator.apply_recommendations(recommendation.model_dump())

        snapshot = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "state": state.model_dump(mode="json"),
            "coc": state.coc,
            "cu_ppb": state.corrosion.cu_ppb,
            "zn_ppb": state.corrosion.zn_ppb,
            "chlorine_mgL": state.biocide.total_chlorine_mgL,
            "turbidity_node4": state.nodes.node4.turbidity,
            "ph_node4": state.nodes.node4.ph,
            "compliant": state.compliant,
            "recommendation": recommendation.model_dump(mode="json") if recommendation else None,
            "model_loaded": self.model_loaded,
            "mode": self.mode,
        }
        self.history.append(snapshot)
        self.last_tick_ts = snapshot["timestamp"]
        await self.ws_manager.broadcast(snapshot)
        return snapshot

    def current(self) -> dict[str, Any] | None:
        return self.history.latest()

    def history_points(self, limit: int = 50, since_ts: str | None = None) -> list[dict[str, Any]]:
        data = self.history.to_list()
        if since_ts:
            data = [x for x in data if x["timestamp"] >= since_ts]
        return data[-limit:]

    def forecast(self, horizon_hours: int) -> dict[str, Any]:
        return forecast_from_history(self.history.to_list(), horizon_hours=horizon_hours).model_dump(mode="json")

    def inject_event(self, event_type: str, magnitude: float) -> dict[str, Any]:
        self.provider.simulator.inject_event(event_type, magnitude)
        return {"accepted": True, "event_type": event_type, "magnitude": magnitude}

    def override_controls(self, payload: dict[str, Any]) -> dict[str, Any]:
        self.mode = payload.get("mode", self.mode)
        mapped = {
            "recommended_blowdown_rate_m3_day": payload.get("blowdown_rate_m3_day"),
            "recommended_biocide_dose_mgL": payload.get("biocide_dose_mgL"),
            "recommended_ph_setpoint": payload.get("ph_setpoint"),
            "recommended_coc_target": payload.get("coc_target"),
        }
        cleaned = {k: v for k, v in mapped.items() if v is not None}
        if cleaned:
            self.provider.simulator.apply_recommendations(cleaned)
        return {"accepted": True, "mode": self.mode}
