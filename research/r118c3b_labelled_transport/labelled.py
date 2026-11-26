"""Open dilute labelled scattering + redshift with conservative ledgers."""
import sys
from pathlib import Path
import numpy as np
from scipy.sparse import coo_matrix,bmat,csr_matrix,vstack
from scipy.sparse.linalg import expm_multiply
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'r118c2t_cosmological'))
from drift import Redshift,L
class Owner:
 def __init__(self,e,g,i,j,K):
    self.e=np.asarray(e,dtype=L);self.g=np.asarray(g,dtype=L);self.i=np.asarray(i);self.j=np.asarray(j);self.K=np.asarray(K,dtype=L)
    self.d=Redshift(e,g);self.top=np.flatnonzero(self.e==max(self.e));self.tw=self.g[self.top]/self.g[self.top].sum();self.ref=L("10.198714553953742")
    self.n=len(e)
 def rates(self,bath):
    H,T,scale,inc=map(L,bath)
    if H<0 or T<=0 or scale<0 or inc<0:raise ValueError('bath domain')
    cap=self.g*np.exp(-(self.e-self.ref)/T)
    # K uses reference Ly alpha thermal activity convention; a change of
    # reference rescales both cap and conductance, here explicitly accounted.
    k=self.K*scale
    return H,cap,k,inc
 def direct(self,N,bath):
    H,c,k,inc=self.rates(bath);a=N/c;F=k*(a[self.j]-a[self.i]);sc=np.zeros(self.n,dtype=L)
    np.add.at(sc,self.i,F);np.add.at(sc,self.j,-F)
    flux=H*self.d.rate*N;dr=self.d.divergence(flux);b=H*inc
    dr[self.top]+=b*self.tw
    esc=flux[self.d.escape].sum()
    return np.r_[sc+dr,esc,esc*self.d.ghost,flux@self.d.de,b,b*self.e.max(),-sc@self.e]
 def matrix(self,bath):
    H,c,k,inc=self.rates(bath);i,j=self.i,self.j;n=self.n;d=self.d;v=np.arange(n)
    r=k/c[i];q=k/c[j]
    S=coo_matrix((np.asarray(np.r_[-r,r,q,-q],float),(np.r_[i,j,i,j],np.r_[i,i,j,j])),shape=(n,n)).tocsr()
    R=coo_matrix((np.asarray(np.r_[-H*d.rate,H*d.w*d.rate[d.j]],float),(np.r_[v,d.i],np.r_[v,d.j])),shape=(n,n)).tocsr()
    esc=np.zeros(n);esc[d.escape]=np.asarray(H*d.rate[d.escape],float)
    a=vstack([S+R,csr_matrix(np.stack([esc,esc*float(d.ghost),np.asarray(H*d.rate*d.de,float),np.zeros(n),np.zeros(n),-np.asarray(self.e,float)@S]))],format='csr')
    return a
 def midpoint(self,N,t,dt,bath):
    N=np.asarray(N,dtype=L);b=bath(t+dt/2)
    f=self.direct(N,b);scale=max(np.max(abs(f)),L('1e-4900'));n=self.n
    a=self.matrix(b)
    G=bmat([[a,csr_matrix((n+6,6)),csr_matrix(np.asarray(f/scale,float)[:,None])],[csr_matrix((1,n)),csr_matrix((1,6)),csr_matrix((1,1))]],format='csr')
    y=np.asarray(expm_multiply(G*dt,np.r_[np.zeros(n+6),1.])[:-1],dtype=L)*scale
    if np.min(N+y[:n])<0:raise ValueError('negative stock')
    return y
