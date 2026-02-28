from __future__ import annotations


def concentration_model(node1_ec: float, node2_ec: float, makeup: dict[str, float]) -> tuple[float, dict[str, float]]:
    if node1_ec <= 0:
        coc = 1.0
    else:
        coc = max(1.0, min(12.0, node2_ec / node1_ec))

    # Conductivity-to-TDS factor varies with ionic composition; use 0.65 as a practical midpoint.
    estimated_tds = node2_ec * 0.65
    basin_chemistry = {
        "conductivity_uScm": node2_ec,
        "estimated_tds_mgL": estimated_tds,
        "estimated_makeup_cu_ppb": makeup["cu_ppb"] * coc,
        "estimated_makeup_zn_ppb": makeup["zn_ppb"] * coc,
        "calcium_mgL": makeup.get("calcium_mgL", 0.0) * coc,
        "magnesium_mgL": makeup.get("magnesium_mgL", 0.0) * coc,
        "silica_mgL": makeup.get("silica_mgL", 0.0) * coc,
        "chloride_mgL": makeup.get("chloride_mgL", 0.0) * coc,
        "sulfate_mgL": makeup.get("sulfate_mgL", 0.0) * coc,
    }
    return coc, basin_chemistry
