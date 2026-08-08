from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
ARTIFACT = ROOT / "archive/expanded/Full_Bianchi_HyRec_PR05C2C1A_direct_compiler_characteristic_v0_66"


def test_pr05c2c1a_immutable_artifact_verifier() -> None:
    result = subprocess.run(
        [sys.executable, str(ARTIFACT / "verify_PR05C2C1A.py")],
        cwd=ARTIFACT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "PASS_PR05C2C1A" in result.stdout


def test_pr05c2c1a_claim_boundary_remains_bounded() -> None:
    metrics = json.loads((ARTIFACT / "NUMERICAL_METRICS.json").read_text())
    assert metrics["direct_node_count"] == 3
    assert metrics["full_withheld_same_cell_validation_completed"] is False
    assert metrics["physical_hyrec_emissivity_opacity_adapter_completed"] is False
    assert metrics["multi_macro_trajectory_completed"] is False
