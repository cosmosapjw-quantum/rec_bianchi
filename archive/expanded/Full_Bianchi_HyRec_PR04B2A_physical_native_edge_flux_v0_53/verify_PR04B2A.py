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
ledger=json.loads((HERE/"PR04B2A_ledger.json").read_text())
assert ledger["status"]=="PASS_PR04B2A_PHYSICAL_NATIVE_EDGE_FLUX_PR04B2B_OPEN"
assert all(ledger["hard_gate_status"].values())
assert ledger["decision"]["PR04"]=="IN_PROGRESS"
assert ledger["decision"]["native_proxy_as_photon_cell"]=="FORBIDDEN"
assert ledger["decision"]["direct_COM_KHW_native_parity"]=="OPEN_FAIL_CLOSED"
with np.load(HERE/"original_hyrec_physical_flux_v053.npz",allow_pickle=False) as d:
    assert str(d["canonical_archive_sha256"].item())=="48cd597519606cdafd0ee6405b781d28467cd323278d16596055a8d0577a1d27"
    assert d["transport_edge_flux_sInv_per_H"].shape==(311,)
    assert d["source_spectral_moments_Hz"].shape==(5,)
    assert float(np.min(d["implicit_stress_occupation"]))>0
    assert float(np.min(d["explicit_stress_occupation"]))<0
print("PR-04B2A physical native edge flux: PASS; PR-04B2B common partition OPEN")
