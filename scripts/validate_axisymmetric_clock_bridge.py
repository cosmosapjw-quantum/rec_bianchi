#!/usr/bin/env python3
"""Read-only matched native accepted-step reduction for REC's actual Bianchi-I module.

Does not invoke a REI solver or infer trajectory convergence from a component
clock comparison.  The CSV is an R8 sampled native-history input, not a new
cosmological history. Requires the original R8 SHA source summary to be supplied
separately for provenance.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path

from full_bianchi_hyrec.background import AxisymmetricBianchiIBackground

FROZEN_TARGET = 1e-9


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def reduce_sample(input_csv: Path, input_summary: Path) -> dict:
    source = json.loads(input_summary.read_text())
    if source.get("run_id") != "REC_BG_R8_20261014":
        raise ValueError("only exact R8 native selected-step contract supported")
    expected = {case["case"]: case for case in source["source_cases"]}
    if set(expected) != {"ZERO", "SHEAR_PLUS", "SHEAR_MINUS"}:
        raise ValueError("missing R8 source-case identity")
    source_files = []
    for label in ("ZERO", "SHEAR_PLUS", "SHEAR_MINUS"):
        sha = expected[label].get("history_sha256")
        if not isinstance(sha, str) or len(sha) != 64:
            raise ValueError("missing upstream native-history SHA256")
        source_files.append({"case": label, "sha256": sha, "rows": expected[label]["rows"]})

    cases = {"ZERO": 0.0, "SHEAR_PLUS": 0.01, "SHEAR_MINUS": -0.01}
    models = {label: AxisymmetricBianchiIBackground(q) for label, q in cases.items()}
    values = []
    counts = {label: 0 for label in cases}
    maxima = {label: 0.0 for label in cases}
    with input_csv.open(newline="") as file:
        reader = csv.DictReader(file)
        required = {"case", "index", "a1", "a2", "signed_q", "saved_dt_s", "reference_dt_s"}
        if not required.issubset(reader.fieldnames or ()):
            raise ValueError("R8 native step CSV schema mismatch")
        for row in reader:
            label = row["case"]
            if label not in cases:
                raise ValueError("unbound native case")
            if float(row["signed_q"]) != cases[label]:
                raise ValueError("signed q mismatch")
            idx = int(row["index"])
            a1, a2 = float(row["a1"]), float(row["a2"])
            result = models[label].interval(a1, a2)
            reference = float(row["reference_dt_s"])
            native = float(row["saved_dt_s"])
            if not math.isfinite(reference) or reference <= 0 or not math.isfinite(native):
                raise ValueError("nonphysical or missing clock oracle")
            relative = result.delta_t_s / reference - 1.0
            counts[label] += 1
            maxima[label] = max(maxima[label], abs(relative))
            values.append({
                "case": label, "accepted_step_index": idx,
                "a1": a1, "a2": a2, "relative_error": relative,
                "legacy_saved_relative": native / reference - 1.0,
                "delta_t_s": result.delta_t_s, "reference_dt_s": reference,
                "delta_b": result.delta_b, "delta_l": result.delta_l,
                "cells_crossed": result.cells_crossed,
            })
    if not values or any(counts[x] != expected[x]["selected"] for x in cases):
        raise ValueError("selected row count missing or does not match source")
    if len(values) != source.get("sample_count"):
        raise ValueError("overall sample count mismatch")
    maximum = max(abs(row["relative_error"]) for row in values)
    native_fails = sum(abs(row["legacy_saved_relative"]) > 1e-8 for row in values)
    return {
        "schema": "rec.axisymmetric_bianchi_i.native_clock_bridge.v1",
        "scientific_status": "SCOPED_COMPONENT_DIAGNOSTIC_ONLY",
        "source_sample_csv_sha256": _sha256(input_csv),
        "source_summary_sha256": _sha256(input_summary),
        "native_history_sources": source_files,
        "model_source_identities": {case: obj.source_sha256 for case, obj in models.items()},
        "sample_count": len(values),
        "counts_by_case": counts,
        "max_relative_error_by_case": maxima,
        "max_relative_error": maximum,
        "legacy_saved_exceeding_1e_minus_8": native_fails,
        "frozen_component_tolerance": FROZEN_TARGET,
        "component_pass": maximum < FROZEN_TARGET,
        "rows": values,
        "not_claimed": [
            "native Rust bit identity", "coupled photon/ion/thermal step parity",
            "full-history convergence", "REI AX11/AX12 scientific admission",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True, help="Private R8 SAMPLED_STEPS.csv")
    parser.add_argument("--summary", type=Path, required=True, help="Private R8 SAMPLED_STEP_SUMMARY.json")
    parser.add_argument("--out", type=Path, required=True, help="New JSON output path, never overwrite")
    args = parser.parse_args()
    if args.out.exists():
        parser.error("output path exists; refuse silent overwrite")
    result = reduce_sample(args.input, args.summary)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2))
    print(json.dumps({k: v for k, v in result.items() if k not in ("rows", "native_history_sources", "not_claimed")}, indent=2))
    return 0 if result["component_pass"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
