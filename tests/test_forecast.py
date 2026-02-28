from coolsense.twin.forecast import forecast_from_history


def test_forecast_bounds_and_size() -> None:
    response = forecast_from_history([], horizon_hours=48)
    assert response.horizon_hours == 24
    assert len(response.points) == 24


def test_forecast_uses_recent_history() -> None:
    history = [
        {
            "timestamp": "2026-01-01T00:00:00+00:00",
            "cu_ppb": 11.0,
            "zn_ppb": 22.0,
            "chlorine_mgL": 0.05,
            "turbidity_node4": 7.0,
            "compliant": True,
        }
    ]
    response = forecast_from_history(history, horizon_hours=3)
    assert len(response.points) == 3
    assert response.points[0].predicted_cu_ppb == 11.0


def test_forecast_trend_projects_rising_values() -> None:
    history = [
        {
            "timestamp": "2026-01-01T00:00:00+00:00",
            "cu_ppb": 10.0,
            "zn_ppb": 20.0,
            "chlorine_mgL": 0.04,
            "turbidity_node4": 5.0,
            "compliant": True,
        },
        {
            "timestamp": "2026-01-01T01:00:00+00:00",
            "cu_ppb": 18.0,
            "zn_ppb": 30.0,
            "chlorine_mgL": 0.06,
            "turbidity_node4": 8.0,
            "compliant": True,
        },
    ]
    response = forecast_from_history(history, horizon_hours=2)
    assert response.points[0].predicted_cu_ppb > 18.0
    assert response.points[1].predicted_turbidity_node4 > response.points[0].predicted_turbidity_node4
