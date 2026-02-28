from __future__ import annotations


def corrosion_model(
    node2_ph: float,
    node2_turbidity: float,
    node3_turbidity: float,
    ambient_temp_c: float = 35.0,
) -> dict[str, float | str]:
    acidity_factor = max(0.0, 8.3 - node2_ph)
    temp_factor = 1.0 + max(0.0, ambient_temp_c - 25.0) * 0.03
    turbidity_delta = max(0.0, node3_turbidity - node2_turbidity)

    severity = min(1.0, acidity_factor * 0.35 + turbidity_delta * 0.02)
    cu_ppb = max(0.0, (30.0 + severity * 400.0) * temp_factor)
    zn_ppb = max(0.0, (40.0 + severity * 350.0) * temp_factor)
    source = "post_hx_corrosion" if turbidity_delta > 2.0 else "distributed_or_stable"

    return {
        "cu_ppb": cu_ppb,
        "zn_ppb": zn_ppb,
        "severity_index": severity,
        "source_diagnosis": source,
    }
