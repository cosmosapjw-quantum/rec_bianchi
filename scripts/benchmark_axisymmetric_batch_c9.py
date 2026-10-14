#!/usr/bin/env python3
"""Real matched-condition benchmark for C9 scalar vs exact-Killing vector batch.

Same prescribed LRS Bianchi I background, common immutable time grid and
time-dependent frequency-sensitive positive scalar source. Warmed constructors
are excluded from ray-call timing; actual SciPy/Numpy runtime, not simulated.
"""
from __future__ import annotations
import argparse
import json
import math
import os
from pathlib import Path
import platform
import statistics
import sys
import time

import numpy as np

from full_bianchi_hyrec.background import AxisymmetricBianchiIBackground
from full_bianchi_hyrec.trajectory.axisymmetric_batched import (
    AxisymmetricBianchiIBatchSolver, BatchIsotropicCoefficients,
)
from full_bianchi_hyrec.trajectory.characteristic_angular import (
    CharacteristicAngularSolver, IsotropicTransferCoefficients,
)


def _rays(count):
    mu=np.linspace(-.97,.97,count)
    angle=np.linspace(0.,17.,count)
    r=np.sqrt(1-mu*mu)
    return np.column_stack((r*np.cos(angle),r*np.sin(angle),mu))


def run():
    m=AxisymmetricBianchiIBackground(q_ref=.01)
    last=math.log(.1/m.a_ref)
    seq=m.snapshots(np.linspace(0,last,257))
    scalar=CharacteristicAngularSolver(seq,interval_source=m)
    batched=AxisymmetricBianchiIBatchSolver(seq,m)

    def j(t,nu):
        return 3e-20*(1+.2*np.sin(2*t)+.02*(nu/2.4e15))

    def chi(t,nu):
        return 4e-17*(1+.1*np.cos(t)+.04*(nu/2.4e15))

    coeff1=IsotropicTransferCoefficients(j,chi)
    coeffN=BatchIsotropicCoefficients(j,chi,thread_safe=True)
    steps=128

    # Warm both APIs to avoid conflating import/tracing with actual throughput.
    d=_rays(2)
    for _ in range(2):
        scalar.trace_to_face(tau_start=0.,tau_end=last,direction_hydrogen=d[0],
            face_frequency_Hz=2.4e15,initial_occupation=.0015,
            coefficients=coeff1,n_step=steps)
        batched.trace_many_to_face(tau_start=0.,tau_end=last,
            face_directions=d,face_frequency_Hz=2.4e15,
            initial_occupation=.0015,coefficients=coeffN,
            n_step=steps,chunk_size=16)

    rows=[]
    trace=[]
    for M in (8,26,64):
        directions=_rays(M)
        def serial():
            return [
                scalar.trace_to_face(tau_start=0.,tau_end=last,
                   direction_hydrogen=n,face_frequency_Hz=2.4e15,
                   initial_occupation=.0015,coefficients=coeff1,n_step=steps)
                for n in directions
            ]
        def vector():
            return batched.trace_many_to_face(tau_start=0.,tau_end=last,
               face_directions=directions,face_frequency_Hz=2.4e15,
               initial_occupation=.0015,coefficients=coeffN,n_step=steps,
               chunk_size=4096,workers=1)
        times={}
        results={}
        for label,fn in (("scalar",serial),("vector",vector)):
            vals=[]
            for i in range(3):
                t=time.perf_counter(); result=fn();vals.append(time.perf_counter()-t)
            times[label]=vals
            results[label]=result
        f_scalar=np.array([x.occupation_face for x in results['scalar']])
        f_vector=results["vector"].occupation_face
        max_relative=float(np.max(np.abs(f_vector/f_scalar-1)))
        # The vector path uses exact conserved momenta; scalar baseline uses
        # midpoint direction integration, so bit equality is not expected.
        if max_relative>5e-7:
            raise AssertionError(("component mismatch",M,max_relative))
        record={"M":M,"n_step":steps,"same_geometry_and_source":True,
           "scalar_samples_s":times["scalar"],"batch_samples_s":times["vector"],
           "scalar_median_s":statistics.median(times["scalar"]),
           "vector_median_s":statistics.median(times["vector"]),
           "ratio_scalar_to_batch":statistics.median(times["scalar"])/statistics.median(times["vector"]),
           "max_relative_occupation_difference":max_relative}
        rows.append(record);print("MATCHED",json.dumps(record),flush=True)

    # Exact batch comparison across possible CPU-parallel execution.
    # Each rayon chunk is independent but callbacks must be pure/thread safe.
    for M in (256,4096,16384):
        directions=_rays(M)
        for workers in (1,2,4):
            fun=lambda: batched.trace_many_to_face(
                  tau_start=0.,tau_end=last,face_directions=directions,
                  face_frequency_Hz=2.4e15,initial_occupation=.0015,
                  coefficients=coeffN,n_step=steps,workers=workers,
                  chunk_size=4096)
            times=[]
            for rep in range(3):
                start=time.perf_counter(); result=fun()
                times.append(time.perf_counter()-start)
            record={"M":M,"workers":workers,"chunk_size":4096,
                    "repeats":len(times),
                    "samples_s":times,"median_s":statistics.median(times),
                    "source_model_sha256":m.source_sha256,
                    "method_identity":result.method_identity}
            trace.append(record);print("THREADED",json.dumps(record),flush=True)

    return {"schema":"rec.c9.opt_benchmark.v1","same_models":True,
            "measurement":"actual local perf_counter; constructors warmed and excluded",
            "machine":platform.platform(),
            "python":sys.version.split()[0],
            "logical_cpus":os.cpu_count(),
            "source_model_sha256":m.source_sha256,
            "n_step":steps,"snapshot_nodes":len(seq.tau),
            "q_ref":m.q_ref,
            "source_kernel":"time-frequency dependent nonnegative emissivity and opacity",
            "matched_legacy":rows,"threaded_batch":trace,
            "scope":"prescribed LRS Bianchi-I, independent scalar occupation only",
            "not_claimed":["NCP scaling","native Rust parity","whole HyRec thermodynamic integration","full observer CMB or reionization detection"]}


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--out",type=Path,required=True)
    args=parser.parse_args()
    if args.out.exists():
        parser.error("refusing output overwrite")
    report=run()
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(report,ensure_ascii=False,indent=2))
    print("SUMMARY",json.dumps({
        "speedups":[(r["M"],r["ratio_scalar_to_batch"]) for r in report["matched_legacy"]],
        "parallel_measures":[(x["M"],x["workers"],x["median_s"]) for x in report["threaded_batch"]]
    }),flush=True)


if __name__=="__main__":
    main()
