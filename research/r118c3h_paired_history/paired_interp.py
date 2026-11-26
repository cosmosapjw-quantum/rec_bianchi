"""C3H paired-history interpolation and residual diagnostic."""
import numpy as np
def harmonic(m0,m1,h0,h1):
 w1=2*h1+h0;w2=h1+2*h0
 ok=(m0*m1>0);den=np.zeros_like(m0);den[ok]=w1[ok]/m0[ok]+w2[ok]/m1[ok]
 return np.divide(w1+w2,den,out=np.zeros_like(m0),where=ok & (den!=0))
def sample(he,hist,t,src,mode='linear',join=64):
 k=np.searchsorted(he,t,side='right')-1;before=k<0;k=np.clip(k,0,len(he)-2);ix=np.arange(t.shape[0])[:,None]
 h=he[k+1]-he[k];r=(t-he[k])/h;y0=hist[k,ix,src[None,:]];y1=hist[k+1,ix,src[None,:]]
 v=(1-r)*y0+r*y1
 if mode=='pchip' and len(he)>=4:
  valid=(k>0)&(k+2<len(he))&((k+2<join)|(k-1>=join))
  km=np.maximum(k-1,0);kp=np.minimum(k+2,len(he)-1)
  h0=np.where(valid,he[k]-he[km],1.);h1=np.where(valid,he[kp]-he[k+1],1.)
  m=(y1-y0)/h;m0=(y0-hist[km,ix,src[None,:]])/h0;m1=(hist[kp,ix,src[None,:]]-y1)/h1
  d0=harmonic(m0,m,h0,h);d1=harmonic(m,m1,h,h1)
  z=(2*r**3-3*r*r+1)*y0+(r**3-2*r*r+r)*h*d0+(-2*r**3+3*r*r)*y1+(r**3-r*r)*h*d1
  v=np.where(valid,np.clip(z,np.minimum(y0,y1),np.maximum(y0,y1)),v)
 elif mode!='linear' and mode!='pchip':raise ValueError('interpolation')
 return np.where(before,0.,v)
def pair_residual(a,b):
 a=np.asarray(a,np.longdouble);b=np.asarray(b,np.longdouble);assert a.shape==b.shape and np.array_equal(a[:,0],b[:,0])
 delta=a-b;h=np.diff(a[:,0]);res=np.diff(delta[:,1])-h*(delta[:-1,3]+delta[1:,3])/2
 return dict(delta_x=float(delta[-1,1]),delta_T=float(delta[-1,2]),max_pair_res=float(np.max(abs(res))),max_pair_res_vs_individual=float(np.max(abs(res-delta[1:,5]))),max_individual_xres=float(max(np.max(abs(a[:,5])),np.max(abs(b[:,5])))))
