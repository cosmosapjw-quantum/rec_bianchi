"""Re-use actual C2K frozen graphs and initial states, not recompiled surrogates."""
import argparse,hashlib,json,time
from pathlib import Path
import numpy as np
from scipy.integrate import solve_ivp
from full_bianchi_hyrec.standalone_line import prepare
from full_bianchi_hyrec.trajectory.atomic_refined_owner import RefinedTwoS,Scatter
from full_bianchi_hyrec.trajectory.atomic_dynamic_companion import State,L
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent.parent/"r118c2n_exact_extent"))
from extent_map import coupled_step, source_step, extent, ExtentRejected
from stable_extent import StableReaction
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"r118c2o_stiff_scatter"))
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"r118c2q_activity_bath"))
from patankar_scatter import PatankarScatter
from stable_activity import StableScatter
p=argparse.ArgumentParser()
p.add_argument('--raw',type=Path,required=True);p.add_argument('--compiled',type=Path,required=True)
p.add_argument('--rates',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
p.add_argument('--bath',choices=['z900','z1100','z1300'],required=True);p.add_argument('--n',type=int,default=128)
p.add_argument('--kind',choices=['pulse','actual','thermal'],default='pulse')
p.add_argument('--duration',type=float,default=1.);a=p.parse_args()
def sha(f):
    with open(f,'rb') as g:return hashlib.file_digest(g,'sha256').hexdigest()
raw=a.raw/a.bath;prior=json.loads((raw/'RESULTS.json').read_text())
cf=a.compiled/(a.bath+'.npz');assert sha(cf)==prior['source_sha256'];assert sha(a.rates)==prior['rate_sha256']
with np.load(cf) as z:q=prepare({k:z[k] for k in z.files},4)
net=RefinedTwoS(a.rates,q,a.n)
gf=raw/f'GRAPH{a.n}.npz'
with np.load(gf) as g:
    for k in ('et','gt','ec','gc'):assert np.array_equal(g[k],getattr(net,k)),k
    assert np.array_equal(g['events'],np.array(net.events,dtype=L))
    edges=list(zip(g['i'],g['j'],g['K'],g['cross'],g['new']))
sc=Scatter(net,edges)
sf=raw/f'n{a.n}_{a.kind}_{2 if a.kind=="thermal" else 4}.npz'
row=next(x for x in prior['cases'] if x['case']==sf.stem)
assert sha(sf)==row['state_sha256']
with np.load(sf) as v:
    base=State(v['nt'],v['nc'],L(v['n2']),L(v['neutral']),v['initial_dt'].copy(),v['initial_dc'].copy(),L(v['initial_d2']))
nt,nc=len(base.nt),len(base.nc);scale=max(base.n2,L('1e-30'))
ii,jj,sg,rate,_=map(np.asarray,zip(*net.events));ii=ii.astype(int);jj=jj.astype(int);sg=sg.astype(L);rate=rate.astype(L)
def fun(t,y):
    v=np.asarray(y,dtype=L)*scale;s=base.clone()
    s.dt+=v[:nt];s.dc+=v[nt:nt+nc];s.d2+=v[-4]
    f=net.point_values(s);fc=(s.nc+s.dc)/net.gc;b=s.n2+s.d2
    F=rate*(b*(1+f[ii])*(fc[jj]+(sg==1))-(s.neutral-b)*f[ii]*(fc[jj]+(sg==-1)))
    d,flux,g=sc.rhs(s);np.add.at(d,ii,F);c=np.zeros(nc,dtype=L);np.add.at(c,jj,sg*F)
    E=flux@sc.de
    return np.asarray(np.r_[d,c,-np.sum(F),np.sum(flux[sc.cross]),flux[sc.new]@sc.de[sc.new],-E]/scale,float)
def independent(rtol,atol):
    sol=solve_ivp(fun,(0,a.duration),np.zeros(nt+nc+4),method='DOP853',rtol=rtol,atol=atol)
    assert sol.success,sol.message
    return np.asarray(sol.y[:,-1],dtype=L)*scale,sol.nfev

import mpmath as mp
mp.mp.dps=65
def mpv(x):return mp.mpf(np.format_float_scientific(L(x),precision=35,unique=False))
sn=StableReaction(net,base);ps=PatankarScatter(StableScatter(sc,base))
anchor=base.clone();anchor.dt[:]=0;anchor.dc[:]=0;anchor.d2=L(0)
tiny=anchor.clone();tiny.dt=tiny.nt*L('1e-23');tiny.dc=-tiny.nc*L('2e-23');tiny.d2=tiny.n2*L('3e-23')
checks=[]
for event_id in np.unique(np.linspace(0,len(net.events)-1,18,dtype=int)):
    event=net.events[event_id];i,j,sg,r,_=event
    b=mpv(anchor.n2);nn=mpv(anchor.neutral)-b;db=mpv(tiny.d2)
    fc=mpv(anchor.nc[j])/mpv(net.gc[j]);dc=mpv(tiny.dc[j])/mpv(net.gc[j])
    f0=mpv(anchor.nt[i])/mpv(net.gt[i]);df0=mpv(tiny.dt[i])/mpv(net.gt[i])
    if i<net.ncore:
        w=list(map(mpv,net.w[i]));z=list(map(mpv,net.z[i]));zi=mpv(net.zi[i])
        def invert_activity(a):return sum(ww*a*zz/(1-a*zz) for ww,zz in zip(w,z))
        a0=mp.findroot(lambda a:invert_activity(a)-f0,mpv(sn.a0[i]),tol=mp.mpf('1e-60'))
        a1=mp.findroot(lambda a:invert_activity(a)-(f0+df0),a0,tol=mp.mpf('1e-60'))
        ft=a0*zi/(1-a0*zi);dft=a1*zi/(1-a1*zi)-ft
    else:ft=f0;dft=df0
    r0=mpv(r)
    def flux(b,nn,ft,fc):return r0*(b*(1+ft)*(fc+(sg==1)) - nn*ft*(fc+(sg==-1)))
    want=flux(b+db,nn-db,ft+dft,fc+dc)-flux(b,nn,ft,fc)
    actual=sn.parts(tiny,event)[1]
    er=float(abs(mpv(actual)/want-1));assert er<1e-11,(event_id,er)
    checks.append(dict(event=int(event_id),kind=int(sg),relative=er))
print('tiny event increment',len(checks),max(v['relative'] for v in checks),flush=True)
ref,nfev=independent(3e-12,2e-14);ref2,nfev2=independent(3e-13,2e-15)
out=dict(status='SCOPED_RUNNING',bath=a.bath,kind=a.kind,source_sha256=sha(cf),rates_sha256=sha(a.rates),graph_sha256=sha(gf),initial_state_sha256=sha(sf),tiny_checks=checks,reference_nfev=[nfev,nfev2],reference_gap=float(np.max(abs(ref-ref2))),rows=[],stiff=[])
def save():a.out.write_text(json.dumps(out,indent=2,allow_nan=False)+'\n')
save()
for h in (10.,100.):
    s=base.clone();t=time.monotonic()
    try:
        v=source_step(sn,s,h);g=v['gross'];dn=s.dt-base.dt;dc=s.dc-base.dc;da=s.d2-base.d2
        N=float(abs(dn.sum()+da)/g);E=float(abs(dn@net.et+dc@net.ec+net.transition*da)/(g*net.transition))
        assert max(N,E)<1e-11
        r=dict(h=h,status='PASS',N=N,E=E,roundoff_fallbacks=v['roundoff_fallbacks'],max_root=v['max_root'],seconds=time.monotonic()-t)
    except ValueError as e:r=dict(h=h,status='REJECTED',error=str(e))
    out['stiff'].append(r);print('source only',r,flush=True);save()
for steps in (1,4,16):
    s=base.clone();t=time.monotonic();g=b=c0=ne=L(0);fallback=0
    try:
        for _ in range(steps):
            v=coupled_step(sn,ps,s,a.duration/steps);g+=v['gross'];b+=v['bath'];c0+=v['cross'];ne+=v['new_energy'];fallback+=v['roundoff_fallbacks']
        dn=s.dt-base.dt;dc=s.dc-base.dc;da=s.d2-base.d2
        d=np.r_[dn,dc,da,c0,ne,b]-ref2
        N=float(abs(dn.sum()+da)/g);E=float(abs(dn@net.et+dc@net.ec+net.transition*da+b)/(g*net.transition))
        assert max(N,E)<1e-11
        r=dict(steps=steps,status='PASS',N=N,E=E,roundoff_fallbacks=fallback,error=float((np.sum(abs(d[:nt+nc]))+abs(d[-4]))/g),seconds=time.monotonic()-t)
    except ValueError as e:r=dict(steps=steps,status='REJECTED',error=str(e))
    out['rows'].append(r);print('coupled',r,flush=True);save()
out['status']='SCOPED_COMPLETE';save()
