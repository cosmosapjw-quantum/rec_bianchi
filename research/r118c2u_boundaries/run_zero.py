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
from zero_scatter import ZeroMPRK,PhysicalCoefficients
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
# Deliberately depleted actual graph; remove selected core nodes and exterior
# nodes. A separate actual positive-stock control uses identical graph.
y0=base.nt+base.dt;degree=np.bincount(np.r_[sc.i,sc.j],minlength=len(y0));candidates=np.flatnonzero(degree>0)
idx=np.unique(np.r_[candidates[np.linspace(0,len(candidates)-1,12,dtype=int)],np.flatnonzero(degree==0)[:4]])
y=y0.copy();y[idx]=0
method=ZeroMPRK(sc.i,sc.j,len(y));coef=PhysicalCoefficients(sc,base)
def rhs(t,v):
 s=np.asarray(v,dtype=L)*scale
 # DOP853 may evaluate slightly negative trial values near empty donors;
 # no clipping: choose positive initial perturbation for reference?
 # Direct point_values requires nonnegative. At exact empty stock the
 # derivative is inward; short reference steps use positive stages.
 p,m=coef(s[:nt]);f=p*s[:nt][sc.j]-m*s[:nt][sc.i]
 return np.asarray(np.r_[method.div(f),f@sc.de]/scale,float)
# Scale each node by a fixed positive numerical scale, not physical floor.
# Absolute vector DOP853 with component-wise atol and short max_step.
scale=max(y.max(),L(1))
rows=[];cases={}
for name,initial in [('positive',y0),('depleted',y)]:
 print('case',name,'zero',np.count_nonzero(initial==0),'max',float(initial.max()),flush=True)
 p,m=coef(initial);f=p*initial[sc.j]-m*initial[sc.i]
 print('max coeff',float(max(p.max(),m.max())),flush=True)
 # Independent direct-rate DOP853, track increments rather than absolute
 # state for small components. May fail at internal trial negativity.
 def direct(t,v):
    stock=initial+np.asarray(v[:nt],dtype=L)*scale
    ss=base.clone();ss.nt=stock.copy();ss.dt=np.zeros_like(stock)
    ff,gg=sc.rates(ss)
    return np.asarray(np.r_[method.div(ff),ff@sc.de]/scale,float)
 refs=[]
 for tol,ms in ((3e-10,.04),(3e-11,.02)):
    try:
      sol=solve_ivp(direct,(0,1.),np.zeros(nt+1),method='DOP853',rtol=tol,atol=tol*1e-5,max_step=ms)
      assert sol.success;refs.append(np.asarray(sol.y[:,-1],dtype=L)*scale);print('reference',tol,ms,sol.nfev,flush=True)
    except ValueError as ex:
      print('reference rejected',str(ex),flush=True);break
 for steps in (1,4,16,64):
    v=initial.copy();total=np.zeros(len(sc.i),dtype=L);gross=L(0)
    for i in range(steps):
      v,f,g=method.advance(v,1./steps,coef);total+=f;gross+=g
    delta=v-initial;en=total@sc.de
    err=None if len(refs)!=2 else float(np.sum(abs(delta-refs[-1][:-1]))/max(gross,L('1e-4900')))
    ndef=float(abs(delta.sum())/max(gross,L('1e-4900')));edef=float(abs(delta@net.et-en)/max(gross*net.transition,L('1e-4900')))
    row=dict(steps=steps,min_stock=float(v.min()),zeros=int(np.count_nonzero(v==0)),number_relative=ndef,energy_relative=edef,state_error=err,gross=float(gross),filled=int(np.count_nonzero(v[idx]>0)))
    assert np.min(v)>=0 and max(ndef,edef)<1e-7
    rows.append(row);print(name,row,flush=True)
 cases[name]=dict(initial_zeros=int(np.count_nonzero(initial==0)),depleted_nodes=idx.tolist() if name=='depleted' else [],reference_status='COMPLETE' if len(refs)==2 else 'REJECTED',reference_gap=None if len(refs)!=2 else float(np.sum(abs(refs[0]-refs[1]))),rows=rows[-4:])
 out=dict(status='SCOPED_ZERO_SAFE_MPRK',cases=cases,source_sha256=sha(cf),rates_sha256=sha(a.rates),graph_sha256=sha(gf),initial_state_sha256=sha(sf))
 a.out.write_text(json.dumps(out,indent=2,allow_nan=False)+'\n')
