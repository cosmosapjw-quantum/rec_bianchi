#!/usr/bin/env python3
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parent

def sha256(path: Path) -> str:
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    return digest

metrics = json.loads((ROOT / "NUMERICAL_METRICS.json").read_text())
gates = json.loads((ROOT / "HARD_GATE_LEDGER.json").read_text())
assert metrics["status"].startswith("PASS_PR05C2C0_SCALAR_THEORY_CONTRACT_COMPLETE")
assert gates["PR05C2C0"] == "COMPLETE_SCALAR_THEORY_CONTRACT"
assert gates["PR05C2C1"] == "OPEN_IMPLEMENTATION_AND_NUMERICAL_EVIDENCE"
assert metrics["maximum_edge_antisymmetry_relative_residual"] < 1e-14
assert metrics["maximum_be_edge_null_relative_residual"] < 1e-13
assert metrics["maximum_pair_free_energy_production"] <= 1e-14
assert metrics["minimum_quasi_positive_boundary_flux"] >= 0.0
assert metrics["minimum_interpolated_active_conductance"] > 0.0
assert metrics["flrw_direction_residual_s_inv"] < 1e-14
assert metrics["flrw_frequency_residual_s_inv"] < 1e-14
assert metrics["minimum_sampled_finite_tilt_doppler_factor"] > 0.0
assert metrics["native_instantaneous_angular_rank"] == 1
assert metrics["number_plus_momentum_angular_rank"] >= 4
assert metrics["graph_null_residual"] < 1e-13
assert metrics["graph_minimum_eigenvalue"] > -1e-12
assert metrics["maximum_preconditioned_condition_number"] < 3.0
assert metrics["muscl_minimum_trace"] > 0.0
assert metrics["muscl_maximum_cell_average_residual"] < 1e-14
assert metrics["direct_thermodynamic_compiler_implemented"] is False
with np.load(ROOT / "pr05c2c0_theory_closure_v065.npz", allow_pickle=False) as data:
    assert data["interpolated_conductance"].shape == (12, 12)
    assert data["angular_directions"].shape[1] == 3
manifest = {}
for line in (ROOT / "MANIFEST_SHA256.txt").read_text().splitlines():
    digest, name = line.split("  ", 1)
    manifest[name] = digest
for name, digest in manifest.items():
    assert sha256(ROOT / name) == digest, name
print(metrics["status"])
