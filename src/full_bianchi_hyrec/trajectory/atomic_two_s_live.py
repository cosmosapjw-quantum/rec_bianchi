"""Bounded coupled 2s/1s + resolved tracked photons, actual source-table events.
Companion radiation is a declared fixed Planck reservoir; HII/2p fixed.
The 2s line source replaces itself only in this subproblem. No native
diffusion, Sobolev or FULL virtual state source simultaneously applied.
"""
from dataclasses import dataclass
import math
import numpy as np
from scipy.constants import h,k,e
from scipy.optimize import brentq
from .atomic_point_transfer import point_partition
from .hyrec_two_photon_raman import OriginalHyRecTwoPhotonRamanTable,A2S_THRESHOLD_EV
from ..recoil.calibrated_source import owner_cells

@dataclass(frozen=True)
class Step:
    f:np.ndarray
    n2:float
    tracked_n:float
    companion_n:float
    tracked_u_eV_m3:float
    companion_u_eV_m3:float
    atom_u_eV_m3:float
    number_defect:float
    energy_defect_eV_m3:float
    max_node_residual:float
    atom_residual:float
    gross_events:float

class TwoSNetwork:
    def __init__(self,archive,q,companion_T):
        self.q=q;self.transition_eV=A2S_THRESHOLD_EV
        if not math.isfinite(companion_T) or companion_T<=0:raise ValueError("companion temperature")
        tab=OriginalHyRecTwoPhotonRamanTable.from_archive(archive)
        x,idx,P,det=point_partition(tab.energy_eV,owner_cells(),q['sub'])
        if not np.array_equal(x,q['x']):raise ValueError("source/hat registry mismatch")
        self.e_ev=h*(q['nu']+q['dnu']*x)/e
        self.znode=np.exp(-h*q['dnu']*x/(k*q['T']))
        self.events=[]
        for col,i in enumerate(idx):
            for node in np.flatnonzero(P[:,col]):
                en=self.e_ev[node];comp=abs(self.transition_eV-en)
                kind=1 if en<self.transition_eV else -1
                if kind!=(1 if tab.process_kind("2s",int(i))=="two_photon" else -1):
                    raise ValueError("source splitting crosses a process threshold")
                if comp<=0:raise ValueError("zero companion energy")
                fc=1/np.expm1(comp*e/(k*companion_T))
                rate=float(tab.A2s_s_inv[i]*P[node,col])
                if rate==0:continue
                A=rate*(1+fc if kind==1 else fc);B=rate*(fc if kind==1 else 1+fc)
                self.events.append((node,int(i),A,B,kind,comp))
        self.active=np.array(sorted({v[0] for v in self.events}),int)
        self.A=np.zeros(len(x));self.B=self.A.copy()
        for i,_,A,B,_,_ in self.events:self.A[i]+=A;self.B[i]+=B
        self.mean=np.array([w@z for w,z in zip(q['w'],q['z'])])
        self.pole=np.array([1/max(max(z),self.znode[i]) for i,z in enumerate(q['z'])])
    def step(self,f,n2,neutral,dt):
        q=self.q;f=np.asarray(f,float)
        if f.shape!=q['g'].shape or not np.isfinite(f).all() or np.any(f<0) or not all(map(math.isfinite,(n2,neutral,dt))) or not 0<=n2<=neutral or neutral<=0 or dt<0:
            raise ValueError("invalid 2s state")
        if dt==0:return Step(f.copy(),n2,0.,0.,0.,0.,0.,0.,0.,0.,0.,0.)
        g=q['g'];old=g*f
        # In the non-inverted regime, fixed-n2 photon BE residual is
        # strictly increasing in activity. Atom residual is increasing
        # since photon stocks increase monotonically with n2.
        inv=min(neutral*self.B[i]/(self.A[i]+self.B[i]) for i in self.active)
        upper=min(n2+math.fsum(old[self.active]),inv*(1-1e-12))
        if n2>upper:raise ValueError("outside non-inverted bounded 2s domain")
        def photon(i,b):
            A=self.A[i]*b;C=self.B[i]*(neutral-b)-A
            if C<0:raise ValueError("inverted 2s trial")
            target=old[i]+dt*A
            if target==0:return 0.,0.
            den=g[i]*self.mean[i]+dt*C*self.znode[i]
            hi=min(target/den*(1+8e-15),.9*self.pole[i])
            if hi<=0:raise ValueError("activity range")
            def v(a):
                y=a*q['z'][i];p=a*self.znode[i]
                return float(g[i]*(q['w'][i]@(y/(1-y)))),float(p/(1-p))
            def residual(t):
                N,p=v(t*hi);return (N+dt*C*p-target)/target
            if residual(1.)<0:raise ValueError("source activity outside bounded reconstruction")
            t=brentq(residual,0.,1.,xtol=1e-15,rtol=1e-15,maxiter=100)
            return v(t*hi)
        def evaluate(b):
            ns=np.array([photon(i,b) for i in self.active])
            p=ns[:,1];net=dt*(self.A[self.active]*b-(self.B[self.active]*(neutral-b)-self.A[self.active]*b)*p)
            return (b-n2)+math.fsum(net),ns,net
        if upper==0:return Step(f.copy(),n2,0.,0.,0.,0.,0.,0.,0.,0.,0.,0.)
        lo=evaluate(0.)[0];hi=evaluate(upper)[0]
        if lo>0 or hi<0:raise ValueError(f"no non-inverted 2s root: {lo} {hi}")
        b=brentq(lambda b:evaluate(b)[0],0.,upper,xtol=1e-30,rtol=1e-15,maxiter=200)
        ar,ns,net=evaluate(b)
        out=f.copy();out[self.active]=ns[:,0]/g[self.active]
        p=dict(zip(self.active,ns[:,1]));cnt=[];compn=[];cu=[];tu=[];gross=0.
        for i,_,A,B,sign,comp in self.events:
            fw=dt*A*b*(1+p[i]);rv=dt*B*(neutral-b)*p[i]
            delta=fw-rv;gross+=fw+rv
            cnt.append(delta);compn.append(sign*delta);cu.append(sign*comp*delta);tu.append(self.e_ev[i]*delta)
        tracked=math.fsum(cnt);comp=math.fsum(compn);ue=math.fsum(tu);uc=math.fsum(cu);ua=-self.transition_eV*tracked
        change=g[self.active]*(out[self.active]-f[self.active])
        number=(b-n2)+math.fsum(change)
        # Physical reservoir energy ledger uses actual state increments for
        # the tracked photon and atom, not a manufactured opposing entry.
        energy=math.fsum(change*self.e_ev[self.active])+self.transition_eV*(b-n2)+uc
        node=float(np.max(abs(change-net)))/max(gross,1e-300)
        return Step(out,b,tracked,comp,ue,uc,ua,number,energy,node,abs(ar)/max(gross,1e-300),gross)
