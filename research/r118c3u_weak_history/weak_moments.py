"""Distributional weak time moments; shifted fixed baseline source history."""
import numpy as np,json
from pathlib import Path
from numpy.polynomial.legendre import leggauss
D=Path(__file__).resolve().parent
def moments(he,L,M,R,ta,tb,src,degree=3):
 h=tb-ta;assert np.all(h>0) and np.max(tb)<he[-1]
 t=ta.copy();out=np.zeros((degree+1,)+t.shape);ix=np.arange(t.shape[0])[:,None] if L.shape[1]==t.shape[0] else 0;j=src[None,:]
 q,w=leggauss(4)
 for _ in range(len(he)+2):
  active=t<tb
  if not active.any():return out
  k=np.searchsorted(he,t,side='right')-1;before=k<0;end=np.minimum(tb,he[np.clip(k+1,0,len(he)-1)]);span=np.where(active,end-t,0.)
  assert not np.any(active&(span<=0))
  k=np.clip(k,0,len(he)-2);hh=he[k+1]-he[k]
  for z,wt in zip(q,w):
   u=t+(z+1)*span/2;s=np.clip((u-he[k])/hh,0,1);v=np.where(active&~before,(1-3*s+2*s*s)*L[k,ix,j]+(4*s-4*s*s)*M[k,ix,j]+(2*s*s-s)*R[k,ix,j],0.)
   c=wt*span/(2*h)*v;p=(u-ta)/h
   for n in range(degree+1):out[n]+=c*p**n
  t=np.where(active,end,t)
 raise ValueError('history segment progress')
def derivatives(m,fl,fr,dl,dr,h,degree=4):
 # z polynomial weak tests. Interval endpoints must not coincide with a jump.
 z=np.zeros_like(fl);d=[];dd=[]
 for k in range(degree+1):
  d.append((fr-(fl if k==0 else 0)-(k*m[k-1] if k else 0))/h)
  dd.append((dr-(dl if k==0 else 0)-(k*d[k-1] if k else 0))/h)
 return np.array(d),np.array(dd)
def run():
 # Piecewise quadratic f(t)=H(t-s)*(J+p(t-s)+q(t-s)^2);
 # exact distribution derivative action including both delta and delta prime.
 l,r,s=.1,.9,.37;h=r-l;J,p,q=.7,.4,-.3
 he=np.array([s,r+1]);L=np.array([[[J]]]);M=np.array([[[J+p*(r+1-s)/2+q*((r+1-s)/2)**2]]]);R=np.array([[[J+p*(r+1-s)+q*(r+1-s)**2]]])
 a=np.array([[l]]);b=np.array([[r]]);m=moments(he,L,M,R,a,b,np.array([0]),3)[:,0,0]
 d,dd=derivatives(m,0,J+p*(r-s)+q*(r-s)**2,0,p+2*q*(r-s),h)
 from scipy.integrate import quad
 z=(s-l)/h
 exact1=np.array([quad(lambda u:((u-l)/h)**i*(p+2*q*(u-s)),s,r)[0]/h+J*z**i/h for i in range(5)])
 exact2=np.array([quad(lambda u:((u-l)/h)**i*2*q,s,r)[0]/h+p*z**i/h-(J*i*z**(i-1)/h**2 if i else 0) for i in range(5)])
 err=max(np.max(abs(d-exact1)),np.max(abs(dd-exact2)));assert err<1e-12
 o=dict(max_error=float(err),scope='weak derivative including delta and delta-prime at interior jump; analytic test moments k0..4')
 (D/'R7.json').write_text(json.dumps(o,indent=2)+'\n');print(o)
if __name__=='__main__':run()
