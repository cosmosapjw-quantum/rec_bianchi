#!/usr/bin/env python3
from __future__ import annotations
import csv, hashlib, json
from pathlib import Path

root = Path(__file__).resolve().parent
hard = json.loads((root / "HARD_GATE_LEDGER.json").read_text())
assert hard["status"] == "PASS_PR04_OPERATOR_CONTRACT_COMPLETE_PR05_NEXT"
assert hard["PR04"] == "COMPLETE_OPERATOR_CONTRACT"
assert all(row["passed"] for row in hard["gates"])
common = json.loads((root / "COMMON_INTERFACE_LEDGER.json").read_text())
assert common["componentwise_passed"] is True
assert common["epsilon_common"] == 0.0
assert [row["target_z"] for row in common["snapshots"]] == [1300.0, 1100.0, 900.0]
with (root / "COMPONENTWISE_SNAPSHOT_LEDGER.csv").open(newline="", encoding="utf-8") as handle:
    rows = list(csv.DictReader(handle))
assert len(rows) == 3
assert all(float(row["minimum_occupation"]) > 0.0 for row in rows)
assert all(float(row["transported_energy_residual_J_per_H"]) == 0.0 for row in rows)
for line in (root / "MANIFEST_SHA256.txt").read_text().splitlines():
    if not line.strip() or line.startswith("#"):
        continue
    digest, relative = line.split("  ", 1)
    assert hashlib.sha256((root / relative).read_bytes()).hexdigest() == digest
print("PR-04C3 v0.57 artifact: PASS; PR-04 operator contract COMPLETE; PR-05 OPEN")
