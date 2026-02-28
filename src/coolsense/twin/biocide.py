from __future__ import annotations

import math


def biocide_model(
    biocide_dose_mgL: float,
    hours_since_dose: float,
    ph: float,
    temp_c: float = 35.0,
) -> dict[str, float | str]:
    # Decay accelerates with temperature and alkaline pH.
    decay_rate = 0.2 * (1.05 ** (temp_c - 25.0))
    decay_rate *= 10 ** (0.1 * (ph - 7.0))
    total = max(0.0, biocide_dose_mgL * math.exp(-decay_rate * max(0.0, hours_since_dose)))
    hocl_fraction = 1.0 / (1.0 + 10.0 ** (ph - 7.54))
    effective = total * hocl_fraction

    status = "low"
    if effective >= 0.4:
        status = "effective"
    elif effective >= 0.2:
        status = "borderline"

    return {
        "total_chlorine_mgL": total,
        "effective_hocl_mgL": effective,
        "hocl_fraction_pct": hocl_fraction * 100.0,
        "decay_rate_per_hour": decay_rate,
        "status": status,
    }
