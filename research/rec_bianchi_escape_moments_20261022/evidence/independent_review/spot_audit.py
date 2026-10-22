"""One bounded ANGULAR01 reviewer audit; never runs the 405-point study.

The independent sphere rule uses scipy.special Legendre roots and a staggered
full-azimuth trapezoid, in the supplied lab frame. Seven off-grid points are
budgeted. The three already-diagnosed input/arithmetic repairs are rechecked
without adding another parameter search. This script prints its evidence.
"""
from __future__ import annotations

import hashlib
import json
import math
import os
from pathlib import Path
import resource
import signal
import sys
import time
import warnings

for _name in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS",
              "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ[_name] = "1"

import numpy as np
from scipy.special import roots_legendre

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "code"))
import escape_moments as em


def _timeout(_signum, _frame):
    raise TimeoutError("Independent review hard budget is 30 seconds")


def _rotation():
    a, b, c = 0.37, -0.51, 0.29
    rz = np.array([[math.cos(a), -math.sin(a), 0.0],
                   [math.sin(a), math.cos(a), 0.0], [0.0, 0.0, 1.0]])
    ry = np.array([[math.cos(b), 0.0, math.sin(b)], [0.0, 1.0, 0.0],
                   [-math.sin(b), 0.0, math.cos(b)]])
    rx = np.array([[1.0, 0.0, 0.0], [0.0, math.cos(c), -math.sin(c)],
                   [0.0, math.sin(c), math.cos(c)]])
    return rz @ ry @ rx


def _independent_rule():
    mu, wm = roots_legendre(192)
    phi = (np.arange(384) + 0.5) * (2.0 * math.pi / 384)
    rho = np.sqrt(1.0 - mu[:, None] ** 2)
    directions = np.stack((rho * np.cos(phi)[None, :],
                           rho * np.sin(phi)[None, :],
                           np.broadcast_to(mu[:, None], (192, 384))), axis=-1)
    weights = np.broadcast_to(wm[:, None] / (2.0 * 384), (192, 384))
    return directions.reshape(-1, 3), weights.reshape(-1)


def main():
    signal.signal(signal.SIGALRM, _timeout)
    signal.alarm(30)
    started = time.perf_counter()
    directions, weights = _independent_rule()
    rotation = _rotation()

    def tensor(spectrum):
        return rotation @ np.diag(spectrum) @ rotation.T

    gate = math.log1p(1e8)
    cases = [
        ("isotropic_off_grid", 0.73, np.zeros((3, 3))),
        ("weak_lrs_off_grid", 0.70, tensor([-0.0005, -0.0005, 0.001])),
        ("large_lrs_off_grid", 0.37, tensor([-0.865, -0.865, 1.73])),
        ("near_boundary_triaxial", 0.127, tensor([-0.97, 0.27, 0.70])),
        ("below_auto_gate", 1.70 * gate * (1.0 - 1e-4), tensor([-0.97, 0.27, 0.70])),
        ("above_auto_gate", 1.70 * gate * (1.0 + 1e-4), tensor([-0.97, 0.27, 0.70])),
        ("thin_triaxial_off_grid", 2.5e-7, tensor([-0.4, -0.2, 0.6])),
    ]
    rows = []
    for label, depth, shear in cases:
        q = 1.0 + np.einsum("ni,ij,nj->n", directions, shear, directions)
        optical_depth = depth / q
        # A separately written thin series avoids the same division path.
        if float(np.max(optical_depth)) < 0.005:
            x = optical_depth
            probability = 1.0 + x * (-0.5 + x * (1.0 / 6.0 + x * (-1.0 / 24.0
                          + x * (1.0 / 120.0 - x / 720.0))))
        else:
            probability = (q / depth) * (-np.expm1(-optical_depth))
        weighted = weights * probability
        mean = float(np.sum(weighted))
        second = np.einsum("n,ni,nj->ij", weighted, directions, directions)
        pstf = second - np.eye(3) * mean / 3.0
        actual = em.angular_moments(depth, shear)
        b_error = abs(actual.mean - mean) / mean
        q_error = float(np.linalg.norm((actual.pstf - pstf) / mean, ord="fro"))
        rows.append({"case": label, "t": depth, "S": shear.tolist(),
                     "method": actual.method, "reference_B": mean,
                     "reference_Q": pstf.tolist(), "actual_B": actual.mean,
                     "actual_Q": actual.pstf.tolist(),
                     "relative_B_difference": b_error,
                     "Q_F_difference_over_B": q_error,
                     "pass": b_error <= 1e-8 and q_error <= 1e-8})

    reference_shear = np.diag([-0.4, -0.2, 0.6])
    extreme = em.angular_moments(1e308, reference_shear)
    extreme_error = float(np.linalg.norm(extreme.pstf / extreme.mean
                                         - (2.0 / 15.0) * reference_shear))
    tiny_bound = em.jensen_gap_bound(em.validate_inputs(1.0, 1e-200 * reference_shear))
    complex_axis_rejected = False
    with warnings.catch_warnings(record=True) as recorded:
        try:
            em.lrs_moments(1.0, 0.2, axis=np.array([0.0, 0.0, 1.0 + 2.0j]), n_mu=4)
        except ValueError:
            complex_axis_rejected = True
    repairs = {
        "thick_large_t": {"normalized_tensor_difference": extreme_error,
                           "Q": extreme.pstf.tolist(), "pass": extreme_error < 1e-12},
        "tiny_nonzero_shear_bound": {"result": tiny_bound,
                                     "pass": tiny_bound["representation"] != "EXACT_ZERO_SHEAR"
                                     and tiny_bound["log_bound"] is not None
                                     and math.isfinite(tiny_bound["log_bound"])},
        "complex_axis": {"rejected": complex_axis_rejected,
                         "warnings": [str(x.message) for x in recorded],
                         "pass": complex_axis_rejected},
    }
    elapsed = time.perf_counter() - started
    signal.alarm(0)
    report = {
        "scope": "Seven off-grid scalar/PSTF comparisons plus targeted rechecks of three observed defects",
        "independence": "Fresh delegated implementation of full-sphere lab-frame rule; not an interval certificate",
        "quadrature_points": len(rows), "reference_nodes_per_point": len(weights),
        "reference_node_evaluations": len(rows) * len(weights),
        "budget_seconds": 30, "budget_max_total_reviewer_quadrature_points": 12,
        "prior_invalid_axis_probe_quadrature_points": 1,
        "new_cosmological_ivps": 0, "old_campaign_runs": 0,
        "full_study_reruns": 0, "elapsed_seconds": elapsed,
        "max_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        "module_sha256": hashlib.sha256((ROOT / "code/escape_moments.py").read_bytes()).hexdigest(),
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "module_call_counters": dict(em.COUNTERS), "rows": rows,
        "targeted_repairs": repairs,
        "pass": all(row["pass"] for row in rows) and all(x["pass"] for x in repairs.values()),
    }
    print(json.dumps(report, indent=2, allow_nan=False))
    return 0 if report["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
