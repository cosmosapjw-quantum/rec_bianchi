#!/usr/bin/env python3
"""Write the deterministic REC-LOCAL-02 source-authority no-go record."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from full_bianchi_hyrec.trajectory.physical_split_reference import build_rec_local02_diagnostic


def main() -> int:
    result = build_rec_local02_diagnostic(ROOT)
    destination = (
        ROOT
        / "artifacts/trajectory/pr05c2c1b2b1e1c_recovery/rec_local02"
        / "REC_LOCAL_02_EXECUTION.json"
    )
    destination.parent.mkdir(parents=True, exist_ok=True)
    encoded = json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n"
    destination.write_text(encoded, encoding="utf-8")
    print(encoded, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
