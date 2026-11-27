"""Audit weak moving source terms on actual frozen outgoing history."""
import numpy as np,json,sys
from pathlib import Path
from dataclasses import replace
from frozen import weak,moments,p,ClockJet,rate_weight,get
from numpy.polynomial.legendre import leggauss
D=Path(__file__).resolve().parent
def run():
 z=np.load(D/'frozen_1110_32.npz');he=z['he'];L,M,R=[z[k] for k in ['L','M','R']];v=np.load(D.parent/'r118c3p_prehistory/z1110_n32_0.npz')['rows']
 mu,w=leggauss(4);MM,ph=np.meshgrid(mu,np.arange(8)*np.pi/4,indexing='ij');n=np.stack([np.sqrt(1-MM*MM)*np.cos(ph),np.sqrt(1-MM*MM)*np.sin(ph),MM],axis=-1).reshape(-1,3);w=np.repeat(w/16,8);w/=w.sum();nr=len(w)
 c=ClockJet(n,he[0]);tab=p._canonical_twophoton_table(p.R);src,ef,es=p._source_edges(tab.energy_eV);lr=np.log(es/ef)
 g=np.genfromtxt(p.B/'plusfine.csv',names=True,delimiter=',');ge=np.log(g['a'])
 m=p.Clock(h=.6735837,omega_cb=.31242079216478097,omega_r_h2=4.1578740068818545e-5,omega_de_h2=.3119234221656212,omega_b_h2=.02242,y_he_mass=.245,tcmb0_K=2.7255,table=p.OriginalHyRecPrimitiveRateTable.from_archive(p.R))
 def face(u):
  x,T=np.array([np.interp(u,he,v[:,k]) for k in [1,2]])
  s=p.populate_original_full_atomic(replace(m,H=np.interp(u,ge,g['h'])*2.1842852410855023e-18),z=np.expm1(-u),xHII=x,xe=x,Tm_K=T,incoming_virtual=np.zeros(311),incoming_lyman=np.zeros(2))
  a,b=rate_weight(c,u,w);_,G=get(s,a,b);return *c.ret(u,lr),G
 rows=[]
 for i in [3,10,32,128,256]:
  l=he[i-1];r=(l+he[i])/2;h=r-l;A,B=face(l),face(r);ta=np.broadcast_to(l-lr,(nr,313));tb=np.broadcast_to(r-lr,(nr,313))
  val,jump=weak(he[:i],L[:i-1],M[:i-1],R[:i-1],ta,tb,A[0],B[0],A[1],B[1],A[2],B[2],h,src)
  def eval(t):
   a=ta+t*A[0]+t*t*A[1];b=tb+t*B[0]+t*t*B[1]
   U,V=moments(he[:i],L[:i-1],M[:i-1],R[:i-1],a,b,src)
   ga=A[2][0]+t*A[2][1]+t*t*A[2][2];gb=B[2][0]+t*B[2][1]+t*t*B[2][2]
   return np.sum(ga.astype(np.longdouble)*U.astype(np.longdouble)+(gb-ga).astype(np.longdouble)*V.astype(np.longdouble))
  y0=eval(0)
  for e in [.1,.05,.025]:
   y1,y2=eval(e),eval(-e);q=np.array([(y1-y2)/(2*e),(y1+y2-2*y0)/(2*e*e)],float)
   rows.append(dict(i=i,eps=e,analytic=val.tolist(),finite=q.tolist(),jump=jump.tolist(),second_relative=float(abs(q[1]-val[1])/max(abs(val[1]),1e-300)),first_abs=float(abs(q[0]-val[0]))))
 o=dict(rows=rows,scope='actual frozen history, local affine retarded-time Taylor map and polynomial gain jets; finite shifted integration check, not full native perturbed evolution')
 (D/'WEAK_AUDIT.json').write_text(json.dumps(o,indent=2)+'\n');print(o,flush=True)
if __name__=='__main__':run()
