"""Structured solve helpers for the C3B1 HYREC native block."""
from __future__ import annotations
from pathlib import Path
import numpy as np

NVIRT=311
NSUBLYA=140
NDIFF=80
START=NSUBLYA-NDIFF//2
STOP=START+NDIFF

def thomas_solve(diagonal,upper,lower,rhs):
    n=len(diagonal)
    alpha=np.zeros(n); gamma=np.zeros(n); out=np.zeros(n)
    alpha[0]=upper[0]/diagonal[0]
    gamma[0]=rhs[0]/diagonal[0]
    for i in range(1,n):
        denom=diagonal[i]-lower[i]*alpha[i-1]
        alpha[i]=upper[i]/denom
        gamma[i]=(rhs[i]-lower[i]*gamma[i-1])/denom
    out[-1]=gamma[-1]
    for i in range(n-2,-1,-1):
        out[i]=gamma[i]-alpha[i]*out[i+1]
    return out

def solve_tvv(diagonal,upper,lower,rhs):
    out=np.empty_like(rhs,dtype=float)
    out[:START]=rhs[:START]/diagonal[:START]
    out[STOP:]=rhs[STOP:]/diagonal[STOP:]
    out[START:STOP]=thomas_solve(
        diagonal[START:STOP],upper[START:STOP],
        lower[START:STOP],rhs[START:STOP]
    )
    return out

def solve_snapshot(path):
    d=np.load(path)
    inv_tvr=np.vstack([
        solve_tvv(d["Tvv_diag"],d["Tvv_upper"],d["Tvv_lower"],d["Tvr"][i])
        for i in range(2)
    ])
    inv_sv=solve_tvv(d["Tvv_diag"],d["Tvv_upper"],d["Tvv_lower"],d["sv"])
    teff=d["Trr"]-d["Trv"]@inv_tvr.T
    seff=d["sr"]-d["Trv"]@inv_sv
    xr=np.linalg.solve(teff,seff)
    xv=inv_sv-inv_tvr.T@xr
    return np.concatenate([xr,xv])
