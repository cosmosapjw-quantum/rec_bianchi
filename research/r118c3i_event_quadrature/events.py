"""Exact first-prefix arrival event table and finite-step jump correction."""
import numpy as np
def event_times(ge,F,Fref,n,us,lr,lo,hi):
 p=n@Fref
 def coframe(t):
  return np.stack([np.interp(t,ge,F[:,i,j]) for i in range(3) for j in range(3)],axis=-1).reshape(np.shape(t)+(3,3))
 def ell(t):
  mat=coframe(t);vec=np.linalg.solve(np.swapaxes(mat,-1,-2),p[...,None])[...,0]
  return np.asarray(t)-np.log(np.linalg.norm(vec,axis=-1))
 # All rays have their own reference covector.
 es=ell(us);el=ell(lo);eh=ell(hi)
 target=es[:,None]+np.asarray(lr)[None,:]
 ok=(target>el[:,None])&(target<=eh[:,None])
 ii,jj=np.where(ok);result=np.full(target.shape,np.inf)
 if len(ii):
  low=np.full(len(ii),lo);high=np.full(len(ii),hi);z=target[ii,jj];pp=p[ii]
  for _ in range(45):
   mid=(low+high)/2;mat=coframe(mid);vec=np.linalg.solve(np.swapaxes(mat,-1,-2),pp[...,None])[...,0]
   test=mid-np.log(np.linalg.norm(vec,axis=-1))
   left=test<z;low=np.where(left,mid,low);high=np.where(left,high,mid)
  result[ii,jj]=(low+high)/2
 return result
def jump_weight(events,l,r):
 if not r>l:raise ValueError('interval')
 mask=(events>l)&(events<=r)
 return np.where(mask,.5-(np.where(mask,events,l)-l)/(r-l),0.)
def correction(events,l,r,v0):
 return jump_weight(events,l,r)*v0[None,:]
