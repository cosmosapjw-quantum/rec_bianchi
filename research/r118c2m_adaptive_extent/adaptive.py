"""Adaptive finite-graph C2L extent/SSPRK2 method; no production owner change."""
import math,sys
from pathlib import Path
import numpy as np
from full_bianchi_hyrec.trajectory.atomic_dynamic_companion import L
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'r118c2l_time_order'))
from midpoint import coupled_step, StepRejected
POS_ERRORS={'first Euler positivity/CFL','second Euler positivity/CFL','SSPRK2 positivity'}

def combine(a,b):
    return {k:(max(a[k],b[k]) if k=='max_event_residual' else a[k]+b[k]) for k in a}

def scaled(a,b,den):
    return abs(a-b)/max(abs(a),abs(b),den)

def estimate(old,coarse,fine,c,f,transition):
    # Relative LOCAL response differences, not relative total background stocks.
    # Floor regularizes nearly cancelling responses (gross event scale).
    floor=L('1e-10')*max(c['gross'],f['gross'],L('1e-300'))
    def l1(a,b,o):
        return np.sum(abs(a-b))/max(np.sum(abs(a-o)),np.sum(abs(b-o)),floor)
    # A large depletion can yield a tiny relative increment difference while
    # the surviving species is grossly inaccurate. Test endpoint stocks too.
    def stock(a,b,base):
        scale=np.maximum(np.maximum(abs(a),abs(b)),L('1e-12')*np.maximum(abs(base),L('1e-300')))
        return np.max(abs(a-b)/scale)
    b0=old.n2+old.d2;bc=coarse.n2+coarse.d2;bf=fine.n2+fine.d2
    atom_floor=L('1e-12')*max(old.n2,L('1e-300'))
    ground_floor=L('1e-12')*max(old.neutral-old.n2,L('1e-300'))
    vals=[l1(coarse.dt,fine.dt,old.dt),l1(coarse.dc,fine.dc,old.dc),
          stock(coarse.nt+coarse.dt,fine.nt+fine.dt,old.nt),
          stock(coarse.nc+coarse.dc,fine.nc+fine.dc,old.nc),
          scaled(bc,bf,atom_floor),
          scaled(old.neutral-bc,old.neutral-bf,ground_floor),
          scaled(coarse.d2-old.d2,fine.d2-old.d2,floor),
          scaled(c['cross'],f['cross'],floor),
          scaled(c['bath'],f['bath'],floor*transition),
          scaled(c['new_energy'],f['new_energy'],floor*transition)]
    return float(max(vals)/3)

def advance(net,sc,state,duration,initial_h,target,*,max_attempts=20000):
    if not all(math.isfinite(x) and x>0 for x in (duration,initial_h,target)) or target>=.1 or max_attempts<=0:
        raise ValueError("adaptive domain")
    initial=state.clone();s=state.clone();t=0.;h=min(duration,initial_h);accepted=reject=pos=attempts=0
    rows=[];ledger={k:L(0) for k in ('gross','bath','cross','new_energy','max_event_residual')}
    while t<duration:
        if attempts>=max_attempts:raise RuntimeError("adaptive attempts cap (transaction rolled back)")
        rem=duration-t;h=min(h,rem)
        if h<max(duration*1e-15,1e-300) and h!=rem:raise RuntimeError("adaptive minimum step")
        attempts+=1
        coarse=s.clone();fine=s.clone()
        try:
            c=coupled_step(net,sc,coarse,h)
            f=combine(coupled_step(net,sc,fine,h/2),coupled_step(net,sc,fine,h/2))
        except ValueError as exc:
            if not isinstance(exc,StepRejected) and str(exc) not in POS_ERRORS:raise
            pos+=1;reject+=1;h*=.5;continue
        err=estimate(s,coarse,fine,c,f,net.transition)
        if not math.isfinite(err):raise RuntimeError("nonfinite estimator")
        if err>target:
            reject+=1;h*=max(.2,min(.8,.8*(target/err)**(1/3)));continue
        # Do not clip or overwrite the input until complete.
        if np.min(fine.nt+fine.dt)<0 or np.min(fine.nc+fine.dc)<0 or not 0<=fine.n2+fine.d2<=fine.neutral:
            raise RuntimeError("accepted state outside physical domain")
        s=fine;accepted+=1;t=duration if h==rem else t+h
        ledger=combine(ledger,f)
        dn=s.dt-initial.dt;dc=s.dc-initial.dc;da=s.d2-initial.d2;gross=max(ledger['gross'],L('1e-300'))
        n=abs(np.sum(dn)+da)/gross
        e=abs(dn@net.et+dc@net.ec+net.transition*da+ledger['bath'])/(gross*net.transition)
        if max(n,e)>1e-11:raise RuntimeError("accepted path invariant defect")
        rows.append(dict(t=t,h=h,error=err,N=float(n),E=float(e)))
        h*=max(.5,min(2.,.9*(target/max(err,1e-300))**(1/3)))
    state.dt,state.dc,state.d2=s.dt,s.dc,s.d2
    return dict(end_s=t,accepted=accepted,rejected=reject,positivity_rejects=pos,attempts=attempts,
                ledger=ledger,rows=rows)
