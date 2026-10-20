#!/usr/bin/env python3
"""Public whole-launch R3P U6 budget; accepts the audited runner's same options.

The existing R3O Budget monitors the complete worker and descendants, including
source binding, input hashes, original C work, Rust checks and worker closeout.
60 CPU seconds / 180 wall seconds / 2 GiB include the unchanged 2 CPU / 3 wall
second final-receipt reserve. No Rust compilation, cap increase or allocation
occurs; the unchanged worker still compiles the original C verifier. Memory
uses per-process RLIMIT_AS plus polled child-tree RSS, not an exact aggregate
of supervisor and child memory.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import resource
import signal
import sys
import time

# Capture before importing the budget helper or numerical worker/parser.
def _cpu():
    own, child = resource.getrusage(resource.RUSAGE_SELF), resource.getrusage(resource.RUSAGE_CHILDREN)
    return own.ru_utime + own.ru_stime + child.ru_utime + child.ru_stime


ENTRY_CLOCK = (_cpu(), time.monotonic())
ROOT = Path(__file__).resolve().parents[1]
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT / "scripts"))
import build_r3o_rust as budget_support
from build_r3o_rust import Budget, dump_new, finalize_resource_record, sha256

CPU_CAP, WALL_CAP, MEMORY_BYTES = 60., 180., 2*1024**3


def worker_command(argv):
    # Import the programmatic worker API: executing the script as __main__
    # intentionally goes back through this supervisor.
    code = ("import sys; sys.path.insert(0, " + repr(str(ROOT / "scripts")) + "); "
            "from run_r3p_u6_audited import main; main()")
    return [sys.executable, "-B", "-c", code, *argv]


def supervise(args, argv, *, start_clock=None):
    """Run one bounded worker; programmatic callers supply validated CLI args."""
    start_cpu, start_wall = (_cpu(), time.monotonic()) if start_clock is None else start_clock
    evidence = Path(args.evidence_dir).resolve()
    out = evidence.parent / (evidence.name + ".r3p_supervision")
    out.mkdir(parents=True, exist_ok=False)
    budget = Budget(out, cpu_s=CPU_CAP, wall_s=WALL_CAP, memory_bytes=MEMORY_BYTES)
    budget.start_cpu, budget.start_wall = start_cpu, start_wall
    record = {"schema": "rec.r3p.u6-supervision.v1", "status": "FAILED",
              "limits": {"cpu_s": CPU_CAP, "wall_s": WALL_CAP, "memory_bytes": MEMORY_BYTES},
              "limits_scope": "SUPERVISOR_AND_COMPLETE_WORKER_PROCESS_TREE_INCLUDING_PREFLIGHT_AND_CLOSEOUT",
              "memory_scope": {
                  "address_space": "PER_PROCESS_RLIMIT_AS",
                  "rss": "POLLED_WORKER_AND_DESCENDANT_RSS",
                  "supervisor_rss_in_polled_total": False,
                  "exact_aggregate_parent_plus_children_memory": False},
              "measurement_exclusion": "FINAL_SUPERVISOR_RECEIPT_SERIALIZATION_FSYNC_ONLY_RESERVED",
              "inherited_process_limits": {
                  "cpu": list(resource.getrlimit(resource.RLIMIT_CPU)),
                  "address_space": list(resource.getrlimit(resource.RLIMIT_AS))},
              "historical_allocation": "CLOSED_HOLD_NOT_RESET",
              "expected_commit": args.expected_commit, "requested_steps": args.steps,
              "allocation_id": args.new_allocation_id,
              "scientific_status": "READ_ORIGINAL_VERIFICATION_AND_WORKER_RECEIPTS",
              "worker_receipt": str(evidence.parent / (evidence.name + ".r3p_execution.json")),
              "first_failure": None}
    code = 2
    try:
        budget.check()
        env = os.environ.copy()
        env.update({name: "1" for name in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS",
                    "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "RAYON_NUM_THREADS")})
        # Also clamp Budget's child preexec limits if an enclosing executor
        # supplied a hard limit below its computed remaining allowance. This
        # changes no Budget clock, threshold, reserve, monitoring or kill rule.
        from run_r3p_u6_audited import InheritedResourceLimits
        original_resource = budget_support.resource
        budget_support.resource = InheritedResourceLimits(original_resource, {})
        try:
            budget.run(worker_command(argv), cwd=ROOT, env=env, label="worker")
        finally:
            budget_support.resource = original_resource
        worker = Path(record["worker_receipt"])
        # The child has already authenticated the complete source/input/build
        # closure and written its receipts, all inside Budget.run's interval.
        record["worker_receipt_sha256"] = sha256(worker)
        budget.check()
        record["status"] = "WORKER_RETURNED_WITHIN_SUPERVISED_BUDGET"
        code = 0
    except BaseException as exc:
        record["first_failure"] = {"type": type(exc).__name__, "message": str(exc)}
    finally:
        record["commands"] = budget.commands
        code = finalize_resource_record(record, budget, code, "R3P_U6_WHOLE_LAUNCH")
        dump_new(out / "supervision.json", record)
    return record, code


def main(argv=None):
    # The wall alarm covers parser imports and supervisor closeout too; the
    # Budget work deadline is 177 s and preserves 3 s for the final receipt.
    argv = list(sys.argv[1:] if argv is None else argv)
    start = ENTRY_CLOCK
    previous_handler = signal.getsignal(signal.SIGALRM)
    previous_timer = signal.getitimer(signal.ITIMER_REAL)

    def expired(*_):
        raise TimeoutError("R3P_WHOLE_LAUNCH_WALL_CAP")

    signal.signal(signal.SIGALRM, expired)
    remaining = WALL_CAP - (time.monotonic() - start[1])
    if previous_timer[0] > 0:
        remaining = min(remaining, previous_timer[0])
    signal.setitimer(signal.ITIMER_REAL, max(.001, remaining))
    try:
        # Bound the supervisor itself as well as Budget's child/descendants.
        # A lower inherited limit is preserved; never attempt to raise it.
        for kind, requested in ((resource.RLIMIT_CPU, 60), (resource.RLIMIT_AS, MEMORY_BYTES)):
            soft, hard = resource.getrlimit(kind)
            effective_hard = min(requested, hard) if hard != resource.RLIM_INFINITY else requested
            effective_soft = min(effective_hard, soft) if soft != resource.RLIM_INFINITY else effective_hard
            resource.setrlimit(kind, (effective_soft, effective_hard))
        from run_r3p_u6_audited import parse_args
        args = parse_args(argv)
        record, code = supervise(args, argv, start_clock=start)
        print(json.dumps({"status": record["status"], "exit_code": code,
               "supervisor_receipt": str(Path(args.evidence_dir).resolve().parent /
                    (Path(args.evidence_dir).name + ".r3p_supervision") / "supervision.json")},
                    sort_keys=True, allow_nan=False))
        return code
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0.)
        signal.signal(signal.SIGALRM, previous_handler)
        if previous_timer[0] > 0:
            elapsed = time.monotonic() - start[1]
            signal.setitimer(signal.ITIMER_REAL, max(.001, previous_timer[0] - elapsed), previous_timer[1])


if __name__ == "__main__":
    raise SystemExit(main())
