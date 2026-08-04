from pathlib import Path
import json
import numpy as np

HERE=Path(__file__).resolve().parent
ledger=json.loads((HERE/'C3A_ledger.json').read_text())
assert all(ledger['hard_gate_status'].values())
reg=np.load(HERE/'true_kernel_regression.npz')
assert np.all(reg['eta'] >= 0)
assert np.all(reg['chi'] >= reg['eta'])
breg=np.load(HERE/'bianchi_structure_registry.npz',allow_pickle=True)
assert len(breg['type_names']) == 11
print('C3A physical true kernel and Bianchi registry: PASS')
