#!/usr/bin/env python3
"""Audit actual C9 optimization speed measurements and peak memory separately.

Only resource measurement and plot generation; never reuses old measurements
as if newly executed. Parallel mode must actually have >1 chunk to count.
"""
from __future__ import annotations
import json,hashlib,math,platform,time,tracemalloc
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from full_bianchi_hyrec.background import AxisymmetricBianchiIBackground
from full_bianchi_hyrec.trajectory.axisymmetric_batched import (
    AxisymmetricBianchiIBatchSolver,BatchIsotropicCoefficients,
)

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"research/rec_c9_optim_20261015"
PRE=OUT/"BENCHMARK.json"
POST=OUT/"BENCHMARK_CACHED.json"


def source_trace_memory(m,solver,M,chunk_size=4096):
    phase=np.linspace(0.,17.,M)
    mu=np.linspace(-.97,.97,M)
    r=np.sqrt(1-mu*mu)
    directions=np.column_stack((r*np.cos(phase),r*np.sin(phase),mu))
    end=math.log(.1/m.a_ref)
    coeff=BatchIsotropicCoefficients(
        lambda t,nu:3e-20*(1+.2*np.sin(2*t)+.02*(nu/2.4e15)),
        lambda t,nu:4e-17*(1+.1*np.cos(t)+.04*(nu/2.4e15)),
    )
    # Warm geometry, so memory reflects ray data and source transfer, not
    # source-model creation; source clock cache itself uses O(n_step).
    solver._prepare_geometry(0.,end,128)
    tracemalloc.start()
    begin=time.perf_counter()
    result=solver.trace_many_to_face(
         tau_start=0.,tau_end=end,face_directions=directions,
         face_frequency_Hz=2.4e15,initial_occupation=.0015,
         coefficients=coeff,n_step=128,chunk_size=chunk_size,workers=1)
    seconds=time.perf_counter()-begin
    curr,peak=tracemalloc.get_traced_memory()
    tracemalloc.stop()
    if result.n_rays!=M or not np.all(result.occupation_face>=0.):
        raise AssertionError("memory specimen failed numerical positivity")
    return {"nrays":M,"peak_python_traced_bytes":peak,
            "post_call_python_traced_bytes":curr,"measured_elapsed_s":seconds,
            "chunk_size":chunk_size,"workers":1,
            "note":"tracemalloc includes Python-managed allocations, not all native library RSS; constructors excluded"}


def main():
    pre=json.loads(PRE.read_text());post=json.loads(POST.read_text())
    for p in (pre,post):
        if p["schema"]!="rec.c9.opt_benchmark.v1" or p["n_step"]!=128:
            raise ValueError("different benchmark family")
        if len(p["matched_legacy"])!=3:
            raise ValueError("missing matched scalar comparisons")
    rawsha={x.name:hashlib.sha256(x.read_bytes()).hexdigest() for x in (PRE,POST)}
    compare=[]
    for a,b in zip(pre["matched_legacy"],post["matched_legacy"]):
        assert a["M"]==b["M"]
        compare.append({
            "nrays":a["M"],
            "original_scalar_median_s":b["scalar_median_s"],
            "uncached_vector_median_s":a["vector_median_s"],
            "cached_vector_median_s":b["vector_median_s"],
            "uncached_speedup":a["ratio_scalar_to_batch"],
            "cached_speedup":b["ratio_scalar_to_batch"],
            "cached_versus_uncached_vector_speedup":a["vector_median_s"]/b["vector_median_s"],
            "max_scalar_to_exact_batch_occupation_relative_difference":
                  max(a["max_relative_occupation_difference"],b["max_relative_occupation_difference"]),
        })
    threaded=[]
    for row in post["threaded_batch"]:
        chunks=math.ceil(row["M"]/row["chunk_size"])
        threaded.append({**row,
          "effective_chunks":chunks,
          "actually_uses_parallel_path":bool(row["workers"]>1 and chunks>1)})
    serial_large=next(x for x in threaded if x["M"]==16384 and x["workers"]==1)
    actual_parallel=[
       {"workers":x["workers"],
        "ratio_to_one_worker":x["median_s"]/serial_large["median_s"],
        "speedup_if_greater_than_one":serial_large["median_s"]/x["median_s"]}
       for x in threaded if x["M"]==16384
    ]
    model=AxisymmetricBianchiIBackground(q_ref=.01)
    seq=model.snapshots(np.linspace(0,math.log(.1/model.a_ref),257))
    solver=AxisymmetricBianchiIBatchSolver(seq,model)
    memory=[source_trace_memory(model,solver,n) for n in (16384,65536)]
    result={
      "schema":"rec.c9.optim_assessment.v1",
      "scope":"C9 option reviewed with source-matched scalar positive transfer",
      "before_after_benchmark_sha256":rawsha,
      "warm_scalar_vs_batch":compare,
      "worker_benchmark":threaded,
      "real_multi_chunk_thread_ratio":actual_parallel,
      "measured_memory":memory,
      "default_parallel_policy":"workers=1; worker>1 is opt-in and only runs concurrently for >=2 chunks and thread-safe pure callbacks",
      "scientific_scope":"normal-comoving prescribed LRS Bianchi I exact null k_i; independent scalar occupation transfer only",
      "not_claimed":["Native Rust/REI full speedup","Numba/CUDA acceleration",
                     "parallel advantage under tested conditions",
                     "full gas radiation Einstein coupling or scientific admission"],
    }
    path=OUT/"OPTIM_ASSESSMENT.json"
    path.write_text(json.dumps(result,indent=2))
    fig,ax=plt.subplots(figsize=(8,5))
    ax.semilogy([x["nrays"] for x in compare],[x["uncached_speedup"] for x in compare],
                "o-",label="Vector batch, cache cold")
    ax.semilogy([x["nrays"] for x in compare],[x["cached_speedup"] for x in compare],
                "o-",label="Vector batch, cache warm")
    ax.set_xlabel("Rays on common 128-step Bianchi-I transport")
    ax.set_ylabel("Scalar runtime / vector batch runtime")
    ax.set_title("Measured matched-source REC scalar-to-vector acceleration")
    ax.grid(True,which="both",alpha=.25)
    ax.legend()
    fig.tight_layout()
    fig.savefig(OUT/"C9_BATCH_SPEEDUP.png",dpi=180)
    plt.close(fig)
    fig,ax=plt.subplots(figsize=(7.5,4.8))
    ax.plot([x["workers"] for x in actual_parallel],[x["ratio_to_one_worker"] for x in actual_parallel],"o-")
    ax.axhline(1.,linestyle=":",linewidth=1)
    ax.set_xlabel("Workers (16,384 rays / 4 chunks)")
    ax.set_ylabel("Wall time / 1-worker wall time")
    ax.set_title("Threaded ray chunks: parallel overhead is measurable")
    ax.grid(True,alpha=.25)
    fig.tight_layout()
    fig.savefig(OUT/"C9_THREADS_COST.png",dpi=180)
    plt.close(fig)
    print(json.dumps({
        "matched_speedups":compare,"real_worker_ratios":actual_parallel,
        "memory":memory,"outputs":[str(path),str(OUT/"C9_BATCH_SPEEDUP.png"),
                                  str(OUT/"C9_THREADS_COST.png")]},indent=2))


if __name__=="__main__":
    main()
