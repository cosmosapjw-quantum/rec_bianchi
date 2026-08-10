#!/usr/bin/env python3
import csv, hashlib, json
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parent
m=json.loads((ROOT/"NUMERICAL_METRICS.json").read_text())
assert m["status"]=='PASS_PR05C2C1B2B1E0_SOURCE_DERIVED_BOOTSTRAP_PARENT_COUPLED_SINGLE_MACRO_OPEN'
assert m["production_parent_validation_passed"]
assert not m["coupled_macro_endpoint"]
assert not m["history_commit_performed"]
assert m["minimum_occupation"]>0.0
assert m["isotropy_residual"]==0.0
assert 900.0<m["median_activity"]<1100.0
assert m["median_parent_to_q1_ratio"]>100.0
assert m["initial_physical_acceptance_metric"]>1.0e-11
assert len(list(csv.DictReader((ROOT/"POINT_CHARACTERISTIC_SAMPLES.csv").open())))==35
assert len(list(csv.DictReader((ROOT/"INTERFACE_SAMPLES.csv").open())))==2
with np.load(ROOT/"pr05c2c1b2b1e0_source_derived_parent_v073.npz") as data:
    assert data["occupation"].shape==(35,26)
    assert np.min(data["occupation"])>0.0
    assert data["parent_payload"].dtype==np.uint8
for line in (ROOT/"MANIFEST_SHA256.txt").read_text().splitlines():
    digest,name=line.split("  ",1)
    assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest
print(m["status"])
