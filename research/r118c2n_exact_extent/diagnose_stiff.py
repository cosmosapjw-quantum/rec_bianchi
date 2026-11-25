"""Re-use actual C2K frozen graphs and initial states, not recompiled surrogates."""
import argparse,hashlib,json,time
from pathlib import Path
import numpy as np
from scipy.integrate import solve_ivp
from full_bianchi_hyrec.standalone_line import prepare
from full_bianchi_hyrec.trajectory.atomic_refined_owner import RefinedTwoS,Scatter
from full_bianchi_hyrec.trajectory.atomic_dynamic_companion import State,L
from equilibrium_extent_v1 import coupled_step, source_step, extent, ExtentRejected
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

trace=[]
orig=net.rates
def traced(s,event,d=L(0)):
    a,b=orig(s,event,d);trace.append([str(d),str(a),str(b),str(a-b)])
    return a,b
net.rates=traced
s=base.clone()
for seqno,seq in enumerate((net.events,reversed(net.events))):
    for event in seq:
        trace=[]
        try:
            d,r=extent(net,s,event,50.)
        except ExtentRejected as ex:
            i,j,sg,_,idx=event
            print(json.dumps(dict(error=str(ex),sweep=seqno,event=[str(v) for v in event],atom=str(s.n2+s.d2),tracked=str(s.nt[i]+s.dt[i]),companion=str(s.nc[j]+s.dc[j]),trace=trace),indent=2),flush=True)
            raise SystemExit(0)
        i,j,sg,_,_=event;s.dt[i]+=d;s.dc[j]+=sg*d;s.d2-=d
raise RuntimeError('expected rejection absent')
