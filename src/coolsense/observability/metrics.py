from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Metrics:
    requests_total: int = 0
    errors_total: int = 0
    websocket_connections: int = 0
    ticks_total: int = 0

    def render_prometheus(self) -> str:
        lines = [
            "# HELP coolsense_requests_total Total HTTP requests",
            "# TYPE coolsense_requests_total counter",
            f"coolsense_requests_total {self.requests_total}",
            "# HELP coolsense_errors_total Total API errors",
            "# TYPE coolsense_errors_total counter",
            f"coolsense_errors_total {self.errors_total}",
            "# HELP coolsense_websocket_connections Active websocket connections",
            "# TYPE coolsense_websocket_connections gauge",
            f"coolsense_websocket_connections {self.websocket_connections}",
            "# HELP coolsense_ticks_total Orchestrator ticks",
            "# TYPE coolsense_ticks_total counter",
            f"coolsense_ticks_total {self.ticks_total}",
        ]
        return "\n".join(lines) + "\n"


_METRICS = Metrics()


def get_metrics() -> Metrics:
    return _METRICS
