from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
ARTIFACT = ROOT / "archive/expanded/Full_Bianchi_HyRec_PR05B1_source_identifiable_DAE_native_time_measure_no_go_v0_59"


def test_pr05b1_artifact_is_bounded_no_go_with_three_componentwise_lanes() -> None:
    hard = json.loads((ARTIFACT / "HARD_GATE_LEDGER.json").read_text())
    assert hard["status"] == "PASS_BOUNDED_NO_GO_NATIVE_LOCAL_TIME_MEASURE_NOT_IDENTIFIED_PR05B2_CAUSAL_HISTORY_NEXT"
    assert hard["PR05B1"] == "COMPLETE_PASS_BOUNDED_NO_GO"
    assert hard["PR05B"] == "IN_PROGRESS"
    assert all(item["passed"] for item in hard["gates"])
    with (ARTIFACT / "THREE_SNAPSHOT_SOURCE_DAE_LEDGER.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        rows = list(csv.DictReader(handle))
    assert [float(row["target_z"]) for row in rows] == [1300.0, 1100.0, 900.0]
    assert all(int(row["differential_rows"]) == 1 for row in rows)
    assert all(int(row["algebraic_rows"]) == 313 for row in rows)
    assert all(row["native_local_time_measure_identifiable"] == "False" for row in rows)


def test_pr05b1_artifact_manifest_and_constructive_witness_are_exact() -> None:
    witness = json.loads((ARTIFACT / "NATIVE_TIME_MEASURE_NO_GO.json").read_text())
    assert witness["classification"] == "CONSTRUCTIVE_NATIVE_LOCAL_TIME_MEASURE_NONIDENTIFIABILITY"
    assert abs(float(witness["candidate_mass_ratio"]) - 2.0) < 2.0e-14
    assert float(witness["candidate_relative_difference"]) > 0.4
    for line in (ARTIFACT / "MANIFEST_SHA256.txt").read_text().splitlines():
        if not line or line.startswith("#"):
            continue
        expected, relative = line.split("  ", 1)
        assert hashlib.sha256((ARTIFACT / relative).read_bytes()).hexdigest() == expected
