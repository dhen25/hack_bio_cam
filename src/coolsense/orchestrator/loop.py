from __future__ import annotations

import asyncio

from coolsense.orchestrator.service import OrchestratorService


async def run_loop(service: OrchestratorService, stop_event: asyncio.Event) -> None:
    interval = float(service.settings.get("poll_interval_seconds", 2))
    while not stop_event.is_set():
        await service.tick()
        await asyncio.sleep(interval)
