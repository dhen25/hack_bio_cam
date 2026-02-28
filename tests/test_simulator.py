from __future__ import annotations

import random

from coolsense.simulator.simulator import CoolingTowerSimulator


def test_read_all_nodes_shape_and_ranges() -> None:
    random.seed(7)
    sim = CoolingTowerSimulator()
    result = sim.read_all_nodes()
    for node in ("node1", "node2", "node3", "node4"):
        assert node in result
        assert 6.5 <= result[node]["ph"] <= 9.5
        assert 200 <= result[node]["ec"] <= 10000
        assert 0 <= result[node]["turbidity"] <= 500
    assert "timestamp" in result
    assert "_internal" in result


def test_corrosion_spike_affects_node3_turbidity() -> None:
    random.seed(11)
    sim = CoolingTowerSimulator()
    baseline = sim.read_all_nodes()
    base_delta = baseline["node3"]["turbidity"] - baseline["node2"]["turbidity"]
    sim.inject_event("corrosion_spike", magnitude=2.0)
    spiked = sim.read_all_nodes()
    spike_delta = spiked["node3"]["turbidity"] - spiked["node2"]["turbidity"]
    assert spike_delta > base_delta


def test_apply_recommendations_updates_controls() -> None:
    sim = CoolingTowerSimulator()
    sim.apply_recommendations(
        {
            "recommended_blowdown_rate_m3_day": 70.0,
            "recommended_biocide_dose_mgL": 3.0,
            "recommended_ph_setpoint": 8.6,
            "recommended_coc_target": 6.5,
        }
    )
    assert sim.blowdown_rate == 70.0
    assert sim.biocide_dose == 3.0
    assert sim.target_ph == 8.6
    assert sim.target_coc == 6.5
