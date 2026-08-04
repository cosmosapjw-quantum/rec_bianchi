from pathlib import Path
import json
import numpy as np

HERE=Path(__file__).resolve().parent
ledger=json.loads((HERE/"coupled_boundary_ledger.json").read_text())
assert all(ledger["hard_gate_status"].values())
assert ledger["FLRW_regression"] == {
 "red_outflow":26,"red_inflow":0,
 "blue_outflow":0,"blue_inflow":26
}
assert np.max(np.abs(
 ledger["combined_step"]["total_four_momentum_residual"]
)) < 1e-11
print("D1C-C2 coupled boundary regressions: PASS")
