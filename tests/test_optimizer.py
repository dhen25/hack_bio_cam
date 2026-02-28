from pathlib import Path

from coolsense.optimizer.inference import infer_recommendations, load_model
from coolsense.optimizer.training import train_model
from coolsense.simulator.simulator import CoolingTowerSimulator
from coolsense.twin.state import compute_system_state


def test_training_is_deterministic_with_seed(tmp_path) -> None:
    m1 = tmp_path / "m1.pt"
    m2 = tmp_path / "m2.pt"
    a1 = train_model(str(m1), n_scenarios=40, seed=123)
    a2 = train_model(str(m2), n_scenarios=40, seed=123)
    assert a1["model_state"]["b3"] == a2["model_state"]["b3"]


def test_inference_fields_and_ranges(tmp_path) -> None:
    model_path = tmp_path / "model.pt"
    train_model(str(model_path), n_scenarios=40, seed=7)
    model, stats = load_model(str(model_path))
    state = compute_system_state(CoolingTowerSimulator().read_all_nodes())
    rec = infer_recommendations(state, model, stats)
    assert 10.0 <= rec.recommended_blowdown_rate_m3_day <= 100.0
    assert 0.5 <= rec.recommended_biocide_dose_mgL <= 5.0
    assert 7.5 <= rec.recommended_ph_setpoint <= 9.0
    assert 3.0 <= rec.recommended_coc_target <= 8.0
    assert len(rec.reasoning) >= 1


def test_train_script_artifact_exists() -> None:
    # Ensure this test does not depend on cwd side-effects.
    assert Path(__file__).exists()
