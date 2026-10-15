"""Reproducible finite-horizon numerics and concurrency survey, not cosmic production."""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
from statistics import median
from time import perf_counter

import numpy as np

from full_bianchi_hyrec.trajectory.causal_virtual_redshift import SOURCE_DLNA
from full_bianchi_hyrec.trajectory.hmla_flrw import HMLAFlrwSource
from full_bianchi_hyrec.trajectory.primitive_rates import (
    OriginalHyRecPrimitiveRateTable,
)
from full_bianchi_hyrec.trajectory.short_full_history import (
    integrate_full_h_short_history,
)


ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT / "archive/inputs/original_hyrec_oct2012/HyRec_Oct2012.zip"
SOURCE = HMLAFlrwSource(
    h=.6735837, omega_cb=.31242079216478097,
    omega_r_h2=4.1578740068818545e-5,
    omega_de_h2=.3119234221656212,
    omega_b_h2=.02242, y_he_mass=.245, tcmb0_K=2.7255,
    table=OriginalHyRecPrimitiveRateTable.from_archive(ARCHIVE),
)


def integrate(steps: int, dlna: float, x: float=.04):
    return integrate_full_h_short_history(
        SOURCE, z_start=900., x_HII_start=x,
        Tm_start_K=.98*SOURCE.tcmb0_K*901,
        steps=steps, dlna=dlna,
    )


def timed(fn):
    t0 = perf_counter()
    result = fn()
    return result, perf_counter()-t0


def execute():
    h0=SOURCE_DLNA/4.
    grids=[(17,h0),(33,h0/2),(65,h0/4)]
    solutions = [integrate(n,h) for n,h in grids]
    for j in range(1,len(solutions)):
        assert abs(solutions[j].z[-1]-solutions[0].z[-1]) < 3.e-11
    diagnostics={}
    for key in ("x_HII","Tm_K"):
        vals=[float(getattr(s,key)[-1]) for s in solutions]
        differences=[abs(vals[i]-vals[i+1]) for i in (0,1)]
        diagnostics[key]={
            "endpoints":vals,
            "successive_absolute_differences":differences,
            "observed_ratio_d_coarse_over_d_fine":
                differences[0]/differences[1] if differences[1] else None,
            "reference_not_exact":True,
        }
    cases=[.037,.04,.043,.046]
    def f(x): return integrate(45,SOURCE_DLNA/4,x)
    # Warm both paths before wall measurement; table sources are immutable.
    f(cases[0])
    def seq(): return [f(x) for x in cases]
    def par():
        with ThreadPoolExecutor(max_workers=2) as pool:
            return list(pool.map(f,cases))
    single_runs=[]
    parallel_runs=[]
    for _ in range(3):
        a,t1=timed(seq)
        b,t2=timed(par)
        for y,z in zip(a,b):
            np.testing.assert_array_equal(y.x_HII,z.x_HII)
            np.testing.assert_array_equal(y.virtual_out,z.virtual_out)
        single_runs.append(t1)
        parallel_runs.append(t2)
    return {
        "schema":"rec.r3d.short_full_numerics.v1",
        "model":"REC_SOURCE_HYREC2012_H_ONLY_Q0_ZERO_PREHISTORY",
        "source_step_ln_a":SOURCE_DLNA,
        "fixed_interval_ln_a":16*h0,
        "grids":[{"steps":n,"step_ln_a":h} for n,h in grids],
        "convergence":diagnostics,
        "real_source_operator":"2-real+311-virtual with 80-bin banded Schur",
        "execution":"local owner PC; 24 logical CPUs, NOT NCP",
        "batch_cases":len(cases),
        "batch_steps_each":45,
        "threads_for_parallel":2,
        "serial_s":single_runs,
        "parallel_s":parallel_runs,
        "median_speedup_serial_div_parallel":median(single_runs)/median(parallel_runs),
        "scoped_claim":"SHORT_CONTROLLED_H_ONLY_NUMERICAL_EXPERIMENT_NOT_FULL_RECOMBINATION",
    }


if __name__=="__main__":
    result=execute()
    path=ROOT/"research/rec_r3d_full_short_20261015/NUMERICS.json"
    path.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps(result,indent=2))
