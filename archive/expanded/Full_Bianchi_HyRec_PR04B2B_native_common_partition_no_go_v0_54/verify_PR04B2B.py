#!/usr/bin/env python3
from pathlib import Path
import hashlib, json
import numpy as np
HERE=Path(__file__).resolve().parent
manifest={}
for line in (HERE/"MANIFEST_SHA256.txt").read_text().splitlines():
    digest,name=line.split("  ",1); manifest[name]=digest
for name,expected in manifest.items():
    got=hashlib.sha256((HERE/name).read_bytes()).hexdigest()
    assert got==expected,(name,got,expected)
ledger=json.loads((HERE/"PR04B2B_ledger.json").read_text())
assert ledger["status"]=="PASS_PR04B2B_IDENTIFIABILITY_NO_GO_PR04C_OPEN"
assert all(ledger["hard_gate_status"].values())
assert ledger["decision"]["PR04"]=="IN_PROGRESS"
assert ledger["decision"]["direct_native_to_17_cell_map"]=="REJECTED_BY_SUPPORT_AND_IDENTIFIABILITY"
with np.load(HERE/"native_common_partition_v054.npz",allow_pickle=False) as data:
    assert data["target_uniform_moment_matrix"].shape==(5,17)
    assert data["production_energy_eV"].shape==(311,)
    assert data["high_resolution_energy_eV"].shape==(1493,)
    assert float(data["full_native_raw_moments_x"][2]/data["full_native_raw_moments_x"][0])>1e8
    assert np.min(data["positive_witness_plus"])>0
    assert np.min(data["positive_witness_minus"])>0
print("PR-04B2B native/common partition: PASS_NO_GO; PR-04C exchange contract OPEN")
