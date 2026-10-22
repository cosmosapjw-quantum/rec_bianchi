"""C2 baseline instrumentation on immutable saved states; no candidate or IVP.

From the repository root:
  python research/rec_saved_diagnostic_reuse_20261023/code/profile_saved_diagnostics.py

All output is create-only. cProfile timings locate cost; three unprofiled
repetitions report baseline latency. No optimization speedup is inferred.
"""
from __future__ import annotations

import os
for _name in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ[_name] = "1"
os.environ["PYTHONDONTWRITEBYTECODE"] = "1"

import time
PROCESS_START = time.perf_counter()
CPU_START = time.process_time()
import argparse
from contextlib import contextmanager
import cProfile
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import pstats
import resource
import signal
import sys
import traceback

sys.dont_write_bytecode = True
import numpy as np
import scipy
import scipy.integrate as integrate

UNIT = Path(__file__).resolve().parents[1]
REPO = UNIT.parents[1]
PARENT = UNIT.parent / "rec_compton_coupled_20261022"
RUNTIME_ID = "c89f576e2c7f15a0a1d0d3f96ce72de516245cbb83b5d4fbaeede342a76e86ac"
CONTRACT_SHA = "02d7b778142ea35402110f042373cae7e4e2b5987039a0b3d32cc93318dafded"
LIMIT_SECONDS = 600.0
POINTS_PER_CASE = 64
REPEATS = 3
ODE_ATTEMPTS = []


def forbidden_ivp(*args, **kwargs):
    ODE_ATTEMPTS.append("forbidden IVP entry attempted")
    raise RuntimeError("C2_ZERO_IVP_GUARD")


# Patch before importing drivers, so their from-import aliases inherit the guard.
for _name in ("solve_ivp", "odeint", "ode", "complex_ode", "BDF", "Radau", "RK45", "RK23", "DOP853", "LSODA"):
    if hasattr(integrate, _name):
        setattr(integrate, _name, forbidden_ivp)
sys.path.insert(0, str(PARENT / "code"))
import run_compton as runner
import analyze_collisions as collision_analysis
from compton_system import ComptonFull63
from collisional_budget import CollisionalBudget


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def save_json(path, obj):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x") as stream:
        json.dump(obj, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write("\n")


def save_npz(path, arrays):
    with Path(path).open("xb") as stream:
        np.savez_compressed(stream, **arrays)


def relative(path):
    path = Path(path)
    try:
        return str(path.resolve().relative_to(REPO))
    except ValueError:
        return str(path)


def binding(path):
    path = Path(path)
    return dict(path=relative(path), bytes=path.stat().st_size, sha256=digest(path))


def load_npz(path):
    with np.load(path, allow_pickle=False) as data:
        return {name: data[name].copy() for name in data.files}


def deadline():
    if time.perf_counter() - PROCESS_START > LIMIT_SECONDS:
        raise TimeoutError("C2_TOTAL_ACTIVE_WALL_CAP")


@contextmanager
def bounded_phase():
    deadline()
    remaining = LIMIT_SECONDS - (time.perf_counter() - PROCESS_START)
    def alarm(signum, frame):
        raise TimeoutError("C2_PHASE_OR_TOTAL_WALL_CAP")
    old = signal.signal(signal.SIGALRM, alarm)
    signal.setitimer(signal.ITIMER_REAL, min(60.0, remaining))
    try:
        yield
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, old)
    deadline()


def measured(function):
    wall, cpu = time.perf_counter(), time.process_time()
    with bounded_phase():
        value = function()
    return value, dict(wall_seconds=time.perf_counter()-wall, cpu_seconds=time.process_time()-cpu)


def profile(function):
    profiler = cProfile.Profile()
    value, timing = measured(lambda: profiler.runcall(function))
    stats = pstats.Stats(profiler)
    rows, edges = [], []
    def key(fn):
        return dict(file=relative(fn[0]) if fn[0] != "~" else "<builtin>", line=fn[1], name=fn[2])
    for fn, (primitive, calls, exclusive, inclusive, callers) in stats.stats.items():
        rows.append(dict(**key(fn), primitive_calls=primitive, total_calls=calls,
                         self_seconds=exclusive, cumulative_seconds=inclusive))
        # Retain all caller relationships; inclusive times overlap by design.
        for caller, counts in callers.items():
            edges.append(dict(caller=key(caller), callee=key(fn), raw_counts=list(counts)))
    rows.sort(key=lambda row: (-row["self_seconds"], row["file"], row["line"]))
    return value, dict(**timing, profiler_total_self_seconds=stats.total_tt,
                       total_calls=stats.total_calls, primitive_calls=stats.prim_calls,
                       functions=rows, caller_edges=edges)


def exact_comparison(actual, expected, names):
    rows = {}
    for name in names:
        a, b = actual[name], expected[name]
        equal = a.shape == b.shape and a.dtype == b.dtype and np.array_equal(a, b)
        record = dict(shape=list(a.shape), dtype=str(a.dtype), exact_equal=bool(equal))
        if a.dtype.kind in "fciub" and a.shape == b.shape:
            difference = np.abs(a.astype(float)-b.astype(float))
            record["max_abs_difference"] = float(difference.max(initial=0))
            record["different_entries"] = int(np.count_nonzero(a != b))
        rows[name] = record
    return dict(pass_exact=all(row["exact_equal"] for row in rows.values()), fields=rows)


def choose_indices(a, collisions):
    n = len(a["x"])
    reasons = {}
    def add(i, reason):
        reasons.setdefault(int(i), []).append(reason)
    add(0, "left_endpoint")
    add(n-1, "right_endpoint")
    add(int(np.argmax(a["T_K"])), "temperature_peak")
    d = {str(name): a["diagnostics"][:, k] for k, name in enumerate(a["diagnostic_names"])}
    for name in ("source_energy_residual", "photo_rr_dr_source_energy_residual",
                 "transfer_ledger_residual_scaled", "compton_backreaction_ratio"):
        add(int(np.argmax(abs(d[name]))), "max_abs:"+name)
    support = collisions["in_published_accuracy_domain"]
    names = collisions["coefficient_names"]
    for k, name in enumerate(names):
        for i in np.flatnonzero(support[1:, k] != support[:-1, k]):
            add(i, "fit_boundary_left:"+str(name))
            add(i+1, "fit_boundary_right:"+str(name))
    # Include both sides of any saved coefficient/power underflow boundary.
    for key in ("coefficient_underflow_to_zero", "ci_channel_power_underflow_to_zero", "ce_channel_power_underflow_to_zero"):
        flags = collisions[key]
        for i in np.flatnonzero(np.any(flags[1:] != flags[:-1], axis=1)):
            add(i, "underflow_boundary_left:"+key)
            add(i+1, "underflow_boundary_right:"+key)
    if len(reasons) > POINTS_PER_CASE:
        raise ValueError("MANDATORY_CORPUS_EXCEEDS_CAP")
    mandatory = sorted(reasons)
    # Greedy maximum distance in saved index (the input x grid is uniform).
    # np.argmax supplies a deterministic smallest-index tie break.
    while len(reasons) < POINTS_PER_CASE:
        points = np.arange(n)
        distances = np.min(abs(points[:, None]-np.array(sorted(reasons))[None, :]), axis=1)
        add(int(np.argmax(distances)), "uniform_maximin_fill")
    indices = np.array(sorted(reasons), dtype=np.int64)
    return indices, dict(mandatory_indices=mandatory, selected_indices=indices.tolist(),
                        reasons={str(i): reasons[i] for i in indices},
                        rule="endpoints/peak/residual maxima/fit and underflow boundaries, then deterministic maximum-distance index fill",
                        exact_state_sha256=hashlib.sha256(a["raw_state"][indices].tobytes()).hexdigest(),
                        x_sha256=hashlib.sha256(a["x"][indices].tobytes()).hexdigest())


def subset(a, indices):
    n = len(a["x"])
    return {name: (value[indices].copy() if value.ndim and value.shape[0] == n else value.copy())
            for name, value in a.items()}


GATHER_POINT_FIELDS = (
    "x", "z", "raw_state", "Y", "T_K", "diagnostics", "diagnostic_names",
    "inherited_diagnostics", "inherited_diagnostic_names", "signed_observables",
    "signed_observable_names", "isotope_scales", "initial_Y", "integrand_names",
    "integrands_J_per_baryon_per_x", "einstein_constraint",
)


def main(output):
    output = output.resolve()
    # Account for all prior attempts, including failed attempts, before another run.
    previous = []
    if output.parent.exists():
        for sibling in sorted(output.parent.glob("attempt_*")):
            if not sibling.is_dir():
                continue
            receipt = sibling / "FINISHED.json"
            if not receipt.exists():
                raise RuntimeError("UNRESOLVED_PRIOR_ATTEMPT:"+str(sibling))
            previous.append(json.loads(receipt.read_text()))
    spent = sum(row["active_wall_seconds"] for row in previous)
    global LIMIT_SECONDS
    LIMIT_SECONDS -= spent
    if LIMIT_SECONDS <= 0:
        raise RuntimeError("C2_PRIOR_ATTEMPTS_EXHAUSTED_BUDGET")
    output.mkdir(parents=True, exist_ok=False)
    save_json(output / "STARTED.json", dict(
        started_utc=datetime.now(timezone.utc).isoformat(), command=sys.argv,
        script=binding(__file__), scope=binding(UNIT/"C2_SCOPE.md"),
        selected_stage="C2", candidate_implementation=False, prior_active_wall_seconds=spent,
        remaining_wall_cap_seconds=LIMIT_SECONDS, phase_cap_seconds=60,
        max_states_per_case=POINTS_PER_CASE, unprofiled_repetitions=REPEATS,
        expected_equality="bitwise numerical array equality with identical saved raw states; cumulative/grid summaries are recomputed on the subset and are not compared to the full grid",
        numerical_threads=1, numerical_workers=1,
        environment=dict(python=sys.version, numpy=np.__version__, scipy=scipy.__version__, platform=platform.platform())))
    try:
        def inventory():
            if digest(PARENT/"NEXT_UNIT_CONTRACT.md") != CONTRACT_SHA:
                raise ValueError("PARENT_CONTRACT_CHANGED")
            runtime_id, runtime_files = runner.source_identity()
            if runtime_id != RUNTIME_ID:
                raise ValueError("PARENT_RUNTIME_CHANGED")
            collision_id, collision_files = collision_analysis._source_identity(runtime_id)
            inputs, records = {}, []
            for spec in runner.CASES:
                label = runner.label_for(*spec)
                folder = PARENT/"results/compton8"/label
                receipt_path = folder/"RESULT.json"
                rec = json.loads(receipt_path.read_text())
                if (rec["status"] != "COMPLETE" or rec["source_identity"] != runtime_id
                        or rec["source_files"] != runtime_files or not all(rec["gates"].values())
                        or rec["case_identity"] != hashlib.sha256(runner.canonical(rec["specification"])).hexdigest()):
                    raise ValueError("CASE_RECEIPT_CHANGED:"+label)
                runner.verify_outputs(folder, rec)
                for filename, expected in sorted(rec["outputs"].items()):
                    path = folder/filename
                    with np.load(path, allow_pickle=False) as data:
                        x, raw = data["x"], data["raw_state"]
                        if raw.shape != (len(x), 63) or not np.isfinite(raw).all() or np.any(np.diff(x) <= 0):
                            raise ValueError("SAVED_SHAPE:"+label+":"+filename)
                        shape = list(raw.shape)
                    records.append(dict(path=relative(path), **expected, raw_state_shape=shape))
                a = load_npz(folder/"dense_1025.npz")
                if (a["raw_state"].shape != (1025, 63)
                        or str(a["compton_branch"]) != rec["specification"]["branch"]
                        or hashlib.sha256(a["initial_state"].tobytes()).hexdigest() != rec["specification"]["initial_state_sha256"]):
                    raise ValueError("CORPUS_STATE_OWNER_CHANGED:"+label)
                cdir = PARENT/"results/analysis_v1"/label/"collisions"
                crec = json.loads((cdir/"RESULT.json").read_text())
                cp = cdir/"collisions_dense_1025.npz"
                if (crec["status"] != "COMPLETE" or crec["source_identity"] != collision_id
                        or crec["input_receipt_sha256"] != digest(receipt_path)
                        or crec["outputs"][cp.name]["sha256"] != digest(cp)
                        or crec["outputs"][cp.name]["bytes"] != cp.stat().st_size):
                    raise ValueError("COLLISION_REFERENCE_CHANGED:"+label)
                coll = load_npz(cp)
                if (str(coll["input_trajectory_sha256"]) != rec["outputs"]["dense_1025.npz"]["sha256"]
                        or str(coll["collision_source_identity"]) != collision_id
                        or not np.array_equal(coll["x"], a["x"])):
                    raise ValueError("COLLISION_GRID_BINDING_CHANGED:"+label)
                indices, selection = choose_indices(a, coll)
                inputs[label] = dict(receipt=rec, a=a, collision=coll, indices=indices, selection=selection)
                records.extend([binding(receipt_path), binding(cdir/"RESULT.json"), binding(cp)])
            return inputs, dict(runtime_identity=runtime_id, source_files=runtime_files,
                                collision_source_identity=collision_id, collision_source_files=collision_files,
                                saved_npz_files_verified=40, collision_reference_npz_files_verified=8, files=records)
        (inputs, manifest), inventory_timing = measured(inventory)
        save_json(output/"INPUT_MANIFEST.json", dict(**manifest, timing=inventory_timing))
        corpus = {label: row["selection"] for label, row in inputs.items()}
        save_json(output/"CORPUS_MANIFEST.json", corpus)
        results = []
        for label, row in inputs.items():
            case_dir = output/label
            case_dir.mkdir()
            rec, indices, a = row["receipt"], row["indices"], row["a"]
            selected = subset(a, indices)
            model, init_timing = measured(lambda: ComptonFull63(rec["specification"]["config"], branch=rec["specification"]["branch"]))
            collision, collision_init = measured(lambda: CollisionalBudget(model.atomic))
            d = {str(name): selected["diagnostics"][:, k] for k, name in enumerate(selected["diagnostic_names"])}
            def gather():
                return runner.gather_set(model, selected["x"], selected["raw_state"], selected["initial_Y"], deadline)
            def collisions():
                return collision_analysis._evaluate_grid(selected, d, model.atomic, collision)
            # One warmup of each exact baseline path, then three unprofiled repeats.
            _, gather_warmup = measured(gather)
            _, collision_warmup = measured(collisions)
            timings = []
            for repeat in range(REPEATS):
                _, gt = measured(gather)
                _, ct = measured(collisions)
                timings.append(dict(repeat=repeat+1, gather=gt, collision=ct))
            (garrays, gmetrics, ggates, genergy), gp = profile(gather)
            (carrays, csummary), cp = profile(collisions)
            point_comparison = exact_comparison(garrays, selected, GATHER_POINT_FIELDS)
            collision_fields = tuple(name for name, value in carrays.items()
                                     if value.ndim and value.shape[0] == POINTS_PER_CASE
                                     and "cumulative" not in name)
            selected_collision = subset(row["collision"], indices)
            collision_comparison = exact_comparison(carrays, selected_collision, collision_fields)
            save_json(case_dir/"GATHER_PROFILE.json", gp)
            save_json(case_dir/"COLLISION_PROFILE.json", cp)
            saved_arrays = {"selected_indices":indices}
            saved_arrays.update({"gather__"+name:value for name,value in garrays.items()})
            saved_arrays.update({"collision__"+name:value for name,value in carrays.items()})
            _, persist = measured(lambda: save_npz(case_dir/"PROFILED_OUTPUTS.npz", saved_arrays))
            output_binding, hash_timing = measured(lambda: binding(case_dir/"PROFILED_OUTPUTS.npz"))
            _, reload_timing = measured(lambda: load_npz(case_dir/"PROFILED_OUTPUTS.npz"))
            result = dict(label=label, states=len(indices), model_initialization=init_timing,
                          collision_initialization=collision_init, warmup=dict(gather=gather_warmup, collision=collision_warmup),
                          unprofiled_repeats=timings, profiled_gather_wall_seconds=gp["wall_seconds"],
                          profiled_collision_wall_seconds=cp["wall_seconds"],
                          gather_point_comparison=point_comparison, collision_point_comparison=collision_comparison,
                          subset_point_gates=ggates, subset_point_metrics=gmetrics,
                          subset_energy_summary= genergy, subset_collision_summary=csummary,
                          grid_summary_scope="64-state subset only; no full-grid quadrature/convergence claim",
                          save_npz_timing=persist, output_hash_timing=hash_timing, reload_npz_timing=reload_timing,
                          retained_outputs=output_binding,
                          pass_stage_point_check=point_comparison["pass_exact"] and collision_comparison["pass_exact"] and all(ggates.values()))
            save_json(case_dir/"RESULT.json", result)
            results.append(result)
            print(json.dumps(dict(label=label, states=len(indices), exact=result["pass_stage_point_check"],
                                  active_wall_seconds=time.perf_counter()-PROCESS_START)), flush=True)
            if not result["pass_stage_point_check"]:
                raise ValueError("POINT_REPLAY_MISMATCH:"+label)
        # Recheck only the actual input/source identities used in this stage.
        (final_runtime_id, final_source_files), final_source_timing = measured(runner.source_identity)
        if (final_runtime_id != RUNTIME_ID or final_source_files != manifest["source_files"]
                or collision_analysis._source_identity(RUNTIME_ID)[0] != manifest["collision_source_identity"]):
            raise ValueError("SOURCE_CHANGED_DURING_PROFILE")
        _, final_inputs_timing = measured(lambda: verify_manifest_files(manifest["files"]))
        if ODE_ATTEMPTS:
            raise RuntimeError("IVP_ATTEMPT_OBSERVED")
        save_json(output/"SUMMARY.json", dict(status="PASS_C2_BASELINE_PROFILE", selected_stage="C2",
                  states_total=sum(row["states"] for row in results), cases=len(results),
                  all_gather_point_arrays_exact=True, all_collision_point_arrays_exact=True,
                  new_IVPs=0, old_IVP_reruns=0, IVP_attempts=ODE_ATTEMPTS,
                  actual_science_source_identity=RUNTIME_ID, candidate_implementation=False,
                  performance_claim="baseline cost attribution only; no candidate speedup measured",
                  final_source_timing=final_source_timing, final_input_identity_timing=final_inputs_timing,
                  numerical_threads=1, numerical_workers=1, active_wall_cap_seconds=600,
                  peak_process_RSS_KiB=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                  case_results=[dict(label=r["label"], result=relative(output/r["label"]/"RESULT.json")) for r in results]))
        status = "PASS_C2_BASELINE_PROFILE"
    except Exception as exc:
        status = "FAILED_PRESERVED"
        save_json(output/"FAILED.json", dict(error=repr(exc), traceback=traceback.format_exc(), IVP_attempts=ODE_ATTEMPTS))
        raise
    finally:
        save_json(output/"FINISHED.json", dict(status=status, active_wall_seconds=time.perf_counter()-PROCESS_START,
                  active_cpu_seconds=time.process_time()-CPU_START, prior_active_wall_seconds=spent,
                  budget_cap_seconds=600, new_IVPs=0, IVP_attempts=ODE_ATTEMPTS,
                  finished_utc=datetime.now(timezone.utc).isoformat()))


def verify_manifest_files(rows):
    for row in rows:
        p = REPO/row["path"]
        if p.stat().st_size != row["bytes"] or digest(p) != row["sha256"]:
            raise ValueError("INPUT_CHANGED_DURING_PROFILE:"+row["path"])


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=UNIT/"evidence/profile/attempt_001")
    args = parser.parse_args()
    main(args.output)
