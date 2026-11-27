"""Causal paired thermal update and exact affine fixed-gas response identities."""
import numpy as np,json
from pathlib import Path
D=Path(__file__).resolve().parent
def thermal_diff(T0,T0next,dT,A0,A1,Tr,h):
 return ((1-h*(2+A1)/2)*dT+h*(A1-A0)*(Tr-(T0+T0next)/2))/(1+h*(2+A1)/2)
def test():
 r=np.random.default_rng(19);errs=[]
 for _ in range(100):
  A0=10**r.uniform(-1,5);A1=A0*(1+r.uniform(-.01,.01));h=1e-5;Tr=3000.;T0=2999.;dT=.001
  step=lambda T,A:(T+h*(A*Tr-(2+A)*T/2))/(1+h*(2+A)/2)
  T=step(T0,A0);ref=step(T0+dT,A1)-T;v=thermal_diff(T0,T,dT,A0,A1,Tr,h)
  errs.append(abs(ref-v))
 assert max(errs)<2e-12
 o=dict(thermal_identity_max_K=max(errs),scope='algebraically exact midpoint thermal difference in exact arithmetic; finite test')
 (D/'R7.json').write_text(json.dumps(o,indent=2)+'\n');print(o)
if __name__=='__main__':test()
