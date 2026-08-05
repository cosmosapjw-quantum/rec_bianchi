from pathlib import Path
import hashlib
import json

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
ARTIFACT = (
    ROOT
    / "archive"
    / "expanded"
    / "Full_Bianchi_HyRec_PR03_full_scalar_COM_KHW_v0_50"
)
DATA = ROOT / "data" / "full_scalar_com_khw_v050.npz"


def test_pr03_durable_ledger_closes_pr03():
    ledger = json.loads((ARTIFACT / "PR03_ledger.json").read_text())
    assert ledger["status"] == "PASS_PR03_COMPLETE"
    assert ledger["decision"]["PR03_status"] == "COMPLETE"
    assert ledger["decision"]["production_amplitude"] == "FULL_SCALAR_COM_KHW"
    assert all(ledger["hard_gate_status"].values())
    assert ledger["decision"]["next_PR"].startswith("PR-04")


def test_pr03_network_is_full_positive_symmetric_and_nontrivial():
    with np.load(DATA, allow_pickle=False) as data:
        assert data["classification"].item() == "PR03_FULL_SCALAR_COM_KHW"
        assert data["amplitude_lane"].item() == (
            "full_bound_continuum_seagull_interference"
        )
        full = data["pair_moments_m3_sInv"]
        provisional = data["provisional_pair_moments_m3_sInv"]
        same = data["same_cell_rates_sInv"]
        assert full.shape == (25, 35, 35)
        assert same.shape == (25, 35)
        assert np.min(full[0]) >= 0.0
        assert np.max(np.abs(full - np.swapaxes(full, 1, 2))) == 0.0
        assert np.linalg.norm(full - provisional) / np.linalg.norm(provisional) > 1e-14
        assert np.all(np.isfinite(full))
        assert np.all(np.isfinite(same))


def test_pr03_manifest_matches_every_artifact_file():
    entries = {}
    for line in (ARTIFACT / "MANIFEST_SHA256.txt").read_text().splitlines():
        digest, name = line.split("  ", 1)
        entries[name] = digest
    expected = {
        path.name for path in ARTIFACT.iterdir()
        if path.name != "MANIFEST_SHA256.txt"
    }
    assert set(entries) == expected
    for name, digest in entries.items():
        assert hashlib.sha256((ARTIFACT / name).read_bytes()).hexdigest() == digest
