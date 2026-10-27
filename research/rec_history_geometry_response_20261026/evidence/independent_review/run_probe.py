"""Reviewer child resource boundary; root approval required; no retry."""
import hashlib
import json
import os
from pathlib import Path
import resource
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
for key in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "BLIS_NUM_THREADS"):
    os.environ[key] = "1"
approval = HERE / "ROOT_PROBE_READY.json"
if not approval.exists() or json.loads(approval.read_text()).get("authorization") != "REVIEW_8_ROOTS_READY":
    raise RuntimeError("ROOT_REVIEW_PROBE_AUTHORIZATION_REQUIRED")
receipt = HERE / "PROBE_EXECUTION_RECEIPT.json"
if receipt.exists() or (HERE / "probe001").exists():
    raise RuntimeError("REVIEW_SINGLE_ATTEMPT_NO_RETRY")
code = HERE / "probe_offgrid.py"
snapshot = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in (code, Path(__file__), approval)}
command = [sys.executable, str(code)]
(HERE / "PROBE_COMMAND.json").write_text(json.dumps({"argv": command, "source_sha256": snapshot,
    "cpu_cap_seconds": 5, "wall_cap_seconds": 15, "address_space_bytes": 1073741824,
    "max_roots": 8, "threads": 1}, indent=2) + "\n")


def limits():
    resource.setrlimit(resource.RLIMIT_CPU, (5, 5))
    resource.setrlimit(resource.RLIMIT_AS, (1073741824, 1073741824))
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))


before = resource.getrusage(resource.RUSAGE_CHILDREN)
started = time.monotonic()
timed_out = False
with (HERE / "PROBE_STDOUT.txt").open("wb") as stdout, (HERE / "PROBE_STDERR.txt").open("wb") as stderr:
    child = subprocess.Popen(command, env=os.environ.copy(), stdout=stdout, stderr=stderr, preexec_fn=limits)
    try:
        returncode = child.wait(timeout=15)
    except subprocess.TimeoutExpired:
        timed_out = True
        child.kill()
        returncode = child.wait()
after = resource.getrusage(resource.RUSAGE_CHILDREN)
record = {"returncode": returncode, "timed_out": timed_out,
          "execution_wall_seconds": time.monotonic() - started,
          "child_inclusive_cpu_seconds": after.ru_utime + after.ru_stime - before.ru_utime - before.ru_stime,
          "child_user_cpu_seconds": after.ru_utime - before.ru_utime,
          "child_system_cpu_seconds": after.ru_stime - before.ru_stime,
          "child_highwaterRSS_KiB": after.ru_maxrss,
          "source_unchanged": all(hashlib.sha256((HERE / name).read_bytes()).hexdigest() == digest for name, digest in snapshot.items()),
          "actual_runtime_model": None, "old_replays": 0, "production_code_imports": 0}
receipt.write_text(json.dumps(record, indent=2) + "\n")
print(json.dumps(record))
sys.exit(returncode if returncode >= 0 else 1)
