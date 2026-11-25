"""Transactional step doubling of C2N reaction + C2O scatter."""
import sys,math
from pathlib import Path
import numpy as np
from full_bianchi_hyrec.trajectory.atomic_dynamic_companion import L
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'r118c2n_exact_extent'))
sys.path.insert(0,str(ROOT/'r118c2m_adaptive_extent'))
from equilibrium_extent import coupled_step,ExtentRejected
from adaptive import estimate
ADDITIVE=('gross','bath','cross','new_energy','saturation','roundoff_fallbacks')
def merge(a,b):
    return {**{k:a[k]+b[k] for k in ADDITIVE},'max_root':max(a['max_root'],b['max_root'])}
def advance_bath(net,at,state,duration,initial_h,target,*,max_attempts=500):
    if not all(math.isfinite(x) and x>0 for x in (duration,initial_h,target)) or target>=.1 or max_attempts<=0:raise ValueError('adaptive domain')
    old=state.clone();s=state.clone();t=0.;h=min(duration,initial_h);attempts=reject=0;rows=[]
    ledger={**{k:L(0) for k in ADDITIVE},'max_root':0.}
    while t<duration:
        if attempts>=max_attempts:raise RuntimeError('adaptive attempts cap; rollback')
        rem=duration-t;h=min(h,rem)
        if h<max(1e-300,duration*1e-14) and h!=rem:raise RuntimeError('adaptive minimum h')
        attempts+=1;coarse=s.clone();fine=s.clone()
        try:
            n0,s0=at(t+h/2);n1,s1=at(t+h/4);n2,s2=at(t+3*h/4)
            c=coupled_step(n0,s0,coarse,h)
            f=merge(coupled_step(n1,s1,fine,h/2),coupled_step(n2,s2,fine,h/2))
        except ValueError as ex:
            if not isinstance(ex,ExtentRejected) and str(ex) not in ('Patankar numerical positivity','Patankar state positivity','Patankar linear residual'):raise
            reject+=1;h*=.5;continue
        er=estimate(s,coarse,fine,c,f,net.transition)
        if not math.isfinite(er):raise RuntimeError('nonfinite estimate')
        if er>target:
            reject+=1;h*=max(.2,min(.8,.8*(target/er)**(1/3)));continue
        if np.min(fine.nt+fine.dt)<0 or np.min(fine.nc+fine.dc)<0 or not 0<=fine.n2+fine.d2<=fine.neutral:raise RuntimeError('domain')
        s=fine;ledger=merge(ledger,f);t=duration if h==rem else t+h
        dn=s.dt-old.dt;dc=s.dc-old.dc;da=s.d2-old.d2;g=max(ledger['gross'],L('1e-300'))
        N=float(abs(np.sum(dn)+da)/g);E=float(abs(dn@net.et+dc@net.ec+net.transition*da+ledger['bath'])/(g*net.transition))
        if max(N,E)>1e-11:raise RuntimeError('ledger defect')
        rows.append(dict(t=t,h=h,error=er,N=N,E=E))
        h*=max(.5,min(2.,.9*(target/max(er,1e-300))**(1/3)))
    state.dt,state.dc,state.d2=s.dt,s.dc,s.d2
    return dict(accepted=len(rows),attempts=attempts,rejected=reject,ledger=ledger,rows=rows)
