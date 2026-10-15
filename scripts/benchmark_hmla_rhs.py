#!/usr/bin/env python3
"""Measured source-rate batching and optional thread chunk overhead.

Different physical x_HII/x_e states share a single background redshift and
matter temperature. Each source rate evaluation carries canonical HyRec
primitive table provenance; this is NOT a spatially resolved radiation
transfer solver. Parallel workers operate only on independent array chunks.
"""
from __future__ import annotations
import argparse,json,math,statistics,time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import numpy as np
from verify_hmla_native_rhs import source

def run():
    s=source()
    z=1100.
    Tm=s.tcmb0_K*(1+z)*.99999
    rows=[]
    for n in (64,512,2048,8192):
        x=np.linspace(.015,.98,n)
        xe=x+.12*s.f_he
        def scalar():
            return np.asarray([s.hydrogen_rhs_ln_a(
                z=z,x_HII=float(a),x_e=float(b),Tm_K=Tm)
                for a,b in zip(x,xe)])
        def vector():
            return s.hydrogen_rhs_ln_a_many(z=z,x_HII=x,x_e=xe,Tm_K=Tm)
        baseline=scalar()
        batched=vector()
        rel=np.abs(batched-baseline)/np.maximum(np.abs(baseline),1e-15)
        if not np.all(np.isfinite(batched)) or np.max(rel)>2e-12:
            raise AssertionError("batch changed HMLA physical RHS")
        timings={}
        for name,fun in (("scalar",scalar),("vectorized",vector)):
            for _ in range(2):fun()
            samples=[]
            for _ in range(3):
                t=time.perf_counter();fun();samples.append(time.perf_counter()-t)
            timings[name]={"samples_s":samples,"median_s":statistics.median(samples)}
        record={"states":n,"source_shared_z":z,"source_shared_Tm_K":Tm,
                "max_scaled_relative_difference":float(np.max(rel)),
                "serial_source":timings["scalar"],"batched_source":timings["vectorized"],
                "speedup":timings["scalar"]["median_s"]/timings["vectorized"]["median_s"]}
        rows.append(record)
        print("BENCH",json.dumps(record),flush=True)

    # Genuine chunk parallel experiment, no native subagent and no claim
    # of workload-wide benefit. Use same 8192 vector states and 4 chunks.
    n=8192;chunk=2048
    x=np.linspace(.015,.98,n);xe=x+.12*s.f_he
    par=[]
    for workers in (1,2,4):
        def run_parallel():
            sections=[(x[j:j+chunk],xe[j:j+chunk]) for j in range(0,n,chunk)]
            def evaluate(pair):
                return s.hydrogen_rhs_ln_a_many(
                    z=z,x_HII=pair[0],x_e=pair[1],Tm_K=Tm)
            if workers==1:
                parts=[evaluate(pair) for pair in sections]
            else:
                with ThreadPoolExecutor(max_workers=workers) as ex:
                    parts=list(ex.map(evaluate,sections))
            return np.concatenate(parts)
        ref=s.hydrogen_rhs_ln_a_many(z=z,x_HII=x,x_e=xe,Tm_K=Tm)
        got=run_parallel()
        if not np.array_equal(got,ref):
            raise AssertionError("parallel chunk physical map differs from serial")
        samples=[]
        for _ in range(5):
            t=time.perf_counter();run_parallel();samples.append(time.perf_counter()-t)
        par.append({"workers":workers,"actual_chunks":4,"samples_s":samples,
                    "median_s":statistics.median(samples),
                    "bit_equal_single_full_numpy":True})
        print("PARALLEL",json.dumps(par[-1]),flush=True)
    return {"schema":"rec.hmla2s2p.vectorized_source_benchmark.v1",
      "source_scope":"single z/Tm with independent hydrogen/helium electron states, 2s2p HMLA RHS only",
      "benchmark":rows,"thread_experiment":par,
      "default_parallel":"1-worker to avoid overhead unless measured future regime",
      "source_rate_table_evaluations":"scalar = N calls; batch=1 call per common z/Tm array",
      "no_FULL_history_speed_claim":True}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,required=True)
    q=p.parse_args()
    if q.out.exists():p.error("output exists")
    data=run()
    q.out.parent.mkdir(parents=True,exist_ok=True)
    q.out.write_text(json.dumps(data,indent=2)+"\n")
if __name__=="__main__":
    main()
