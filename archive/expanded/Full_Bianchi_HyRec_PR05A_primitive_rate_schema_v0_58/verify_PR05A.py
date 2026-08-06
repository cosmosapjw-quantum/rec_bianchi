#!/usr/bin/env python3
from __future__ import annotations
import csv, hashlib, json
from pathlib import Path
root = Path(__file__).resolve().parent
hard = json.loads((root / "HARD_GATE_LEDGER.json").read_text())
assert hard["status"] == "PASS_PR05A_SCHEMA_SOURCE_LOCK_ONE_STEP_DAE_PR05B_NEXT"
assert hard["PR05A"] == "COMPLETE" and hard["PR05"] == "IN_PROGRESS"
assert all(row["passed"] for row in hard["gates"])
with (root / "THREE_SNAPSHOT_PRIMITIVE_LEDGER.csv").open(newline="", encoding="utf-8") as handle:
    rows = list(csv.DictReader(handle))
assert [float(row["target_z"]) for row in rows] == [1300.0, 1100.0, 900.0]
assert all(float(row["native_residual_relative"]) < 2e-13 for row in rows)
assert all(float(row["implicit_backward_error"]) < 1e-11 for row in rows)
assert all(float(row["minimum_physical_state"]) > 0 for row in rows)
for line in (root / "MANIFEST_SHA256.txt").read_text().splitlines():
    if not line.strip() or line.startswith("#"):
        continue
    expected, relative = line.split("  ", 1)
    assert hashlib.sha256((root / relative).read_bytes()).hexdigest() == expected
print("PR-05A v0.58 artifact: PASS; schema/source lock and bounded one-step DAE COMPLETE; PR-05B OPEN")
