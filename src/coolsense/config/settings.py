from __future__ import annotations

import os


def get_settings() -> dict:
    return {
        "poll_interval_seconds": float(os.getenv("COOLSENSE_POLL_INTERVAL_SECONDS", "2")),
        "model_path": os.getenv("COOLSENSE_MODEL_PATH", "coolsense_model.pt"),
        "history_size": int(os.getenv("COOLSENSE_HISTORY_SIZE", "500")),
        "mode": os.getenv("COOLSENSE_MODE", "auto"),
        "read_requires_auth": os.getenv("COOLSENSE_READ_REQUIRES_AUTH", "false").lower() in {"1", "true", "yes"},
        "read_rate_limit_per_minute": int(os.getenv("COOLSENSE_READ_RATE_LIMIT_PER_MINUTE", "120")),
        "mutating_rate_limit_per_minute": int(os.getenv("COOLSENSE_MUTATING_RATE_LIMIT_PER_MINUTE", "30")),
        "metrics_requires_auth": os.getenv("COOLSENSE_METRICS_REQUIRES_AUTH", "false").lower()
        in {"1", "true", "yes"},
    }
