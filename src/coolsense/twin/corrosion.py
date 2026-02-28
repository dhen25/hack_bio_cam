from __future__ import annotations


def corrosion_model(
    node2_ph: float,
    node3_ph: float,
    node2_ec: float,
    node3_ec: float,
    node2_turbidity: float,
    node3_turbidity: float,
    ambient_temp_c: float = 35.0,
) -> dict[str, float | str]:
    ph_ref = max(6.5, min(9.5, node3_ph))
    temp_factor = 2 ** ((ambient_temp_c - 25.0) / 20.0)
    turbidity_delta = max(0.0, node3_turbidity - node2_turbidity)
    ec_delta = max(0.0, node3_ec - node2_ec)

    # Simplified pH-solubility relationship inspired by Pourbaix trends.
    cu_ppb = 10 ** (-0.5 * ph_ref + 6.0)
    cu_ppb = max(5.0, min(cu_ppb, 1000.0)) * temp_factor

    zn_ppb = 10 ** (-0.4 * ph_ref + 5.5)
    zn_ppb = max(10.0, min(zn_ppb, 500.0)) * temp_factor

    if node2_turbidity > 0:
        turbidity_component = turbidity_delta / node2_turbidity
    else:
        turbidity_component = 0.0
    ec_component = ec_delta / max(node2_ec, 1.0)
    ph_drop_component = max(0.0, node2_ph - node3_ph) * 0.6
    severity = max(0.0, min(1.0, turbidity_component + ec_component * 4.0 + ph_drop_component))

    source = "post_hx_corrosion" if severity > 0.2 else "distributed_or_stable"

    return {
        "cu_ppb": cu_ppb,
        "zn_ppb": zn_ppb,
        "severity_index": severity,
        "source_diagnosis": source,
    }
