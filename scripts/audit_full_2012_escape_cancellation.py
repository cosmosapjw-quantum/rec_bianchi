"""High-precision diagnosis of original HyRec optical depth cancellation.

The source native expression uses 1-(1-exp(-tau))/tau for tau>1e-6,
which subtracts nearly identical binary64 numbers in the vicinity of tau=1e-6.
This audit does not mutate the legacy C definition or falsely call a formula
change 'scientific parity'. It quantifies the representation error separately.
"""
from __future__ import annotations
import argparse
import json
import math
from pathlib import Path

import mpmath as mp
import numpy as np

from full_bianchi_hyrec.trajectory.full_2012_atomic_source import (
    populate_original_full_atomic,_original_escape_factors,NVIRT,
)
from full_bianchi_hyrec.trajectory.hmla_flrw import HMLAFlrwSource
from full_bianchi_hyrec.trajectory.primitive_rates import OriginalHyRecPrimitiveRateTable

ROOT=Path(__file__).resolve().parents[1]
ARCHIVE=ROOT/"archive/inputs/original_hyrec_oct2012/HyRec_Oct2012.zip"
COSMO=dict(h=.6735837,omega_cb=.31242079216478097,
    omega_r_h2=4.1578740068818545e-5,
    omega_de_h2=.3119234221656212,omega_b_h2=.02242,
    y_he_mass=.245,tcmb0_K=2.7255)


def audit():
    model=HMLAFlrwSource(**COSMO,
        table=OriginalHyRecPrimitiveRateTable.from_archive(ARCHIVE))
    cases=[]
    mp.mp.dps=75
    for z,x,ratio in ((650.,.002,.95),(900.,.04,.98),
                       (1200.,.45,.999),(1450.,.97,.99999)):
        s=populate_original_full_atomic(
            model,z=z,xHII=x,xe=x,Tm_K=model.tcmb0_K*(1+z)*ratio,
            incoming_virtual=np.zeros(NVIRT),incoming_lyman=np.zeros(2))
        tau=s.Dtau
        native_p,_=_original_escape_factors(tau)
        stable=np.array(native_p,copy=True)
        large=tau>1e-6
        stable[large]=1+np.expm1(-tau[large])/tau[large]
        # More stable small-but-above-threshold continuation using expm1,
        # not a different physical model or epsilon floor.
        errors=[]
        for k in np.where(large)[0]:
            a=mp.mpf(float(tau[k]))
            high=mp.mpf(1)+mp.expm1(-a)/a
            native=float(abs((mp.mpf(float(native_p[k]))-high)/high))
            accurate=float(abs((mp.mpf(float(stable[k]))-high)/high))
            errors.append((native,accurate,int(k),float(tau[k])))
        largest=max(errors,key=lambda z:z[0]) if errors else None
        cases.append({
            "z":z,"large_tau_bins":len(errors),
            "max_rel_source_one_minus_P":0 if largest is None else largest[0],
            "max_rel_expm1_same_index":0 if largest is None else largest[1],
            "worst_bin_index":None if largest is None else largest[2],
            "worst_tau":None if largest is None else largest[3],
            "max_rel_stable_over_all_bins":max([q[1] for q in errors],default=0),
        })
    return {
        "schema":"rec.r3b.native_escape_cancellation_audit.v1",
        "validated_state":"same original source states and tau, 75-digit mpmath reference",
        "physical_process_changed":False,
        "original_C_formula_modified":False,
        "source_branch":"tau>1e-6 -> 1-(1-exp(-tau))/tau, else tau/2-tau^2/6",
        "alternate_branch":"tau>1e-6 -> 1+expm1(-tau)/tau",
        "cases":cases
    }


if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args()
    result=audit()
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps(result["cases"],indent=2))
