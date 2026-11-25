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

from scipy.sparse import coo_matrix
ps=PatankarScatter(sc)
# independent nonlinear scattering-only RHS and analytic Jacobian of actual activity inversion
i,j=sc.i,sc.j;n=nt;stock=base.nt+base.dt
horizon=10000.
initial=sc.rhs(base)[0]
scale_s=np.maximum(abs(initial)*L(horizon),np.maximum(stock*L('1e-13'),L('1e-40')))
def decode(y):
    s=base.clone();s.dt+=np.asarray(y,dtype=L)*scale_s
    return s
def srhs(t,y):
    return np.asarray(sc.rhs(decode(y))[0]*L(horizon)/scale_s,float)
def sjac(t,y):
    s=decode(y);f=net.point_values(s);k=sc.K*(s.neutral-s.n2-s.d2)/L(net.q['n1s'])
    df=1/net.gt.copy()
    a=f[:net.ncore]/(net.zi*(1+f[:net.ncore]))
    den=np.sum(net._w*net._z/(1-a[:,None]*net._z)**2,axis=1)
    df[:net.ncore]=net.zi/((1-a*net.zi)**2*den*net.gt[:net.ncore])
    fi=k*(f[j]/sc.z[j]-(1+f[j])/sc.z[i])*df[i]
    fj=k*((1+f[i])/sc.z[j]-f[i]/sc.z[i])*df[j]
    # coordinate-scaled matrix; duplicate diagonals are summed by CSC conversion
    data=np.asarray(L(horizon)*np.r_[fi,fj*scale_s[j]/scale_s[i],-fi*scale_s[i]/scale_s[j],-fj],float)
    return coo_matrix((data,(np.r_[i,i,j,j],np.r_[i,j,i,j])),shape=(n,n)).tocsc()
# Test directional Jacobian on a perturbation large enough to exceed finite precision
# but small in absolute photon stock. Directional derivative normalized by response.
rng=np.random.default_rng(118);v=rng.normal(size=n);v/=np.max(abs(v))
# use physical stock scale for finite-difference direction
v=np.asarray(v*stock/scale_s,float);v/=np.max(abs(v))
J=sjac(0,np.zeros(n));exact=J@v
gaps=[]
for ep in (1e-2,1e-3,1e-4):
    fd=(srhs(0,ep*v)-srhs(0,-ep*v))/(2*ep)
    gaps.append(float(np.linalg.norm(fd-exact)/max(np.linalg.norm(exact),1e-300)))
print('jacobian gaps',gaps,flush=True)
assert min(gaps)<2e-3
refs={}
for method,tol in [('BDF',2e-8),('Radau',2e-9)]:
    start=time.monotonic()
    sol=solve_ivp(srhs,(0,1),np.zeros(n),method=method,jac=sjac,rtol=tol,atol=tol*1e-3)
    assert sol.success,sol.message
    x=np.asarray(sol.y[:,-1],dtype=L)*scale_s
    assert np.min(stock+x)>0
    refs[method]=(x,dict(nfev=sol.nfev,njev=sol.njev,nlu=sol.nlu,seconds=time.monotonic()-start,net_energy=float(x@net.et),number_defect=float(abs(x.sum()))))
    print('reference',method,refs[method][1],flush=True)
x=refs['Radau'][0];den=max(np.sum(abs(x)),L('1e-40'))
refgap=float(np.sum(abs(refs['BDF'][0]-x))/den)
rows=[]
for steps in (1,4,16,64,128):
    s=base.clone();t=time.monotonic();gross=L(0);bath=L(0)
    try:
        for _ in range(steps):
            r=ps.step(s,horizon/steps);gross+=r['gross'];bath+=r['bath_energy_eV_m3']
    except ValueError as e:
        rows.append(dict(steps=steps,status='REJECTED',error=str(e)));continue
    d=s.dt-base.dt
    assert np.min(s.nt+s.dt)>0 and max(abs(d.sum()),abs(d@net.et+bath)/net.transition)/gross<1e-11
    row=dict(steps=steps,status='PASS_POSITIVE_CONSERVATIVE',response_l1_relative=float(np.sum(abs(d-x))/den),energy_abs_error=float(abs((d-x)@net.et)),net_energy=float(d@net.et),seconds=time.monotonic()-t)
    rows.append(row);print('long scatter',row,flush=True)
# independent coupled reference and adaptive combined integration on 10s interval
ref,nfev=independent(3e-12,2e-14);ref2,nfev2=independent(3e-13,2e-15)
adaptive=[]
for target in (1e-2,3e-3,1e-3):
    s=base.clone();t=time.monotonic()
    try:r=advance(net,ps,s,a.duration,a.duration,target,max_attempts=300)
    except (RuntimeError,ValueError) as ex:
        adaptive.append(dict(target=target,status='REJECTED',error=str(ex)));print('adaptive reject',target,str(ex),flush=True);continue
    v=r['ledger'];d=np.r_[s.dt-base.dt,s.dc-base.dc,s.d2-base.d2,v['cross'],v['new_energy'],v['bath']]-ref2
    row=dict(target=target,status='COMPLETE',accepted=r['accepted'],attempts=r['attempts'],rejected=r['rejected'],max_N=max(x['N'] for x in r['rows']),max_E=max(x['E'] for x in r['rows']),max_local=max(x['error'] for x in r['rows']),state_l1_over_gross=float((np.sum(abs(d[:nt+nc]))+abs(d[-4]))/v['gross']),delta_n2_abs=float(abs(d[-4])),delta_n2_rel=float(abs(d[-4])/max(abs(ref2[-4]),L('1e-30'))),seconds=time.monotonic()-t,rows=r['rows'])
    adaptive.append(row);print('adaptive', {k:v for k,v in row.items() if k!='rows'},flush=True)
out=dict(status='SCOPED_EXECUTION',bath=a.bath,kind=a.kind,source_sha256=sha(cf),rates_sha256=sha(a.rates),graph_sha256=sha(gf),initial_state_sha256=sha(sf),jacobian_gaps=gaps,long_scatter=dict(duration=horizon,references={k:v[1] for k,v in refs.items()},reference_l1_gap=refgap,rows=rows),coupled=dict(duration=a.duration,reference_nfev=[nfev,nfev2],reference_max_abs_gap=float(np.max(abs(ref-ref2))),adaptive=adaptive))
a.out.write_text(json.dumps(out,indent=2,allow_nan=False)+'\n')
