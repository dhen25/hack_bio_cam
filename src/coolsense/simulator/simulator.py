from __future__ import annotations

import math
import random
import threading
import time
from datetime import datetime, timezone
from typing import Any


EVENT_TYPES = {
    "corrosion_spike",
    "biocide_overdose",
    "biocide_underdose",
    "makeup_quality_drop",
    "concentration_buildup",
    "ph_drop",
    "turbidity_event",
}


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


class CoolingTowerSimulator:
    """Simulates 4 cooling tower sensor nodes with physical coupling."""

    def __init__(self) -> None:
        self.blowdown_rate = 50.0
        self.biocide_dose = 2.0
        self.target_ph = 8.0
        self.target_coc = 5.0

        self.ambient_temp = 35.0
        self.makeup_ph = 7.8
        self.makeup_ec = 500.0
        self.makeup_turbidity = 2.0

        self.current_coc = 5.0
        self.corrosion_severity = 0.1
        self.biofouling_level = 0.05
        self.time_since_biocide = 0.0
        self.biocide_residual = 1.5
        self._last_tick = time.time()

        self._events: list[dict[str, float | str]] = []
        self._lock = threading.Lock()

    def inject_event(self, event_type: str, magnitude: float = 1.0) -> None:
        if event_type not in EVENT_TYPES:
            raise ValueError(f"Unknown event type: {event_type}")

        now = time.time()
        with self._lock:
            self._events.append(
                {
                    "type": event_type,
                    "magnitude": max(0.1, magnitude),
                    "start_time": now,
                    "duration": random.uniform(30.0, 120.0),
                }
            )

    def apply_recommendations(self, recommendations: dict[str, Any]) -> None:
        self.blowdown_rate = _clamp(
            float(recommendations.get("recommended_blowdown_rate_m3_day", self.blowdown_rate)),
            10.0,
            100.0,
        )
        self.biocide_dose = _clamp(
            float(recommendations.get("recommended_biocide_dose_mgL", self.biocide_dose)),
            0.5,
            5.0,
        )
        self.target_ph = _clamp(
            float(recommendations.get("recommended_ph_setpoint", self.target_ph)),
            6.5,
            9.5,
        )
        self.target_coc = _clamp(
            float(recommendations.get("recommended_coc_target", self.target_coc)),
            1.0,
            10.0,
        )

    def _add_noise(self, value: float, noise_pct: float = 0.02) -> float:
        return value * (1.0 + random.gauss(0.0, noise_pct))

    def _event_multiplier(self, now: float) -> dict[str, float]:
        multipliers = {name: 0.0 for name in EVENT_TYPES}
        with self._lock:
            active_events: list[dict[str, float | str]] = []
            for event in self._events:
                start_time = float(event["start_time"])
                duration = float(event["duration"])
                if now - start_time <= duration:
                    active_events.append(event)
                    progress = (now - start_time) / duration
                    intensity = math.sin(progress * math.pi) * float(event["magnitude"])
                    multipliers[str(event["type"])] += intensity
            self._events = active_events
        return multipliers

    def read_all_nodes(self) -> dict[str, Any]:
        now = time.time()
        dt_hours = max(1e-6, (now - self._last_tick) / 3600.0)
        self._last_tick = now
        m = self._event_multiplier(now)

        self.current_coc += (self.target_coc - self.current_coc) * 0.02
        self.current_coc += m["concentration_buildup"] * 0.2
        self.current_coc = _clamp(self.current_coc, 1.0, 10.0)

        self.time_since_biocide += dt_hours
        decay_rate = 0.2 * (1.05 ** (self.ambient_temp - 25.0))
        self.biocide_residual = self.biocide_dose * math.exp(-decay_rate * self.time_since_biocide)
        if self.time_since_biocide > 4.0:
            self.time_since_biocide = 0.0
            self.biocide_residual = self.biocide_dose

        self.biocide_residual += m["biocide_overdose"] * 1.5
        self.biocide_residual -= m["biocide_underdose"] * 1.0
        self.biocide_residual = _clamp(self.biocide_residual, 0.0, 10.0)

        self.corrosion_severity += (0.2 - self.corrosion_severity) * 0.01
        self.corrosion_severity += m["corrosion_spike"] * 0.2
        self.corrosion_severity = _clamp(self.corrosion_severity, 0.0, 1.0)

        self.biofouling_level += m["biocide_underdose"] * 0.05
        self.biofouling_level -= m["biocide_overdose"] * 0.04
        self.biofouling_level = _clamp(self.biofouling_level, 0.0, 1.0)

        makeup_ec = self.makeup_ec + m["makeup_quality_drop"] * 300.0
        makeup_turbidity = self.makeup_turbidity + m["makeup_quality_drop"] * 15.0 + m["turbidity_event"] * 45.0
        target_ph = self.target_ph - m["ph_drop"] * 1.2

        node1_ph = _clamp(self._add_noise(self.makeup_ph, 0.005), 6.5, 9.5)
        node1_ec = _clamp(self._add_noise(makeup_ec, 0.01), 200.0, 10000.0)
        node1_turb = _clamp(self._add_noise(makeup_turbidity, 0.05), 0.0, 500.0)

        node2_ph = _clamp(self._add_noise(target_ph, 0.01), 6.5, 9.5)
        node2_ec = _clamp(self._add_noise(node1_ec * self.current_coc, 0.015), 200.0, 10000.0)
        node2_turb = _clamp(self._add_noise(node1_turb + 2.5 + self.biofouling_level * 20.0, 0.08), 0.0, 500.0)

        node3_ph = _clamp(self._add_noise(node2_ph - self.corrosion_severity * 0.2, 0.01), 6.5, 9.5)
        node3_ec = _clamp(self._add_noise(node2_ec + self.corrosion_severity * 200.0, 0.02), 200.0, 10000.0)
        node3_turb = _clamp(
            self._add_noise(node2_turb + self.corrosion_severity * 18.0 + m["corrosion_spike"] * 8.0, 0.08),
            0.0,
            500.0,
        )

        node4_ph = _clamp(self._add_noise((node2_ph + node3_ph) / 2.0, 0.01), 6.5, 9.5)
        node4_ec = _clamp(self._add_noise((node2_ec + node3_ec) / 2.0, 0.02), 200.0, 10000.0)
        node4_turb = _clamp(self._add_noise((node2_turb + node3_turb) / 2.0, 0.08), 0.0, 500.0)

        return {
            "node1": {"ph": node1_ph, "ec": node1_ec, "turbidity": node1_turb},
            "node2": {"ph": node2_ph, "ec": node2_ec, "turbidity": node2_turb},
            "node3": {"ph": node3_ph, "ec": node3_ec, "turbidity": node3_turb},
            "node4": {"ph": node4_ph, "ec": node4_ec, "turbidity": node4_turb},
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "_internal": {
                "true_coc": self.current_coc,
                "true_corrosion": self.corrosion_severity,
                "true_biocide_residual": self.biocide_residual,
                "true_biofouling": self.biofouling_level,
                "ambient_temp_c": self.ambient_temp,
            },
        }
