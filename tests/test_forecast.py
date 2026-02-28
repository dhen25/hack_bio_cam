from coolsense.twin.forecast import forecast_from_history


def test_forecast_bounds_and_size() -> None:
    response = forecast_from_history([], horizon_hours=48)
    assert response.horizon_hours == 24
    assert len(response.points) == 24


def test_forecast_uses_recent_history() -> None:
    history = [{"cu_ppb": 11.0, "zn_ppb": 22.0, "chlorine_mgL": 0.9, "turbidity_node4": 7.0, "compliant": True}]
    response = forecast_from_history(history, horizon_hours=3)
    assert len(response.points) == 3
    assert response.points[0].predicted_cu_ppb == 11.0
