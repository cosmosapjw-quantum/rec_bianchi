"""Exact primitive for piecewise linear accepted source; zero before initial knot."""
import numpy as np
def primitive(he,hist,area,t,src):
 k=np.searchsorted(he,t,side='right')-1;before=k<0
 if np.any(t>=he[-1]):raise ValueError('retarded time not strictly accepted')
 k=np.clip(k,0,len(he)-2);ix=np.arange(t.shape[0])[:,None];j=src[None,:]
 h=he[k+1]-he[k];z=t-he[k];f=hist[k,ix,j];g=hist[k+1,ix,j]
 out=area[k,ix,j]+z*f+.5*z*z*(g-f)/h
 return np.where(before,0.,out)
def average(he,hist,area,l,r,src):
 if np.min(r-l)<=0:raise ValueError('nonmonotone retarded map')
 return (primitive(he,hist,area,r,src)-primitive(he,hist,area,l,src))/(r-l)
def check():
 he=np.array([0.,1.,2.,3.]);hist=np.array([1.,3.,4.,5.])[:,None,None];a=np.r_[0,np.cumsum((hist[1:,0,0]+hist[:-1,0,0])/2)][:,None,None]
 l=np.array([[-.5]]);r=np.array([[1.5]])
 got=average(he,hist,a,l,r,np.array([0]))[0,0]
 assert abs(got-(2+1.625)/2)<1e-14
 return got
if __name__=='__main__':print(check())
