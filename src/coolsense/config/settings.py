from __future__ import annotations

import os

from coolsense.config.defaults import DEFAULT_MAKEUP_CHEMISTRY, DEFAULT_PERMIT_LIMITS


def _env_float(name: str, default: float) -> float:
    value = os.getenv(name)
    if value is None:
        return float(default)
    try:
        return float(value)
    except ValueError:
        return float(default)


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
        "blowdown_rate_m3_day": _env_float("COOLSENSE_BLOWDOWN_RATE_M3_DAY", 50.0),
        "makeup_chemistry": {
            "calcium_mgL": _env_float("COOLSENSE_MAKEUP_CALCIUM_MG_L", DEFAULT_MAKEUP_CHEMISTRY["calcium_mgL"]),
            "magnesium_mgL": _env_float("COOLSENSE_MAKEUP_MAGNESIUM_MG_L", DEFAULT_MAKEUP_CHEMISTRY["magnesium_mgL"]),
            "silica_mgL": _env_float("COOLSENSE_MAKEUP_SILICA_MG_L", DEFAULT_MAKEUP_CHEMISTRY["silica_mgL"]),
            "chloride_mgL": _env_float("COOLSENSE_MAKEUP_CHLORIDE_MG_L", DEFAULT_MAKEUP_CHEMISTRY["chloride_mgL"]),
            "sulfate_mgL": _env_float("COOLSENSE_MAKEUP_SULFATE_MG_L", DEFAULT_MAKEUP_CHEMISTRY["sulfate_mgL"]),
            "cu_ppb": _env_float("COOLSENSE_MAKEUP_CU_PPB", DEFAULT_MAKEUP_CHEMISTRY["cu_ppb"]),
            "zn_ppb": _env_float("COOLSENSE_MAKEUP_ZN_PPB", DEFAULT_MAKEUP_CHEMISTRY["zn_ppb"]),
            "chlorine_mgL": _env_float("COOLSENSE_MAKEUP_CHLORINE_MG_L", DEFAULT_MAKEUP_CHEMISTRY["chlorine_mgL"]),
            "inhibitor_phosphorus_mgL": _env_float(
                "COOLSENSE_MAKEUP_INHIBITOR_PHOSPHORUS_MG_L",
                DEFAULT_MAKEUP_CHEMISTRY["inhibitor_phosphorus_mgL"],
            ),
        },
        "permit_limits": {
            "cu_ppb": _env_float("COOLSENSE_PERMIT_CU_PPB", DEFAULT_PERMIT_LIMITS["cu_ppb"]),
            "zn_ppb": _env_float("COOLSENSE_PERMIT_ZN_PPB", DEFAULT_PERMIT_LIMITS["zn_ppb"]),
            "trc_mgL": _env_float("COOLSENSE_PERMIT_TRC_MG_L", DEFAULT_PERMIT_LIMITS["trc_mgL"]),
            "ph_min": _env_float("COOLSENSE_PERMIT_PH_MIN", DEFAULT_PERMIT_LIMITS["ph_min"]),
            "ph_max": _env_float("COOLSENSE_PERMIT_PH_MAX", DEFAULT_PERMIT_LIMITS["ph_max"]),
            "turbidity_ntu": _env_float("COOLSENSE_PERMIT_TURBIDITY_NTU", DEFAULT_PERMIT_LIMITS["turbidity_ntu"]),
        },
    }
