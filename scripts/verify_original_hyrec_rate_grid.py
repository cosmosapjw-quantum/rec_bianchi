#!/usr/bin/env python3
"""Compare REC Python atomic primitive rates against original compiled HyRec C.

Always extracts original source from a byte-locked 2012 archive into a fresh
temporary directory, compiles the original interpolate_rates hydrogen.c and
hyrectools.c with an existing source-read-only C harness, and evaluates the
identical Tr[eV], Tm/Tr points through both implementations.

This is a local primitive *function parity*, not a HyRec recombination
history or radioactive full Boltzmann/source-coupling result.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
from pathlib import Path
import subprocess
import tempfile
import numpy as np

from full_bianchi_hyrec.trajectory.primitive_rates import (
    OriginalHyRecPrimitiveRateTable,
)
from full_bianchi_hyrec.recoil.original_hyrec_native import ORIGINAL_HYREC_ARCHIVE_SHA256

ROOT=Path(__file__).resolve().parents[1]
ARCHIVE=ROOT/"archive/inputs/original_hyrec_oct2012/HyRec_Oct2012.zip"
HARNESS=ROOT/"scripts/c_harness/original_hyrec_primitive_rates_harness.c"

def _vector(rate):
    return np.concatenate([
      rate.alpha_m3_s*1e6,
      rate.delta_alpha_m3_s*1e6,
      rate.beta_s_inv,
      np.array([rate.R_2p2s_s_inv]),
    ])

def run() -> dict:
    raw=ARCHIVE.read_bytes()
    assert hashlib.sha256(raw).hexdigest()==ORIGINAL_HYREC_ARCHIVE_SHA256
    table=OriginalHyRecPrimitiveRateTable.from_archive(ARCHIVE)
    temperature=[.004,.00405,.005,.01,.02,.04,.08,.17,.26,.38]
    ratios=[.1,.28,.63,.81,.97,1.]
    trials=[]
    with tempfile.TemporaryDirectory(prefix="rec_hyrec_native_parity_") as work:
        source=table.extract_source_tree(work)
        exe=Path(work)/"primitive_rates_native"
        compile_cmd=[
            "gcc","-std=c11","-D_DEFAULT_SOURCE","-O2",
            "-I",str(source),str(HARNESS),
            str(source/"hydrogen.c"),str(source/"hyrectools.c"),
            "-lm","-o",str(exe),
        ]
        build=subprocess.run(compile_cmd,capture_output=True,text=True,timeout=30)
        if build.returncode!=0:
            raise RuntimeError(f"original C parity compiler failed: {build.stderr[-900:]}")
        for Tr in temperature:
            for ratio in ratios:
                p=subprocess.run([str(exe),f"{Tr:.17g}",f"{ratio:.17g}","1","1"],
                          cwd=source,capture_output=True,text=True,timeout=10)
                if p.returncode:
                    raise RuntimeError(f"upstream source C interpolation failed at {(Tr,ratio)}: {p.stderr}")
                reference=np.asarray([float(x) for x in p.stdout.split()],dtype=float)
                if reference.shape!=(7,) or not np.all(np.isfinite(reference)):
                    raise ValueError("original source C rates invalid")
                rates=table.evaluate(
                    radiation_temperature_eV_rescaled=Tr,
                    matter_to_radiation_temperature_ratio=ratio,
                )
                observed=_vector(rates)
                if observed.shape!=reference.shape:
                    raise ValueError("C parity shape mismatch")
                # Exact-zero source rates are valid at the cold edge, and are
                # compared by zero class, not by imaginary relative accuracy.
                zero=reference==0.
                if np.any(observed[zero]!=0):
                    raise AssertionError(f"native zero differs from Python: {(Tr,ratio)}")
                active=~zero
                relative=np.abs(observed[active]/reference[active]-1.)
                max_rel=float(relative.max()) if relative.size else 0.
                if max_rel>3e-12:
                    raise AssertionError(f"HyRec original-C interpolation parity mismatch {Tr,ratio,max_rel}")
                trials.append({
                    "radiation_temperature_eV":Tr,
                    "matter_radiation_ratio":ratio,
                    "max_nonzero_relative_difference":max_rel,
                    "native_zero_photoionization":bool(np.any(zero[4:6])),
                    "native_vector_cgs_and_s_inv":reference.tolist(),
                    "python_vector_cgs_and_s_inv":observed.tolist(),
                })
    return {
        "schema":"rec.hyrec2012.primitive_C_vs_python.v1",
        "source_archive_sha256":ORIGINAL_HYREC_ARCHIVE_SHA256,
        "original_native_harness_sha256":hashlib.sha256(HARNESS.read_bytes()).hexdigest(),
        "count":len(trials),
        "temperature_eV_grid":temperature,"matter_temperature_ratio_grid":ratios,
        "maximum_nonzero_relative_difference":max(x["max_nonzero_relative_difference"] for x in trials),
        "cold_native_beta_zero_points":sum(x["native_zero_photoionization"] for x in trials),
        "acceptance_gate_nonzero_relative":3e-12,
        "source_original_C_semantics":"rates: [Alpha2s,Alpha2p,DAlpha2s,DAlpha2p,Beta2s,Beta2p,R2p2s] in cgs cm^3/s and s^-1",
        "current_REC_status":"SCOPED_ORIGINAL_C_ATOMIC_INTERPOLATION_PARITY",
        "whole_REC_recombination_history_status":"NOT_IMPLEMENTED_IN_THIS_NATIVE_COMPARISON",
        "rows":trials,
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,required=True)
    args=p.parse_args()
    if args.out.exists():
        p.error("refusing reference output overwrite")
    r=run()
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(r,indent=2)+"\n")
    print(json.dumps({k:v for k,v in r.items() if k!="rows"},indent=2))

if __name__=="__main__":
    main()
