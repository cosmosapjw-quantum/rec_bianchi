from pathlib import Path
import csv
import json
import numpy as np

HERE=Path(__file__).resolve().parent
ledger=json.loads((HERE/"PR01C_ledger.json").read_text())
assert ledger["status"] == "PASS_PR01_COMPLETE"
assert all(ledger["hard_gate_status"].values())

models=list(csv.DictReader((HERE/"background_model_summary.csv").open()))
assert {row["bianchi_type"] for row in models} == {"II","VI_h","VI_-1/9"}
assert all(int(row["selected_root_count"]) >= 1 for row in models)

data=np.load(HERE/"background_frame_snapshots.npz")
assert data["directions"].shape == (26,3)
assert len(data["model_names"]) == 3
print("PR-01C background frame adapter: PASS")
