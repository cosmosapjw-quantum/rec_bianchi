#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parent
metrics = json.loads((ROOT / "NUMERICAL_METRICS.json").read_text())
gates = json.loads((ROOT / "HARD_GATE_LEDGER.json").read_text())
withheld = json.loads((ROOT / "WITHHELD_FULL_NETWORK_AUDIT.json").read_text())
assert metrics["status"].startswith("PASS_PR05C2C1B1_CANONICAL_SPIKE_PHYSICAL_LINE_SOURCE_ADAPTER")
assert gates["PR05C2C1B1"] == "COMPLETE_BOUNDED_SOURCE_ADAPTER_WITHHELD_AUDIT"
assert gates["PR05C2C1B2"] == "OPEN_PRECONDITIONER_MULTI_MACRO"
assert metrics["maximum_spike_jvp_relative_residual"] < 1e-7
assert metrics["maximum_planck_lte_null_relative_residual"] < 1e-13
assert metrics["maximum_characteristic_frequency_relative_residual"] < 1e-11
assert metrics["minimum_characteristic_occupation"] > 0
assert withheld["pair_block_count"] == 442
assert withheld["same_cell_block_count"] == 17
assert withheld["scalar_event_mass_weighted_relative"] < 1e-4
assert withheld["scalar_edge_maximum_relative"] < 9e-3
assert withheld["same_cell_maximum_relative"] < 1.7e-2
print("PR-05C2C1B1 v0.67 artifact: PASS; preconditioner and multi-macro OPEN")
