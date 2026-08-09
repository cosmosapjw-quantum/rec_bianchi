#!/usr/bin/env python3
from pathlib import Path
import csv, hashlib, json
import numpy as np
ROOT=Path(__file__).resolve().parent
metrics=json.loads((ROOT/"NUMERICAL_METRICS.json").read_text())
rows=list(csv.DictReader((ROOT/"PHYSICAL_ACCEPTANCE_DT_SWEEP.csv").open(newline="")))
assert metrics["status"].startswith("PASS_P0_FALSE_CONVERGENCE_GATE_FIXED")
assert metrics["legacy_gate_false_pass_at_canonical_dt"]
assert metrics["corrected_generic_gate_rejects_canonical_parent"]
assert metrics["problem_specific_gate_rejects_canonical_parent"]
assert metrics["canonical_physical_gross_backward_error"] > 0.9
assert metrics["canonical_physical_number_relative_residual"] > 0.9
assert metrics["shifted_matrix_free_jvp_relative_residual"] < 1.0e-8
assert metrics["corrected_rescaling_invariance_relative_residual"] < 1.0e-12
assert metrics["legacy_rescaling_disagreement_factor"] > 1.0e15
assert len(rows) >= 80
with np.load(ROOT/"pr05c2c1b2b1b_physical_acceptance_gate_v071.npz") as data:
    assert data["physical_acceptance_metric"].max() >= 1.0
manifest={}
for line in (ROOT/"MANIFEST_SHA256.txt").read_text().splitlines():
    digest,name=line.split("  ",1);manifest[name]=digest
for name,digest in manifest.items():
    assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest
print(metrics["status"])
