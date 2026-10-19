#!/usr/bin/env python3
"""Measure the unchanged owned-U6 verifier; optionally use lossless stored NPZ.

Smoke/pilot collect missing phase costs. Full mode retains the original 5210
steps and requires the executor's already-valid allocation and recovery reserve.
This command creates neither an allocation nor a full-run admission decision.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import re
import subprocess
import sys

for _key in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ[_key] = "1"
ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "scripts")]

from r3l_u6_cost import PhaseLedger, file_sha256, instrument_verifier

EXTRA_FILES = ("scripts/run_r3l_u6_profiled.py", "scripts/r3l_u6_cost.py")


def bind_profile_source(root, expected_commit):
    from run_r3j_u6_owned import source_binding
    binding = source_binding(Path(root), expected_commit)
    # git diff ignores untracked files: these new adapters must themselves be
    # committed, not merely present next to an otherwise clean old checkout.
    subprocess.run(["git", "-C", str(root), "ls-files", "--error-unmatch", "--", *EXTRA_FILES],
                   capture_output=True, text=True, check=True, timeout=10)
    for name in EXTRA_FILES:
        binding["additional_source_sha256"][name] = file_sha256(Path(root) / name)
    return binding


def step_count(mode, pilot_steps):
    if mode not in ("smoke", "pilot", "full"):
        raise ValueError("U6_PROFILE_MODE")
    if isinstance(pilot_steps, bool) or not isinstance(pilot_steps, int) or not 1 <= pilot_steps <= 128:
        raise ValueError("BOUNDED_PILOT_STEPS_1_TO_128")
    return {"smoke": 3, "pilot": pilot_steps, "full": 5210}[mode]


def execute(verifier, owned_integrator, *, checkpoint, evidence, steps,
            binding, allocation_id, container):
    evidence = Path(evidence).resolve()
    if evidence.exists():
        raise FileExistsError("CREATE_ONLY_EVIDENCE_ALREADY_EXISTS")
    evidence.parent.mkdir(parents=True, exist_ok=True)
    journal = evidence.parent / (evidence.name + ".r3l_phases.jsonl")
    summary = evidence.parent / (evidence.name + ".r3l_profile.json")
    if journal.exists() or summary.exists():
        raise FileExistsError("CREATE_ONLY_PROFILE_ALREADY_EXISTS")
    original_argv = sys.argv[:]
    primary, secondary, report = None, [], None

    def secondary_failure(stage, error):
        secondary.append((stage, error, error.__traceback__))

    try:
        with journal.open("x", encoding="utf-8") as stream:
            ledger = PhaseLedger(stream)
            try:
                ledger.emit({"event": "launch", "utc": datetime.now(timezone.utc).isoformat(),
                             "source": binding, "allocation_id": allocation_id,
                             "historical_allocation": "CLOSED_HOLD_NOT_RESET",
                             "steps_requested": steps, "history_container": container,
                             "cpu_cap_s": 60, "wall_cap_s": 180,
                             "address_limit_bytes": 2 * 1024**3})
                with instrument_verifier(verifier, owned_integrator, ledger, container=container):
                    sys.argv = [str(ROOT / "scripts/verify_r3i_h2_u6_rt_boundary.py"),
                                "--checkpoint", str(Path(checkpoint).resolve()),
                                "--evidence-dir", str(evidence),
                                "--max-extra-accepted", str(steps)]
                    verifier.main()
            except BaseException as exc:
                primary = (exc, exc.__traceback__)
            finally:
                sys.argv = original_argv
            run_error = None if primary is None else {
                "type": type(primary[0]).__name__, "message": str(primary[0])}
            report = {"schema": "rec.r3l.phase-profile.v1", "source": binding,
                      "allocation_id": allocation_id, "requested_steps": steps,
                      "historical_allocation": "CLOSED_HOLD_NOT_RESET",
                      "history_container": container, "run_error": run_error,
                      "execution_status": "failed" if primary else "returned",
                      "scientific_status": "READ_ORIGINAL_VERIFICATION_RECEIPT",
                      "full_run_budget_admission": "NOT_ESTABLISHED_BY_PROFILING",
                      "runtime": {"python": sys.version, "platform": platform.platform(),
                                  "numpy": verifier.np.__version__,
                                  "scipy": importlib.metadata.version("scipy"),
                                  "executor_label": os.environ.get("REC_R3L_EXECUTION_LOCATION", "unspecified"),
                                  "thread_environment": {k: os.environ.get(k) for k in (
                                      "OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS")}}}
            try:
                report["timings"] = ledger.summary()
            except BaseException as error:
                secondary_failure("timing_summary", error)
                report["timings"] = {"accounting_status": "INVALID_PROFILING_ERROR",
                                     "profiling_errors": ledger.profiling_errors}
            verification = evidence / "verification.json"
            try:
                if verification.is_file():
                    report["verification"] = {"path": str(verification),
                                              "sha256": file_sha256(verification)}
                    receipt = json.loads(verification.read_text())
                    report["verification"].update({
                        "status": receipt.get("status"), "first_failure": receipt.get("first_failure"),
                        "python_result": receipt.get("python_result"), "resources": receipt.get("resources"),
                        "same_h_status": receipt.get("same_h_parity", {}).get("status")})
            except BaseException as error:
                secondary_failure("verification_receipt_read", error)
                report.setdefault("verification", {})["read_status"] = "UNREADABLE_PRESERVED"
            report["closeout_errors"] = [{"stage": stage, "type": type(error).__name__, "message": str(error)}
                                         for stage, error, _ in secondary]
            try:
                with summary.open("x", encoding="utf-8") as out:
                    out.write(json.dumps(report, sort_keys=True, indent=2, allow_nan=False) + "\n")
                    out.flush(); os.fsync(out.fileno())
            except BaseException as error:
                secondary_failure("profile_save", error)
            try:
                ledger.emit({"event": "closeout", "profile_sha256": file_sha256(summary) if summary.is_file() else None,
                             "execution_status": report["execution_status"],
                             "closeout_errors": [{"stage": stage, "type": type(error).__name__, "message": str(error)}
                                                 for stage, error, _ in secondary]})
            except BaseException as error:
                secondary_failure("final_journal", error)
    except BaseException as error:
        if primary is None and not secondary:
            primary = (error, error.__traceback__)
        else:
            secondary_failure("journal_or_profile_close", error)
    finally:
        sys.argv = original_argv
    if primary is not None:
        for stage, error, _ in secondary:
            primary[0].add_note(f"Secondary closeout failure ({stage}): {type(error).__name__}: {error}")
        raise primary[0].with_traceback(primary[1])
    if secondary:
        # A successful verifier with a failed profile is still a failed profiling
        # operation; it never silently becomes a successful new run receipt.
        raise secondary[0][1].with_traceback(secondary[0][2])
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--checkpoint", type=Path, required=True)
    parser.add_argument("--evidence-dir", type=Path, required=True)
    parser.add_argument("--expected-commit", required=True)
    parser.add_argument("--new-allocation-id", required=True)
    parser.add_argument("--mode", choices=("smoke", "pilot", "full"), default="pilot")
    parser.add_argument("--pilot-steps", type=int, default=128)
    parser.add_argument("--history-container", choices=("compressed", "stored"), default="compressed")
    args = parser.parse_args(argv)
    if re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,95}", args.new_allocation_id) is None:
        parser.error("new-allocation-id must identify an already-valid allocation")
    n = step_count(args.mode, args.pilot_steps)
    binding = bind_profile_source(ROOT, args.expected_commit)
    import verify_r3i_h2_u6_rt_boundary as verifier
    from full_bianchi_hyrec.trajectory.primordial_2012_owned_u6 import integrate_u6_owned
    report = execute(verifier, integrate_u6_owned, checkpoint=args.checkpoint,
                     evidence=args.evidence_dir, steps=n, binding=binding,
                     allocation_id=args.new_allocation_id, container=args.history_container)
    print(json.dumps(report, sort_keys=True, allow_nan=False))


if __name__ == "__main__":
    main()
