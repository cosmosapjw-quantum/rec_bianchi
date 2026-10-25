"""One measured H5 subprocess within the current 90 CPU-s / 600 wall-s cap."""
from __future__ import annotations
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import resource
import subprocess
import sys
import time

UNIT = Path(__file__).resolve().parents[1]
FREEZE = UNIT.parent / "EXECUTION_FREEZE_HD_H5.json"


def save(path, data):
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("label")
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    command = args.command
    if command and command[0] == "--":
        command = command[1:]
    if not command:
        raise ValueError("COMMAND_REQUIRED")
    freeze = json.loads(FREEZE.read_text())
    limits = freeze["budgets"]["H5"]
    records = list((UNIT / "evidence" / "execution").glob("*/RECEIPT.json"))
    spent = [json.loads(p.read_text()) for p in records]
    cpu_used = sum(x["child_inclusive_cpu_seconds"] for x in spent)
    wall_used = sum(x["child_wall_seconds"] for x in spent)
    cpu_left, wall_left = limits["cpu_seconds"] - cpu_used, limits["execution_wall_seconds"] - wall_used
    if cpu_left < 1 or wall_left <= 0:
        raise ValueError("H5_OWN_BUDGET_EXHAUSTED")
    output = UNIT / "evidence" / "execution" / args.label
    output.mkdir(parents=True, exist_ok=False)
    env = os.environ.copy()
    for key in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS",
                "NUMEXPR_NUM_THREADS", "BLIS_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
        env[key] = "1"
    cpu_cap = max(1, min(30, math.floor(cpu_left)))
    wall_cap = min(120, wall_left)
    def boundary():
        resource.setrlimit(resource.RLIMIT_CPU, (cpu_cap, cpu_cap))
        resource.setrlimit(resource.RLIMIT_AS, (1073741824, 1073741824))
        resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
    identities = {}
    for path in sorted(UNIT.rglob("*")):
        if path.is_file() and (path.suffix == ".py" or path.parent.name == "inputs"):
            payload = path.read_bytes()
            identities[str(path.relative_to(UNIT))] = {
                "bytes": len(payload), "sha256": hashlib.sha256(payload).hexdigest()}
    preexec = {"argv": command, "cwd": os.getcwd(), "limits": {
        "cpu_seconds": cpu_cap, "wall_seconds": wall_cap,
        "RLIMIT_AS_bytes": 1073741824, "threads": 1},
        "prior_measured_cpu_seconds": cpu_used, "prior_measured_wall_seconds": wall_used,
        "freeze_sha256": hashlib.sha256(FREEZE.read_bytes()).hexdigest(),
        "code_and_current_input_identities": identities,
        "git_head": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()}
    save(output / "PREEXEC.json", preexec)
    start = time.perf_counter()
    before = resource.getrusage(resource.RUSAGE_CHILDREN)
    timeout = False
    with (output / "stdout.txt").open("wb") as out, (output / "stderr.txt").open("wb") as err:
        child = subprocess.Popen(command, env=env, stdout=out, stderr=err,
                                 preexec_fn=boundary)
        try:
            code = child.wait(timeout=wall_cap)
        except subprocess.TimeoutExpired:
            timeout = True
            child.kill()
            code = child.wait()
    after = resource.getrusage(resource.RUSAGE_CHILDREN)
    cpu = after.ru_utime + after.ru_stime - before.ru_utime - before.ru_stime
    wall = time.perf_counter() - start
    receipt = {"returncode": code, "timed_out": timeout,
               "child_inclusive_cpu_seconds": cpu, "child_wall_seconds": wall,
               "child_max_RSS_KiB": after.ru_maxrss,
               "cumulative_H5_cpu_seconds": cpu_used + cpu,
               "cumulative_H5_wall_seconds": wall_used + wall,
               "within_H5_cumulative_cap": cpu_used + cpu <= limits["cpu_seconds"] and wall_used + wall <= limits["execution_wall_seconds"],
               "known_cost_scope": "This child including its imports and I/O; model/tool/network and earlier read-only intake cost not measured and not zero",
               "observed_runtime_model_identity": "NOT_OBSERVABLE",
               "stdout": "stdout.txt", "stderr": "stderr.txt"}
    save(output / "RECEIPT.json", receipt)
    print(json.dumps(receipt, sort_keys=True))
    return code if code >= 0 else 1


if __name__ == "__main__":
    sys.exit(main())
