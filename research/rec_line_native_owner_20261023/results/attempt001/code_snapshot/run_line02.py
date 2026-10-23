"""One finite LINE02 pass. Refuses to overwrite attempt001 or any output."""
from __future__ import annotations

import csv
from datetime import datetime, timezone
from decimal import Decimal, localcontext
import hashlib
import json
import math
import os
from pathlib import Path
import platform
import shutil
import sys
import time
import traceback

import numpy as np
import scipy
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import native_line_owner as nlo
import escape_moments as angular

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "attempt001"
FIG = ROOT / "figures"
START = time.monotonic()
CHECKS = []
ACTIVE_CONTEXT = {}
COUNTS = {
    "owner_cases": 0, "full_313_reference_solves": 0, "direct_schur_2x2_solves": 0,
    "jvp_directions": 0, "complex_313_reference_solves": 0, "angular_cases": 0,
    "propagated_bound_cases": 0, "additional_bound_rank_queries": 0,
    "invalid_cases": 0, "mutation_cases": 0, "rank_plot_samples": 0,
    "native_runtime_runs": 0, "ivp_runs": 0, "historical_campaign_replays": 0,
}
PROTECTED = {
    "Physical": "HOLD", "REC_U5": "HOLD_9_FAIL/HOLD_8_FAIL",
    "reset_status": "CLOSED_HOLD_NOT_RESET", "global_convergence": "NOT_RUN",
    "production": "NOT_APPROVED", "REI_activation": False,
    "historical_first_failed_REI_raw": "LOCAL_ONLY",
}


def serial(value):
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, dict):
        return {str(k): serial(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [serial(v) for v in value]
    return value


def write_json(name, value):
    path = OUT / name
    with path.open("x", encoding="utf-8") as f:
        json.dump(serial(value), f, indent=2, allow_nan=False)
        f.write("\n")
        f.flush()
        os.fsync(f.fileno())


def append(name, value):
    with (OUT / name).open("a", encoding="utf-8") as f:
        f.write(json.dumps(serial(value), allow_nan=False) + "\n")
        f.flush()
        os.fsync(f.fileno())


def log(message):
    stamp = datetime.now(timezone.utc).isoformat()
    with (OUT / "RUN_LOG.txt").open("a", encoding="utf-8") as f:
        f.write(f"{stamp} {message}\n")
        f.flush()
        os.fsync(f.fileno())
    print(message, flush=True)


def check(name, observed, limit=0.0, *, passed=None):
    ok = bool(observed <= limit) if passed is None else bool(passed)
    row = {"name": name, "observed": observed, "limit": limit, "passed": ok}
    CHECKS.append(row)
    append("CHECKS.jsonl", row)
    if not ok:
        raise AssertionError(f"{name}: observed={observed!r}, limit={limit!r}")
    return row


def digest(path):
    raw = path.read_bytes()
    return {"path": str(path.relative_to(ROOT)), "bytes": len(raw),
            "sha256": hashlib.sha256(raw).hexdigest()}


def relative_component(actual, reference):
    return float(np.max(np.abs(actual - reference) / np.maximum(np.abs(reference), 1e-30)))


def backward(matrix, state, source):
    scale = np.abs(matrix) @ np.abs(state) + np.abs(source) + np.finfo(float).tiny
    return float(np.max(np.abs(matrix @ state - source) / scale))


def jvp_error(actual, reference):
    difference = float(np.max(np.abs(actual - reference)))
    scale = max(float(np.max(np.abs(actual))), float(np.max(np.abs(reference))))
    component_scale = np.maximum(np.abs(reference), max(64 * nlo.EPS * scale, 1e-30))
    return {"absolute_inf": difference, "mixed_scale": scale,
            "scaled_inf": difference / scale if scale else difference,
            "component_max": float(np.max(np.abs(actual - reference) / component_scale))}


def source_reference(owner):
    with (ROOT / "inputs/ORIGINAL_HYREC_TRAJECTORY_SNAPSHOT.csv").open(newline="") as f:
        rows = list(csv.reader(f))
    meta = {r[1]: r[2] for r in rows if r[0] == "META"}
    real = {int(r[1]): r[2] for r in rows if r[0] == "REAL"}
    with localcontext() as ctx:
        ctx.prec = 70
        r = Decimal("4.662899067555897e15") * Decimal(meta["H_sInv"]) / (
            Decimal(meta["nH_cm3"]) * Decimal(meta["x1s"]))
        b = Decimal(3) * Decimal(meta["x1s"]) * Decimal(meta["Dfplus_Lya"])
        loss, incoming = r * Decimal(real[1]), r * b
        net = loss - incoming
        gross = abs(loss) + abs(incoming)
        computed = owner.r0 * (owner.src.xr[1] - owner.b0)
        error = abs(Decimal.from_float(computed) - net)
        allowance = Decimal("5e-13") * gross
        check("native_net_against_70digit_source_decimal", float(error), float(allowance))
        return {
            "precision": 70, "r_s_inv": str(r), "b_departure": str(b),
            "signed_loss_departure": str(loss), "signed_incoming_departure": str(incoming),
            "net_per_H_s": str(net), "gross_scale": str(gross),
            "computed_float": computed, "absolute_error": float(error),
            "allowance": float(allowance),
        }


def write_csv(name, rows):
    path = OUT / name
    with path.open("x", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def save_figure(figure, name, caption, sources):
    figure.tight_layout()
    png, pdf = FIG / (name + ".png"), FIG / (name + ".pdf")
    if png.exists() or pdf.exists():
        raise FileExistsError("refusing to overwrite figure")
    figure.savefig(png, dpi=170, bbox_inches="tight")
    figure.savefig(pdf, bbox_inches="tight")
    plt.close(figure)
    return {"name": name, "caption": caption,
            "source_data": [digest(OUT / path) for path in sources],
            "png": digest(png), "pdf": digest(pdf), "PDF_raster_review": "NOT_RUN"}


def main():
    global ACTIVE_CONTEXT
    if OUT.exists():
        raise FileExistsError("attempt001 already exists; preserve it and target a diagnosed resume")
    OUT.mkdir(parents=True)
    FIG.mkdir(parents=True, exist_ok=True)
    for name in ("native_line_owner.py", "run_line02.py"):
        copy = OUT / "code_snapshot" / name
        copy.parent.mkdir(exist_ok=True)
        shutil.copyfile(ROOT / "code" / name, copy)
    paths = [
        "code/native_line_owner.py", "code/run_line02.py", "code/escape_moments.py",
        "vendor/original_hyrec_physical_flux.py", "vendor/hyrec_spike_transfer.py",
        "inputs/ORIGINAL_HYREC_TRAJECTORY_SNAPSHOT.csv",
        "FROZEN_CONTRACT.md", "PREEXEC_BOUND_ADDENDUM.md", "THEORY.md",
    ]
    identities = [digest(ROOT / p) for p in paths]
    write_json("ENVIRONMENT.json", {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(), "python": sys.version,
        "numpy": np.__version__, "scipy": scipy.__version__, "matplotlib": matplotlib.__version__,
        "platform": platform.platform(), "argv": sys.argv, "cwd": os.getcwd(),
        "command": os.environ.get("LINE02_COMMAND", "python code/run_line02.py"),
        "threads": {k: os.environ.get(k) for k in (
            "OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS")},
        "identities": identities,
        "reconstruction_identity": "NEW_CODE_IDENTITY_AFTER_LOSS_NOT_BYTE_RECOVERY",
        "previous_review_inherited_as_test": False,
    })
    log("START: first new-code primary pass; no native history or IVP.")
    owner = nlo.NativeLineOwner()
    q = owner.src
    write_json("AST_REUSE.json", owner.reuse)
    expected_hashes = {
        "inputs/ORIGINAL_HYREC_TRAJECTORY_SNAPSHOT.csv": nlo.INPUT_SHA256,
        "vendor/original_hyrec_physical_flux.py": nlo.SOURCE_SHA256,
        "vendor/hyrec_spike_transfer.py": nlo.DONOR_SHA256,
        "code/escape_moments.py": nlo.ANGULAR_SHA256,
    }
    for path, expected in expected_hashes.items():
        check("immutable_identity_" + path, digest(ROOT / path)["sha256"],
              passed=digest(ROOT / path)["sha256"] == expected)
    reference = source_reference(owner)
    partition = {
        "photoionization_Beta": float(q.Beta[1]), "2p_to_2s_mixing": float(-q.Trr[0, 1]),
        "direct_Lya": owner.r0,
        "two_photon_Raman": -math.fsum(q.Tvr[1]) - q.A2p_up_s_inv - q.A2p_dn_s_inv,
        "virtual_diffusion": q.A2p_up_s_inv + q.A2p_dn_s_inv,
    }
    partition_error = abs(math.fsum(partition.values()) - q.Trr[1, 1])
    check("native_2p_diagonal_partition", partition_error,
          64 * nlo.EPS * math.fsum(abs(v) for v in partition.values()))
    host_K = owner.K.copy()
    host_K[1, 1] -= owner.r0
    host_inverse = np.linalg.inv(host_K)
    check("host_inverse_nonnegative", float(np.min(host_inverse)), passed=np.min(host_inverse) >= 0.0)
    check("native_gamma_physical_branch", owner.gamma0, passed=0 <= owner.gamma0 < 1)
    modern_coefficient = 8 * math.pi / (3 * (100 * nlo.H_SI * nlo.C_SI / nlo.ENERGY_J) ** 3)
    prep = {
        "r0_s_inv": owner.r0, "b0_departure": owner.b0, "s0_per_H_s": owner.s0,
        "native_tau": owner.native_tau, "gamma0": owner.gamma0, "K_condition": owner.K_condition,
        "K": owner.K, "j": owner.j, "v": owner.v, "a": owner.a,
        "host_K_inverse": host_inverse, "host_inverse_diagnostic_solves": 1,
        "diagonal_partition_s_inv": partition, "diagonal_partition_absolute_error": partition_error,
        "source_decimal_reference": reference,
        "saved_snapshot_backward": backward(owner.M, q.source_solution, owner.s),
        "prepared_backward": backward(owner.M, owner.X0, owner.s),
        "saved_vs_prepared_component_error": relative_component(q.source_solution, owner.X0),
        "native_constant": nlo.LYA_FACT_CM3_INV,
        "modern_hc_reconstructed_coefficient": modern_coefficient,
        "modern_hc_relative_difference": modern_coefficient / nlo.LYA_FACT_CM3_INV - 1,
        "source_constant_difference_is_not_roundoff": True,
    }
    write_json("PREPARATION.json", prep)
    np.savez_compressed(OUT / "PREPARED_BLOCKS.npz", M=owner.M, source=owner.s, W=owner.W,
                        u=owner.u, K=owner.K, j=owner.j, X0=owner.X0, w=owner.w)
    log("Prepared original 313 blocks, one 3-RHS virtual band solve, one 2-RHS real solve.")

    controls = [
        ("native_exact", 1.0, 1.0), ("line_removed", 0.0, 1.0),
        ("half_line", .5, 1.0), ("double_line", 2.0, 1.0),
        ("zero_incoming", 1.0, 0.0), ("blue_minus", 1.0, .9), ("blue_plus", 1.0, 1.1),
    ]
    solutions, owner_rows = {}, []
    for name, rr, bb in controls:
        r, b = rr * owner.r0, bb * owner.b0
        sol = owner.solution(r, b)
        matrix, source = owner.assembled(r, b)
        independent_matrix = owner.original.dense_original_hyrec_matrix(q)
        independent_source = np.concatenate((q.sr, q.sv))
        independent_matrix[1, 1] = independent_matrix[1, 1] - owner.r0 + r
        independent_source[1] = independent_source[1] - owner.r0 * owner.b0 + r * b
        full = np.linalg.solve(independent_matrix, independent_source)
        COUNTS["full_313_reference_solves"] += 1
        K, j = owner.K.copy(), owner.j.copy()
        K[1, 1] += r - owner.r0
        j[1] += r * b - owner.s0
        real = np.linalg.solve(K, j)
        direct_schur = np.concatenate((real, owner.u - owner.W @ real))
        COUNTS["direct_schur_2x2_solves"] += 1
        ACTIVE_CONTEXT = {"stage": "owner", "case": name, "rank_state": sol.state,
                          "full_state": full, "direct_schur_state": direct_schur}
        mask = np.ones((313, 313), dtype=bool)
        mask[1, 1] = False
        source_mask = np.arange(313) != 1
        check(name + "_unchanged_matrix_blocks", bool(np.array_equal(matrix[mask], owner.M[mask])),
              passed=np.array_equal(matrix[mask], owner.M[mask]))
        check(name + "_unchanged_source_blocks", bool(np.array_equal(source[source_mask], owner.s[source_mask])),
              passed=np.array_equal(source[source_mask], owner.s[source_mask]))
        errors = {
            "rank_real": relative_component(sol.real, full[:2]),
            "rank_virtual": relative_component(sol.virtual, full[2:]),
            "schur_real": relative_component(direct_schur[:2], full[:2]),
            "schur_virtual": relative_component(direct_schur[2:], full[2:]),
        }
        for label, value in errors.items():
            check(name + "_" + label, value, 5e-10)
        back = backward(independent_matrix, sol.state, independent_source)
        check(name + "_full_backward", back, 5e-12)
        api_residual = owner.residual(sol.state, r, b)
        gross = np.abs(independent_matrix) @ np.abs(sol.state) + np.abs(independent_source) + np.finfo(float).tiny
        api_backward = float(np.max(np.abs(api_residual) / gross))
        api_assembly_error = float(np.max(np.abs(api_residual - (independent_matrix @ sol.state - independent_source)) / gross))
        check(name + "_residual_API_backward", api_backward, 5e-12)
        check(name + "_residual_API_vs_assembly", api_assembly_error, 64 * nlo.EPS)
        populations = owner.physical_populations(sol.state)
        virtual_occupation = q.blackbody_occupation + sol.virtual / q.x1s
        blue_occupation = 1 / math.expm1(nlo.E21_EV / q.TR_eV_rescaled) + b / (3 * q.x1s)
        check(name + "_physical_population_positive", min(populations.values()),
              passed=min(populations.values()) >= 0)
        check(name + "_virtual_occupation_positive", float(np.min(virtual_occupation)),
              passed=np.min(virtual_occupation) >= 0)
        check(name + "_blue_occupation_positive", blue_occupation, passed=blue_occupation >= 0)
        if name == "native_exact":
            check("native_reinsertion_exact_matrix", True, passed=np.array_equal(matrix, owner.M))
            check("native_reinsertion_exact_source", True, passed=np.array_equal(source, owner.s))
        ledger = nlo.event_ledger(owner.solved_line_rate(sol), owner.nH_m3)
        check(name + "_ledger", nlo.ledger_invariants(ledger), passed=nlo.ledger_invariants(ledger)["passed"])
        row = {
            "case": name, "r_ratio": rr, "b_ratio": bb, "r_s_inv": r, "b_departure": b,
            "eta": sol.eta, "alpha": sol.alpha, "condition_Kstar": float(np.linalg.cond(K)),
            "state": sol.state, "full_reference": full, "direct_schur": direct_schur,
            "errors": errors, "backward": back, "API_backward": api_backward,
            "API_assembly_error": api_assembly_error, "API_residual": api_residual,
            "physical_populations": populations, "min_virtual_total_occupation": float(np.min(virtual_occupation)),
            "blue_total_occupation": blue_occupation, "stable_drive": owner.solved_drive(sol),
            "rounded_drive": float(sol.state[1] - b), "ledger": ledger,
        }
        append("OWNER_CASES.jsonl", row)
        owner_rows.append(row)
        solutions[name] = sol
        COUNTS["owner_cases"] += 1
    log("Completed seven exclusive owner controls against full313 and Schur2 references.")

    step = 1e-30
    for base_name in ("native_exact", "half_line", "blue_plus"):
        sol = solutions[base_name]
        for direction_name in ("state_only", "r_only", "b_only", "mixed"):
            dx = (np.cos(np.arange(313) * .37) * np.maximum(np.abs(sol.state), 1e-30)
                  if direction_name in ("state_only", "mixed") else np.zeros(313))
            dr = .13 * owner.r0 if direction_name in ("r_only", "mixed") else 0.0
            db = .17 * owner.b0 if direction_name in ("b_only", "mixed") else 0.0
            residual_jvp = owner.residual_jvp(sol.state, dx, sol.r_s_inv, sol.b_departure, dr=dr, db=db)
            solution_jvp = owner.solution_jvp(sol, dr=dr, db=db)
            cr, cb = sol.r_s_inv + 1j * step * dr, sol.b_departure + 1j * step * db
            cm = owner.original.dense_original_hyrec_matrix(q).astype(complex)
            cs = np.concatenate((q.sr, q.sv)).astype(complex)
            cm[1, 1] = cm[1, 1] - owner.r0 + cr
            cs[1] = cs[1] - owner.r0 * owner.b0 + cr * cb
            residual_ref = np.imag(cm @ (sol.state + 1j * step * dx) - cs) / step
            solution_ref = np.imag(np.linalg.solve(cm, cs)) / step
            COUNTS["complex_313_reference_solves"] += 1
            residual_error = jvp_error(residual_jvp, residual_ref)
            solution_error = jvp_error(solution_jvp, solution_ref)
            raw = {
                "case": base_name + "_" + direction_name, "state_direction": dx, "dr": dr, "db": db,
                "complex_step": step, "residual_jvp": residual_jvp, "residual_reference": residual_ref,
                "solution_jvp": solution_jvp, "solution_reference": solution_ref,
                "residual_error": residual_error, "solution_error": solution_error,
            }
            ACTIVE_CONTEXT = raw
            check(raw["case"] + "_residual_JVP", residual_error["scaled_inf"], 5e-9)
            check(raw["case"] + "_solution_JVP", solution_error["scaled_inf"], 5e-9)
            if direction_name == "state_only":
                check(raw["case"] + "_solved_zero_exact", True,
                      passed=np.array_equal(solution_jvp, np.zeros(313)) and np.array_equal(solution_ref, np.zeros(313)))
            append("JVP_CASES.jsonl", raw)
            COUNTS["jvp_directions"] += 1
    log("Completed twelve residual and solved-state JVP directions with complex full algebra.")

    zero = np.zeros((3, 3))
    tri = np.diag([-.4, .1, .3])
    axis = np.array([1., 2., -1.]) / math.sqrt(6)
    cross = np.array([[0., -axis[2], axis[1]], [axis[2], 0., -axis[0]], [-axis[1], axis[0], 0.]])
    rotation = np.eye(3) * math.cos(.73) + (1 - math.cos(.73)) * np.outer(axis, axis) + math.sin(.73) * cross
    angular_cases = [
        ("native_iso", owner.native_tau, zero, False),
        ("native_tri", owner.native_tau, tri, False),
        ("native_rotated", owner.native_tau, rotation @ tri @ rotation.T, False),
    ]
    for tau in (.3, 2., 30.):
        angular_cases.extend([(f"synthetic_{tau:g}_iso", tau, zero, True),
                              (f"synthetic_{tau:g}_tri", tau, tri, True)])
    angular_rows = []
    for name, tau, shear, synthetic in angular_cases:
        row = owner.angular_event(tau, shear, synthetic=synthetic)
        row["case"] = name
        ACTIVE_CONTEXT = {"stage": "angular_event", "row": row}
        invariants = nlo.ledger_invariants(row["ledger"])
        check(name + "_ledger", invariants, passed=invariants["passed"])
        check(name + "_PSTF_projection", row["PSTF_projection_norm"], 64 * nlo.EPS * abs(row["C"]))
        bound = owner.state_bound(row["rbase_s_inv"], owner.b0, tau, shear,
                                 base_solution=None if synthetic else solutions["native_exact"])
        row["bound"] = bound
        if synthetic:
            finite = owner.solution(row["rstar_s_inv"], owner.b0)
            COUNTS["additional_bound_rank_queries"] += 2
            base_state = bound["baseline_state"]
            finite_flux = owner.solved_line_rate(finite)
            base_flux = bound["baseline_flux_per_H_s"]
            finite_tensor = nlo.ENERGY_J * owner.nH_m3 * row["rbase_s_inv"] * owner.solved_drive(finite) * row["D"]
            KS = 2 * shear / 15
            base_tensor = nlo.ENERGY_J * owner.nH_m3 * base_flux * KS
            differences = {
                "state_inf": float(np.max(np.abs(finite.state - base_state))),
                "flux_per_H_s": abs(finite_flux - base_flux),
                "tensor_J_m3_s": float(np.linalg.norm(finite_tensor - base_tensor, ord="fro")),
            }
            flux_roundoff = 64 * nlo.EPS * (abs(finite_flux) + abs(base_flux))
            roundoff = {
                "state_inf": 64 * nlo.EPS * max(float(np.max(np.abs(finite.state))), float(np.max(np.abs(base_state)))),
                "flux_per_H_s": flux_roundoff,
                "tensor_J_m3_s": nlo.ENERGY_J * owner.nH_m3 * flux_roundoff *
                    max(float(np.linalg.norm(row["D"])), float(np.linalg.norm(KS)), 1.0),
            }
            comparison = {
                "finite_state": finite.state, "finite_stable_drive": owner.solved_drive(finite),
                "finite_rounded_drive": float(finite.state[1] - owner.b0), "finite_flux": finite_flux,
                "finite_tensor": finite_tensor, "baseline_tensor": base_tensor,
                "differences": differences, "roundoff": roundoff,
                "departure_gross_flux_roundoff_not_used": 64 * nlo.EPS * row["rbase_s_inv"] *
                    (abs(finite.state[1]) + abs(owner.b0)),
                "bound_above_roundoff": {key: (bound["bounds"][key]["value"] or 0.) > roundoff[key] for key in differences},
                "scope": "NEW_SYNTHETIC_FROZEN_ALGEBRA_NOT_SAVED_SOURCE_EVENT",
            }
            ACTIVE_CONTEXT = {"stage": "angular_bound", "row": row, "comparison": comparison}
            for key, difference in differences.items():
                bound_value = bound["bounds"][key]["value"]
                check(name + "_propagated_" + key, difference, (bound_value or 0.) + roundoff[key])
            row["solved_bound_comparison"] = comparison
            COUNTS["propagated_bound_cases"] += 1
        append("ANGULAR_CASES.jsonl", row)
        angular_rows.append(row)
        COUNTS["angular_cases"] += 1
    covariance = float(np.linalg.norm(angular_rows[2]["D"] - rotation @ angular_rows[1]["D"] @ rotation.T))
    check("native_rotation_covariance", covariance, 5e-10 * angular_rows[1]["C"])
    log("Completed nine angular source rows and six bound controls with twelve additional rank queries.")

    invalid = [
        ("negative_r", lambda: owner.solution(-1., owner.b0)),
        ("nan_r", lambda: owner.solution(float("nan"), owner.b0)),
        ("infinite_r", lambda: owner.solution(float("inf"), owner.b0)),
        ("nan_b", lambda: owner.solution(owner.r0, float("nan"))),
        ("state_shape", lambda: owner.residual(np.zeros(312), owner.r0, owner.b0)),
        ("state_nonfinite", lambda: owner.residual(np.full(313, np.inf), owner.r0, owner.b0)),
        ("direction_shape", lambda: owner.residual_jvp(owner.X0, np.zeros(312), owner.r0, owner.b0)),
        ("duplicate_owner", lambda: owner.solution(owner.r0, owner.b0, native_owner_active=True)),
        ("additive_owner", lambda: nlo.NativeLineOwner(ownership="additive")),
        ("zero_tau", lambda: owner.angular_event(0., zero, synthetic=True)),
        ("contracting_direction", lambda: owner.angular_event(2., np.diag([-1.1, .5, .6]), synthetic=True)),
        ("collapsed_eta_margin", lambda: nlo.checked_denominator(32 * nlo.EPS, 1.)),
    ]
    for name, call in invalid:
        rejected, message = False, None
        try:
            call()
        except (ValueError, FloatingPointError) as exc:
            rejected, message = True, str(exc)
        check("invalid_" + name, rejected, passed=rejected)
        append("INVALID_CASES.jsonl", {"case": name, "rejected": rejected, "message": message})
        COUNTS["invalid_cases"] += 1
    bad_energy = dict(owner_rows[0]["ledger"])
    bad_energy["atomic_internal_J_m3_s"] *= -1
    invariants = nlo.ledger_invariants(bad_energy)
    check("mutation_wrong_internal_energy_sign_rejected", invariants, passed=not invariants["passed"])
    append("MUTATION_CASES.jsonl", {"case": "wrong_internal_energy_sign", "invariants": invariants})
    COUNTS["mutation_cases"] += 1
    wrong_pair = .5 * owner.r0 * owner.b0 - owner.r0 * owner.b0
    gross_pair = 1.5 * abs(owner.r0 * owner.b0)
    pair_rejected = abs(wrong_pair) > 64 * nlo.EPS * gross_pair
    check("mutation_unpaired_loss_at_equilibrium_rejected", abs(wrong_pair), passed=pair_rejected)
    append("MUTATION_CASES.jsonl", {"case": "half_loss_unchanged_incoming",
           "equilibrium_defect": wrong_pair, "roundoff_limit": 64 * nlo.EPS * gross_pair,
           "rejected": pair_rejected})
    COUNTS["mutation_cases"] += 1

    plot_rows = []
    for rr in (.5, 1., 2.):
        for bb in np.linspace(.8, 1.2, 61):
            sol = owner.solution(rr * owner.r0, float(bb) * owner.b0)
            row = {"r_ratio": rr, "b_ratio": float(bb), "xr2s": float(sol.real[0]),
                   "xr2p": float(sol.real[1]), "x2p": owner.physical_populations(sol.state)["x2p"],
                   "eta": sol.eta, "line_per_H_s": owner.solved_line_rate(sol),
                   "virtual_response_inf": float(np.max(np.abs(sol.virtual - owner.X0[2:])))}
            append("PLOT_SAMPLES.jsonl", row)
            plot_rows.append(row)
            COUNTS["rank_plot_samples"] += 1
    write_csv("AFFINE_RESPONSE.csv", plot_rows)
    angular_csv = [{
        "case": row["case"], "tau": row["tau"], "C": row["C"],
        "D_norm": float(np.linalg.norm(row["D"])), "photon_m3_s": row["ledger"]["photon_count_m3_s"],
        "radiation_J_m3_s": row["ledger"]["radiation_J_m3_s"],
        "atomic_internal_J_m3_s": row["ledger"]["atomic_internal_J_m3_s"],
        "D_xx": float(row["D"][0, 0]), "D_yy": float(row["D"][1, 1]), "D_zz": float(row["D"][2, 2]),
    } for row in angular_rows]
    write_csv("ANGULAR_LEDGER.csv", angular_csv)

    plt.rcParams.update({"font.size": 10, "axes.grid": True, "grid.alpha": .2})
    plot_manifest = []
    fig, axes = plt.subplots(1, 2, figsize=(11, 4))
    labels = ["Photoionization", "2p to 2s mixing", "Direct Ly-alpha", "Two-photon/Raman", "Virtual diffusion"]
    axes[0].barh(labels, list(partition.values()), color=["#7094bd", "#7094bd", "#bb5c35", "#7094bd", "#7094bd"])
    axes[0].set_xscale("log")
    axes[0].set_xlabel("2p diagonal contribution [s$^{-1}$]")
    axes[0].set_title("Native source ownership at z = 1100")
    axes[1].bar(["Loss departure", "Incoming departure", "Net emission"],
                [abs(float(reference["signed_loss_departure"])), abs(float(reference["signed_incoming_departure"])),
                 abs(float(reference["net_per_H_s"]))], color=["#537da2", "#76a69e", "#bb5c35"])
    axes[1].set_yscale("log")
    axes[1].set_ylabel("Signed departure magnitude [H$^{-1}$ s$^{-1}$]")
    axes[1].tick_params(axis="x", rotation=16)
    axes[1].set_title("Matched direct-line pair")
    plot_manifest.append(save_figure(fig, "line02_source_partition",
        "Actual preserved native source coefficients; departures are signed contributions, not positive microscopic gross rates.",
        ["PREPARATION.json"]))

    fig, axes = plt.subplots(2, 1, figsize=(8, 6), sharex=True)
    native_x2p = owner.physical_populations(owner.X0)["x2p"]
    for rr, color in zip((.5, 1., 2.), ("#4477aa", "#228833", "#cc6677")):
        selected = [row for row in plot_rows if row["r_ratio"] == rr]
        x = [row["b_ratio"] for row in selected]
        axes[0].plot(x, [100 * (row["x2p"] / native_x2p - 1) for row in selected],
                     label=f"r/r0 = {rr:g}", color=color)
        axes[1].plot(x, [row["line_per_H_s"] / 1e-15 for row in selected], color=color)
    axes[0].set_ylabel("2p population response [%]")
    axes[0].set_title("Exclusive affine source response, all other blocks frozen")
    axes[0].legend()
    axes[1].axhline(0, color=".4", linewidth=.7)
    axes[1].set_ylabel("Line event rate [$10^{-15}$ H$^{-1}$ s$^{-1}$]")
    axes[1].set_xlabel("Incoming departure b/b0")
    plot_manifest.append(save_figure(fig, "line02_affine_response",
        "183 new rank-one algebraic samples, three source-loss controls and 61 incoming-boundary values each; no history evolution.",
        ["AFFINE_RESPONSE.csv", "OWNER_CASES.jsonl"]))

    fig, axes = plt.subplots(2, 2, figsize=(11, 7))
    for suffix, color in (("iso", "#4477aa"), ("tri", "#cc6677")):
        selected = [row for row in angular_rows if row["case"].startswith("synthetic") and row["case"].endswith(suffix)]
        axes[0, 0].plot([r["tau"] for r in selected], [r["C"] for r in selected], "o-", color=color, label=suffix)
        axes[0, 1].plot([r["tau"] for r in selected], [np.linalg.norm(r["D"]) for r in selected], "o-", color=color, label=suffix)
    for ax in axes[0]:
        ax.set_xscale("log")
        ax.set_xlabel("Constructed opacity tau")
        ax.legend()
    axes[0, 0].axhline(1., color=".4", linewidth=.7)
    axes[0, 0].set_ylabel("Native rate factor C")
    axes[0, 1].set_ylabel("PSTF norm ||D||")
    native_rows = angular_rows[:3]
    x = np.arange(3)
    axes[1, 0].bar(x - .17, [r["ledger"]["radiation_J_m3_s"] / 1e-26 for r in native_rows],
                   width=.34, label="Radiation", color="#4477aa")
    axes[1, 0].bar(x + .17, [r["ledger"]["atomic_internal_J_m3_s"] / 1e-26 for r in native_rows],
                   width=.34, label="Atomic internal", color="#cc6677")
    axes[1, 0].set_xticks(x, ["Isotropic", "Triaxial", "Rotated"])
    axes[1, 0].set_ylabel("Native energy injection [$10^{-26}$ J m$^{-3}$ s$^{-1}$]")
    axes[1, 0].legend()
    for index, (label, color) in enumerate(zip(("xx", "yy", "zz"), ("#4477aa", "#228833", "#cc6677"))):
        axes[1, 1].bar(x + (index - 1) * .23, [r["D"][index, index] for r in native_rows],
                      width=.23, label=label, color=color)
    axes[1, 1].set_xticks(x, ["Isotropic", "Triaxial", "Rotated"])
    axes[1, 1].set_ylabel("Native tensor injection / scalar energy injection")
    axes[1, 1].legend()
    fig.suptitle("Direct bound-bound ledger: zero electron and ionic yield", y=1.02)
    plot_manifest.append(save_figure(fig, "line02_angular_ledger",
        "Six constructed finite-opacity coefficient controls above; three native scalar-state energy/PSTF injections below. Tensor injection is not stored radiation stress.",
        ["ANGULAR_LEDGER.csv", "ANGULAR_CASES.jsonl"]))
    write_json("PLOT_MANIFEST.json", plot_manifest)
    expected_counts = {"owner_cases": 7, "jvp_directions": 12, "angular_cases": 9,
                       "additional_bound_rank_queries": 12, "propagated_bound_cases": 6,
                       "invalid_cases": 12, "mutation_cases": 2, "rank_plot_samples": 183,
                       "full_313_reference_solves": 7, "complex_313_reference_solves": 12}
    for key, expected in expected_counts.items():
        check("count_" + key, COUNTS[key], passed=COUNTS[key] == expected)
    check("count_rank_queries", nlo.COUNTERS["rank_one_solution_queries"],
          passed=nlo.COUNTERS["rank_one_solution_queries"] == 202)
    for path, expected in expected_hashes.items():
        check("postrun_identity_" + path, digest(ROOT / path)["sha256"],
              passed=digest(ROOT / path)["sha256"] == expected)
    summary = {
        "status": "PASS", "counts": COUNTS, "operator_counters": dict(nlo.COUNTERS),
        "angular_counters": dict(angular.COUNTERS), "checks": len(CHECKS),
        "elapsed_s": time.monotonic() - START, "r0_s_inv": owner.r0,
        "b0_departure": owner.b0, "native_tau": owner.native_tau,
        "gamma0": owner.gamma0, "K_condition": owner.K_condition,
        "source_reference": reference, "rotation_covariance_abs": covariance,
        "max_rank_real_component_error": max(r["errors"]["rank_real"] for r in owner_rows),
        "max_rank_virtual_component_error": max(r["errors"]["rank_virtual"] for r in owner_rows),
        "max_backward": max(r["backward"] for r in owner_rows),
        "figures": len(plot_manifest), "figure_review": "PENDING_ACTUAL_PNG_INSPECTION",
        "protected_status": PROTECTED, "prior_review_inherited_as_test": False,
        "new_code_primary_only": True,
    }
    write_json("SUMMARY.json", summary)
    log("PASS: bounded primary complete; PNG visual inspection remains.")
    print(json.dumps(serial(summary), indent=2), flush=True)


if __name__ == "__main__":
    if OUT.exists():
        raise SystemExit("Immutable attempt001 already exists; no replay permitted.")
    try:
        main()
    except BaseException as exc:
        if OUT.exists() and not (OUT / "FAILURE.json").exists():
            write_json("FAILURE.json", {
                "status": "FAIL", "type": type(exc).__name__, "message": str(exc),
                "counts_completed": COUNTS, "operator_counters": dict(nlo.COUNTERS),
                "angular_counters": dict(angular.COUNTERS), "elapsed_s": time.monotonic() - START,
                "traceback": traceback.format_exc(), "active_context": ACTIVE_CONTEXT,
            })
            log(f"FAIL preserved: {type(exc).__name__}: {exc}")
        raise
    finally:
        if OUT.exists() and not (OUT / "MANIFEST.json").exists():
            write_json("MANIFEST.json", {
                "files": [digest(p) for p in sorted(OUT.rglob("*")) if p.is_file() and p.name != "MANIFEST.json"],
                "hash_scope": "ALL_ATTEMPT_PAYLOADS_EXCEPT_THIS_MANIFEST",
            })

