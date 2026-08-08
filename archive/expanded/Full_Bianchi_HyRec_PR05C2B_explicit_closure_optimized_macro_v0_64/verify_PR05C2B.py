#!/usr/bin/env python3
import csv, json
from pathlib import Path
root=Path(__file__).resolve().parent
metrics=json.loads((root/"NUMERICAL_METRICS.json").read_text())
hard=json.loads((root/"HARD_GATE_LEDGER.json").read_text())
with (root/"MACRO_SOLVER_LEDGER.csv").open(newline="", encoding="utf-8") as h: macro=list(csv.DictReader(h))
with (root/"THERMODYNAMIC_DIRECT_VALIDATION.csv").open(newline="", encoding="utf-8") as h: direct=list(csv.DictReader(h))
assert metrics["status"].startswith("PASS_EXPLICIT_CLOSURE")
assert len(macro)==9 and all(int(row["converged"])==1 for row in macro)
assert len(direct)==12
assert metrics["maximum_macro_gross_backward_error"] < 1e-11
assert metrics["maximum_macro_number_residual"] < 1e-11
assert metrics["maximum_macro_energy_residual"] < 1e-11
assert metrics["maximum_macro_jvp_residual"] < 1e-8
assert 0.25 < metrics["maximum_direct_thermodynamic_closure_discrepancy"] < 0.31
assert metrics["performance"]["speedup_action_only_vs_pair_loop"] > 10
assert metrics["performance"]["speedup_vectorized_jvp_vs_pair_loop"] > 10
assert metrics["performance"]["dense_assembly_speedup"] > 1.5
assert all(item["passed"] for item in hard["gates"])
print(metrics["status"])
