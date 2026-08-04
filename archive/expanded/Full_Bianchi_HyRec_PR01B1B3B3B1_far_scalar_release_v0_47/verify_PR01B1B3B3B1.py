from pathlib import Path
import json,numpy as np
HERE=Path(__file__).resolve().parent
ledger=json.loads((HERE/"PR01B1B3B3B1_ledger.json").read_text())
for key,value in ledger["hard_gate_status"].items():
    if key in {"exterior_exterior_collision","PR01C_background_adapter"}: assert not value
    else: assert value
data=np.load(HERE/"far_scalar_release.npz")
S=data["pair_moments_m3_sInv"]
assert S.shape==(25,35,35)
assert np.max(np.abs(S-np.swapaxes(S,1,2)))<1e-12*(np.max(np.abs(S))+1e-300)
assert np.min(S[0])>=0
print("PR01B1-B3B3B1 far scalar release: PASS")
