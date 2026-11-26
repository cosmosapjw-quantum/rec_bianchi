"""Piecewise-constant physical canonical momentum remap, not native virtual stock."""
import numpy as np
def transfer(edges,occupation,target):
 e=np.asarray(edges,float);t=np.asarray(target,float);f=np.asarray(occupation,float)
 if e.ndim!=1 or t.ndim!=1 or f.shape!=(len(e)-1,) or min(e)<0 or min(t)<0 or np.any(np.diff(e)<=0) or np.any(np.diff(t)<=0) or np.any(f<0) or not all(np.isfinite(x).all() for x in (e,t,f)):raise ValueError('invalid remap')
 l=np.maximum(e[:-1,None],t[None,:-1]);h=np.minimum(e[1:,None],t[None,1:]);M=np.maximum(h**3-l**3,0)/3
 V=np.diff(e**3)/3;represented=M.sum(axis=1)
 low=np.maximum(np.minimum(e[1:],t[0])**3-e[:-1]**3,0)/3
 high=np.maximum(e[1:]**3-np.maximum(e[:-1],t[-1])**3,0)/3
 if not np.allclose(represented+low+high,V,rtol=1e-12,atol=1e-15):raise ArithmeticError('volume partition')
 out=f@M;lost=np.array([f@low,f@high])
 return out,lost
