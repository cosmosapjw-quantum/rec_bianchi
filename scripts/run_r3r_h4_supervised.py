#!/usr/bin/env python3
"""Source-bound R3R h4 pilot: 1..32 new steps, 60 CPU/180 wall s, 2 GiB.

The original R3Q worker remains frozen. This entry point selects only its
native-stream comparator, records the binding, and reuses the R3P/R3O
whole-process-tree Budget. The frozen worker's 32-step smoke bound is stricter
than the user's 128-step ceiling. No event/full allocation is exposed.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import resource
import signal
import subprocess
import sys
import time


def cpu():
    own, child = resource.getrusage(resource.RUSAGE_SELF), resource.getrusage(resource.RUSAGE_CHILDREN)
    return own.ru_utime + own.ru_stime + child.ru_utime + child.ru_stime


ENTRY_CLOCK = (cpu(), time.monotonic())
ROOT = Path(__file__).resolve().parents[1]
CPU_CAP, WALL_CAP, MEMORY_BYTES = 60., 180., 2 * 1024**3
MANIFEST = "research/rec_r3q_h4_continuation_20261020/SOURCE_CLOSURE.json"
CHECKPOINT = "research/rec_r3o_grid_frontiers_20261019/h4_start_002/python_h4_full_start.npz"
ADDED_RUNTIME = ("scripts/run_r3r_h4_supervised.py", "scripts/r3r_stream_audit.py",
                 "scripts/build_r3o_rust.py", MANIFEST)
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT / "scripts"))


def digest(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def dump_new(path, obj):
    with Path(path).open("x") as stream:
        json.dump(obj, stream, sort_keys=True, indent=2, allow_nan=False)
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())


def parse_args(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--expected-commit", required=True)
    ap.add_argument("--new-allocation-id", required=True)
    ap.add_argument("--evidence-dir", required=True, type=Path)
    ap.add_argument("--backend", choices=("legacy", "numpy"), default="legacy")
    ap.add_argument("--steps", type=int, default=16)
    args = ap.parse_args(argv)
    if not re.fullmatch(r"[0-9a-f]{40}", args.expected_commit):
        ap.error("--expected-commit must be the full lowercase Git SHA")
    if not args.new_allocation_id.strip() or "CLOSED" in args.new_allocation_id.upper():
        ap.error("use a fresh allocation identifier")
    if not 1 <= args.steps <= 32:
        ap.error("--steps must be 1..32; frozen smoke bound, event/full mode unavailable")
    return args


class InheritedLimits:
    """Clamp a module's limit requests without changing global resource APIs."""
    def __init__(self, original, records):
        self.original, self.records = original, records

    def __getattr__(self, name):
        return getattr(self.original, name)

    def setrlimit(self, kind, requested):
        inherited = self.original.getrlimit(kind)
        def smallest(*values):
            finite = [x for x in values if x != self.original.RLIM_INFINITY]
            return min(finite) if finite else self.original.RLIM_INFINITY
        hard = smallest(requested[1], inherited[1])
        soft = smallest(requested[0], inherited[0], hard)
        self.original.setrlimit(kind, (soft, hard))
        self.records.append({"kind": kind, "requested": list(requested),
                             "inherited": list(inherited), "applied": [soft, hard]})


def bind_source(expected_commit):
    """Match every frozen closure byte and each new runtime file to Git."""
    def git(*argv):
        return subprocess.check_output(["git", *argv], cwd=ROOT)
    head = git("rev-parse", "HEAD").decode().strip()
    if head != expected_commit:
        raise ValueError("R3R_EXPECTED_COMMIT_MISMATCH")
    entries = {}
    for record in git("ls-tree", "-rz", expected_commit).split(b"\0"):
        if record:
            prefix, name = record.split(b"\t", 1)
            mode, kind, blob = prefix.decode().split()
            entries[name.decode()] = (mode, kind, blob)
    manifest = json.loads((ROOT / MANIFEST).read_text())
    hashes = {}
    for name in sorted(set(manifest["files"]) | set(ADDED_RUNTIME)):
        path = ROOT / name
        data = path.read_bytes()
        blob = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
        expected = entries.get(name)
        if path.is_symlink() or expected is None or expected[1] != "blob" or blob != expected[2]:
            raise ValueError("R3R_RUNTIME_NOT_AT_EXPECTED_COMMIT:" + name)
        hashes[name] = hashlib.sha256(data).hexdigest()
        if name in manifest["files"] and hashes[name] != manifest["files"][name]:
            raise ValueError("R3R_FROZEN_SOURCE_CHANGED:" + name)
    return {"source_commit": head, "source_tree": git("rev-parse", "HEAD^{tree}").decode().strip(),
            "source_sha256": hashes, "frozen_files_verified": len(manifest["files"]),
            "source_closure_manifest_sha256": hashes[MANIFEST],
            "checkpoint_sha256": digest(ROOT / CHECKPOINT)}


def run_worker(argv=None):
    """Internal worker entered only by the bounded public launcher."""
    args = parse_args(argv)
    out = args.evidence_dir.resolve()
    record = {"schema": "rec.r3r.runtime-binding.v1", "status": "FAILED",
              "backend": args.backend, "requested_steps": args.steps,
              "allocation_id": args.new_allocation_id, "limit_clamps": [],
              "comparator_calls": [], "first_failure": None}
    code = 2
    worker = None
    original_compare = original_resource = None
    before = None
    try:
        prefix = out / "pycache-worker"
        if sys.pycache_prefix != str(prefix) or not prefix.is_dir() or any(prefix.iterdir()):
            raise ValueError("R3R_FRESH_WORKER_PYCACHE_PREFIX_REQUIRED")
        record["worker_entry_limits"] = {
            "cpu": list(resource.getrlimit(resource.RLIMIT_CPU)),
            "address_space": list(resource.getrlimit(resource.RLIMIT_AS)),
            "pycache_prefix": sys.pycache_prefix, "prefix_empty_at_entry": True,
            "dont_write_bytecode": sys.dont_write_bytecode}
        before = bind_source(args.expected_commit)
        record["before"] = before
        import verify_r3q_h4_continuation as worker
        import r3r_stream_audit as candidate
        record["environment"] = {
            "python": sys.version, "executable": sys.executable,
            "platform": platform.platform(), "hostname": platform.node(),
            "machine": platform.machine(), "libc": list(platform.libc_ver()),
            "numpy": candidate.np.__version__,
            "initial_affinity": sorted(os.sched_getaffinity(0)),
            "thread_environment": {key: os.environ.get(key) for key in
                ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS")},
            "gcc": subprocess.check_output(["gcc", "--version"], text=True).splitlines()[0]}
        original_compare, original_resource = worker.compare_native_stream, worker.resource
        worker.resource = InheritedLimits(original_resource, record["limit_clamps"])
        def compare(*positional, **keyword):
            stats = {}
            t0, w0 = time.process_time(), time.perf_counter()
            try:
                if args.backend == "numpy":
                    return candidate.compare_native_stream(*positional, **keyword, stats=stats)
                return original_compare(*positional, **keyword)
            finally:
                record["comparator_calls"].append({
                    "cpu_s": time.process_time()-t0, "wall_s": time.perf_counter()-w0,
                    "scope": "COMPLETE_STREAM_AUDIT_OPEN_PARSE_ALLOCATE_COMPARE_VERDICT",
                    "stats": stats})
        worker.compare_native_stream = compare
        original_argv = sys.argv
        sys.argv = [str(ROOT / "scripts/verify_r3q_h4_continuation.py"),
                    "--supervised", "--checkpoint", str(ROOT / CHECKPOINT),
                    "--evidence-dir", str(out / "worker"), "--mode", "smoke",
                    "--new-allocation-id", args.new_allocation_id,
                    "--max-extra-accepted", str(args.steps)]
        try:
            worker.main()
        finally:
            sys.argv = original_argv
        record["status"] = "WORKER_RETURNED"
        code = 0
    except BaseException as exc:
        record["first_failure"] = {"type": type(exc).__name__, "message": str(exc)}
    finally:
        if worker is not None and original_compare is not None:
            worker.compare_native_stream, worker.resource = original_compare, original_resource
        try:
            after = bind_source(args.expected_commit)
            record["after"] = after
            if before is None or before != after:
                raise ValueError("R3R_SOURCE_IDENTITY_CHANGED_OR_NOT_BOUND")
            record["source_identity"] = "UNCHANGED"
        except BaseException as exc:
            code = 2
            record["status"] = "FAILED"
            record["source_identity_failure"] = {"type": type(exc).__name__, "message": str(exc)}
        record["exit_code"] = code
        dump_new(out / "R3R_BINDING.json", record)
    return code


def supervise(args, argv, start_clock):
    out = args.evidence_dir.resolve()
    out.mkdir(parents=True, exist_ok=False)
    # -B disables writes, but does not reject an existing stale .pyc. Both
    # processes use create-only empty prefixes before any project import.
    for name in ("pycache-supervisor", "pycache-worker"):
        (out / name).mkdir(exist_ok=False)
    sys.pycache_prefix = str(out / "pycache-supervisor")
    import build_r3o_rust as budget_module
    budget = budget_module.Budget(out, cpu_s=CPU_CAP, wall_s=WALL_CAP, memory_bytes=MEMORY_BYTES)
    budget.start_cpu, budget.start_wall = start_clock
    report = {"schema": "rec.r3r.h4-supervision.v1", "status": "FAILED",
              "allocation_id": args.new_allocation_id, "backend": args.backend,
              "requested_steps": args.steps, "historical_budget": "CLOSED_HOLD_NOT_RESET",
              "rei_activation": False, "expected_commit": args.expected_commit,
              "limits": {"cpu_s": CPU_CAP, "wall_s": WALL_CAP,
                         "per_process_address_space_bytes": MEMORY_BYTES, "max_steps": 32,
                         "user_step_ceiling": 128},
              "scope": "SUPERVISOR_AND_COMPLETE_WORKER_TREE_WITH_PREFLIGHT_COMPILE_AUDIT_CLOSEOUT",
              "clock_start": "ENTRY_CLOCK_AFTER_STDLIB_IMPORTS; interpreter startup remains within inherited process limits",
              "memory_scope": "PER_PROCESS_AS_AND_POLLED_WORKER_TREE_RSS; SUPERVISOR_RSS_NOT_IN_POLLED_TOTAL",
              "first_failure": None, "limit_clamps": []}
    report["preexec_clamp_record_scope"] = "FORK_LOCAL; actual inherited worker values are in R3R_BINDING.json"
    report["fresh_pycache_prefixes"] = {
        "supervisor": str(out / "pycache-supervisor"),
        "worker": str(out / "pycache-worker"), "writes_disabled": sys.dont_write_bytecode}
    code = 2
    try:
        budget.check()
        report["source_binding"] = bind_source(args.expected_commit)
        env = os.environ.copy()
        env.update({key: "1" for key in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS",
                                         "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS")})
        command = [sys.executable, "-B", "-X", "pycache_prefix=" + str(out / "pycache-worker"), "-c",
                   "import sys;sys.path.insert(0," + repr(str(ROOT / "scripts")) +
                   ");from run_r3r_h4_supervised import run_worker;raise SystemExit(run_worker())",
                   *argv]
        original_resource = budget_module.resource
        budget_module.resource = InheritedLimits(original_resource, report["limit_clamps"])
        try:
            budget.run(command, cwd=ROOT, env=env, label="worker")
        finally:
            budget_module.resource = original_resource
        verification = json.loads((out / "worker/verification.json").read_text())
        binding = json.loads((out / "R3R_BINDING.json").read_text())
        report["worker_verification_sha256"] = digest(out / "worker/verification.json")
        report["runtime_binding_sha256"] = digest(out / "R3R_BINDING.json")
        report["worker_status"] = verification["status"]
        report["actual_accepted_steps"] = verification.get("python_result", {}).get("extra_accepted")
        if (verification["status"] != "SMOKE_ONLY" or verification.get("first_failure") is not None
                or binding["exit_code"] != 0 or binding.get("source_identity") != "UNCHANGED"
                or verification.get("same_h_parity", {}).get("status") != "PASS"
                or report["actual_accepted_steps"] != args.steps):
            raise ValueError("R3R_WORKER_OR_IDENTITY_GATE")
        budget.check()
        report["status"] = "COMPLETED_SCOPED_SMOKE"
        report["scientific_admission"] = "HOLD_GLOBAL_CONVERGENCE_AND_PHYSICAL_VALIDITY"
        code = 0
    except BaseException as exc:
        report["first_failure"] = {"type": type(exc).__name__, "message": str(exc)}
    finally:
        report["commands"] = budget.commands
        code = budget_module.finalize_resource_record(report, budget, code, "R3R_PILOT")
        dump_new(out / "supervision.json", report)
    return report, code


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    start = ENTRY_CLOCK
    old_handler, old_timer = signal.getsignal(signal.SIGALRM), signal.getitimer(signal.ITIMER_REAL)
    old_pycache_prefix = sys.pycache_prefix
    def expired(*_):
        raise TimeoutError("R3R_WHOLE_LAUNCH_WALL_CAP")
    signal.signal(signal.SIGALRM, expired)
    remaining = max(.001, WALL_CAP - (time.monotonic()-start[1]))
    if old_timer[0] > 0:
        remaining = min(remaining, old_timer[0])
    signal.setitimer(signal.ITIMER_REAL, remaining)
    try:
        limits = InheritedLimits(resource, [])
        limits.setrlimit(resource.RLIMIT_CPU, (60, 60))
        limits.setrlimit(resource.RLIMIT_AS, (MEMORY_BYTES, MEMORY_BYTES))
        args = parse_args(argv)
        report, code = supervise(args, argv, start)
        print(json.dumps({"status": report["status"], "exit_code": code,
                          "supervision": str(args.evidence_dir.resolve() / "supervision.json")}))
        return code
    finally:
        sys.pycache_prefix = old_pycache_prefix
        signal.setitimer(signal.ITIMER_REAL, 0.)
        signal.signal(signal.SIGALRM, old_handler)
        if old_timer[0] > 0:
            signal.setitimer(signal.ITIMER_REAL, max(.001, old_timer[0]-(time.monotonic()-start[1])), old_timer[1])


if __name__ == "__main__":
    raise SystemExit(main())

