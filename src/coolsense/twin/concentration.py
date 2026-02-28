from __future__ import annotations


def concentration_model(node1_ec: float, node2_ec: float, makeup: dict[str, float]) -> tuple[float, dict[str, float]]:
    if node1_ec <= 0:
        coc = 1.0
    else:
        coc = max(1.0, min(12.0, node2_ec / node1_ec))

    basin_chemistry = {
        "estimated_tds_mgL": node2_ec * 0.65,
        "estimated_makeup_cu_ppb": makeup["cu_ppb"] * coc,
        "estimated_makeup_zn_ppb": makeup["zn_ppb"] * coc,
    }
    return coc, basin_chemistry
