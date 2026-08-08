#!/usr/bin/env python3
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import numpy as np
ROOT = Path(__file__).resolve().parent
STATUS = 'PASS_PR05C2C1A_DIRECT_NODAL_NETWORK_CHARACTERISTIC_FACE_SOLVER_SELECTED_WITHHELD_VALIDATION_PRECONDITIONER_NOT_SELECTED_MULTI_MACRO_OPEN'
def sha256(path):
    d=hashlib.sha256()
    with Path(path).open("rb") as h:
        for b in iter(lambda:h.read(1024*1024),b""): d.update(b)
    return d.hexdigest()
m=json.loads((ROOT/"NUMERICAL_METRICS.json").read_text())
g=json.loads((ROOT/"HARD_GATE_LEDGER.json").read_text())
assert m["status"] == STATUS
assert g["PR05C2C1A"] == "COMPLETE_BOUNDED_DIRECT_AND_CHARACTERISTIC_STAGE"
assert m["direct_node_count"] == 3 and m["total_direct_block_receipts"] == 1377
assert m["minimum_direct_scalar_conductance"] > 0
assert m["maximum_direct_pair_symmetry_residual"] < 1e-14
assert m["maximum_direct_be_action_relative_residual"] < 1e-12
assert m["maximum_direct_number_relative_residual"] < 1e-12
assert m["maximum_harmonic_gram_residual"] < 1e-12
assert m["reference_3000K_anchor_exact"] is True
assert m["maximum_selected_withheld_relative_error"] < 3e-3
assert m["maximum_face_frequency_relative_residual"] < 1e-12
assert m["minimum_manufactured_refinement_ratio"] > 3.5
assert m["entropy_graph_preconditioner_selected"] is False
assert m["full_withheld_same_cell_validation_completed"] is False
assert m["physical_hyrec_emissivity_opacity_adapter_completed"] is False
assert m["multi_macro_trajectory_completed"] is False
with np.load(ROOT/"pr05c2c1a_direct_compiler_characteristic_v066.npz",allow_pickle=False) as d:
    assert d["direct_temperature_K"].shape == (3,)
    assert d["withheld_relative_error"].shape == (10,)
manifest={}
for line in (ROOT/"MANIFEST_SHA256.txt").read_text().splitlines():
    digest,name=line.split("  ",1); manifest[name]=digest
for name,digest in manifest.items(): assert sha256(ROOT/name)==digest,name
print(STATUS)
