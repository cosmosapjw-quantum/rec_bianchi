from pathlib import Path
import json

import numpy as np


ROOT = Path(__file__).resolve().parents[2]
ARTIFACT = (
    ROOT
    / "archive"
    / "expanded"
    / "Full_Bianchi_HyRec_PR01C_background_frame_adapter_v0_48"
)


def test_pr01c_durable_ledger_closes_pr01():
    ledger = json.loads((ARTIFACT / "PR01C_ledger.json").read_text())

    assert ledger["status"] == "PASS_PR01_COMPLETE"
    assert ledger["decision"]["PR01"] == "COMPLETE"
    assert all(ledger["hard_gate_status"].values())


def test_pr01c_snapshot_registry_contains_representative_types():
    data = np.load(ROOT / "data" / "pr01c_background_snapshots_v048.npz")

    assert data["directions"].shape == (26, 3)
    assert set(data["model_names"].tolist()) == {
        "Bianchi_II_large_shear",
        "Bianchi_VI_h_tilted_large_shear",
        "Bianchi_VI_minus_1_over_9_exceptional",
    }

    for prefix in (
        "Bianchi_II_large_shear",
        "Bianchi_VI_h_tilted_large_shear",
        "Bianchi_VI_minus_1_over_9_exceptional",
    ):
        assert data[f"{prefix}_sigma_s_inv"].shape[1:] == (3, 3)
        assert data[f"{prefix}_N_s_inv"].shape[1:] == (3, 3)
        assert data[f"{prefix}_hydrogen_R_s_inv"].shape[1] == 26
        assert np.all(np.isfinite(data[f"{prefix}_hydrogen_R_s_inv"]))
