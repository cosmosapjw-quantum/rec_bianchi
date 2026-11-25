import json,hashlib
from pathlib import Path
import numpy as np
from scipy.sparse import bmat,csr_matrix
from scipy.sparse.linalg import expm_multiply
from scipy.integrate import solve_ivp
from boundary import JoinedDrift,L
D=Path(__file__).resolve().parent;H=Path('/home/cosmosapjw/Downloads/rec_r118c2k_refined/z1100')
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
g=np.load(H/'GRAPH128.npz');s=np.load(H/'n128_pulse_4.npz')
n=np.r_[s['nt']+s['initial_dt'],s['nc']+s['initial_dc']].astype(L);d=JoinedDrift(g['et'],g['gt'],g['ec'],g['gc'])
z0=1099.7154650522846;cases=[]
for name,du in [('physical_1s',5.1464449497217536e-14),('actual_dz_point1',np.log(1100.7154650522846/1100.6154650522847))]:
    inj=d.planck_influx(L(du)/2,z0)
    dx,l=d.affine(n,np.zeros_like(n),du,inj);v=n+dx
    nd=abs(dx.sum()+l['escape_N']-l['in_N'])/n.sum();ed=abs(dx@d.e+l['escape_U']+l['work']-l['in_U'])/(n@d.e)
    assert max(nd,ed)<1e-14 and l['cross_N']>0 and np.min(v)>=0
    # independent affine sparse exponential including count/work ledgers.
    b=np.zeros(len(n)+3);b[d.top]=np.asarray(inj*d.topw,float)
    A=bmat([[d.matrix(),csr_matrix(b[:,None])],[csr_matrix((1,len(b))),csr_matrix((1,1))]],format='csr')
    ref=expm_multiply(A*du,np.asarray(np.r_[n,0.,0.,0.,1.],float))
    er=float(np.sum(abs(v-ref[:len(n)]))/n.sum());le=float(np.max(abs(np.array([l[k] for k in ('escape_N','escape_U','work')],dtype=L)-ref[len(n):len(n)+3])/np.maximum(abs(ref[len(n):len(n)+3]),1e-300)))
    assert er<1e-11 and le<1e-10
    row=dict(case=name,du=du,number_defect=float(nd),energy_defect=float(ed),state_relative=er,ledger_relative=le,ledger={k:float(v) for k,v in l.items()})
    cases.append(row);print(row,flush=True)
# time-varying top boundary over actual dz=0.1: independent ODE on increments
du=cases[1]['du'];scale=L(n.max())
def rhs(t,y):
 stock=n+np.asarray(y[:len(n)],dtype=L)*scale;f=d.rate*stock;I=d.planck_influx(t,z0);dd=d.divergence(f);dd[d.top]+=I*d.topw;esc=f[d.escape].sum()
 return np.asarray(np.r_[dd,esc,esc*d.ghost,f@d.de,I,I*d.e.max(),f@d.cross_weight]/scale,float)
refs=[]
for tol in (3e-10,3e-11):
 r=solve_ivp(rhs,(0,du),np.zeros(len(n)+6),method='DOP853',rtol=tol,atol=tol*1e-5,max_step=du/256);assert r.success;refs.append(np.asarray(r.y[:,-1],dtype=L)*scale)
rr=[]
for steps in (1,4,16):
 delta=np.zeros_like(n);l={k:L(0) for k in ('escape_N','escape_U','work','in_N','in_U','cross_N')}
 for i in range(steps):
    h0=L(du)/steps;delta,v=d.affine(n,delta,h0,d.planck_influx((L(i)+L('.5'))*h0,z0))
    for k in l:l[k]+=v[k]
 ref=refs[-1];er=float(np.sum(abs(delta-ref[:len(n)]))/np.sum(abs(ref[:len(n)])))
 le=float(np.max(abs(np.array(list(l.values()),dtype=L)/ref[len(n):]-1)))
 row=dict(steps=steps,response_error=er,ledger_relative=le,number_defect=float(abs(delta.sum()+l['escape_N']-l['in_N'])/n.sum()),energy_defect=float(abs(delta@d.e+l['escape_U']+l['work']-l['in_U'])/(n@d.e)))
 rr.append(row);print('evolving',row,flush=True)
out=dict(status='SCOPED_JOINED_BOUNDARY',scope='one nodal registry and prescribed blackbody upper boundary; not original HyRec line-face fplus',graph_sha=sha(H/'GRAPH128.npz'),initial_sha=sha(H/'n128_pulse_4.npz'),cases=cases,refinements=rr,reference_gap=float(np.sum(abs(refs[0]-refs[1]))/np.sum(abs(refs[1]))))
(D/'BOUNDARY.json').write_text(json.dumps(out,indent=2)+'\n')
