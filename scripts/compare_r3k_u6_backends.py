#!/usr/bin/env python3
"""Compare legacy/owned U6 on one reviewed Python U5 checkpoint.

This is a bounded source-identical backend test, not a full U6 run or a
C/Python convergence test. Both paths evolve independently from the same
immutable h/2 checkpoint. No C trajectory is imported as Python state.
"""
from __future__ import annotations

import argparse
import gc
import hashlib
import json
import math
import os
from pathlib import Path
import resource
import signal
import sys
import time

for _key in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ[_key] = "1"
ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "scripts")]
import numpy as np

ARRAY_FIELDS = ("virtual_out", "average_virtual", "lyman_out")
CPU_CAP_S = 60
WALL_CAP_S = 180
MAX_STEPS = 128


def array_digest(value) -> dict:
    """Canonical logical row order without materializing a whole strided copy."""
    a = np.asarray(value)
    if a.ndim != 2 or a.dtype != np.dtype("float64"):
        raise ValueError("PARITY_ARRAY_SHAPE_OR_DTYPE")
    digest = hashlib.sha256()
    for row in a:
        if not np.all(np.isfinite(row)):
            raise ValueError("PARITY_ARRAY_NONFINITE")
        digest.update(np.asarray(row, dtype="<f8").tobytes(order="C"))
    return {"shape": list(a.shape), "dtype": "<f8", "sha256": digest.hexdigest()}


def result_digests(result) -> dict:
    """Bind every accepted state/RHS, event, endpoint and all stored spectra."""
    scalars = {key: getattr(result, key) for key in
               ("states", "steps", "event", "full_evaluations", "status", "rt_stop_iz")}
    scalar_bytes = json.dumps(scalars, sort_keys=True, separators=(",", ":"),
                              allow_nan=False).encode("utf-8")
    return {"scalar_sha256": hashlib.sha256(scalar_bytes).hexdigest(),
            "state_count": len(result.states), "accepted_steps": len(result.steps),
            "first_iz": result.states[0]["iz"], "last_iz": result.states[-1]["iz"],
            "trajectory_status": result.status,
            "arrays": {key: array_digest(getattr(result, key)) for key in ARRAY_FIELDS}}


def require_identical(left: dict, right: dict) -> None:
    if left != right:
        changed = sorted(k for k in set(left) | set(right) if left.get(k) != right.get(k))
        raise ArithmeticError("BACKEND_BYTE_MISMATCH:" + ",".join(changed))


def compare_checkpoint(checkpoint, cosmology, source, *, steps: int) -> dict:
    """Integrate each real backend; return exact-byte identity and separate clocks."""
    if isinstance(steps, bool) or not isinstance(steps, int) or not 1 <= steps <= MAX_STEPS:
        raise ValueError("BOUNDED_PARITY_STEPS_1_TO_128")
    from full_bianchi_hyrec.trajectory.primordial_2012_refined_u6_rt_boundary import integrate_u6_rt_boundary
    from full_bianchi_hyrec.trajectory.primordial_2012_owned_u6 import integrate_u6_owned
    prefix_before = {key: array_digest(checkpoint[key]) for key in ARRAY_FIELDS}
    records = {}
    for name, integrate in (("legacy", integrate_u6_rt_boundary), ("owned", integrate_u6_owned)):
        gc.collect()
        cpu0, wall0 = time.process_time(), time.perf_counter()
        result = integrate(checkpoint, cosmology, source, max_extra_accepted=steps,
                           max_full_evaluations=steps)
        elapsed = {"integration_cpu_s": time.process_time()-cpu0,
                   "integration_wall_s": time.perf_counter()-wall0}
        digest = result_digests(result)
        if digest["accepted_steps"] != steps or digest["last_iz"] != digest["first_iz"]+steps:
            raise ArithmeticError("BACKEND_INCOMPLETE_BOUNDED_INTERVAL")
        if result.full_evaluations != steps:
            raise ArithmeticError("BACKEND_ATOMIC_CALL_COUNT")
        records[name] = {"digest": digest, **elapsed}
        del result
        if {key: array_digest(checkpoint[key]) for key in ARRAY_FIELDS} != prefix_before:
            raise ArithmeticError("INPUT_CHECKPOINT_MUTATED:" + name)
    require_identical(records["legacy"]["digest"], records["owned"]["digest"])
    return {"status": "PASS_BOUNDED_BACKEND_BYTE_EQUIVALENCE", "steps": steps,
            "records": records,
            "measured_integration_wall_ratio": records["legacy"]["integration_wall_s"] /
                records["owned"]["integration_wall_s"],
            "timing_scope": "one paired run, integration only; not a production speedup claim",
            "physical_scope": "reviewed q0 h/2 U5 checkpoint, finite U6 prefix only",
            "full_U6": "NOT_RUN", "same_h_original_C": "NOT_TESTED_BY_THIS_RUNNER"}


def main(argv=None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--checkpoint", type=Path, required=True)
    parser.add_argument("--evidence-dir", type=Path, required=True)
    parser.add_argument("--expected-commit", required=True)
    parser.add_argument("--allocation-id", required=True)
    parser.add_argument("--steps", type=int, default=16)
    args = parser.parse_args(argv)
    if not args.allocation_id.strip() or not 1 <= args.steps <= MAX_STEPS:
        parser.error("require an allocation label and steps in 1..128")
    from run_r3j_u6_owned import source_binding
    binding = source_binding(ROOT, args.expected_commit)
    for name in ("scripts/compare_r3k_u6_backends.py",):
        binding["additional_source_sha256"][name] = hashlib.sha256((ROOT/name).read_bytes()).hexdigest()
    ev = args.evidence_dir.resolve()
    ev.mkdir(parents=True, exist_ok=False)
    affinity = min(os.sched_getaffinity(0))
    os.sched_setaffinity(0, {affinity})
    report = {"schema": "rec.r3k.u6-bounded-pair.v1", "status": "FAIL",
              "source": binding, "allocation_id": args.allocation_id,
              "historical_allocation": "CLOSED_HOLD_NOT_RESET", "first_failure": None,
              "resources": {"cpu_cap_s": CPU_CAP_S, "wall_cap_s": WALL_CAP_S,
                            "address_limit_bytes": 2*1024**3, "affinity": [affinity]}}
    start = time.perf_counter()
    try:
        resource.setrlimit(resource.RLIMIT_AS, (2*1024**3, 2*1024**3))
        resource.setrlimit(resource.RLIMIT_CPU, (CPU_CAP_S, CPU_CAP_S))
        signal.signal(signal.SIGALRM, lambda *_: (_ for _ in ()).throw(TimeoutError("PAIR_WALL_CAP")))
        signal.alarm(WALL_CAP_S)
        from full_bianchi_hyrec.trajectory.primordial_2012_refined_u6_rt_boundary import load_frozen_checkpoint, CHECKPOINT_SHA256
        from full_bianchi_hyrec.trajectory.primordial_2012_refined_start import HyRec2012Cosmology, make_hmla_source
        from full_bianchi_hyrec.trajectory.primitive_rates import OriginalHyRecPrimitiveRateTable
        archive = ROOT/"archive/inputs/original_hyrec_oct2012/HyRec_Oct2012.zip"
        original_sha = hashlib.sha256(archive.read_bytes()).hexdigest()
        if original_sha != "48cd597519606cdafd0ee6405b781d28467cd323278d16596055a8d0577a1d27":
            raise ValueError("ORIGINAL_SOURCE_SHA_MISMATCH")
        cp = load_frozen_checkpoint(args.checkpoint)
        c = HyRec2012Cosmology()
        table = OriginalHyRecPrimitiveRateTable.from_archive(archive)
        source = make_hmla_source(c, table)
        report.update(compare_checkpoint(cp, c, source, steps=args.steps))
        report.update({"checkpoint_sha256": CHECKPOINT_SHA256, "original_zip_sha256": original_sha})
    except Exception as error:
        report["status"] = "FAIL"
        report["first_failure"] = {"type": type(error).__name__, "message": str(error)}
    finally:
        signal.alarm(0)
        usage = resource.getrusage(resource.RUSAGE_SELF)
        cpu = usage.ru_utime + usage.ru_stime
        report["resources"].update({"wall_s": time.perf_counter()-start,
                                    "process_cpu_s": cpu, "peak_rss_bytes": usage.ru_maxrss*1024})
        if not math.isfinite(cpu) or cpu >= CPU_CAP_S:
            report["status"] = "FAIL_CPU_CAP"
        (ev/"RESULT.json").write_text(json.dumps(report, indent=2, sort_keys=True, allow_nan=False)+"\n")
        print(json.dumps(report, indent=2, sort_keys=True, allow_nan=False))
    if report["status"] != "PASS_BOUNDED_BACKEND_BYTE_EQUIVALENCE":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
