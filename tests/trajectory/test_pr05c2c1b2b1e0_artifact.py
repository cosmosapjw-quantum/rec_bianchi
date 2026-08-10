from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

import numpy as np


ROOT = Path(__file__).resolve().parents[2]
NAME = "Full_Bianchi_HyRec_PR05C2C1B2B1E0_source_derived_bootstrap_parent_v0_73"
EXPANDED = ROOT / "archive" / "expanded" / NAME


def test_v073_artifact_claim_boundary_and_parent_payload() -> None:
    metrics = json.loads((EXPANDED / "NUMERICAL_METRICS.json").read_text())
    assert metrics["production_parent_validation_passed"]
    assert metrics["claim_boundary"] == "BOOTSTRAP_PARENT_NOT_COUPLED_MACRO_ENDPOINT"
    assert not metrics["coupled_macro_endpoint"]
    assert not metrics["history_commit_performed"]
    assert metrics["accepted_history_index"] == 5127
    assert metrics["accepted_history_count"] == 5128
    assert metrics["minimum_occupation"] > 0.0
    assert metrics["isotropy_residual"] == 0.0
    assert 900.0 < metrics["median_activity"] < 1100.0
    assert metrics["initial_physical_acceptance_metric"] > 1.0e-11

    with np.load(EXPANDED / "pr05c2c1b2b1e0_source_derived_parent_v073.npz") as data:
        assert data["occupation"].shape == (35, 26)
        assert np.min(data["occupation"]) > 0.0
        assert data["source_indices"].shape == (35,)
        assert data["parent_payload"].dtype == np.uint8


def test_v073_compact_verifier_passes() -> None:
    result = subprocess.run(
        [sys.executable, str(EXPANDED / "verify_PR05C2C1B2B1E0.py")],
        cwd=EXPANDED,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    assert result.returncode == 0, result.stdout
