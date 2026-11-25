"""Common physical tracked/companion registry for a bounded exterior extension.

The two outer COM parents and six wing cells are refined. Other original
COM blocks are retained. All rates refer to the same physical hat stocks;
the old exterior point stock is removed, not duplicated.
"""
import math
import numpy as np
from scipy.constants import h,k,e,c
from numpy.polynomial.legendre import leggauss
from .atomic_dynamic_companion import DynamicTwoS,L,PHASE,nodal_volume
from .atomic_physical_exterior import physical_blocks
from .hyrec_two_photon_raman import OriginalHyRecTwoPhotonRamanTable
from ..recoil.calibrated_source import PCC,EX,Bath,angular,density,uv_nodes,tensor_nodes,owner_cells

class RefinedTwoS(DynamicTwoS):
    def __init__(self,archive,q,n):
        if q['sub']!=4 or n not in (16,32,64,128):raise ValueError("mixed mesh domain")
        old=DynamicTwoS(archive,q);self.transition=old.transition
        self.bounds=list(map(tuple,owner_cells()));self.cross_blocks=[];selected=[]
        for typ,I,J,a,b in physical_blocks(old):
            if typ=='cross':
                i=I[0]//5
            else:i=len(self.bounds)-1
            j=len(self.bounds);self.bounds.append(b);selected.append(J[0]-old.ncore)
            self.cross_blocks.append((typ,i,j,a,b))
        if len(set(selected))!=6:raise ValueError("duplicate exterior owner")
        self.levels=[n if i in (29,34) or i>=35 else 4 for i in range(41)]
        self.offset=np.r_[0,np.cumsum(np.array(self.levels)+1)]
        self.ncom=int(self.offset[35]);self.ncore=int(self.offset[-1])
        xs=[np.linspace(*b,l+1) for b,l in zip(self.bounds,self.levels)]
        x=np.concatenate(xs);u,gw=leggauss(24);u=(u+1)/2;gw=gw/2
        w=[[] for _ in x];xx=[[] for _ in x]
        for m,grid in enumerate(xs):
            for j,(lo,hi) in enumerate(zip(grid[:-1],grid[1:])):
                s=lo+(hi-lo)*u
                wt=8*np.pi*q['dnu']/c**3*(hi-lo)*gw*(q['nu']+q['dnu']*s)**2
                for b,hat in [(j,1-u),(j+1,u)]:
                    idx=int(self.offset[m]+b);xx[idx].extend(s);w[idx].extend(wt*hat)
        g=np.array([sum(v) for v in w]);self.w=[np.asarray(v,dtype=L)/L(a) for v,a in zip(w,g)]
        # Normalize weights in extended precision, not by rounded sum.
        self.w=[v/v.sum() for v in self.w]
        self.z=[np.exp(-L(h)*L(q['dnu'])*np.asarray(v,dtype=L)/(L(k)*L(q['T']))) for v in xx]
        self.zmean=np.array([a@b for a,b in zip(self.w,self.z)])
        self.zi=np.exp(-L(h)*L(q['dnu'])*np.asarray(x,dtype=L)/(L(k)*L(q['T'])))
        self.q=dict(q,x=x,g=g,w=self.w,z=self.z,xx=xx)
        keep=np.setdiff1d(np.arange(len(old.exterior_indices)),selected)
        self.exterior_indices=old.exterior_indices[keep]
        self.et=np.r_[L(h)*(L(q['nu'])+L(q['dnu'])*np.asarray(x,dtype=L))/L(e),old.et[old.ncore+keep]]
        self.gt=np.r_[np.asarray(g,dtype=L),old.gt[old.ncore+keep]]
        self.phase_relative=max(float(abs(self.gt[self.ids(35+j)].sum()/old.gt[old.ncore+idx]-1)) for j,idx in enumerate(selected))
        if self.phase_relative>1e-9:raise ValueError("exterior phase partition")
        tab=OriginalHyRecTwoPhotonRamanTable.from_archive(archive);self.owner_indices=np.arange(len(tab.energy_eV))
        events=[];self.rate_aggregate=np.zeros(len(tab.energy_eV),dtype=L);energy=np.zeros_like(self.rate_aggregate)
        lookup={int(i):self.ncore+j for j,i in enumerate(self.exterior_indices)}
        for i,E in enumerate(tab.energy_eV):
            E=L(E);rate=L(tab.A2s_s_inv[i])
            if i in lookup:parts=[(lookup[i],L(1))]
            else:
                matches=[j for j in range(41) if self.et[self.offset[j]]<=E<=self.et[self.offset[j+1]-1]]
                if len(matches)!=1:raise ValueError("nonunique source point owner")
                a,b=self.offset[matches[0]:matches[0]+2]
                j=a+min(int(np.searchsorted(self.et[a:b],E,side='right'))-1,b-a-2)
                t=(E-self.et[j])/(self.et[j+1]-self.et[j]);parts=[(j,1-t),(j+1,t)]
            for j,v in parts:
                if v<0 or v>1:raise ValueError("source hat support")
                if v*rate>0:events.append((int(j),i,rate*v))
                self.rate_aggregate[i]+=rate*v;energy[i]+=rate*v*self.et[j]
        self.source_rate_relative=float(np.max(abs(self.rate_aggregate-tab.A2s_s_inv)/np.maximum(tab.A2s_s_inv,1e-300)))
        self.source_energy_relative=float(np.max(abs(energy-tab.A2s_s_inv*tab.energy_eV)/np.maximum(tab.A2s_s_inv*tab.energy_eV,1e-300)))
        comp=np.asarray([abs(self.transition-self.et[j]) for j,_,_ in events],dtype=L)
        self.ec,ci=np.unique(comp,return_inverse=True)
        self.gc=nodal_volume(self.ec,L(0),self.transition/2);self.events=[]
        for (j,i,r),m in zip(events,ci):
            sign=1 if self.et[j]<self.transition else -1
            if sign!=(1 if tab.process_kind('2s',i)=='two_photon' else -1):raise ValueError("changed process kind")
            self.events.append((j,int(m),sign,r,i))
        # fixed padded quadrature for vector point activity inversion
        width=max(map(len,self.w))
        self._w=np.zeros((self.ncore,width),dtype=L);self._z=np.ones_like(self._w)
        for i,(w,z) in enumerate(zip(self.w,self.z)):
            self._w[i,:len(w)]=w;self._z[i,:len(z)]=z
    def ids(self,parent):
        return np.arange(self.offset[parent],self.offset[parent+1],dtype=int)
    def point_values(self,s):
        f=(s.nt+s.dt)/self.gt
        if np.min(f)<0:raise ValueError("negative stock")
        a=f[:self.ncore]/(1+f[:self.ncore])/self.zmean
        for _ in range(8):
            y=a[:,None]*self._z
            if np.any(y>=1):raise ValueError("activity pole")
            a-=(np.sum(self._w*y/(1-y),axis=1)-f[:self.ncore])/np.sum(self._w*self._z/(1-y)**2,axis=1)
        v=a*self.zi
        if np.min(v)<0 or np.max(v)>=1:raise ValueError("activity domain")
        f[:self.ncore]=v/(1-v)
        return f

def lift_pair(x,y,w,a,b):
    i=np.searchsorted(a,x,side='right')-1;j=np.searchsorted(b,y,side='right')-1
    i=np.minimum(i,len(a)-2);j=np.minimum(j,len(b)-2)
    if min(i.min(),j.min())<0:raise ValueError("lift outside support")
    t=(x-a[i])/(a[i+1]-a[i]);s=(y-b[j])/(b[j+1]-b[j])
    if min(t.min(),s.min())<0 or max(t.max(),s.max())>1:raise ValueError("lift support")
    n=len(b);index=i*n+j;Q=np.zeros(len(a)*n)
    for off,z in ((0,(1-t)*(1-s)),(1,(1-t)*s),(n,t*(1-s)),(n+1,t*s)):
        Q+=np.bincount(index+off,weights=w*z,minlength=len(Q))
    return Q.reshape(len(a),len(b))

def compile_integrals(net,bath):
    """Integrate 34 re-lifted original blocks and six new blocks.
    Accumulate angular weights before the frequency-hat deposit. No new
    approximation in angular integration relative to the selected lane."""
    out=[]
    for i,j in [(i,j) for i in range(17) for j in (29,34)]+[(i,j) for _,i,j,_,_ in net.cross_blocks]:
        original=j<35
        I,J=(j,i) if original else (i,j)
        a,b=net.bounds[I],net.bounds[J];par=EX.LANES['production' if original else 'reference']
        mu,wmu=angular(par)
        use=np.ones(len(mu),bool)
        if original:
            use=np.arange(len(mu))<par['ob']
            use|=EX._crosses_resonance_mean(tuple(a),tuple(b))|((mu>.995)&EX._touching_intervals(tuple(a),tuple(b)))
        nodes=[]
        for mask,rule in [(use,lambda:uv_nodes(a,b,par,.08)),(~use,lambda:tensor_nodes(a,b,par['nf']))]:
            if not np.any(mask):continue
            nt,ns,ww=rule();D=np.zeros_like(ww)
            for ix in np.array_split(np.flatnonzero(mask),max(1,int(np.ceil(mask.sum()/8)))):
                m=mu[ix,None]
                D+=np.sum(density(nt[None,:],ns[None,:],m,bath)*(wmu[ix,None]*.75*(1+m*m))*ww[None,:]*(8*np.pi*PCC.dnu/c**3/bath.z0),axis=0)
            xt=(nt-PCC.nu_abs)/PCC.dnu;xs=(ns-PCC.nu_abs)/PCC.dnu
            nodes.append((xs,xt,D) if original else (xt,xs,D))
        x,y,w=map(np.concatenate,zip(*nodes))
        out.append((i,j,x,y,w))
    return out

def assemble(net,data,integrals):
    old={(int(i),int(j)):Q for (i,j),Q in zip(data['pairs'],data['Q4'])}
    blocks={(i,j):(x,y,w) for i,j,x,y,w in integrals}
    edges=[];max_coarse=0.;max_marg=0.;direct=np.zeros(2);new_keys=set()
    for i,j in sorted(set(old)|set(blocks)):
        a,b=net.q['x'][net.ids(i)],net.q['x'][net.ids(j)]
        if (i,j) in blocks:
            x,y,w=blocks[i,j];K=lift_pair(x,y,w,a,b);s=w.sum()
            if s>0:
                max_marg=max(max_marg,max(abs(K.sum()-s),abs(K.sum(axis=1)@a-w@x),abs(K.sum(axis=0)@b-w@y))/s)
            if (i,j) in old:
                aa=np.linspace(*net.bounds[i],5);bb=np.linspace(*net.bounds[j],5)
                P=np.stack([np.interp(a,aa,v) for v in np.eye(5)],axis=1)
                Q=np.stack([np.interp(b,bb,v) for v in np.eye(5)],axis=1)
                den=max(old[i,j].sum(),1e-300)
                max_coarse=max(max_coarse,np.sum(abs(P.T@K@Q-old[i,j]))/den)
            else:
                new_keys.add((i,j))
                for k0,sg in enumerate((1.,-1.)):
                    Tr=net.q['T']*(1+sg*.001)
                    nu=net.q['nu']+net.q['dnu']*x;nv=net.q['nu']+net.q['dnu']*y
                    ft=1/np.expm1(h*nu/(k*Tr));fs=1/np.expm1(h*nv/(k*Tr))
                    at=np.exp(-h*nu/(k*Tr)+h*net.q['dnu']*x/(k*net.q['T']))
                    az=np.exp(-h*nv/(k*Tr)+h*net.q['dnu']*y/(k*net.q['T']))
                    direct[k0]+=np.sum(w*(1+ft)*(1+fs)*(az-at)*(x-y))
        else:K=old[i,j]
        if np.min(K)<0 or not np.all(np.isfinite(K)):raise ValueError("conductance domain")
        ix,jx=np.nonzero(np.triu(K,1) if i==j else K)
        I,J=net.ids(i),net.ids(j)
        edges.extend((int(I[u]),int(J[v]),float(K[u,v]),i<35<=j,(i,j) in new_keys) for u,v in zip(ix,jx))
    if len(new_keys)!=6 or max_coarse>1e-10 or max_marg>1e-10:raise ValueError(f"ownership/coarse parity {max_coarse} {max_marg}")
    return edges,dict(original_blocks=len(old),relifted_blocks=34,new_blocks=len(new_keys),coarse_error=float(max_coarse),moment_error=float(max_marg),direct=direct.tolist())

class Scatter:
    def __init__(self,net,edges):
        self.net=net
        self.i=np.array([x[0] for x in edges],int);self.j=np.array([x[1] for x in edges],int)
        self.K=np.array([x[2] for x in edges],dtype=L)
        self.cross=np.array([x[3] for x in edges],bool)
        self.new=np.array([x[4] if len(x)>4 else x[3] for x in edges],bool)
        if len(set(zip(self.i,self.j)))!=len(edges) or np.any(self.i>=self.j) or np.any(self.K<0) or not np.all(np.isfinite(self.K)):raise ValueError("edge identity")
        self.z=np.exp(-(net.et-L(h)*L(net.q['nu'])/L(e))*L(e)/(L(k)*L(net.q['T'])))
        self.de=net.et[self.i]-net.et[self.j]
    def rates(self,s):
        f=self.net.point_values(s);a=f/(self.z*(1+f))
        fac=self.K*(1+f[self.i])*(1+f[self.j])*(s.neutral-s.n2-s.d2)/L(self.net.q['n1s'])
        return fac*(a[self.j]-a[self.i]),fac*(a[self.j]+a[self.i])
    def action(self,s):
        f,g=self.rates(s);return float(f[self.new]@self.de[self.new]),float(g[self.new]@abs(self.de[self.new]))
    def rhs(self,s):
        f,g=self.rates(s);d=np.zeros_like(s.dt);np.add.at(d,self.i,f);np.add.at(d,self.j,-f)
        return d,f,g
    def step(self,s,dt):
        if not math.isfinite(dt) or dt<=0:raise ValueError("dt")
        old=s.dt.copy();d,f,g=self.rhs(s);ds=L(dt);trial=s.clone();trial.dt=old+ds*d
        if np.min(trial.nt+trial.dt)<0:raise ValueError("first Euler positivity/CFL")
        d1,f1,g1=self.rhs(trial)
        if np.min(trial.nt+trial.dt+ds*d1)<0:raise ValueError("second Euler positivity/CFL")
        delta=ds/2*(d+d1);flux=ds/2*(f+f1);gross=ds/2*np.sum(g+g1)
        new=old+delta
        if np.min(s.nt+new)<0:raise ValueError("SSPRK2 positivity")
        actual=new-old;de=flux@self.de;scale=max(gross,L('1e-4900'))
        r=dict(gross=float(gross),energy_eV_m3=float(de),bath_energy_eV_m3=float(-de),cross_into_com=float(np.sum(flux[self.cross])),new_energy=float(flux[self.new]@self.de[self.new]),number_relative=float(abs(np.sum(actual))/scale),energy_relative=float(abs(actual@self.net.et-de)/(scale*self.net.transition)),net_energy_relative=float(abs(actual@self.net.et-de)/max(abs(de),scale*L('1e-20'))))
        s.dt=new;return r
