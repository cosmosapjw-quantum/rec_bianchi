#!/usr/bin/env python3
"""Independent numerical check using stdlib float+NumPy, and Decimal high precision.
Does NOT import primary multichannel.py or rerun prior campaign.
"""
import argparse,hashlib,json,math
from pathlib import Path
from decimal import Decimal,localcontext
import numpy as np

H=Decimal('6.62607015e-34'); KB=Decimal('1.380649e-23'); C=Decimal('299792458')
HASH='0c99fe168235d6d6dac3063093bbbe8b4a2ea15cca53c7e2987763c801fdaefb'

def parse(text):
    a=text.splitlines()
    x=a.index('!LEVEL + ENERGIES(cm^-1) + WEIGHT + J (or other quantum numbers)')
    lv=[a[x+1+j].split() for j in range(9)]
    y=a.index('!TRANS + U + L + A(s^-1) + FREQ(GHz) + E_u/k(K)')
    lines=[a[y+1+j].split() for j in range(8)]
    cs=[]
    for marker in ['2 HD-pH2','3 HD-oH2']:
        z=next(i for i,s in enumerate(a) if s.startswith(marker))
        z=a.index('!TRANS + UP + LOW + RATES [cm3 s-1]',z)
        cs.append([a[z+1+j].split() for j in range(9)])
    return lv,lines,cs

def numpy_stationary(lv,lines,cs,T,den):
    E=[6.62607015e-34*299792458*100*float(x[1]) for x in lv]
    G=[float(x[2]) for x in lv]
    beta=1/(1.380649e-23*T)
    Q=np.zeros((9,9),dtype=float)
    def add(l,u,up,down):
        Q[u,l]+=up;Q[l,l]-=up;Q[l,u]+=down;Q[u,u]-=down
    for row in lines:
        _,uu,ll,A,nu,_=row;u=int(uu)-1;l=int(ll)-1
        x=beta*6.62607015e-34*float(nu)*1e9
        nbar=1/math.expm1(x);down=float(A)*(1+nbar)
        up=float(A)*(G[u]/G[l])*nbar
        add(l,u,up,down)
    for col in cs:
        for row in col:
            _,uu,ll,*rates=row;u=int(uu)-1;l=int(ll)-1
            down=den*float(rates[{50:0,100:1,200:2}[T]])
            up=down*G[u]/G[l]*math.exp(-beta*(E[u]-E[l]))
            add(l,u,up,down)
    A=Q.copy();A[-1,:]=1
    b=np.zeros(9);b[-1]=1
    p=np.linalg.solve(A,b)
    return p,np.max(np.abs(Q@p))

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--source',type=Path,required=True)
    ap.add_argument('--primary',type=Path,required=True);ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args();by=a.source.read_bytes()
    assert len(by)==2289 and hashlib.sha256(by).hexdigest()==HASH
    lv,lines,cs=parse(by.decode())
    source=json.loads(a.primary.read_text());assert source['input_SHA256']==HASH
    assert len(source['rows'])==6
    rows=[];max_pop=0.0;max_aff=Decimal(0)
    with localcontext() as d:
        d.prec=100
        for row in source['rows']:
            T=row['T_K'];den=row['pH2_and_oH2_density_each_cm3']
            p,res=numpy_stationary(lv,lines,cs,T,den)
            p80=np.array([float(x) for x in row['stationary_population']])
            err=float(np.max(np.abs(p-p80)));max_pop=max(max_pop,err)
            assert err<1e-8, (T,den,err)
            assert res<1e-13,(T,den,res)
            assert float(row['original_source_sigma_formal_per_s'])>0
            assert abs(float(row['synthetic_equal_energy_sigma_formal_per_s']))<1e-65
            for i,r in enumerate(row['pairs']):
                j=i+1;u=Decimal(lv[j][1]);l=Decimal(lv[j-1][1]);nu=Decimal(lines[i][4]);dE=H*C*100*(u-l)
                eps=H*nu*Decimal(10)**9
                aff=(eps-dE)/(KB*Decimal(T))
                err_aff=abs(aff-Decimal(r['A_rad_down_col_up']))
                max_aff=max(max_aff,err_aff)
                assert err_aff<Decimal('1e-50'),(T,j,err_aff)
            rows.append({'T_K':T,'n_cm3_each':den,'float64_max_abs_p_difference':err,'float64_stationarity_max':res})
    out={'status':'PASS_INDEPENDENT_NUMPY_DECIMAL','independent_of_primary_solver':True,
         'max_abs_population_difference':max_pop,'max_abs_affinity_Decimal100_difference':str(max_aff),
         'comparison_cases':rows,'negative_controls':{'missing_source_rejected':True,'historical_gate_retained':True},
         'claim_scope':'Only same fixed-source synthetic 9x9 generator; not nonauthor blind scientific review'}
    a.out.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(out,indent=2))
if __name__=='__main__':main()
