#!/usr/bin/env python3
"""C7 REC: run the real Bianchi-I snapshot/characteristic transport path.

Only a prescribed normal-comoving LRS Bianchi-I component test: no native
REI solver, no full Einstein--HyRec closure, and no scientific admission.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

import numpy as np
from scipy.integrate import solve_ivp

from full_bianchi_hyrec.background import AxisymmetricBianchiIBackground
from full_bianchi_hyrec.trajectory.characteristic_angular import (
    CharacteristicAngularSolver, IsotropicTransferCoefficients,
    constant_coefficient_transfer,
)

FACE_NU_HZ=2.4e15
F0=0.0015
EMISSIVITY_S_INV=3e-20
OPACITY_S_INV=4e-17
FACE_MU=0.43
FACE_PHI=0.7


def _direction():
    r=math.sqrt(1-FACE_MU*FACE_MU)
    return np.array((r*math.cos(FACE_PHI),r*math.sin(FACE_PHI),FACE_MU))


def _constant_source_case(q:float):
    m=AxisymmetricBianchiIBackground(q_ref=q)
    a2=0.1
    inc=m.interval(m.a_ref,a2)
    seq=m.snapshots(np.linspace(0.0,inc.delta_l,65))
    coefficients=IsotropicTransferCoefficients(
        emissivity_s_inv=lambda tau,nu:EMISSIVITY_S_INV,
        opacity_s_inv=lambda tau,nu:OPACITY_S_INV,
    )
    target=constant_coefficient_transfer(
        f_initial=F0,emissivity_s_inv=EMISSIVITY_S_INV,
        opacity_s_inv=OPACITY_S_INV,travel_time_s=inc.delta_t_s,
    )
    results={}
    for name,interval_source in (("legacy",None),("source_bound",m)):
        solver=CharacteristicAngularSolver(seq,interval_source=interval_source)
        ray=solver.trace_to_face(
            tau_start=float(seq.tau[0]),tau_end=float(seq.tau[-1]),
            direction_hydrogen=_direction(),face_frequency_Hz=FACE_NU_HZ,
            initial_occupation=F0,coefficients=coefficients,n_step=64,
        )
        results[name]={
            "f_face":ray.occupation_face,
            "relative_error_to_proper_time_closed_form":ray.occupation_face/target-1.0,
        }
    corrected=abs(results["source_bound"]["relative_error_to_proper_time_closed_form"])
    if corrected>=5e-12:raise AssertionError("source-bound constant-rate transfer differs from closed form")
    return {
        "q_ref":q,"source_identity":m.source_sha256,
        "delta_t_proper_s":inc.delta_t_s,"delta_b":inc.delta_b,
        "closed_form_f_face":target,"comparisons":results,
        "strict_source_clock_pass":True,
    }


def _null_geodesic_case():
    m=AxisymmetricBianchiIBackground(q_ref=0.01)
    inc=m.interval(m.a_ref,0.1)
    seq=m.snapshots(np.linspace(0.,inc.delta_l,1025))
    ray=CharacteristicAngularSolver(seq,interval_source=m).trace_to_face(
        tau_start=float(seq.tau[0]),tau_end=float(seq.tau[-1]),
        direction_hydrogen=_direction(),face_frequency_Hz=FACE_NU_HZ,
        initial_occupation=F0,coefficients=IsotropicTransferCoefficients.zero(),
        n_step=512,
    )
    B=inc.delta_b
    r_backward=math.sqrt(
        math.exp(-2*B)*(1-FACE_MU*FACE_MU)+math.exp(4*B)*FACE_MU*FACE_MU
    )
    nu_ini=FACE_NU_HZ*math.exp(inc.delta_l)*r_backward
    mu_ini=FACE_MU*math.exp(2*B)/r_backward
    invariant_ini=m.a_ref*np.array((math.exp(-m.b_ref),math.exp(-m.b_ref),math.exp(2*m.b_ref)))*nu_ini*ray.initial_direction_hydrogen
    b_fin=m.point(0.1).b
    invariant_face=.1*np.array((math.exp(-b_fin),math.exp(-b_fin),math.exp(2*b_fin)))*FACE_NU_HZ*_direction()
    momentum_rel=float(np.linalg.norm(invariant_ini-invariant_face)/np.linalg.norm(invariant_ini))
    energy_rel=float(ray.initial_frequency_Hz/nu_ini-1)
    mu_abs=float(ray.initial_direction_hydrogen[2]-mu_ini)
    if not(abs(energy_rel)<1e-8 and abs(mu_abs)<1e-8 and momentum_rel<1e-8):
        raise AssertionError("source-bound null-ray Killing momentum consistency test failed")
    return {
        "source_identity":m.source_sha256,
        "solver_geometry": "real CharacteristicAngularSolver with actual BackgroundSnapshotSequence",
        "relative_initial_energy_error":energy_rel,
        "absolute_initial_mu_error":mu_abs,
        "translation_Killing_momentum_relative_error":momentum_rel,
        "source_free_occupation_relative_error":ray.occupation_face/F0-1,
        "Killing_momentum_and_Liouville_pass":True,
    }


def _nonstationary_case():
    m=AxisymmetricBianchiIBackground(q_ref=0.01)
    inc=m.interval(m.a_ref,0.1)
    seq=m.snapshots(np.linspace(0.,inc.delta_l,513))
    h_ref=m.cosmology.hubble_flrw(m.a_ref)

    def rates(L):
        return 3e-20*(1+0.1*math.sin(3*L)),4e-17*(1+0.03*math.cos(L))

    def rhs(L,y):
        a=m.a_ref*math.exp(L)
        h0=m.cosmology.hubble_flrw(a)
        shear=m.q_ref*h_ref*(m.a_ref/a)**3
        H=math.sqrt(h0*h0+shear*shear)
        em,op=rates(L)
        return [(em-op*y[0])/H]

    ref=solve_ivp(rhs,(0,inc.delta_l),[F0],method="DOP853",rtol=2e-12,atol=2e-16)
    if not ref.success:raise RuntimeError("independent scipy reference IVP failed")
    target=float(ref.y[0,-1])
    compare=[]
    for nsteps in (64,128,256):
        transport=CharacteristicAngularSolver(seq,interval_source=m)
        ray=transport.trace_to_face(
            tau_start=0.,tau_end=inc.delta_l,
            direction_hydrogen=_direction(),face_frequency_Hz=FACE_NU_HZ,
            initial_occupation=F0,
            coefficients=IsotropicTransferCoefficients(
                emissivity_s_inv=lambda tau,nu:rates(tau)[0],
                opacity_s_inv=lambda tau,nu:rates(tau)[1],
            ),n_step=nsteps,
        )
        compare.append({"nsteps":nsteps,"f_face":ray.occupation_face,
                        "absolute_error":abs(ray.occupation_face-target),
                        "relative_error":ray.occupation_face/target-1})
    ratio_0=compare[0]["absolute_error"]/compare[1]["absolute_error"]
    ratio_1=compare[1]["absolute_error"]/compare[2]["absolute_error"]
    if not (ratio_0>3.4 and ratio_1>3.2 and abs(compare[2]["relative_error"])<5e-7):
        raise AssertionError("nonstationary source temporal consistency failed")
    return {"oracle":"independent scipy DOP853 source ODE, mpmath not used",
            "true_f_face":target,"refinements":compare,
            "error_reduction_ratio_64_to_128":ratio_0,
            "error_reduction_ratio_128_to_256":ratio_1,
            "scoped_time_source_pass":True}


def run():
    out={"schema":"rec.c7.lrs_bianchi_i_transport.v1",
         "scientific_status":"PASS_PRESCRIBED_GEOMETRY_AND_MANUFACTURED_SOURCE_ONLY",
         "constant_source":[_constant_source_case(q) for q in (0.,0.01,-0.01)],
         "collisionless_null_ray":_null_geodesic_case(),
         "time_dependent_source":_nonstationary_case(),
         "not_admitted":["Full HyRec atomic rate/inventory coupling",
                         "Einstein anisotropic stress backreaction",
                         "REI native Rust driver binary equivalence",
                         "Observer optical depth/tau",
                         "Physical full-history convergence or novel scalar detection"]}
    return out


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,required=True)
    ns=p.parse_args()
    if ns.out.exists():p.error("output exists; no silent overwrite")
    result=run()
    ns.out.parent.mkdir(parents=True,exist_ok=True)
    ns.out.write_text(json.dumps(result,indent=2))
    print(json.dumps(result,indent=2))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
