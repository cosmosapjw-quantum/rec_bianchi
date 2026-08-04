from pathlib import Path
import json
import numpy as np
from hyrec_native_sparse_block import solve_snapshot
HERE=Path(__file__).resolve().parent
ledger=json.loads((HERE/"C3B1_ledger.json").read_text())
assert all(ledger["hard_gate_status"].values())
p=HERE/"native_sparse_block_snapshot.npz"
d=np.load(p)
x=solve_snapshot(p)
assert np.linalg.norm(x-d["direct_solution"])/np.linalg.norm(d["direct_solution"]) < 1e-12
assert np.max(np.abs(d["null_solution"])) == 0.0
print("C3B1 native sparse block: PASS")
