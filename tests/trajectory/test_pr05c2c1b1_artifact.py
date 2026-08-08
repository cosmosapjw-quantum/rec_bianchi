from pathlib import Path
import json
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
NAME = "Full_Bianchi_HyRec_PR05C2C1B1_source_adapter_withheld_v0_67"
EXPANDED = ROOT / "archive" / "expanded" / NAME
BUNDLE = ROOT / "archive" / "bundles" / f"{NAME}.zip"


def test_pr05c2c1b1_artifact_is_durable_and_self_verifying():
    assert EXPANDED.is_dir()
    assert BUNDLE.is_file()
    metrics = json.loads((EXPANDED / "NUMERICAL_METRICS.json").read_text())
    gates = json.loads((EXPANDED / "HARD_GATE_LEDGER.json").read_text())
    source = json.loads((EXPANDED / "SOURCE_LINE_LEDGER.json").read_text())
    withheld = json.loads((EXPANDED / "WITHHELD_FULL_NETWORK_AUDIT.json").read_text())

    assert metrics["status"].startswith(
        "PASS_PR05C2C1B1_CANONICAL_SPIKE_PHYSICAL_LINE_SOURCE_ADAPTER"
    )
    assert gates["PR05C2C1B1"] == "COMPLETE_BOUNDED_SOURCE_ADAPTER_WITHHELD_AUDIT"
    assert gates["PR05C2C1B2"] == "OPEN_PRECONDITIONER_MULTI_MACRO"
    assert source["original_hyrec_virtual_spike"]["source_file"] == "HyRec/hydrogen.c"
    assert 521 in source["original_hyrec_virtual_spike"]["source_lines"]
    assert withheld["pair_block_count"] == 442
    assert withheld["same_cell_block_count"] == 17
    assert withheld["scalar_event_mass_weighted_relative"] < 1.0e-4
    assert withheld["scalar_edge_maximum_relative"] < 9.0e-3
    assert withheld["same_cell_maximum_relative"] < 1.7e-2
    assert metrics["maximum_spike_jvp_relative_residual"] < 1.0e-7
    assert metrics["maximum_planck_lte_null_relative_residual"] < 1.0e-13
    assert metrics["maximum_characteristic_frequency_relative_residual"] < 1.0e-11
    assert metrics["minimum_characteristic_occupation"] > 0.0

    result = subprocess.run(
        [sys.executable, str(EXPANDED / "verify_pr05c2c1b1_artifact.py")],
        cwd=EXPANDED,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
