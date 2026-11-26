"""Positive edgewise reduction preserving energy action and refining to identity."""
import sys
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'r118c2x_writeback'))
from writeback import LinearProject,L

def action(a,i,j,K):
    a=np.asarray(a,dtype=L)
    F=K*(a[j]-a[i]);q=np.zeros(len(a),dtype=L)
    np.add.at(q,i,F);np.add.at(q,j,-F);return q

def positive_pairs(e,f,i,j,K):
    p=LinearProject(e,f);e=p.coarse;f=p.fine
    i=np.asarray(i);j=np.asarray(j);K=np.asarray(K,dtype=L)
    if not np.all(K>=0):raise ValueError('negative fine K')
    low=np.where(f[i]<=f[j],i,j);high=np.where(f[i]<=f[j],j,i)
    de=f[high]-f[low]
    # Barycentric supports of each endpoint. Remove common mass first.
    li=np.stack([p.i[low],p.i[low]+1],axis=1);hi=np.stack([p.i[high],p.i[high]+1],axis=1)
    lw=np.stack([1-p.w[low],p.w[low]],axis=1);hw=np.stack([1-p.w[high],p.w[high]],axis=1)
    for a in range(2):
      for b in range(2):
        m=np.where(li[:,a]==hi[:,b],np.minimum(lw[:,a],hw[:,b]),L(0))
        lw[:,a]-=m;hw[:,b]-=m
    mass=lw.sum(axis=1)
    if np.max(abs(mass-hw.sum(axis=1)))>1e-17:raise ValueError('mass coupling')
    g=np.zeros((len(e),len(e)),dtype=L)
    for a in range(2):
      for b in range(2):
        keep=(lw[:,a]>0)&(hw[:,b]>0)&(de>0)
        ii=li[keep,a];jj=hi[keep,b]
        if np.any(ii>=jj):raise ValueError('nonmonotone coupling')
        v=K[keep]*de[keep]*lw[keep,a]*hw[keep,b]/(mass[keep]*(e[jj]-e[ii]))
        np.add.at(g,(ii,jj),v)
    ii,jj=np.nonzero(g);kk=g[ii,jj]
    target=p.deposit(action(f,i,j,K));actual=action(e,ii,jj,kk)
    if np.sum(abs(target-actual))>1e-14*np.sum(abs(target)):raise ValueError('energy action mismatch')
    return p,(ii,jj,kk)

def nested(e,f,subdiv):
    if subdiv==0:return np.unique(np.r_[e,f])
    new=list(e)
    for lo,hi in zip(e[:-1],e[1:]):
      q=np.unique(f[(f>lo)&(f<hi)])
      if len(q):
        idx=np.rint(np.arange(1,subdiv)* (len(q)-1)/subdiv).astype(int)
        new.extend(q[idx])
    return np.unique(np.asarray(new,dtype=L))

def bose_action(e,a,i,j,K,x,T):
    zz=np.exp(-(e-L('10.198714553953742'))/T)
    f=a*zz/(1-a*zz)
    if np.min(f)<=0 or np.any(a*zz>=1):raise ValueError('occupation')
    return action(a,i,j,K*(1+f[i])*(1+f[j])*x)
