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
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"r118c2v_stable_zero"))
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
nt,nc=len(base.nt),len(base.nc);scale=max(base.n2,L('1e-30'))
ii,jj,sg,rate,_=map(np.asarray,zip(*net.events));ii=ii.astype(int);jj=jj.astype(int);sg=sg.astype(L);rate=rate.astype(L)

assert a.bath=='z1100'
H=Path('/home/cosmosapjw/Downloads');D=Path(__file__).resolve().parent
states=json.loads((a.compiled/'STATES.json').read_text())['states']
anchor=states['z1100'];histpath=a.compiled/'z900_HISTORY.json';bh=ActualBath(json.loads(histpath.read_text())['states'],anchor)
r0=bh.point(anchor['z']);assert abs(r0['n1s']/q['n1s']-1)<1e-14
ends=[]
for name in ('end','mid'):
    p=H/('rec_r118c2w_'+name);r=json.loads((p/'RECEIPT.json').read_text())
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
assert a.duration==10.
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

# Same 16-partition actual trajectory, preserve midpoint and evolving stocks.
s=base.clone();rows=[];led=None
for i in range(16):
    l=step(s,i*10/16,10/16);led=l if led is None else merge(led,l)
    if i+1 in (4,8,12,16):
        t=(i+1)*10/16;st,n,sc1,dil=at(t,s)
        p=D/f'EVOLVING_{i+1}.npz';np.savez_compressed(p,nt=s.nt,dt=s.dt,nc=s.nc,dc=s.dc,n2=s.n2,d2=s.d2,neutral=s.neutral)
        row=dict(t=t,z=z_at(t),stock_sha=sha(p),n2=float(st.n2+st.d2),tracked=float((st.nt+st.dt).sum()))
        if i+1==8:
            # Independent compiled midpoint kernel on the evolved stock.
            f,g=sc1.rates(st);sc1.K=km;f0,g0=sc1.rates(st)
            diff=f-f0;den=np.sum(g0);dd=np.zeros(nt,dtype=L);np.add.at(dd,sc.i,diff);np.add.at(dd,sc.j,-diff)
            row.update(K_l1=float(np.sum(abs(mid-km))/np.sum(km)),net_l1_over_gross=float(np.sum(abs(diff))/den),divergence_over_gross=float(np.sum(abs(dd))/den),new_energy_relative=float(abs(diff[sc.new]@sc.de[sc.new])/max(abs(f0[sc.new]@sc.de[sc.new]),L('1e-4900'))))
        rows.append(row);print(row,flush=True)
old=np.load(D/'LONG.state_16.npz')
assert np.array_equal(old['dt'],s.dt) and np.array_equal(old['dc'],s.dc) and old['d2']==s.d2
(D/'EVOLVING.json').write_text(json.dumps(dict(status='SCOPED_ACTUAL_MIDPOINT_ACTION',rows=rows,mid_graph_sha=sha(pm/'GRAPH128.npz'),end_graph_sha=sha(p1/'GRAPH128.npz'),terminal_bitwise_equal=True,scope='actual 10s HMLA evolved stock; direct midpoint vs local anchor interpolation, not broad trajectory certificate'),indent=2)+'\n')
