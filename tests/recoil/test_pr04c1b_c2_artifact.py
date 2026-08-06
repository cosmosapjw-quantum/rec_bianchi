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
    / "archive/expanded/Full_Bianchi_HyRec_PR04C1B_C2_coupled_interface_v0_56"
)


def _read_csv(name: str) -> list[dict[str, str]]:
    with (ARTIFACT / name).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def test_pr04c1b_c2_artifact_closes_declared_hard_gates() -> None:
    ledger = json.loads((ARTIFACT / "HARD_GATE_LEDGER.json").read_text())
    assert ledger["classification"] == "PR04C1B_C2_HARD_GATE_LEDGER"
    assert ledger["status"] == "PASS_PR04C1B_C2_PR04C3_OPEN"
    assert ledger["PR04"] == "IN_PROGRESS"
    assert all(item["passed"] for item in ledger["gates"])

    snapshots = _read_csv("THREE_SNAPSHOT_COUPLED_METRICS.csv")
    assert {float(row["target_z"]) for row in snapshots} == {900.0, 1100.0, 1300.0}
    for row in snapshots:
        assert row["converged"] == "True"
        assert float(row["backward_error_relative"]) < 1.0e-11
        assert float(row["number_relative_residual"]) < 1.0e-11
        assert float(row["minimum_occupation"]) > 0.0
        assert float(row["transported_energy_residual_J_per_H"]) == 0.0
        assert float(row["atom_energy_change_J_per_H"]) == 0.0

    jvp = _read_csv("JVP_REFERENCE.csv")
    assert max(float(row["relative_error"]) for row in jvp) < 1.0e-8

    branches = _read_csv("BIANCHI_BRANCH_AUDIT.csv")
    assert {row["model"] for row in branches} == {
        "Bianchi_II_large_shear",
        "Bianchi_VI_h_tilted_large_shear",
        "Bianchi_VI_minus_1_over_9_exceptional",
    }
    assert all(int(row["red_root_count"]) + int(row["blue_root_count"]) >= 1 for row in branches)


def test_pr04c1b_c2_restart_and_manifest_are_exact() -> None:
    restart = json.loads((ARTIFACT / "COUPLED_RESTART.json").read_text())
    assert restart["schema"] == "PR04C1B_C2_RESTART_V1"
    assert len(restart["snapshots"]) == 3
    assert all(snapshot["state"]["interface_enabled"] for snapshot in restart["snapshots"])

    for line in (ARTIFACT / "MANIFEST_SHA256.txt").read_text().splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        digest, relative = line.split("  ", 1)
        path = ARTIFACT / relative
        assert hashlib.sha256(path.read_bytes()).hexdigest() == digest

    completed = subprocess.run(
        [sys.executable, str(ARTIFACT / "verify_PR04C1B_C2.py")],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
