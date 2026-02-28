from __future__ import annotations

from coolsense.config.defaults import DEFAULT_PERMIT_LIMITS


def compute_pollution_score(
    cu_ppb: float,
    zn_ppb: float,
    biocide_mgL: float,
    phosphorus_mgL: float,
    blowdown_m3_day: float,
    effective_hocl_mgL: float,
    basin_ec: float,
    ph: float,
) -> float:
    cu_norm = cu_ppb / max(DEFAULT_PERMIT_LIMITS["cu_ppb"], 1e-6)
    zn_norm = zn_ppb / max(DEFAULT_PERMIT_LIMITS["zn_ppb"], 1e-6)
    biocide_norm = biocide_mgL / max(DEFAULT_PERMIT_LIMITS["trc_mgL"], 1e-6)
    water_norm = blowdown_m3_day / 100.0
    phosphorus_norm = phosphorus_mgL / 2.0

    score = (
        cu_norm * 4.0
        + zn_norm * 2.5
        + biocide_norm * 2.0
        + phosphorus_norm * 0.8
        + water_norm * 1.2
    )

    # Constraint penalties to keep recommendations operationally realistic.
    if effective_hocl_mgL < 0.2:
        score += 10.0
    if basin_ec > 5000:
        score += 3.0
    if ph < 7.5 or ph > 9.0:
        score += 2.0
    if cu_ppb > DEFAULT_PERMIT_LIMITS["cu_ppb"] * 4.0:
        score += 8.0
    return score

