from __future__ import annotations

from coolsense.api.schemas import SystemState


def build_reasoning(state: SystemState) -> list[str]:
    reasons: list[str] = []
    if state.corrosion.severity_index > 0.4:
        reasons.append("Corrosion severity is elevated; increase blowdown and stabilize pH.")
    if state.biocide.effective_hocl_mgL < 0.2:
        reasons.append("Effective HOCl is low; increase biocide dose to maintain microbial control.")
    if not state.compliant:
        reasons.append("Compliance exceedances detected; adjust controls to bring discharge within limits.")
    if not reasons:
        reasons.append("System is stable; keep controls near current setpoints.")
    return reasons

