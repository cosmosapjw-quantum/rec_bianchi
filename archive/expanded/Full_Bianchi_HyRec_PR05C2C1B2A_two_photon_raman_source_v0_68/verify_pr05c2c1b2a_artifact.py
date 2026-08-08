#!/usr/bin/env python3
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parent
m=json.loads((ROOT/"NUMERICAL_METRICS.json").read_text())
g=json.loads((ROOT/"HARD_GATE_LEDGER.json").read_text())
r=json.loads((ROOT/"CHANNEL_REGISTRY.json").read_text())
assert m["status"].startswith("PASS_PR05C2C1B2A_CANONICAL_TWO_PHOTON_RAMAN_SOURCE_ADAPTER")
assert g["PR05C2C1B2A"]=="COMPLETE_CANONICAL_TWO_PHOTON_RAMAN_SOURCE_ADAPTER"
assert g["PR05C2C1B2B"]=="OPEN_PRECONDITIONER_MULTI_MACRO"
assert m["maximum_c_source_parity_relative"] < 3e-13
assert m["maximum_canonical_jvp_gross_relative"] < 1e-8
assert m["maximum_canonical_detailed_balance_relative"] < 1e-13
assert m["maximum_physical_planck_null_relative"] < 2e-13
assert m["maximum_physical_jvp_relative"] < 2e-8
assert r["2s"]["two_photon_bins"]==140 and r["2s"]["raman_bins"]==171
print("PR-05C2C1B2A v0.68 artifact: PASS; preconditioner and multi-macro OPEN")
