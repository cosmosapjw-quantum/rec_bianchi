#!/usr/bin/env python3
"""Adapt pinned, independently evolved R3G original-h states to R3N.

This copies accepted states. It executes no HyRec trajectory. The old
integer-redshift C comparison is retained as aggregate evidence only: it
does not supply nodewise uncertainty on the source grid.
"""
from __future__ import annotations

import argparse
from dataclasses import asdict
import hashlib
import json
import math
from pathlib import Path
import resource
import shutil
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))
import numpy as np

from compare_r3n_time_grids import (
    R3I_CONTRACT_SHA256, dump, empty_output, load_history, sha,
)
from full_bianchi_hyrec.trajectory.time_convergence import (
    FIELD_FLOORS, SOURCE_ZIP_SHA256, X0, cubic_stencil, grid_size, grid_step,
    original_cubic,
)
from full_bianchi_hyrec.trajectory.primordial_2012_refined_start import HyRec2012Cosmology

INPUT_SHA256 = {
    "independent_source_grid.npz": "12818562014c3f7563d4396d3b499ae9666feef3d8824db8232717325cc0bf15",
    "independent_integer_z_history.csv": "c7c113af50fd49e7937a3bfef15ac2e295fe51cc161e83196bc921e0f02c98ce",
    "verification.json": "43ccacd3bce28512ee5223ec9d5ff9979c435227d63da5f78e7572a89de478fa",
}
PRODUCER = "6c6c385f69f73ad477a3131d637b25fe7faca5ac"
PHYSICS_ID = "aca3d76043802e93260ae590f92984453f191e55c31bb8290a24350e198777ef"
SOURCE_ZIP = ROOT / "archive/inputs/original_hyrec_oct2012/HyRec_Oct2012.zip"
NODES, EMLA_INPUT, PEEBLES_INPUT = 105859, 29195, 72466
PRESERVE = {"U5_h": "HOLD_9_FAIL", "U5_h2": "HOLD_8_FAIL",
            "historical_budget": "CLOSED_HOLD_NOT_RESET", "REI_activation": False}


def input_hashes(raw: Path) -> dict:
    return {name: sha(raw / name) for name in INPUT_SHA256}


def validate_receipt(r: dict) -> None:
    expected = {
        "task": "R3G-U8-LOW-Z-TO-END-001",
        "execution_revision": PRODUCER,
        "status": "STOP_AT_SOURCE_Z0_CUBIC_STENCIL",
        "end_global_iz": NODES - 1, "accepted_extra": 35859,
        "attempted_evaluations": 35859, "emla_updates": 2467,
        "peebles_updates": 33392, "first_failure": None,
        "stop_failure": None, "rei_activation": False,
        "historic_u5_original_verification": "FAIL",
        "historic_u5_average_gate": "HOLD_ORIGINAL_TOLERANCE_NOT_MET",
        "independent_source_grid_sha256": INPUT_SHA256["independent_source_grid.npz"],
        "independent_integer_z_history_sha256": INPUT_SHA256["independent_integer_z_history.csv"],
    }
    if any(k not in r or r[k] != v for k, v in expected.items()):
        raise ValueError("R3G_RECEIPT_CONTRACT")
    event = r.get("event", {})
    if (r.get("rei_activation") is not False or
            not str(r.get("claim_ceiling", "")).startswith("q=0 ") or
            event.get("global_iz") != PEEBLES_INPUT or event.get("reason") != "TR_MIN" or
            r.get("start", {}).get("global_iz") != 69999):
        raise ValueError("R3G_RECEIPT_STAGE_OR_Q0")
    for iz, z in ((NODES - 1, r["end_z"]), (PEEBLES_INPUT, event["z"])):
        expected_z = 8001. * math.exp(-grid_step(0) * iz) - 1.
        if not math.isfinite(z) or abs(z - expected_z) > 2.e-12:
            raise ValueError("R3G_RECEIPT_SOURCE_CLOCK")
    if NODES != grid_size(0):
        raise ValueError("ORIGINAL_H_GRID_SIZE_CHANGED")


def source_values(path: Path) -> dict:
    with np.load(path, allow_pickle=False) as a:
        if set(a.files) != set(FIELD_FLOORS):
            raise ValueError("R3G_SOURCE_GRID_FIELDS")
        values = {k: a[k] for k in FIELD_FLOORS}
    for a in values.values():
        if (a.shape != (NODES,) or a.dtype.kind != "f" or a.dtype.itemsize != 8 or
                not np.all(np.isfinite(a)) or np.any(a <= 0.)):
            raise ValueError("R3G_SOURCE_GRID_SHAPE_DTYPE_OR_DOMAIN")
    return values


def check_saved_output_clock(path: Path, values: dict) -> dict:
    """Check seven Python-output anchors; this is not a C parity bound."""
    with path.open() as f:
        if f.readline().strip() != "z,xe,Tm_K,Tm_Tr_ratio":
            raise ValueError("R3G_INTEGER_HISTORY_HEADER")
        table = np.loadtxt(f, delimiter=",")
    if (table.shape != (8001, 4) or not np.all(np.isfinite(table)) or
            not np.array_equal(table[:, 0], np.arange(8000, -1, -1)) or
            np.any(table[:, 1:] <= 0.)):
        raise ValueError("R3G_INTEGER_HISTORY_DOMAIN_OR_ORDER")
    ratio = table[:, 2] / (HyRec2012Cosmology().T0_K * (1. + table[:, 0]))
    if not np.allclose(ratio, table[:, 3], rtol=5.e-14, atol=0.):
        raise ValueError("R3G_INTEGER_HISTORY_THERMAL_UNITS")
    maxima = {k: 0. for k in FIELD_FLOORS}
    anchors = (8000, 1700, 1100, 836, 20, 16, 0)
    for z in anchors:
        ix, fraction, _ = cubic_stencil(0, -math.log1p(z))
        for key, col in (("xe", 1), ("Tm_K", 2)):
            actual = original_cubic(values[key][ix], fraction)
            saved = float(table[8000 - z, col])
            err = abs(actual - saved) / max(abs(saved), FIELD_FLOORS[key])
            maxima[key] = max(maxima[key], err)
    # A serialization/clock coherence check, separate from any physical gate.
    if any(v > 5.e-12 for v in maxima.values()):
        raise ValueError("R3G_PYTHON_OUTPUT_SOURCE_CLOCK_MISMATCH")
    return {"anchors_z": list(anchors), "max_scaled_difference": maxima,
            "meaning": "source-grid to saved Python integer-z output only"}


def _prepare_h(raw: Path, out: Path, source_zip: Path) -> dict:
    """Called only after main atomically reserves its evidence directory."""
    before = input_hashes(raw)
    if before != INPUT_SHA256:
        raise ValueError("R3G_REVIEWED_INPUT_HASH_MISMATCH")
    source_before = sha(source_zip)
    if source_before != SOURCE_ZIP_SHA256:
        raise ValueError("ORIGINAL_SOURCE_ZIP_IDENTITY")
    if sha(ROOT / "research/rec_r3i_time_refinement_20261016/CONTRACT.json") != R3I_CONTRACT_SHA256:
        raise ValueError("R3I_CONVERGENCE_CONTRACT_CHANGED_REVIEW_REQUIRED")
    receipt = json.loads((raw / "verification.json").read_text())
    validate_receipt(receipt)
    values = source_values(raw / "independent_source_grid.npz")
    clock = check_saved_output_clock(raw / "independent_integer_z_history.csv", values)
    physics = {"cosmology": asdict(HyRec2012Cosmology()), "source_zip_sha256": SOURCE_ZIP_SHA256,
               "atomic_thermal": "original_oct2012", "stage_rule": "original_oct2012",
               "predictor": "current_and_prev2", "q": 0, "REI_activation": False}
    physics_id = hashlib.sha256(json.dumps(physics, sort_keys=True).encode()).hexdigest()
    if physics_id != PHYSICS_ID:
        raise ValueError("R3N_PREPARED_R3M_PHYSICS_IDENTITY_CHANGED")
    indices = np.arange(NODES, dtype=np.int64)
    labels = np.full(NODES, "UNKNOWN", dtype="U7")
    labels[EMLA_INPUT:PEEBLES_INPUT] = "EMLA"
    labels[PEEBLES_INPUT:] = "PEEBLES"
    h = grid_step(0)
    boundary = [X0 + h * EMLA_INPUT, X0 + h * PEEBLES_INPUT]
    arrays = {"global_iz": indices,
              "redshift": np.array([8001. * math.exp(-h * int(i)) - 1. for i in indices]),
              "regime": labels, **values}
    for key in FIELD_FLOORS:
        arrays["quantization_abs_" + key] = np.zeros(NODES)
    # No parity_abs_* arrays: an integer-z maximum is not a nodewise bound.
    with (out / "h_state_trace.npz").open("xb") as f:
        np.savez_compressed(f, **arrays)
    provenance = {
        "kind": "independent_python", "checkpoint_resampled": False,
        "q": 0, "REI_activation": False, "source_zip_sha256": SOURCE_ZIP_SHA256,
        "physics_id": physics_id, "physics_contract": physics, "source_commit": PRODUCER,
        "boundary_coverage_lna": [boundary[0], 0.],
        "boundary_coverage_basis": "Known from input 29195 through physical z=0; final source node beyond z=0 retained for cubic output stencil",
        "regime_semantics": "original source-guard INPUT index; before input 29195 UNKNOWN",
        "run_location": "reused R3G U8 producer; machine type not reclassified by adapter",
        "quantization_basis": "binary64 NPZ; no additional decimal output quantization",
        "nodewise_C_parity": "UNKNOWN",
        "same_h_scope": "Prior 8001 integer-z aggregate retained separately; no per-node C discrepancy supplied",
        "source_array_bytes_sha256": {k: hashlib.sha256(v.tobytes()).hexdigest() for k, v in values.items()},
    }
    descriptor = {"schema": "rec.r3n.history.v1", "level": 0, "dlna": h,
                  "origin_lna": X0, "npz": "h_state_trace.npz",
                  "npz_sha256": sha(out / "h_state_trace.npz"), "provenance": provenance,
                  "boundary_lna": boundary, "producer_inputs_sha256": before}
    dump(out / "h_state_trace.json", descriptor)
    restored = load_history(out / "h_state_trace.json")
    if any(restored.values[k].tobytes() != values[k].tobytes() for k in values):
        raise ValueError("SOURCE_STATE_BYTE_ROUNDTRIP_MISMATCH")
    # These three small originals make the adapter runnable from its delivery.
    copies = out / "producer_inputs"
    copies.mkdir()
    for name in INPUT_SHA256:
        with (raw / name).open("rb") as src, (copies / name).open("xb") as dst:
            shutil.copyfileobj(src, dst)
    if input_hashes(copies) != before or input_hashes(raw) != before or sha(source_zip) != source_before:
        raise ValueError("INPUT_MUTATION_DURING_EXTRACTION")
    return {"status": "REUSED_ORIGINAL_H_STATE_TRACE_PREPARED", "nodes": NODES,
            "global_iz": [0, NODES - 1], "source_dlna": h, "new_integrations": 0,
            "source_files_sha256": before, "trace_sha256": descriptor["npz_sha256"],
            "state_bytes_preserved": True, "nodewise_C_parity": "UNKNOWN",
            "python_output_clock_check": clock,
            "prior_integer_z_8001_C_max_relative": receipt["integer_z_8001_max_relative"],
            "parity_bound_conversion": "NOT_PERFORMED_INSUFFICIENT_NODEWISE_EVIDENCE",
            "source_clock_final_lna": X0 + h * (NODES - 1),
            "physical_boundary_coverage_lna": provenance["boundary_coverage_lna"],
            "prior_full_tar": {"bytes": 309819364,
                "sha256": "d302fc3680bbaafe39f1f5c840365cc04c9d6718d3e0a3221929a40c4c7d3012",
                "dropbox_whole_readback": "MATCH_REUSED_FROM_PARENT_INTAKE",
                "new_remote_readback_by_adapter": False},
            "preserve": PRESERVE, "scientific_admission": "NOT_ESTABLISHED_BY_ADAPTER"}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw-dir", type=Path, required=True)
    parser.add_argument("--evidence-dir", type=Path, required=True)
    parser.add_argument("--source-zip", type=Path, default=SOURCE_ZIP)
    args = parser.parse_args(argv)
    empty_output(args.evidence_dir)
    started = time.monotonic()
    try:
        result = _prepare_h(args.raw_dir, args.evidence_dir, args.source_zip)
        dump(args.evidence_dir / "result.json", result)
        code = 0
    except Exception as e:
        result = {"status": "INPUT_OR_IMPLEMENTATION_ERROR", "error": str(e)}
        dump(args.evidence_dir / "failure.json", {"type": type(e).__name__, "message": str(e)})
        code = 2
    record = {"schema": "rec.r3o.h-input-execution.v1", "command": sys.argv if argv is None else argv,
              "status": result["status"], "exit_code": code, "cpu_process_s": time.process_time(),
              "wall_s": time.monotonic() - started, "run_location": "caller environment; retained run receipt identifies sandbox",
              "peak_rss_kib_linux": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
              "python": sys.version, "numpy": np.__version__, "integration_executed": False,
              "files": {str(p.relative_to(args.evidence_dir)): {"bytes": p.stat().st_size, "sha256": sha(p)}
                        for p in sorted(args.evidence_dir.rglob("*")) if p.is_file()}}
    dump(args.evidence_dir / "execution.json", record)
    print(json.dumps({"status": result["status"], "exit_code": code,
                      "cpu_process_s": record["cpu_process_s"]}))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
