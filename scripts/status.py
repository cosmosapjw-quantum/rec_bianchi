#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
state = json.loads((ROOT / "state/PROJECT_STATE.json").read_text())
print(json.dumps(state, indent=2))
print("\nGit status:")
try:
    print(
        subprocess.check_output(
            ["git", "status", "--short", "--branch"],
            cwd=ROOT,
            text=True,
        )
    )
except Exception as error:
    print(f"git status unavailable: {error}")
