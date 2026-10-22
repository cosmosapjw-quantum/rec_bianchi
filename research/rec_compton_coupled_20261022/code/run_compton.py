"""Finite native-full63 Compton pilot; reuse prior solutions by identity.

The first end-to-end case and the remaining cohort share an append-only
execution allocation. Completed ODEs are never replayed for restoration.
Run from this unit:
  python3 code/run_compton.py --output results/compton8 --case s03_m03_r03_actual_hot_nominal
  python3 code/run_compton.py --output results/compton8 --all --resume
"""
from __future__ import annotations

import os
for _key in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ[_key] = "1"

import argparse
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import platform
import resource
import sys
import time
import traceback
import numpy as np
import scipy
from scipy.integrate import solve_ivp, simpson, cumulative_trapezoid

UNIT = Path(__file__).resolve().parents[1]
REPO = UNIT.parents[1]
THERMAL = UNIT.parent / "rec_thermal_moments_20261022"
OMITTED = UNIT.parent / "rec_thermal_omitted_budget_20261022"
DONOR = UNIT.parent / "rec_rei_hheli_sandbox_20261021"
for _p in (THERMAL / "code", OMITTED / "code"):
    if str(_p) not in sys.path:
        sys.path.append(str(_p))

from compton_system import ComptonFull63
from run_thermal import source_identity as thermal_source_identity
from postprocess_omitted import runtime_identity as omitted_source_identity

THERMAL_ID = "dfd2ca42b7fb768f3e31e5a7cc3ab64a4aa8b422ef0c5b79b8852043b197ff2e"
OMITTED_ID = "88edf8e7e5ccff94509e03ff2979b3b93e5e988641c5dbd4a5d64f4583bca02c"
SEEDS = ("s03_m03_r03", "s04_m04_r04")
BRANCHES = ("actual_hot", "planck_reference")
CASES = tuple((seed, branch, refined) for seed in SEEDS for branch in BRANCHES for refined in (False, True))
CASE_CAP_SECONDS = 240.0
CAMPAIGN_CAP_SECONDS = 1200.0
SIGNED_NAMES = ("Sigma_F", "P_matter", "P_radiation", "P_total", "P_photon", "P_neutrino")
INTEGRAND_NAMES = (
    "gas_source", "work", "gas_source_minus_work", "absolute_throughput",
    "compton_selected", "compton_uv", "compton_bath", "uv_bath", "escaped_radiation",
)
REQUIRED_OUTPUTS = frozenset((
    "accepted_solver_nodes.npz", "trajectory.npz", "accepted_diagnostics.npz",
    "dense_513.npz", "dense_1025.npz",
))
RETAINED_SETS = ("comparison_109", "accepted", "dense_513", "dense_1025")
ADMISSION_GATES = (
    "finite", "temperature_domain", "population_positivity", "isotope_conservation",
    "baryon_conservation", "zero_n_T", "ne_nonnegative", "monotone_tau",
    "number_monopoles", "einstein_constraint", "tensor_sum", "finite_angular_positivity",
    "trace_energy_small", "source_energy", "transfer_ledger",
)
REQUIRED_GATES = frozenset(
    [grid + ":" + gate for grid in RETAINED_SETS for gate in ADMISSION_GATES]
    + ["integrated_energy_1025", "initial_state_exact", "source_unchanged", "inputs_unchanged"]
)


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def json_scalar(value):
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, Path):
        return str(value)
    raise TypeError(type(value).__name__)


def save_json(path, value):
    """Create a complete file atomically; never replace existing evidence."""
    path = Path(path)
    temporary = path.with_name(path.name + f".{os.getpid()}.tmp")
    with temporary.open("xb") as stream:
        stream.write((json.dumps(value, indent=2, allow_nan=False, default=json_scalar) + "\n").encode())
        stream.flush()
        os.fsync(stream.fileno())
    os.link(temporary, path)
    temporary.unlink()


def save_npz(path, **arrays):
    path = Path(path)
    temporary = path.with_name(path.name + f".{os.getpid()}.tmp")
    with temporary.open("xb") as stream:
        np.savez_compressed(stream, **arrays)
        stream.flush()
        os.fsync(stream.fileno())
    os.link(temporary, path)
    temporary.unlink()


def label_for(seed, branch, refined):
    return seed + "_" + branch + ("_refined" if refined else "_nominal")


def source_identity():
    tid, tfiles = thermal_source_identity()
    oid, ofiles = omitted_source_identity()
    if tid != THERMAL_ID or oid != OMITTED_ID:
        raise ValueError("INHERITED_SOURCE_IDENTITY_CHANGED")
    files = {
        str((UNIT / "code" / name).relative_to(REPO)): digest(UNIT / "code" / name)
        for name in ("run_compton.py", "compton_system.py")
    }
    files[str((UNIT / "FROZEN_CONTRACT.md").relative_to(REPO))] = digest(UNIT / "FROZEN_CONTRACT.md")
    files.update({str((THERMAL / name).relative_to(REPO)): sha for name, sha in tfiles.items()})
    files.update({str((OMITTED / name).relative_to(REPO)): sha for name, sha in ofiles.items()})
    identity = hashlib.sha256(canonical(dict(files=files, thermal_identity=tid, omitted_identity=oid))).hexdigest()
    return identity, files


def load_inputs():
    """Read four immutable old baselines and the exact common initial states."""
    inputs = {}
    for seed in SEEDS:
        cases = {}
        for refined in (False, True):
            old_label = seed + "_mao2017_" + ("refined" if refined else "nominal")
            folder = THERMAL / "results/thermal8" / old_label
            receipt_path = folder / "RESULT.json"
            receipt = json.loads(receipt_path.read_text())
            path = folder / "trajectory.npz"
            sha = digest(path)
            if (receipt["status"] != "COMPLETE" or not all(receipt["gates"].values())
                    or receipt["source_identity"] != THERMAL_ID
                    or sha != receipt["trajectory_sha256"]
                    or path.stat().st_size != receipt["trajectory_bytes"]):
                raise ValueError("BASELINE_IDENTITY_CHANGED:" + old_label)
            with np.load(path, allow_pickle=False) as a:
                arrays = {key: a[key].copy() for key in a.files}
            if arrays["raw_state"].shape != (109, 63) or arrays["x"].shape != (109,):
                raise ValueError("BASELINE_SHAPE:" + old_label)
            if not np.array_equal(arrays["initial_state"], arrays["raw_state"][0]):
                raise ValueError("BASELINE_INITIAL_STATE:" + old_label)
            if int(arrays["source_index"]) != 84:
                raise ValueError("BASELINE_RESTART_INDEX:" + old_label)
            if hashlib.sha256(arrays["initial_state"].tobytes()).hexdigest() != receipt["initial_state_sha256"]:
                raise ValueError("BASELINE_INITIAL_HASH:" + old_label)
            cases[refined] = dict(
                arrays=arrays, receipt=receipt,
                identity=dict(label=old_label, path=str(path.relative_to(REPO)),
                              bytes=path.stat().st_size, sha256=sha,
                              receipt_path=str(receipt_path.relative_to(REPO)),
                              receipt_sha256=digest(receipt_path)),
            )
        a, b = cases[False]["arrays"], cases[True]["arrays"]
        for key in ("initial_state", "x", "isotope_scales", "initial_Y"):
            if not np.array_equal(a[key], b[key]):
                raise ValueError("NOMINAL_REFINED_INPUT_MISMATCH:" + seed + ":" + key)
        if np.any(a["initial_state"][[40, 45, 46]] != 0):
            raise ValueError("NATIVE_N_T_INITIAL_NONZERO:" + seed)
        donor = DONOR / "results/pilot_v2/cases" / seed
        dp, dr = donor / "trajectory.npz", donor / "RESULT.json"
        drec = json.loads(dr.read_text())
        if (digest(dp) != cases[False]["receipt"]["donor_sha256"]
                or digest(dr) != cases[False]["receipt"]["donor_receipt_sha256"]):
            raise ValueError("DONOR_IDENTITY_CHANGED:" + seed)
        with np.load(dp, allow_pickle=False) as old:
            if not np.array_equal(a["initial_state"][:62], old["raw_state"][84]):
                raise ValueError("EXACT_DONOR_RESTART_CHANGED:" + seed)
        inputs[seed] = dict(cases=cases, config=drec["config"],
                            donor=dict(path=str(dp.relative_to(REPO)), sha256=digest(dp),
                                       receipt_path=str(dr.relative_to(REPO)), receipt_sha256=digest(dr)))
    return inputs


def input_manifest(inputs):
    return {seed: dict(config=row["config"], donor=row["donor"],
                       baselines=[row["cases"][r]["identity"] for r in (False, True)])
            for seed, row in inputs.items()}


def environment():
    return dict(python=sys.version.split()[0], numpy=np.__version__, scipy=scipy.__version__,
                platform=platform.platform(), numerical_threads=1)


def require_preflight(identity):
    path = UNIT / "evidence/PREFLIGHT_ADMISSION.json"
    receipt = json.loads(path.read_text())
    if receipt.get("status") != "ADMITTED_FOR_FINITE_PILOT" or receipt.get("runtime_identity") != identity:
        raise ValueError("PREFLIGHT_NOT_ADMITTED_FOR_CURRENT_SOURCE")
    for row in receipt["evidence_files"]:
        evidence_path = UNIT / row["path"]
        if digest(evidence_path) != row["sha256"]:
            raise ValueError("PREFLIGHT_EVIDENCE_CHANGED:" + row["path"])
    if not receipt["evidence_files"]:
        raise ValueError("PREFLIGHT_EVIDENCE_EMPTY")
    return dict(path=str(path.relative_to(UNIT)), sha256=digest(path))


def numerical_spec(refined):
    factor = 0.1 if refined else 1.0
    return dict(method="BDF", rtol=2e-8 * factor,
                atol=(factor * np.r_[np.full(40, 2e-11), np.full(21, 2e-10), 2e-11, 2e-10]).tolist(),
                max_step=0.0125 if refined else 0.025, dense_output=True,
                comparison_nodes=109, dense_nodes=[513, 1025], retain_accepted_nodes=True)


def gather_set(model, xs, raw, initial_Y, check_deadline):
    """Admission at explicitly retained physical samples, not Newton trials."""
    xs = np.asarray(xs, dtype=float)
    raw = np.asarray(raw, dtype=float)
    if raw.shape != (len(xs), 63) or not np.all(np.isfinite(raw)) or np.any(np.diff(xs) <= 0):
        raise ValueError("RETAINED_STATE_SHAPE_OR_FINITE")
    if np.any(raw[:, [40, 45, 46]] != 0):
        raise ValueError("RETAINED_NATIVE_N_T_NONZERO")
    rows, inherited, signed, constraints = [], [], [], []
    for xx, yy in zip(xs, raw):
        check_deadline()
        d = model.sample(float(xx), yy)
        rows.append(d)
        inherited.append(model.diagnostics(float(xx), yy))
        f = model.geometry.fields(float(xx), yy[:40])
        signed.append(model.geometry.normalized(float(xx), yy[:40], f))
        lhs = 3 * f["H"] ** 2
        rhs = (3 * model.geometry.source.h0 ** 2 *
               (f["dust_energy_norm"] + f["massive_energy_norm"] + f["rad_energy_norm"] +
                model.geometry.source.omega_lambda) + 3 * f["s"] ** 2)
        constraints.append(abs(lhs - rhs) / lhs)
    names = tuple(rows[0])
    inames = tuple(k for k in inherited[0] if k != "signed_observables")
    if any(tuple(r) != names for r in rows):
        raise ValueError("DIAGNOSTIC_SCHEMA_CHANGED")
    diag = np.array([[r[n] for n in names] for r in rows], dtype=float)
    idiag = np.array([[r[n] for n in inames] for r in inherited], dtype=float)
    signed = np.array(signed)
    Y = raw[:, 40:61] * model.scale
    T = np.exp(raw[:, 62])
    d = {name: diag[:, i] for i, name in enumerate(names)}
    ii = {name: idiag[:, i] for i, name in enumerate(inames)}
    isotope_errors = {
        name: float(np.max(np.abs(Y[:, indices].sum(axis=1) - initial_Y[list(indices)].sum()))
                    / model.scale[indices[0]])
        for name, indices in model.atomic.isotope_groups.items()
    }
    angular_min = min(float(np.min(ii[n])) for n in (
        "min_photon_angular_weight", "min_neutrino_angular_weight",
        "min_photon_number_angular_weight", "min_neutrino_number_angular_weight"))
    metrics = dict(
        samples=len(xs), isotope_errors=isotope_errors,
        max_baryon_error=float(np.max(np.abs(Y @ model.atomic.A - 1))),
        min_scaled_population=float(np.min(raw[:, 40:61])),
        min_ne_m3=float(d["ne_m3"].min()), min_T_K=float(T.min()), max_T_K=float(T.max()),
        min_tau_increment=float(np.min(np.diff(raw[:, 61]))),
        max_number_monopole_error=float(max(np.max(abs(raw[:, 13] - 1)), np.max(abs(raw[:, 31] - 1)))),
        max_einstein_constraint=float(max(constraints)),
        max_tensor_sum_residual=float(np.max(abs(signed[:, 3] - signed[:, 1] - signed[:, 2]))),
        min_finite_angular_weight=angular_min,
        max_trace_energy_fraction=float(ii["trace_energy_fraction"].max()),
        max_source_energy_residual=float(np.max(abs(d["source_energy_residual"]))),
        max_transfer_ledger_residual=float(np.max(abs(d["transfer_ledger_residual_scaled"]))),
    )
    gates = dict(
        finite=bool(np.isfinite(diag).all() and np.isfinite(idiag).all() and np.isfinite(signed).all()),
        temperature_domain=bool(np.all((T >= 100) & (T <= 1e6))),
        population_positivity=metrics["min_scaled_population"] >= -2e-8,
        isotope_conservation=max(isotope_errors.values()) < 2e-7,
        baryon_conservation=metrics["max_baryon_error"] < 2e-8,
        zero_n_T=bool(np.all(Y[:, [0, 5, 6]] == 0)),
        ne_nonnegative=metrics["min_ne_m3"] >= 0,
        monotone_tau=metrics["min_tau_increment"] >= -2e-10,
        number_monopoles=metrics["max_number_monopole_error"] < 2e-9,
        einstein_constraint=metrics["max_einstein_constraint"] < 2e-13,
        tensor_sum=metrics["max_tensor_sum_residual"] < 2e-16,
        finite_angular_positivity=angular_min > -2e-7,
        trace_energy_small=metrics["max_trace_energy_fraction"] < 1e-5,
        source_energy=metrics["max_source_energy_residual"] < 5e-12,
        transfer_ledger=metrics["max_transfer_ledger_residual"] < 5e-12,
    )
    nbH = d["nb_m3"] * d["H_s"]
    source = d["gas_energy_source_J_per_baryon_per_x"]
    work = d["work_J_per_baryon_per_x"]
    throughput = (abs(d["photo_absorbed_W_m3"]) + abs(d["total_escape_W_m3"]) +
                  abs(d["compton_selected_W_m3"]) + abs(d["compton_uv_W_m3"])) / nbH + abs(work)
    integrands = np.column_stack((
        source, work, source - work, throughput,
        d["compton_selected_W_m3"] / nbH, d["compton_uv_W_m3"] / nbH,
        d["compton_bath_source_W_m3"] / nbH, d["uv_bath_source_W_m3"] / nbH,
        d["escaped_radiation_source_W_m3"] / nbH,
    ))
    arrays = dict(x=xs, z=21 * np.exp(-xs) - 1, raw_state=raw, Y=Y, T_K=T,
                  diagnostics=diag, diagnostic_names=np.array(names),
                  inherited_diagnostics=idiag, inherited_diagnostic_names=np.array(inames),
                  signed_observables=signed, signed_observable_names=np.array(SIGNED_NAMES),
                  isotope_scales=model.scale, initial_Y=initial_Y,
                  integrand_names=np.array(INTEGRAND_NAMES),
                  integrands_J_per_baryon_per_x=integrands,
                  cumulative_trapezoid_J_per_baryon=cumulative_trapezoid(integrands, x=xs, axis=0, initial=0),
                  einstein_constraint=np.array(constraints))
    integrals = simpson(integrands, x=xs, axis=0)
    delta = float(d["gas_energy_J_per_baryon"][-1] - d["gas_energy_J_per_baryon"][0])
    energy = dict(delta_energy_J_per_baryon=delta,
                  integrated_net_J_per_baryon=float(integrals[2]),
                  throughput_J_per_baryon=float(integrals[3]),
                  residual_scaled=abs(delta - integrals[2]) / max(float(integrals[3]), 1e-300),
                  simpson_integrals_J_per_baryon=dict(zip(INTEGRAND_NAMES, integrals.tolist())),
                  backreaction_ratio_integral=float(simpson(d["compton_backreaction_ratio"], x=xs)),
                  max_backreaction_ratio=float(d["compton_backreaction_ratio"].max()),
                  cumulative_rule="trapezoid; endpoint energy audit uses Simpson on the same retained arrays")
    return arrays, metrics, gates, energy


def verify_outputs(folder, receipt):
    if (receipt.get("status") != "COMPLETE"
            or not isinstance(receipt.get("source_identity"), str)
            or not receipt["source_identity"]):
        raise ValueError("OUTPUT_RECEIPT_NOT_COMPLETE_OR_IDENTIFIED")
    if set(receipt.get("outputs", {})) != REQUIRED_OUTPUTS:
        raise ValueError("OUTPUT_INVENTORY_INCOMPLETE_OR_CHANGED")
    gates = receipt.get("gates", {})
    if set(gates) != REQUIRED_GATES or not all(value is True for value in gates.values()):
        raise ValueError("OUTPUT_ADMISSION_INCOMPLETE_OR_FAILED")
    for name, row in receipt["outputs"].items():
        path = folder / name
        if path.stat().st_size != row["bytes"] or digest(path) != row["sha256"]:
            raise ValueError("OUTPUT_IDENTITY_CHANGED:" + str(path))


def one_case(spec, inputs, output, identity, source_files, campaign_deadline):
    seed, branch, refined = spec
    label = label_for(*spec)
    config = inputs[seed]["config"]
    old = inputs[seed]["cases"][False]["arrays"]
    y0 = old["initial_state"].copy()
    numeric = numerical_spec(refined)
    spec_record = dict(seed=seed, branch=branch, refined=refined, rr_closure="mao2017",
                       config=config, numeric=numeric, input=input_manifest({seed: inputs[seed]})[seed],
                       initial_state_sha256=hashlib.sha256(y0.tobytes()).hexdigest(),
                       source_identity=identity)
    case_identity = hashlib.sha256(canonical(spec_record)).hexdigest()
    dest = output / label
    if (dest / "RESULT.json").exists():
        result = json.loads((dest / "RESULT.json").read_text())
        if (result["status"] != "COMPLETE" or result["case_identity"] != case_identity
                or result["source_identity"] != identity or not all(result["gates"].values())):
            raise ValueError("EXISTING_RESULT_IDENTITY_MISMATCH:" + label)
        verify_outputs(dest, result)
        return dict(label=label, execution="complete_reused", result=result)
    if dest.exists():
        raise FileExistsError("PRESERVE_PARTIAL_CASE:" + str(dest))
    dest.mkdir()
    start, cpu = time.perf_counter(), time.process_time()
    deadline = min(start + CASE_CAP_SECONDS, campaign_deadline)
    model = None
    last_trial = {}
    base = dict(label=label, case_identity=case_identity, source_identity=identity,
                source_files=source_files, specification=spec_record,
                started_utc=datetime.now(timezone.utc).isoformat(),
                old_IVP_reruns=0, elapsed_clock="proper Myr since donor z20, not cosmic age or restart time",
                physical_scope="test-fluid gas Compton pilot; opposite bath sources recorded, not applied to radiation/Einstein",
                physical_status="HOLD", production="NOT_APPROVED", global_convergence="NOT_RUN", REI_activation=False)

    def check_deadline():
        if time.perf_counter() > deadline:
            raise TimeoutError("FINITE_CASE_OR_CAMPAIGN_WALL_EXHAUSTED")

    save_json(dest / "STARTED.json", base)
    try:
        check_deadline()
        model = ComptonFull63(dict(config, _case_wall_seconds=max(0.001, deadline - time.perf_counter())),
                              branch=branch)
        if not np.array_equal(model.scale, old["isotope_scales"]):
            raise ValueError("SPECIES_SCALE_CHANGED")
        x = old["x"]
        if x[-1] != math.log(7) or len(x) != 109:
            raise ValueError("FROZEN_COMPARISON_GRID_CHANGED")

        def rhs(xx, yy):
            check_deadline()
            last_trial.update(x=float(xx), y=yy.copy())
            return model.rhs(xx, yy)

        def jac(xx, yy):
            check_deadline()
            return model.jac(xx, yy)

        integration_started = time.perf_counter()
        sol = solve_ivp(rhs, (float(x[0]), float(x[-1])), y0, method="BDF", jac=jac,
                        rtol=numeric["rtol"], atol=np.array(numeric["atol"]),
                        max_step=numeric["max_step"], dense_output=True)
        integration_wall_seconds = time.perf_counter() - integration_started
        # Accepted nodes are preserved before any diagnostic can fail.
        save_npz(dest / "accepted_solver_nodes.npz", x=sol.t, raw_state=sol.y.T,
                 initial_state=y0, state_role=np.array("accepted_BDF_nodes"))
        if not sol.success or sol.y.shape[0] != 63 or sol.t[-1] != x[-1]:
            raise RuntimeError("COMPTON_INTEGRATION_FAILED:" + sol.message)
        xs1025 = np.linspace(x[0], x[-1], 1025)
        sets = (
            ("comparison_109", x, sol.sol(x).T, "trajectory.npz"),
            ("accepted", sol.t, sol.y.T, "accepted_diagnostics.npz"),
            ("dense_513", xs1025[::2], sol.sol(xs1025[::2]).T, "dense_513.npz"),
            ("dense_1025", xs1025, sol.sol(xs1025).T, "dense_1025.npz"),
        )
        admission, energies, all_gates = {}, {}, {}
        endpoint = None
        output_names = ["accepted_solver_nodes.npz"]
        for set_name, sx, sy, filename in sets:
            arrays, metrics, gates, energy = gather_set(model, sx, sy, old["initial_Y"], check_deadline)
            arrays.update(initial_state=y0, source_index=np.array(84), compton_branch=np.array(branch))
            save_npz(dest / filename, **arrays)
            output_names.append(filename)
            admission[set_name] = dict(metrics=metrics, gates=gates)
            energies[set_name] = energy
            all_gates.update({set_name + ":" + name: bool(value) for name, value in gates.items()})
            if set_name == "comparison_109":
                endpoint = dict(temperature_end_K=float(arrays["T_K"][-1]),
                                temperature_peak_109_K=float(arrays["T_K"].max()),
                                tau_end=float(sy[-1, 61]), signed_endpoint=arrays["signed_observables"][-1])
        all_gates["integrated_energy_1025"] = energies["dense_1025"]["residual_scaled"] < 3e-4
        all_gates["initial_state_exact"] = bool(np.array_equal(sol.y[:, 0], y0))
        all_gates["source_unchanged"] = source_identity()[0] == identity
        all_gates["inputs_unchanged"] = input_manifest(load_inputs()) == input_manifest(inputs)
        check_deadline()
        outputs = {name: dict(bytes=(dest / name).stat().st_size, sha256=digest(dest / name))
                   for name in output_names}
        check_deadline()
        result = dict(base, status="COMPLETE" if all(all_gates.values()) else "GATE_FAIL",
                      gates=all_gates, outputs=outputs, admission=admission, energy_integrals=energies,
                      energy_grid_delta_scaled=abs(energies["dense_1025"]["integrated_net_J_per_baryon"] -
                                                   energies["dense_513"]["integrated_net_J_per_baryon"]) /
                                                energies["dense_1025"]["throughput_J_per_baryon"],
                      **endpoint, accepted_nodes=len(sol.t), samples=109, dense_samples=[513, 1025],
                      nfev=sol.nfev, njev=sol.njev, nlu=sol.nlu, rhs_calls=model.nrhs, jac_calls=model.njac,
                      solver_message=sol.message, integration_wall_seconds=integration_wall_seconds,
                      diagnostics_and_persistence_wall_seconds=time.perf_counter() - integration_started - integration_wall_seconds,
                      wall_seconds=time.perf_counter() - start,
                      own_cpu_seconds=time.process_time() - cpu,
                      process_peak_RSS_KiB=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                      environment=environment(),
                      admission_scope="comparison109, all saved accepted BDF nodes, dense513 and dense1025; no claim about internal Newton trials or the continuum")
        save_json(dest / "RESULT.json", result)
        if not all(all_gates.values()):
            raise RuntimeError("FINITE_GATE_FAILED:" + ",".join(k for k, v in all_gates.items() if not v))
        return dict(label=label, execution="new_complete", result=result)
    except Exception as exc:
        if last_trial:
            save_npz(dest / "last_rhs_trial_not_accepted.npz", x=np.array(last_trial["x"]),
                     raw_state=last_trial["y"], state_role=np.array("last_RHS_trial_not_certified_accepted"))
        save_json(dest / "FAILED.json", dict(
            base, status="FAILED", error=repr(exc), traceback=traceback.format_exc(),
            wall_seconds=time.perf_counter() - start, own_cpu_seconds=time.process_time() - cpu,
            rhs_calls=getattr(model, "nrhs", None), jac_calls=getattr(model, "njac", None),
            preserved_files=sorted(p.name for p in dest.iterdir() if p.is_file())))
        raise


def refinement_pairs(output, identity):
    comparisons = {}
    for seed in SEEDS:
        for branch in BRANCHES:
            paths = [output / label_for(seed, branch, r) for r in (False, True)]
            recs = [json.loads((p / "RESULT.json").read_text()) for p in paths]
            for p, rec in zip(paths, recs):
                if rec["status"] != "COMPLETE" or rec["source_identity"] != identity:
                    raise ValueError("REFINEMENT_INPUT_NOT_COMPLETE:" + str(p))
                verify_outputs(p, rec)
            with np.load(paths[0] / "trajectory.npz", allow_pickle=False) as a, np.load(paths[1] / "trajectory.npz", allow_pickle=False) as b:
                if not np.array_equal(a["x"], b["x"]) or not np.array_equal(a["isotope_scales"], b["isotope_scales"]):
                    raise ValueError("REFINEMENT_GRID_OR_SCALES_CHANGED")
                if (not np.array_equal(a["initial_state"], b["initial_state"])
                        or not np.array_equal(a["initial_state"], a["raw_state"][0])
                        or not np.array_equal(b["initial_state"], b["raw_state"][0])):
                    raise ValueError("REFINEMENT_INITIAL_STATE_CHANGED")
                raw_delta = b["raw_state"] - a["raw_state"]
                signed_delta = b["signed_observables"] - a["signed_observables"]
                metrics = dict(max_abs_delta_lnT=float(abs(raw_delta[:, 62]).max()),
                               max_abs_delta_conditional_ion_fraction=float(abs(raw_delta[:, 40:61]).max()),
                               max_abs_delta_tau=float(abs(raw_delta[:, 61]).max()),
                               max_abs_delta_signed_six=float(abs(signed_delta).max()),
                               max_abs_delta_signed_stress_only=float(abs(signed_delta[:, 1:]).max()),
                               max_abs_delta_signed_shear=float(abs(signed_delta[:, 0]).max()))
                gates = dict(lnT=metrics["max_abs_delta_lnT"] < 3e-5,
                             ionic_fractions=metrics["max_abs_delta_conditional_ion_fraction"] < 3e-5,
                             tau=metrics["max_abs_delta_tau"] < 3e-7,
                             signed_six=metrics["max_abs_delta_signed_six"] < 3e-7)
                comparisons[seed + "_" + branch] = dict(
                    metrics=metrics, gates=gates,
                    input_receipt_sha256=[digest(p / "RESULT.json") for p in paths],
                    input_trajectory_sha256=[recs[i]["outputs"]["trajectory.npz"]["sha256"] for i in range(2)])
    return dict(source_identity=identity, status="PASS" if all(all(r["gates"].values()) for r in comparisons.values()) else "FAIL",
                pairs=comparisons, scope="same-branch finite numerical evidence; no global error bound")


def execution_spent(output):
    spent = 0.0
    for directory in sorted((output / "execution").glob("attempt_*")):
        begin = json.loads((directory / "STARTED.json").read_text())
        complete = directory / "FINISHED.json"
        if complete.exists():
            spent += float(json.loads(complete.read_text())["wall_seconds"])
        else:
            # An interrupted attempt cannot reset its allocation by resuming.
            spent += max(0.0, time.time() - float(begin["started_epoch"]))
    return spent


def run(output, selected, resume):
    start, cpu = time.perf_counter(), time.process_time()
    identity, files = source_identity()
    preflight = require_preflight(identity)
    inputs = load_inputs()
    frozen = dict(schema="rec.compton.full63.campaign.v1", source_identity=identity,
                  source_files=files, preflight=preflight, inputs=input_manifest(inputs),
                  cases=[label_for(*s) for s in CASES],
                  case_wall_cap_seconds=CASE_CAP_SECONDS, campaign_wall_cap_seconds=CAMPAIGN_CAP_SECONDS,
                  allocation="sum of active invocation wall time including diagnostics; unfinished interrupted invocations charged elapsed wall time until resolution",
                  old_IVP_reruns=0, environment=environment())
    output = Path(output).resolve()
    if output != (UNIT / "results/compton8").resolve():
        raise ValueError("FROZEN_CAMPAIGN_OUTPUT_REQUIRED: results/compton8")
    if output.exists():
        if not resume:
            raise FileExistsError("USE_EXPLICIT_RESUME_FOR_EXISTING_CAMPAIGN")
        if json.loads((output / "CAMPAIGN_LOCK.json").read_text()) != frozen:
            raise ValueError("CAMPAIGN_IDENTITY_CHANGED")
    else:
        if resume:
            raise FileNotFoundError("RESUME_REQUIRES_EXISTING_CAMPAIGN")
        output.mkdir()
        (output / "execution").mkdir()
        save_json(output / "CAMPAIGN_LOCK.json", frozen)
    spent = execution_spent(output)
    if spent >= CAMPAIGN_CAP_SECONDS:
        raise TimeoutError("CAMPAIGN_ALLOCATION_EXHAUSTED")
    attempt = output / "execution" / ("attempt_" + str(len(list((output / "execution").glob("attempt_*"))) + 1).zfill(3))
    attempt.mkdir()
    save_json(attempt / "STARTED.json", dict(started_epoch=time.time(), started_utc=datetime.now(timezone.utc).isoformat(),
                                            pid=os.getpid(), command=sys.argv, source_identity=identity,
                                            previously_charged_wall_seconds=spent,
                                            remaining_allocation_seconds=CAMPAIGN_CAP_SECONDS - spent))
    deadline = start + CAMPAIGN_CAP_SECONDS - spent
    outcomes = []
    status, error = "FAILED", None
    try:
        specs = CASES if selected == "all" else tuple(s for s in CASES if label_for(*s) == selected)
        if not specs:
            raise ValueError("UNKNOWN_FROZEN_CASE:" + selected)
        for spec in specs:
            if time.perf_counter() >= deadline:
                raise TimeoutError("CAMPAIGN_ALLOCATION_EXHAUSTED")
            row = one_case(spec, inputs, output, identity, files, deadline)
            outcomes.append(row)
            print(json.dumps({k: row["result"][k] for k in ("label", "status", "temperature_end_K", "wall_seconds")} |
                             {"execution": row["execution"]}), flush=True)
        if selected == "all":
            refinement = refinement_pairs(output, identity)
            rp = output / "REFINEMENT.json"
            if rp.exists():
                if json.loads(rp.read_text()) != refinement:
                    raise ValueError("EXISTING_REFINEMENT_CHANGED")
            else:
                save_json(rp, refinement)
            if refinement["status"] != "PASS":
                raise RuntimeError("FINITE_REFINEMENT_GATE_FAILED")
        if time.perf_counter() >= deadline:
            raise TimeoutError("CAMPAIGN_ALLOCATION_EXHAUSTED_AFTER_DIAGNOSTICS")
        status = "COMPLETE"
        return dict(status=status, source_identity=identity,
                    new_integrations=sum(r["execution"] == "new_complete" for r in outcomes),
                    reused=sum(r["execution"] == "complete_reused" for r in outcomes),
                    old_IVP_reruns=0, results=[dict(label=r["label"], execution=r["execution"]) for r in outcomes])
    except Exception as exc:
        error = dict(error=repr(exc), traceback=traceback.format_exc())
        raise
    finally:
        receipt = dict(status=status, source_identity=identity, command=sys.argv,
                       wall_seconds=time.perf_counter() - start, own_cpu_seconds=time.process_time() - cpu,
                       previously_charged_wall_seconds=spent, results=[dict(label=r["label"], execution=r["execution"]) for r in outcomes],
                       new_integrations_completed=sum(r["execution"] == "new_complete" for r in outcomes),
                       reused=sum(r["execution"] == "complete_reused" for r in outcomes),
                       old_IVP_reruns=0, error=error)
        save_json(attempt / "FINISHED.json", receipt)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    choice = parser.add_mutually_exclusive_group()
    choice.add_argument("--case", choices=[label_for(*s) for s in CASES])
    choice.add_argument("--all", action="store_true")
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--output", type=Path, default=UNIT / "results/compton8")
    args = parser.parse_args()
    if not args.case and not args.all:
        print(json.dumps(dict(status="PLAN_ONLY", cases=[label_for(*s) for s in CASES],
                              new_IVPs_planned=8, old_IVP_reruns=0), indent=2))
    else:
        print(json.dumps(run(args.output, "all" if args.all else args.case, args.resume), indent=2))

