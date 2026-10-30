"""HD J=0..14 CMB-coupled statistical equilibrium from frozen Neufeld 2026 source.

No astrophysical history IVP. No substitution into the CDMS2011 owner model.
The source must be Neufeld 2026 v2 original `hd_lamda.dat` with SHA256 verified.
"""
from __future__ import annotations
import argparse, json, math
from pathlib import Path
from pr169_neufeld15_reference import (parse_lamda, m_matrix_positive_solve,
    H, C, K_B, SI_CONVERSION, Model)

TCMB0_K=2.72548
DEFAULT_TEMP_K=(100.,200.,400.,1000.)
DEFAULT_DENS_CM3=(100.,1e4,1e6,1e8)
DEFAULT_REDSHIFT=(0.,10.,30.,50.,73.,100.)


def planck_number(nu_hz: float, bath_K: float) -> float:
    if nu_hz <= 0 or bath_K <= 0:
        raise ValueError('positive frequency and CMB temperature required')
    x = H*nu_hz/(K_B*bath_K)
    return 0.0 if x>700 else 1.0/math.expm1(x)


def solve_cmb(model:Model,Tgas_K:float,nH2_cm3:float,z:float,*,f_ortho:float=.75,
              background:bool=True)->dict:
    if Tgas_K<=0 or nH2_cm3<=0 or z<0 or not 0<=f_ortho<=1:
        raise ValueError('Nonphysical T, density, z, ortho fraction')
    nlev=len(model.levels)
    M=[[0.]*nlev for _ in range(nlev)]
    def add(u,l,r):
        M[l][u]+=r
        M[u][u]-=r
    Tbg=TCMB0_K*(1+z)
    nbar=[]
    for (u,l,A,nu) in model.rad:
        nb=planck_number(nu,Tbg) if background else 0.0
        nbar.append(nb)
        add(u,l,A*(1+nb))
        if background:
            add(l,u,A*model.levels[u][2]/model.levels[l][2]*nb)
    pt,para=model.collision[2]
    ot,ortho=model.collision[3]
    if pt!=ot or Tgas_K not in pt or set(para)!=set(ortho):
        raise ValueError('Only exact original-source temperature and matched collider rows')
    ti=pt.index(Tgas_K)
    for (u,l),rates in para.items():
        d=nH2_cm3*((1-f_ortho)*rates[ti]+f_ortho*ortho[(u,l)][ti])
        ju,eu,gu=model.levels[u]
        jl,el,gl=model.levels[l]
        up=d*(gu/gl)*math.exp(-SI_CONVERSION*(eu-el)/Tgas_K)
        add(u,l,d)
        add(l,u,up)
    pop=m_matrix_positive_solve(M)
    lines=[]
    for (u,l,A,nu),nb in zip(model.rad,nbar):
        energy=H*nu
        s=pop[u]*A*energy
        stimulated=s*nb
        absorbed=pop[l]*A*(model.levels[u][2]/model.levels[l][2])*nb*energy
        lines.append({'J_upper':model.levels[u][0], 'J_lower':model.levels[l][0],
            'nu_Hz':nu, 'spontaneous_W_per_HD':s,
            'stimulated_W_per_HD':stimulated,
            'absorbed_W_per_HD':absorbed,
            'net_W_per_HD':s+stimulated-absorbed})
    residual=max(abs(sum(M[i][j]*pop[j] for j in range(nlev))) for i in range(nlev))
    return {'Tgas_K':Tgas_K,'nH2_cm3':nH2_cm3,'z':z,'Tbg_K':Tbg,
        'populations_J0_to_J14':pop,'net_cooling_W_per_HD':sum(r['net_W_per_HD'] for r in lines),
        'spont_power_W_per_HD':sum(r['spontaneous_W_per_HD'] for r in lines),
        'max_stationary_residual_s_inverse':residual,'sum_pop':sum(pop),
        'line_power_records':lines}


def grid(model:Model,Ts=DEFAULT_TEMP_K,densities=DEFAULT_DENS_CM3,zs=DEFAULT_REDSHIFT):
    result=[]
    for T in Ts:
        for n in densities:
            for z in zs:
                result.append(solve_cmb(model,T,n,z))
    return result


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--source',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    model=parse_lamda(args.source.read_bytes(),verify=True)
    if len(model.levels)!=15 or len(model.rad)!=14 or len(model.collision[2][1])!=105:
        raise ValueError('Original 2026 HD source structure mismatch')
    results=grid(model)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(results,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'states':len(results),'line_records':sum(len(r['line_power_records']) for r in results),
       'original_source_sha256':model.source_sha256,'owner_35Hz':'FAIL7/8',
       'canonical_DAG':'28/88','REC_physical_DAG':'0/313','production':'HOLD'}))
if __name__=='__main__':main()
