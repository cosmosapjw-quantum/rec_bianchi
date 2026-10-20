#!/usr/bin/env python3
"""Own the R3Q worker process group and preserve its terminal resource receipt.

A fresh allocation is 60 CPU/180 wall seconds for smoke or 600/900 for the
first h4 event frontier. Both include compilation, comparison and closeout.
The event allocation is a new campaign, never a reset of historical U5 caps.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import resource
import signal
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]


def read_verification(path):
    raw = None
    try:
        raw = Path(path).read_bytes()
        worker = json.loads(raw)
        if not isinstance(worker, dict):
            raise ValueError("worker verification must be an object")
        return worker, None, hashlib.sha256(raw).hexdigest()
    except (OSError, ValueError, UnicodeError) as exc:
        return {}, {"type": type(exc).__name__, "message": str(exc)}, (
            hashlib.sha256(raw).hexdigest() if raw is not None else None)


def worker_completed(worker, process):
    return (process["returncode"] == 0 and process["failure"] is None
            and worker.get("first_failure") is None
            and worker.get("status") in (
                "SMOKE_ONLY", "HOLD_CAP_BEFORE_EVENT_PLUS_TWO", "PASS_PENDING_INDEPENDENT_REVIEW"))


def run_owned(command, cwd, stdout, stderr, wall_seconds):
    """Return a receipt even when a worker exits before writing verification."""
    start = time.monotonic()
    before = resource.getrusage(resource.RUSAGE_CHILDREN)
    p = None
    error = None
    killed = False
    try:
        with Path(stdout).open("xb") as so, Path(stderr).open("xb") as se:
            p = subprocess.Popen(command, cwd=cwd, stdout=so, stderr=se,
                                 start_new_session=True)
            p.wait(timeout=wall_seconds)
    except BaseException as exc:
        error = {"type": type(exc).__name__, "message": str(exc)}
    finally:
        # Kill descendants as well after a failed/timed-out direct child.
        if p is not None and (error is not None or p.returncode):
            try:
                os.killpg(p.pid, signal.SIGKILL)
                killed = True
            except ProcessLookupError:
                pass
            p.wait()
    after = resource.getrusage(resource.RUSAGE_CHILDREN)
    return {"returncode": None if p is None else p.returncode, "failure": error,
            "wall_s": time.monotonic()-start, "process_group_owned": True,
            "process_group_kill_sent": killed,
            "waited_children_cpu_s": after.ru_utime+after.ru_stime-before.ru_utime-before.ru_stime,
            "waited_children_peak_rss_bytes": after.ru_maxrss*1024,
            "peak_rss_scope": "maximum waited child, not simultaneous process-tree sum"}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--evidence-dir", required=True, type=Path)
    p.add_argument("--new-allocation-id", required=True)
    p.add_argument("--mode", choices=("smoke", "event"), default="smoke")
    p.add_argument("--steps", type=int, default=16, help="smoke steps, 1..32")
    p.add_argument("--checkpoint", type=Path, default=ROOT / "research/rec_r3o_grid_frontiers_20261019/h4_start_002/python_h4_full_start.npz")
    args = p.parse_args()
    if not args.new_allocation_id.strip() or "CLOSED" in args.new_allocation_id.upper():
        p.error("use a fresh campaign allocation identifier")
    if not 1 <= args.steps <= 32:
        p.error("--steps must be 1..32")
    out = args.evidence_dir.resolve()
    out.mkdir(parents=True, exist_ok=False)
    cpu, wall = (60, 180) if args.mode == "smoke" else (600, 900)
    command = [sys.executable, "-B", str(ROOT / "scripts/verify_r3q_h4_continuation.py"),
               "--supervised", "--checkpoint", str(args.checkpoint.resolve()),
               "--evidence-dir", str(out / "worker"), "--mode", args.mode,
               "--new-allocation-id", args.new_allocation_id,
               "--max-extra-accepted", str(args.steps if args.mode == "smoke" else 8192)]
    receipt = {"schema": "rec.r3q.h4-supervised.v1", "status": "STARTED",
               "command": command, "new_allocation_id": args.new_allocation_id,
               "historical_budget": "CLOSED_HOLD_NOT_RESET", "rei_activation": False,
               "allocation": {"total_cpu_s": cpu, "total_wall_s": wall,
                              "address_space_bytes_per_process": 2*1024**3, "threads": 1,
                              "worker_closeout_cpu_s_in_total": 5,
                              "worker_closeout_wall_s_in_total": 12,
                              "supervisor_closeout_wall_s_in_total": 2}}
    (out / "STARTED.json").write_text(json.dumps(receipt, indent=2)+"\n")
    own_start = time.process_time()
    start = time.monotonic()
    receipt["process"] = run_owned(command, ROOT, out/"worker.stdout", out/"worker.stderr", wall-2)
    verification = out / "worker/verification.json"
    worker, read_failure, verification_sha = read_verification(verification)
    receipt["worker_verification_read_failure"] = read_failure
    receipt["worker_status"] = worker.get("status", "MISSING_TERMINAL_VERIFICATION")
    receipt["worker_verification_sha256"] = verification_sha
    used_cpu = time.process_time()-own_start+receipt["process"]["waited_children_cpu_s"]
    receipt["total_cpu_s_including_supervisor"] = used_cpu
    receipt["total_wall_s_including_supervisor"] = time.monotonic()-start
    passed = (read_failure is None and worker_completed(worker, receipt["process"])
              and used_cpu < cpu and receipt["total_wall_s_including_supervisor"] < wall)
    receipt["status"] = "COMPLETED_SCOPED" if passed else "HOLD_EXECUTION_OR_RESOURCE"
    receipt["scientific_admission"] = "HOLD_PENDING_INDEPENDENT_REVIEW"
    with (out/"TERMINAL.json").open("x") as f:
        json.dump(receipt, f, sort_keys=True, indent=2, allow_nan=False)
        f.write("\n")
    print(json.dumps({"status": receipt["status"], "worker_status": receipt["worker_status"]}))
    return 0 if passed else 2


if __name__ == "__main__":
    raise SystemExit(main())
