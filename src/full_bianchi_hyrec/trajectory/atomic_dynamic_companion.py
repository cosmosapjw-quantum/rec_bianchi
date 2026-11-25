"""Finite positive 2s paired-event model with actual source table and live
tracked + companion stocks. Original high-frequency table is one-sided:
all source energies exceed E21/2, their partners are below E21/2.
Exterior/companion phase volumes are an explicitly chosen auxiliary nodal
closure, NOT widths assigned to original zero-width virtual states.
No native diffusion or Sobolev owner is included. Fixed T, HII, 2p.
"""
from dataclasses import dataclass
import math
import numpy as np
from scipy.constants import h,k,e,c
from scipy.optimize import brentq
from .atomic_point_transfer import point_partition
from .hyrec_two_photon_raman import OriginalHyRecTwoPhotonRamanTable,A2S_THRESHOLD_EV
from ..recoil.calibrated_source import owner_cells
L=np.longdouble
PHASE=L(8)*L(str(math.pi))*(L(e)/L(h)/L(c))**3

def nodal_volume(energy,lo,hi):
    v=np.asarray(energy,dtype=L)
    if not len(v) or np.any(np.diff(v)<=0) or not lo<v[0] or not v[-1]<hi:raise ValueError("auxiliary mode support")
    ed=np.r_[L(lo),(v[:-1]+v[1:])/2,L(hi)]
    g=PHASE*(ed[1:]-ed[:-1])*(ed[1:]**2+ed[1:]*ed[:-1]+ed[:-1]**2)/3
    if np.any(g<=0):raise ValueError("phase volume")
    return g

@dataclass
class State:
    nt:np.ndarray;nc:np.ndarray;n2:L;neutral:L
    dt:np.ndarray;dc:np.ndarray;d2:L=L(0)
    def clone(self):
        return State(self.nt,self.nc,self.n2,self.neutral,self.dt.copy(),self.dc.copy(),L(self.d2))

class DynamicTwoS:
    def __init__(self,archive,q):
        self.q=q;self.transition=L(A2S_THRESHOLD_EV);self.ncore=len(q['g'])
        tab=OriginalHyRecTwoPhotonRamanTable.from_archive(archive)
        x,idx,P,_=point_partition(tab.energy_eV,owner_cells(),q['sub'])
        if not np.array_equal(x,q['x']):raise ValueError("core registry")
        self.owner_indices=np.arange(len(tab.energy_eV))
        self.exterior_indices=np.setdiff1d(self.owner_indices,idx)
        core=np.asarray(h*(q['nu']+q['dnu']*x)/e,dtype=L)
        ext=np.asarray(tab.energy_eV[self.exterior_indices],dtype=L)
        self.et=np.r_[core,ext]
        if np.min(self.et)<=self.transition/2 or np.any(self.et==self.transition):raise ValueError("not a disjoint one-sided source")
        # Separate auxiliary exterior volumes at the actual COM faces.
        red=ext<core.min();blue=ext>core.max()
        if not np.all(red|blue):raise ValueError("overlap between auxiliary exterior and COM")
        ge=np.empty_like(ext)
        ge[red]=nodal_volume(ext[red],self.transition/2,core.min())
        ge[blue]=nodal_volume(ext[blue],core.max(),ext[-1]+(ext[-1]-ext[-2])/2)
        self.gt=np.r_[np.asarray(q['g'],dtype=L),ge]
        events=[]
        for j,i in enumerate(idx):
            for n in np.flatnonzero(P[:,j]):
                events.append((int(n),int(i),L(tab.A2s_s_inv[i])*L(P[n,j])))
        for j,i in enumerate(self.exterior_indices):
            events.append((self.ncore+j,int(i),L(tab.A2s_s_inv[i])))
        events=[(n,i,r) for n,i,r in events if r>0]
        companions=np.asarray([abs(self.transition-self.et[n]) for n,_,_ in events],dtype=L)
        self.ec,ci=np.unique(companions,return_inverse=True)
        if self.ec[-1]>=self.transition/2 or self.ec[0]<=0:raise ValueError("overlap/zero companion")
        self.gc=nodal_volume(self.ec,L(0),self.transition/2)
        self.events=[]
        self.rate_aggregate=np.zeros(len(tab.energy_eV),dtype=L)
        for (n,i,r),j in zip(events,ci):
            sign=1 if self.et[n]<self.transition else -1
            if sign!=(1 if tab.process_kind('2s',i)=='two_photon' else -1):raise ValueError("process threshold changed")
            self.events.append((n,int(j),sign,r,i))
            self.rate_aggregate[i]+=r
        self.source_rate_relative=float(np.max(abs(self.rate_aggregate-tab.A2s_s_inv)/np.maximum(tab.A2s_s_inv,1e-300)))
        self.zi=np.exp(-L(h)*L(q['dnu'])*np.asarray(x,dtype=L)/(L(k)*L(q['T'])))
        self.w=[np.asarray(w,dtype=L) for w in q['w']];self.z=[np.asarray(z,dtype=L) for z in q['z']]
        self.zmean=np.array([w@z for w,z in zip(self.w,self.z)])
    def initial(self,T,neutral,n2=None,*,equilibrium=False,tracked_vacuum=False,tracked_temperature=None,companion_scale=1.):
        T=L(T);neutral=L(neutral);tt=T if tracked_temperature is None else L(tracked_temperature)
        if min(T,tt,neutral)<=0 or not np.isfinite([T,tt,neutral,companion_scale]).all() or companion_scale<0:raise ValueError("initial state")
        beta=L(e)/(L(k)*T)
        if equilibrium:
            if n2 is not None or tracked_vacuum or tt!=T or companion_scale!=1.:raise ValueError("inconsistent equilibrium")
            ratio=np.exp(-beta*self.transition);n2=neutral*ratio/(1+ratio)
        elif n2 is None:raise ValueError("n2 required")
        n2=L(n2)
        if not 0<=n2<=neutral:raise ValueError("population domain")
        ft=1/np.expm1(self.et*L(e)/(L(k)*tt))
        for i,(w,xx) in enumerate(zip(self.w,self.q['xx'])):
            E=L(h)*(L(self.q['nu'])+L(self.q['dnu'])*np.asarray(xx,dtype=L))/L(e)
            ft[i]=w@(1/np.expm1(E*L(e)/(L(k)*tt)))
        if tracked_vacuum:ft.fill(0)
        nc=self.gc*(L(companion_scale)/np.expm1(beta*self.ec))
        return State(self.gt*ft,nc,n2,neutral,np.zeros_like(ft),np.zeros_like(nc))
    def point_t(self,i,mass):
        f=mass/self.gt[i]
        if f<0:raise ValueError("negative tracked stock")
        if i>=self.ncore or f==0:return f
        a=f/(1+f)/self.zmean[i];w,z=self.w[i],self.z[i]
        for _ in range(12):
            y=a*z
            if np.any(y>=1):raise ValueError("activity pole")
            d=(w@(y/(1-y))-f)/(w@(z/(1-y)**2))
            a-=d
            if abs(d)<=8*np.finfo(L).eps*max(abs(a),L('1e-4900')):break
        v=a*self.zi[i]
        if not 0<=v<1:raise ValueError("point activity domain")
        return v/(1-v)
    def rates(self,s,event,delta=L(0)):
        i,j,sg,r,_=event
        ft=self.point_t(i,s.nt[i]+(s.dt[i]+delta))
        fc=(s.nc[j]+(s.dc[j]+sg*delta))/self.gc[j]
        b=s.n2+(s.d2-delta)
        if fc<0 or b<0 or b>s.neutral:raise ValueError("negative companion or atomic stock")
        A=r*b*(1+ft)*((1+fc) if sg==1 else fc)
        B=r*(s.neutral-b)*ft*(fc if sg==1 else (1+fc))
        return A,B
    def action(self,s):
        v=np.array([self.rates(s,p) for p in self.events],dtype=L)
        return dict(flux=v[:,0]-v[:,1],gross=np.sum(v))
    def step(self,state,dt):
        if not math.isfinite(dt) or dt<=0:raise ValueError("positive time required")
        s=state.clone();old=s.clone();dt=L(dt);gross=L(0);jnet=L(0);cnet=L(0)
        max_res=L(0)
        # Symmetric event ordering is used only to reduce ordering bias;
        # per-event BE remains first order, not an exact Strang step.
        for seq in (self.events,reversed(self.events)):
            for event in seq:
                i,j,sg,r,_=event;A,B=self.rates(s,event);f0=(A-B)*dt/2
                if f0==0:gross+=(A+B)*dt/2;continue
                nt=s.nt[i]+s.dt[i];nc=s.nc[j]+s.dc[j];b=s.n2+s.d2
                cap=min(b,nc) if sg==-1 else b
                low=min(nt,s.neutral-b,nc) if sg==1 else min(nt,s.neutral-b)
                span=min(abs(f0),cap if f0>0 else low)
                if span==0:gross+=(A+B)*dt/2;continue
                direction=L(1) if f0>0 else L(-1)
                def fun(t):
                    de=direction*span*L(t);a,z=self.rates(s,event,de)
                    return float((de-(a-z)*dt/2)/(direction*span))
                # At feasibility bound floating-point cancellation may make
                # an exact boundary stock marginally negative; no clipping.
                v=fun(1.)
                if v<0:
                    if v>-1e-12:theta=1.
                    else:raise ValueError("event BE bracket")
                else:theta=brentq(fun,0.,1.,xtol=1e-15,rtol=1e-15,maxiter=100)
                de=direction*span*L(theta)
                a,z=self.rates(s,event,de);g=(a+z)*dt/2
                max_res=max(max_res,abs(de-(a-z)*dt/2)/max(g,L('1e-4900')))
                s.dt[i]+=de;s.dc[j]+=sg*de;s.d2-=de
                gross+=g;jnet+=de;cnet+=sg*de
        dn=s.dt-old.dt;dc=s.dc-old.dc;da=s.d2-old.d2
        if np.min(s.nt+s.dt)<0 or np.min(s.nc+s.dc)<0 or not 0<=s.n2+s.d2<=s.neutral:raise ValueError("state left positive domain")
        num=max(abs(np.sum(dn)+da),abs(np.sum(dn)-jnet),abs(np.sum(dc)-cnet))
        en=dn@self.et+dc@self.ec+self.transition*da
        scale=max(gross,L('1e-4900'))
        out=dict(gross=float(gross),tracked_N=float(np.sum(dn)),companion_N=float(np.sum(dc)),atom_delta=float(da),number_relative=float(num/scale),energy_relative=float(abs(en)/(scale*self.transition)),energy_eV_m3=float(en),max_event_residual=float(max_res),max_companion_relative=float(np.max(abs(s.dc)/np.maximum(s.nc,L('1e-4900')))))
        state.dt=s.dt;state.dc=s.dc;state.d2=s.d2
        return out
