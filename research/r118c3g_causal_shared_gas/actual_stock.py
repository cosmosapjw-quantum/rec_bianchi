"""Diagnostic collisionless canonical-q transfer on actual REC accepted outgoing history.
This is a piecewise-constant reconstruction, not the native HyRec stock owner."""
import numpy as np,json,hashlib
from pathlib import Path
from shared_gas import B,R,_canonical_twophoton_table,interpF,KB_NATIVE_EV_K
from canonical_stock import transfer
D=Path(__file__).resolve().parent
P=D/'ACCEPTED_LOCAL_DIRECTIONAL.npz'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 v=np.load(P);eta=v['eta'];out=v['outgoing'];n=v['rays'];w=v['weights0'];Fref=v['reference_F']
 assert out.shape==(len(eta),len(n),314) and abs(w.sum()-1)<1e-13
 g=np.genfromtxt(B/'plusfine.csv',names=True,delimiter=',');ge=np.log(g['a'])
 F=np.stack([g[f'F{i}{j}'] for i in range(3) for j in range(3)],axis=1).reshape(-1,3,3)
 E=_canonical_twophoton_table(R).energy_eV
 edges=np.r_[E[0]*np.sqrt(E[0]/E[1]),np.sqrt(E[:-1]*E[1:]),E[-1]*np.sqrt(E[-1]/E[-2])]
 def rr(u):
  mat=interpF(ge,F,u);return np.linalg.norm(np.linalg.solve(mat.T,Fref.T)@n.T,axis=0)
 rows=[]
 for i,j in [(len(eta)-2,len(eta)-1),(0,len(eta)-1)]:
  a0,a1=np.exp(eta[[i,j]]);r0,r1=rr(eta[i]),rr(eta[j]);f=1/np.expm1(E/(KB_NATIVE_EV_K*2.7255/a0))+out[i,:,:311]
  assert np.min(f)>=0
  N0=Ng=Nl=Nh=E0=Eg=El=Eh=Ered=0.
  max_Nres=max_Eres=0.
  for k in range(len(n)):
   q0=edges*a0/r0[k];q1=edges*a1/r1[k];fk=f[k]
   dst,lost=transfer(q0,fk,q1)
   lo=np.maximum(q0[:-1,None],q1[None,:-1]);hi=np.minimum(q0[1:,None],q1[None,1:])
   M4=np.maximum(hi**4-lo**4,0)/4
   low4=np.maximum(np.minimum(q0[1:],q1[0])**4-q0[:-1]**4,0)/4
   high4=np.maximum(q0[1:]**4-np.maximum(q0[:-1],q1[-1])**4,0)/4
   initN=fk@np.diff(q0**3)/3;initE=r0[k]/a0*(fk@np.diff(q0**4)/4)
   ge1=r1[k]/a1*np.sum(fk@M4);le1=r1[k]/a1*(fk@low4);he1=r1[k]/a1*(fk@high4)
   targetE=initE*(r1[k]/a1)/(r0[k]/a0)
   max_Nres=max(max_Nres,abs(dst.sum()+lost.sum()-initN)/initN)
   max_Eres=max(max_Eres,abs(ge1+le1+he1-targetE)/targetE)
   N0+=w[k]*initN;Ng+=w[k]*dst.sum();Nl+=w[k]*lost[0];Nh+=w[k]*lost[1]
   E0+=w[k]*initE;Eg+=w[k]*ge1;El+=w[k]*le1;Eh+=w[k]*he1;Ered+=w[k]*targetE
  assert max_Nres<1e-12 and max_Eres<1e-12
  rows.append(dict(i=i,j=j,a0=a0,a1=a1,N0=N0,N_grid=Ng,N_low=Nl,N_high=Nh,N_rel_residual=(Ng+Nl+Nh-N0)/N0,E0=E0,E_grid=Eg,E_low=El,E_high=Eh,E_redshifted=Ered,redshift_work=Ered-E0,E_rel_residual=(Eg+El+Eh-Ered)/Ered,max_ray_Nres=max_Nres,max_ray_Eres=max_Eres,redshift_factor_range=[float(np.min(r1/a1/(r0/a0))),float(np.max(r1/a1/(r0/a0)))]))
 result=dict(status='SCOPED_PIECEWISE_CONSTANT_CANONICAL_STOCK_TRANSFER',source_sha=sha(P),geometry_sha=sha(B/'plusfine.csv'),rates_sha=sha(R),normalization='common phase-space prefactor omitted; q in a*eV, E in eV times canonical number measure',scope='collisionless diagnostic, not native atomic reaction or physical line flux owner; explicit exterior stocks',rows=rows)
 (D/'ACTUAL_CANONICAL_STOCK.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
