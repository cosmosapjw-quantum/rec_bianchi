"""Analytic canonical retarded time coefficients and weak moving-jump checks."""
import numpy as np,json,sys
from pathlib import Path
from scipy.interpolate import CubicSpline
from scipy.linalg import expm
from scipy.integrate import cumulative_trapezoid
from numpy.polynomial.legendre import leggauss
D=Path(__file__).resolve().parent
sys.path.insert(0,str(D.parent/'r118c3p_prehistory'))
import prehistory as p
class ClockJet:
 def __init__(self,n,u0):
  g=np.genfromtxt(p.B/'plusfine.csv',names=True,delimiter=',');ge=np.log(g['a'])
  S=np.array([p.stf([g[f'S{k}'][j] for k in range(5)]) for j in range(len(g))]);self.S=CubicSpline(ge,S,axis=0)
  self.ge=ge;self.n=n;self.u0=u0
  from scipy.integrate import solve_ivp
  # relative coframe D'= -lambda S D, integrated from u0 both directions
  def rhs(u,z):a,b=z.reshape(2,3,3);return np.r_[-self.S(u).ravel(),(-self.S(u)@a).ravel()]
  self.lo=solve_ivp(rhs,(u0,ge[0]),np.zeros(18),method='DOP853',rtol=1e-11,atol=1e-14,dense_output=True)
  self.hi=solve_ivp(rhs,(u0,ge[-1]),np.zeros(18),method='DOP853',rtol=1e-11,atol=1e-14,dense_output=True)
 def jets(self,u):
  v=np.asarray(u);flat=v.ravel();z=np.empty((len(flat),18))
  for m,sol in [(flat<self.u0,self.lo),(flat>=self.u0,self.hi)]:
   if m.any():z[m]=sol.sol(flat[m]).T
  return z.reshape(v.shape+(2,3,3))
 def bc(self,u,n):
  z=self.jets(u);a=np.einsum('...ij,...j->...i',z[...,0,:,:],n);b=np.einsum('...ij,...j->...i',z[...,1,:,:],n)
  l=np.sum(n*a,axis=-1);c=np.sum(n*b,axis=-1)+.5*np.sum(a*a,axis=-1)-l*l
  bp=-np.einsum('...i,...ij,...j->...',n,self.S(u),n)
  return l,c,bp
 def ret(self,u,lr):
  t=u-lr;nn=self.n[:,None,:];b,c,bp=self.bc(t[None,:],nn);B,C,_=self.bc(np.asarray(u),self.n)
  t1=b-B[:,None];return t1,c-C[:,None]+bp*t1
 def exact(self,lam,u,lr):
  from scipy.integrate import solve_ivp
  rhs=lambda t,z:(-lam*self.S(t)@z.reshape(3,3)).ravel()
  lo=solve_ivp(rhs,(self.u0,self.ge[0]),np.eye(3).ravel(),method='DOP853',rtol=3e-12,atol=1e-14,dense_output=True)
  hi=solve_ivp(rhs,(self.u0,self.ge[-1]),np.eye(3).ravel(),method='DOP853',rtol=3e-12,atol=1e-14,dense_output=True)
  def val(t):
   v=np.asarray(t);q=v.ravel();z=np.empty((len(q),9))
   for m,s in [(q<self.u0,lo),(q>=self.u0,hi)]:
    if m.any():z[m]=s.sol(q[m]).T
   return z.reshape(v.shape+(3,3))
  n=self.n;B=np.log(np.linalg.norm(np.einsum('ij,nj->ni',val(u),n),axis=1));t=np.broadcast_to(u-lr,(len(n),len(lr))).copy()
  for _ in range(20):
   q=np.log(np.linalg.norm(np.einsum('...ij,...j->...i',val(t),n[:,None,:]),axis=-1));tn=u-lr+q-B[:,None]
   if np.max(abs(tn-t))<1e-14:return tn
   t=tn
  raise ValueError('retarded')
def test():
 mu,w=leggauss(4);m,ph=np.meshgrid(mu,np.arange(8)*np.pi/4,indexing='ij');n=np.stack([np.sqrt(1-m*m)*np.cos(ph),np.sqrt(1-m*m)*np.sin(ph),m],axis=-1).reshape(-1,3)
 he=np.load(D.parent/'r118c3p_prehistory/z1110_n32_0.npz')['rows'][:,0];j=ClockJet(n,he[0]);src,ef,es=p._source_edges(p._canonical_twophoton_table(p.R).energy_eV);lr=np.log(es/ef);u=he[-1]
 a,b=j.ret(u,lr);rows=[]
 for lam in [.2,.1,.05]:
  plus,minus=[j.exact(s*lam,u,lr) for s in [-1,1]][::-1]
  first=(plus-minus)/(2*lam);second=(plus+minus-2*(u-lr))/(2*lam*lam)
  rows.append(dict(lam=lam,t1_norm=float(np.linalg.norm(a)),t2_norm=float(np.linalg.norm(b)),first_relative=float(np.linalg.norm(first-a)/np.linalg.norm(a)),second_relative=float(np.linalg.norm(second-b)/np.linalg.norm(b))))
 # moving discontinuity: H(u+lambda*a+lambda²*b-s), integrated g=u².
 # exact crossing root and analytic coefficients.
 s=.4;a=.07;b=.03;g=lambda u:u*u;v0=(1-s**3)/3;v1=a*s*s;v2=b*s*s-a*a*s
 for lam in [.01,.005]:
  v=lambda l:(1-(s-l*a-l*l*b)**3)/3
  assert abs((v(lam)-v(-lam))/(2*lam)-v1)<1e-6
  assert abs((v(lam)+v(-lam)-2*v0)/(2*lam*lam)-v2)<1e-6
 o=dict(rows=rows,manufactured_weak=[v0,v1,v2],scope='continuous diagnostic scaled shear, exact first/second retarded time jets; moving-event weak Taylor coefficients, no full feedback')
 (D/'R7.json').write_text(json.dumps(o,indent=2)+'\n');print(o,flush=True)
if __name__=='__main__':test()
