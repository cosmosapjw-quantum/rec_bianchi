"""Independent dense linear-solve + adaptive quadrature cross-check.

This is algorithmically independent of the production M-matrix elimination
and Gauss-Hermite line integration, not a distinct-author referee.
"""
from __future__ import annotations
import argparse,json,math
from pathlib import Path
import numpy as np
from scipy.integrate import quad
from pr169_neufeld15_reference import H,K_B,SI_CONVERSION
from hd_cmb15 import solve_cmb
from hd_line_transfer import read_models,beta_gauss


def dense_population(model,Tgas,nH2,z,f_ortho=.75):
    nlev=len(model.levels)
    L=np.zeros((nlev,nlev),dtype=float)
    def edge(start,end,rate):
        L[end,start]+=rate
        L[start,start]-=rate
    for upper,lower,A,nu in model.rad:
        y=H*nu/(K_B*(2.72548*(1+z)))
        nbar=0. if y>700. else 1./np.expm1(y)
        gu=model.levels[upper][2];gl=model.levels[lower][2]
        edge(upper,lower,A*(1+nbar))
        edge(lower,upper,A*(gu/gl)*nbar)
    ps,pr=model.collision[2];os,ort=model.collision[3]
    assert ps==os and Tgas in ps
    ti=ps.index(Tgas)
    for (u,l),pv in pr.items():
        Cdown=nH2*(pv[ti]*(1-f_ortho)+ort[(u,l)][ti]*f_ortho)
        _,Eu,gu=model.levels[u];_,El,gl=model.levels[l]
        Cup=Cdown*(gu/gl)*math.exp(-SI_CONVERSION*(Eu-El)/Tgas)
        edge(u,l,Cdown)
        edge(l,u,Cup)
    A=L.copy();A[-1,:]=1.
    b=np.zeros(nlev);b[-1]=1.
    p=np.linalg.solve(A,b)
    return p, np.linalg.norm(L@p,ord=np.inf)


def beta_quad(tau):
    if tau==0:return 1.
    def integrand(x):
        y=tau*math.exp(-x*x)
        if abs(y)<1.e-8:
            f=1.-y/2.+y*y/6.-y**3/24.
        else:
            f=-math.expm1(-y)/y
        return math.exp(-x*x)*f/math.sqrt(math.pi)
    return 2*quad(integrand,0,10,epsabs=2e-13,epsrel=2e-13,limit=300)[0]


def validate(root):
    models=read_models(root)
    cases=[(100.,1e2,100.),(100.,1e8,0.),(400.,1e4,30.),
           (1000.,1e6,50.),(4000.,1e4,0.),(4000.,1e4,100.),
           (4000.,1e8,10.),(2000.,1e6,30.)]
    records=[]
    for name,model in models.items():
     for T,n,z in cases:
      p,res=dense_population(model,T,n,z)
      x=np.array(solve_cmb(model,T,n,z)['populations_J0_to_J14'])
      records.append({'source':name,'Tgas_K':T,'nH2_cm3':n,'z':z,
          'max_population_abs_difference':float(np.max(np.abs(p-x))),
          'dense_residual_s_inv':float(res), 'min_population':float(np.min(p))})
    betas=[]
    for t in (-.02,-.000585,0.,.0001,.02,.1,.5,1.,6.6):
        a=beta_gauss(t);b=beta_quad(t)
        betas.append({'tau0':t,'hermite_beta':a,'adaptive_quad_beta':b,
            'abs_difference':abs(a-b)})
    results={'source':'Neufeld2026 v2 original','method':'independently built NumPy generator + dense linear solve; scipy.integrate.quad vs 96-node Gauss-Hermite',
        'population_checks':len(records), 'max_population_abs_difference':max(x['max_population_abs_difference'] for x in records),
        'max_dense_residual_s_inv':max(x['dense_residual_s_inv'] for x in records),
        'beta_checks':len(betas),'max_beta_abs_difference':max(x['abs_difference'] for x in betas),
        'records':records,'beta_checks_detail':betas}
    out=Path(root)/'evidence';out.mkdir(exist_ok=True)
    (out/'INDEPENDENT_SCIPY_16_STATES_9_TAU.json').write_text(json.dumps(results,indent=2,allow_nan=False)+'\n',encoding='utf-8')
    return results

if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,default=Path('.'))
 x=validate(ap.parse_args().root)
 print(json.dumps({k:x[k] for k in ('population_checks','max_population_abs_difference','beta_checks','max_beta_abs_difference')},indent=2))
