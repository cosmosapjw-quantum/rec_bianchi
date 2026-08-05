from pathlib import Path
import json

import numpy as np


ROOT = Path(__file__).resolve().parents[2]
ARTIFACT = (
    ROOT
    / "archive"
    / "expanded"
    / "Full_Bianchi_HyRec_PR02_nonlinear_bose_runtime_v0_49"
)


def test_pr02_durable_ledger_closes_pr02():
    ledger = json.loads((ARTIFACT / "PR02_ledger.json").read_text())

    assert ledger["status"] == "PASS_PR02_COMPLETE"
    assert ledger["decision"]["PR02_status"] == "COMPLETE"
    assert all(ledger["hard_gate_status"].values())
    assert ledger["decision"]["next_PR"].startswith("PR-03")


def test_pr02_top_level_evidence_contains_all_adaptive_lanes():
    with np.load(
        ROOT / "data" / "pr02_nonlinear_bose_runtime_v049.npz",
        allow_pickle=False,
    ) as data:
        assert set(data["scenario_names"].tolist()) == {
            "finite_or_mixed_tilt",
            "nonlinear_even_shear",
            "directional_crossing",
        }
        for prefix, angle_count in (
            ("finite_or_mixed_tilt", 302),
            ("nonlinear_even_shear", 590),
            ("directional_crossing", 974),
        ):
            assert data[f"{prefix}_weights"].shape == (angle_count,)
            assert np.min(data[f"{prefix}_weights"]) > 0
            assert data[f"{prefix}_occupation"].shape == (35, angle_count)
            assert np.min(data[f"{prefix}_implicit_occupation"]) > 0
