#!/usr/bin/env python3
"""Prepare reviewed R3M state evidence or analyze independent time grids.

Every output directory is create-only. A successful program exit means a
diagnostic was produced; the JSON status carries the scientific limitations.
No original integrator, tolerance, stage rule, or historical hold is changed.
"""
from __future__ import annotations

import argparse
from dataclasses import asdict
import hashlib
import json
import math
from pathlib import Path
import resource
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
import numpy as np

from full_bianchi_hyrec.trajectory.time_convergence import (
    FIELD_FLOORS, GridHistory, SOURCE_ZIP_SHA256, X0, compare_histories, grid_step,
)

R3M_FILES = {
    "python_u6_rt.npz": "5ceb99a7ed221f920460aa41188ce60a748332e854a75ee58362d3f10a360cd2",
    "native_oracle_stdout.csv": "57ebca0157e956747059af4ae3d9dfb44a98157e58e6ffdbb917a520c3406c38",
    "verification.json": "1d55f1ff90a9fad7174ddc6022bbf957aeb4f683b7831ecbb63acd854d925b4b",
}
R3I_CONTRACT_SHA256 = "308aecdfb9fbe1eac292a5d6cc120ba60966b7988e6df82bd4e337d6598a6fa6"


def sha(path: Path) -> str:
    with Path(path).open("rb") as f:
        return hashlib.file_digest(f, "sha256").hexdigest()


def dump(path: Path, data) -> None:
    with path.open("x") as f:
        f.write(json.dumps(data, indent=2, sort_keys=True, allow_nan=False)+"\n")


def empty_output(path: Path) -> None:
    try:
        path.mkdir(parents=True, exist_ok=False)
    except FileExistsError as e:
        raise ValueError("OUTPUT_EXISTS_PRESERVE_PRIOR_EVIDENCE") from e


def prepare_r3m(raw: Path, out: Path) -> dict:
    """Extract STATE-only evidence from pinned raw bytes; no integration."""
    before = {name: sha(raw/name) for name in R3M_FILES}
    if before != R3M_FILES:
        raise ValueError("R3M_REVIEWED_INPUT_HASH_MISMATCH")
    r = json.loads((raw/"verification.json").read_text())
    if (r["source_zip_sha256"] != SOURCE_ZIP_SHA256 or
            r["checkpoint_sha256"] != "7aeec545cfc028e870d51e07d1fe3f052bd770d1eb4537568f5faa889bf6752b" or
            r["python_result"]["steps"] != 5210 or r["first_failure"] is not None):
        raise ValueError("R3M_RECEIPT_CONTRACT")
    with np.load(raw/"python_u6_rt.npz", allow_pickle=False) as a:
        states = [json.loads(str(s)) for s in a["states_json"]]
    g = np.array([s["iz"] for s in states], dtype=np.int64)
    if not np.array_equal(g, np.arange(53179, 58390)):
        raise ValueError("R3M_STATE_ORDER")
    native = []
    with (raw/"native_oracle_stdout.csv").open() as f:
        for line in f:
            if line.startswith("BASE,"):
                p = line.rstrip().split(",")[1:]
                native.append((int(p[0]), float(p[5]), float(p[6])))
            elif line.startswith("STEP,"):
                p = line.rstrip().split(",")[1:]
                if int(p[0]) != len(native)-1:
                    raise ValueError("R3M_NATIVE_STEP_ORDER")
                native.append((int(p[1]), float(p[6]), float(p[7])))
    if len(native) != len(states) or [n[0] for n in native] != g.tolist():
        raise ValueError("R3M_NATIVE_STATE_COUNT")
    from full_bianchi_hyrec.trajectory.primordial_2012_refined_start import HyRec2012Cosmology
    physics = {"cosmology": asdict(HyRec2012Cosmology()), "source_zip_sha256": SOURCE_ZIP_SHA256,
               "atomic_thermal": "original_oct2012", "stage_rule": "original_oct2012",
               "predictor": "current_and_prev2", "q": 0, "REI_activation": False}
    provenance = {"kind": "independent_python", "checkpoint_resampled": False,
        "q": 0, "REI_activation": False, "source_zip_sha256": SOURCE_ZIP_SHA256,
        "physics_id": hashlib.sha256(json.dumps(physics, sort_keys=True).encode()).hexdigest(),
        "physics_contract": physics, "source_commit": "d0e534b1f5b4bb20fe19875f6d502681b833470d",
        "reviewed_checkpoint_sha256": r["checkpoint_sha256"],
        "boundary_coverage_lna": [X0+grid_step(1)*53177, X0+grid_step(1)*58389],
        "same_h_scope": "U6 state discrepancies vs original C; original U5 holds remain",
        "quantization_basis": "binary64 NPZ; no additional decimal output quantization",
        "run_location": "owner workstation (reused PR107); extraction location is separate"}
    arrays = {"global_iz": g, "redshift": np.array([s["z"] for s in states]),
              "regime": np.full(len(g), "U6_FULL", dtype="U16")}
    for key, col in (("xe", 1), ("Tm_K", 2)):
        arrays[key] = np.array([s[key] for s in states])
        arrays["parity_abs_"+key] = np.abs(arrays[key]-np.array([n[col] for n in native]))
        arrays["quantization_abs_"+key] = np.zeros(len(g))
    # A descriptor hashes its data and binds the original producer evidence.
    with (out/"h2_state_trace.npz").open("xb") as f:
        np.savez_compressed(f, **arrays)
    descriptor = {"schema": "rec.r3n.history.v1", "level": 1, "dlna": grid_step(1),
                  "origin_lna": X0, "npz": "h2_state_trace.npz",
                  "npz_sha256": sha(out/"h2_state_trace.npz"), "provenance": provenance,
                  "boundary_lna": [X0+grid_step(1)*53177, X0+grid_step(1)*58389],
                  "producer_inputs_sha256": before}
    if {name: sha(raw/name) for name in R3M_FILES} != before:
        raise ValueError("INPUT_MUTATION_DURING_EXTRACTION")
    dump(out/"h2_state_trace.json", descriptor)
    # Validate the serialized adapter output before calling it usable.
    load_history(out/"h2_state_trace.json")
    return {"status": "REVIEWED_H2_STATE_TRACE_PREPARED", "nodes": len(g),
            "full_U6_reused": True, "new_integrations": 0,
            "state_only": True, "photon_convergence": "NOT_EVALUATED",
            "source_files_sha256": before, "trace_sha256": descriptor["npz_sha256"]}


def load_history(descriptor_path: Path) -> GridHistory:
    d = json.loads(descriptor_path.read_text())
    if d.get("schema") != "rec.r3n.history.v1":
        raise ValueError("HISTORY_DESCRIPTOR_SCHEMA")
    level = d["level"]
    if d.get("dlna") != grid_step(level) or d.get("origin_lna") != X0:
        raise ValueError("GRID_SPACING_OR_ORIGIN_IDENTITY")
    path = (descriptor_path.parent/d["npz"]).resolve()
    # Descriptors cannot silently select data outside their delivery directory.
    if not path.is_relative_to(descriptor_path.parent.resolve()):
        raise ValueError("HISTORY_DATA_PATH_OUTSIDE_DESCRIPTOR_DIRECTORY")
    before = sha(path)
    if before != d["npz_sha256"]:
        raise ValueError("HISTORY_DATA_SHA_MISMATCH")
    with np.load(path, allow_pickle=False) as a:
        g = a["global_iz"]
        redshift = a["redshift"]
        expected_z = np.array([8001.*math.exp(-grid_step(level)*int(i))-1. for i in g])
        if (redshift.shape != g.shape or not np.all(np.isfinite(redshift)) or
                np.any(np.abs(redshift-expected_z) > 2.e-12)):
            raise ValueError("SOURCE_REDSHIFT_GRID_MISMATCH")
        values = {k: a[k] for k in FIELD_FLOORS}
        parity = {k: a["parity_abs_"+k] if "parity_abs_"+k in a else None for k in FIELD_FLOORS}
        quant = {k: a["quantization_abs_"+k] if "quantization_abs_"+k in a else None for k in FIELD_FLOORS}
        result = GridHistory(level, g, values, parity, quant, a["regime"],
                             tuple(d["boundary_lna"]), d["provenance"])
    if sha(path) != before:
        raise ValueError("INPUT_MUTATION_DURING_ANALYSIS")
    return result


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("prepare-r3m")
    p.add_argument("--raw-dir", type=Path, required=True)
    p.add_argument("--evidence-dir", type=Path, required=True)
    p = sub.add_parser("analyze")
    p.add_argument("--history", type=Path, action="append", required=True)
    p.add_argument("--evidence-dir", type=Path, required=True)
    p.add_argument("--require-complete", action="store_true")
    args = parser.parse_args(argv)
    empty_output(args.evidence_dir)
    start_cpu, start_wall = time.process_time(), time.monotonic()
    try:
        if sha(ROOT/"research/rec_r3i_time_refinement_20261016/CONTRACT.json") != R3I_CONTRACT_SHA256:
            raise ValueError("R3I_CONVERGENCE_CONTRACT_CHANGED_REVIEW_REQUIRED")
        if args.command == "prepare-r3m":
            result = prepare_r3m(args.raw_dir, args.evidence_dir)
        else:
            hashes = {str(p.resolve()): sha(p) for p in args.history}
            result = compare_histories([load_history(p) for p in args.history])
            if {str(p.resolve()): sha(p) for p in args.history} != hashes:
                raise ValueError("DESCRIPTOR_MUTATION_DURING_ANALYSIS")
            result["descriptor_sha256"] = hashes
        dump(args.evidence_dir/"result.json", result)
        code = 3 if (args.command == "analyze" and args.require_complete and
                     not result["global_coverage"]) else 0
    except Exception as e:
        dump(args.evidence_dir/"failure.json", {"type": type(e).__name__, "message": str(e)})
        result, code = {"status": "INPUT_OR_IMPLEMENTATION_ERROR", "error": str(e)}, 2
    record = {"schema": "rec.r3n.execution.v1", "command": sys.argv if argv is None else argv,
              "status": result["status"], "exit_code": code, "cpu_s": time.process_time()-start_cpu,
              "wall_s": time.monotonic()-start_wall, "peak_rss_native_units": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
              "python": sys.version, "numpy": np.__version__, "integration_executed": False,
              "files": {p.name: {"bytes": p.stat().st_size, "sha256": sha(p)}
                        for p in sorted(args.evidence_dir.iterdir()) if p.is_file()}}
    dump(args.evidence_dir/"execution.json", record)
    print(json.dumps({"status": result["status"], "exit_code": code, "cpu_s": record["cpu_s"]}))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
