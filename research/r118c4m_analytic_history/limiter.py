"""Directional derivative of the actual normalized adaptive positivity LP.
Differentiate active linear inequalities and each appended simple critical root.
Retain optimizer ambiguity or mismatch as failure; use original finite stencil only as explicit fallback."""
import numpy as np
from numpy.polynomial.legendre import legvander,legval,legder,legroots
from scipy.optimize import linprog
C=np.array([[1.,0.,0.],[-3.,6.,0.],[5.,-30.,30.]])
def analytic(O,fr,dO,expected):
 q=C@O;q[0]+=fr;dq=C@dO
 scale=max(np.max(abs(q)),fr);mag=max(np.max(abs(dq)),1e-300);dq=dq/mag
 ties=abs(abs(q)-scale)<=8*np.spacing(scale)
 ds=max([float(x) for x in np.sign(q[ties])*dq[ties]]+([0.] if abs(fr-scale)<=8*np.spacing(scale) else []))
 x=q/scale;dx=dq-x*ds;grid=np.linspace(-1,1,65);dg=np.zeros_like(grid);hist=[]
 for it in range(8):
  V=legvander(grid,6);dV=np.stack([legval(grid,legder(np.eye(7)[k])) for k in range(7)],axis=1)*dg[:,None]
  A=np.c_[-V[:,3:],V[:,3:]];dA=np.c_[-dV[:,3:],dV[:,3:]];b=V[:,:3]@x-1e-10;db=V[:,:3]@dx+dV[:,:3]@x
  r=linprog(np.ones(8),A_ub=A,b_ub=b,bounds=(0,None),method='highs');assert r.success
  z=r.x;hi=z[:4]-z[4:];tight=np.flatnonzero(r.ineqlin.residual<=2e-9);support=np.flatnonzero(z>1e-10)
  bounds=[(None,None) if j in support else (0,None) for j in range(8)];rhs=db[tight]-dA[tight]@z
  v=linprog(np.ones(8),A_ub=A[tight],b_ub=rhs,bounds=bounds,method='highs')
  if not v.success:raise ValueError('directional LP: '+v.message)
  dz=v.x;dh=dz[:4]-dz[4:];co=np.r_[x,hi];dco=np.r_[dx,dh]
  roots=legroots(legder(co));roots=roots.real[(abs(roots.imag)<1e-10)&(abs(roots.real)<1)]
  zz=np.r_[-1,1,roots];vv=legval(zz,co);mn=vv.min()
  hist.append(dict(iteration=it,grid=len(grid),rank=int(np.linalg.matrix_rank(A[np.ix_(tight,support)])),support=support.tolist(),tight=tight.tolist(),derivative_violation=float(max(0.,np.max(A[tight]@dz-rhs,initial=0.))),min_value=float(mn)))
  if mn>0:
   assert np.max(abs(hi*scale-expected[3:]))<1e-9*scale
   return mag*(dh+ds*hi),hist
  new=zz[vv<=0];dd=[]
  for rt in new:
   if abs(rt)>=1:dd.append(0.);continue
   p2=legval(rt,legder(co,2));assert abs(p2)>1e-12
   dd.append(-legval(rt,legder(dco))/p2)
  G=np.r_[grid,new];DG=np.r_[dg,dd];grid,ii=np.unique(G,return_index=True);dg=DG[ii]
 raise ValueError('adaptive LP iterations')
