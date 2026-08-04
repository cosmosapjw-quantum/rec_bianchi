from pathlib import Path
import importlib.util
import json
import numpy as np

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location(
    "adapter", HERE/"hyrec2_adapter.py"
)
adapter=importlib.util.module_from_spec(spec)
spec.loader.exec_module(adapter)

snapshot=json.loads(
    (HERE/"hyrec2_rate_snapshot_3000K.json").read_text()
)
weights=np.asarray(snapshot["cubic_weights"])
assert abs(weights.sum()-1.0) < 1e-15
assert snapshot["iTR_zero_based"] == 89
assert abs(snapshot["Alpha_2s_cm3_s"]-2.100869404125195e-13) < 1e-27
assert abs(snapshot["Alpha_2p_cm3_s"]-5.52691480687963e-13) < 1e-27
assert abs(snapshot["Beta_2s_sInv"]-162.01858795609893) < 1e-11
assert abs(snapshot["Beta_2p_sInv"]-142.07815282028678) < 1e-11
assert abs(snapshot["R_2p_to_2s_sInv"]-768.4808925060993) < 1e-10
assert snapshot["R_2s_to_2p_sInv"] == 3.0*snapshot["R_2p_to_2s_sInv"]
assert snapshot["detailed_balance_residual_2s"] == 0.0
assert snapshot["detailed_balance_residual_2p"] == 0.0

contract=json.loads((HERE/"hyrec2_data_contract.json").read_text())
assert contract["virtual_state_table"]["shape"] == [311,5]
assert contract["effective_rate_tables"]["Alpha_inf.dat"]["shape"] == [100,40,4]
print("C3B0 HYREC-2 source lock: PASS")
