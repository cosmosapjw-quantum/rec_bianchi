"""Event-split outgoing history with stable local polynomial quadrature."""
import numpy as np
from quadratic import basis
def local_means(he,L,M,R,l,r,src):
 h=r-l
 if np.any(h<=0) or np.any(r>=he[-1]):raise ValueError('causal local interval')
 t=l.copy();out=np.zeros_like(l);first=np.zeros_like(l);ix=np.arange(l.shape[0])[:,None];j=src[None,:]
 for _ in range(len(he)+2):
  active=t<r
  if not active.any():return out,first
  k=np.searchsorted(he,t,side='right')-1
  before=k<0;end=np.minimum(r,he[np.clip(k+1,0,len(he)-1)])
  span=np.where(active,end-t,0.)
  if np.any(active & (span<=0)):raise ValueError('history segment progress')
  k=np.clip(k,0,len(he)-2);den=he[k+1]-he[k]
  for a in [.5-.5/np.sqrt(3),.5+.5/np.sqrt(3)]:
   q=t+a*span;z=np.clip((q-he[k])/den,0.,1.);b=basis(z)
   v=np.where(active & ~before,b[0]*L[k,ix,j]+b[1]*M[k,ix,j]+b[2]*R[k,ix,j],0.)
   w=span/(2*h);out+=w*v;first+=w*v*(q-l)/h
  t=np.where(active,end,t)
 raise ValueError('too many source knots')
def union_mesh(base,events,tol,anchors):
 e=np.sort(np.concatenate([base,*[x[np.isfinite(x)] for x in events]]));groups=[];group=[e[0]]
 for x in e[1:]:
  if x-group[0]<=tol:group.append(x)
  else:groups.append(group);group=[x]
 groups.append(group)
 out=[]
 for g in groups:
  a=[v for v in anchors if g[0]-tol*1e-3<=v<=g[-1]+tol*1e-3]
  out.append(a[0] if a else .5*(g[0]+g[-1]))
 assert np.min(np.diff(out))>0 and out[0]==base[0] and out[-1]==base[-1]
 return np.array(out)
