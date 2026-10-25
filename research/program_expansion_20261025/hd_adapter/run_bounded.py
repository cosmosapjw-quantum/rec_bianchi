"""Run only the new HD adapter checks under the separately frozen HD allowance."""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import resource
import subprocess
import sys
import time

UNIT = Path(__file__).resolve().parent
FREEZE = UNIT.parent / "EXECUTION_FREEZE_HD_H5.json"


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def measured_cpu():
    own = resource.getrusage(resource.RUSAGE_SELF)
    child = resource.getrusage(resource.RUSAGE_CHILDREN)
    return own.ru_utime + own.ru_stime + child.ru_utime + child.ru_stime


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--wu-module", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--previous-receipt", type=Path, action="append", default=[])
    parser.add_argument("--diagnostics-only", action="store_true", help="save source-specific diagnostics after a preserved source gate failure")
    parser.add_argument("--case", action="append", default=[], help="changed-dependency unittest method only")
    args = parser.parse_args()
    freeze = json.loads(FREEZE.read_text())
    cpu_cap = freeze["budgets"]["HD"]["cpu_seconds"]
    wall_cap = freeze["budgets"]["HD"]["execution_wall_seconds"]
    memory_cap = freeze["budgets"]["process_max_RSS_bytes"]
    receipts = sorted({path.resolve() for path in (list((UNIT / "raw").glob("**/EXECUTION.json")) + args.previous_receipt)})
    prior = sum(json.loads(path.read_text())["sampled_process_tree_cpu_seconds"] for path in receipts)
    prior_wall = sum(json.loads(path.read_text())["execution_wall_seconds"] for path in receipts)
    if prior >= cpu_cap or prior_wall >= wall_cap:
        raise RuntimeError("HD allowance exhausted; not reset")
    args.output.mkdir(parents=True, exist_ok=False)
    started = time.monotonic()
    os.environ.update({"OMP_NUM_THREADS": "1", "OPENBLAS_NUM_THREADS": "1", "MKL_NUM_THREADS": "1",
                       "NUMEXPR_NUM_THREADS": "1", "PYTHONDONTWRITEBYTECODE": "1"})
    environment = dict(os.environ, REC_HD_SOURCE=str(args.source.resolve()), REC_HD_WU_MODULE=str(args.wu_module.resolve()))
    manifest = {"schema": "REC_HD_BOUNDED_EXECUTION_V1", "created_UTC": datetime.now(timezone.utc).isoformat(),
                "source": {"bytes": args.source.stat().st_size, "sha256": digest(args.source)},
                "WU_source_sha256": digest(args.wu_module), "freeze_sha256": digest(FREEZE),
                "source_code": {path.name: digest(path) for path in UNIT.glob("*.py")},
                "cpu_cap_seconds": cpu_cap, "wall_cap_seconds": wall_cap, "address_space_limit_bytes": memory_cap,
                "threads": 1, "prior_measured_CPU_seconds": prior, "prior_wall_seconds": prior_wall,
                "prior_receipts": {str(path): digest(path) for path in receipts},
                "commands": [], "old_compiler_fixture_runs": 0, "IVP_runs": 0, "native_runs": 0}
    (args.output / "PREEXEC.json").write_text(json.dumps(manifest, indent=2) + "\n")
    commands = [("unittest", [sys.executable, "-m", "unittest", "-v", "test_hd_adapter.py"]),
                ("diagnostics", [sys.executable, str(UNIT / "lamda_hd.py"), str(args.source.resolve()),
                                 "--wu-module", str(args.wu_module.resolve()), "--diagnostics", str((args.output / "diagnostics.json").resolve())])]
    if args.case:
        commands = [("targeted_unittest", [sys.executable, "-m", "unittest", "-v", *args.case])]
    if args.diagnostics_only:
        if args.case:
            raise ValueError("choose diagnostics-only or targeted-case")
        commands = commands[1:]
    status = 0
    for name, command in commands:
        before = resource.getrusage(resource.RUSAGE_CHILDREN)
        remaining_cpu = cpu_cap - prior - measured_cpu()
        remaining_wall = wall_cap - prior_wall - (time.monotonic() - started)
        if remaining_cpu < 1 or remaining_wall <= 0:
            status = 124
            break
        def limits():
            cpu = max(1, min(30, math.floor(remaining_cpu)))
            resource.setrlimit(resource.RLIMIT_CPU, (cpu, cpu))
            resource.setrlimit(resource.RLIMIT_AS, (memory_cap, memory_cap))
        child_start = time.monotonic()
        timed_out = False
        with (args.output / f"{name}.stdout.txt").open("x") as stdout, (args.output / f"{name}.stderr.txt").open("x") as stderr:
            try:
                completed = subprocess.run(command, cwd=UNIT, env=environment, stdout=stdout, stderr=stderr,
                                           timeout=min(60, remaining_wall), preexec_fn=limits, check=False)
                returncode = completed.returncode
            except subprocess.TimeoutExpired:
                returncode, timed_out = 124, True
        after = resource.getrusage(resource.RUSAGE_CHILDREN)
        manifest["commands"].append({"name": name, "argv": command, "cwd": str(UNIT), "returncode": returncode,
                                     "timeout": timed_out, "cpu_seconds": after.ru_utime + after.ru_stime - before.ru_utime - before.ru_stime,
                                     "wall_seconds": time.monotonic() - child_start,
                                     "maxRSS_KiB_cumulative_child_upper_bound": after.ru_maxrss})
        if returncode:
            status = returncode
            break
    manifest.update({"status": "PASS_EXECUTED_TARGETED_UNIT_PENDING_INDEPENDENT_REVIEW" if status == 0 else "FAILED_PRESERVED",
                     "returncode": status, "sampled_process_tree_cpu_seconds": measured_cpu(),
                     "execution_wall_seconds": time.monotonic() - started,
                     "unmeasured_final_receipt_write_CPU": "UNKNOWN_NOT_ZERO",
                     "maxRSS_KiB": max(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss, resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss),
                     "source_identity_unchanged": manifest["source"]["sha256"] == digest(args.source)})
    (args.output / "EXECUTION.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps(manifest, indent=2))
    return status


if __name__ == "__main__":
    raise SystemExit(main())
