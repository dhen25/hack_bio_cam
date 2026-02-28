from coolsense.optimizer.score import compute_pollution_score


def test_penalties_increase_score() -> None:
    baseline = compute_pollution_score(
        cu_ppb=100,
        zn_ppb=100,
        biocide_mgL=0.3,
        phosphorus_mgL=0.5,
        blowdown_m3_day=40,
        effective_hocl_mgL=0.3,
        basin_ec=5000,
        ph=8.0,
    )
    bad = compute_pollution_score(
        cu_ppb=2500,
        zn_ppb=1400,
        biocide_mgL=1.2,
        phosphorus_mgL=2.5,
        blowdown_m3_day=90,
        effective_hocl_mgL=0.1,
        basin_ec=9000,
        ph=9.5,
    )
    assert bad > baseline
