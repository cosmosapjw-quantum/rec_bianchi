#!/usr/bin/env python3
from __future__ import annotations
import csv, hashlib, json
from pathlib import Path
root=Path(__file__).resolve().parent
hard=json.loads((root/"HARD_GATE_LEDGER.json").read_text())
assert hard["status"]=="PASS_PR05C1_ADAPTIVE_CANONICAL_MACRO_CONTROLLER_PR05C2_OPEN"
assert hard["PR05C1"]=="COMPLETE" and hard["PR05C"]=="IN_PROGRESS"
assert all(item["passed"] for item in hard["gates"])
with (root/"SOURCE_CONDITIONED_MACRO_LEDGER.csv").open(newline="") as handle:
 rows=list(csv.DictReader(handle))
assert [int(row["target_z"]) for row in rows]==[1300,1100,900]
assert all(int(row["history_increment"])==1 for row in rows)
with (root/"EVENT_CONTROLLER_LEDGER.csv").open(newline="") as handle:
 events=list(csv.DictReader(handle))
assert len(events)==3 and sum(int(row["event_count"]) for row in events)==3
for line in (root/"MANIFEST_SHA256.txt").read_text().splitlines():
 if not line.strip() or line.startswith("#"): continue
 expected,relative=line.split("  ",1)
 assert hashlib.sha256((root/relative).read_bytes()).hexdigest()==expected
print("PR-05C1 v0.62 artifact: PASS; adaptive canonical-macro controller COMPLETE; PR-05C2 full coupling OPEN")
