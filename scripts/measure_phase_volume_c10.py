#!/usr/bin/env python3
"""Independent R1/C10 photon-number and anisotropic-energy quadrature.

Only collisionless photon phase-volume mapping for a prescribed, non-tilted LRS
Bianchi-I background. The moment identities do not establish atomic source,
Thomson scattering, photoheating, or coupled reionization-history convergence.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import time
import statistics

import mpmath as mp
import numpy as np
from numpy.polynomial.legendre import leggauss

from full_bianchi_hyrec.background import AxisymmetricBianchiIBackground
from full_bianchi_hyrec.trajectory.axisymmetric_phase_space import (
    axisymmetric_phase_space_map,
    prepare_axisymmetric_phase_space_map,
)


def _mp_reference(model:AxisymmetricBianchiIBackground, end:float):
    mp.mp.dps=75
    c=model.cosmology
    h0=mp.mpf(float(c.h0_per_s))
    om=mp.mpf(float(c.omega_m))
    orad=mp.mpf(float(c.omega_r))
    ol=mp.mpf(float(c.omega_lambda))
    ar=mp.mpf(float(model.a_ref))
    s0=mp.mpf(float(model._s_ref))
    endmp=mp.mpf(float(end))

    def rate(x):
        a=ar*mp.exp(x)
        s=s0*mp.exp(-3*x)
        Hf=h0*mp.sqrt(om/a**3+orad/a**4+ol)
        H=Hf if model.same_h else mp.sqrt(Hf**2+s**2)
        return s/H

    B=-mp.quad(rate,[mp.mpf(0),endmp])
    def R(u):
        return mp.exp(2*B)*(1-u*u)+mp.exp(-4*B)*u*u
    energy=mp.quad(lambda u:R(u)**(-2),[-1,1])/2
    return float(B),float(energy)


def _angles(n:int=96):
    mu,w=leggauss(n)
    directions=np.column_stack((np.sqrt(1-mu*mu),np.zeros_like(mu),mu))
    return directions,w


def _moments(model,end,dirs,weights):
    m=axisymmetric_phase_space_map(model,0.,end,dirs)
    number=0.5*np.dot(weights,m.solid_angle_initial_over_face)
    anisotropy=0.5*np.dot(weights,m.solid_angle_initial_over_face**(4/3))
    expected_phase_volume=np.exp(3*end)
    jac_phase=m.energy_initial_over_face**3*m.solid_angle_initial_over_face
    max_relative=float(np.max(np.abs(jac_phase/expected_phase_volume-1)))
    return m,float(number),float(anisotropy),max_relative



def _performance(model,end):
    """Measure cold quadrature and prepared geometry separately."""
    def build(n):
        mu=np.linspace(-.99,.99,n)
        return np.column_stack((np.sqrt(1-mu*mu),np.zeros_like(mu),mu))
    prestart=time.perf_counter()
    prep=prepare_axisymmetric_phase_space_map(model,0.,end)
    prep_time=time.perf_counter()-prestart
    baseB=prep.delta_b_initial_minus_face

    measured=[]
    for N in (64,1024,8192):
        dirs=build(N)

        def scalar_prepared():
            # Independent scalar loop, with the same shear integral prepared
            # once as the vector path (no repeated cosmological background).
            out=[]
            perp=math.exp(baseB)
            axial=math.exp(-2*baseB)
            for mu in dirs[:,2]:
                R=math.sqrt(perp*perp*(1-mu*mu)+axial*axial*mu*mu)
                out.append((math.exp(end)*R,R**-3))
            return np.asarray(out)

        def vector_prepared():
            r=prep.map(dirs)
            return np.column_stack((r.energy_initial_over_face,
                                    r.solid_angle_initial_over_face))

        def vector_cold():
            r=axisymmetric_phase_space_map(model,0.,end,dirs)
            return np.column_stack((r.energy_initial_over_face,
                                    r.solid_angle_initial_over_face))

        for f in (scalar_prepared,vector_prepared,vector_cold):f()
        a=scalar_prepared();b=vector_prepared();c=vector_cold()
        max_rel=float(np.max(np.abs(a/b-1)))
        if max_rel>1e-12 or np.max(abs(b/c-1))>1e-15:
            raise AssertionError(("equal physics different prep paths",N,max_rel))
        timings={}
        for name,fn in (
            ("scalar_prepared",scalar_prepared),
            ("vector_prepared",vector_prepared),
            ("vector_cold",vector_cold),
        ):
            times=[]
            for _ in range(5):
                t=time.perf_counter()
                fn()
                times.append(time.perf_counter()-t)
            timings[name]={"median_s":statistics.median(times),
                           "samples_s":times}

        measured.append({
            "nrays":N,
            "source_prepare_once_s":prep_time,
            "scalar_prepared":timings["scalar_prepared"],
            "vector_prepared":timings["vector_prepared"],
            "vector_cold":timings["vector_cold"],
            "prepared_speedup_vs_scalar":
                timings["scalar_prepared"]["median_s"]/
                timings["vector_prepared"]["median_s"],
            "prepared_speedup_vs_cold":
                timings["vector_cold"]["median_s"]/
                timings["vector_prepared"]["median_s"],
            "max_relative_difference":max_rel,
        })
    return measured

def run():
    cases=[]
    nq=(0.,-.005,.005,-.01,.01)
    dirs,w=_angles()
    for q in nq:
        model=AxisymmetricBianchiIBackground(q_ref=q)
        last=math.log(.1/model.a_ref)
        r,number,energy,phase_error=_moments(model,last,dirs,w)
        B_exact,E_exact=_mp_reference(model,last)
        B_float=-model.interval_log(0.,last).delta_b
        if not (
            abs(number-1)<3e-14 and phase_error<4e-14
            and abs(energy-E_exact)<3e-14
            and (q==0 or abs(B_float/B_exact-1)<1e-9)
        ):
            raise AssertionError(("phase volume mismatch",q,number,energy,E_exact,phase_error))
        cases.append({
          "q_ref":q,"source_sha256":model.source_sha256,
          "initial_l":0.,"face_l":last,
          "B_initial_minus_face":B_float,
          "B_mpmath75":B_exact,
          "number_jacobian_full_sky_normalized":number,
          "energy_moment_full_sky_factor":energy,
          "energy_factor_mpmath75":E_exact,
          "cubic_phase_volume_max_relative_error":phase_error,
          "small_B_energy_series_4th":
            1+8/5*B_float**2+16/21*B_float**3+8/35*B_float**4,
        })
    lookup={x["q_ref"]:x for x in cases}
    def even(q):
        return ((lookup[q]["energy_moment_full_sky_factor"]-1)
               +(lookup[-q]["energy_moment_full_sky_factor"]-1))/2
    even_ratio=even(.01)/even(.005)
    if not (3.8 < even_ratio <4.2):
        raise AssertionError(("quadratic shear parity",even_ratio))
    benchmark=_performance(AxisymmetricBianchiIBackground(q_ref=.01),
                          lookup[.01]["face_l"])
    return {
       "schema":"rec.c10.phase_space_moment.v1",
       "model":"non-tilted axisymmetric prescribed Bianchi I, passive collisionless radiation",
       "conventions":{"signature":"-+++","log_scale":"L=ln(a/a_ref)",
          "number_density":"n_gamma(face)/n_gamma(initial)=(a_initial/a_face)^3 for isotropic initial f",
          "energy_density":"rho_gamma(face)/rho_gamma(initial)=(a_initial/a_face)^4 * mean_sky(R^-4)",
          "solid_angle":"dOmega_initial/dOmega_face=R^-3"},
       "source_reference":"independent mpmath 75-digit B and full-sky energy moment",
       "angles_gl_order":len(w),
       "cases":cases,
       "even_correction_q01_over_q005":even_ratio,
       "actual_matched_benchmark":benchmark,
       "not_claimed":["full-Boltzmann energy moment from evolving f",
         "ionizing photon absorption or heating ledger","native REI q family convergence",
         "Thomson scattering","novel observational signature or strong no-go"],
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    if a.out.exists():
        p.error("refuse to overwrite existing evidence")
    data=run()
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(data,indent=2))
    print(json.dumps({
       "q_even_ratio":data["even_correction_q01_over_q005"],
       "number_checks":[(x["q_ref"],x["number_jacobian_full_sky_normalized"])
                        for x in data["cases"]],
       "vectorized_benchmark":[(x["nrays"],x["prepared_speedup_vs_scalar"],x["max_relative_difference"])
                        for x in data["actual_matched_benchmark"]]
    },indent=2))


if __name__=="__main__":
    main()
