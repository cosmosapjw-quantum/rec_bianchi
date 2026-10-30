"""Independent linear algebra for selected source model diagnostic cases.

This intentionally reconstructs the transition generator in a different code path
than pr169's positive M-matrix elimination and uses scipy.linalg.solve on an
explicitly normalized column-conserving generator. Only compares physically
resolved populations/line powers at the specified warm cases.
"""
from __future__ import annotations
import hashlib
import math
from pathlib import Path
import numpy as np
from scipy.linalg import solve
H=6.62607015e-34
K=1.380649e-23
C=299792458.

def source_data(source:bytes):
    t=[r.split() for r in source.decode('ascii').splitlines()]
    e=[r for r in t if len(r)==4 and r[0].isdigit()]
    a=[r for r in t if len(r)==6 and r[0].isdigit()]
    c=[r for r in t if len(r)==12 and r[0].isdigit()]
    assert len(e)==15 and len(a)==14 and len(c)==210
    energies=np.array([float(v[1]) for v in e])
    weights=np.array([float(v[2]) for v in e])
    rad=[(int(r[1])-1,int(r[2])-1,float(r[3]),float(r[4])*1e9) for r in a]
    coll=[(int(r[1])-1,int(r[2])-1,np.array([float(v) for v in r[3:]])) for r in c]
    return energies,weights,rad,coll

def independent(T:float,n:float,z:float,original_bytes:bytes):
    en,g,rad,coll=source_data(original_bytes)
    temp=(100,200,300,400,600,1000,2000,3000,4000)
    ix=temp.index(T)
    bath=2.72548*(1+z)
    M=np.zeros((15,15),float)
    def add(u,l,rate):
        M[l,u]+=rate
        M[u,u]-=rate
    for u,l,A,freq in rad:
        nb=1/math.expm1(H*freq/K/bath)
        add(u,l,A*(1+nb))
        add(l,u,A*(g[u]/g[l])*nb)
    for q,oq in zip(coll[:105],coll[105:]):
        u,l,para=q;u2,l2,ortho=oq
        if (u,l)!=(u2,l2):raise ValueError('Collision pair mismatch')
        down=n*(para[ix]+3*ortho[ix])/4
        up=down*g[u]/g[l]*math.exp(-(100*H*C/K)*(en[u]-en[l])/T)
        add(u,l,down)
        add(l,u,up)
    A=M.copy();A[0,:]=1.
    b=np.zeros(15);b[0]=1.
    p=solve(A,b,assume_a='gen',check_finite=True)
    lines=[]
    for u,l,Ar,nu in rad:
        nb=1/math.expm1(H*nu/K/bath)
        val=H*nu*Ar*(p[u]*(1+nb)-p[l]*(g[u]/g[l])*nb)
        lines.append(val)
    return dict(populations=p, lines=np.array(lines), balance=float(np.max(np.abs(M@p))), norm=float(np.sum(p)))

if __name__=='__main__':
    import json
    R=Path(__file__).resolve().parents[1]
    src=[(R/'source/zenodo_v2'/fn).read_bytes() for fn in ('hd_lamda.dat','hd_lamda_altex.dat')]
    from pr169_neufeld15_reference import parse_lamda
    from hd_cmb15 import solve_cmb
    results=[]
    for T,n,z in ((1000,1e6,0),(1000,1e6,30),(2000,1e6,100),(4000,1e6,100)):
        for k,v in enumerate(src):
            independent_result=independent(T,n,z,v)
            original=solve_cmb(parse_lamda(v,verify=k==0),T,n,z)
            origline=np.array([x['net_W_per_HD'] for x in original['line_power_records']])
            significant=np.array([x>1e-30 for x in abs(origline)])
            rel_err=max(abs(independent_result['lines'][significant]-origline[significant])/abs(origline[significant]))
            pop_err=max(abs(independent_result['populations']-np.array(original['populations_J0_to_J14'])))
            item={'T_K':T,'nH2_cm3':n,'z':z,'model':'std' if k==0 else 'alt',
                  'max_pop_abs_diff':float(pop_err),'max_significant_line_relative_diff':float(rel_err),
                  'max_generator_balance':independent_result['balance'],'normalization':independent_result['norm']}
            if pop_err>1e-11 or rel_err>2e-10:raise AssertionError(item)
            results.append(item)
    out=R/'evidence/INDEPENDENT_SCIPY_8_SOURCE_CASES.json'
    out.write_text(json.dumps(results,indent=2)+'\n')
    print(json.dumps({'cases':len(results),'max_pop_diff':max(x['max_pop_abs_diff'] for x in results),
                      'max_relative_line_diff':max(x['max_significant_line_relative_diff'] for x in results)}))
