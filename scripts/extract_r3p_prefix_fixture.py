#!/usr/bin/env python3
"""Extract small, source-authenticated real prefix slices from saved R3M raw."""
from __future__ import annotations
import argparse
import gzip
import json
import os
from pathlib import Path
import sys
import time

for key in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[key] = "1"
ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "src")]
import numpy as np
from benchmark_r3p_audit import load_inputs, REVIEWED
from r3p_rust_audit import sha256
from verify_r3i_h2_u6_rt_boundary import KB_EV_K, RT_IZ, LINE_EV


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for key in ("raw", "checkpoint", "output"):
        p.add_argument("--" + key, type=Path, required=True)
    a = p.parse_args()
    a.output.mkdir(parents=True, exist_ok=False)
    start = time.process_time()
    result, c, table, *_ = load_inputs(a.raw, a.checkpoint)
    starts = (0, 8000, 16725)
    columns = np.array([col for first in starts for col in range(first, first + 8)], dtype=np.int64)
    selected = set(columns.tolist())
    rows = []
    with (a.raw / "native_oracle_stdout.csv").open() as stream:
        for line in stream:
            if line.startswith("BASE,"):
                break
            if line.startswith(("PV,", "PL,")) and int(line.split(",", 2)[1]) in selected:
                rows.append(line)
    if len(rows) != len(columns) * 314:
        raise ValueError("R3P_FIXTURE_RECORD_COUNT")
    native = np.empty((len(columns), 314), dtype=np.float64)
    for i, line in enumerate(rows):
        tag, col, slot, value = line.strip().split(",")
        j, b = divmod(i, 314)
        if (int(col) != columns[j] or tag != ("PV" if b < 311 else "PL")
                or int(slot) != (b if b < 311 else b - 311)):
            raise ValueError("R3P_FIXTURE_ORDER")
        native[j, b] = float(value)
    py = np.column_stack((result.virtual_out[:, columns].T, result.lyman_out[:, columns].T))
    tr = np.array([KB_EV_K * c.T0_K * (1. + c.redshift(RT_IZ + int(col))) for col in columns])
    energies = np.concatenate((table.energy_eV, LINE_EV))
    np.savez_compressed(a.output / "prefix.npz", py=py, native=native, tr=tr,
                        energies=energies, columns=columns, block_starts=np.array(starts, dtype=np.int64))
    with (a.output / "prefix.csv.gz").open("xb") as f:
        f.write(gzip.compress("".join(rows).encode("ascii"), mtime=0))
    meta = {"schema": "rec.r3p.real-prefix-fixture.v1", "source_raw_sha256": REVIEWED,
            "source_checkpoint_sha256": sha256(a.checkpoint), "new_physical_steps": 0,
            "source": "Reviewed R3M saved full original-h2 U6 output; extraction only",
            "block_starts": list(starts), "columns_per_block": 8, "prefix_fields": len(rows),
            "source_script_sha256": sha256(Path(__file__)), "extraction_cpu_s": time.process_time() - start,
            "files": {name: sha256(a.output / name) for name in ("prefix.npz", "prefix.csv.gz")}}
    for name, digest in REVIEWED.items():
        if sha256(a.raw / name) != digest:
            raise ValueError("R3P_FIXTURE_INPUT_CHANGED")
    (a.output / "MANIFEST.json").write_text(json.dumps(meta, indent=2, sort_keys=True) + "\n")
    print(json.dumps(meta, sort_keys=True))


if __name__ == "__main__":
    main()
