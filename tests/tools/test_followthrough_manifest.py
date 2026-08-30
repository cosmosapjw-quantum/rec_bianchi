from __future__ import annotations

import subprocess
import sys
from pathlib import Path


REPOSITORY = Path(__file__).resolve().parents[2]


def test_followthrough_manifest_matches_the_tracked_payload() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "research/continuation_20260830/verify_payload.py",
            "--root",
            ".",
            "--repo",
            ".",
        ],
        cwd=REPOSITORY,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert '"status": "PASS_DELIVERY_INTAKE_ONLY"' in result.stdout
