"""HYREC-2 native atomic-table adapter.

This module does not redistribute upstream data. Point it at a pinned
HYREC-2 checkout and it parses/interpolates the native tables.
"""
from __future__ import annotations
import math
from pathlib import Path
import numpy as np

TR_MIN, TR_MAX, NTR = 0.004, 0.4, 100
T_RATIO_MIN, T_RATIO_MAX, NTM = 0.1, 1.0, 40
NVIRT = 311
EI_EV = 13.598286071938324
K_BOLTZ_EV_PER_K = 8.617343e-5
SAHA_FACT_0 = 3.016103031869581e21


def cubic_weights(frac: float) -> np.ndarray:
    f=float(frac)
    return np.array([
        f*(f-1.0)*(2.0-f)/6.0,
        (1.0+f)*(1.0-f)*(2.0-f)/2.0,
        (1.0+f)*f*(2.0-f)/2.0,
        (1.0+f)*f*(f-1.0)/6.0,
    ])


def coordinate(value, minimum, maximum, count, logarithmic):
    if not minimum <= value <= maximum:
        raise ValueError("outside HYREC table range")
    if logarithmic:
        raw=(math.log(value)-math.log(minimum))/(
            (math.log(maximum)-math.log(minimum))/(count-1)
        )
    else:
        raw=(value-minimum)/((maximum-minimum)/(count-1))
    index=max(1,min(count-3,math.floor(raw)))
    frac=raw-index
    return index, frac, cubic_weights(frac)


def parse_alpha(path: str | Path) -> np.ndarray:
    values=np.loadtxt(path)
    if values.shape != (NTR*NTM,4):
        raise ValueError(f"unexpected Alpha table shape {values.shape}")
    return values.reshape(NTR,NTM,4)


def parse_r(path: str | Path) -> np.ndarray:
    values=np.loadtxt(path)
    if values.shape != (NTR,):
        raise ValueError(f"unexpected R table shape {values.shape}")
    return values


def parse_virtual(path: str | Path) -> np.ndarray:
    values=np.loadtxt(path)
    if values.shape != (NVIRT,5):
        raise ValueError(f"unexpected two-photon shape {values.shape}")
    return values


def _log4(values, weights):
    values=np.asarray(values)
    if np.any(values <= 0.0):
        raise ValueError("positive rate required for log interpolation")
    return float(np.exp(np.dot(np.log(values),weights)))


def interpolate_rates(alpha_table, r_table, Tm_K, Tr_K, fsR=1.0, meR=1.0):
    Tr=Tr_K*K_BOLTZ_EV_PER_K/(fsR*fsR*meR)
    ratio=Tm_K/Tr_K
    if ratio < T_RATIO_MIN:
        raise ValueError("Tm/Tr below HYREC range")
    if ratio > 1.0:
        t_ratio=1.0/ratio
        col_offset=2
    else:
        t_ratio=ratio
        col_offset=0

    iT,fT,wT=coordinate(Tr,TR_MIN,TR_MAX,NTR,True)
    iR,fR,wR=coordinate(t_ratio,T_RATIO_MIN,T_RATIO_MAX,NTM,False)

    alpha_eq=np.zeros(2)
    alpha=np.zeros(2)
    for level in range(2):
        alpha_eq[level]=(fsR/meR)**2*_log4(
            alpha_table[iT-1:iT+3,NTM-1,level],wT
        )
        temp=np.zeros(4)
        for row in range(4):
            temp[row]=_log4(
                alpha_table[
                    iT-1:iT+3,
                    iR-1+row,
                    level+col_offset
                ],
                wT,
            )
        alpha[level]=(fsR/meR)**2*_log4(temp,wR)

    saha=SAHA_FACT_0*(fsR*meR)**3
    beta=np.array([
        alpha_eq[level]*saha*Tr*math.sqrt(Tr)
        *math.exp(-0.25*EI_EV/Tr)/(2*level+1)
        for level in range(2)
    ])
    r2p2s=fsR**5*meR*_log4(r_table[iT-1:iT+3],wT)
    return {
        "Alpha":alpha,
        "Alpha_eq":alpha_eq,
        "DAlpha":alpha-alpha_eq,
        "Beta":beta,
        "R2p2s":r2p2s,
        "R2s2p":3.0*r2p2s,
    }
