"""Three weak moments, positive high-order history preserving the first three moments."""
import numpy as np
from numpy.polynomial.legendre import legval,legder,legroots,legvander
from scipy.optimize import linprog
def reconstruct(O,fr,degree=6):
 # O shape [3, rays, 314], fr lower Planck bound [311].
 a=np.zeros(O.shape[1:]+(degree+1,))
 a[...,0]=O[0];a[...,1]=3*(2*O[1]-O[0]);a[...,2]=5*(6*O[2]-6*O[1]+O[0])
 q=a[...,:311,:3].copy();q[...,0]+=fr
 A,B,C=q[...,0],q[...,1],q[...,2]
 y=np.clip(np.divide(-B,3*C,out=np.zeros_like(B),where=C!=0),-1,1)
 v=np.minimum(np.minimum(A-B+C,A+B+C),A+B*y+C*(3*y*y-1)/2)
 bad=np.argwhere(v<=0);rows=[]
 for i,j in bad:
  x=q[i,j];scale=max(np.max(abs(x)),fr[j]);x=x/scale
  if x[0]<=0:raise ValueError(f'negative full mean {i} {j} {x}')
  # Preserve first three moments. Find small higher coefficients via LP,
  # then add exact polynomial minima if sampled constraints missed them.
  grid=np.linspace(-1,1,65);n=degree-2
  for it in range(8):
   V=legvander(grid,degree);g=V[:,:3]@x;M=V[:,3:]
   r=linprog(np.ones(2*n),A_ub=np.c_[-M,M],b_ub=g-1e-10,bounds=(0,None),method='highs')
   if not r.success:raise ValueError(f'positive polynomial infeasible at {i} {j}: {x.tolist()}')
   h=r.x[:n]-r.x[n:];co=np.r_[x,h];roots=legroots(legder(co));roots=roots.real[(abs(roots.imag)<1e-10)&(abs(roots.real)<1)]
   zz=np.r_[-1,1,roots];vv=legval(zz,co);m=vv.min()
   if m>0:break
   grid=np.unique(np.r_[grid,zz[vv<=0]])
  else:raise ValueError(f'positive polynomial certificate failed {i} {j} {m}')
  a[i,j,3:]=h*scale;v[i,j]=m*scale
  rows.append([int(i),int(j),float(np.min(legval(np.linspace(-1,1,65),x))*scale/fr[j]),float(m*scale/fr[j]),float(np.linalg.norm(h)*scale/fr[j])])
 assert np.min(v)>0
 return a,rows,float(np.min(v/fr))
