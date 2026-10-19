#!/usr/bin/env python3
"""Lossless storage-only comparison on the existing real U4 checkpoint.

No ODE, atomic source, native trajectory or previously completed U4/U5 campaign
is rerun. Timings measure container writes, with readback measured separately.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import resource
import sys
import time
import zipfile

for key in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ[key] = "1"
import numpy as np
from r3l_u6_cost import file_sha256, write_stored_history

ROOT = Path(__file__).resolve().parents[1]
CHECKPOINT = ROOT / "research/rec_r3i_time_refinement_20261016/h2_u4_post_saha_exit_001/ncp_run_001/python_u4_exit.npz"
CHECKPOINT_SHA256 = "7ad1476c78d08218e42ac616dc43d03dd8eb232c44bfb66a8f20a237dcce6943"


def array_identity(value):
    a = np.asarray(value)
    return {"dtype": a.dtype.str, "shape": list(a.shape),
            "sha256_C_order": hashlib.sha256(a.tobytes(order="C")).hexdigest()}


def member_identity(path):
    with zipfile.ZipFile(path) as z:
        return {i.filename: {"bytes": i.file_size,
                             "sha256": hashlib.sha256(z.read(i)).hexdigest()}
                for i in z.infolist()}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--evidence-dir", type=Path, required=True)
    ap.add_argument("--repeats", type=int, default=3)
    args = ap.parse_args(argv)
    if not 1 <= args.repeats <= 3:
        ap.error("repeats outside 1..3")
    ev = args.evidence_dir.resolve(); ev.mkdir(parents=True, exist_ok=False)
    if file_sha256(CHECKPOINT) != CHECKPOINT_SHA256:
        raise ValueError("REAL_U4_CHECKPOINT_IDENTITY")
    affinity = min(os.sched_getaffinity(0)); os.sched_setaffinity(0, {affinity})
    resource.setrlimit(resource.RLIMIT_AS, (2 * 1024**3, 2 * 1024**3))
    resource.setrlimit(resource.RLIMIT_CPU, (60, 60))
    start = time.perf_counter()
    with np.load(CHECKPOINT, allow_pickle=False) as a:
        arrays = {key: a[key] for key in a.files}
    before = {key: array_identity(value) for key, value in arrays.items()}
    records = []
    member_baseline = None
    for repetition in range(args.repeats):
        order = ("compressed", "stored") if repetition % 2 == 0 else ("stored", "compressed")
        for mode in order:
            p = ev / f"history_{repetition}_{mode}.npz"
            cpu0, wall0 = time.process_time(), time.perf_counter()
            if mode == "stored":
                write_stored_history(p, **arrays)
            else:
                # Flush and fsync both modes for the same durability contract.
                with p.open("xb") as stream:
                    np.savez_compressed(stream, **arrays)
                    stream.flush(); os.fsync(stream.fileno())
            write_cpu, write_wall = time.process_time() - cpu0, time.perf_counter() - wall0
            read_cpu0, read_wall0 = time.process_time(), time.perf_counter()
            with np.load(p, allow_pickle=False) as a:
                after = {key: array_identity(a[key]) for key in a.files}
            members = member_identity(p)
            if before != after:
                raise ArithmeticError("RESTORED_ARRAY_BITS_DIFFER")
            if member_baseline is None: member_baseline = members
            if members != member_baseline:
                raise ArithmeticError("UNCOMPRESSED_NPY_PAYLOADS_DIFFER")
            records.append({"repetition": repetition, "mode": mode,
                            "write_cpu_s": write_cpu, "write_wall_s": write_wall,
                            "validation_cpu_s": time.process_time() - read_cpu0,
                            "validation_wall_s": time.perf_counter() - read_wall0,
                            "file": p.name, "bytes": p.stat().st_size,
                            "file_sha256": file_sha256(p),
                            "array_bytes_equal": True, "NPY_members_equal": True})
    if before != {key: array_identity(value) for key, value in arrays.items()}:
        raise ArithmeticError("INPUT_ARRAY_MUTATION")
    result = {"schema": "rec.r3l.history-container-benchmark.v1",
              "status": "PASS_LOSSLESS_CONTAINER_ONLY",
              "execution_location": "GitHub Actions" if os.environ.get("GITHUB_ACTIONS") == "true" else
                  os.environ.get("REC_R3L_EXECUTION_LOCATION", "unspecified; see executor receipt"),
              "checkpoint_sha256": CHECKPOINT_SHA256, "checkpoint_kind": "actual saved U4",
              "python": platform.python_version(), "numpy": np.__version__, "affinity": [affinity],
              "array_identities": before, "NPY_member_identities": member_baseline,
              "records": records, "total_wall_s": time.perf_counter() - start,
              "new_U5_or_U6_integrations": 0, "new_native_C_runs": 0,
              "source_files": {str(p.relative_to(ROOT)): file_sha256(p) for p in (
                  ROOT / "scripts/benchmark_r3l_history_container.py", ROOT / "scripts/r3l_u6_cost.py")},
              "full_U6": "NOT_RUN", "production_speedup": "NOT_MEASURED",
              "full_run_budget_admission": "UNRESOLVED_REQUIRES_PHASE_MEASUREMENTS_AND_ALLOCATION"}
    (ev / "RESULT.json").write_text(json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n")
    print(json.dumps(result, sort_keys=True, allow_nan=False))


if __name__ == "__main__":
    main()
