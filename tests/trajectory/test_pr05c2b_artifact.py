from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
ARTIFACT = (
    ROOT
    / "archive/expanded/Full_Bianchi_HyRec_PR05C2B_explicit_closure_optimized_macro_v0_64"
)
DATA = ROOT / "data/pr05c2b_explicit_closure_optimized_v064.npz"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


def test_pr05c2b_artifact_is_explicit_closure_not_source_identical() -> None:
    metrics = json.loads((ARTIFACT / "NUMERICAL_METRICS.json").read_text())
    gates = json.loads((ARTIFACT / "HARD_GATE_LEDGER.json").read_text())

    assert metrics["status"] == (
        "PASS_EXPLICIT_CLOSURE_WITH_UNCERTAINTY_"
        "OPTIMIZED_CANONICAL_MACRO_REFERENCE_PR05C2C_NEXT"
    )
    assert metrics["macro_lane_count"] == 9
    assert metrics["all_macro_lanes_converged"] is True
    assert metrics["source_identical_angular_reconstruction"] is False
    assert metrics["source_identical_thermodynamic_recompilation"] is False
    assert metrics["multi_macro_trajectory_completed"] is False
    assert metrics["maximum_macro_gross_backward_error"] < 1.0e-11
    assert metrics["maximum_macro_number_residual"] < 1.0e-11
    assert metrics["maximum_macro_energy_residual"] < 1.0e-11
    assert metrics["maximum_macro_jvp_residual"] < 1.0e-8
    assert metrics["minimum_macro_occupation"] > 0.0
    assert metrics["maximum_collision_entropy_production"] <= 0.0
    assert metrics["maximum_interface_atom_source_abs"] == 0.0
    assert metrics["maximum_collision_four_force_residual"] == 0.0
    assert metrics["maximum_direct_thermodynamic_closure_discrepancy"] > 0.25
    assert metrics["maximum_direct_thermodynamic_closure_discrepancy"] < 0.35
    assert gates["PR05C2B"] == "COMPLETE_PASS_EXPLICIT_CLOSURE_WITH_UNCERTAINTY"
    assert gates["PR05C2C"] == "OPEN"


def test_pr05c2b_optimization_evidence_is_operator_preserving() -> None:
    metrics = json.loads((ARTIFACT / "NUMERICAL_METRICS.json").read_text())
    performance = metrics["performance"]
    assert performance["dense_matrix_relative_difference"] < 1.0e-20
    assert performance["speedup_vectorized_full_vs_pair_loop"] > 10.0
    assert performance["speedup_action_only_vs_pair_loop"] > 20.0
    assert performance["speedup_vectorized_jvp_vs_pair_loop"] > 10.0
    assert performance["dense_assembly_speedup"] > 1.1


def test_pr05c2b_npz_and_manifest_are_exact() -> None:
    assert DATA.is_file()
    with np.load(DATA, allow_pickle=False) as data:
        assert data["macro_target_z"].shape == (9,)
        assert set(data["macro_target_z"].tolist()) == {900, 1100, 1300}
        assert float(np.max(data["macro_gross_backward_error"])) < 1.0e-11
        assert float(np.max(data["macro_number_residual"])) < 1.0e-11
        assert float(np.max(data["macro_energy_residual"])) < 1.0e-11

    entries: dict[str, str] = {}
    for line in (ARTIFACT / "MANIFEST_SHA256.txt").read_text().splitlines():
        digest, name = line.split("  ", 1)
        entries[name] = digest
    assert entries["pr05c2b_explicit_closure_optimized_v064.npz"] == sha256(
        ARTIFACT / "pr05c2b_explicit_closure_optimized_v064.npz"
    )
    assert sha256(DATA) == sha256(
        ARTIFACT / "pr05c2b_explicit_closure_optimized_v064.npz"
    )
    result = subprocess.run(
        [sys.executable, str(ARTIFACT / "verify_PR05C2B.py")],
        cwd=ARTIFACT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
