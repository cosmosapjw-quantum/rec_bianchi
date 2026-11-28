"""Exact parameter JVP of represented not-a-knot inverse cubic spline."""
from pathlib import Path
import sys,numpy as np
from scipy.linalg import solve_banded
from scipy.interpolate import CubicSpline
D=Path(__file__).resolve().parent
import importlib.util
spec=importlib.util.spec_from_file_location('prior_event',D.parent/'r118c4m_analytic_history/event.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
class MovingSpline:
 def __init__(self,g,dx):
  x=g.x;y=g(x);h=np.diff(x);dh=np.diff(dx);sl=np.diff(y)/h;dsl=-sl*dh/h
  N=len(x);M=g(x,2);A=np.zeros((5,N));dA=np.zeros_like(A);b=np.zeros(N);db=b.copy()
  def put(row,col,v,d):A[2+row-col,col]=v;dA[2+row-col,col]=d
  put(0,0,-h[1],-dh[1]);put(0,1,h[0]+h[1],dh[0]+dh[1]);put(0,2,-h[0],-dh[0])
  put(N-1,N-3,-h[-1],-dh[-1]);put(N-1,N-2,h[-2]+h[-1],dh[-2]+dh[-1]);put(N-1,N-1,-h[-2],-dh[-2])
  i=np.arange(1,N-1);A[3,i-1]=h[:-1];A[2,i]=2*(h[:-1]+h[1:]);A[1,i+1]=h[1:];dA[3,i-1]=dh[:-1];dA[2,i]=2*(dh[:-1]+dh[1:]);dA[1,i+1]=dh[1:];b[i]=6*np.diff(sl);db[i]=6*np.diff(dsl)
  def dot(A,v):
   o=np.zeros(N)
   for k in range(-2,3):
    j=np.arange(max(0,-k),min(N,N-k));o[j+k]+=A[2+k,j]*v[j]
   return o
  res=b-dot(A,M);DM=solve_banded((2,2),A,db-dot(dA,M),check_finite=False)
  self.res=float(np.max(abs(res))/max(np.max(abs(b)),1e-300))
  self.g=g;self.x=x;self.dx=dx
  self.dc=np.stack([(DM[1:]-DM[:-1])/(6*h)-g.c[0]*dh/h,DM[:-1]/2,dsl-(dh*(2*M[:-1]+M[1:])+h*(2*DM[:-1]+DM[1:]))/6])
  self.dmres=float(np.max(abs(dot(A,DM)-(db-dot(dA,M))))/max(np.max(abs(db-dot(dA,M))),1e-300))
 def __call__(self,q,dq=0.):
  q=np.asarray(q);j=np.clip(np.searchsorted(self.x,q,side='right')-1,0,len(self.x)-2);z=q-self.x[j]
  c=self.dc[:,j];g=self.g
  # derivative on same nominal piece; endpoints use one-sided extrapolation limit.
  return ((c[0]*z+c[1])*z+c[2])*z+g(q,1)*(dq-self.dx[j])
class Events(mod.Events):
 def __init__(self,m):
  super().__init__(m)
  self.moving=[MovingSpline(g,f(m.D.x)) for g,f in zip(m.g,self.fl)]
  self.spline_res=max(s.res for s in self.moving);self.spline_dres=max(s.dmres for s in self.moving)
 def gd(self,q,dq):
  return np.stack([s(q[j],dq[j]) for j,s in enumerate(self.moving)])
 def td(self,u,du=0.):
  m=self.m;U=np.broadcast_to(u,(m.nr,313));v=m.t(U);f=self.ev(self.fl,U)+self.ev(m.f,U,1)*du
  dv=self.gd(self.ev(m.f,U)-m.lr,f);assert np.isfinite(dv).all();return v,dv
 def arrival(self,sk,cross,mask):
  m=self.m;q=self.ev(m.f,sk)+m.lr
  # Evaluate derivative only at defined inverse-spline domain.
  v=np.stack([np.clip(q[j],g.x[0],g.x[-1]) for j,g in enumerate(m.g)])
  return self.gd(v,self.ev(self.fl,sk))
# Use the exact parent quadrature arithmetic, replacing the two approximate arrival derivatives.
s=(D.parent/'r118c4m_analytic_history/event.py').read_text()
a=s.index(' def correction(');b=s.index(' def integrate(',a);c=s.index("  raise ValueError('too many events')",b)+len("  raise ValueError('too many events')")
q=s[a:c]
a='dc=(self.ev(self.fl,sk)-self.ev(self.fl,cr))/self.ev(m.f,cr,1)'
b='dc=(self.ev(self.fl,nk)-self.ev(self.fl,cr))/self.ev(m.f,cr,1)'
assert q.count(a)==1 and q.count(b)==1
q=q.replace(a,'dc=self.arrival(sk,cr,near)').replace(b,'dc=self.arrival(nk,cr,hit)')
ns={};exec('import numpy as np\nclass _Methods:\n'+q+'\n',ns)
Events.correction=ns['_Methods'].correction;Events.integrate=ns['_Methods'].integrate
