from __future__ import annotations

from coolsense.providers.base import SensorProvider
from coolsense.simulator.simulator import CoolingTowerSimulator


class SimulatorProvider(SensorProvider):
    def __init__(self, simulator: CoolingTowerSimulator | None = None) -> None:
        self.simulator = simulator or CoolingTowerSimulator()

    def read_all_nodes(self) -> dict:
        return self.simulator.read_all_nodes()
