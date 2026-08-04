from pathlib import Path
import json, numpy as np
HERE=Path(__file__).resolve().parent
ledger=json.loads((HERE/"PR01B1B3B3B0_ledger.json").read_text())
for key,value in ledger["hard_gate_status"].items():
    if key in {"far_direct_jump_closure","full_adaptive_L12_L20_L24"}:
        assert not value
    else:
        assert value
data=np.load(HERE/"exterior_interface_conductance.npz")
assert data["conductance_m3_sInv"].shape == (25,12,17)
assert np.min(data["conductance_m3_sInv"][0]) >= 0.0
assert np.max(np.abs(data["photon_transfer_weighted"]+data["hydrogen_transfer_weighted"])) == 0.0
print("PR01B1-B3B3B0 near-exterior interface: PASS")
