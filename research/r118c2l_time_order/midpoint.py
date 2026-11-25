"""Opt-in finite graph integrator. Original source owner and default stay unchanged."""
import math
import numpy as np
from scipy.optimize import brentq
from full_bianchi_hyrec.trajectory.atomic_dynamic_companion import L

class StepRejected(ValueError):
    pass

def extent(net,s,event,h):
    """Solve d=h F(s+d*v/2) on the physical extent interval; no clipping."""
    i,j,sg,_,_=event
    A,B=net.rates(s,event)
    f=A-B
    if f==0:
        return L(0),h*(A+B),L(0)
    nt=s.nt[i]+s.dt[i];nc=s.nc[j]+s.dc[j];b=s.n2+s.d2
    cap=min(b,nc) if sg==-1 else b
    low=min(nt,s.neutral-b,nc) if sg==1 else min(nt,s.neutral-b)
    sign=L(1) if f>0 else L(-1)
    cap=cap if f>0 else low
    if cap<=0:
        raise StepRejected("outward flux at boundary")
    span=min(cap,2*h*abs(f))
    def root(t):
        d=sign*span*L(t)
        a,z=net.rates(s,event,d/2)
        return float((d-h*(a-z))/(sign*span))
    for _ in range(100):
        if root(1.)>=0:
            break
        if span==cap:
            raise StepRejected("midpoint root outside feasible extent")
        span=min(cap,2*span)
    else:
        raise StepRejected("bracket expansion limit")
    t=brentq(root,0.,1.,xtol=1e-15,rtol=1e-15)
    d=sign*span*L(t)
    a,z=net.rates(s,event,d/2)
    g=h*(a+z)
    res=abs(d-h*(a-z))/max(g,L('1e-4900'))
    return d,g,res

def source_step(net,state,dt):
    if not math.isfinite(dt) or dt<=0:
        raise ValueError("positive time required")
    s=state.clone();gross=L(0);maxres=L(0)
    for seq in (net.events,reversed(net.events)):
        for event in seq:
            i,j,sg,_,_=event
            d,g,res=extent(net,s,event,L(dt)/2)
            s.dt[i]+=d;s.dc[j]+=sg*d;s.d2-=d
            gross+=g;maxres=max(maxres,res)
    if np.min(s.nt+s.dt)<0 or np.min(s.nc+s.dc)<0 or not 0<=s.n2+s.d2<=s.neutral:
        raise StepRejected("source positivity")
    state.dt,state.dc,state.d2=s.dt,s.dc,s.d2
    return gross,maxres

def coupled_step(net,sc,state,dt):
    """Source midpoint symmetric sweep(h/2), scatter SSPRK2(h), source sweep(h/2).
    Transactional: original state remains unchanged if any stage fails."""
    s=state.clone()
    g0,r0=source_step(net,s,dt/2)
    v=sc.step(s,dt)
    g1,r1=source_step(net,s,dt/2)
    state.dt,state.dc,state.d2=s.dt,s.dc,s.d2
    return dict(gross=g0+g1+L(v['gross']),max_event_residual=max(r0,r1),
                bath=L(v['bath_energy_eV_m3']),cross=L(v['cross_into_com']),
                new_energy=L(v['new_energy']))
