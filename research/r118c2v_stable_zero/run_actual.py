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
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"r118c2s_evolving"))
from evolving import ActualBath,KernelHistory
from stable_zero import IncrementMPRK,PhysicalRates
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
y0=base.nt+base.dt;degree=np.bincount(np.r_[sc.i,sc.j],minlength=len(y0));cand=np.flatnonzero(degree>0)
idx=np.unique(np.r_[cand[np.linspace(0,len(cand)-1,12,dtype=int)],np.flatnonzero(degree==0)[:4]])
method=IncrementMPRK(sc.i,sc.j,len(y0));cases={}
for name in ('positive','depleted'):
 state=base.clone()
 if name=='depleted':
    state.nt=y0.copy();state.nt[idx]=0;state.dt=np.zeros_like(y0)
 initial=state.dt.copy();stock=state.nt.copy();rates=PhysicalRates(sc,state)
 scale=max((stock+initial).max(),L(1))
 def direct(t,v):
    ss=state.clone();ss.dt=initial+np.asarray(v[:nt],dtype=L)*scale
    ff,gg=sc.rates(ss)
    return np.asarray(np.r_[method.div(ff),ff@sc.de]/scale,float)
 refs=[]
 for tol,ms in ((3e-10,.04),(3e-11,.02)):
    sol=solve_ivp(direct,(0,1.),np.zeros(nt+1),method='DOP853',rtol=tol,atol=tol*1e-5,max_step=ms)
    assert sol.success;refs.append(np.asarray(sol.y[:,-1],dtype=L)*scale)
 rows=[]
 for steps in (1,4,16,64):
    d=initial.copy();total=np.zeros(len(sc.i),dtype=L);gross=L(0)
    for k in range(steps):
      d,f,g=method.advance(stock,d,1./steps,rates);total+=f;gross+=g
    dx=d-initial;E=total@sc.de
    row=dict(steps=steps,min_stock=float((stock+d).min()),zeros=int(np.count_nonzero(stock+d==0)),filled=int(np.count_nonzero((stock+d)[idx]>0)),N=float(abs(dx.sum())/gross),E=float(abs(dx@net.et-E)/(gross*net.transition)),error=float(np.sum(abs(dx-refs[-1][:-1]))/gross),gross=float(gross))
    assert min(stock+d)>=0 and max(row['N'],row['E'])<1e-11
    if name=='depleted':assert row['filled']==12 and row['zeros']==4
    rows.append(row);print(name,row,flush=True)
 cases[name]=dict(rows=rows,reference_gap=float(np.sum(abs(refs[0]-refs[1]))))
 out=dict(status='SCOPED_INCREMENT_ZERO_MPRK',cases=cases,source_sha256=sha(cf),rates_sha256=sha(a.rates),graph_sha256=sha(gf),initial_state_sha256=sha(sf))
 a.out.write_text(json.dumps(out,indent=2,allow_nan=False)+'\n')
