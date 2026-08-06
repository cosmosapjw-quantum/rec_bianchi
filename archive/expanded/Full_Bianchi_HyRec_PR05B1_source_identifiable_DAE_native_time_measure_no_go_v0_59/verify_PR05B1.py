#!/usr/bin/env python3
from __future__ import annotations
import csv, hashlib, json
from pathlib import Path
root = Path(__file__).resolve().parent
hard = json.loads((root / "HARD_GATE_LEDGER.json").read_text())
assert hard["status"] == "PASS_BOUNDED_NO_GO_NATIVE_LOCAL_TIME_MEASURE_NOT_IDENTIFIED_PR05B2_CAUSAL_HISTORY_NEXT"
assert hard["PR05B1"] == "COMPLETE_PASS_BOUNDED_NO_GO" and hard["PR05B"] == "IN_PROGRESS"
assert all(row["passed"] for row in hard["gates"])
with (root / "THREE_SNAPSHOT_SOURCE_DAE_LEDGER.csv").open(newline="", encoding="utf-8") as handle:
    rows = list(csv.DictReader(handle))
assert [float(row["target_z"]) for row in rows] == [1300.0, 1100.0, 900.0]
assert all(int(row["differential_rows"]) == 1 and int(row["algebraic_rows"]) == 313 for row in rows)
assert all(row["native_local_time_measure_identifiable"] == "False" for row in rows)
no_go = json.loads((root / "NATIVE_TIME_MEASURE_NO_GO.json").read_text())
assert abs(float(no_go["candidate_mass_ratio"]) - 2.0) < 2e-14
for line in (root / "MANIFEST_SHA256.txt").read_text().splitlines():
    if not line.strip() or line.startswith("#"):
        continue
    expected, relative = line.split("  ", 1)
    assert hashlib.sha256((root / relative).read_bytes()).hexdigest() == expected
print("PR-05B1 v0.59 artifact: PASS_BOUNDED_NO_GO; source-identifiable DAE complete; PR-05B2 causal history OPEN")
