from coolsense.simulator.simulator import CoolingTowerSimulator
from coolsense.twin.biocide import biocide_model
from coolsense.twin.concentration import concentration_model
from coolsense.twin.state import compute_system_state


def test_coc_computation() -> None:
    coc, basin = concentration_model(node1_ec=500.0, node2_ec=2500.0, makeup={"cu_ppb": 10.0, "zn_ppb": 20.0})
    assert coc == 5.0
    assert basin["estimated_tds_mgL"] > 0


def test_hocl_fraction_lower_at_higher_ph() -> None:
    low_ph = biocide_model(2.0, 0.2, ph=7.2)
    high_ph = biocide_model(2.0, 0.2, ph=8.5)
    assert float(low_ph["effective_hocl_mgL"]) > float(high_ph["effective_hocl_mgL"])


def test_compute_state_coherent() -> None:
    sim = CoolingTowerSimulator()
    state = compute_system_state(sim.read_all_nodes())
    assert state.coc >= 1.0
    assert state.corrosion.cu_ppb >= 0.0
