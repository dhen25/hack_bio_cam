from __future__ import annotations

import json
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


def generate_training_data(n_scenarios: int = 500, seed: int = 42) -> tuple[list[list[float]], list[list[float]]]:
    random.seed(seed)
    sim = CoolingTowerSimulator()
    X: list[list[float]] = []
    Y: list[list[float]] = []

    for _ in range(n_scenarios):
        nodes = sim.read_all_nodes()
        state = compute_system_state(nodes)
        x = _extract_features(nodes, state)

        # Lightweight heuristic "optimal controls" proxy for MVP training labels.
        best = {
            "blowdown": max(10.0, min(100.0, 45.0 + state.corrosion.severity_index * 35.0)),
            "biocide": max(0.5, min(5.0, 2.0 + (0.3 - state.biocide.effective_hocl_mgL) * 2.0)),
            "ph": max(7.5, min(9.0, 8.1 - state.corrosion.severity_index * 0.6)),
            "coc": max(3.0, min(8.0, 6.0 - state.corrosion.severity_index * 1.5)),
        }

        _ = compute_pollution_score(
            cu_ppb=state.corrosion.cu_ppb,
            zn_ppb=state.corrosion.zn_ppb,
            biocide_mgL=state.biocide.total_chlorine_mgL,
            phosphorus_mgL=state.basin_chemistry.get("phosphorus_mgL", 0.0),
            blowdown_m3_day=best["blowdown"],
            effective_hocl_mgL=state.biocide.effective_hocl_mgL,
            basin_ec=state.nodes.node2.ec,
            ph=state.nodes.node2.ph,
        )
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
