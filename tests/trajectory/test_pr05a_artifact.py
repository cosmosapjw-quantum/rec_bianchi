from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
ARTIFACT = (
    ROOT
    / "archive/expanded/Full_Bianchi_HyRec_PR05A_primitive_rate_schema_v0_58"
)


def _rows(name: str) -> list[dict[str, str]]:
    with (ARTIFACT / name).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def test_pr05a_artifact_closes_schema_source_lock_and_bounded_dae_only() -> None:
    hard = json.loads((ARTIFACT / "HARD_GATE_LEDGER.json").read_text())
    assert hard["classification"] == "PR05A_HARD_GATE_LEDGER"
    assert hard["status"] == "PASS_PR05A_SCHEMA_SOURCE_LOCK_ONE_STEP_DAE_PR05B_NEXT"
    assert hard["PR05A"] == "COMPLETE"
    assert hard["PR05"] == "IN_PROGRESS"
    assert all(row["passed"] for row in hard["gates"])
    assert hard["claim_boundary"]["one_step_source_conditioned_dae"] is True
    assert hard["claim_boundary"]["native_time_dependent_trajectory"] is False
    assert hard["claim_boundary"]["flrw_history_parity"] is False

    rows = _rows("THREE_SNAPSHOT_PRIMITIVE_LEDGER.csv")
    assert [float(row["target_z"]) for row in rows] == [1300.0, 1100.0, 900.0]
    for row in rows:
        assert float(row["native_residual_relative"]) < 2.0e-13
        assert float(row["analytic_jvp_relative_error"]) < 1.0e-8
        assert float(row["implicit_backward_error"]) < 1.0e-11
        assert float(row["implicit_number_relative_change"]) < 1.0e-11
        assert float(row["saha_detailed_balance_relative"]) < 5.0e-13
        assert float(row["minimum_physical_state"]) > 0.0
        assert float(row["photon_atom_energy_residual_W_m3"]) == 0.0
        assert row["m_matrix_pass"] == "True"
        assert row["restart_exact"] == "True"
        assert row["interface_enabled"] == "False"


def test_pr05a_source_registry_ownership_and_manifest_are_fail_closed() -> None:
    registry = _rows("PRIMITIVE_RATE_SOURCE_REGISTRY.csv")
    assert {row["public_name"] for row in registry} == {
        "alpha_2s",
        "alpha_2p",
        "delta_alpha_2s",
        "delta_alpha_2p",
        "beta_2s",
        "beta_2p",
        "R_2p2s",
        "A1s",
        "A2s",
        "A3s3d",
        "A4s4d",
    }
    assert all(len(row["source_sha256"]) == 64 for row in registry)
    delta = [row for row in registry if row["public_name"].startswith("delta_alpha")]
    assert all("not a derivative" in row["semantics"] for row in delta)

    ownership = _rows("OWNERSHIP_REMOVAL_MATRIX.csv")
    assert ownership
    assert all(row["current_owner"] for row in ownership)
    compressed = {
        "sobolev_lya_escape",
        "native_A1s_diffusion",
        "completed_Tvv_schur",
        "scalar_Dfplus_history_feedback",
    }
    assert all(row["removed"] == "False" for row in ownership if row["term"] in compressed)

    for line in (ARTIFACT / "MANIFEST_SHA256.txt").read_text().splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        digest, relative = line.split("  ", 1)
        assert hashlib.sha256((ARTIFACT / relative).read_bytes()).hexdigest() == digest

    completed = subprocess.run(
        [sys.executable, str(ARTIFACT / "verify_PR05A.py")],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
