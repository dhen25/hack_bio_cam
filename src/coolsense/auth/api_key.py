from __future__ import annotations

import os


def is_api_key_valid(provided_key: str | None) -> bool:
    expected_key = os.getenv("COOLSENSE_API_KEY", "").strip()
    allow_empty = os.getenv("COOLSENSE_ALLOW_EMPTY_API_KEY", "true").lower() in {"1", "true", "yes"}

    if not expected_key:
        return allow_empty
    return bool(provided_key) and provided_key == expected_key
