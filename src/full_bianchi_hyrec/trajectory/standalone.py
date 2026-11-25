"""REC-owned independent hydrogen/temperature history (bounded HMLA lane).
Only primitive atomic rate bytes inherited. No external recombination
history, executable, or C FFI. Neutral helium, flat FLRW, no FULL transfer.
"""
from __future__ import annotations
import argparse, hashlib, json, math
from pathlib import Path
import numpy as np
from .primitive_rates import OriginalHyRecPrimitiveRateTable, LYMAN_ALPHA_ENERGY_EV
from .hmla_flrw import HMLAFlrwSource, integrate_hmla_hydrogen, KB_NATIVE_EV_K, LYA_FACT_CM3, LAMBDA_2S1S_S_INV
from .primordial_2012_helium import HyRec2012Cosmology

def make_source(table, c=HyRec2012Cosmology()):
    if c.omega_k_h2!=0 or c.w0!=-1 or c.wa!=0 or c.fsR!=1 or c.meR!=1:
        raise ValueError("standalone HMLA scope: flat constant-Lambda, standard atomic constants")
    radiation=4.48162687719e-7*c.T0_K**4*(1+0.227107317660239*c.N_eff)
    hh=c.omega_m_h2+radiation+c.omega_de_h2
    return HMLAFlrwSource(math.sqrt(hh),c.omega_m_h2/hh,radiation,c.omega_de_h2,c.omega_b_h2,c.YHe,c.T0_K,table)

def ground_state(source,z,xp,tm):
    """QSS excited-state population estimate consistent with the HMLA
    neutral-as-ground escape closure, not a FULL excited-level trajectory.
    Solve the two real-state balances plus retained H abundance exactly."""
    H,n=source.cosmology(z);tr=source.tcmb0_K*(1+z)
    t=KB_NATIVE_EV_K*tr
    rates=source.table.evaluate(radiation_temperature_eV_rescaled=t,matter_to_radiation_temperature_ratio=tm/tr)
    bs,bp=rates.beta_s_inv;R=rates.R_2p2s_s_inv;L=LAMBDA_2S1S_S_INV
    neutral=1-xp
    ly=LYA_FACT_CM3*H/(n*1e-6*neutral)
    w=math.exp(-LYMAN_ALPHA_ENERGY_EV/t)
    # Eliminate x1s = neutral - xs - xp2, avoiding badly scaled
    # abundance row in the solve. Recombination uses actual xp*xe=xp^2.
    A=np.array([[bs+3*R+L+L*w,-R+L*w],[-3*R+3*ly*w,bp+R+ly+3*ly*w]])
    rhs=n*rates.alpha_m3_s*xp*xp+np.array([L,3*ly])*neutral*w
    s,p=np.linalg.solve(A,rhs);g=neutral-s-p
    if min(g,s,p)<0 or not np.isfinite([g,s,p]).all():
        raise ValueError("QSS retained-state population outside simplex")
    res=A@np.array([s,p])-rhs
    return dict(z=float(z),T_r_K=float(tr),T_m_K=float(tm),H_s=float(H),n_H_m3=float(n),x_HII=float(xp),x_1s=float(g),x_2s=float(s),x_2p=float(p),n_1s_m3=float(n*g),qss_relative_residual=float(np.max(abs(res))/max(np.max(abs(rhs)),1e-300)),neutral_as_ground_relative_error=float((s+p)/neutral),population_scope="HMLA_retained_QSS_neutral_escape")

def independent_history(archive,*,z_initial=1600.,z_end=900.,points=701,rtol=1e-9,atol=1e-11,method="BDF",initialization="post_saha",cosmology=HyRec2012Cosmology()):
    table=OriginalHyRecPrimitiveRateTable.from_archive(archive)
    source=make_source(table,cosmology)
    h=integrate_hmla_hydrogen(source,z_initial=z_initial,z_final=z_end,points=points,rtol=rtol,atol=atol,method=method,initialization=initialization)
    states=[ground_state(source,z,x,t) for z,x,t in zip(h.z,h.x_HII,h.Tm_K)]
    return dict(schema="rec_bianchi.independent_hmla/1",scope=h.source_mode,history_owner="REC_BIANCHI",runtime_dependencies=["numpy","scipy"],external_hyrec_runtime=False,external_history=False,rate_hashes=dict(table.source_hashes),cosmology={k:getattr(cosmology,k) for k in cosmology.__dataclass_fields__},initialization=initialization,method=method,rtol=rtol,atol=atol,states=states)

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--rates",type=Path,required=True);p.add_argument("--out",type=Path,required=True)
    p.add_argument("--z-start",type=float,default=1600.);p.add_argument("--z-end",type=float,default=900.);p.add_argument("--points",type=int,default=701)
    p.add_argument("--rtol",type=float,default=1e-9);p.add_argument("--atol",type=float,default=1e-11);p.add_argument("--method",choices=["BDF","Radau"],default="BDF")
    a=p.parse_args();h=independent_history(a.rates,z_initial=a.z_start,z_end=a.z_end,points=a.points,rtol=a.rtol,atol=a.atol,method=a.method)
    with a.out.open("x") as f:json.dump(h,f,indent=2,allow_nan=False)
if __name__=="__main__":main()
