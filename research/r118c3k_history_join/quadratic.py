"""Piecewise quadratic source history, separate left/right at prefix join."""
import numpy as np
def basis(z):
 return 1-3*z+2*z*z,4*z-4*z*z,2*z*z-z
def integ(z):
 return z-1.5*z*z+2*z**3/3,2*z*z-4*z**3/3,2*z**3/3-z*z/2
def gather(he,L,M,R,t,src,area=None):
 k=np.searchsorted(he,t,side='right')-1;before=k<0
 if np.any(t>=he[-1]):raise ValueError('future history')
 k=np.clip(k,0,len(he)-2);ix=np.arange(t.shape[0])[:,None];j=src[None,:]
 h=he[k+1]-he[k];z=(t-he[k])/h
 z=np.where(before,0.,z)
 w=basis(z) if area is None else integ(z)
 v=w[0]*L[k,ix,j]+w[1]*M[k,ix,j]+w[2]*R[k,ix,j]
 if area is not None:v=area[k,ix,j]+h*v
 return np.where(before,0.,v)
def average(he,L,M,R,area,l,r,src):
 if np.min(r-l)<=0:raise ValueError('nonmonotone')
 return (gather(he,L,M,R,r,src,area)-gather(he,L,M,R,l,src,area))/(r-l)
def manufactured():
 # x'(t)=g(t-tau), with a quadratic outgoing history and a jump at join t=0.5.
 # compare linear and midpoint quadratic, exact retarded interval integration.
 rows=[]
 for n in [16,32,64,128]:
  he=np.linspace(0,1,n+1);l=he[:-1];r=he[1:];mid=(l+r)/2
  side=(l>=.5).astype(float);L=(l*l+side)[:,None,None];R=(r*r+side)[:,None,None];M=(mid*mid+side)[:,None,None]
  errs={}
  for tag,m in [('linear',(L+R)/2),('quadratic',M)]:
   area=np.r_[0,np.cumsum(np.diff(he)*(L[:,0,0]+4*m[:,0,0]+R[:,0,0])/6)][:,None,None]
   v=gather(he,L,m,R,np.array([[.9375]]),np.array([0]),area)[0,0]-gather(he,L,m,R,np.array([[.123]]),np.array([0]),area)[0,0]
   exact=(.9375**3-.123**3)/3+.9375-.5
   errs[tag]=float(abs(v-exact))
  rows.append(dict(n=n,**errs))
 return rows
if __name__=='__main__':print(manufactured())
