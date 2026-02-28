from __future__ import annotations

import asyncio

from coolsense.config.settings import get_settings
from coolsense.orchestrator.service import OrchestratorService


async def main() -> None:
    service = OrchestratorService(settings=get_settings())
    for _ in range(5):
        await service.tick()
    print(f"Seeded {len(service.history.to_list())} snapshots in memory.")


if __name__ == "__main__":
    asyncio.run(main())
