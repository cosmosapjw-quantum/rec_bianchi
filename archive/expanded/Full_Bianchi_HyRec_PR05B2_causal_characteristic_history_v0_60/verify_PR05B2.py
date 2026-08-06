#!/usr/bin/env python3
from __future__ import annotations
import csv, hashlib, json
from pathlib import Path
root = Path(__file__).resolve().parent
hard = json.loads((root / "HARD_GATE_LEDGER.json").read_text())
assert hard["status"] == "PASS_PR05B2_CAUSAL_HISTORY_BLOCK_PR05B3_NEXT"
assert hard["PR05B2"] == "COMPLETE" and hard["PR05"] == "IN_PROGRESS"
assert all(row["passed"] for row in hard["gates"])
with (root / "THREE_SNAPSHOT_CAUSAL_HISTORY_LEDGER.csv").open(newline="", encoding="utf-8") as handle:
    rows = list(csv.DictReader(handle))
assert [float(row["target_z"]) for row in rows] == [1300.0, 1100.0, 900.0]
assert all(int(row["query_count"]) == 313 for row in rows)
assert all(row["reject_exact"] == "True" and row["rollback_exact"] == "True" and row["restart_exact"] == "True" for row in rows)
metrics = json.loads((root / "NUMERICAL_METRICS.json").read_text())
assert metrics["scalar_history_replacement_contract_complete"] is True
assert metrics["compressed_term_owner_swap_performed"] is False
provenance = json.loads((root / "SOURCE_HISTORY_PROVENANCE.json").read_text())
repo = root.parents[2]
history_path = repo / provenance["npz_path"]
assert history_path.is_file()
assert history_path.stat().st_size == int(provenance["npz_size_bytes"])
assert hashlib.sha256(history_path.read_bytes()).hexdigest() == provenance["npz_sha256"]
for line in (root / "MANIFEST_SHA256.txt").read_text().splitlines():
    if not line.strip() or line.startswith("#"):
        continue
    expected, relative = line.split("  ", 1)
    assert hashlib.sha256((root / relative).read_bytes()).hexdigest() == expected
print("PR-05B2 v0.60 artifact: PASS; causal characteristic history COMPLETE; PR-05B3 ownership swap OPEN")
