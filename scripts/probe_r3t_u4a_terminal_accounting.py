#!/usr/bin/env python3
"""Lightweight NCP systemd terminal-accounting probe; never starts science."""
from __future__ import annotations
import argparse
import json
import resource
import subprocess
import sys
import tempfile
import time
import uuid
from pathlib import Path

from run_r3t_u4a_supervised import cgroup_terminal_state, launch_registered_service, show

CPU_BURN = "import time; s=time.process_time(); exec('while time.process_time()-s<0.22: pass')"
CASES = {
    "fast_exit": "pass",
    "bootstrap_final_write": CPU_BURN + "; import tempfile; f=tempfile.TemporaryFile(); f.write(b'done'); f.flush(); s=time.process_time(); exec('while time.process_time()-s<0.22: pass')",
    "child_cpu_delayed_exit": "import subprocess,sys,time; s=time.process_time(); exec('while time.process_time()-s<0.10: pass'); p=subprocess.Popen([sys.executable,'-c',\"" + CPU_BURN.replace('"','\\"') + "\"]); p.wait(); time.sleep(0.2)",
    "orphan_child_cleanup": "import subprocess,sys; subprocess.Popen([sys.executable,'-c','import time; time.sleep(3.)']);",
    "nonzero_exit": "raise SystemExit(7)",
    "signal_exit": "import os,signal; os.kill(os.getpid(),signal.SIGTERM)",
    "cpu_cap": "import time; s=time.process_time(); exec('while time.process_time()-s<3.: pass')",
    "wall_cap": "import time; time.sleep(3.)",
}

def run_case(name: str):
    unit = "r3t-account-probe-" + uuid.uuid4().hex[:12] + ".service"
    proof_path = Path(tempfile.gettempdir()) / (unit + ".limits.json")
    limit_code = (
        "import json,resource; limit=2*1024**3; "
        "resource.setrlimit(resource.RLIMIT_AS,(limit,limit)); "
        "assert resource.getrlimit(resource.RLIMIT_AS)==(limit,limit); "
        "open(" + repr(str(proof_path)) + ", 'x').write(json.dumps({'RLIMIT_AS':resource.getrlimit(resource.RLIMIT_AS)}))\n"
    )
    code = limit_code + CASES[name]
    cmd = ["systemd-run", "--no-block", "--remain-after-exit", "--unit=" + unit,
           "--property=Type=exec", "--property=CPUAccounting=yes", "--property=CPUQuota=100%",
           "--property=MemoryAccounting=yes", "--property=MemoryMax=2G",
           sys.executable, "-c", code]
    launch, launch_record = launch_registered_service(cmd)
    launch_record["argv"] = cmd
    start = time.monotonic()
    snapshots = []
    invocation = None
    kill = None
    final = None
    for _ in range(100):
        snap = show(unit)
        if snap.get("InvocationID"):
            if invocation and snap["InvocationID"] != invocation:
                raise RuntimeError("invocation changed")
            invocation = snap["InvocationID"]
        if len(snapshots) < 4 or snap.get("SubState") in ("exited", "failed"):
            snapshots.append(snap)
        if name in ("cpu_cap", "wall_cap") and kill is None:
            raw = snap.get("CPUUsageNSec")
            cpu = int(raw) / 1e9 if raw and raw.isdecimal() else 0.
            wall = time.monotonic() - start
            if (name == "cpu_cap" and cpu >= 0.3) or (name == "wall_cap" and wall >= 0.3):
                p = subprocess.run(["systemctl", "kill", "--signal=KILL", "--kill-whom=all", unit], capture_output=True, text=True, timeout=2)
                kill = {"exit": p.returncode, "stdout": p.stdout, "stderr": p.stderr, "cpu_at_kill_s": cpu, "wall_at_kill_s": wall}
        if invocation and cgroup_terminal_state(snap, unit) == "REMOVED":
            final = snap
            break
        time.sleep(0.05)
    if final is None:
        final = show(unit)
    journal = subprocess.run(["journalctl", "-u", unit, "--no-pager", "-o", "json"], capture_output=True, text=True, timeout=5)
    stop = subprocess.run(["systemctl", "stop", unit], capture_output=True, text=True, timeout=3)
    if final.get("ActiveState") == "failed":
        subprocess.run(["systemctl", "reset-failed", unit], capture_output=True, text=True, timeout=3)
    proof = json.loads(proof_path.read_text()) if proof_path.exists() else None
    return {"case": name, "unit": unit, "launcher": launch_record,
            "per_process_limit_proof": proof,
            "invocation_id": invocation, "snapshots": snapshots, "final": final, "terminal_state": cgroup_terminal_state(final, unit),
            "kill": kill, "stop": {"exit": stop.returncode, "stdout": stop.stdout, "stderr": stop.stderr},
            "journal": {"argv": ["journalctl", "-u", unit, "--no-pager", "-o", "json"], "exit": journal.returncode, "stdout": journal.stdout, "stderr": journal.stderr},
            "elapsed_wall_s": time.monotonic() - start}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    if args.output.exists(): raise SystemExit("output exists")
    result = {"python": sys.version, "cases": [run_case(name) for name in CASES],
              "missing_counter_contract": {"raw": "[not set]", "parsed_cpu": None, "verdict": "CAP_HOLD"}}
    with args.output.open("x") as file:
        json.dump(result, file, indent=2, sort_keys=True)
        file.write("\n")
    print(json.dumps({"output": str(args.output), "cases": [{"case": x["case"], "state": x["terminal_state"], "cpu": x["final"].get("CPUUsageNSec"), "worker_exit": [x["final"].get("ExecMainCode"), x["final"].get("ExecMainStatus")], "kill": x["kill"]} for x in result["cases"]]}, sort_keys=True))

if __name__ == "__main__": main()
