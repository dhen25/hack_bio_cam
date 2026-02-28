from __future__ import annotations


def blowdown_predictor(
    node4: dict[str, float],
    basin: dict[str, float],
    corrosion: dict[str, float | str],
    biocide: dict[str, float | str],
    phosphorus_mgL: float,
    permit_limits: dict[str, float],
    blowdown_m3_day: float = 50.0,
) -> dict:
    cu_ppb = float(basin.get("estimated_makeup_cu_ppb", 0.0)) + float(corrosion["cu_ppb"])
    zn_ppb = float(basin.get("estimated_makeup_zn_ppb", 0.0)) + float(corrosion["zn_ppb"])
    trc = float(biocide["total_chlorine_mgL"])
    ph = node4["ph"]
    turbidity = node4["turbidity"]
    conductivity = float(basin.get("conductivity_uScm", node4.get("ec", 0.0)))

    discharge = {
        "cu_ppb": cu_ppb,
        "zn_ppb": zn_ppb,
        "trc_mgL": trc,
        "ph": ph,
        "turbidity_ntu": turbidity,
        "conductivity_uScm": conductivity,
        "phosphorus_mgL": phosphorus_mgL,
    }
    mass_loadings = {
        "cu_g_day": cu_ppb * blowdown_m3_day * 1e-3,
        "zn_g_day": zn_ppb * blowdown_m3_day * 1e-3,
        "trc_g_day": trc * blowdown_m3_day,
        "phosphorus_g_day": phosphorus_mgL * blowdown_m3_day,
    }

    exceedances: list[dict[str, float | str]] = []

    def maybe_exceed(name: str, measured: float, limit: float) -> None:
        if measured > limit:
            exceedances.append(
                {
                    "parameter": name,
                    "measured": measured,
                    "limit": limit,
                    "severity": max(0.0, (measured - limit) / max(limit, 1e-6)),
                }
            )

    maybe_exceed("cu_ppb", cu_ppb, permit_limits["cu_ppb"])
    maybe_exceed("zn_ppb", zn_ppb, permit_limits["zn_ppb"])
    maybe_exceed("trc_mgL", trc, permit_limits["trc_mgL"])
    maybe_exceed("turbidity_ntu", turbidity, permit_limits["turbidity_ntu"])
    if ph < permit_limits["ph_min"]:
        exceedances.append(
            {
                "parameter": "ph_min",
                "measured": ph,
                "limit": permit_limits["ph_min"],
                "severity": (permit_limits["ph_min"] - ph) / permit_limits["ph_min"],
            }
        )
    if ph > permit_limits["ph_max"]:
        exceedances.append(
            {
                "parameter": "ph_max",
                "measured": ph,
                "limit": permit_limits["ph_max"],
                "severity": (ph - permit_limits["ph_max"]) / permit_limits["ph_max"],
            }
        )

    return {
        "discharge_composition": discharge,
        "mass_loadings_per_day": mass_loadings,
        "exceedances": exceedances,
        "compliant": len(exceedances) == 0,
        "n_exceedances": len(exceedances),
    }
