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
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"r118c2r_stable_extent"))
from extent_map import coupled_step, source_step, extent, ExtentRejected
from stable_extent import StableReaction
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"r118c2o_stiff_scatter"))
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"r118c2q_activity_bath"))
from patankar_scatter import PatankarScatter
from stable_activity import StableScatter,bath_at
from evolving import ActualBath,KernelHistory
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"r118c2m_adaptive_extent"))
from adaptive import estimate
p=argparse.ArgumentParser()
p.add_argument('--raw',type=Path,required=True);p.add_argument('--compiled',type=Path,required=True)
p.add_argument('--rates',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
p.add_argument('--bath',choices=['z900','z1100','z1300'],required=True);p.add_argument('--n',type=int,default=128)
p.add_argument('--kind',choices=['pulse','actual','thermal'],default='pulse')
p.add_argument('--duration',type=float,default=1.);p.add_argument('--clock',choices=['physical','accelerated'],required=True);a=p.parse_args()
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

assert a.bath=='z1100'
H=Path('/home/cosmosapjw/Downloads');D=Path(__file__).resolve().parent
states=json.loads((a.compiled/'STATES.json').read_text())['states']
anchor=states['z1100'];histpath=a.compiled/'z900_HISTORY.json';bh=ActualBath(json.loads(histpath.read_text())['states'],anchor)
r0=bh.point(anchor['z']);assert abs(r0['n1s']/q['n1s']-1)<1e-14
ends=[]
for name in ('end','mid'):
    p=H/('rec_r118c2s_'+name);r=json.loads((p/'RECEIPT.json').read_text())
    assert r['status']=='COMPILED_SAME_GRAPH' and r['history_sha']==sha(histpath) and r['rate_sha']==sha(a.rates)
    for f,h in r['hashes'].items():assert sha(p/f)==h
    g=np.load(p/'GRAPH128.npz')
    assert np.array_equal(g['i'],sc.i) and np.array_equal(g['j'],sc.j)
    ends.append((p,r,g['K']))
p1,rr1,k1=ends[0];pm,rrm,km=ends[1]
def beta(T):return -1/L(T)
K=KernelHistory([beta(rr1['bath']['T_m_K']),beta(anchor['T_m_K'])],[rr1['bath']['n1s'],q['n1s']],np.stack([k1,sc.K]))
mid=K(beta(rrm['bath']['T_m_K']),rrm['bath']['n1s'])
interp=dict(max_edge_rel=float(np.max(abs(mid/km-1))),global_l1=float(np.sum(abs(mid-km))/np.sum(km)),cross_l1=float(np.sum(abs(mid[sc.cross]-km[sc.cross]))/np.sum(km[sc.cross])),new_l1=float(np.sum(abs(mid[sc.new]-km[sc.new]))/np.sum(km[sc.new])))
assert interp['global_l1']<1e-5 and interp['new_l1']<1e-5
print('full local graph midpoint',interp,flush=True)
z0=anchor['z']
clock=bh.clock(a.duration) if a.clock=='physical' else lambda t:z0-.1*t/a.duration
def at(t,s):
    v=bh.point(clock(t))
    trial=s.clone();trial.n2=base.n2*L(v['n2']/r0['n2']);trial.neutral=base.neutral*L((v['n1s']+v['n2'])/(r0['n1s']+r0['n2']))
    n,scatter=bath_at(net,sc,trial,v['T_m_K'])
    n.q['n1s']=v['n1s'];scatter.K=K(beta(v['T_m_K']),v['n1s'])
    return trial,n,scatter
def step(s,t,h):
    stage,n,scatter=at(t+h/2,s)
    rr=coupled_step(StableReaction(n,stage),PatankarScatter(scatter),stage,h)
    s.dt,s.dc,s.d2=stage.dt,stage.dc,stage.d2
    return rr
def merge(a,b):
    return {k:(max(a[k],b[k]) if k=='max_root' else a[k]+b[k]) for k in a}
def adaptive(target):
    s=base.clone();t=0.;h=a.duration;rows=[];ledger=None;rejected=0;attempts=0
    while t<a.duration:
        attempts+=1
        if attempts>100:raise RuntimeError('adaptive cap')
        rem=a.duration-t;h=min(h,rem);c=s.clone();f=s.clone()
        try:
            c0=step(c,t,h);f0=merge(step(f,t,h/2),step(f,t+h/2,h/2))
        except ExtentRejected:
            rejected+=1;h*=.5;continue
        # Compare atomic TOTAL stocks at the same endpoint background, not midpoint.
        old,_,_=at(t,s);ca,_,_=at(t+h,c);fa,_,_=at(t+h,f)
        # estimate() uses old neutral; use endpoint background for both candidates and old comparison.
        old.n2=ca.n2;old.neutral=ca.neutral
        er=estimate(old,ca,fa,c0,f0,net.transition)
        if er>target:
            rejected+=1;h*=max(.2,min(.8,.8*(target/er)**(1/3)));continue
        if np.min(fa.nt+fa.dt)<=0 or np.min(fa.nc+fa.dc)<0 or not 0<=fa.n2+fa.d2<=fa.neutral:raise RuntimeError('state domain')
        s=f;t=a.duration if h==rem else t+h;ledger=f0 if ledger is None else merge(ledger,f0)
        dn=s.dt-base.dt;dc=s.dc-base.dc;da=s.d2-base.d2;g=ledger['gross']
        N=float(abs(dn.sum()+da)/g);E=float(abs(dn@net.et+dc@net.ec+net.transition*da+ledger['bath'])/(g*net.transition))
        assert max(N,E)<1e-11
        rows.append(dict(t=t,h=h,error=er,N=N,E=E));h*=max(.5,min(2.,.9*(target/max(er,1e-300))**(1/3)))
    return s,ledger,rows,rejected
def fun(t,y):
    v=np.asarray(y,dtype=L)*scale;s=base.clone();s.dt+=v[:nt];s.dc+=v[nt:nt+nc];s.d2+=v[-4]
    st,n,scatter=at(t,s)
    # Independent direct product ODE on the same externally prescribed background.
    f=n.point_values(st);fc=(st.nc+st.dc)/n.gc;b=st.n2+st.d2
    F=rate*(b*(1+f[ii])*(fc[jj]+(sg==1))-(st.neutral-b)*f[ii]*(fc[jj]+(sg==-1)))
    d,flux,g=scatter.rhs(st);np.add.at(d,ii,F);c=np.zeros(nc,dtype=L);np.add.at(c,jj,sg*F);En=flux@scatter.de
    return np.asarray(np.r_[d,c,-np.sum(F),np.sum(flux[scatter.cross]),flux[scatter.new]@scatter.de[scatter.new],-En]/scale,float)
refs=[]
for tol in (3e-11,3e-12):
    sol=solve_ivp(fun,(0,a.duration),np.zeros(nt+nc+4),method='DOP853',rtol=tol,atol=tol/100)
    assert sol.success
    refs.append((np.asarray(sol.y[:,-1],dtype=L)*scale,sol.nfev))
ref=refs[-1][0];rows=[];out=dict(status='SCOPED_RUNNING',clock=a.clock,duration=a.duration,initial_z=z0,final_z=clock(a.duration),initial_bath=r0,final_bath=bh.point(clock(a.duration)),interpolation=interp,history_sha=sha(histpath),source_sha256=sha(cf),rates_sha256=sha(a.rates),graph_sha256=sha(gf),initial_state_sha256=sha(sf),local_graphs={name:dict(path=str(p),receipt_sha=sha(p/'RECEIPT.json'),hashes=r['hashes']) for name,(p,r,g) in zip(('end','mid'),ends)},reference_gap=float(np.max(abs(refs[0][0]-ref))),reference_nfev=[v[1] for v in refs],rows=rows)
def save():a.out.write_text(json.dumps(out,indent=2,allow_nan=False)+'\n')
save()
for target in (1e-2,3e-3):
    t0=time.monotonic();s,g,r,reject=adaptive(target)
    d=np.r_[s.dt-base.dt,s.dc-base.dc,s.d2-base.d2,g['cross'],g['new_energy'],g['bath']]-ref
    row=dict(target=target,accepted=len(r),rejected=reject,max_local=max(x['error'] for x in r),max_N=max(x['N'] for x in r),max_E=max(x['E'] for x in r),error=float((np.sum(abs(d[:nt+nc]))+abs(d[-4]))/g['gross']),fallbacks=g['roundoff_fallbacks'],seconds=time.monotonic()-t0,steps=r)
    rows.append(row);print(a.clock,{k:v for k,v in row.items() if k!='steps'},flush=True);save()
out['status']='COMPLETE_PRESCRIBED_EVOLVING_GRAPH';save()
