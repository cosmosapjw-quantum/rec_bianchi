from pathlib import Path
import json,numpy as np
HERE=Path(__file__).resolve().parent
ledger=json.loads((HERE/"PR03_ledger.json").read_text())
assert ledger["status"]=="PASS_PR03_COMPLETE"
assert all(ledger["hard_gate_status"].values())
data=np.load(HERE/"full_scalar_com_khw_v050.npz",allow_pickle=False)
S=data["pair_moments_m3_sInv"]
assert S.shape==(25,35,35)
assert np.min(S[0])>=0
assert np.max(np.abs(S-np.swapaxes(S,1,2)))<2e-12*(np.max(np.abs(S))+1e-300)
assert data["amplitude_lane"].item()=="full_bound_continuum_seagull_interference"
print("PR-03 full scalar COM-KHW: PASS")
