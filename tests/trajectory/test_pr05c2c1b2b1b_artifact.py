from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
import subprocess
import sys

import numpy as np


ROOT = Path(__file__).resolve().parents[2]
NAME = "Full_Bianchi_HyRec_PR05C2C1B2B1B_physical_acceptance_gate_v0_71"
ARTIFACT = ROOT / "archive" / "expanded" / NAME


def test_pr05c2c1b2b1b_artifact_closes_false_acceptance_gate() -> None:
    metrics = json.loads((ARTIFACT / "NUMERICAL_METRICS.json").read_text())
    assert metrics["status"].startswith("PASS_P0_FALSE_CONVERGENCE_GATE_FIXED")
    assert metrics["legacy_gate_false_pass_at_canonical_dt"]
    assert metrics["corrected_generic_gate_rejects_canonical_parent"]
    assert metrics["problem_specific_gate_rejects_canonical_parent"]
    assert metrics["canonical_physical_acceptance_metric"] > 0.9
    assert metrics["canonical_dt_to_parent_gate_dt_ratio"] > 1.0e15
    assert metrics["shifted_matrix_free_jvp_relative_residual"] < 1.0e-8
    assert metrics["corrected_rescaling_invariance_relative_residual"] < 1.0e-12
    assert metrics["legacy_rescaling_disagreement_factor"] > 1.0e15
    assert not metrics["canonical_macro_convergence_claimed"]


def test_pr05c2c1b2b1b_dt_sweep_and_plot_are_present() -> None:
    rows = list(
        csv.DictReader((ARTIFACT / "PHYSICAL_ACCEPTANCE_DT_SWEEP.csv").open())
    )
    assert len(rows) >= 80
    assert any(int(row["physical_gate_pass_1e_11"]) == 1 for row in rows)
    assert any(int(row["physical_gate_pass_1e_11"]) == 0 for row in rows)
    plot = ARTIFACT / "PHYSICAL_ACCEPTANCE_DIAGNOSTIC.png"
    assert plot.stat().st_size > 50_000


def test_pr05c2c1b2b1b_runtime_npz_and_manifest() -> None:
    with np.load(
        ARTIFACT / "pr05c2c1b2b1b_physical_acceptance_gate_v071.npz"
    ) as data:
        assert data["parent_occupation"].shape == (910,)
        assert data["physical_acceptance_metric"].max() >= 1.0
        assert data["legacy_unit_floor_backward_error"].max() < 1.0e-11

    manifest = {}
    for line in (ARTIFACT / "MANIFEST_SHA256.txt").read_text().splitlines():
        digest, name = line.split("  ", 1)
        manifest[name] = digest
    for name, digest in manifest.items():
        observed = hashlib.sha256((ARTIFACT / name).read_bytes()).hexdigest()
        assert observed == digest


def test_pr05c2c1b2b1b_compact_verifier() -> None:
    result = subprocess.run(
        [sys.executable, str(ARTIFACT / "verify_PR05C2C1B2B1B.py")],
        cwd=ARTIFACT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    assert result.returncode == 0, result.stdout
    assert "PASS_P0_FALSE_CONVERGENCE_GATE_FIXED" in result.stdout
