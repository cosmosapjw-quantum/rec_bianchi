#!/usr/bin/env python3
import csv, hashlib, json
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parent
m=json.loads((ROOT/"NUMERICAL_METRICS.json").read_text())
assert m["status"]=='PASS_BOUNDED_NO_GO_DYNAMIC_ATOMIC_MACRO_OWNERSHIP_OVERLAP_SPLIT_DOMAIN_REPLACEMENT_REQUIRED'
assert m["native_virtual_count"]==311
assert m["com_interior_native_count"]==8
assert m["com_interior_native_indices"]==list(range(136,144))
assert m["diffusion_inside_edge_count"]==6
assert m["diffusion_cross_edge_count"]==2
assert m["diffusion_outside_edge_count"]==70
assert m["canonical_up_rate_interior_fraction"]>0.97
assert m["canonical_down_rate_interior_fraction"]>0.97
assert m["real_to_virtual_abs_interior_fraction"]>0.90
assert m["virtual_to_real_abs_interior_fraction"]>0.90
assert not m["current_v074_ready"]
assert not m["naive_dynamic_atomic_ready"]
assert m["contract_witness_ready"]
assert m["contract_witness_only"]
assert m["no_fitted_normalization"]
assert m["no_native_cell_inference"]
assert m["dynamic_macro_not_executed"]
assert len(list(csv.DictReader((ROOT/"NATIVE_POINT_SUPPORT.csv").open())))==311
with np.load(ROOT/"pr05c2c1b2b1e1b0_dynamic_macro_ownership_v075.npz") as data:
    assert data["energy_eV"].shape==(311,)
    assert int(np.sum(data["inside_com_support"]))==8
for line in (ROOT/"MANIFEST_SHA256.txt").read_text().splitlines():
    digest,name=line.split("  ",1)
    assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest
print(m["status"])
