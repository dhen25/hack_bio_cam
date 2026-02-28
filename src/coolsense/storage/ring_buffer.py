from __future__ import annotations

from collections import deque
from typing import Any


class RingBuffer:
    def __init__(self, maxlen: int = 500) -> None:
        self._items: deque[dict[str, Any]] = deque(maxlen=maxlen)

    def append(self, item: dict[str, Any]) -> None:
        self._items.append(item)

    def latest(self) -> dict[str, Any] | None:
        if not self._items:
            return None
        return self._items[-1]

    def to_list(self) -> list[dict[str, Any]]:
        return list(self._items)
