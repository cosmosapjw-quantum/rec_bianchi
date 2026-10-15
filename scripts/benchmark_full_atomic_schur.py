"""Matched-accuracy numerical performance of original HyRec 2+311 block solve.

Benchmark only the algebraic source step on fixed physical coefficients,
not rate-table loading, photon history advection or full xe(z) integration.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import statistics
import time

import numpy as np

from full_bianchi_hyrec.trajectory.hmla_flrw import HMLAFlrwSource
from full_bianchi_hyrec.trajectory.primitive_rates import OriginalHyRecPrimitiveRateTable
from full_bianchi_hyrec.trajectory.full_2012_atomic_source import (
    populate_original_full_atomic,NVIRT,
)

ROOT=Path(__file__).resolve().parents[1]
ARCHIVE=ROOT/"archive/inputs/original_hyrec_oct2012/HyRec_Oct2012.zip"
COSMO=dict(h=.6735837,omega_cb=.31242079216478097,
    omega_r_h2=4.1578740068818545e-5,
    omega_de_h2=.3119234221656212,omega_b_h2=.02242,
    y_he_mass=.245,tcmb0_K=2.7255)


def dense_block(snapshot):
    m=np.zeros((NVIRT+2,NVIRT+2),dtype=float)
    m[:2,:2]=snapshot.Trr
    m[:2,2:]=snapshot.Trv
    m[2:,:2]=snapshot.Tvr.T
    p=np.arange(NVIRT)+2
    m[p,p]=snapshot.Tvv[0]
    m[p[1:],p[:-1]]=snapshot.Tvv[1,1:]
    m[p[:-1],p[1:]]=snapshot.Tvv[2,:-1]
    return m, np.r_[snapshot.sr,snapshot.sv]


def run():
    model=HMLAFlrwSource(**COSMO,
         table=OriginalHyRecPrimitiveRateTable.from_archive(ARCHIVE))
    samples=[]
    for z,x,ratio in ((900.,.04,.98),(1200.,.45,.999)):
        s=populate_original_full_atomic(
            model,z=z,xHII=x,xe=x,
            Tm_K=model.tcmb0_K*(1+z)*ratio,
            incoming_virtual=np.linspace(2e-11,3e-11,NVIRT),
            incoming_lyman=np.array([1e-11,2e-11]),
        )
        mat,src=dense_block(s)
        # Independent exact matrix assembly. This tests that the 80-bin
        # reduction did not discard any diffusion or atomic coupling.
        real,virtual=s.instantaneous_schur_solution()
        band=np.r_[real,virtual]
        dense=np.linalg.solve(mat,src)
        diff=float(np.max(np.abs(band-dense)))
        rel=diff/max(float(np.max(np.abs(dense))),1e-250)
        band_res=float(np.max(np.abs(mat@band-src))/max(np.max(np.abs(src)),
                                                  np.max(np.abs(mat@band)),1e-250))
        dense_res=float(np.max(np.abs(mat@dense-src))/max(np.max(np.abs(src)),
                                                   np.max(np.abs(mat@dense)),1e-250))
        if rel>2e-7 or max(dense_res,band_res)>1e-8:
            raise AssertionError(
                f"matched numerical accuracy failed rel={rel}; residuals {band_res} {dense_res}"
            )
        # Warm up both implementations under identical process/thread policy.
        for _ in range(5):
            s.instantaneous_schur_solution();np.linalg.solve(mat,src)
        timing={}
        for name,fn,loops in (
            ("banded_schur",s.instantaneous_schur_solution,80),
            ("dense313",lambda:np.linalg.solve(mat,src),15),
        ):
            trials=[]
            for _ in range(5):
                tick=time.perf_counter_ns()
                for j in range(loops):
                    fn()
                trials.append((time.perf_counter_ns()-tick)*1e-9/loops)
            timing[name]={"median_s_per_call":statistics.median(trials),
                          "trials_s_per_call":trials}
        samples.append({
            "z":z,"x_HII":x,"Tm_over_Tr":ratio,
            "dense_dimension":313,"banded_diffusion_dimension":80,
            "max_abs_solution_difference":diff,
            "global_relative_solution_difference":rel,
            "banded_matrix_relative_residual":band_res,
            "dense_matrix_relative_residual":dense_res,
            "timing":timing,
            "banded_over_dense_speedup":timing["dense313"]["median_s_per_call"]/
                                           timing["banded_schur"]["median_s_per_call"],
        })
    return {
        "schema":"rec.r3b.sparse_schur_vs_dense.v1",
        "scope":"fixed-coefficient algebraic solve only",
        "single_thread_requested":True,
        "samples":samples,
    }


if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args()
    result=run()
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    for s in result["samples"]:
        print(s["z"],"rel",s["global_relative_solution_difference"],
              "speedup",s["banded_over_dense_speedup"],
              "banded_ms",s["timing"]["banded_schur"]["median_s_per_call"]*1000,
              "dense_ms",s["timing"]["dense313"]["median_s_per_call"]*1000)
