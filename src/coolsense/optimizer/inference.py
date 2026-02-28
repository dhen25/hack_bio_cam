from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from coolsense.api.schemas import Recommendation, SystemState
from coolsense.optimizer.nn import CoolSenseOptimizer
from coolsense.optimizer.reasoning import build_reasoning


def _feature_vector(state: SystemState) -> list[float]:
    n = state.nodes
    return [
        n.node1.ph,
        n.node1.ec,
        n.node1.turbidity,
        n.node2.ph,
        n.node2.ec,
        n.node2.turbidity,
        n.node3.ph,
        n.node3.ec,
        n.node3.turbidity,
        n.node4.ph,
        n.node4.ec,
        n.node4.turbidity,
        state.coc,
        state.corrosion.severity_index,
        state.corrosion.cu_ppb,
        state.biocide.total_chlorine_mgL,
    ]


def load_model(model_path: str = "coolsense_model.pt") -> tuple[CoolSenseOptimizer, dict[str, Any]]:
    path = Path(model_path)
    if not path.exists():
        raise FileNotFoundError(f"Model file not found: {model_path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    model = CoolSenseOptimizer(seed=int(data["meta"]["seed"]))
    model.b3 = [float(v) for v in data["model_state"]["b3"]]
    return model, {"x_mean": data["x_mean"], "x_std": data["x_std"]}


def infer_recommendations(state: SystemState, model: CoolSenseOptimizer, stats: dict[str, Any]) -> Recommendation:
    x = _feature_vector(state)
    x_mean = stats["x_mean"]
    x_std = stats["x_std"]
    xn = [(x[i] - x_mean[i]) / (x_std[i] or 1.0) for i in range(len(x))]
    y = model.forward(xn)
    scaled = model.denormalize_outputs(y)
    return Recommendation(
        recommended_blowdown_rate_m3_day=scaled["recommended_blowdown_rate_m3_day"],
        recommended_biocide_dose_mgL=scaled["recommended_biocide_dose_mgL"],
        recommended_ph_setpoint=scaled["recommended_ph_setpoint"],
        recommended_coc_target=scaled["recommended_coc_target"],
        reasoning=build_reasoning(state),
    )
