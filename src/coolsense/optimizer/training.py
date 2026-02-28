from __future__ import annotations

import json
import math
import random
from pathlib import Path
from typing import Any

from coolsense.optimizer.nn import CoolSenseOptimizer
from coolsense.optimizer.score import compute_pollution_score
from coolsense.simulator.simulator import CoolingTowerSimulator
from coolsense.twin.state import compute_system_state


def _extract_features(nodes: dict[str, Any], state) -> list[float]:
    raw = []
    for name in ("node1", "node2", "node3", "node4"):
        raw.extend([nodes[name]["ph"], nodes[name]["ec"], nodes[name]["turbidity"]])
    raw.extend([state.coc, state.corrosion.severity_index, state.corrosion.cu_ppb, state.biocide.total_chlorine_mgL])
    return raw


def _normalize_features(X: list[list[float]]) -> tuple[list[float], list[float], list[list[float]]]:
    cols = list(zip(*X))
    mean = [sum(col) / len(col) for col in cols]
    std = []
    Xn = []
    for i, col in enumerate(cols):
        var = sum((v - mean[i]) ** 2 for v in col) / len(col)
        std.append((var**0.5) or 1.0)
    for row in X:
        Xn.append([(row[i] - mean[i]) / std[i] for i in range(len(row))])
    return mean, std, Xn


def _search_optimal_controls(state) -> dict[str, float]:
    best_score = float("inf")
    best_controls = {
        "blowdown": 50.0,
        "biocide": 2.0,
        "ph": 8.0,
        "coc": 5.0,
    }
    baseline_phosphorus = float(state.basin_chemistry.get("phosphorus_mgL", 0.0))
    makeup_ec = float(state.nodes.node1.ec)
    ambient_temp = 35.0

    for blowdown_rate in (20.0, 35.0, 50.0, 65.0, 80.0, 95.0):
        for biocide_dose in (0.8, 1.5, 2.2, 3.0, 4.0):
            for target_ph in (7.6, 8.0, 8.4, 8.8):
                for target_coc in (3.2, 4.2, 5.2, 6.2, 7.2):
                    est_cu = 10 ** (-0.5 * target_ph + 6.0)
                    est_zn = 10 ** (-0.4 * target_ph + 5.5)
                    temp_factor = 2 ** ((ambient_temp - 25.0) / 20.0)
                    est_cu *= temp_factor
                    est_zn *= temp_factor

                    hocl_frac = 1.0 / (1.0 + 10 ** (target_ph - 7.54))
                    total_biocide = biocide_dose * math.exp(-0.2 * 2.0)
                    effective_hocl = total_biocide * hocl_frac
                    est_basin_ec = makeup_ec * target_coc

                    phosphorus_scale = target_coc / max(state.coc, 1e-6)
                    est_phosphorus = baseline_phosphorus * phosphorus_scale
                    score = compute_pollution_score(
                        cu_ppb=est_cu,
                        zn_ppb=est_zn,
                        biocide_mgL=total_biocide,
                        phosphorus_mgL=est_phosphorus,
                        blowdown_m3_day=blowdown_rate,
                        effective_hocl_mgL=effective_hocl,
                        basin_ec=est_basin_ec,
                        ph=target_ph,
                    )
                    if score < best_score:
                        best_score = score
                        best_controls = {
                            "blowdown": blowdown_rate,
                            "biocide": biocide_dose,
                            "ph": target_ph,
                            "coc": target_coc,
                        }
    return best_controls


def generate_training_data(n_scenarios: int = 500, seed: int = 42) -> tuple[list[list[float]], list[list[float]]]:
    random.seed(seed)
    sim = CoolingTowerSimulator()
    X: list[list[float]] = []
    Y: list[list[float]] = []

    for _ in range(n_scenarios):
        nodes = sim.read_all_nodes()
        state = compute_system_state(nodes)
        x = _extract_features(nodes, state)
        best = _search_optimal_controls(state)
        y = [
            (best["blowdown"] - 10.0) / 90.0,
            (best["biocide"] - 0.5) / 4.5,
            (best["ph"] - 7.5) / 1.5,
            (best["coc"] - 3.0) / 5.0,
        ]
        X.append(x)
        Y.append(y)
    return X, Y


def train_model(model_path: str = "coolsense_model.pt", n_scenarios: int = 500, seed: int = 42) -> dict[str, Any]:
    X, Y = generate_training_data(n_scenarios=n_scenarios, seed=seed)
    x_mean, x_std, Xn = _normalize_features(X)
    model = CoolSenseOptimizer(seed=seed)

    # Minimal fitting: set final bias to label mean for stable deterministic outputs.
    y_mean = [sum(row[i] for row in Y) / len(Y) for i in range(4)]
    model.b3 = [0.0 if y <= 0 or y >= 1 else (-(1 / y - 1)) for y in y_mean]

    artifact = {
        "meta": {"n_scenarios": n_scenarios, "seed": seed, "model_type": "lightweight_mlp_16_32_16_4"},
        "x_mean": x_mean,
        "x_std": x_std,
        "model_state": {"b3": model.b3},
        "sample_count": len(Xn),
    }
    Path(model_path).write_text(json.dumps(artifact, indent=2), encoding="utf-8")
    return artifact
