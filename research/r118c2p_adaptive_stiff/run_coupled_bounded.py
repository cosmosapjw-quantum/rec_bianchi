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
from equilibrium_extent import coupled_step, source_step, extent, ExtentRejected
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"r118c2o_stiff_scatter"))
from patankar_scatter import PatankarScatter
from adaptive_stiff import advance
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


ps=PatankarScatter(sc)
ref,nfev=independent(3e-12,2e-14);ref2,nfev2=independent(3e-13,2e-15)
print('coupled reference',nfev,nfev2,float(np.max(abs(ref-ref2))),flush=True)
rows=[]
for target in (1e-2,3e-3):
    s=base.clone();t=time.monotonic()
    r=advance(net,ps,s,a.duration,a.duration,target,max_attempts=100)
    v=r['ledger'];d=np.r_[s.dt-base.dt,s.dc-base.dc,s.d2-base.d2,v['cross'],v['new_energy'],v['bath']]-ref2
    row=dict(target=target,accepted=r['accepted'],attempts=r['attempts'],rejected=r['rejected'],max_N=max(x['N'] for x in r['rows']),max_E=max(x['E'] for x in r['rows']),max_local=max(x['error'] for x in r['rows']),state_l1_over_gross=float((np.sum(abs(d[:nt+nc]))+abs(d[-4]))/v['gross']),delta_n2_abs=float(abs(d[-4])),delta_n2_rel=float(abs(d[-4])/max(abs(ref2[-4]),L('1e-30'))),seconds=time.monotonic()-t,rows=r['rows'])
    rows.append(row);print('adaptive',{k:v for k,v in row.items() if k!='rows'},flush=True)
    a.out.write_text(json.dumps(dict(status='COUPLED_SCOPED',bath=a.bath,kind=a.kind,source_sha256=sha(cf),rates_sha256=sha(a.rates),graph_sha256=sha(gf),initial_state_sha256=sha(sf),duration=a.duration,reference_nfev=[nfev,nfev2],reference_max_abs_gap=float(np.max(abs(ref-ref2))),rows=rows),indent=2,allow_nan=False)+'\n')
