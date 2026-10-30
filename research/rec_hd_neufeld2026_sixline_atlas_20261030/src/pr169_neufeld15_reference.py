"""Reproduce HD 15-level, two-collider optically thin non-LTE populations.

Physical scope: Neufeld (2026), source-authentic HD LAMDA-style input,
Wan et al. (2019) H2 rates at exact tabulated temperatures, fixed OPR=3,
spontaneous Einstein A emission, no external radiation.

The original 35 Hz CDMS 2011 v2 owner gate is NOT relaxed by this standalone
scientific benchmark. In particular, J>8 collision rates are source-extrapolated.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import NamedTuple

H = 6.62607015e-34  # J s, exact SI
C = 299792458.0  # m/s, exact SI
K_B = 1.380649e-23  # J/K, exact SI
SOURCE_CONVERSION = 1.4388  # K cm, empirically source-FITS-matched, not the SI conversion
SI_CONVERSION = 100 * H * C / K_B
NEUFELD_2026_SHA256 = 'f07f36fd56fe351fe4032235abbc863319b652838e635cd76bbf09664ce099cb'
SOURCE_T_GRID = (100., 200., 300., 400., 600., 1000., 2000., 3000., 4000.)

class Model(NamedTuple):
    levels: tuple[tuple[int, float, float], ...]  # (J, E/cm^-1, g)
    rad: tuple[tuple[int,int,float,float], ...]  # (upper index,lower index,A/s,Hz)
    collision: dict[int, tuple[tuple[float,...], dict[tuple[int,int],tuple[float,...]]]]
    source_sha256: str


def parse_lamda(contents: bytes, *, verify: bool = False) -> Model:
    digest = hashlib.sha256(contents).hexdigest()
    if verify and digest != NEUFELD_2026_SHA256:
        raise ValueError(f'Unexpected source bytes (SHA256 {digest})')
    # LAMDA human-readable section headings start with '!'. The collision
    # partner description lines (e.g., '2 HD-pH2...') are NOT comments.
    rows = [x.strip() for x in contents.decode('ascii').splitlines()
            if x.strip() and not x.lstrip().startswith('!')]
    cursor = 0
    def take() -> str:
        nonlocal cursor
        if cursor >= len(rows):
            raise ValueError('Truncated LAMDA source')
        x = rows[cursor]; cursor += 1
        return x
    species = take()
    if species != 'HD':
        raise ValueError(f'Not HD: {species}')
    mass = float(take())
    if not (2.8 < mass < 3.3):
        raise ValueError('Unexpected HD molecular weight')
    nlevels = int(take())
    levels=[]
    for ix in range(nlevels):
        data=take().split()
        if len(data)<4 or int(data[0])!=ix+1:
            raise ValueError('Bad energy-level row ordering')
        levels.append((int(data[3]),float(data[1]),float(data[2])))
    nrad=int(take())
    rad=[]
    for ix in range(nrad):
        data=take().split()
        if len(data)<5 or int(data[0])!=ix+1:
            raise ValueError('Bad radiative row ordering')
        up,lo=int(data[1])-1,int(data[2])-1
        A,Hz=float(data[3]),float(data[4])*1e9
        if not (0<=lo<up<nlevels and A>0 and Hz>0):
            raise ValueError('Invalid Einstein line')
        rad.append((up,lo,A,Hz))
    npart=int(take())
    collision={}
    for _ in range(npart):
        descriptor=take().split()
        partner=int(descriptor[0])
        if partner in collision:
            raise ValueError('Duplicate collision partner')
        ntrans=int(take())
        nt=int(take())
        ts=[]
        while len(ts)<nt:
            ts.extend(float(x) for x in take().split())
        if len(ts)!=nt:
            raise ValueError('Collision temperature grid mismatch')
        qs={}
        for index in range(ntrans):
            data=take().split()
            if len(data)!=3+nt or int(data[0])!=index+1:
                raise ValueError(f'Malformed collision-rate row {index+1}')
            up,lo=int(data[1])-1,int(data[2])-1
            if not 0<=lo<up<nlevels or (up,lo) in qs:
                raise ValueError('Invalid collision transition')
            values=tuple(map(float,data[3:]))
            if any(not math.isfinite(v) or v<=0 for v in values):
                raise ValueError('Nonpositive collision rate')
            qs[up,lo]=values
        collision[partner]=(tuple(ts),qs)
    if cursor!=len(rows):
        raise ValueError(f'Unexpected trailing source lines: {rows[cursor:cursor+2]}')
    if set(collision)!={2,3}:
        raise ValueError('Require separate para and ortho-H2 inputs')
    return Model(tuple(levels),tuple(rad),collision,digest)


def m_matrix_positive_solve(matrix: list[list[float]]) -> list[float]:
    """Solve a column-sum-zero CTMC generator using nonnegative M-matrix elimination.

    Anchors p[0]=1 before normalization. For an irreducible Markov generator,
    -L[1:,1:] is a nonsingular M-matrix and p[1:]/p[0]>=0.
    This avoids cancellation from replacing a delicate high-J balance row.
    """
    size=len(matrix)
    N=size-1
    A=[[-matrix[i+1][j+1] for j in range(N)] for i in range(N)]
    rhs=[matrix[i+1][0] for i in range(N)]
    for j in range(N):
        d=A[j][j]
        if not d>0 or not math.isfinite(d):
            raise ArithmeticError('M-matrix pivot not positive')
        for i in range(j+1,N):
            w=A[i][j]/d
            for k in range(j+1,N):
                A[i][k]-=w*A[j][k]
            rhs[i]-=w*rhs[j]
            A[i][j]=0.0
    x=[0.0]*N
    for i in range(N-1,-1,-1):
        s=rhs[i]-sum(A[i][j]*x[j] for j in range(i+1,N))
        x[i]=s/A[i][i]
    norm=1+sum(x)
    p=[1/norm]+[y/norm for y in x]
    if any(not math.isfinite(y) or y < 0 for y in p):
        raise ArithmeticError('M-matrix population positivity violated')
    if abs(sum(p)-1)>1e-10:
        raise ArithmeticError('Population normalization violated')
    return p


def solve(model:Model, temperature: float, density_cm3:float, *, conversion:float=SI_CONVERSION,
          ortho_fraction:float=0.75)->dict:
    if not 0<=ortho_fraction<=1 or density_cm3<=0:
        raise ValueError('Invalid physical density / H2 spin fraction')
    n=len(model.levels)
    M=[[0.]*n for _ in range(n)]
    def add(up:int,lo:int,r:float)->None:
        M[lo][up]+=r
        M[up][up]-=r
    for u,l,A,nu in model.rad:
        add(u,l,A)
    paraT,para=model.collision[2]
    orthoT,ortho=model.collision[3]
    if paraT!=orthoT or temperature not in paraT:
        raise ValueError('Only exact source-tabulated temperatures allowed')
    t=paraT.index(temperature)
    if set(para)!=set(ortho):
        raise ValueError('Source collisional edges mismatch')
    for (u,l),qpara in para.items():
        down=density_cm3*((1-ortho_fraction)*qpara[t]+ortho_fraction*ortho[u,l][t])
        ju,eu,gu=model.levels[u]
        jl,el,gl=model.levels[l]
        upward=down*gu/gl*math.exp(-conversion*(eu-el)/temperature)
        add(u,l,down)
        add(l,u,upward)
    p=m_matrix_positive_solve(M)
    lines=[p[u]*A*H*nu for u,l,A,nu in model.rad]
    resid=max(abs(sum(M[i][j]*p[j] for j in range(n))) for i in range(n))
    return {'temperature_K':temperature,'n_H2_cm3':density_cm3,'ortho_fraction':ortho_fraction,
            'populations':p,'line_spontaneous_power_W_per_HD':lines,
            'total_spontaneous_power_W_per_HD':sum(lines),
            'maximum_stationarity_residual_per_s':resid,
            'sum_populations':sum(p),'min_population':min(p)}


def run_at_source_temperatures(source:bytes,output_dir:Path)->dict:
    model=parse_lamda(source,verify=True)
    if len(model.levels)!=15 or len(model.rad)!=14 or len(model.collision[2][1])!=105:
        raise ValueError('Not the exact 2026 15-level source model')
    output_dir.mkdir(parents=True,exist_ok=True)
    result=[]
    for T in SOURCE_T_GRID:
        for n in (1e2,1e4,1e6,1e8,1e10):
            ref=solve(model,T,n,conversion=SOURCE_CONVERSION)
            si=solve(model,T,n,conversion=SI_CONVERSION)
            result.append({'T_K':T,'n_H2_cm3':n,'source_reproduction':ref,'SI_physical':si})
    (output_dir/'NEUFELD_15LEVEL_45_SOURCE_AND_SI_CASES.json').write_text(
       json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf8')
    return {'cases':len(result),'line_power_rows_per_convention':len(result)*len(model.rad),
            'source_sha256':model.source_sha256,'SI_cm_to_K':SI_CONVERSION,
            'source_reproduction_cm_to_K':SOURCE_CONVERSION}


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--source',type=Path,required=True,help='Original Neufeld2026 v2 hd_lamda.dat (SHA256-pinned)')
    p.add_argument('--output',type=Path,required=True)
    args=p.parse_args()
    print(json.dumps(run_at_source_temperatures(args.source.read_bytes(),args.output),indent=2))
if __name__=='__main__':
    main()
