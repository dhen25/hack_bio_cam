from __future__ import annotations


def phosphorus_estimate(coc: float, inhibitor_phosphorus_mgL: float) -> float:
    return max(0.0, coc * inhibitor_phosphorus_mgL)
