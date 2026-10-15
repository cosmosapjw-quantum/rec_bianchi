"""Measured equal-input incoming-history vectorization/parallelization.

This microbenchmark measures the 311+2 incoming history SOURCE operator,
not a FULL recombination trajectory, not atom/radiation self-consistency.
"""
from __future__ import annotations
import argparse
import hashlib
import io
import json
import math
from pathlib import Path
import statistics
import time
from concurrent.futures import ThreadPoolExecutor
import zipfile

import numpy as np

from full_bianchi_hyrec.trajectory.causal_virtual_redshift import (
    SOURCE_DLNA, causal_incoming_from_accepted_histories,
    safe_constant_shear_dlna,
)

ROOT=Path(__file__).resolve().parents[1]
ARCHIVE=ROOT/"archive/inputs/original_hyrec_oct2012/HyRec_Oct2012.zip"


def run():
    source_hash=hashlib.sha256(ARCHIVE.read_bytes()).hexdigest()
    with zipfile.ZipFile(ARCHIVE) as zf:
        e=np.loadtxt(io.BytesIO(zf.read("HyRec/two_photon_tables.dat")))[:,0]
    n=640
    mu_grid=np.linspace(-1,1,17)
    times=np.arange(n)[None,None,:]
    m=mu_grid[:,None,None]
    vir=1e-8*((1+np.arange(311)[None,:,None]/500)
                *(1+.25*m+times/1300))
    lyman=1e-9*((1+np.arange(3)[None,:,None]/4)
                *(1+.13*m-times/1900))
    q=.018
    step=safe_constant_shear_dlna(e,shear_q=q)
    z=math.expm1(math.log1p(1600.)-step*n)
    temp=2.7255*(1+z)
    def call(mus):
        result=causal_incoming_from_accepted_histories(
            energies_eV=e,virtual_history=vir,lyman_history=lyman,
            z_start=1600.,z_face=z,iz=n,mu_face=np.asarray(mus),
            mu_grid=mu_grid,shear_q=q,radiation_T_face_K=temp,dlna=step)
        return np.concatenate((result.virtual_distortion,
                               result.lya_lyb_incoming_distortion),axis=1)
    records=[]
    for count in (16,64,128):
        rays=np.linspace(-1,1,count)
        vector_times=[]
        for _ in range(5):
            t=time.perf_counter()
            v=call(rays)
            vector_times.append(time.perf_counter()-t)
        serial_times=[]
        for _ in range(2):
            t=time.perf_counter()
            s=np.vstack([call((float(ray),)) for ray in rays])
            serial_times.append(time.perf_counter()-t)
        error=float(np.max(np.abs(s-v)))
        if not np.allclose(s,v,rtol=1e-13,atol=1e-18):
            raise RuntimeError("scalar vs vector incoming history mismatch")
        parallel={}
        if count==128:
            for workers in (2,4):
                elapsed=[]
                for _ in range(3):
                    slices=np.array_split(rays,workers)
                    t=time.perf_counter()
                    with ThreadPoolExecutor(max_workers=workers) as pool:
                        pieces=list(pool.map(call,slices))
                    parallel_result=np.vstack(pieces)
                    elapsed.append(time.perf_counter()-t)
                    if not np.allclose(parallel_result,v,rtol=1e-13,atol=1e-18):
                        raise RuntimeError("parallel per-ray data mismatch")
                parallel[str(workers)] = {
                    "median_s":statistics.median(elapsed),
                    "all_s":elapsed,
                    "max_abs_difference":float(np.max(np.abs(parallel_result-v))),
                }
        records.append({
            "ray_count":count,
            "vector_median_s":statistics.median(vector_times),
            "scalar_reference_median_s":statistics.median(serial_times),
            "vector_speedup_over_independent_calls":
                statistics.median(serial_times)/statistics.median(vector_times),
            "vector_trials_s":vector_times,
            "scalar_trials_s":serial_times,
            "max_abs_difference":error,
            "parallel_trials":parallel,
        })
    return {
        "model":"source-locked 2012 HyRec 311+2 incoming photon history, no atomic FULL",
        "reference_comparison":"identical Python method one-by-one per ray vs NumPy vectorized rays",
        "source_archive_sha256":source_hash,
        "source_bins":len(e),
        "accepted_history_steps":n,
        "source_direction_nodes":len(mu_grid),
        "shear_q":q,
        "effective_dlna":step,
        "native_flrw_dlna":SOURCE_DLNA,
        "extra_full_history_concatenate_bytes":int(vir.nbytes+lyman.nbytes),
        "records":records,
    }


if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args()
    result=run()
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
    print(json.dumps({
        "output":str(args.output),
        "short":[{k:rec[k] for k in
            ("ray_count","vector_median_s","scalar_reference_median_s",
             "vector_speedup_over_independent_calls","max_abs_difference")}
             for rec in result["records"]]
    },indent=2))
