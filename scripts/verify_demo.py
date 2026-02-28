from __future__ import annotations

import os
import socket
import sys
from pathlib import Path

import httpx


def _port_open(host: str, port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.2)
        return sock.connect_ex((host, port)) == 0


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    model_path = Path(os.getenv("COOLSENSE_MODEL_PATH", str(root / "coolsense_model.pt")))
    api_base = os.getenv("COOLSENSE_API_BASE_URL", "http://localhost:8000").rstrip("/")

    issues: list[str] = []
    if not model_path.exists():
        issues.append(f"Missing model artifact: {model_path}")
    if not os.getenv("COOLSENSE_API_KEY"):
        issues.append("COOLSENSE_API_KEY is not set")
    if _port_open("127.0.0.1", 8000):
        try:
            r = httpx.get(f"{api_base}/health", timeout=2.0)
            if r.status_code != 200:
                issues.append(f"API unhealthy on :8000 (status={r.status_code})")
        except Exception as exc:  # pragma: no cover
            issues.append(f"API check failed: {exc}")
    if _port_open("127.0.0.1", 8501):
        issues.append("Port 8501 already in use")

    if issues:
        print("DEMO PREFLIGHT FAILED")
        for item in issues:
            print(f"- {item}")
        return 1

    print("DEMO PREFLIGHT OK")
    print(f"- model: {model_path}")
    print(f"- api_base: {api_base}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
