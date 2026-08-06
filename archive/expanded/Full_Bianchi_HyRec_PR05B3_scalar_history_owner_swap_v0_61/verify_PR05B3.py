#!/usr/bin/env python3
from __future__ import annotations
import csv, hashlib, json
from pathlib import Path
root = Path(__file__).resolve().parent
hard = json.loads((root / "HARD_GATE_LEDGER.json").read_text())
assert hard["status"] == "PASS_PR05B3_SCALAR_HISTORY_OWNER_SWAP_PR05C_NEXT"
assert hard["PR05B3"] == "COMPLETE" and hard["PR05"] == "IN_PROGRESS"
assert all(item["passed"] for item in hard["gates"])
assert hard["claim_boundary"]["typed_history_is_sole_python_owner"] is True
with (root / "THREE_SNAPSHOT_OWNER_SWAP_LEDGER.csv").open(newline="", encoding="utf-8") as handle:
    rows = list(csv.DictReader(handle))
assert [float(row["target_z"]) for row in rows] == [1300.0, 1100.0, 900.0]
assert all(row["active_owner"] == "TYPED_CHARACTERISTIC_HISTORY" for row in rows)
with (root / "SCALAR_HISTORY_OWNERSHIP_MATRIX.csv").open(newline="", encoding="utf-8") as handle:
    owners = list(csv.DictReader(handle))
assert all(int(row["owner_count"]) == 1 for row in owners)
assert owners[0]["active_owner"] == "TYPED_CHARACTERISTIC_HISTORY"
repo = root.parents[2]
metrics = json.loads((root / "NUMERICAL_METRICS.json").read_text())
data = repo / "data/pr05b3_scalar_history_owner_swap_v061.npz"
assert data.is_file()
assert hashlib.sha256(data.read_bytes()).hexdigest() == hashlib.sha256((root / data.name).read_bytes()).hexdigest()
for line in (root / "MANIFEST_SHA256.txt").read_text().splitlines():
    if not line.strip() or line.startswith("#"):
        continue
    expected, relative = line.split("  ", 1)
    assert hashlib.sha256((root / relative).read_bytes()).hexdigest() == expected
print("PR-05B3 v0.61 artifact: PASS; scalar typed-history owner swap COMPLETE; PR-05C adaptive short trajectory OPEN")
