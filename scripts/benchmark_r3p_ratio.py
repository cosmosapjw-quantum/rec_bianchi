#!/usr/bin/env python3
"""Matched, bounded microbenchmark of saved independent V-lane ratios.

Example (run only after other performance experiments have finished)::

    python scripts/benchmark_r3p_ratio.py \
        --fixture /path/to/audit_pilot_legacy/ratio_fixture.npz \
        --provenance /path/to/audit_pilot_legacy/result.json \
        --build /path/to/r3p_build_001/build.json --output /tmp/ratio_run.json

The input already contains scalar-associated fbb. No expm1, CSV parsing,
physical integration, or prefix audit is timed. Each backend includes its
validation and output allocation; Rust also includes ctypes dispatch. Its
ratio ABI is serial and does not use the handle's Rayon pool. SIMD attribution
requires inspection of the recorded binary, independently of this benchmark.

Loading, hashing, pool setup, bitwise checks, negative controls, and warmups
are outside timed samples. The complete, nonadaptive schedule is written to
the create-only output before setup. Every timed method has equal repetitions
and input lanes. Results establish no end-to-end audit or physics speedup.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import platform
import resource
import statistics
import sys
import time
import zipfile

THREAD_ENV = ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
              "NUMEXPR_NUM_THREADS")
if __name__ == "__main__":
    for _name in THREAD_ENV:
        os.environ[_name] = "1"

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))
from r3p_rust_audit import PrefixAuditor, library_from_build, sha256

MAX_LANES = 64 * 314
MAX_FIXTURE_BYTES = 2 * 1024 * 1024
BACKENDS = ("scalar", "numpy", "rust")


def _inputs(py, native, fbb):
    arrays = tuple(np.asarray(x) for x in (py, native, fbb))
    if any(a.dtype != np.dtype("float64") for a in arrays):
        raise ValueError("R3P_RATIO_F64")
    if (any(a.ndim != 1 for a in arrays)
            or any(a.shape != arrays[0].shape for a in arrays)
            or len(arrays[0]) > MAX_LANES):
        raise ValueError("R3P_RATIO_SHAPE")
    return tuple(np.ascontiguousarray(a) for a in arrays)


def scalar_ratios(py, native, fbb):
    """Original ordered binary64 expression, with finite-input/output gates."""
    p, c, b = _inputs(py, native, fbb)
    out = np.empty_like(p)
    for i in range(len(p)):
        pv, cv, bv = float(p[i]), float(c[i]), float(b[i])
        if not (math.isfinite(pv) and math.isfinite(cv)
                and math.isfinite(bv) and bv >= 0.):
            raise ArithmeticError(f"R3P_RATIO_INPUT:{i}")
        tol = 1.e-7 * max(abs(pv), abs(cv)) + 1.e-10 * bv
        if not math.isfinite(tol) or tol == 0.:
            raise ArithmeticError(f"R3P_RATIO_TOLERANCE:{i}")
        ratio = abs(pv - cv) / tol
        if not math.isfinite(ratio):
            raise ArithmeticError(f"R3P_RATIO_NONFINITE:{i}")
        out[i] = ratio
    return out


def numpy_ratios(py, native, fbb):
    """Separate elementwise ufuncs preserve the scalar association; no sum."""
    p, c, b = _inputs(py, native, fbb)
    if not (np.isfinite(p).all() and np.isfinite(c).all()
            and np.isfinite(b).all() and (b >= 0.).all()):
        raise ArithmeticError("R3P_RATIO_INPUT")
    with np.errstate(over="ignore", invalid="ignore", divide="ignore",
                     under="ignore"):
        relative = 1.e-7 * np.maximum(np.abs(p), np.abs(c))
        floor = 1.e-10 * b
        tol = relative + floor
        out = np.abs(p - c) / tol
    if not np.isfinite(tol).all() or not np.isfinite(out).all():
        raise ArithmeticError("R3P_RATIO_NONFINITE")
    return out


def require_bitwise_equal(expected, actual, label="ratio"):
    """Reject NaN/Inf and every differing binary64 bit, including signed zero."""
    a, b = np.asarray(expected), np.asarray(actual)
    if (a.dtype != np.dtype("float64") or b.dtype != a.dtype
            or a.shape != b.shape or a.ndim != 1):
        raise AssertionError(f"R3P_RATIO_BITS_SHAPE:{label}")
    if not np.isfinite(a).all() or not np.isfinite(b).all():
        raise AssertionError(f"R3P_RATIO_BITS_NONFINITE:{label}")
    ab = np.ascontiguousarray(a).view(np.uint64)
    bb = np.ascontiguousarray(b).view(np.uint64)
    bad = np.flatnonzero(ab != bb)
    if bad.size:
        i = int(bad[0])
        raise AssertionError(
            f"R3P_RATIO_BITS:{label}:{i}:{int(ab[i]):016x}:{int(bb[i]):016x}")


def array_record(array):
    """Hash canonical little-endian, C-order raw bytes, not an NPY header."""
    a = np.asarray(array)
    canonical = np.ascontiguousarray(a, dtype=a.dtype.newbyteorder("<"))
    return {"dtype": canonical.dtype.str, "shape": list(canonical.shape),
            "nbytes": canonical.nbytes,
            "raw_sha256": hashlib.sha256(canonical.tobytes(order="C")).hexdigest()}


def load_fixture(path, provenance):
    path, provenance = Path(path).resolve(), Path(provenance).resolve()
    if path.stat().st_size > MAX_FIXTURE_BYTES:
        raise ValueError("R3P_RATIO_FIXTURE_SIZE")
    digest = sha256(path)
    metadata_bytes = provenance.read_bytes()
    metadata = json.loads(metadata_bytes)
    schema = metadata.get("schema")
    if schema == "rec.r3p.ratio-fixture.v1":
        expected = metadata["fixture_sha256"]
    elif schema == "rec.r3p.saved-audit.v1":
        expected = metadata["ratio_fixture_sha256"]
    else:
        raise ValueError("R3P_RATIO_PROVENANCE_SCHEMA")
    if digest != expected:
        raise ValueError("R3P_RATIO_FIXTURE_SHA")
    with zipfile.ZipFile(path) as archive:
        entries = archive.infolist()
        if len(entries) > 8 or sum(e.file_size for e in entries) > MAX_FIXTURE_BYTES:
            raise ValueError("R3P_RATIO_FIXTURE_EXPANDED_SIZE")
    with np.load(path, allow_pickle=False) as data:
        arrays = _inputs(*(data[name] for name in ("py", "native", "fbb")))
    if not len(arrays[0]):
        raise ValueError("R3P_RATIO_EMPTY_FIXTURE")
    if sha256(path) != digest:
        raise ValueError("R3P_RATIO_FIXTURE_CHANGED_DURING_LOAD")
    records = {name: array_record(a)
               for name, a in zip(("py", "native", "fbb"), arrays)}
    if schema == "rec.r3p.ratio-fixture.v1":
        if metadata.get("lanes") != len(arrays[0]):
            raise ValueError("R3P_RATIO_FIXTURE_LANES")
        if any(metadata["arrays"].get(k) != v for k, v in records.items()):
            raise ValueError("R3P_RATIO_INPUT_RAW_SHA")
    for a in arrays:
        a.flags.writeable = False
    return arrays, {"path": str(path), "npz_sha256": digest,
                    "npz_bytes": path.stat().st_size, "lanes": len(arrays[0]),
                    "arrays": records, "provenance_path": str(provenance),
                    "provenance_sha256": hashlib.sha256(metadata_bytes).hexdigest(),
                    "provenance": metadata}


def make_plan(lanes, *, repeats=64, trials=6, warmups=2, threads=1):
    """Pure predeclaration: no timings, calibration, or adaptive repetition."""
    if type(lanes) is not int or not 1 <= lanes <= MAX_LANES:
        raise ValueError("R3P_RATIO_PLAN_LANES")
    if type(repeats) is not int or not 1 <= repeats <= 256:
        raise ValueError("R3P_RATIO_PLAN_REPEATS")
    if type(trials) is not int or trials not in (3, 6, 9, 12):
        raise ValueError("R3P_RATIO_PLAN_BALANCED_TRIALS")
    if type(warmups) is not int or not 0 <= warmups <= 8:
        raise ValueError("R3P_RATIO_PLAN_WARMUPS")
    if type(threads) is not int or threads not in (1, 2, 4):
        raise ValueError("R3P_RATIO_PLAN_THREADS")
    if lanes * repeats * trials > 50_000_000:
        raise ValueError("R3P_RATIO_PLAN_WORK_CAP")
    schedule = [list(BACKENDS[i % 3:] + BACKENDS[:i % 3]) for i in range(trials)]
    return {"lanes": lanes, "repeats_per_sample": repeats, "trials": trials,
            "warmups_per_backend": warmups, "schedule": schedule,
            "timed_calls_per_backend": repeats * trials,
            "timed_lanes_per_backend": lanes * repeats * trials,
            "handle_threads": threads, "ratio_execution_threads": 1,
            "pool_used_by_ratio": False, "adaptive_repeats": False}


def negative_controls(methods):
    """Fail closed on invalid lanes; also exercise the bitwise gate itself."""
    controls = {
        "python_nan": (float("nan"), 0., 1.),
        "native_inf": (0., float("inf"), 1.),
        "fbb_nan": (0., 0., float("nan")),
        "fbb_negative": (0., 0., -1.),
        "zero_over_zero": (0., 0., 0.),
        "difference_overflow": (sys.float_info.max, -sys.float_info.max, 1.),
    }
    results = {}
    for name, method in methods.items():
        rejected = []
        for control, values in controls.items():
            args = tuple(np.array([v], dtype=np.float64) for v in values)
            try:
                method(*args)
            except ArithmeticError:
                rejected.append(control)
            else:
                raise AssertionError(f"R3P_RATIO_NEGATIVE_ACCEPTED:{name}:{control}")
        results[name] = rejected
    for name, original, changed in (
            ("one_ulp", np.array([1.]), np.array([np.nextafter(1., math.inf)])),
            ("signed_zero", np.array([0.]), np.array([-0.]))):
        try:
            require_bitwise_equal(original, changed, name)
        except AssertionError:
            results[name] = "rejected"
        else:
            raise AssertionError(f"R3P_RATIO_NEGATIVE_BITS_ACCEPTED:{name}")
    return results


def _process_threads():
    tasks = Path("/proc/self/task")
    return len(list(tasks.iterdir())) if tasks.exists() else None


def _sources(build):
    names = set(build["source_sha256"]) | {
        "scripts/benchmark_r3p_ratio.py", "scripts/r3p_rust_audit.py",
        "scripts/verify_r3i_h2_u6_rt_boundary.py"}
    return {name: sha256(ROOT / name) for name in sorted(names)}


def _stamp():
    return time.process_time_ns(), time.perf_counter_ns()


def _elapsed(start):
    cpu, wall = _stamp()
    return {"cpu_seconds": (cpu - start[0]) / 1.e9,
            "wall_seconds": (wall - start[1]) / 1.e9}


def remaining_cpu_budget(requested, used, limits):
    """Respect inherited absolute CPU limits without changing either limit."""
    finite = [float(limit) - used - 1. for limit in limits
              if limit != resource.RLIM_INFINITY]
    remaining = min([requested, *finite])
    if remaining <= 0.:
        raise RuntimeError("R3P_RATIO_INHERITED_CPU_BUDGET_EXHAUSTED")
    return remaining


def _run(args):
    """Execute one complete matched plan; never overwrite an existing receipt."""
    if (not math.isfinite(args.cpu_cap) or not 0. < args.cpu_cap <= 30.
            or not math.isfinite(args.wall_cap) or not 0. < args.wall_cap <= 180.):
        raise ValueError("R3P_RATIO_TIME_CAP")
    preparation = _stamp()
    inherited_cpu = resource.getrlimit(resource.RLIMIT_CPU)
    effective_cpu = remaining_cpu_budget(args.cpu_cap, preparation[0] / 1.e9, inherited_cpu)
    arrays, input_record = load_fixture(args.fixture, args.provenance)
    build_path = Path(args.build).resolve()
    build = json.loads(build_path.read_text())
    library = library_from_build(build_path)
    source_hashes = _sources(build)
    plan = make_plan(len(arrays[0]), repeats=args.repeats, trials=args.trials,
                     warmups=args.warmups, threads=args.threads)
    affinity = sorted(os.sched_getaffinity(0)) if hasattr(os, "sched_getaffinity") else None
    if args.threads > min(4, len(affinity) if affinity else (os.cpu_count() or 1)):
        raise ValueError("R3P_RATIO_THREADS_AFFINITY")
    report = {
        "schema": "rec.r3p.ratio-benchmark.v1", "status": "PLANNED",
        "scope": "saved independent-lane ratios; no integration or full-audit claim",
        "timed_boundary": "backend validation, output allocation, call, and per-call budget check",
        "excluded_from_samples": ["input loading", "hashing", "pool setup", "preflight",
                                  "warmups", "post-sample bitwise checks", "pool teardown"],
        "command": list(sys.argv), "cwd": str(Path.cwd()),
        "plan": plan, "input": input_record,
        "build_receipt": {"path": str(build_path), "sha256": sha256(build_path)},
        "binary": {"path": str(library), "sha256": sha256(library)},
        "build_source_sha256": build["source_sha256"], "source_sha256": source_hashes,
        "environment": {"python": sys.version, "numpy": np.__version__,
                        "platform": platform.platform(), "machine": platform.machine(),
                        "affinity": affinity, "threads_before_setup": _process_threads(),
                        "thread_environment": {k: os.environ.get(k) for k in THREAD_ENV}},
        "caps": {"requested_cpu_seconds": args.cpu_cap, "effective_cpu_seconds": effective_cpu,
                 "wall_seconds": args.wall_cap, "inherited_cpu_limits_seconds": [
                     None if value == resource.RLIM_INFINITY else value for value in inherited_cpu],
                 "process_cpu_used_at_start_seconds": preparation[0] / 1.e9,
                 "inherited_limit_reserve_seconds": 1., "resource_limits_changed": False,
                 "scope": "from input loading onward; interpreter imports precede this interval",
                 "enforcement": "checked between calls; one in-flight call may exceed a cap"},
        "preparation": _elapsed(preparation), "samples": [],
    }
    output = Path(args.output).resolve()
    # Open before creating the pool; a crash leaves the predeclared plan.
    with output.open("x+", encoding="utf-8") as stream:
        def persist():
            stream.seek(0)
            json.dump(report, stream, sort_keys=True, indent=2, allow_nan=False)
            stream.write("\n")
            stream.truncate()
            stream.flush()
            os.fsync(stream.fileno())

        persist()
        started = _stamp()
        auditor = None

        def guard():
            spent = _elapsed(preparation)
            if spent["cpu_seconds"] > effective_cpu or spent["wall_seconds"] > args.wall_cap:
                raise RuntimeError("R3P_RATIO_BUDGET")

        try:
            guard()
            stamp = _stamp()
            auditor = PrefixAuditor(library, threads=args.threads)
            report["pool_setup"] = _elapsed(stamp)
            report["environment"]["threads_after_setup"] = _process_threads()
            report["pool_setup"]["kind"] = "direct serial handle" if args.threads == 1 else "local Rayon pool"
            methods = {"scalar": scalar_ratios, "numpy": numpy_ratios, "rust": auditor.ratios}
            stamp = _stamp()
            expected = scalar_ratios(*arrays)
            for name, method in methods.items():
                require_bitwise_equal(expected, method(*arrays), name)
                guard()
            report["negative_controls"] = negative_controls(methods)
            report["preflight"] = {**_elapsed(stamp), "all_lanes_bitwise_equal": True,
                                   "reference": "original ordered scalar binary64 expression",
                                   "output": array_record(expected)}
            stamp = _stamp()
            for _ in range(plan["warmups_per_backend"]):
                for name, method in methods.items():
                    require_bitwise_equal(expected, method(*arrays), f"warmup:{name}")
                    guard()
            report["warmup"] = _elapsed(stamp)
            report["status"] = "RUNNING"
            persist()
            for trial, order in enumerate(plan["schedule"]):
                for position, name in enumerate(order):
                    guard()
                    sample = {"trial": trial, "position": position, "backend": name,
                              "completed_calls": 0, "status": "RUNNING"}
                    report["samples"].append(sample)
                    method = methods[name]
                    stamp = _stamp()
                    try:
                        for _ in range(plan["repeats_per_sample"]):
                            actual = method(*arrays)
                            sample["completed_calls"] += 1
                            guard()
                    finally:
                        sample.update(_elapsed(stamp))
                    require_bitwise_equal(expected, actual, f"trial:{trial}:{name}")
                    sample.update(status="COMPLETE", last_output=array_record(actual))
                persist()
            if (_sources(build) != source_hashes or sha256(library) != report["binary"]["sha256"]
                    or sha256(build_path) != report["build_receipt"]["sha256"]
                    or sha256(args.fixture) != input_record["npz_sha256"]
                    or sha256(args.provenance) != input_record["provenance_sha256"]):
                raise RuntimeError("R3P_RATIO_PROVENANCE_CHANGED_DURING_RUN")
            if any(array_record(a) != input_record["arrays"][name]
                   for name, a in zip(("py", "native", "fbb"), arrays)):
                raise RuntimeError("R3P_RATIO_INPUT_MUTATED")
            report["summary"] = {}
            for name in BACKENDS:
                samples = [s for s in report["samples"] if s["backend"] == name]
                assert sum(s["completed_calls"] for s in samples) == plan["timed_calls_per_backend"]
                report["summary"][name] = {
                    "samples": len(samples), "calls": plan["timed_calls_per_backend"],
                    "lanes": plan["timed_lanes_per_backend"],
                    "median_cpu_seconds": statistics.median(s["cpu_seconds"] for s in samples),
                    "median_wall_seconds": statistics.median(s["wall_seconds"] for s in samples),
                }
            report["status"] = "COMPLETE_BITWISE_EQUAL"
        except Exception as exc:
            report["status"] = "FAILED"
            report["failure"] = {"type": type(exc).__name__, "message": str(exc)}
            raise
        finally:
            if auditor is not None:
                stamp = _stamp()
                auditor.close()
                report["pool_teardown"] = _elapsed(stamp)
            report["environment"]["threads_after_teardown"] = _process_threads()
            report["execution_including_setup_checks_and_io"] = _elapsed(started)
            report["total_including_preparation"] = _elapsed(preparation)
            persist()
    return report


def run(args):
    """Also preserve failures before a valid input/build permits a full plan."""
    started = _stamp()
    try:
        return _run(args)
    except Exception as exc:
        failure = {
            "schema": "rec.r3p.ratio-benchmark.v1", "status": "FAILED",
            "phase": "preparation", "command": list(sys.argv), "cwd": str(Path.cwd()),
            "failure": {"type": type(exc).__name__, "message": str(exc)},
            "observed_elapsed": _elapsed(started), "samples": [],
            "requested_paths": {name: str(getattr(args, name, None))
                                for name in ("fixture", "provenance", "build")},
        }
        try:
            with Path(args.output).open("x", encoding="utf-8") as stream:
                json.dump(failure, stream, sort_keys=True, indent=2, allow_nan=False)
                stream.write("\n")
        except FileExistsError:
            # A running/final receipt, or an earlier unrelated file, is never
            # overwritten here. _run writes its own post-plan failure receipt.
            pass
        except OSError as receipt_error:
            exc.add_note(f"Could not create failure receipt: {receipt_error}")
        raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixture", type=Path, required=True)
    parser.add_argument("--provenance", type=Path, required=True)
    parser.add_argument("--build", type=Path, default=os.environ.get("R3P_BUILD_RECEIPT"))
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--repeats", type=int, default=64)
    parser.add_argument("--trials", type=int, default=6, choices=(3, 6, 9, 12))
    parser.add_argument("--warmups", type=int, default=2)
    parser.add_argument("--threads", type=int, default=1, choices=(1, 2, 4))
    parser.add_argument("--cpu-cap", type=float, default=30.)
    parser.add_argument("--wall-cap", type=float, default=120.)
    args = parser.parse_args()
    if args.build is None:
        parser.error("--build or R3P_BUILD_RECEIPT is required")
    try:
        report = run(args)
    except Exception as exc:
        print(json.dumps({"status": "FAILED", "output": str(args.output.resolve()),
                          "type": type(exc).__name__, "message": str(exc)}, sort_keys=True),
              file=sys.stderr)
        return 1
    print(json.dumps({"status": report["status"], "output": str(args.output.resolve()),
                      "summary": report["summary"]}, sort_keys=True, allow_nan=False))


if __name__ == "__main__":
    sys.exit(main())
