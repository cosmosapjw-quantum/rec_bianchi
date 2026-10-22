"""Re-evaluate exactly five saved validator failures; no quadrature imports/runs."""
import ast
import csv
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import time

started = time.monotonic()
UNIT = Path(__file__).resolve().parents[1]
ROOT = UNIT / "results/attempt_001"
digest = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
summary = json.loads((ROOT / "study_summary.json").read_text())
with (ROOT / "grid.csv").open(newline="") as source:
    rows = list(csv.DictReader(source))
failed = [row for row in rows if row["passed"] == "False"]
expected_indices = [1, 4, 5, 14, 16]
if [int(row["index"]) for row in failed] != expected_indices:
    raise RuntimeError("Unexpected failure set; this repair is limited to the diagnosed five rows")
if any(row["failed_checks"] != "thick_scalar_upper" for row in failed):
    raise RuntimeError("Different failure kind; do not broaden this repair")
records = []
for row in failed:
    t, qmax, mean = float(row["t"]), float(row["qmax"]), float(row["B128"])
    slack = 2.0e-12 * float(row["beta_iso"])
    lower = -math.expm1(-t / qmax) / t
    passed = mean + slack >= lower
    records.append({"index": int(row["index"]), "t": t, "qmax": qmax, "B_saved": mean,
                    "stable_B_lower_bound": lower, "stable_B_minus_lower": mean - lower,
                    "old_guard_excess": float(row["thick_B_absolute_defect"]) - float(row["thick_B_absolute_bound"]),
                    "unchanged_slack": slack, "passed": passed})
source_files = [UNIT / "code/run_study.py", UNIT / "code/escape_moments.py", UNIT / "code/plot_results.py"]
for path in source_files:
    ast.parse(path.read_text(), filename=str(path))
passed = (len(rows) == 405 and summary["standalone_checks_passed"] == 89
          and summary["grid_points_passed"] == 400 and all(r["passed"] for r in records))
decision = {"schema": "ANGULAR01_SAVED_DATA_ADJUDICATION_V1", "status": "PASS" if passed else "FAIL",
            "decision_kind": "SAVED_DATA_VALIDATOR_REPAIR", "at_utc": datetime.now(timezone.utc).isoformat(),
            "initial_study_status": summary["status"], "initial_study_exit_code": 1,
            "initial_study_summary_sha256": digest(ROOT / "study_summary.json"),
            "source_grid_sha256": digest(ROOT / "grid.csv"),
            "source_grid_numeric_values_modified": False,
            "initial_full_study_runs": 1, "full_study_reruns": 0,
            "accepted_grid_points": 405 if passed else 400,
            "unchanged_passed_grid_points_reused": 400, "saved_validator_rows_rechecked": 5,
            "new_quadratures_in_repair": 0, "new_donor_calls_in_repair": 0,
            "new_cosmological_IVPs": 0, "old_IVPs": 0,
            "standalone_checks_reused": 89, "standalone_checks_rerun": 0,
            "original_guard": "1/t-B <= exp(-t/qmax)/t + slack",
            "repaired_guard": "B + slack >= -expm1(-t/qmax)/t",
            "equivalence": "Subtract 1/t from the original bound and multiply by -1; 1-exp(-u) is evaluated with -expm1(-u).",
            "unchanged_tolerance": "slack=2e-12*beta_iso(t)",
            "diagnosis": "Thin isotropic equality made the original O(1/t) comparison lose more absolute precision than the fixed O(beta_iso) slack.",
            "typed_change": "VALIDATOR_REPRESENTATION_REPAIR; no physical formula or acceptance threshold changed",
            "targeted_records": records,
            "current_source_sha256": {str(p.relative_to(UNIT)): digest(p) for p in source_files},
            "old_validator_source_sha256": digest(UNIT / "evidence/run_study_before_conditioning_repair.py"),
            "elapsed_seconds": time.monotonic() - started,
            "global_convergence": "NOT_RUN", "production": "NOT_APPROVED", "REI_activation": False}
with (ROOT / "FINAL_DECISION.json").open("x") as output:
    output.write(json.dumps(decision, indent=2) + "\n")
print(json.dumps(decision))
raise SystemExit(0 if passed else 1)
