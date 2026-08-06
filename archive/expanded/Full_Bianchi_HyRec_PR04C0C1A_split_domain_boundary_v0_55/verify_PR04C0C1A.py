#!/usr/bin/env python3
from pathlib import Path
import hashlib, json
import numpy as np
HERE=Path(__file__).resolve().parent
for line in (HERE/"MANIFEST_SHA256.txt").read_text().splitlines():
    expected,name=line.split("  ",1)
    got=hashlib.sha256((HERE/name).read_bytes()).hexdigest()
    assert got==expected,(name,got,expected)
ledger=json.loads((HERE/"PR04C0C1A_ledger.json").read_text())
assert ledger["status"]=="PASS_PR04C0_OWNERSHIP_PR04C1A_NATIVE_BOUNDARY_INSTRUMENTATION_PR04C1B_C2_OPEN"
assert all(ledger["hard_gate_status"].values())
assert ledger["decision"]["PR04"]=="IN_PROGRESS"
assert ledger["metrics"]["packet_count"]==6
assert ledger["metrics"]["current_history_endpoint_uses"]>=1
assert ledger["metrics"]["maximum_reconstruction_relative_residual"]<3e-13
with np.load(HERE/"pr04c_split_domain_boundary_v055.npz",allow_pickle=False) as data:
    assert data["target_z"].shape==(6,)
    assert data["number_flux_components_per_H_s"].shape==(6,3)
    assert np.all(data["number_flux_components_per_H_s"][:,0]>0)
    assert np.max(np.abs(data["residuals"][:,1:]))==0
print("PR-04C0/C1A split-domain boundary: PASS; PR-04C1B/C2 OPEN")
