from pathlib import Path
import csv
import hashlib
import json
import numpy as np

HERE = Path(__file__).resolve().parent
ledger = json.loads((HERE / "PR04A_ledger.json").read_text())
assert ledger["status"] == "PASS_PR04A_COMMON_MEASURE_CORE_PR04B_ORIGINAL_HYREC_ARCHIVE_OPEN"
assert all(ledger["hard_gate_status"].values())
assert ledger["decision"]["PR04"] == "IN_PROGRESS"
assert ledger["decision"]["original_HyRec_archive_parity"] == "OPEN_FAIL_CLOSED"

with np.load(HERE / "hyrec_common_measure_v051.npz", allow_pickle=False) as data:
    x = data["frequency_moments_x_m3_sInv"]
    hz = data["frequency_moments_Hz_m3_sInv"]
    dnu = float(data["Doppler_width_Hz"])
    assert x.shape == (5, 17, 17)
    assert hz.shape == x.shape
    for order in range(5):
        scale = max(float(np.max(np.abs(x[order]))), 1e-300)
        assert np.max(np.abs(x[order] - (-1)**order * x[order].T)) < 5e-13 * scale
        assert np.max(np.abs(hz[order] - x[order] * dnu**order)) < 5e-13 * max(float(np.max(np.abs(hz[order]))), 1e-300)
    assert np.min(x[0]) >= 0
    assert np.min(x[2]) >= 0
    assert np.min(x[4]) >= 0
    assert np.max(np.abs(np.diag(x[1]))) == 0
    assert np.max(np.abs(np.diag(x[3]))) == 0
    assert data["native_virtual_indices"].shape == (80,)
    assert str(data["hyrec2_source_commit"].item()) == "09e8243d0e08edd3603a94dfbc445ae06cafe139"
    assert str(data["original_hyrec_archive_sha256"].item()) == "OPEN_NOT_ACQUIRED"

implicit = list(csv.DictReader((HERE / "implicit_update_summary.csv").open()))
assert len(implicit) == 1
assert implicit[0]["converged"] == "True"
assert float(implicit[0]["explicit_trial_minimum"]) < 0
assert float(implicit[0]["implicit_minimum"]) > 0
assert float(implicit[0]["free_energy_change_m3"]) < 0

for line in (HERE / "MANIFEST_SHA256.txt").read_text().splitlines():
    expected, name = line.split("  ", 1)
    actual = hashlib.sha256((HERE / name).read_bytes()).hexdigest()
    assert actual == expected, name

print("PR-04A HYREC common-measure core: PASS; PR-04B original archive parity OPEN")
