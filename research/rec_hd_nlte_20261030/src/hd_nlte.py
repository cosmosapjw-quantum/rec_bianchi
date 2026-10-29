"""Source-visible-text HD cooling model. NEVER a replacement for pinned owner/source gate.

Source: official LAMDA hd.dat 7 June 2021 visible text transcription;
not original exact 2289-byte raw file and not a CDMS2011v2 re-fit.

Analytic 2-level J1->0 line source gate PASS within pinned 35Hz; 9-level
calculations are physical model diagnostics ONLY, full ladder fails that source gate.
"""
from __future__ import annotations
from decimal import Decimal, localcontext
from pathlib import Path
from typing import Any
import json
import math
import numpy as np
from scipy.linalg import solve

C = 299792458.0
H = 6.62607015e-34
KB = 1.380649e-23
SOURCE_GATE_HZ=35


def _require(condition: bool, message: str) -> None:
    # Source guard stays active under python -O.
    if not condition:
        raise ValueError(message)


def read_source(path: str|Path) -> dict[str,Any]:
    src=json.loads(Path(path).read_text(encoding="utf-8"))
    _require(src["schema"]=="REC_HD_LAMDA_20210607_SOURCE_TRANSCRIPTION_V1", "invalid source schema")
    _require(not src["exact_source_bytes_acquired"], "source transcription cannot self-certify original raw bytes")
    _require(len(src["levels"])==9 and len(src["radiative_lines"])==8, "HD shape mismatch")
    _require(len(src["collision_partner_para_H2"]["rates_cm3_s1"])==9, "para collision shape")
    _require(len(src["collision_partner_ortho_H2"]["rates_cm3_s1"])==9, "ortho collision shape")
    _require(src["temperature_nodes_K"]==[50,100,200], "temperature nodes unqualified")
    for j,lvl in enumerate(src["levels"]):
        _require(lvl["J"]==j and Decimal(lvl["g"]) == Decimal(2*j+1), "level J/degeneracy mismatch")
    for j,line in enumerate(src["radiative_lines"],start=1):
        _require(line["upper_J"]==j and line["lower_J"]==j-1, "radiative graph mismatch")
        _require(Decimal(line["A_s1"])>0 and Decimal(line["nu_GHz"])>0, "nonpositive radiative fields")
    base=[(p["upper_J"],p["lower_J"]) for p in src["collision_partner_para_H2"]["rates_cm3_s1"]]
    alt=[(p["upper_J"],p["lower_J"]) for p in src["collision_partner_ortho_H2"]["rates_cm3_s1"]]
    _require(len(set(base))==9 and base==alt, "collision partner graph mismatch")
    _require(set(base)=={(u,u-1) for u in range(1,9)}|{(2,0)}, "unexpected source collision edge")
    for q in (src["collision_partner_para_H2"],src["collision_partner_ortho_H2"]):
        _require(all(len(x["values"])==3 and all(Decimal(v)>0 for v in x["values"]) for x in q["rates_cm3_s1"]), "invalid collision rates")
    _require(src["2011_source_gate_pass_J"]==[1] and src["2011_source_gate_fail_J"]==list(range(2,9)), "frozen original gate changed")
    return src


def j1_gap_Hz_exact(src:dict[str,Any])->Decimal:
    with localcontext() as c:
        c.prec=70
        return (Decimal(src["levels"][1]["E_cm1"])-Decimal(src["levels"][0]["E_cm1"]))*Decimal(100)*Decimal(299792458)


def j1_source_gap_check(src):
    with localcontext() as c:
        c.prec=70
        nuP=Decimal(src["radiative_lines"][0]["nu_GHz"])*Decimal(10)**9
        diff=j1_gap_Hz_exact(src)-nuP
        _require(abs(diff)<SOURCE_GATE_HZ, f"J1 source gap exceeded frozen 35Hz gate: {diff}")
        return {"nuE_minus_nuP_Hz":str(diff),"frozen_gate_Hz":SOURCE_GATE_HZ,"line_1":"PASS", "lines_2_to_8":"FAIL_UNCHANGED"}


def mixed_q10(src, T:int, ortho_fraction:float)->float:
    if type(T) is not int or T not in (50,100,200):raise ValueError("T must be actual source node")
    if not math.isfinite(ortho_fraction) or not 0 <= ortho_fraction <= 1: raise ValueError("fraction outside [0,1]")
    i=src["temperature_nodes_K"].index(T)
    qp=float(src["collision_partner_para_H2"]["rates_cm3_s1"][0]["values"][i]);qo=float(src["collision_partner_ortho_H2"]["rates_cm3_s1"][0]["values"][i])
    return (1-ortho_fraction)*qp+ortho_fraction*qo


def two_level(src,T:int,nH2_cm3:float,ortho_fraction:float)->dict[str,float]:
    if not math.isfinite(nH2_cm3) or nH2_cm3<0:raise ValueError("nonfinite or negative collider density")
    q10=mixed_q10(src,T,ortho_fraction)
    gap=float(j1_gap_Hz_exact(src));nuP=float(src["radiative_lines"][0]["nu_GHz"])*1e9
    A=float(src["radiative_lines"][0]["A_s1"])
    b=(float(src["levels"][1]["g"])/float(src["levels"][0]["g"]))*math.exp(-H*gap/(KB*T))
    q01=q10*b;C10=nH2_cm3*q10;C01=nH2_cm3*q01
    p1= C01/(A+C01+C10)
    cool_p=A*p1*H*nuP
    cool_e=A*p1*H*gap
    eqb=q01/(q01+q10)
    n_half=A/(q01+q10)
    return {"T_K":T,"nH2_cm3":nH2_cm3,"ortho_fraction":ortho_fraction,
            "q10_cm3_s":q10,"q01_cm3_s":q01,"A10_s":A,
            "population_J1":p1,"population_J0":1-p1,
            "pJ1_LTE":eqb,"n_half_cooling_cm3":n_half,
            "cool_photon_W_per_HD":cool_p,"cool_gap_energy_W_per_HD":cool_e,
            "source_frequency_consistency_defect_W_per_HD":cool_e-cool_p,
            "collisional_energy_exchange_W_per_HD":H*gap*(C01*(1-p1)-C10*p1),
            "upper_spontaneous_events_s_per_HD":A*p1,
            "high_density_limit_photon_W_per_HD":A*eqb*H*nuP}


def full_generator(src,T:int,nH2_cm3:float,ortho_fraction:float)->np.ndarray:
    if type(T) is not int or T not in (50,100,200):raise ValueError("T outside actual source nodes")
    if not math.isfinite(nH2_cm3) or nH2_cm3<0:raise ValueError("invalid nH2")
    if not math.isfinite(ortho_fraction) or not 0 <= ortho_fraction <= 1:raise ValueError("invalid ortho fraction")
    Q=np.zeros((9,9),dtype=float)
    def insert(u:int,l:int,rate:float):
        _require(u!=l and rate>=0 and math.isfinite(rate), "invalid generator transition")
        Q[l,u]+=rate;Q[u,u]-=rate
    for l in src["radiative_lines"]:
        insert(l["upper_J"],l["lower_J"],float(l["A_s1"]))
    a=src["collision_partner_para_H2"]["rates_cm3_s1"]
    b=src["collision_partner_ortho_H2"]["rates_cm3_s1"]
    for item,other in zip(a,b):
        u,l=item["upper_J"],item["lower_J"]
        ind=src["temperature_nodes_K"].index(T)
        qdown=(1-ortho_fraction)*float(item["values"][ind])+ortho_fraction*float(other["values"][ind])
        boltz=(2*u+1)/(2*l+1)*math.exp(-H*C*100*(float(src["levels"][u]["E_cm1"])-float(src["levels"][l]["E_cm1"]))/(KB*T))
        insert(u,l,nH2_cm3*qdown)
        insert(l,u,nH2_cm3*qdown*boltz)
    return Q


def full_nlte(src,T:int,nH2_cm3:float,ortho_fraction:float)->dict[str,Any]:
    Q=full_generator(src,T,nH2_cm3,ortho_fraction)
    B=Q.copy();B[-1,:]=1.0
    b=np.zeros(9);b[-1]=1.0
    p=solve(B,b,assume_a='gen',check_finite=True)
    minp=float(min(p));norm_err=float(abs(p.sum()-1));residual=float(max(abs(Q@p)))
    # Important: no clipping/re-normalization of individual populations; tiny signed
    # high-J values at low T are recorded as numerical condition limits, not physics.
    ok=(minp>=-1e-12 and norm_err<=1e-10 and residual<=max(1e-18,float(max(-np.diag(Q)))*1e-11))
    vals=[];total_p=0.;total_e=0.
    for line in src["radiative_lines"]:
        u,l=line["upper_J"],line["lower_J"]
        A=float(line["A_s1"]); nuP=float(line["nu_GHz"])*1e9
        nuE=C*100*(float(src["levels"][u]["E_cm1"])-float(src["levels"][l]["E_cm1"]))
        wP=float(p[u])*A*H*nuP;wE=float(p[u])*A*H*nuE
        vals.append({"upper_J":u,"nuP_Hz":nuP,"nuE_Hz":nuE,"power_printed_W_per_HD":wP,"power_internal_gap_W_per_HD":wE,"population_upper":float(p[u])})
        total_p+=wP;total_e+=wE
    return {"T_K":T,"nH2_cm3":nH2_cm3,"ortho_fraction":ortho_fraction,
            "populations":p.tolist(),"minimum_population":minp,"sum_error":norm_err,"stationary_residual_s1":residual,
            "valid_numerical_solution":ok,"source_policy":"SOURCE_ONLY_FULL9_DIAGNOSTIC_FAIL7_OF8_NO_PHYSICAL_ADMISSION",
            "total_printed_power_W_per_HD":total_p,"total_internal_gap_power_W_per_HD":total_e,
            "power_difference_W_per_HD":total_e-total_p,"lines":vals}


def lte(src,T:int)->list[float]:
    vals=np.array([(2*j+1)*math.exp(-H*C*100*float(e["E_cm1"])/(KB*T)) for j,e in enumerate(src["levels"])],dtype=float)
    return (vals/vals.sum()).tolist()


def emit_dataset(src:dict[str,Any])->dict[str,Any]:
    dens=[0,1,100,10_000,1_000_000,100_000_000,10_000_000_000]
    temps=[50,100,200];fractions=[0,0.5,1]
    two=[two_level(src,T,n,f) for T in temps for n in dens for f in fractions]
    full=[full_nlte(src,T,n,f) for T in temps for n in dens for f in fractions]
    raw={"schema":"REC_HD_NONLTE_PHYSICAL_DATA_V1","source":"Official LAMDA June 2021 hd.dat transcribed visible numeric fields; not original raw bytes","nH2_unit":"cm^-3","density_grid":dens,"temperature_grid":temps,"ortho_fraction_grid":fractions,"radiation_background":"none; vacuum optically thin","two_level_scope":"J1->0 frozen35Hz gate PASS; physical source-conditional","full9_scope":"UNQUALIFIED source field discrepancy J2..8; math/physics diagnostic only","source_gate":j1_source_gap_check(src),"two_level_rows":two,"full9_rows":full}
    return raw

if __name__=="__main__":
    import argparse
    ap=argparse.ArgumentParser();ap.add_argument("--source",required=True);ap.add_argument("--output",required=True)
    args=ap.parse_args();data=emit_dataset(read_source(args.source));Path(args.output).write_text(json.dumps(data,indent=2,ensure_ascii=False,allow_nan=False)+"\n",encoding="utf-8")
    print(json.dumps({"two_level":len(data["two_level_rows"]),"full9":len(data["full9_rows"]),"valid_full9":sum(x["valid_numerical_solution"] for x in data["full9_rows"]),"bad_full9":sum(not x["valid_numerical_solution"] for x in data["full9_rows"]),"source_gate":data["source_gate"]},indent=2))