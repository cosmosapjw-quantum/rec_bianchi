"""THERM02 frozen eight-case runner with retained-state and energy ledgers.

--preflight checks runner contracts without any cosmological IVP or old suite.
--run executes only missing cases of the frozen cohort; completed exact-hash
outputs are reused, and preserved failures/interrupted attempts stop execution.
--plot reads finished arrays. No arguments print help and do not run science.
"""
from __future__ import annotations

import os
for _thread_key in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ[_thread_key] = "1"
os.environ.setdefault("MPLCONFIGDIR", "/tmp/therm02-mpl")

import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path
import platform
import sys
import tempfile
import time
import traceback

import numpy as np
import scipy
from numpy.polynomial.legendre import leggauss
from scipy.integrate import solve_ivp

from coupled_thermal import (ROOT, XEND, KB, LEDGER_COLUMNS,
                             CoupledThermalSystem, lift34, restrict63,
                             verify_reused_files)

SCHEMA = "therm02.compact34.full63.current_compton.v1"
BASE = dict(Sigma_F=.15, matter_A=.6, radiation_A=.15, T0_K=1000.,
            Emax_eV=60., uv_multiplier=1., rr_closure="mao2017")
CASES = {
    "t02_split_mao_off": dict(BASE, cmb_branch="off"),
    "t02_split_mao_hot": dict(BASE, cmb_branch="actual_hot"),
    "t02_split_mao_planck": dict(BASE, cmb_branch="planck_reference"),
    "t02_split_derivative_planck": dict(BASE, rr_closure="rate_derivative", cmb_branch="planck_reference"),
    "t02_iso_mao_planck": dict(BASE, Sigma_F=0., matter_A=0., radiation_A=0., cmb_branch="planck_reference"),
    "t02_split_mao_hot_tight34": dict(BASE, cmb_branch="actual_hot"),
    "t02_split_mao_planck_tight34": dict(BASE, cmb_branch="planck_reference"),
    "t02_split_mao_planck_oracle63": dict(BASE, cmb_branch="planck_reference"),
}
STATUS_FLAGS = dict(Physical="HOLD", REC_U5="HOLD_9_FAIL/HOLD_8_FAIL",
                    closure="CLOSED_HOLD_NOT_RESET", global_convergence="NOT_RUN",
                    production="NOT_APPROVED", REI_activation=False)
SOURCE_PATHS = ("code/run.py", "code/coupled_thermal.py", "code/checks.py",
                "FROZEN_CONTRACT.md", "provenance/REUSED_FILES.json")
LOCAL_RESIDUAL_NAMES = ("local_ledger_scaled", "local_transfer_scaled",
                        "atomic_source_scaled", "affine_direct_scaled")
CASE_SECONDS = 180.
TOTAL_SECONDS = 1200.


def utc_now():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def json_default(value):
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, Path):
        return str(value)
    raise TypeError(type(value).__name__)


def dump(path, value):
    """Closed atomic JSON replacement; successful receipts never use NaN."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".writing")
    temporary.write_text(json.dumps(value, indent=2, allow_nan=False,
                                    default=json_default) + "\n")
    os.replace(temporary, path)


def save_npz(path, **arrays):
    path = Path(path)
    temporary = path.with_name(path.name + ".writing")
    with temporary.open("wb") as handle:
        np.savez_compressed(handle, **arrays)
    os.replace(temporary, path)


def source_hashes():
    return {name: digest(ROOT / name) for name in SOURCE_PATHS}


def verify_pre_ode_receipt():
    """Reuse the existing adapter checks at their exact identities."""
    path = ROOT / "evidence/PRE_ODE_CHECKS.json"
    receipt = json.loads(path.read_text())
    if receipt.get("status") != "PASS" or receipt.get("exit_code") != 0:
        raise RuntimeError("MATCHING_PASS_PRE_ODE_CHECKS_REQUIRED")
    expected_names = set(SOURCE_PATHS) - {"code/run.py"}
    if set(receipt.get("code_input_sha256", {})) != expected_names:
        raise RuntimeError("PRE_ODE_RECEIPT_SOURCE_SET_CHANGED")
    for name, expected in receipt["code_input_sha256"].items():
        if digest(ROOT / name) != expected:
            raise RuntimeError("STALE_PRE_ODE_CHECK:" + name)
    if receipt.get("cosmological_IVPs_executed") != 0 or receipt.get("old_suites_executed") != 0:
        raise RuntimeError("PRE_ODE_RECEIPT_SCOPE_CHANGED")
    verify_reused_files()
    return dict(path=str(path.relative_to(ROOT)), sha256=digest(path),
                status="PASS_REUSED", suites_reexecuted=0)


def configuration(name):
    if name not in CASES:
        raise ValueError("case is outside frozen THERM02 cohort")
    tight = name.endswith("tight34")
    return dict(CASES[name], id=name, samples=193, x_start=0., x_end=XEND,
                method="BDF", rtol=2e-9/(100 if tight else 1),
                atol_divisor=100 if tight else 1, full63=name.endswith("oracle63"),
                max_step=.0125 if tight else .025, dense_output=True, t_eval=None)


def absolute_tolerances(config):
    full = np.r_[np.full(40, 2e-12), np.full(21, 2e-11), 2e-12, 2e-7]
    full /= config["atol_divisor"]
    return full if config["full63"] else restrict63(full)


def identity(name):
    payload = dict(schema=SCHEMA, sources=source_hashes(), config=configuration(name))
    payload["sha256"] = hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return payload


class Budget:
    """Cooperative cumulative limit, including prior receipts and failures."""
    def __init__(self, previous_seconds):
        self.previous_seconds = float(previous_seconds)
        self.started = time.perf_counter()

    @property
    def elapsed(self):
        return self.previous_seconds + time.perf_counter() - self.started

    def check(self, case_started=None):
        if self.elapsed > TOTAL_SECONDS:
            raise TimeoutError("THERM02 cumulative science 1200 s ceiling")
        if case_started is not None and time.perf_counter() - case_started > CASE_SECONDS:
            raise TimeoutError("THERM02 case 180 s ceiling including diagnostics")


def peak(value, x, *, absolute=True):
    value = np.asarray(value)
    selected = abs(value) if absolute else value
    index = int(np.argmax(selected))
    return dict(value=float(value[index]), index=index, x=float(x[index]),
                z=float(21 * np.exp(-x[index]) - 1))


def evaluate_states(system, x, states, budget, started, scope):
    """One current point serves diagnostics and the five ledger sources."""
    x = np.asarray(x)
    states = np.asarray(states)
    if x.ndim != 1 or states.shape != (system.size, len(x)) or not len(x):
        raise ValueError("invalid state sampling shape:" + scope)
    diagnostics, observations, integrands = [], [], []
    names = None
    for index, coordinate in enumerate(x):
        budget.check(started)
        try:
            point = system.point(float(coordinate), states[:, index])
            row = system.diagnose_from_point(point, float(coordinate))
            observations.append(row.pop("signed_observables"))
            if names is None:
                names = list(row)
            if list(row) != names:
                raise RuntimeError("diagnostic ordering changed")
            diagnostics.append([row[name] for name in names])
            integrands.append(system.ledger_from_point(point))
        except Exception as error:
            raise RuntimeError(f"POINT_EVALUATION_FAILED:{scope}:index={index}:x={coordinate:.17g}: {error}") from error
    diagnostics = np.asarray(diagnostics)
    observations = np.asarray(observations)
    integrands = np.asarray(integrands)
    D = {name: diagnostics[:, i] for i, name in enumerate(names)}
    full = states if system.full else lift34(states)
    Y = full[40:61].T * system.scale
    isotope_errors = {}
    for isotope, indices in system.atomic.isotope_groups.items():
        ii = list(indices)
        expected = float(system.atomic.initial_Y[ii].sum())
        isotope_errors[isotope] = float(np.max(abs(Y[:, ii].sum(axis=1) - expected)) / system.scale[ii[0]])
    baryon = abs(Y @ system.atomic.A - 1)
    number = np.maximum(abs(full[13] - 1), abs(full[31] - 1))
    tensor = abs(observations[:, 3] - observations[:, 1] - observations[:, 2])
    tau_increment = float(np.min(np.diff(full[61]))) if len(x) > 1 else 0.
    minimum = float(np.min(full[40:61]))
    metrics = dict(sample_count=len(x), x_range=[float(x[0]), float(x[-1])],
        minimum_scaled_population=minimum, isotope_errors=isotope_errors,
        maximum_baryon_error=float(baryon.max()), minimum_ne_m3=float(D["ne_m3"].min()),
        T_range_K=[float(D["T_K"].min()), float(D["T_K"].max())],
        minimum_tau_increment=tau_increment, maximum_number_monopole_error=float(number.max()),
        maximum_einstein_residual=float(D["einstein_residual"].max()),
        maximum_signed_tensor_sum_residual=float(tensor.max()),
        maximum_trace_energy_fraction=float(D["trace_energy_fraction"].max()),
        local_residual_peaks={name: peak(D[name], x) for name in LOCAL_RESIDUAL_NAMES},
        baryon_peak=peak(baryon, x), number_monopole_peak=peak(number, x),
        einstein_peak=peak(D["einstein_residual"], x), tensor_sum_peak=peak(tensor, x))
    gates = dict(finite=bool(np.isfinite(states).all() and np.isfinite(diagnostics).all()
                            and np.isfinite(observations).all() and np.isfinite(integrands).all()),
        increasing_x=bool(len(x) == 1 or np.all(np.diff(x) > 0)),
        minimum_isotope_fraction=minimum >= -2e-8,
        isotope_inventory=max(isotope_errors.values()) < 2e-7,
        baryon_error=float(baryon.max()) < 2e-8,
        nonnegative_electrons=float(D["ne_m3"].min()) >= 0,
        temperature_domain=bool(D["T_K"].min() >= 100 and D["T_K"].max() <= 1e6),
        tau_nondecreasing=tau_increment >= -2e-10,
        number_monopoles=float(number.max()) < 2e-9,
        einstein=float(D["einstein_residual"].max()) < 2e-13,
        signed_tensor_sum=float(tensor.max()) < 2e-16,
        trace_energy_fraction=float(D["trace_energy_fraction"].max()) < 1e-5,
        zero_n_T=bool(np.all(full[40 + np.array([0, 5, 6])] == 0) and np.all(D["decay_max"] == 0)),
        local_source_transfer=bool(all(D[name].max() < 5e-12 for name in LOCAL_RESIDUAL_NAMES)))
    return dict(names=names, diagnostics=diagnostics, obs=observations, full=full,
                Y=Y, integrands=integrands, D=D,
                report=dict(scope=scope, status="PASS" if all(gates.values()) else "FAIL",
                            gates=gates, metrics=metrics))


def require_scope(evaluated):
    report = evaluated["report"]
    if report["status"] != "PASS":
        failed = [name for name, passed in report["gates"].items() if not passed]
        raise RuntimeError("PHYSICAL_ADMISSION_FAILED:" + report["scope"] + ":" + ",".join(failed))


def cumulative_integrals(values, weights, halfwidths):
    """Integrate absolute instantaneous sources before cumulative summation."""
    per_interval = halfwidths[:, None] * np.einsum("j,ijk->ik", weights, values)
    per_interval_abs = halfwidths[:, None] * np.einsum("j,ijk->ik", weights, abs(values))
    zero = np.zeros((1, values.shape[2]))
    return (np.vstack((zero, np.cumsum(per_interval, axis=0))),
            np.vstack((zero, np.cumsum(per_interval_abs, axis=0))))


def ledger_residual(energy, ledger, absolute_ledger):
    residual = energy - energy[0] - ledger[:, 0] + ledger[:, 1] + ledger[:, 2] - ledger[:, 3] - ledger[:, 4]
    denominator = np.maximum.reduce((np.full(len(energy), abs(energy[0])), abs(energy),
                                     np.sum(absolute_ledger, axis=1)))
    if np.any(denominator <= 0) or not np.isfinite(denominator).all():
        raise ValueError("positive finite ledger normalization required")
    return residual, denominator, abs(residual) / denominator


def run_case(name, budget, adapter_receipt):
    ident = identity(name)
    directory = ROOT / "data" / name
    result_path = directory / "RESULT.json"
    raw_path = directory / "trajectory.npz"
    if result_path.exists():
        old = json.loads(result_path.read_text())
        if old.get("identity", {}).get("sha256") != ident["sha256"]:
            raise RuntimeError("SOURCE_CONFIG_IDENTITY_CHANGED:" + name)
        if old.get("status") != "PASS":
            raise RuntimeError("PRESERVED_FAILED_CASE_REQUIRES_ROOT_DECISION:" + name)
        if not old.get("artifacts"):
            raise RuntimeError("ARTIFACT_MANIFEST_REQUIRED:" + name)
        for relative, record in old["artifacts"].items():
            path = directory / relative
            if not path.is_file() or path.stat().st_size != record["bytes"] or digest(path) != record["sha256"]:
                raise RuntimeError("RAW_IDENTITY_CHANGED:" + name + ":" + relative)
        print(name + ": CACHE_VERIFIED (0 new IVPs)", flush=True)
        return old, False
    directory.mkdir(parents=True, exist_ok=True)
    if any(directory.iterdir()):
        raise RuntimeError("PRESERVED_INTERRUPTED_CASE_REQUIRES_ROOT_DECISION:" + name)
    budget.check()
    started = time.perf_counter()
    result = dict(schema=SCHEMA, id=name, status="FAIL", identity=ident, started_UTC=utc_now(),
        gates={}, physical_scopes={}, adapter_checks=adapter_receipt, statuses=STATUS_FLAGS,
        environment=dict(python=sys.version, numpy=np.__version__, scipy=scipy.__version__,
                         platform=platform.platform(), numerical_threads=1),
        resource_contract=dict(case_seconds=CASE_SECONDS, total_seconds=TOTAL_SECONDS,
                               enforcement="cooperative; serialization is included"))
    # Exclusive creation prevents two independently launched runners from
    # integrating the same case after both observed an empty directory.
    attempt = dict(id=name, identity=ident, started_UTC=result["started_UTC"],
        pid=os.getpid(), status="STARTED", next="result receipt required; never automatically retry")
    with (directory / "ATTEMPT.json").open("x") as handle:
        handle.write(json.dumps(attempt, indent=2, allow_nan=False) + "\n")
    system = None
    last_trial = None
    rhs_range = None
    partial = directory / "trajectory_partial.npz"
    payload = {}
    try:
        config = ident["config"]
        system = CoupledThermalSystem(config, full=config["full63"])
        system.started = started
        grid = np.linspace(0., XEND, 193)

        def recorded_rhs(x, state):
            nonlocal last_trial
            last_trial = (float(x), np.asarray(state).copy())
            budget.check(started)
            return system.rhs(x, state)

        solution = solve_ivp(recorded_rhs, (0., XEND), system.y0, method="BDF",
            rtol=config["rtol"], atol=absolute_tolerances(config), t_eval=None,
            max_step=config["max_step"], dense_output=True)
        # The actual accepted BDF nodes survive solver failure and all later gates.
        save_npz(directory / "solver_return.npz", x=solution.t, raw_state=solution.y.T)
        rhs_range = [system.min_trial_T, system.max_trial_T]
        result.update(nfev=int(solution.nfev), njev=int(solution.njev), nlu=int(solution.nlu),
                      accepted_nodes=len(solution.t), rhs_calls=system.nrhs,
                      solver_message=solution.message, solver_success=bool(solution.success),
                      rhs_trial_T_range_K=rhs_range)
        if not solution.success or solution.t[-1] != XEND or solution.y.shape[0] != system.size:
            raise RuntimeError("BDF incomplete: " + solution.message)
        budget.check(started)
        state = solution.sol(grid)
        payload.update(x=grid, z=21*np.exp(-grid)-1, raw_state=state.T,
                       accepted_x=solution.t, accepted_raw_state=solution.y.T)
        save_npz(partial, **payload)
        saved = evaluate_states(system, grid, state, budget, started, "saved193")
        result["physical_scopes"]["saved193"] = saved["report"]
        payload.update(full63_state=saved["full"].T, Y=saved["Y"],
            scaled_populations=saved["full"][40:61].T,
            signed_observables=saved["obs"], diagnostics=saved["diagnostics"],
            diagnostic_names=np.array(saved["names"]), species_names=np.array(system.atomic.names),
            A=system.atomic.A, q=system.atomic.q, isotope_scales=system.scale,
            initial_Y=system.atomic.initial_Y, ledger_columns=np.array(LEDGER_COLUMNS))
        save_npz(partial, **payload)
        require_scope(saved)

        accepted = evaluate_states(system, solution.t, solution.y, budget, started, "accepted_BDF_nodes")
        result["physical_scopes"]["accepted_BDF_nodes"] = accepted["report"]
        save_npz(directory / "solver_return.npz", x=solution.t, raw_state=solution.y.T,
            full63_state=accepted["full"].T, diagnostics=accepted["diagnostics"],
            diagnostic_names=np.array(accepted["names"]), signed_observables=accepted["obs"])
        require_scope(accepted)

        halfwidth = np.diff(grid) / 2
        midpoint = (grid[:-1] + grid[1:]) / 2
        for order in (8, 16):
            budget.check(started)
            nodes, weights = leggauss(order)
            xx = (midpoint[:, None] + halfwidth[:, None]*nodes).ravel()
            dense = solution.sol(xx)
            payload[f"dense_GL{order}_x"] = xx
            payload[f"dense_GL{order}_state"] = dense.T
            save_npz(partial, **payload)
            evaluated = evaluate_states(system, xx, dense, budget, started, f"dense_GL{order}")
            result["physical_scopes"][f"dense_GL{order}"] = evaluated["report"]
            values = evaluated["integrands"].reshape(len(halfwidth), order, 5)
            ledger, absolute_ledger = cumulative_integrals(values, weights, halfwidth)
            ratio_values = np.column_stack((evaluated["D"]["compton_over_HUgamma"],
                                            evaluated["D"]["compton_over_HUref"]))
            integrated_ratios, _unused = cumulative_integrals(
                ratio_values.reshape(len(halfwidth), order, 2), weights, halfwidth)
            payload[f"ledger_GL{order}"] = ledger
            payload[f"ledger_abs_GL{order}"] = absolute_ledger
            payload[f"dense_GL{order}_integrands"] = evaluated["integrands"]
            payload[f"dense_GL{order}_exchange_ratios"] = ratio_values
            payload[f"exchange_ratio_integrals_GL{order}"] = integrated_ratios
            save_npz(partial, **payload)
            require_scope(evaluated)

        energy = saved["D"]["epsilon_total_J"]
        residual, denominator, normalized = ledger_residual(
            energy, payload["ledger_GL16"], payload["ledger_abs_GL16"])
        difference = np.max(abs(payload["ledger_GL8"] - payload["ledger_GL16"]), axis=1) / denominator
        absolute_difference = np.max(abs(payload["ledger_abs_GL8"] - payload["ledger_abs_GL16"]), axis=1) / denominator
        payload.update(ledger_residual_J=residual, ledger_denominator_J=denominator,
                       ledger_normalized_residual=normalized, ledger_GL_difference=difference,
                       ledger_absolute_GL_difference=absolute_difference,
                       exchange_ratio_columns=np.array(["abs_Q_C_over_H_U_gamma", "abs_Q_C_over_H_U_ref"]))
        save_npz(partial, **payload)
        budget.check(started)
        gates = dict(full_interval_193=bool(len(grid) == 193 and grid[-1] == XEND),
            all_sampled_physical_scopes=all(row["status"] == "PASS" for row in result["physical_scopes"].values()),
            rhs_trial_temperature_domain=bool(rhs_range[0] >= 100 and rhs_range[1] <= 1e6),
            dense_integrated_energy=float(normalized.max()) < 3e-6,
            GL8_GL16_difference=float(difference.max()) < 3e-6,
            GL8_GL16_absolute_throughput=float(absolute_difference.max()) < 3e-6)
        result.update(gates=gates, max_energy_residual=float(normalized.max()),
            max_GL_difference=float(difference.max()),
            max_absolute_GL_difference=float(absolute_difference.max()),
            energy_residual_peak=peak(normalized, grid), GL_difference_peak=peak(difference, grid),
            energy_gate_margin_fraction=float(1 - normalized.max()/3e-6),
            final_T_K=float(saved["D"]["T_K"][-1]), final_tau=float(saved["D"]["tau_T"][-1]),
            T_range_K=[float(saved["D"]["T_K"].min()), float(saved["D"]["T_K"].max())],
            all_evaluated_T_range_K=[system.min_trial_T, system.max_trial_T],
            exchange_scale=dict(
                actual_density_peak=peak(saved["D"]["compton_over_HUgamma"], grid),
                external_reference_peak=peak(saved["D"]["compton_over_HUref"], grid),
                integral_GL16=payload["exchange_ratio_integrals_GL16"][-1].tolist(),
                integral_GL8=payload["exchange_ratio_integrals_GL8"][-1].tolist(),
                denominator_owners=["actual current photon density", "external reference; zero if inactive"],
                backreaction_error_bound="NOT_ESTABLISHED"),
            scope="finite saved193, accepted BDF nodes, GL8 and GL16 states; no continuum positivity claim")
        os.replace(partial, raw_path)
        result["raw_sha256"] = digest(raw_path)
        result["solver_return_sha256"] = digest(directory / "solver_return.npz")
        if not all(gates.values()):
            raise RuntimeError("FINITE_TRAJECTORY_GATE_FAILED:" + ",".join(k for k, v in gates.items() if not v))
        budget.check(started)
        result["status"] = "PASS"
    except Exception as error:
        result.update(error=str(error), traceback=traceback.format_exc())
        if last_trial is not None:
            save_npz(directory / "last_rhs_trial.npz", x=np.array([last_trial[0]]),
                     raw_state=last_trial[1][None, :])
        if system is not None:
            result["rhs_calls"] = system.nrhs
            values = (system.min_trial_T, system.max_trial_T)
            result["observed_T_range_K"] = [float(v) if np.isfinite(v) else None for v in values]
    result["completed_UTC"] = utc_now()
    result["artifacts"] = {str(p.relative_to(directory)): dict(bytes=p.stat().st_size, sha256=digest(p))
                           for p in sorted(directory.iterdir()) if p.is_file() and p != result_path}
    result["wall_seconds"] = time.perf_counter() - started
    result["cumulative_science_seconds"] = budget.elapsed
    if result["wall_seconds"] > CASE_SECONDS or budget.elapsed > TOTAL_SECONDS:
        result["status"] = "FAIL"
        result.setdefault("error", "cooperative budget exceeded while preserving output")
    dump(result_path, result)
    print(f"{name}: {result['status']} {result['wall_seconds']:.3f}s", flush=True)
    if result["status"] != "PASS":
        raise RuntimeError("THERM02 finite case failed; preserved " + str(result_path))
    return result, True


def comparisons():
    pairs = (("t02_split_mao_hot", "t02_split_mao_hot_tight34"),
             ("t02_split_mao_planck", "t02_split_mao_planck_tight34"),
             ("t02_split_mao_planck", "t02_split_mao_planck_oracle63"))
    rows = {}
    for nominal_name, other_name in pairs:
        with np.load(ROOT / "data" / nominal_name / "trajectory.npz", allow_pickle=False) as a, \
             np.load(ROOT / "data" / other_name / "trajectory.npz", allow_pickle=False) as b:
            if not np.array_equal(a["x"], b["x"]):
                raise RuntimeError("different comparison grids")
            na = {str(k): i for i, k in enumerate(a["diagnostic_names"])}
            nb = {str(k): i for i, k in enumerate(b["diagnostic_names"])}
            ta, tb = a["diagnostics"][:, na["T_K"]], b["diagnostics"][:, nb["T_K"]]
            relative_T = abs(ta-tb)/np.maximum(abs(ta), abs(tb))
            fractions = np.max(abs(a["scaled_populations"]-b["scaled_populations"]), axis=1)
            tau = abs(a["diagnostics"][:, na["tau_T"]]-b["diagnostics"][:, nb["tau_T"]])
            signed = abs(a["signed_observables"]-b["signed_observables"])
            values = dict(nominal=nominal_name, comparison=other_name,
                max_relative_T=float(relative_T.max()), max_charge_fraction_absolute=float(fractions.max()),
                max_tau_absolute=float(tau.max()), max_signed_normalized_absolute=float(signed.max()),
                signed_component_maxima=dict(zip(("shear", "matter", "radiation", "total", "gamma", "nu"),
                                                np.max(signed, axis=0).tolist())),
                peaks=dict(T=peak(relative_T, a["x"]), fractions=peak(fractions, a["x"]),
                           tau=peak(tau, a["x"]), signed=peak(np.max(signed, axis=1), a["x"])))
        values["gates"] = dict(T=values["max_relative_T"] < 3e-5,
            fractions=values["max_charge_fraction_absolute"] < 3e-5,
            tau=values["max_tau_absolute"] < 3e-7,
            signed=values["max_signed_normalized_absolute"] < 3e-7)
        values["status"] = "PASS" if all(values["gates"].values()) else "FAIL"
        rows[other_name] = values
    dump(ROOT / "results/VALIDATION_COMPARISONS.json", rows)
    return rows


def preflight():
    """New runner wiring checks only: no RHS, cosmological IVP, or old suite."""
    started = time.perf_counter()
    adapter = verify_pre_ode_receipt()
    configurations = {}
    for name in CASES:
        config = configuration(name)
        system = CoupledThermalSystem(config, full=config["full63"])
        atol = absolute_tolerances(config)
        if atol.shape != (system.size,) or not np.all(atol > 0):
            raise AssertionError("tolerance projection shape/positivity")
        original = system.expand(system.y0)
        if not np.allclose(lift34(restrict63(original)), original, rtol=0, atol=8*np.finfo(float).eps):
            raise AssertionError("initial compact admission")
        ident = identity(name)
        if json.loads(json.dumps(ident)) != ident:
            raise AssertionError("JSON identity round trip")
        configurations[name] = dict(size=system.size, rtol=config["rtol"],
            max_step=config["max_step"], atol_min=float(atol.min()), atol_max=float(atol.max()),
            identity_sha256=ident["sha256"], rhs_calls=system.nrhs)
    if len(configurations) != 8 or sum(c["size"] == 63 for c in configurations.values()) != 1:
        raise AssertionError("frozen 7 compact34 + 1 full63 configurations")
    # A source that reverses sign has zero net integral and nonzero throughput.
    weights = np.array([1., 1.])
    values = np.array([[[2., 1., .5, .7, .02]]*2, [[2., 1., .5, -.7, .02]]*2])
    ledger, absolute = cumulative_integrals(values, weights, np.array([.25, .25]))
    np.testing.assert_allclose(ledger[-1], [2., 1., .5, 0., .02], rtol=0, atol=1e-15)
    np.testing.assert_allclose(absolute[-1], [2., 1., .5, .7, .02], rtol=0, atol=1e-15)
    energy = 1 + ledger[:, 0]-ledger[:, 1]-ledger[:, 2]+ledger[:, 3]+ledger[:, 4]
    residual, denominator, normalized = ledger_residual(energy, ledger, absolute)
    np.testing.assert_allclose(normalized, 0., rtol=0, atol=2e-16)
    if denominator[-1] != np.sum(absolute[-1]) or absolute[-1, 3] <= abs(ledger[-1, 3]):
        raise AssertionError("instantaneous absolute throughput ownership")
    with tempfile.TemporaryDirectory(prefix="therm02-preflight-") as tmp:
        p = Path(tmp)/"fixture.npz"
        save_npz(p, raw_state=np.arange(68.).reshape(2, 34), ledger=ledger,
                 names=np.array(LEDGER_COLUMNS))
        with np.load(p, allow_pickle=False) as r:
            if not np.array_equal(r["ledger"], ledger) or r["raw_state"].shape != (2, 34):
                raise AssertionError("NPZ closed-file round trip")
    receipt = dict(schema=SCHEMA, status="PASS", command="python code/run.py --preflight",
        exit_code=0, time_UTC=utc_now(), source_sha256=source_hashes(), adapter_checks=adapter,
        configurations=configurations, checks=["frozen eight configurations and projected tolerances",
        "initial-state projection admission", "JSON identity round trip", "signed source/absolute throughput separation",
        "closed NPZ round trip"], elapsed_seconds=time.perf_counter()-started,
        cosmological_IVPs_executed=0, RHS_calls=0, old_suites_executed=0)
    dump(ROOT / "evidence/RUNNER_STATIC_CHECKS.json", receipt)
    print("RUNNER_PREFLIGHT: PASS; 8 configurations; 0 RHS calls; 0 cosmological IVPs; 0 old suites", flush=True)
    return receipt


def run_campaign():
    adapter = verify_pre_ode_receipt()
    preflight_path = ROOT / "evidence/RUNNER_STATIC_CHECKS.json"
    checked = json.loads(preflight_path.read_text())
    if checked.get("status") != "PASS" or checked.get("source_sha256") != source_hashes():
        raise RuntimeError("MATCHING_RUNNER_PREFLIGHT_REQUIRED: python code/run.py --preflight")
    existing = []
    for name in CASES:
        path = ROOT / "data" / name / "RESULT.json"
        if path.exists():
            receipt = json.loads(path.read_text())
            existing.append(receipt)
            if receipt.get("status") != "PASS":
                raise RuntimeError("PRESERVED_FAILED_CASE_REQUIRES_ROOT_DECISION:" + name)
    budget = Budget(sum(row["wall_seconds"] for row in existing))
    receipts, executed = [], 0
    try:
        for name in CASES:
            row, new = run_case(name, budget, adapter)
            receipts.append(row)
            executed += int(new)
        budget.check()
        compared = comparisons()
        success = all(row["status"] == "PASS" for row in compared.values())
        summary = dict(schema=SCHEMA, status="PASS" if success else "FAIL",
            case_ids=list(CASES), unique_completed_new_cohort_IVPs=len(receipts),
            new_IVPs_this_invocation=executed, cached_IVPs_this_invocation=len(receipts)-executed,
            old_campaign_IVPs_executed=0, comparisons=compared,
            case_receipts=[str(Path("data")/name/"RESULT.json") for name in CASES],
            sum_case_wall_seconds=sum(row["wall_seconds"] for row in receipts),
            cumulative_science_seconds=budget.elapsed, statuses=STATUS_FLAGS,
            scope="finite representative trajectory/refinement checks; global convergence NOT_RUN")
        dump(ROOT / "results/SCIENCE_SUMMARY.json", summary)
        print(f"THERM02_CAMPAIGN: {summary['status']}; completed={len(receipts)}; new_this_invocation={executed}", flush=True)
        return 0 if success else 1
    except Exception as error:
        dump(ROOT / "results/SCIENCE_SUMMARY.json", dict(schema=SCHEMA, status="STOPPED",
            error=str(error), traceback=traceback.format_exc(), case_ids=list(CASES),
            accepted_receipts_this_invocation=[row["id"] for row in receipts],
            completed_new_IVPs_this_invocation=executed, cumulative_science_seconds=budget.elapsed,
            old_campaign_IVPs_executed=0, statuses=STATUS_FLAGS,
            next="Diagnose preserved case and receipt before any further science execution."))
        raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--preflight", action="store_true")
    parser.add_argument("--run", action="store_true")
    parser.add_argument("--plot", action="store_true")
    args = parser.parse_args()
    if not any(vars(args).values()):
        parser.print_help()
        return 0
    if args.preflight:
        preflight()
    if args.run:
        code = run_campaign()
        if code:
            return code
    if args.plot:
        from plot import make_figures
        make_figures()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
