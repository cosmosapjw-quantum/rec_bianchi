"""Equilibrium-interval exponential extent map, opt-in finite graph.
Each stage is transactional. No projection/clipping of physical stocks.
"""
import math
import numpy as np
from scipy.optimize import brentq
from full_bianchi_hyrec.trajectory.atomic_dynamic_companion import L

class ExtentRejected(ValueError):
    pass

def extent(net,s,event,h):
    if not math.isfinite(h) or h<=0:raise ValueError("positive event duration")
    h=L(h);i,j,sg,_,_=event
    F,G,A,B=net.net_rates(s,event)
    if not np.isfinite([A,B,F]).all() or min(A,B)<0:raise ExtentRejected("invalid initial rates")
    if F==0:return L(0),dict(gross=h*(A+B),saturation=False,root_relative=0.,roundoff_fallback=False)
    sign=L(1) if F>0 else L(-1);f0=abs(F)
    nt=s.nt[i]+s.dt[i];nc=s.nc[j]+s.dc[j];b=s.n2+s.d2
    forward=min(b,nc) if sg==-1 else b
    reverse=min(nt,s.neutral-b,nc) if sg==1 else min(nt,s.neutral-b)
    cap=forward if sign>0 else reverse
    if not np.isfinite(cap) or cap<=0:raise ExtentRejected("outward or empty extent")
    def rate(x):
        f,g,a,z=net.net_rates(s,event,sign*x)
        if not np.isfinite([f,g,a,z]).all() or min(a,z)<0:raise ExtentRejected("invalid rates")
        return sign*f,g
    # Locate a sign-changing interval comparable to the root rather than to
    # the possibly enormous stock cap. Use an inward trial if exact endpoint
    # arithmetic makes a boundary rate undefined.
    span=min(cap,max(h*f0,cap*L('1e-24')))
    lower=L(0)
    for _ in range(256):
        try:g,_=rate(span)
        except ValueError:
            if span!=cap:raise
            span=np.nextafter(cap,L(0));g,_=rate(span)
        if g<=0:break
        lower=span
        if span>=cap:raise ExtentRejected("equilibrium not bracketed")
        new=min(cap,2*span)
        if new<=span:raise ExtentRejected("bracket stagnation")
        span=new
    else:raise ExtentRejected("bracket iteration limit")
    if lower==0 and g<0:
        for _ in range(256):
            mid=span/2
            if mid<=0:raise ExtentRejected("root underflow")
            gm,_=rate(mid)
            if gm>=0:
                lower=mid
                if gm==0:span=mid;g=gm
                break
            span=mid;g=gm
        else:raise ExtentRejected("root scale not resolved")
    if g==0:star=span
    else:
        def fun(z):
            v,_=rate(span*L(z))
            q=v/f0
            return float(np.clip(q,L('-1e300'),L('1e300')))
        root=brentq(fun,float(lower/span),1.,xtol=5e-16,rtol=1e-15,maxiter=100)
        star=span*L(root)
    if not 0<star<=cap:raise ExtentRejected("equilibrium domain")
    gres,gross_star=rate(star)
    root_rel=float(abs(gres)/max(gross_star,f0,L('1e-4900')))
    if root_rel>1e-10:raise ExtentRejected("equilibrium residual")
    k0=f0/star
    half=-np.expm1(-h*k0/2)
    saturation=bool(half>1-L('1e-6'))
    # Only the rate evaluation is moved away from the rounded equilibrium;
    # the updated extent is not clipped or projected.
    eval_x=star*(min(half,L(1)-L('1e-6')))
    gm,gross_mid=rate(eval_x)
    km=gm/(star-eval_x)
    fallback=False
    if not np.isfinite(km) or km<=0:
        # Explicitly restricted numerical roundoff lane, not a proof of
        # exact equilibrium or a general replacement for the midpoint rate.
        eps=L(np.finfo(L).eps);stock=min(nt,nc,b,s.neutral-b)
        if (gm==0 and stock>0 and star<=64*eps*stock
            and f0<=64*eps*(A+B)):
            km=k0;fallback=True
        else:
            raise ExtentRejected("nonpositive relaxation rate")
    x=star*(-np.expm1(-h*km))
    if not 0<=x<=star:raise ExtentRejected("exponential interval")
    return sign*x,dict(gross=h*gross_mid,saturation=saturation,root_relative=root_rel,roundoff_fallback=fallback)

def source_step(net,state,dt):
    if not math.isfinite(dt) or dt<=0:raise ValueError("positive duration")
    s=state.clone();gross=L(0);sat=0;root=0.;fallbacks=0
    for seq in (net.events,reversed(net.events)):
        for event in seq:
            i,j,sg,_,_=event
            d,r=extent(net,s,event,L(dt)/2)
            s.dt[i]+=d;s.dc[j]+=sg*d;s.d2-=d
            if min(s.nt[i]+s.dt[i],s.nc[j]+s.dc[j],s.n2+s.d2,s.neutral-(s.n2+s.d2))<0:
                raise ExtentRejected("post-event positivity")
            gross+=r['gross'];sat+=int(r['saturation']);root=max(root,r['root_relative']);fallbacks+=int(r['roundoff_fallback'])
    state.dt,state.dc,state.d2=s.dt,s.dc,s.d2
    return dict(gross=gross,saturation=sat,max_root=root,roundoff_fallbacks=fallbacks)

def coupled_step(net,sc,state,dt):
    s=state.clone()
    a=source_step(net,s,dt/2);v=sc.step(s,dt);b=source_step(net,s,dt/2)
    state.dt,state.dc,state.d2=s.dt,s.dc,s.d2
    return dict(gross=a['gross']+b['gross']+L(v['gross']),bath=L(v['bath_energy_eV_m3']),
                cross=L(v['cross_into_com']),new_energy=L(v['new_energy']),
                saturation=a['saturation']+b['saturation'],max_root=max(a['max_root'],b['max_root']),roundoff_fallbacks=a['roundoff_fallbacks']+b['roundoff_fallbacks'])
