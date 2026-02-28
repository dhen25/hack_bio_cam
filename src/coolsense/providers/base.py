from __future__ import annotations

from typing import Protocol


class SensorProvider(Protocol):
    def read_all_nodes(self) -> dict:
        ...
