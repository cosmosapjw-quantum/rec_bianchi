#!/usr/bin/env python3
"""Source-bound replay benchmark for the opt-in R3R native-stream comparator.

This script opens an already-produced native CSV and Python NPZ.  It never
builds an oracle or advances the solver.  The timed interval includes opening
the CSV, scalar parsing, comparator allocations, callbacks and verdict
assembly; input loading and provenance checks are reported outside it.  File
hashing and explicit warmups make this a warm-cache replay measurement.

At most five paired rounds alternate their backend order.  Separate fresh
subprocesses measure each backend's process-lifetime peak RSS, including
interpreter/import/input setup.  Those peaks are not incremental comparator
allocations.  Existing hard limits are only lowered, with recovery reserves
inside the 60 CPU-second / 180 wall-second / 2 GiB envelope.
"""
from __future__ import annotations

import argparse
from array import array
import hashlib
import json
import math
import os
import platform
import resource
import signal
import statistics
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

START_WALL = time.monotonic()
os.environ.update({"OMP_NUM_THREADS": "1", "OPENBLAS_NUM_THREADS": "1",
                   "MKL_NUM_THREADS": "1", "NUMEXPR_NUM_THREADS": "1"})
FRESH_PYCACHE_PREFIX = None
if __name__ == "__main__":
    # -B prevents writes but still permits stale timestamp-valid .pyc reads.
    # A newly created empty prefix makes every later task import read source.
    FRESH_PYCACHE_PREFIX = tempfile.mkdtemp(prefix="rec-r3r-benchmark-pycache-")
    sys.pycache_prefix = FRESH_PYCACHE_PREFIX
    sys.dont_write_bytecode = True

CPU_LIMIT_S = 60
WALL_LIMIT_S = 180
RECOVERY_CPU_S = 5
RECOVERY_WALL_S = 12
ADDRESS_LIMIT_BYTES = 2 * 1024 ** 3


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def file_identity(path):
    path = Path(path)
    return {"path": str(path.resolve()), "bytes": path.stat().st_size,
            "sha256": sha256(path)}


def total_cpu_s():
    own = resource.getrusage(resource.RUSAGE_SELF)
    children = resource.getrusage(resource.RUSAGE_CHILDREN)
    return own.ru_utime + own.ru_stime + children.ru_utime + children.ru_stime


def check_budget(stage):
    cpu = total_cpu_s()
    wall = time.monotonic() - START_WALL
    if cpu >= CPU_LIMIT_S - RECOVERY_CPU_S or wall >= WALL_LIMIT_S - RECOVERY_WALL_S:
        raise RuntimeError(f"R3R_REPLAY_BUDGET:{stage}:cpu_s={cpu:.6f}:wall_s={wall:.6f}")


def lower_limit(kind, cap):
    soft, hard = resource.getrlimit(kind)
    hard_new = cap if hard == resource.RLIM_INFINITY else min(hard, cap)
    soft_new = hard_new if soft == resource.RLIM_INFINITY else min(soft, hard_new)
    resource.setrlimit(kind, (soft_new, hard_new))


def install_limits():
    lower_limit(resource.RLIMIT_AS, ADDRESS_LIMIT_BYTES)
    lower_limit(resource.RLIMIT_CPU, CPU_LIMIT_S)

    def deadline(_signum, _frame):
        raise TimeoutError("R3R_REPLAY_WALL_WORK_LIMIT")

    signal.signal(signal.SIGALRM, deadline)
    remaining = WALL_LIMIT_S - RECOVERY_WALL_S - (time.monotonic() - START_WALL)
    if remaining <= 0:
        raise TimeoutError("R3R_REPLAY_WALL_WORK_LIMIT")
    signal.setitimer(signal.ITIMER_REAL, remaining)


if __name__ == "__main__":
    # Include numerical imports in the CLI envelope. Programmatic imports by
    # regression tests neither alter process limits nor install an alarm.
    install_limits()

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "src")]
import verify_r3q_h4_continuation as baseline
import r3r_stream_audit as optimized

CHECKPOINT = ROOT / "research/rec_r3o_grid_frontiers_20261019/h4_start_002/python_h4_full_start.npz"
SOURCE_ARCHIVE = ROOT / "archive/inputs/original_hyrec_oct2012/HyRec_Oct2012.zip"
BACKENDS = {"legacy": baseline.compare_native_stream,
            "r3r_numpy": optimized.compare_native_stream}


def environment_identity():
    cpu_model = None
    cpuinfo = Path("/proc/cpuinfo")
    if cpuinfo.is_file():
        cpu_model = next((line.split(":", 1)[1].strip()
                          for line in cpuinfo.read_text().splitlines()
                          if line.startswith("model name")), None)
    return {"python": sys.version, "python_executable": file_identity(sys.executable),
            "numpy_version": np.__version__, "platform": platform.platform(),
            "machine": platform.machine(), "cpu_model": cpu_model,
            "affinity": sorted(os.sched_getaffinity(0)) if hasattr(os, "sched_getaffinity") else None,
            "thread_environment": {k: os.environ[k] for k in (
                "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS")},
            "rlimit_as": list(resource.getrlimit(resource.RLIMIT_AS)),
            "rlimit_cpu": list(resource.getrlimit(resource.RLIMIT_CPU)),
            "fresh_pycache_prefix": FRESH_PYCACHE_PREFIX,
            "active_pycache_prefix": sys.pycache_prefix,
            "dont_write_bytecode": sys.dont_write_bytecode,
            "np_geterr": np.geterr()}


def git_value(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def source_identity(expected_sha):
    actual = git_value("rev-parse", "HEAD")
    if actual != expected_sha:
        raise ValueError(f"R3R_SOURCE_HEAD_MISMATCH:{actual}:{expected_sha}")
    modified = git_value("diff", "--name-only", "HEAD", "--", "scripts", "src")
    if modified:
        raise ValueError(f"R3R_SOURCE_WORKTREE_MODIFIED:{modified}")
    sources = {}
    for relative in ("scripts/benchmark_r3r_stream_audit.py", "scripts/r3r_stream_audit.py",
                     "scripts/verify_r3q_h4_continuation.py"):
        expected = subprocess.check_output(["git", "show", f"{actual}:{relative}"], cwd=ROOT)
        identity = file_identity(ROOT / relative)
        if identity["sha256"] != hashlib.sha256(expected).hexdigest():
            raise ValueError(f"R3R_SOURCE_FILE_MISMATCH:{relative}")
        sources[relative] = identity
    return {"source_commit_sha": actual, "source_tree_sha": git_value("rev-parse", "HEAD^{tree}"),
            "branch": git_value("branch", "--show-current"), "source_files": sources,
            "tracked_scripts_and_src_unchanged": True}


def load_inputs(checkpoint_path, result_path, archive_path, event):
    checkpoint = baseline.load_frozen_start(checkpoint_path)
    with np.load(result_path, allow_pickle=False) as arrays:
        result = SimpleNamespace(
            states=tuple(json.loads(str(value)) for value in arrays["states_json"]),
            steps=tuple(json.loads(str(value)) for value in arrays["steps_json"]),
            virtual_out=arrays["virtual_out"], average_virtual=arrays["average_virtual"],
            lyman_out=arrays["lyman_out"], event=event)
    cosmology = baseline.HyRec2012Cosmology()
    rates = baseline.OriginalHyRecPrimitiveRateTable.from_archive(archive_path)
    table = baseline._canonical_twophoton_table(rates.archive_path)
    return checkpoint, result, cosmology, table


def input_identity(args):
    identities = {key: file_identity(getattr(args, key)) for key in
                  ("native_stream", "python_result", "verification", "checkpoint", "source_archive")}
    verification = json.loads(args.verification.read_text())
    expected = {"native_stream": verification["native_run"]["stdout_sha256"],
                "python_result": verification["python_history_sha256"],
                "checkpoint": verification["checkpoint_sha256"],
                "source_archive": verification["source_zip_sha256"]}
    for key, digest in expected.items():
        if identities[key]["sha256"] != digest:
            raise ValueError(f"R3R_INPUT_RECEIPT_MISMATCH:{key}")
    if verification["native_run"]["returncode"] != 0 or verification.get("first_failure") is not None:
        raise ValueError("R3R_INPUT_RECEIPT_FAILED_EXECUTION")
    closure = baseline.verify_capsule_source_closure(ROOT, args.checkpoint)
    return {"files": identities, "original_execution_status": verification["status"],
            "original_execution_allocation": verification.get("new_allocation_id"),
            "original_source_producer_sha256": verification.get("producer_sha256"),
            "frozen_source_closure": closure}, verification["python_result"]["event"]


def arrays_identity(inputs):
    checkpoint, result, _, table = inputs
    arrays = {f"checkpoint/{key}": value for key, value in checkpoint.items()
              if isinstance(value, np.ndarray)}
    arrays.update({f"result/{key}": getattr(result, key) for key in
                   ("virtual_out", "average_virtual", "lyman_out")})
    arrays["table/energy_eV"] = table.energy_eV
    return {key: {"shape": list(value.shape), "dtype": value.dtype.str,
                  "sha256": hashlib.sha256(value.tobytes(order="C")).hexdigest()}
            for key, value in arrays.items()}


def verdict_identity(verdict, guards):
    """Canonical JSON plus every returned maximum's exact binary64 hex value."""
    clean = json.loads(json.dumps(verdict, allow_nan=False))
    return {"verdict": clean,
            "maxima_float_hex": {key: float(value).hex() for key, value in verdict["maxima"].items()},
            "guard_labels": list(guards)}


def trace_lane_ratios(native_stream, inputs, block_rows, output_dir=None):
    """Untimed, ordered native-binary64 trace for a healthy vector-only replay.

    The independent scalar scan retains the frozen comparator expression.
    The candidate is observed externally at its division ufunc; no production
    instrumentation or acceptance path is modified.  This is a lane-byte
    check, separate from returned-maxima or predicate equality.
    """
    checkpoint, result, c, table = inputs
    scalar = array("d")
    order_digest = hashlib.sha256()
    with native_stream.open() as stream:
        for line_number, line in enumerate(stream, 1):
            if line_number % 8192 == 0:
                check_budget("scalar_lane_trace")
            values = line.rstrip("\n").split(",")
            tag = values[0]
            if tag not in ("V", "A", "L"):
                continue
            j, b = int(values[1]), int(values[2])
            source = ({"V": checkpoint["virtual_out"], "A": checkpoint["average_virtual"],
                       "L": checkpoint["lyman_out"]} if j < 8 else
                      {"V": result.virtual_out, "A": result.average_virtual, "L": result.lyman_out})
            py, cv = source[tag][b, j], float(values[3])
            z = c.redshift(72892+j)
            ev = baseline.LINE_EV[b] if tag == "L" else table.energy_eV[b]
            fbb = 1./math.expm1(ev/(baseline.KB_EV_K*c.T0_K*(1.+z)))
            tol = 1.e-7*max(abs(py), abs(cv))+1.e-10*fbb
            ratio = abs(py-cv)/tol
            if not math.isfinite(ratio) or ratio > 1.:
                raise ArithmeticError(f"R3R_SCALAR_TRACE_INVALID:j={j}:tag={tag}:bin={b}")
            scalar.append(float(ratio))
            order_digest.update(f"{tag},{j},{b}\n".encode("ascii"))
    observed = []
    original_divide = optimized.np.divide

    def traced_divide(*args, **kwargs):
        value = original_divide(*args, **kwargs)
        observed.append(value.tobytes(order="C"))
        return value

    guards, stats = [], {}
    with patch.object(optimized.np, "divide", traced_divide):
        verdict = optimized.compare_native_stream(
            native_stream, *inputs, guards.append, block_rows=block_rows, stats=stats)
    scalar_bytes, observed_bytes = scalar.tobytes(), b"".join(observed)
    count = sum(verdict["counts"][tag] for tag in ("V", "A", "L"))
    if (scalar.itemsize != 8 or stats["scalar_replay_blocks"] or
            len(scalar_bytes) != 8*count or len(observed_bytes) != 8*count):
        raise ArithmeticError("R3R_LANE_TRACE_REQUIRES_HEALTHY_BINARY64_VECTOR_PATH")
    old_bits, new_bits = (np.frombuffer(content, dtype=np.uint64)
                          for content in (scalar_bytes, observed_bytes))
    differing = int(np.count_nonzero(old_bits != new_bits))
    traces = {}
    for name, content in (("scalar", scalar_bytes), ("numpy", observed_bytes)):
        identity = {"bytes": len(content), "sha256": hashlib.sha256(content).hexdigest()}
        if output_dir is not None:
            path = output_dir / f"lane_ratios_{name}.f64native.bin"
            with path.open("xb") as out:
                out.write(content)
            identity["path"] = str(path)
        traces[name] = identity
    if differing:
        raise ArithmeticError(f"R3R_LANE_BYTES_DIFFER:{differing}")
    return {"status": "PASS", "lanes": count, "differing_binary64_lanes": differing,
            "native_byteorder": sys.byteorder, "ordered_tag_j_bin_sha256": order_digest.hexdigest(),
            "traces": traces, "identity": verdict_identity(verdict, guards),
            "scope": "separate untimed scalar CSV scan vs external NumPy divide trace; healthy vector path only"}


def run_trial(backend, args, inputs, phase, round_index, position):
    check_budget("before_trial")
    guards = []
    stats = {}

    def guard(label):
        guards.append(label)
        check_budget(label)

    options = {"block_rows": args.block_rows, "stats": stats} if backend == "r3r_numpy" else {}
    cpu_before, wall_before = time.process_time(), time.perf_counter()
    verdict = BACKENDS[backend](args.native_stream, *inputs, guard, **options)
    wall_s, cpu_s = time.perf_counter() - wall_before, time.process_time() - cpu_before
    check_budget("after_trial")
    return {"backend": backend, "phase": phase, "round": round_index, "position": position,
            "cpu_s": cpu_s, "wall_s": wall_s, "identity": verdict_identity(verdict, guards),
            "optional_comparator_stats": stats if backend == "r3r_numpy" else None}


def peak_rss_bytes():
    value = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return int(value if sys.platform == "darwin" else value * 1024)


def memory_worker(args):
    install_limits()
    provenance, event = input_identity(args)
    inputs = load_inputs(args.checkpoint, args.python_result, args.source_archive, event)
    trial = run_trial(args.rss_backend, args, inputs, "fresh_process_rss", 0, 0)
    return {"status": "PASS", "backend": args.rss_backend, "pid": os.getpid(),
            "source": source_identity(args.source_sha),
            "input_file_hashes": {key: value["sha256"] for key, value in provenance["files"].items()},
            "trial": trial, "peak_rss_bytes": peak_rss_bytes(),
            "peak_rss_scope": "fresh process lifetime including interpreter, imports, hashing and input setup",
            "process_tree_cpu_s": total_cpu_s(), "environment": environment_identity()}


def measure_fresh_rss(backend, args):
    check_budget("before_rss_child")
    command = [sys.executable, "-B", str(Path(__file__).resolve()),
               "--source-sha", args.source_sha, "--native-stream", str(args.native_stream.resolve()),
               "--python-result", str(args.python_result.resolve()),
               "--verification", str(args.verification.resolve()),
               "--checkpoint", str(args.checkpoint.resolve()),
               "--source-archive", str(args.source_archive.resolve()),
               "--block-rows", str(args.block_rows), "--rss-backend", backend]
    remaining_cpu = int(math.floor(CPU_LIMIT_S - RECOVERY_CPU_S - total_cpu_s()))
    remaining_wall = WALL_LIMIT_S - RECOVERY_WALL_S - (time.monotonic() - START_WALL)
    if remaining_cpu < 1 or remaining_wall <= 0:
        raise RuntimeError("R3R_REPLAY_NO_CHILD_BUDGET")

    def child_limit():
        lower_limit(resource.RLIMIT_CPU, remaining_cpu)

    failure = None
    try:
        done = subprocess.run(command, cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                              timeout=remaining_wall, preexec_fn=child_limit, check=False)
        stdout, stderr, returncode = done.stdout, done.stderr, done.returncode
    except subprocess.TimeoutExpired as exc:
        stdout, stderr, returncode = exc.stdout or b"", exc.stderr or b"", None
        failure = {"type": type(exc).__name__, "message": str(exc),
                   "exit_code": "UNAVAILABLE_AFTER_TIMEOUT"}
    for suffix, content in (("stdout.json", stdout), ("stderr.log", stderr)):
        with (args.output_dir / f"rss_{backend}.{suffix}").open("xb") as out:
            out.write(content)
    process = {"command": command, "returncode": returncode,
               "stdout_sha256": hashlib.sha256(stdout).hexdigest(),
               "stderr_sha256": hashlib.sha256(stderr).hexdigest(),
               "child_cpu_limit_s": remaining_cpu}
    if failure is not None:
        process["failure"] = failure
    elif returncode == 0:
        try:
            process["result"] = json.loads(stdout)
        except (ValueError, UnicodeError) as exc:
            process["failure"] = {"type": type(exc).__name__, "message": str(exc)}
    return process


def summarize(trials):
    measured = [trial for trial in trials if trial["phase"] == "measured"]
    backend_summary = {}
    for backend in BACKENDS:
        rows = [trial for trial in measured if trial["backend"] == backend]
        backend_summary[backend] = {
            "trials": len(rows),
            "median_cpu_s": statistics.median(row["cpu_s"] for row in rows),
            "median_wall_s": statistics.median(row["wall_s"] for row in rows)}
    pairs = []
    for index in sorted({trial["round"] for trial in measured}):
        pair = {row["backend"]: row for row in measured if row["round"] == index}
        pairs.append({"round": index,
                      "order": [row["backend"] for row in sorted(pair.values(), key=lambda row: row["position"])],
                      "legacy_over_r3r_cpu": pair["legacy"]["cpu_s"] / pair["r3r_numpy"]["cpu_s"],
                      "legacy_over_r3r_wall": pair["legacy"]["wall_s"] / pair["r3r_numpy"]["wall_s"]})
    return {"backends": backend_summary, "paired_ratios": pairs,
            "median_paired_cpu_ratio": statistics.median(pair["legacy_over_r3r_cpu"] for pair in pairs),
            "median_paired_wall_ratio": statistics.median(pair["legacy_over_r3r_wall"] for pair in pairs),
            "measurement_scope": "entire warm-cache CSV audit including open, parsing, allocations, callbacks, and verdict; no solver",
            "uncertainty_scope": "at most five local paired rounds; no confidence interval or platform-general claim"}


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-sha", required=True, help="full committed source HEAD; dirty code is rejected")
    parser.add_argument("--native-stream", required=True, type=Path)
    parser.add_argument("--python-result", required=True, type=Path)
    parser.add_argument("--verification", required=True, type=Path)
    parser.add_argument("--checkpoint", type=Path, default=CHECKPOINT)
    parser.add_argument("--source-archive", type=Path, default=SOURCE_ARCHIVE)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--rounds", type=int, choices=range(1, 6), default=5)
    parser.add_argument("--warmups", type=int, choices=range(0, 3), default=1)
    parser.add_argument("--block-rows", type=int, default=optimized.DEFAULT_BLOCK_ROWS)
    parser.add_argument("--rss-backend", choices=tuple(BACKENDS), help=argparse.SUPPRESS)
    args = parser.parse_args(argv)
    if len(args.source_sha) != 40 or any(char not in "0123456789abcdef" for char in args.source_sha):
        parser.error("--source-sha must be a full lowercase 40-character SHA")
    if not 1 <= args.block_rows <= optimized.MAX_BLOCK_ROWS:
        parser.error("--block-rows must be in 1..625")
    if args.rss_backend is None and args.output_dir is None:
        parser.error("--output-dir is required for the parent benchmark")
    return args


def main(argv=None):
    args = parse_args(argv)
    if args.rss_backend is not None:
        print(json.dumps(memory_worker(args), sort_keys=True, allow_nan=False))
        return 0
    args.output_dir.mkdir(parents=True, exist_ok=False)
    receipt = {"schema": "REC_R3R_STREAM_AUDIT_BENCHMARK_V1", "status": "RUNNING",
               "command": [sys.executable, *sys.argv], "trials": [], "fresh_process_rss": {},
               "solver_integrations": 0, "limits": {"cpu_s": CPU_LIMIT_S, "wall_s": WALL_LIMIT_S,
                    "address_bytes": ADDRESS_LIMIT_BYTES, "recovery_cpu_s": RECOVERY_CPU_S,
                    "recovery_wall_s": RECOVERY_WALL_S}}
    try:
        install_limits()
        receipt["source"] = source_identity(args.source_sha)
        receipt["inputs"], event = input_identity(args)
        receipt["environment"] = environment_identity()
        inputs = load_inputs(args.checkpoint, args.python_result, args.source_archive, event)
        before = arrays_identity(inputs)
        reference = None
        for phase, rounds in (("warmup", args.warmups), ("measured", args.rounds)):
            for index in range(rounds):
                order = ("legacy", "r3r_numpy") if index % 2 == 0 else ("r3r_numpy", "legacy")
                for position, backend in enumerate(order):
                    trial = run_trial(backend, args, inputs, phase, index, position)
                    receipt["trials"].append(trial)
                    if reference is None:
                        reference = trial["identity"]
                    if trial["identity"] != reference:
                        raise ArithmeticError(f"R3R_REPLAY_DIFFERENTIAL:{phase}:{index}:{backend}")
        for backend in BACKENDS:
            memory = measure_fresh_rss(backend, args)
            receipt["fresh_process_rss"][backend] = memory
            if memory["returncode"] != 0 or memory.get("failure") is not None:
                raise RuntimeError(f"R3R_RSS_CHILD_FAILED:{backend}:{memory['returncode']}")
            check_budget("after_rss_child")
            if memory["result"]["trial"]["identity"] != reference:
                raise ArithmeticError(f"R3R_RSS_DIFFERENTIAL:{backend}")
        receipt["lane_binary64_trace"] = trace_lane_ratios(
            args.native_stream, inputs, args.block_rows, args.output_dir)
        if receipt["lane_binary64_trace"]["identity"] != reference:
            raise ArithmeticError("R3R_INSTRUMENTED_REPLAY_DIFFERENTIAL")
        after = arrays_identity(inputs)
        if after != before:
            raise ArithmeticError("R3R_INPUT_ARRAYS_CHANGED")
        receipt["input_arrays_before_after"] = {"status": "UNCHANGED", "identities": before}
        for key, identity in receipt["inputs"]["files"].items():
            if sha256(getattr(args, key)) != identity["sha256"]:
                raise ArithmeticError(f"R3R_INPUT_FILE_CHANGED:{key}")
        if source_identity(args.source_sha) != receipt["source"]:
            raise ArithmeticError("R3R_SOURCE_CHANGED_DURING_BENCHMARK")
        check_budget("final_verification")
        receipt["summary"] = summarize(receipt["trials"])
        receipt["differential"] = {"status": "PASS", "compared": "canonical verdict JSON, all maxima float.hex, guard labels"}
        receipt["status"] = "PASS_SAVED_STREAM_AUDIT_ONLY"
        receipt["claim_limits"] = {"new_production_speedup": "NOT_MEASURED",
                                    "physical_validity": "UNCHANGED_NOT_ESTABLISHED",
                                    "global_convergence": "NOT_RUN", "rei_activation": False}
    except BaseException as exc:
        receipt["status"] = "FAIL"
        receipt["failure"] = {"type": type(exc).__name__, "message": str(exc)}
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        receipt["resources"] = {"process_tree_cpu_s": total_cpu_s(),
                                "wall_s_since_module_start": time.monotonic() - START_WALL,
                                "parent_cumulative_peak_rss_bytes": peak_rss_bytes(),
                                "parent_rss_scope": "process lifetime; not a per-backend comparison"}
        with (args.output_dir / "benchmark.json").open("x") as out:
            json.dump(receipt, out, indent=2, sort_keys=True, allow_nan=False)
            out.write("\n")
    print(json.dumps({"status": receipt["status"], "receipt": str(args.output_dir / "benchmark.json")}, sort_keys=True))
    return 0 if receipt["status"] == "PASS_SAVED_STREAM_AUDIT_ONLY" else 1


if __name__ == "__main__":
    raise SystemExit(main())
