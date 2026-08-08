#!/usr/bin/env python3
from pathlib import Path
import csv, hashlib, json
import numpy as np
ROOT=Path(__file__).resolve().parent
rows=list(csv.DictReader((ROOT/"MACRO_EVIDENCE_INTEGRITY.csv").open(newline="")))
metrics=json.loads((ROOT/"NUMERICAL_METRICS.json").read_text())
assert metrics["status"].startswith("PASS_BOUNDED_NO_GO_V064_RECORDED_MACRO_ENDPOINTS")
assert len(rows)==18
assert all(int(r["strictly_positive_parent_exists"])==0 for r in rows)
assert min(int(r["nonpositive_parent_count"]) for r in rows)>0
assert min(float(r["recorded_dt_to_positivity_limit_ratio"]) for r in rows)>1.0e9
manifest={}
for line in (ROOT/"MANIFEST_SHA256.txt").read_text().splitlines():
    digest,name=line.split("  ",1);manifest[name]=digest
for name,digest in manifest.items():
    assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest
with np.load(ROOT/"pr05c2c1b2b0_macro_evidence_integrity_v069.npz") as data:
    assert data["recorded_dt_to_positivity_limit_ratio"].min()>1.0e9
print(metrics["status"])
