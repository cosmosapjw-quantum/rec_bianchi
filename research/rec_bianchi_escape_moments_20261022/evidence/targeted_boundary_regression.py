"""Three targeted regressions for the single pre-study boundary repair."""
import os
for option in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ[option] = "1"
import hashlib
import json
from pathlib import Path
import sys
import time

UNIT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(UNIT / "code"))
import numpy as np
import escape_moments as em

started = time.monotonic()
em.COUNTERS.clear()
S = np.diag([-0.4, -0.2, 0.6])
huge = em.thick_moments(1.0e308, S)
scaled_error = float(np.linalg.norm(huge.pstf * 1.0e308 - (2.0 / 15.0) * S))
tiny = em.jensen_gap_bound(em.validate_inputs(1.0, 1.0e-200 * S))
complex_rejected = False
try:
    em.lrs_moments(1.0, 0.2, axis=np.array([0.0, 0.0, 1.0 + 1.0j]))
except ValueError:
    complex_rejected = True
checks = [
    {"name": "large_finite_t_retains_tensor", "passed": bool(np.count_nonzero(huge.pstf) == 3 and scaled_error <= 2.0e-12), "scaled_tensor_error": scaled_error, "Q": huge.pstf.tolist()},
    {"name": "nonzero_tiny_shear_not_exact_zero", "passed": bool(tiny["representation"] == "UNDERFLOW_USE_LOG" and tiny["bound"] is None and np.isfinite(tiny["log_bound"])), "bound": tiny},
    {"name": "complex_axis_rejected", "passed": complex_rejected},
]
record = {"scope": "three affected boundary regressions only; before the 405-point study",
          "checks": checks, "passed": all(c["passed"] for c in checks),
          "elapsed_seconds": time.monotonic() - started, "counts": dict(em.COUNTERS),
          "source_sha256": hashlib.sha256((UNIT / "code/escape_moments.py").read_bytes()).hexdigest(),
          "new_IVPs": 0, "old_tests": 0, "frozen_tolerances_changed": False}
destination = UNIT / "evidence/BOUNDARY_REGRESSION_RESULT.json"
with destination.open("x") as output:
    output.write(json.dumps(record, indent=2) + "\n")
print(json.dumps(record))
raise SystemExit(0 if record["passed"] else 1)
