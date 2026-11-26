"""Exact Einstein pair with directional Sobolev escape; native Wien limit diagnostic."""
import numpy as np
EL=10.198714553953742;A21=6.265e8;LY=4.662899067555897e15
def line_pair(x1,dep,Tr_eV,H,nh_cm3,rates,inc,w):
 # x2p includes 3-fold degeneracy, dimensionless per H nucleus.
 bol=np.exp(-EL/Tr_eV);f0=1/np.expm1(EL/Tr_eV);f=f0+inc
 x2=3*x1*bol+dep
 if min(f)<0 or x2<0 or x2>=3*x1:raise ValueError('line population domain')
 R=LY*H/(nh_cm3*x1)*rates
 tau=(A21/R)*(1-x2/(3*x1));P=-np.expm1(-tau)/tau
 emit=P*A21*x2*(1+f);absorb=P*A21*3*x1*f
 stable=P*A21*(dep*(1+f)-3*x1*(1-bol)*inc)
 native=R*(dep-3*x1*inc)
 ww=w/w.sum()
 return np.array([ww@emit,ww@absorb,ww@stable,ww@native,ww@(emit-absorb-stable),np.min(tau)])
