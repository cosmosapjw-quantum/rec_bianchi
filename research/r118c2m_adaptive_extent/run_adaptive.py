"""Re-use actual C2K frozen graphs and initial states, not recompiled surrogates."""
import argparse,hashlib,json,time
from pathlib import Path
import numpy as np
from scipy.integrate import solve_ivp
from full_bianchi_hyrec.standalone_line import prepare
from full_bianchi_hyrec.trajectory.atomic_refined_owner import RefinedTwoS,Scatter
from full_bianchi_hyrec.trajectory.atomic_dynamic_companion import State,L
from adaptive import advance
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
ref,nfev=independent(3e-12,2e-14);ref2,nfev2=independent(3e-13,2e-15)

rows=[]
for target in (1e-3,1e-4,1e-5):
    state=base.clone();t=time.monotonic()
    r=advance(net,sc,state,a.duration,a.duration,target)
    l=r['ledger'];dn=state.dt-base.dt;dc=state.dc-base.dc;da=state.d2-base.d2
    y=np.r_[dn,dc,da,l['cross'],l['new_energy'],l['bath']]
    d=y-ref2
    rec=dict(target=target,accepted=r['accepted'],rejected=r['rejected'],positivity_rejects=r['positivity_rejects'],
         max_error=max(q['error'] for q in r['rows']),max_N=max(q['N'] for q in r['rows']),max_E=max(q['E'] for q in r['rows']),
         delta_n2_rel=float(abs(d[-4])/max(abs(ref2[-4]),L('1e-30'))),
         delta_n2_abs=float(abs(d[-4])),state_l1_over_gross=float((np.sum(abs(d[:nt+nc]))+abs(d[-4]))/max(l['gross'],L('1e-300'))),
         cross_abs=float(abs(d[-3])),bath_abs=float(abs(d[-1])),wall_s=time.monotonic()-t,rows=r['rows'])
    assert rec['max_error']<=target and max(rec['max_N'],rec['max_E'])<1e-11
    print(a.bath,a.kind,a.duration,{k:v for k,v in rec.items() if k!='rows'},flush=True);rows.append(rec)
out=dict(bath=a.bath,kind=a.kind,n=a.n,physical_duration_s=a.duration,source_sha256=sha(cf),rates_sha256=sha(a.rates),graph_sha256=sha(gf),initial_state_sha256=sha(sf),reference_nfev=[nfev,nfev2],reference_delta_n2=float(ref2[-4]),reference_state_max_diff=float(np.max(abs(ref-ref2))),rows=rows)
a.out.write_text(json.dumps(out,indent=2,allow_nan=False)+'\n')
