from __future__ import annotations

import math
import random


def _relu(x: float) -> float:
    return x if x > 0 else 0.0


def _sigmoid(x: float) -> float:
    return 1.0 / (1.0 + math.exp(-x))


class CoolSenseOptimizer:
    """Lightweight 16->32->16->4 feedforward model."""

    def __init__(self, seed: int = 42) -> None:
        rng = random.Random(seed)
        self.w1 = [[rng.uniform(-0.1, 0.1) for _ in range(16)] for _ in range(32)]
        self.b1 = [0.0 for _ in range(32)]
        self.w2 = [[rng.uniform(-0.1, 0.1) for _ in range(32)] for _ in range(16)]
        self.b2 = [0.0 for _ in range(16)]
        self.w3 = [[rng.uniform(-0.1, 0.1) for _ in range(16)] for _ in range(4)]
        self.b3 = [0.0 for _ in range(4)]

    def forward(self, x: list[float]) -> list[float]:
        h1 = [_relu(sum(w * v for w, v in zip(row, x)) + b) for row, b in zip(self.w1, self.b1)]
        h2 = [_relu(sum(w * v for w, v in zip(row, h1)) + b) for row, b in zip(self.w2, self.b2)]
        return [_sigmoid(sum(w * v for w, v in zip(row, h2)) + b) for row, b in zip(self.w3, self.b3)]

    @staticmethod
    def denormalize_outputs(y: list[float]) -> dict[str, float]:
        return {
            "recommended_blowdown_rate_m3_day": 10.0 + y[0] * 90.0,
            "recommended_biocide_dose_mgL": 0.5 + y[1] * 4.5,
            "recommended_ph_setpoint": 7.5 + y[2] * 1.5,
            "recommended_coc_target": 3.0 + y[3] * 5.0,
        }

