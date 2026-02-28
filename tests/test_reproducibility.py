from coolsense.optimizer.training import train_model
from coolsense.utils.reproducibility import set_global_seed


def test_seed_control_for_training(tmp_path) -> None:
    set_global_seed(123)
    a1 = train_model(str(tmp_path / "a.pt"), n_scenarios=30, seed=123)
    set_global_seed(123)
    a2 = train_model(str(tmp_path / "b.pt"), n_scenarios=30, seed=123)
    assert a1["model_state"]["b3"] == a2["model_state"]["b3"]
