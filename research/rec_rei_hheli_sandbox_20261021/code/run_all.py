#!/usr/bin/env python3
"""Run or reuse the finite campaign, then rebuild its saved-data deliverables.

The default only reads completed trajectories. --execute enables the existing
hash-checked dispatcher, which reuses completed cases and preserves failures.
No scientific equations or campaign identities are defined in this wrapper.
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import uuid

ROOT = Path(__file__).resolve().parents[1]


def rooted(value):
    path = Path(value)
    return path.resolve() if path.is_absolute() else (ROOT / path).resolve()


def write_receipt(path, value):
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps(value, indent=2) + "\n")
    os.replace(temporary, path)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true", help="run only missing cases; complete cases are reused")
    parser.add_argument("--input", default="results/pilot_v2")
    parser.add_argument("--control", default="results/control")
    parser.add_argument("--output", default="results")
    parser.add_argument("--figures", default="figures")
    parser.add_argument("--workers", default="auto")
    parser.add_argument("--peer-reservations", action="append", default=[])
    args = parser.parse_args(argv)
    source, control, output, figures = map(rooted, (args.input, args.control, args.output, args.figures))
    commands = []
    if args.execute:
        shared = [item for path in args.peer_reservations for item in ("--peer-reservations", str(rooted(path)))]
        for name, manifest, destination in (
            ("main_campaign", "data/CAMPAIGN.json", source),
            ("opacity_off_control", "data/CONTROL_CAMPAIGN.json", control),
        ):
            commands.append((name, [sys.executable, str(ROOT / "code/run_pilot.py"), "--execute",
                "--manifest", str(ROOT / manifest), "--output", str(destination), "--workers", args.workers, *shared]))
    commands.extend([
        ("saved_data_summary", [sys.executable, str(ROOT / "code/summarize_pilot.py"),
            "--input", str(source), "--control", str(control), "--output", str(output)]),
        ("saved_data_figures", [sys.executable, str(ROOT / "code/plot_pilot.py"),
            "--input", str(source), "--control", str(control), "--output", str(figures)]),
    ])
    run_id = uuid.uuid4().hex
    logdir = ROOT / "evidence/pipeline_runs" / run_id
    logdir.mkdir(parents=True, exist_ok=False)
    cache = tempfile.TemporaryDirectory(prefix="hheli-matplotlib-")
    env = dict(os.environ)
    env.update({key: "1" for key in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS")})
    env["MPLCONFIGDIR"] = cache.name
    receipt = {"schema": "rec.hheli.pipeline.v1", "run_id": run_id,
        "started_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "wrapper_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "execute_missing_enabled": args.execute, "steps": [], "status": "RUNNING",
        "scope": "Runnable finite pilot and saved-data reports; no benchmark or global convergence claim."}
    receipt_path = logdir / "RECEIPT.json"
    write_receipt(receipt_path, receipt)
    for name, command in commands:
        result = subprocess.run(command, cwd=ROOT, env=env, text=True, capture_output=True)
        stdout, stderr = logdir / (name + ".stdout.txt"), logdir / (name + ".stderr.txt")
        stdout.write_text(result.stdout); stderr.write_text(result.stderr)
        record = {"name": name, "command": command, "exit_code": result.returncode,
            "stdout": str(stdout.relative_to(ROOT)), "stderr": str(stderr.relative_to(ROOT))}
        if name in {"main_campaign", "opacity_off_control"} and result.returncode == 0:
            dispatch = json.loads(result.stdout)
            record["completion_counts"] = {status: sum(r["status"] == status for r in dispatch["records"])
                for status in ("completed", "complete_reused")}
            record["new_workers"] = dispatch.get("new_workers", dispatch.get("resources", {}).get("workers"))
        receipt["steps"].append(record)
        write_receipt(receipt_path, receipt)
        print(json.dumps({"step": name, "exit_code": result.returncode, "completion_counts": record.get("completion_counts")}), flush=True)
        if result.returncode:
            receipt["status"] = "FAILED_PRESERVED"
            write_receipt(receipt_path, receipt)
            print(result.stderr[-4000:], file=sys.stderr)
            cache.cleanup()
            return result.returncode
    receipt["status"] = "COMPLETE"
    receipt["finished_utc"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    write_receipt(receipt_path, receipt)
    write_receipt(ROOT / "evidence/PIPELINE_LAST_RUN.json", receipt)
    cache.cleanup()
    print(json.dumps({"status": "COMPLETE", "receipt": str((logdir / "RECEIPT.json").relative_to(ROOT))}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
