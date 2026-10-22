#!/usr/bin/env python3
"""Execute the single frozen ANGULAR01 finite study, preserving every attempt."""
from __future__ import annotations

import os
for _angular_thread_option in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
                               "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "BLIS_NUM_THREADS"):
    os.environ[_angular_thread_option] = "1"

import argparse
from collections import Counter
import csv
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import platform
import resource
import shlex
import signal
import sys
import time
import traceback

import numpy as np
import escape_moments as em


UNIT = Path(__file__).resolve().parents[1]
SPECTRA = [
    ("isotropic", (0.0, 0.0, 0.0), 0.0),
    ("LRS_m0p8", (0.4, 0.4, -0.8), -0.8),
    ("LRS_m0p2", (0.1, 0.1, -0.2), -0.2),
    ("LRS_p0p2", (-0.1, -0.1, 0.2), 0.2),
    ("LRS_p0p8", (-0.4, -0.4, 0.8), 0.8),
    ("LRS_p1p8", (-0.9, -0.9, 1.8), 1.8),
    ("triaxial_A", (-0.8, 0.15, 0.65), None),
    ("triaxial_B", (-0.4, -0.2, 0.6), None),
    ("triaxial_C", (-0.97, 0.27, 0.70), None),
]
FINITE_TOL = 1.0e-8
SLACK_FACTOR = 2.0e-12


class StudyBudgetStop(RuntimeError):
    pass


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def clean_json(value):
    if isinstance(value, np.ndarray):
        return clean_json(value.tolist())
    if isinstance(value, np.generic):
        return clean_json(value.item())
    if isinstance(value, float) and not math.isfinite(value):
        return "+Infinity" if value > 0 else ("-Infinity" if value < 0 else "NaN")
    if isinstance(value, dict):
        return {str(k): clean_json(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [clean_json(v) for v in value]
    return value


def save_json(path, value):
    path = Path(path)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(clean_json(value), indent=2, ensure_ascii=False, allow_nan=False) + "\n")
    temporary.replace(path)


def numerical_upper(bound):
    """Only for finite-precision inequalities with the separately frozen slack."""
    if bound is not None:
        return float(bound)
    # The log value/underflow flag remain in the record. Zero is NOT the certificate.
    return 0.0


def check_record(group, name, passed, measured=None, threshold=None, **detail):
    return {"group": group, "name": name, "passed": bool(passed),
            "measured": measured, "threshold": threshold, **detail}


def rotation_matrix():
    a, b, c = 0.37, -0.61, 0.29
    rz = np.array([[math.cos(a), -math.sin(a), 0.0], [math.sin(a), math.cos(a), 0.0], [0.0, 0.0, 1.0]])
    ry = np.array([[math.cos(b), 0.0, math.sin(b)], [0.0, 1.0, 0.0], [-math.sin(b), 0.0, math.cos(b)]])
    rx = np.array([[1.0, 0.0, 0.0], [0.0, math.cos(c), -math.sin(c)], [0.0, math.sin(c), math.cos(c)]])
    return rz @ ry @ rx


def function_and_scalar_checks():
    checks = []
    scalar_rows = []
    for t in (1.0e-8, 1.0e-3, 1.0, 30.0, 1.0e3):
        for q in (0.03, 0.5, 1.0, 2.8):
            donor = em.donor_beta_reference(t, q)
            vector = em.beta_vector(t, q)
            relative = abs(vector - donor) / abs(donor)
            row = {"t": t, "q": q, "donor_beta": donor, "vector_beta": vector,
                   "relative_error": relative, "passed": relative <= 5.0e-14}
            scalar_rows.append(row)
            checks.append(check_record("donor_scalar", f"t={t:g};q={q:g}", row["passed"], relative, 5.0e-14))
    zero = np.zeros((3, 3))
    invalid = [
        ("zero_t", 0.0, zero), ("negative_t", -1.0, zero),
        ("nan_t", math.nan, zero), ("infinite_t", math.inf, zero),
        ("vector_t", [1.0, 2.0], zero), ("complex_t", 1.0 + 1.0j, zero),
        ("wrong_shape", 1.0, np.zeros((2, 2))), ("flat_shape", 1.0, np.zeros(9)),
        ("nonfinite_tensor", 1.0, np.diag([math.nan, 0.0, 0.0])),
        ("infinite_tensor", 1.0, np.diag([math.inf, 0.0, 0.0])),
        ("complex_tensor", 1.0, zero.astype(complex) + 1.0j * np.eye(3)),
        ("nontracefree", 1.0, 0.1 * np.eye(3)),
        ("nonsymmetric", 1.0, np.array([[0.0, 0.1, 0.0], [0.0, 0.0, 0.0], [0.0, 0.0, 0.0]])),
        ("zero_directional_expansion", 1.0, np.diag([-1.0, 0.5, 0.5])),
        ("negative_directional_expansion", 1.0, np.diag([-1.1, 0.55, 0.55])),
        ("roundoff_zero_band", 1.0, np.diag([-1.0 + 8.0 * np.finfo(float).eps,
                                            0.5 - 4.0 * np.finfo(float).eps,
                                            0.5 - 4.0 * np.finfo(float).eps])),
    ]
    for name, t, tensor in invalid:
        rejected, reason = False, None
        try:
            em.validate_inputs(t, tensor)
        except ValueError as exc:
            rejected, reason = True, str(exc)
        checks.append(check_record("invalid_domain", name, rejected, reason=reason))
    eps = np.finfo(float).eps
    raw = np.diag([-0.4, -0.2, 0.6])
    raw[0, 1] += 2.0 * eps
    raw[0, 0] += 2.0 * eps
    fixed = em.validate_inputs(1.0, raw)
    checks.append(check_record("input_roundoff", "canonicalization_reported",
                               0.0 < fixed.correction_norm <= fixed.tolerance
                               and abs(np.trace(fixed.tensor)) <= fixed.tolerance
                               and np.linalg.norm(fixed.tensor - fixed.tensor.T) <= fixed.tolerance,
                               fixed.correction_norm, fixed.tolerance))
    auto_low = em.angular_moments(1.0, np.diag([-0.4, -0.2, 0.6]))
    auto_high = em.angular_moments(100.0, np.diag([-0.4, -0.2, 0.6]))
    checks.append(check_record("auto_api", "low_depth_uses_quadrature", auto_low.method == "general_eigenbasis_2d"))
    checks.append(check_record("auto_api", "certified_depth_uses_thick", auto_high.method == "analytic_thick"))
    try:
        em.thick_moments(1.0, zero)
        unsafe_rejected = False
    except ValueError:
        unsafe_rejected = True
    checks.append(check_record("auto_api", "uncertified_thick_request_rejected", unsafe_rejected))
    underflow = em.thick_bounds(1000.0, 1.0)
    checks.append(check_record("bound_representation", "underflow_keeps_log",
                               underflow["absolute_B"] is None
                               and math.isfinite(underflow["log_absolute_B"])
                               and underflow["absolute_B_representation"] == "UNDERFLOW_USE_LOG"))
    directions = np.array([[1.0, 2.0, 3.0], [-2.0, 1.0, 0.5], [0.4, -0.7, 1.1]])
    directions /= np.linalg.norm(directions, axis=1)[:, None]
    tensor = np.diag([-0.97, 0.27, 0.70])
    baseline_q = 1.0 + np.einsum("ni,ij,nj->n", directions, tensor, directions)
    base_beta = em.beta_vector(0.03, baseline_q)
    for signs in ((-1, 1, 1), (1, -1, 1), (1, 1, -1), (-1, -1, -1)):
        reflected = directions * np.asarray(signs)
        reflected_q = 1.0 + np.einsum("ni,ij,nj->n", reflected, tensor, reflected)
        error = float(np.max(np.abs(em.beta_vector(0.03, reflected_q) - base_beta)))
        checks.append(check_record("reflection", str(signs), error <= 2.0e-12, error, 2.0e-12,
                                   scope="individual reflections in principal frame; inversion in every frame"))
    return checks, scalar_rows


def grid_case(index, name, eigenvalues, lrs_s, t):
    tensor = np.diag(eigenvalues)
    nominal = em.angular_moments(t, tensor, n_mu=64, n_phi=128, mode="quadrature")
    reference = em.angular_moments(t, tensor, n_mu=128, n_phi=256, mode="quadrature")
    data = em.validate_inputs(t, tensor)
    iso = em.beta_vector(t, 1.0)
    slack = SLACK_FACTOR * iso
    difference = em.observed_difference(nominal, reference, iso)
    bounds = reference.analytic_bounds
    jensen = em.jensen_gap_bound(data)
    b0 = 1.0 / t
    q0 = 2.0 * data.tensor / (15.0 * t)
    b_thick_defect = b0 - reference.mean
    q_thick_defect = float(np.linalg.norm(q0 - reference.pstf, ord="fro"))
    jensen_gap = iso - reference.mean
    second = reference.pstf + reference.mean * np.eye(3) / 3.0
    psd_min = float(np.linalg.eigvalsh(0.5 * (second + second.T))[0])
    symmetry = float(np.linalg.norm(reference.pstf - reference.pstf.T, ord="fro"))
    trace = abs(float(np.trace(reference.pstf)))
    checks = {
        "two_level_B": difference["scalar"] <= FINITE_TOL,
        "two_level_Q": difference["tensor_F"] <= FINITE_TOL,
        "Jensen_lower": jensen_gap >= -slack,
        "Jensen_upper": jensen_gap <= numerical_upper(jensen["bound"]) + slack,
        "thick_scalar_lower": b_thick_defect >= -slack,
        "thick_scalar_upper": b_thick_defect <= numerical_upper(bounds["absolute_B"]) + slack,
        "thick_tensor_upper": q_thick_defect <= numerical_upper(bounds["absolute_Q_F"]) + slack,
        "probability": 0.0 < reference.mean <= 1.0 + slack,
        "symmetry": symmetry <= slack,
        "trace": trace <= slack,
        "second_moment_PSD": psd_min >= -slack,
    }
    lrs_d_b, lrs_d_q, lrs_finite_b, lrs_finite_q = None, None, None, None
    if lrs_s is not None:
        one_d_nominal = em.lrs_moments(t, lrs_s, n_mu=64)
        one_d_reference = em.lrs_moments(t, lrs_s, n_mu=128)
        lrs_d_b = max(abs(one_d_nominal.mean - nominal.mean), abs(one_d_reference.mean - reference.mean)) / iso
        lrs_d_q = max(np.linalg.norm(one_d_nominal.pstf - nominal.pstf),
                      np.linalg.norm(one_d_reference.pstf - reference.pstf)) / iso
        one_d_delta = em.observed_difference(one_d_nominal, one_d_reference, iso)
        lrs_finite_b, lrs_finite_q = one_d_delta["scalar"], one_d_delta["tensor_F"]
        checks.update({"LRS_independent_B": lrs_d_b <= FINITE_TOL,
                       "LRS_independent_Q": lrs_d_q <= FINITE_TOL,
                       "LRS_two_level_B": lrs_finite_b <= FINITE_TOL,
                       "LRS_two_level_Q": lrs_finite_q <= FINITE_TOL})
    if name == "isotropic":
        checks["isotropic_B"] = abs(reference.mean - iso) <= slack
        checks["isotropic_Q"] = np.linalg.norm(reference.pstf) <= slack
    eligible = bool(bounds["auto_eligible"])
    # Reuse the just-computed nominal result when AUTO chooses quadrature.
    # The two representative function checks separately exercise the public AUTO path.
    selected = em.thick_moments(t, tensor) if eligible else nominal
    auto_b = abs(selected.mean - reference.mean) / iso
    auto_q = float(np.linalg.norm(selected.pstf - reference.pstf)) / iso
    checks["auto_decision"] = (selected.method == "analytic_thick") == (t / data.qmax >= em.AUTO_THRESHOLD)
    if eligible:
        checks["auto_observed_B"] = auto_b <= em.AUTO_EPSILON + SLACK_FACTOR
        checks["auto_observed_Q"] = auto_q <= em.AUTO_EPSILON + SLACK_FACTOR
    row = {
        "index": index, "spectrum": name, "t": t, "lambda_1": eigenvalues[0],
        "lambda_2": eigenvalues[1], "lambda_3": eigenvalues[2], "lrs_s": lrs_s,
        "qmin": data.qmin, "qmax": data.qmax, "beta_iso": iso,
        "B64": nominal.mean, "B128": reference.mean,
        "Qxx": reference.pstf[0, 0], "Qyy": reference.pstf[1, 1], "Qzz": reference.pstf[2, 2],
        "Qxy": reference.pstf[0, 1], "Qxz": reference.pstf[0, 2], "Qyz": reference.pstf[1, 2],
        "Q_F": float(np.linalg.norm(reference.pstf)),
        "Q_F_over_B": float(np.linalg.norm(reference.pstf)) / reference.mean,
        "scalar_suppression": jensen_gap / iso,
        "two_level_B_normalized": difference["scalar"],
        "two_level_Q_normalized": difference["tensor_F"],
        "lrs_1d_2d_B_normalized": lrs_d_b, "lrs_1d_2d_Q_normalized": lrs_d_q,
        "lrs_two_level_B_normalized": lrs_finite_b, "lrs_two_level_Q_normalized": lrs_finite_q,
        "Jensen_bound": jensen["bound"], "log_Jensen_bound": jensen["log_bound"],
        "Jensen_bound_representation": jensen["representation"],
        "thick_B": b0, "thick_Q_F": float(np.linalg.norm(q0)),
        "thick_B_absolute_defect": b_thick_defect, "thick_Q_F_absolute_defect": q_thick_defect,
        "thick_B_absolute_bound": bounds["absolute_B"],
        "log_thick_B_absolute_bound": bounds["log_absolute_B"],
        "thick_Q_F_absolute_bound": bounds["absolute_Q_F"],
        "log_thick_Q_F_absolute_bound": bounds["log_absolute_Q_F"],
        "log_thick_relative_B_bound": bounds["log_relative_B"],
        "auto_method": selected.method, "auto_eligible": eligible,
        "auto_observed_B_normalized": auto_b, "auto_observed_Q_normalized": auto_q,
        "auto_nodes": selected.nodes, "reference_nodes": reference.nodes,
        "nominal_nodes": nominal.nodes, "input_correction_norm": data.correction_norm,
        "second_moment_min_eigenvalue": psd_min, "Q_trace_abs": trace,
        "Q_symmetry_F": symmetry, "slack": slack,
        "passed": all(checks.values()), "failed_checks": ";".join(k for k, passed in checks.items() if not passed),
    }
    return row, checks


def rotation_checks(deadline):
    checks, rows = [], []
    rotation = rotation_matrix()
    for name, eigenvalues, _ in SPECTRA[-3:]:
        for t in (0.03, 1.0, 30.0):
            deadline()
            tensor = np.diag(eigenvalues)
            rotated = rotation @ tensor @ rotation.T
            base = em.angular_moments(t, tensor, n_mu=128, n_phi=256, mode="quadrature")
            covariant = em.angular_moments(t, rotated, n_mu=128, n_phi=256, mode="quadrature")
            lab = em.lab_frame_oracle(t, rotated, n_mu=128, n_phi=256)
            iso = em.beta_vector(t, 1.0)
            expected_q = rotation @ base.pstf @ rotation.T
            metrics = {"rotation_B": abs(covariant.mean - base.mean) / iso,
                       "rotation_Q": float(np.linalg.norm(covariant.pstf - expected_q)) / iso,
                       "independent_lab_B": abs(lab.mean - covariant.mean) / iso,
                       "independent_lab_Q": float(np.linalg.norm(lab.pstf - covariant.pstf)) / iso}
            for key, error in metrics.items():
                checks.append(check_record("rotation", f"{name};t={t:g};{key}", error <= FINITE_TOL,
                                           error, FINITE_TOL))
            rows.append({"spectrum": name, "t": t, **metrics, "rotation": rotation.tolist(),
                         "rotated_tensor": rotated.tolist(), "base_Q": base.pstf.tolist(),
                         "rotated_Q": covariant.pstf.tolist(), "lab_Q": lab.pstf.tolist()})
    return checks, rows


def weak_shear_checks(deadline):
    checks, rows = [], []
    s = 1.0e-3
    unit_shear = np.diag([-0.5, -0.5, 1.0])
    for t in (0.1, 1.0, 3.0, 10.0):
        deadline()
        plus, minus = em.lrs_moments(t, s, n_mu=128), em.lrs_moments(t, -s, n_mu=128)
        iso = em.beta_vector(t, 1.0)
        second_order = iso - s * s * t * math.exp(-t) / 10.0
        qmin, qmax = 1.0 - s / 2.0, 1.0 + s
        candidates = [qmin, qmax] + [q for q in (t / 6.0, t / 2.0) if qmin <= q <= qmax]
        third_values = [abs(t * math.exp(-t / q) * (3.0 * q - t) / q ** 5) for q in candidates]
        third_sup = max(third_values)
        taylor_bound = third_sup * abs(s) ** 3 / 6.0  # E|delta|^3 <= ||S||op^3.
        remainder = abs(plus.mean - second_order)
        # Stable form of 1-(1+t)exp(-t).
        coefficient = 2.0 * (-math.expm1(-t) - t * math.exp(-t)) / (15.0 * t)
        observed_odd_coefficient = (plus.pstf - minus.pstf) / (2.0 * s)
        coefficient_error = float(np.linalg.norm(observed_odd_coefficient - coefficient * unit_shear))
        checks.append(check_record("weak_shear", f"t={t:g};scalar_Taylor_remainder",
                                   remainder <= taylor_bound + 2.0e-12, remainder, taylor_bound + 2.0e-12))
        checks.append(check_record("weak_shear", f"t={t:g};Q_odd_coefficient",
                                   coefficient_error <= 1.0e-6, coefficient_error, 1.0e-6))
        rows.append({"t": t, "s": s, "B_plus": plus.mean, "B_minus": minus.mean,
                     "scalar_coefficient_observed": (plus.mean - iso) / s ** 2,
                     "scalar_coefficient_expected": -t * math.exp(-t) / 10.0,
                     "scalar_remainder": remainder, "Taylor_third_derivative_sup": third_sup,
                     "Taylor_sup_candidates": candidates, "Taylor_remainder_bound": taylor_bound,
                     "Q_coefficient_expected": coefficient, "Q_coefficient_F_error": coefficient_error,
                     "Q_odd_coefficient": observed_odd_coefficient.tolist()})
    return checks, rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true", help="Explicitly run the frozen finite study")
    parser.add_argument("--attempt", default="attempt_001")
    args = parser.parse_args()
    if not args.execute:
        parser.error("Use --execute only after the Stage A contract/source checkpoint is preserved")
    if not args.attempt.replace("_", "").replace("-", "").isalnum():
        parser.error("attempt must be a simple label")
    output = UNIT / "results" / args.attempt
    output.mkdir(parents=True, exist_ok=False)
    evidence = UNIT / "evidence"
    evidence.mkdir(parents=True, exist_ok=True)
    log_path = evidence / (args.attempt + ".log")
    log_file = log_path.open("x", buffering=1)
    started_at, started = utc_now(), time.monotonic()
    rows, all_checks, scalar_rows, rotation_rows, weak_rows = [], [], [], [], []
    stage_counts = {}
    last_case = None
    exception_record = None
    status = "RUNNING"
    em.COUNTERS.clear()

    def say(message):
        line = f"{utc_now()} {message}"
        print(line, flush=True)
        log_file.write(line + "\n")

    def deadline():
        if time.monotonic() - started > 180.0:
            raise StudyBudgetStop("180-second study target reached; preserve partial results")

    def terminate(signum, frame):
        raise StudyBudgetStop(f"Received signal {signum}; preserve partial results")

    signal.signal(signal.SIGTERM, terminate)
    source_paths = [UNIT / "FROZEN_CONTRACT.md", UNIT / "THEORY.md", em.DONOR_PATH,
                    Path(em.__file__), Path(__file__)]
    identity = {str(p.relative_to(UNIT)): {"sha256": sha256(p), "bytes": p.stat().st_size} for p in source_paths}
    request = {"unit": "ANGULAR01", "attempt": args.attempt, "started_at_utc": started_at,
               "command": shlex.join([sys.executable, *sys.argv]), "source_identity": identity,
               "planned_grid_points": 405, "planned_new_donor_scalars": 20,
               "new_cosmological_IVPs": 0, "old_IVPs": 0, "old_test_suites": 0,
               "thread_environment": {k: os.environ[k] for k in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "BLIS_NUM_THREADS")},
               "python": sys.version, "numpy": np.__version__, "platform": platform.platform(),
               "study_target_seconds": 180, "required_external_hard_timeout_seconds": 240,
               "memory_target_MiB": 256,
               "quadrature_claim": "FINITE_OBSERVED_COMPARISONS_NOT_GLOBAL_CONVERGENCE",
               "bound_claim": "ANALYTIC_TRUNCATION_NOT_INTERVAL_FLOATING_CERTIFICATION"}
    try:
        from threadpoolctl import threadpool_info
        request["observed_threadpools"] = threadpool_info()
    except ImportError:
        request["observed_threadpools"] = "NOT_AVAILABLE; one-thread environment set before NumPy import"
    save_json(output / "EXECUTION_REQUEST.json", request)
    say(f"BEGIN ANGULAR01 {args.attempt}; 405 parameter points, 20 donor scalars, IVPs=0")
    try:
        if identity["vendor/hyrec_spike_transfer.py"]["sha256"] != em.DONOR_SHA256:
            raise RuntimeError("Pinned donor byte identity mismatch; do not execute science")
        checks, scalar_rows = function_and_scalar_checks()
        all_checks.extend(checks)
        stage_counts["standalone_function_checks"] = dict(em.COUNTERS)
        save_json(output / "scalar_reference.json", scalar_rows)
        save_json(output / "standalone_checks.json", all_checks)
        say(f"Function/scalar checks: {len(checks)} checks, {sum(not x['passed'] for x in checks)} failures")
        before = Counter(em.COUNTERS)
        with (output / "grid.csv").open("x", newline="") as csv_file, (output / "grid_checks.jsonl").open("x") as detail_file:
            writer = None
            index = 0
            for name, eigenvalues, lrs_s in SPECTRA:
                for t in np.logspace(-8.0, 3.0, 45):
                    deadline()
                    last_case = {"index": index, "spectrum": name, "t": float(t), "phase": "STARTED"}
                    save_json(output / "PROGRESS.json", {"completed_rows": len(rows), "last_case": last_case})
                    row, flags = grid_case(index, name, eigenvalues, lrs_s, float(t))
                    if writer is None:
                        writer = csv.DictWriter(csv_file, fieldnames=list(row))
                        writer.writeheader()
                    writer.writerow(row)
                    csv_file.flush()
                    detail_file.write(json.dumps(clean_json({"index": index, "spectrum": name, "t": float(t), "checks": flags})) + "\n")
                    detail_file.flush()
                    rows.append(row)
                    last_case["phase"] = "COMPLETED"
                    save_json(output / "PROGRESS.json", {"completed_rows": len(rows), "last_case": last_case})
                    index += 1
                say(f"Grid spectrum {name}: {len(rows)}/405 rows; failed rows={sum(not x['passed'] for x in rows)}")
        stage_counts["grid_quadratures_and_auto"] = dict(Counter(em.COUNTERS) - before)
        before = Counter(em.COUNTERS)
        checks, rotation_rows = rotation_checks(deadline)
        all_checks.extend(checks)
        stage_counts["standalone_rotation"] = dict(Counter(em.COUNTERS) - before)
        save_json(output / "rotation_oracle.json", rotation_rows)
        save_json(output / "standalone_checks.json", all_checks)
        before = Counter(em.COUNTERS)
        checks, weak_rows = weak_shear_checks(deadline)
        all_checks.extend(checks)
        stage_counts["standalone_weak_shear"] = dict(Counter(em.COUNTERS) - before)
        save_json(output / "weak_shear.json", weak_rows)
        save_json(output / "standalone_checks.json", all_checks)
        deadline()
        status = "PASS" if len(rows) == 405 and all(row["passed"] for row in rows) and all(x["passed"] for x in all_checks) else "FAIL"
    except StudyBudgetStop as exc:
        status, exception_record = "PARTIAL_BUDGET_STOP", {"type": type(exc).__name__, "message": str(exc)}
        say(str(exc))
    except Exception as exc:
        status = "ERROR"
        exception_record = {"type": type(exc).__name__, "message": str(exc), "traceback": traceback.format_exc()}
        say(exception_record["traceback"])
    finally:
        elapsed = time.monotonic() - started
        peak_mib = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0
        failed_rows = [{"index": r["index"], "spectrum": r["spectrum"], "t": r["t"], "failed_checks": r["failed_checks"]} for r in rows if not r["passed"]]
        failed_checks = [x for x in all_checks if not x["passed"]]
        maxima = {}
        for column in ("two_level_B_normalized", "two_level_Q_normalized", "lrs_1d_2d_B_normalized", "lrs_1d_2d_Q_normalized", "auto_observed_B_normalized", "auto_observed_Q_normalized"):
            values = [float(row[column]) for row in rows if row[column] is not None]
            maxima[column] = max(values) if values else None
        summary = {"schema": "ANGULAR01_FINITE_STUDY_V1", "unit": "ANGULAR01", "attempt": args.attempt,
                   "status": status, "started_at_utc": started_at, "finished_at_utc": utc_now(),
                   "grid_points_planned": 405, "grid_points_completed": len(rows),
                   "grid_points_passed": sum(r["passed"] for r in rows), "failed_grid_points": failed_rows,
                   "standalone_checks": len(all_checks), "standalone_checks_passed": sum(x["passed"] for x in all_checks),
                   "failed_standalone_checks": failed_checks, "new_donor_scalar_comparisons": len(scalar_rows),
                   "rotation_parameter_cases": len(rotation_rows), "weak_shear_parameter_cases": len(weak_rows),
                   "auto_thick_grid_points": sum(r["auto_eligible"] for r in rows),
                   "auto_quadrature_grid_points": sum(not r["auto_eligible"] for r in rows),
                   "elapsed_seconds": elapsed, "peak_RSS_MiB": peak_mib,
                   "memory_target_met": peak_mib < 256.0, "study_time_target_met": elapsed <= 180.0,
                   "actual_call_counts": dict(em.COUNTERS), "counts_by_phase": stage_counts,
                   "maxima": maxima, "last_case": last_case, "exception": exception_record,
                   "new_cosmological_IVPs": 0, "old_IVPs": 0, "old_test_suites": 0,
                   "global_convergence": "NOT_RUN", "production": "NOT_APPROVED", "REI_activation": False,
                   "Physical": "HOLD", "REC_U5": "HOLD_9_FAIL/HOLD_8_FAIL; CLOSED_HOLD_NOT_RESET",
                   "claims": {"finite_comparisons": "OBSERVED_ONLY", "thick_error": "ANALYTIC_TRUNCATION_BOUND", "floating_error": "NOT_INTERVAL_CERTIFIED"}}
        save_json(output / "study_summary.json", summary)
        save_json(output / "standalone_checks.json", all_checks)
        save_json(output / "FILES.json", {str(p.relative_to(output)): {"sha256": sha256(p), "bytes": p.stat().st_size} for p in sorted(output.iterdir()) if p.is_file() and p.name != "FILES.json"})
        say(f"END status={status}; grid={len(rows)}/405; standalone={len(all_checks)}; elapsed={elapsed:.3f}s; peak_RSS={peak_mib:.3f}MiB")
        log_file.close()
    return 0 if status == "PASS" else (124 if status == "PARTIAL_BUDGET_STOP" else 1)


if __name__ == "__main__":
    raise SystemExit(main())
