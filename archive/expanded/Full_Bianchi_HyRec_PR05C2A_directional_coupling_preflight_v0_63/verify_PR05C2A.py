#!/usr/bin/env python3
import csv
import json
from pathlib import Path
root=Path(__file__).resolve().parent
metrics=json.loads((root/"NUMERICAL_METRICS.json").read_text())
hard=json.loads((root/"HARD_GATE_LEDGER.json").read_text())
no_go=json.loads((root/"COUPLING_IDENTIFIABILITY_NO_GO.json").read_text())
with (root/"SOURCE_DERIVED_BOUNDARY_ROOTS.csv").open(newline="", encoding="utf-8") as handle:
    roots=list(csv.DictReader(handle))
with (root/"THERMODYNAMIC_GRID_LEDGER.csv").open(newline="", encoding="utf-8") as handle:
    thermodynamic=list(csv.DictReader(handle))
assert metrics["status"].startswith("PASS_PR05C2A")
assert metrics["lane_count"] == 9
assert metrics["thermodynamic_lane_count"] == 3
assert metrics["bounded_no_go"] is True
assert len(roots) == 18
assert len({(row["model"], row["side"], row["root_index"]) for row in roots}) == len(roots)
assert len(thermodynamic) == 3
assert no_go["native_history_angular_rank"] == 1
assert no_go["minimum_number_momentum_rank"] == 4
assert no_go["exact_face_trace_rank"] == 26
assert no_go["thermodynamic_adapter_required"] is True
assert no_go["collision_block_preconditioner_required"] is True
assert all(item["passed"] for item in hard["gates"])
print(metrics["status"])
