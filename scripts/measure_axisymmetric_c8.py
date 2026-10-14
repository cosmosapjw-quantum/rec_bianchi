#!/usr/bin/env python3
"""REC C8: finite-clock / characteristic error and measured resource audit.

Prescribed normal-comoving axisymmetric Bianchi I. No native REI simulation,
full original-HyRec source, observer redshift history, or scientific admission.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
import platform
import statistics
import time
from pathlib import Path

import mpmath as mp
import numpy as np
from scipy.integrate import solve_ivp

from full_bianchi_hyrec.background import AxisymmetricBianchiIBackground
from full_bianchi_hyrec.trajectory.characteristic_angular import (
    CharacteristicAngularSolver, IsotropicTransferCoefficients,
    constant_coefficient_transfer,
)

SOURCE_VERSION="rec_c8_lrs_log_clock_measurement_v1"
INITIAL_OCCUPATION=0.0015
FACE_HZ=2.4e15
MU=0.43
PHI=0.7


def _mp_ref(model, L1: float, L2: float):
    """Independent 70-digit integral with native float parameters frozen."""
    mp.mp.dps=70
    lo=mp.mpf(float(L1))
    delta=mp.mpf(float(L2))-lo
    h0=mp.mpf(float(model.cosmology.h0_per_s))
    om=mp.mpf(float(model.cosmology.omega_m))
    rr=mp.mpf(float(model.cosmology.omega_r))
    la=mp.mpf(float(model.cosmology.omega_lambda))
    ar=mp.mpf(float(model.a_ref))
    shear0=mp.mpf(float(model._s_ref))

    def evaluate(y):
        l=lo+delta*y
        a=ar*mp.exp(l)
        shear=shear0*mp.exp(-3*l)
        HF2=h0*h0*(om/a**3+rr/a**4+la)
        H=mp.sqrt(HF2 if model.same_h else HF2+shear**2)
        return 1/H, shear/H

    dt=delta*mp.quad(lambda y:evaluate(y)[0],[0,1])
    db=delta*mp.quad(lambda y:evaluate(y)[1],[0,1])
    return float(dt), float(db)


def _orbit(model, photon_steps, snapshot_nodes, interval, jfun, chifun,
           source_bound: bool = True):
    sequence=model.snapshots(np.linspace(0.,interval.delta_l,snapshot_nodes))
    mu=MU
    direction=np.array([math.sqrt(1-mu*mu)*math.cos(PHI),
        math.sqrt(1-mu*mu)*math.sin(PHI),mu])
    started=time.perf_counter()
    solver=CharacteristicAngularSolver(
        sequence,interval_source=model if source_bound else None
    )
    result=solver.trace_to_face(
        tau_start=float(sequence.tau[0]),tau_end=float(sequence.tau[-1]),
        direction_hydrogen=direction,face_frequency_Hz=FACE_HZ,
        initial_occupation=INITIAL_OCCUPATION,
        coefficients=IsotropicTransferCoefficients(
            emissivity_s_inv=lambda l,nu:jfun(l,nu),
            opacity_s_inv=lambda l,nu:chifun(l,nu),
        ),
        n_step=photon_steps,
    )
    elapsed=time.perf_counter()-started
    return result,elapsed


def _source_rates(L, nu):
    return (3e-20*(1+.1*math.sin(3*L)),
            4e-17*(1+.03*math.cos(L)))


def _source_target(model,end_L):
    """Independent SciPy DOP853 in L, analytic H (not a Hermite clock)."""
    m=model.cosmology
    Hf=m.hubble_flrw
    s0=model.q_ref*Hf(model.a_ref)
    def rhs(L,Y):
        a=model.a_ref*math.exp(L)
        H=math.sqrt(Hf(a)**2 + (s0*math.exp(-3*L))**2)
        j,chi=_source_rates(L,FACE_HZ)
        return [(j-chi*Y[0])/H]
    p=solve_ivp(rhs,(0.,end_L),[INITIAL_OCCUPATION],rtol=2e-12,
                atol=2e-16,method="DOP853")
    if not p.success:raise RuntimeError(p.message)
    return float(p.y[0,-1])


def _angular_ref(model,end_L):
    # Independent exact conserved-covariant-momentum finite map; B from
    # high-precision quadrature, not the Hermite numerical reference.
    _dt,B=_mp_ref(model,0.0,end_L)
    r=math.sqrt(math.exp(-2*B)*(1-MU*MU)+math.exp(4*B)*MU*MU)
    return math.exp(end_L)*r, MU*math.exp(2*B)/r


def measure() -> dict:
    q_cases=(0., .005, -.005, .01, -.01)
    endpoints=[
        (0.0,1e-14),(0.0,1e-12),(.05,math.nextafter(.05,math.inf)),
        (.021,.02101),(.08,.25),(0.0,math.log(.1/(1/21))),
    ]
    checks=[]
    for q in q_cases:
        model=AxisymmetricBianchiIBackground(q_ref=q)
        for l1,l2 in endpoints:
            inc=model.interval_log(l1,l2)
            dt,db=_mp_ref(model,l1,l2)
            dt_rel=inc.delta_t_s/dt-1.
            db_rel=0 if q==0 else inc.delta_b/db-1.
            if not (inc.delta_t_s>0 and abs(dt_rel)<1e-9 and abs(db_rel)<1e-9):
                raise AssertionError((q,l1,l2,dt_rel,db_rel))
            checks.append({"q_ref":q,"l1":l1,"l2":l2,
              "delta_L":inc.delta_l,"seconds":inc.delta_t_s,"delta_b":inc.delta_b,
              "dt_reference_seconds":dt,"db_reference":db,
              "dt_relative_error":dt_rel,"db_relative_error":db_rel})

    model=AxisymmetricBianchiIBackground(q_ref=.01)
    end_L=math.log(.1/model.a_ref)
    inc=model.interval_log(0.,end_L)
    reference_f=_source_target(model,end_L)
    nu_initial_ratio,mu_initial=_angular_ref(model,end_L)
    rows=[]
    directions=np.array([math.sqrt(1-MU*MU)*math.cos(PHI),
        math.sqrt(1-MU*MU)*math.sin(PHI),MU])
    for nodes in (65,257,513):
        for steps in (32,64,128,256):
            result,took=_orbit(
                model,steps,nodes,inc,
                lambda l,nu:_source_rates(l,nu)[0],
                lambda l,nu:_source_rates(l,nu)[1],
            )
            error_f=result.occupation_face/reference_f-1
            rel_energy=result.initial_frequency_Hz/(FACE_HZ*nu_initial_ratio)-1
            mu_error=result.initial_direction_hydrogen[2]-mu_initial
            rows.append({
                "background_nodes":nodes,"steps":steps,
                "f_relative_error":error_f,
                "f_absolute_error":abs(result.occupation_face-reference_f),
                "energy_relative_error":rel_energy,
                "mu_absolute_error":mu_error,
                "measured_wall_s":took,
                "geometry_integrator":"second-order midpoint, stored snap interpolant",
                "source_integrator":"positive source-bound proper-time exponential update",
            })

    source_walls=[]
    for bound in (False, True):
        times=[]
        for repeat in range(5):
            _,duration=_orbit(model,128,257,inc,
                lambda l,nu:_source_rates(l,nu)[0],
                lambda l,nu:_source_rates(l,nu)[1],
                source_bound=bound)
            times.append(duration)
        source_walls.append({"path":"positive_rate_log_interval" if bound else "legacy_midpoint_H",
                             "median_wall_s":statistics.median(times),
                             "sample_wall_s":times,"repeats":5})

    strong=[]
    for chi in (0.0,1e-20,1e-17,1e-12,1e-8):
        # Optical depths from zero up to saturated, with nonnegative rates.
        emissivity=chi*.4 if chi>0 else 3e-20
        result,_=_orbit(model,64,65,inc,
             lambda l,nu:emissivity,lambda l,nu:chi)
        oracle=constant_coefficient_transfer(
             f_initial=INITIAL_OCCUPATION,emissivity_s_inv=emissivity,
             opacity_s_inv=chi,travel_time_s=inc.delta_t_s)
        err=abs(result.occupation_face-oracle)
        if err>3e-12:raise AssertionError(("opacity",chi,err))
        strong.append({"chi_s_inv":chi,"j_s_inv":emissivity,
            "optical_depth":chi*inc.delta_t_s,"f":result.occupation_face,
            "abs_error":err})

    # Guard the near-roundtrip defect from the previous implementation.
    tiny=model.interval_log(0.,1e-14)
    a0=model.a_ref
    collapsed=sum(
        a0*math.exp(i*1e-14/256)==a0*math.exp((i+1)*1e-14/256)
        for i in range(256)
    )
    if collapsed<1:raise AssertionError("round-trip counterexample no longer reproducible")
    return {
        "schema":SOURCE_VERSION,
        "scientific_status":"SCOPED_C8_NUMERIC_CONVERGENCE_ONLY",
        "q_cases":list(q_cases),
        "mesh_method":"1024 Hermite cells; binary64 stored log coordinates",
        "log_method_identity":model.interval_log(0.,1e-14).method_identity,
        "physical_background_identity":model.source_sha256,
        "legacy_midpoint_method_identity":"rec_legacy_midpoint_H_per_step",
        "numeric_precision_source":"mpmath70 frozen binary64 parameters and exact dyadic endpoints",
        "tiny_previous_scale_roundtrip_collapsed_substeps":collapsed,
        "tiny_positive_seconds":tiny.delta_t_s,
        "endpoint_checks":checks,
        "max_abs_clock_rel_error":max(abs(x["dt_relative_error"]) for x in checks),
        "max_abs_shear_rel_error":max(abs(x["db_relative_error"]) for x in checks),
        "time_varying_oracle":"SciPy DOP853 independent analytic H formula",
        "time_varying_oracle_occupation":reference_f,
        "null_oracle":"exact conserved spatial momenta with 70-digit shear quadrature",
        "refinement":rows,
        "timing":source_walls,
        "opacity":strong,
        "not_admitted":["nonlinear HyRec gas/photon energy conservation",
            "full original reionization histories",
            "native REI driver changed-path acceptance",
            "scientific detection or observational constraint"],
        "next_stage":"C9_independent_code_and_science_review",
    }


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--out",type=Path,required=True)
    args=parser.parse_args()
    if args.out.exists():parser.error("output exists, refusing overwrite")
    result=measure()
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,indent=2))
    print(json.dumps({
        "schema":result["schema"],"q_cases":result["q_cases"],
        "endpoint_count":len(result["endpoint_checks"]),
        "max_abs_clock_rel_error":result["max_abs_clock_rel_error"],
        "max_abs_shear_rel_error":result["max_abs_shear_rel_error"],
        "tiny_previous_scale_roundtrip_collapsed_substeps":
          result["tiny_previous_scale_roundtrip_collapsed_substeps"],
        "last_refinement":result["refinement"][-1],
        "timing":result["timing"],
        "opacity":result["opacity"],
    },indent=2))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
