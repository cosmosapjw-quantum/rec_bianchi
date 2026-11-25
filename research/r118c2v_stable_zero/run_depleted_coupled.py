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
from reaction_boundary import BoundaryReaction as StableReaction
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"r118c2o_stiff_scatter"))
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"r118c2q_activity_bath"))
from patankar_scatter import PatankarScatter
from stable_activity import StableScatter,bath_at
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"r118c2s_evolving"))
from evolving import ActualBath,KernelHistory
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"r118c2u_boundaries"))
from boundary import JoinedDrift
from stable_zero import IncrementScatter
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
degree=np.bincount(np.r_[sc.i,sc.j],minlength=len(base.nt));cand=np.flatnonzero(degree>0)
idx=np.unique(np.r_[cand[np.linspace(0,len(cand)-1,12,dtype=int)],np.flatnonzero(degree==0)[:4]])
base.nt=base.nt+base.dt;base.nt[idx]=0;base.dt=np.zeros_like(base.nt)
print("depleted initial nodes",idx.tolist(),flush=True)
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

assert a.clock=='physical'
# Integrate u directly, avoid subtracting nearly equal scale factors.
usol=solve_ivp(lambda t,v:[bh.splines['H_s']((1+z0)*np.exp(-v[0])-1)],(0,a.duration),[0.],rtol=1e-12,atol=1e-27,dense_output=True)
assert usol.success
def u(t):return L(usol.sol(t)[0])
def z_at(t):return float((1+L(z0))*np.exp(-u(t))-1)
drift=JoinedDrift(net.et,net.gt,net.ec,net.gc)
def at(t,s):
    v=bh.point(z_at(t));dil=np.exp(-3*u(t))
    stage=s.clone();stage.nt=s.nt*dil;stage.nc=s.nc*dil;stage.dt=s.dt*dil;stage.dc=s.dc*dil;stage.d2=s.d2*dil
    stage.n2=base.n2*L(v['n2']/r0['n2']);stage.neutral=base.neutral*L((v['n1s']+v['n2'])/(r0['n1s']+r0['n2']))
    n,scatter=bath_at(net,sc,stage,v['T_m_K'])
    n.q['n1s']=v['n1s'];scatter.K=K(beta(v['T_m_K']),v['n1s'])
    return stage,n,scatter,dil
def gmap(s,ta,tb):
    ua,ub=u(ta),u(tb)
    delta,l=drift.affine(np.r_[s.nt,s.nc],np.r_[s.dt,s.dc],ub-ua,drift.planck_influx((ua+ub)/2,z0))
    s.dt=delta[:nt].copy();s.dc=delta[nt:].copy()
    return l
def step(s,t,h):
    a=gmap(s,t,t+h/2)
    stage,n,scatter,dil=at(t+h/2,s)
    before=stage.clone();rr=coupled_step(StableReaction(n,stage),IncrementScatter(scatter,stage),stage,h)
    s.dt+=(stage.dt-before.dt)/dil;s.dc+=(stage.dc-before.dc)/dil;s.d2+=(stage.d2-before.d2)/dil
    b=gmap(s,t+h/2,t+h)
    for k in ('gross','bath','cross','new_energy'):rr[k]/=dil
    return {**rr,**{k:a[k]+b[k] for k in a}}
def merge(a,b):return {k:(max(a[k],b[k]) if k=='max_root' else a[k]+b[k]) for k in a}
def fun(t,y):
    v=np.asarray(y,dtype=L)*scale;s=base.clone();s.dt+=v[:nt];s.dc+=v[nt:nt+nc];s.d2+=v[-10]
    st,n,scatter,dil=at(t,s)
    f=n.point_values(st);fc=(st.nc+st.dc)/n.gc;b=st.n2+st.d2
    F=rate*(b*(1+f[ii])*(fc[jj]+(sg==1))-(st.neutral-b)*f[ii]*(fc[jj]+(sg==-1)))
    d,flux,g=scatter.rhs(st);np.add.at(d,ii,F);c=np.zeros(nc,dtype=L);np.add.at(c,jj,sg*F);en=flux@scatter.de
    H=L(bh.splines['H_s'](z_at(t)));ff=H*drift.rate*np.r_[s.nt+s.dt,s.nc+s.dc];inj=H*drift.planck_influx(u(t),z0)
    dx=drift.divergence(ff);dx[drift.top]+=inj*drift.topw;esc=ff[drift.escape].sum()
    return np.asarray(np.r_[d/dil+dx[:nt],c/dil+dx[nt:],-np.sum(F)/dil,np.sum(flux[scatter.cross])/dil,flux[scatter.new]@scatter.de[scatter.new]/dil,-en/dil,esc,esc*drift.ghost,ff@drift.de,inj,inj*drift.e.max(),ff@drift.cross_weight]/scale,float)
refs=[]
for tol in (3e-10,3e-11):
    sol=solve_ivp(fun,(0,a.duration),np.zeros(nt+nc+10),method='DOP853',rtol=tol,atol=tol/100)
    assert sol.success
    refs.append((np.asarray(sol.y[:,-1],dtype=L)*scale,sol.nfev))
    print('reference',tol,sol.nfev,flush=True)
ref=refs[-1][0];rows=[];out=dict(status='SCOPED_RUNNING',duration=a.duration,depleted_nodes=idx.tolist(),du=float(u(a.duration)),z_end=z_at(a.duration),history_sha=sha(histpath),source_sha256=sha(cf),rates_sha256=sha(a.rates),graph_sha256=sha(gf),initial_state_sha256=sha(sf),local_graphs={name:dict(path=str(p),receipt_sha=sha(p/'RECEIPT.json'),hashes=r['hashes']) for name,(p,r,g) in zip(('end','mid'),ends)},reference_gap=float(np.max(abs(refs[0][0]-ref))),reference_nfev=[v[1] for v in refs],rows=rows)
def save():a.out.write_text(json.dumps(out,indent=2,allow_nan=False)+'\n')
save()
for steps in (1,4,16):
    s=base.clone();ledger=None;t0=time.monotonic()
    for k in range(steps):
        v=step(s,k*a.duration/steps,a.duration/steps)
        ledger=v if ledger is None else merge(ledger,v)
    dn=s.dt-base.dt;dc=s.dc-base.dc;da=s.d2-base.d2
    d=np.r_[dn,dc,da,ledger['cross'],ledger['new_energy'],ledger['bath'],ledger['escape_N'],ledger['escape_U'],ledger['work'],ledger['in_N'],ledger['in_U'],ledger['cross_N']]-ref
    N=abs(dn.sum()+da+ledger['cross_N']-ledger['in_N']);En=abs(dn@net.et+dc@net.ec+net.transition*da+ledger['bath']+ledger['escape_U']+ledger['work']-ledger['in_U'])
    Ng=max(ledger['gross']+ledger['cross_N']+ledger['in_N'],L('1e-300'));Eg=max(ledger['gross']*net.transition+ledger['escape_U']+ledger['work']+ledger['in_U'],L('1e-300'))
    row=dict(steps=steps,N=float(N/Ng),E=float(En/Eg),tracked_error=float(np.sum(abs(d[:nt]))/max(np.sum(abs(ref[:nt])),L('1e-300'))),companion_error=float(np.sum(abs(d[nt:nt+nc]))/max(np.sum(abs(ref[nt:nt+nc])),L('1e-300'))),atomic_abs_error=float(abs(d[-10])),atomic_response=float(da),gross=float(ledger['gross']),cross_N=float(ledger['cross_N']),escape_N=float(ledger['escape_N']),in_N=float(ledger['in_N']),work=float(ledger['work']),fallbacks=ledger['roundoff_fallbacks'],seconds=time.monotonic()-t0)
    assert np.min(s.nt+s.dt)>=0 and np.min(s.nc+s.dc)>=0 and max(row['N'],row['E'])<1e-11
    rows.append(row);print('coupled',row,flush=True);save()
out['status']='COMPLETE_SCOPED_STABLE_ZERO_COUPLED';save()
