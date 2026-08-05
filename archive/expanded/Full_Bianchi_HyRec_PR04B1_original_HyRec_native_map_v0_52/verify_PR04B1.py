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
ledger=json.loads((HERE/"PR04B1_ledger.json").read_text())
assert ledger["status"]=="PASS_PR04B1_ORIGINAL_HYREC_SOURCE_NATIVE_PROXY_MAP_PR04B2_OPEN"
assert all(ledger["hard_gate_status"].values())
assert ledger["decision"]["PR04"]=="IN_PROGRESS"
assert ledger["decision"]["native_raw_rate_substitution"]=="FORBIDDEN"
with np.load(HERE/"original_hyrec_native_v052.npz",allow_pickle=False) as d:
    assert str(d["archive_sha256"].item())=="48cd597519606cdafd0ee6405b781d28467cd323278d16596055a8d0577a1d27"
    assert d["native_generator_sInv"].shape==(81,81)
    assert d["schur_generator_sInv"].shape==(80,80)
    assert float(d["physical_number_map_relative_residual"])>1e-4
print("PR-04B1 original-HyRec native proxy map: PASS; PR-04B2 physical closure OPEN")
