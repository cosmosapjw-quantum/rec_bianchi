#!/usr/bin/env python3
import csv, hashlib, json
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parent
m=json.loads((ROOT/"NUMERICAL_METRICS.json").read_text())
assert m["status"]=='PASS_PR05C2C1B2B1E1A_SOURCE_CONDITIONED_SINGLE_COM_MACRO_ROUNDOFF_LIMITED_ROOT_ATOMIC_HISTORY_COUPLING_OPEN'
assert m["strict_positivity"]
assert m["final_gross_backward_error"]<1e-11
assert m["final_number_relative_residual"]<1e-11
assert m["final_energy_gross_backward_error"]<1e-11
assert m["final_residual_roundoff_limited"]
assert m["final_energy_roundoff_limited"]
assert m["final_net_scaled_residual"]>1e-11
assert m["activity_shift_max_relative"]<1e-8
assert m["final_pair_loop_action_relative_residual"]<1e-8
assert m["final_pair_loop_four_force_gross_relative_residual"]<1e-12
assert m["final_collision_entropy_production"]<=0.0
assert not m["history_append_performed"]
assert not m["atomic_source_evolved"]
assert not m["native_boundary_evolved"]
assert not m["full_coupled_macro_endpoint"]
assert m["interior_red_boundary_root_count"]==0
assert m["interior_blue_boundary_root_count"]==0
assert m["initial_tie_resolved_by_endpoint_branch"]
assert len(list(csv.DictReader((ROOT/"ITERATION_LEDGER.csv").open())))>=3
with np.load(ROOT/"pr05c2c1b2b1e1a_single_com_macro_v074.npz") as data:
    assert data["parent_occupation"].shape==(35,26)
    assert data["candidate_occupation"].shape==(35,26)
    assert np.min(data["candidate_occupation"])>0.0
for line in (ROOT/"MANIFEST_SHA256.txt").read_text().splitlines():
    digest,name=line.split("  ",1)
    assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest
print(m["status"])
