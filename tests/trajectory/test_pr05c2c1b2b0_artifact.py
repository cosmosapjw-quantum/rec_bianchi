from __future__ import annotations

import csv
import json
from pathlib import Path
import subprocess
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
ARTIFACT = (
    ROOT
    / "archive/expanded/Full_Bianchi_HyRec_PR05C2C1B2B0_macro_evidence_integrity_v0_69"
)
DATA = ROOT / "data/pr05c2c1b2b0_macro_evidence_integrity_v069.npz"


def test_macro_integrity_artifact_records_all_nine_lanes_and_two_boundary_closures() -> None:
    rows = list(csv.DictReader((ARTIFACT / "MACRO_EVIDENCE_INTEGRITY.csv").open(newline="")))
    assert len(rows) == 18
    assert {int(row["target_z"]) for row in rows} == {900, 1100, 1300}
    assert {row["bianchi_type"] for row in rows} == {"II", "VI_h", "VI_-1/9"}
    assert {row["boundary_closure"] for row in rows} == {
        "isotropic",
        "maximum_entropy_outward",
    }
    assert all(int(row["strictly_positive_parent_exists"]) == 0 for row in rows)
    assert min(int(row["nonpositive_parent_count"]) for row in rows) > 0
    assert min(float(row["recorded_dt_to_positivity_limit_ratio"]) for row in rows) > 1.0e9


def test_macro_integrity_artifact_downgrades_only_v064_macro_claim() -> None:
    gates = json.loads((ARTIFACT / "HARD_GATE_LEDGER.json").read_text())
    metrics = json.loads((ARTIFACT / "NUMERICAL_METRICS.json").read_text())
    assert gates["v064_artifact_bytes"] == "DURABLE_VERIFIED"
    assert gates["v064_nine_macro_convergence_claim"].startswith("SUPERSEDED")
    assert gates["v065_theory"] == "UNAFFECTED"
    assert gates["v066_v067_v068_source_network_adapters"] == "UNAFFECTED"
    assert metrics["v064_macro_convergence_claim_reusable"] is False
    assert metrics["downstream_theory_and_source_adapters_affected"] is False


def test_macro_integrity_public_npz_and_self_verifier() -> None:
    with np.load(DATA) as data:
        assert data["recorded_dt_to_positivity_limit_ratio"].shape == (18,)
        assert data["recorded_dt_to_positivity_limit_ratio"].min() > 1.0e9
        assert data["nonpositive_parent_count"].min() > 0
    result = subprocess.run(
        [sys.executable, str(ARTIFACT / "verify_PR05C2C1B2B0.py")],
        cwd=ARTIFACT,
        check=False,
    )
    assert result.returncode == 0
