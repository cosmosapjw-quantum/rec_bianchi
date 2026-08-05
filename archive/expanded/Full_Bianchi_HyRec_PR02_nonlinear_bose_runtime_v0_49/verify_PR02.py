from pathlib import Path
import csv
import hashlib
import json
import numpy as np

HERE = Path(__file__).resolve().parent
ledger = json.loads((HERE / "PR02_ledger.json").read_text())
assert ledger["status"] == "PASS_PR02_COMPLETE"
assert all(ledger["hard_gate_status"].values())

policies = list(csv.DictReader((HERE / "runtime_policy_summary.csv").open()))
assert {(row["selected_policy"], int(row["ell_max"])) for row in policies} == {
    ("finite_or_mixed_tilt", 12),
    ("nonlinear_even_shear", 20),
    ("directional_crossing", 24),
}
assert all(float(row["minimum_weight"]) > 0 for row in policies)

implicit = list(csv.DictReader((HERE / "implicit_update_summary.csv").open()))
assert all(float(row["explicit_trial_minimum"]) < 0 for row in implicit)
assert all(float(row["implicit_minimum"]) > 0 for row in implicit)
assert all(float(row["free_energy_change"]) < 0 for row in implicit)

data = np.load(HERE / "nonlinear_bose_runtime_evidence.npz")
assert set(data["scenario_names"].tolist()) == {
    "finite_or_mixed_tilt",
    "nonlinear_even_shear",
    "directional_crossing",
}

for line in (HERE / "MANIFEST_SHA256.txt").read_text().splitlines():
    expected, name = line.split("  ", 1)
    actual = hashlib.sha256((HERE / name).read_bytes()).hexdigest()
    assert actual == expected, name

print("PR-02 nonlinear Bose production runtime: PASS")
