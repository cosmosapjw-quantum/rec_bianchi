#!/usr/bin/env python3
from pathlib import Path
import csv, hashlib, json
import numpy as np
HERE=Path(__file__).resolve().parent
for line in (HERE/"MANIFEST_SHA256.txt").read_text().splitlines():
    if not line.strip() or line.startswith("#"):
        continue
    expected,name=line.split("  ",1)
    got=hashlib.sha256((HERE/name).read_bytes()).hexdigest()
    assert got==expected,(name,got,expected)
ledger=json.loads((HERE/"HARD_GATE_LEDGER.json").read_text())
assert ledger["status"]=="PASS_PR04C1B_C2_PR04C3_OPEN"
assert ledger["PR04"]=="IN_PROGRESS"
assert all(item["passed"] for item in ledger["gates"])
with (HERE/"THREE_SNAPSHOT_COUPLED_METRICS.csv").open(newline="") as handle:
    rows=list(csv.DictReader(handle))
assert len(rows)==3
assert max(float(row["backward_error_relative"]) for row in rows)<1e-11
assert max(float(row["number_relative_residual"]) for row in rows)<1e-11
assert min(float(row["minimum_occupation"]) for row in rows)>0
with np.load(HERE/"pr04c_coupled_interface_v056.npz",allow_pickle=False) as data:
    assert data["updated_occupation"].shape==(3,35,26)
    assert np.all(data["updated_occupation"]>0)
print("PR-04C1B/C2 coupled interface: PASS; PR-04C3 OPEN")
