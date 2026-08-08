from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[2]
NAME = "Full_Bianchi_HyRec_PR05C2C1B2A_two_photon_raman_source_v0_68"
EXPANDED = ROOT / "archive" / "expanded" / NAME
BUNDLE = ROOT / "archive" / "bundles" / f"{NAME}.zip"


def test_pr05c2c1b2a_artifact_is_durable_and_self_verifying():
    assert EXPANDED.is_dir()
    assert BUNDLE.is_file()
    metrics = json.loads((EXPANDED / "NUMERICAL_METRICS.json").read_text())
    gates = json.loads((EXPANDED / "HARD_GATE_LEDGER.json").read_text())
    source = json.loads((EXPANDED / "SOURCE_LINE_LEDGER.json").read_text())
    registry = json.loads((EXPANDED / "CHANNEL_REGISTRY.json").read_text())

    assert metrics["status"].startswith(
        "PASS_PR05C2C1B2A_CANONICAL_TWO_PHOTON_RAMAN_SOURCE_ADAPTER"
    )
    assert gates["PR05C2C1B2A"] == "COMPLETE_CANONICAL_TWO_PHOTON_RAMAN_SOURCE_ADAPTER"
    assert gates["PR05C2C1B2B"] == "OPEN_PRECONDITIONER_MULTI_MACRO"
    assert source["canonical_table"]["member"] == "HyRec/two_photon_tables.dat"
    assert 472 in source["canonical_matrix_coupling"]["source_lines"]
    assert registry["2s"]["two_photon_bins"] == 140
    assert registry["2s"]["raman_bins"] == 171
    assert registry["3s3d"]["two_photon_bins"] == 271
    assert registry["3s3d"]["raman_bins"] == 40
    assert registry["4s4d"]["two_photon_bins"] == 311
    assert registry["4s4d"]["raman_bins"] == 0
    assert metrics["maximum_c_source_parity_relative"] < 3.0e-13
    assert metrics["maximum_canonical_jvp_gross_relative"] < 1.0e-8
    assert metrics["maximum_canonical_jvp_active_edge_relative"] < 1.0e-6
    assert metrics["maximum_canonical_detailed_balance_relative"] < 1.0e-13
    assert metrics["maximum_physical_planck_null_relative"] < 2.0e-13
    assert metrics["maximum_physical_jvp_relative"] < 2.0e-8
    assert metrics["minimum_physical_forward_rate_H_inv_s_inv"] >= 0.0
    assert metrics["minimum_physical_reverse_rate_H_inv_s_inv"] >= 0.0

    result = subprocess.run(
        [sys.executable, str(EXPANDED / "verify_pr05c2c1b2a_artifact.py")],
        cwd=EXPANDED,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
