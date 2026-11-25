"""Disjoint physical COM-KHW wing blocks on C2I auxiliary exterior cells.

Native virtual-state proxy rates are NOT interpreted as physical photon
number rates. Additional actual KHW integrals use the same bath and phase
measure as the calibrated core. Only six selected neighbor blocks.
"""
import math
import numpy as np
from scipy.constants import h,k,e,c
from scipy.optimize import brentq
from .atomic_dynamic_companion import L
from ..recoil.calibrated_source import PCC,EX,Bath,density,angular,uv_nodes,tensor_nodes,owner_cells

def physical_blocks(net):
    bounds=owner_cells();p=net.q['sub']+1
    ext=net.et[net.ncore:];core=net.et[:net.ncore]
    x=(ext*L(e)/L(h)-L(PCC.nu_abs))/L(PCC.dnu)
    out=[]
    for side in (-1,1):
        ids=np.flatnonzero(ext<core.min() if side==-1 else ext>core.max())
        edges=np.r_[net.transition/2 if side==-1 else core.max(),(ext[ids[:-1]]+ext[ids[1:]])/2,core.min() if side==-1 else ext[-1]+(ext[-1]-ext[-2])/2]
        ed=np.asarray((edges*L(e)/L(h)-L(PCC.nu_abs))/L(PCC.dnu),float)
        # use exact COM face, not a rounded conversion of its energy
        if side==-1:ed[-1]=-21.25
        else:ed[0]=21.25
        order=list(range(len(ids)-1,len(ids)-4,-1)) if side==-1 else [0,1,2]
        first=order[0];parent=29 if side==-1 else 34
        core_ids=list(range(parent*p,(parent+1)*p))
        extids=[int(net.ncore+ids[j]) for j in order]
        cells=[(float(ed[j]),float(ed[j+1])) for j in order]
        out.append(('cross',core_ids,[extids[0]],tuple(bounds[parent]),cells[0]))
        for j in range(2):out.append(('wing',[extids[j]],[extids[j+1]],cells[j],cells[j+1]))
    return out

def integrate_pair(a,b,bath,lane,na=1,nb=1):
    par=EX.LANES[lane];mu,wmu=angular(par)
    # Integrate each core subcell separately so the piecewise linear hat
    # kinks are true quadrature breakpoints. Point exterior cell owns all
    # of its integrated event rate; its represented energy is its centre.
    aa=np.linspace(*a,na if na>1 else 2);bb=np.linspace(*b,nb if nb>1 else 2)
    K=np.zeros((na,nb));direct=np.zeros(2)
    for ii,A in enumerate(zip(aa[:-1],aa[1:])):
     for jj,B in enumerate(zip(bb[:-1],bb[1:])):
      # all selected intervals lie on one wing; no central pole crossing
      nt,ns,ww=uv_nodes(A,B,par,.08)
      xt=(nt-PCC.nu_abs)/PCC.dnu;xs=(ns-PCC.nu_abs)/PCC.dnu
      t=(xt-A[0])/(A[1]-A[0]);s=(xs-B[0])/(B[1]-B[0])
      if min(t.min(),s.min())<-1e-10 or max(t.max(),s.max())>1+1e-10:raise ValueError("quadrature support")
      # Numerical coordinate conversion tolerance only (interior GL nodes).
      if min(t.min(),s.min())<0 or max(t.max(),s.max())>1:raise ValueError("hat support")
      ht=[1-t,t] if na>1 else [np.ones_like(t)]
      hs=[1-s,s] if nb>1 else [np.ones_like(s)]
      for q in range(0,len(mu),8):
       m=mu[q:q+8,None];W=wmu[q:q+8,None]*.75*(1+m*m)*ww[None,:]*8*np.pi*PCC.dnu/c**3
       D=density(nt[None,:],ns[None,:],m,bath)*W/bath.z0
       for u,hu in enumerate(ht):
        for v,hv in enumerate(hs):K[ii+u,jj+v]+=np.sum(D*hu*hv)
       for j,sign in enumerate((1.,-1.)):
        Tr=bath.T_m_K*(1+sign*.001)
        ft=1/np.expm1(h*nt/(k*Tr));fs=1/np.expm1(h*ns/(k*Tr))
        # normalized activity, stable near thermal null
        at=np.exp(-h*nt/(k*Tr)+h*(nt-PCC.nu_abs)/(k*bath.T_m_K))
        az=np.exp(-h*ns/(k*Tr)+h*(ns-PCC.nu_abs)/(k*bath.T_m_K))
        direct[j]+=np.sum(D*(1+ft)*(1+fs)*(az-at)*(xt-xs))
    if np.any(K<0) or not np.all(np.isfinite(K)):raise ValueError("physical conductance")
    return K,direct

def compile_blocks(net,lane):
    bath=Bath(net.q['T'],net.q['n1s']);rows=[];edges=[]
    for typ,i,j,a,b in physical_blocks(net):
        K,d=integrate_pair(a,b,bath,lane,len(i),len(j))
        for u,ii in enumerate(i):
            for v,jj in enumerate(j):
                if K[u,v]>0:edges.append((ii,jj,float(K[u,v])))
        rows.append(dict(kind=typ,i=i,j=j,a=a,b=b,K=K.tolist(),direct_centered=d.tolist()))
    return edges,rows

class ExteriorPairs:
    def __init__(self,net,edges):
        self.net=net;self.edges=[(int(i),int(j),L(K)) for i,j,K in edges]
        self.z=np.exp(-(net.et-L(h)*L(net.q['nu'])/L(e))*L(e)/(L(k)*L(net.q['T'])))
        keys=[tuple(sorted((i,j))) for i,j,K in self.edges]
        if len(set(keys))!=len(keys) or any(i==j or i<0 or j<0 or max(i,j)>=len(net.et) or (i<net.ncore and j<net.ncore) or not np.isfinite(K) or K<0 for i,j,K in self.edges):raise ValueError("overlapping or invalid exterior pairs")
    def rates(self,s,i,j,K,delta=L(0)):
        fi=self.net.point_t(i,s.nt[i]+(s.dt[i]+delta));fj=self.net.point_t(j,s.nt[j]+(s.dt[j]-delta))
        return K*fj*(1+fi)/self.z[j],K*fi*(1+fj)/self.z[i]
    def action(self,s):
        E=L(0);gross=L(0)
        for i,j,K in self.edges:
            a,b=self.rates(s,i,j,K)
            E+=(a-b)*(self.net.et[i]-self.net.et[j]);gross+=(a+b)*abs(self.net.et[i]-self.net.et[j])
        return float(E),float(gross)
    def step(self,state,dt):
        if not math.isfinite(dt) or dt<=0:raise ValueError("dt")
        s=state.clone();old=s.dt.copy();gross=L(0);nflux=L(0);energy=L(0);cross=L(0);maxres=L(0)
        for seq in (self.edges,reversed(self.edges)):
            for i,j,K in seq:
                # rate is proportional to actual live ground-state density
                K=K*(s.neutral-s.n2-s.d2)/L(self.net.q['n1s'])
                A,B=self.rates(s,i,j,K);f0=(A-B)*L(dt)/2
                if f0==0:gross+=(A+B)*L(dt)/2;continue
                sg=L(1) if f0>0 else L(-1)
                cap=s.nt[j]+s.dt[j] if sg>0 else s.nt[i]+s.dt[i]
                span=min(abs(f0),cap)
                if span<=0:continue
                def residual(t):
                    d=sg*span*L(t);a,b=self.rates(s,i,j,K,d)
                    return float((d-(a-b)*L(dt)/2)/(sg*span))
                v=residual(1.)
                # When a near-null net rate is much smaller than its gross
                # forward/backward rates, relative-to-net bracket arithmetic
                # can be ill-conditioned. First enlarge the feasible bracket.
                # Accept an unresolved tiny net only against a documented
                # gross-rate residual, never a silently widened net target.
                while v<0 and span<cap:
                    span=min(2*span,cap);v=residual(1.)
                if v<0:
                    a,b=self.rates(s,i,j,K,sg*span)
                    if abs(sg*span-(a-b)*L(dt)/2)>1e-14*max((a+b)*L(dt)/2,L('1e-4900')):
                        raise ValueError("exterior event bracket")
                    t=1.
                else:t=brentq(residual,0.,1.,xtol=1e-15,rtol=1e-15,maxiter=100)
                d=sg*span*L(t);a,b=self.rates(s,i,j,K,d)
                g=(a+b)*L(dt)/2;gross+=g;maxres=max(maxres,abs(d-(a-b)*L(dt)/2)/max(g,L('1e-4900')))
                s.dt[i]+=d;s.dt[j]-=d;energy+=d*(self.net.et[i]-self.net.et[j])
                if i<self.net.ncore:cross+=d
                elif j<self.net.ncore:cross-=d
                nflux+=abs(d)
        delta=s.dt-old;dE=delta@self.net.et
        if np.min(s.nt+s.dt)<0:raise ValueError("negative exterior photons")
        scale=max(gross,L('1e-4900'));state.dt=s.dt
        return dict(number_relative=float(abs(np.sum(delta))/scale),energy_relative=float(abs(dE-energy)/(scale*self.net.transition)),energy_eV_m3=float(dE),bath_energy_eV_m3=float(-energy),cross_into_core=float(cross),gross=float(gross),net_event_abs=float(nflux),max_event_residual=float(maxres))
