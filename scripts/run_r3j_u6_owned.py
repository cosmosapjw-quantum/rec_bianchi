#!/usr/bin/env python3
"""Run the existing U6 verifier with an explicitly selected owned-history backend.

The legacy verifier, original C oracle, V6 closure, tolerances, 60 CPU-second
cap and 180 wall-second cap are unchanged. This adapter binds additional
sources and requires the executor to name a NEW allocation after preflight;
it neither resets the old exhausted allocation nor authorizes more compute.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
EXTRA_FILES = (
    "scripts/run_r3j_u6_owned.py",
    "src/full_bianchi_hyrec/trajectory/owned_flrw_history.py",
    "src/full_bianchi_hyrec/trajectory/primordial_2012_owned_u6.py",
    "tests/trajectory/test_owned_flrw_history.py",
)


def source_binding(root: Path, expected_commit: str) -> dict:
    if re.fullmatch(r"[0-9a-f]{40}", expected_commit) is None:
        raise ValueError("EXACT_SOURCE_COMMIT_REQUIRED")
    proc = subprocess.run(["git", "-C", str(root), "rev-parse", "HEAD"],
                          capture_output=True, text=True, check=True, timeout=10)
    actual = proc.stdout.strip()
    if actual != expected_commit:
        raise ValueError("SOURCE_COMMIT_MISMATCH")
    # Read-only check of tracked files. Existing user checkouts are not cleaned.
    subprocess.run(["git", "-C", str(root), "diff", "--quiet", "HEAD", "--"],
                   check=True, timeout=10)
    hashes = {path: hashlib.sha256((root/path).read_bytes()).hexdigest()
              for path in EXTRA_FILES}
    return {"commit": actual, "additional_source_sha256": hashes}


def main(argv=None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--checkpoint", required=True, type=Path)
    parser.add_argument("--evidence-dir", required=True, type=Path)
    parser.add_argument("--expected-commit", required=True)
    parser.add_argument("--new-allocation-id", required=True)
    parser.add_argument("--mode", choices=("smoke", "full"), default="smoke")
    args = parser.parse_args(argv)
    if re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,95}", args.new_allocation_id) is None:
        parser.error("new-allocation-id must be an explicitly recorded fresh allocation")
    binding = source_binding(ROOT, args.expected_commit)
    evidence = args.evidence_dir.resolve()
    if evidence.exists():
        raise FileExistsError("CREATE_ONLY_EVIDENCE_ALREADY_EXISTS")
    evidence.parent.mkdir(parents=True, exist_ok=True)
    journal_path = evidence.parent/(evidence.name+".r3j_execution.jsonl")
    for key in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
        os.environ[key] = "1"
    sys.path[:0] = [str(ROOT/"src"), str(ROOT/"scripts")]
    import verify_r3i_h2_u6_rt_boundary as verifier
    from full_bianchi_hyrec.trajectory.primordial_2012_owned_u6 import integrate_u6_owned
    if verifier.CPU_CAP != 60 or verifier.WALL_CAP != 180:
        raise ValueError("LEGACY_RESOURCE_CAP_DRIFT")
    # Explicit, process-local dependency injection. No source file is rewritten.
    verifier.integrate_u6_rt_boundary = integrate_u6_owned
    n = 3 if args.mode == "smoke" else 5210
    with journal_path.open("x", encoding="utf-8") as journal:
        def record(phase, **extra):
            journal.write(json.dumps({"phase": phase,
                "utc": datetime.now(timezone.utc).isoformat(), **extra},
                sort_keys=True, allow_nan=False)+"\n")
            journal.flush()
            os.fsync(journal.fileno())
        record("START", source=binding, backend="R3J_OWNED_FLRW",
               new_allocation_id=args.new_allocation_id, mode=args.mode,
               max_new_steps=n, old_allocation="CLOSED_HOLD_NOT_RESET",
               cpu_cap_s=60, wall_cap_s=180, input=str(args.checkpoint.resolve()))
        original_argv = sys.argv[:]
        try:
            sys.argv = [str(ROOT/"scripts/verify_r3i_h2_u6_rt_boundary.py"),
                        "--checkpoint", str(args.checkpoint.resolve()),
                        "--evidence-dir", str(evidence),
                        "--max-extra-accepted", str(n)]
            verifier.main()
        except BaseException as error:
            record("EXCEPTION_OR_EXIT", error_type=type(error).__name__,
                   message=str(error), scientific_admission="READ_VERIFICATION_NOT_ASSUMED")
            raise
        else:
            record("RETURNED", scientific_admission="READ_VERIFICATION_NOT_ASSUMED")
        finally:
            sys.argv = original_argv


if __name__ == "__main__":
    main()
