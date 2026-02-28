from __future__ import annotations


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
    score = (
        cu_ppb * 1.0
        + zn_ppb * 0.8
        + biocide_mgL * 120.0
        + phosphorus_mgL * 100.0
        + blowdown_m3_day * 2.0
    )
    if effective_hocl_mgL < 0.2:
        score += 1000.0
    if basin_ec > 7000:
        score += 500.0
    if ph < 7.0 or ph > 9.2:
        score += 300.0
    if cu_ppb > 2000:
        score += 1000.0
    return score

