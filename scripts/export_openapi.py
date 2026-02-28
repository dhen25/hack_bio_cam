from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from coolsense.api.app import app


def main() -> None:
    output_path = Path("contracts/openapi.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    openapi_schema = app.openapi()
    output_path.write_text(json.dumps(openapi_schema, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"Exported OpenAPI to {output_path}")


if __name__ == "__main__":
    main()
