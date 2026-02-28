from __future__ import annotations

import asyncio

from coolsense.config.settings import get_settings
from coolsense.orchestrator.service import OrchestratorService


async def run_terminal_mode(seconds: int = 10) -> None:
    service = OrchestratorService(settings=get_settings())
    end_at = asyncio.get_event_loop().time() + seconds
    while asyncio.get_event_loop().time() < end_at:
        snap = await service.tick()
        print(
            f"[{snap['timestamp']}] compliant={snap['compliant']} "
            f"cu={snap['cu_ppb']:.1f} zn={snap['zn_ppb']:.1f} mode={snap['mode']}"
        )
        await asyncio.sleep(float(service.settings.get("poll_interval_seconds", 2)))


def main() -> None:
    asyncio.run(run_terminal_mode())


if __name__ == "__main__":
    main()
