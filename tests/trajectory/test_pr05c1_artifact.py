from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[2]
ARTIFACT = ROOT / "archive/expanded/Full_Bianchi_HyRec_PR05C1_adaptive_canonical_macro_v0_62"
BUNDLE = ROOT / "archive/bundles/Full_Bianchi_HyRec_PR05C1_adaptive_canonical_macro_v0_62.zip"
DATA = ROOT / "data/pr05c1_adaptive_short_trajectory_v062.npz"


def test_pr05c1_artifact_is_complete_and_self_verifying() -> None:
    hard = json.loads((ARTIFACT / "HARD_GATE_LEDGER.json").read_text())
    assert hard["status"] == "PASS_PR05C1_ADAPTIVE_CANONICAL_MACRO_CONTROLLER_PR05C2_OPEN"
    assert all(item["passed"] for item in hard["gates"])
    assert hard["claim_boundary"]["full_com_interface_coupling"] is False
    assert hard["claim_boundary"]["source_derived_bianchi_boundary_speeds"] is False
    assert BUNDLE.is_file() and DATA.is_file()
    result = subprocess.run(
        [sys.executable, str(ARTIFACT / "verify_PR05C1.py")],
        cwd=ARTIFACT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_pr05c1_ledgers_keep_source_and_controller_evidence_separate() -> None:
    with (ARTIFACT / "SOURCE_CONDITIONED_MACRO_LEDGER.csv").open(newline="") as handle:
        source_rows = list(csv.DictReader(handle))
    with (ARTIFACT / "EVENT_CONTROLLER_LEDGER.csv").open(newline="") as handle:
        event_rows = list(csv.DictReader(handle))
    assert [int(row["target_z"]) for row in source_rows] == [1300, 1100, 900]
    assert all(row["typed_owner"] == "TYPED_CHARACTERISTIC_HISTORY" for row in source_rows)
    assert all(int(row["history_increment"]) == 1 for row in source_rows)
    assert {row["geometry"] for row in event_rows} == {
        "Bianchi-II",
        "VI_h-class-B",
        "VI_-1/9",
    }
    assert sum(int(row["event_count"]) for row in event_rows) == 3
    assert all(int(row["history_increment"]) == 4 for row in event_rows)


def test_pr05c1_manifest_and_repository_copy_match() -> None:
    for line in (ARTIFACT / "MANIFEST_SHA256.txt").read_text().splitlines():
        expected, relative = line.split("  ", 1)
        assert hashlib.sha256((ARTIFACT / relative).read_bytes()).hexdigest() == expected
    assert hashlib.sha256(DATA.read_bytes()).hexdigest() == hashlib.sha256(
        (ARTIFACT / DATA.name).read_bytes()
    ).hexdigest()
