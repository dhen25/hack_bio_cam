from __future__ import annotations

import json
import logging


def get_logger() -> logging.Logger:
    logger = logging.getLogger("coolsense")
    if not logger.handlers:
        handler = logging.StreamHandler()
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger


def log_request(trace_id: str, method: str, path: str, status_code: int, duration_ms: float) -> None:
    event = {
        "trace_id": trace_id,
        "method": method,
        "path": path,
        "status_code": status_code,
        "duration_ms": round(duration_ms, 2),
    }
    get_logger().info(json.dumps(event, separators=(",", ":")))
