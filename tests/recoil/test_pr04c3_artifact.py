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
    / "archive/expanded/Full_Bianchi_HyRec_PR04C3_common_ledger_v0_57"
)


def _read_csv(name: str) -> list[dict[str, str]]:
    with (ARTIFACT / name).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def test_pr04c3_artifact_closes_operator_contract_without_trajectory_claim() -> None:
    ledger = json.loads((ARTIFACT / "HARD_GATE_LEDGER.json").read_text())
    assert ledger["classification"] == "PR04C3_HARD_GATE_LEDGER"
    assert ledger["status"] == "PASS_PR04_OPERATOR_CONTRACT_COMPLETE_PR05_NEXT"
    assert ledger["PR04"] == "COMPLETE_OPERATOR_CONTRACT"
    assert all(item["passed"] for item in ledger["gates"])
    assert ledger["claim_boundary"]["state"] == "OPERATOR_VERIFICATION"
    assert not ledger["claim_boundary"]["native_com_trajectory_parity"]

    snapshots = _read_csv("COMPONENTWISE_SNAPSHOT_LEDGER.csv")
    assert [float(row["target_z"]) for row in snapshots] == [1300.0, 1100.0, 900.0]
    for row in snapshots:
        assert float(row["backward_error_relative"]) < 1.0e-11
        assert float(row["number_relative_residual"]) < 1.0e-11
        assert float(row["jvp_relative_error"]) < 1.0e-8
        assert float(row["native_direct_source_relative"]) < 1.0e-13
        assert float(row["native_schur_direct_relative"]) < 1.0e-13
        assert float(row["native_structural_flux_relative"]) < 3.0e-11
        assert float(row["transported_energy_residual_J_per_H"]) == 0.0
        assert float(row["interface_atom_source_J_per_H"]) == 0.0
        assert float(row["minimum_occupation"]) > 0.0
        assert float(row["collision_entropy_production"]) <= 0.0
        assert row["restart_exact"] == "True"


def test_pr04c3_common_ledger_and_manifest_are_exact() -> None:
    common = json.loads((ARTIFACT / "COMMON_INTERFACE_LEDGER.json").read_text())
    assert common["schema"] == "PR04C3_COMMON_INTERFACE_LEDGER_V1"
    assert [row["target_z"] for row in common["snapshots"]] == [1300.0, 1100.0, 900.0]
    assert common["componentwise_passed"]
    assert common["epsilon_common"] == 0.0
    assert common["state_classification"] == "operator_verification"
    assert common["direct_state_remap_used"] is False
    assert common["fitted_normalization_used"] is False

    for line in (ARTIFACT / "MANIFEST_SHA256.txt").read_text().splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        digest, relative = line.split("  ", 1)
        path = ARTIFACT / relative
        assert hashlib.sha256(path.read_bytes()).hexdigest() == digest

    completed = subprocess.run(
        [sys.executable, str(ARTIFACT / "verify_PR04C3.py")],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
