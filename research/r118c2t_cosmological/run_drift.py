import hashlib,json
from pathlib import Path
import numpy as np
from scipy.sparse.linalg import expm_multiply
from drift import Redshift,L
D=Path(__file__).resolve().parent;H=Path('/home/cosmosapjw/Downloads/rec_r118c2k_refined/z1100')
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
g=np.load(H/'GRAPH128.npz');s=np.load(H/'n128_pulse_4.npz')
rows=[]
for name,E,G,N in [('tracked',g['et'],g['gt'],s['nt']+s['initial_dt']),('companion',g['ec'],g['gc'],s['nc']+s['initial_dc'])]:
 d=Redshift(E,G)
 for tag,du in [('physical_1s',5.1464449497217536e-14),('actual_dz_point1',np.log(1100.7154650522846/1100.6154650522847))]:
  dx,ledger=d.increment(N,np.zeros_like(N),du);v=N+dx
  ndef=abs(dx.sum()+ledger['escape_N'])/N.sum()
  edef=abs(dx@E+ledger['escape_U']+ledger['work'])/(N@E)
  assert max(ndef,edef)<1e-14 and np.min(v)>=0
  # independently evolve augmented generator, integrate the three ledger outputs
  ref=expm_multiply(d.matrix()*float(du),np.asarray(np.r_[N,0.,0.,0.],float))
  gap=np.sum(abs(v-ref[:-3]))/N.sum()
  lg=np.array(list(ledger.values()),dtype=L)
  lref=np.array(ref[-3:],dtype=L)
  lerr=np.max(abs(lg-lref)/np.maximum(abs(lref),L('1e-300')))
  assert gap<1e-11 and lerr<1e-10
  row=dict(domain=name,n=len(N),case=tag,du=float(du),lambda_du=float(d.lam*du),number_defect=float(ndef),energy_defect=float(edef),state_relative=float(gap),ledger_relative=float(lerr),escape_N=float(ledger['escape_N']),escape_U=float(ledger['escape_U']),redshift_work=float(ledger['work']),relative_work=float(ledger['work']/(N@E)),minimum=float(v.min()))
  rows.append(row);print(row,flush=True)
out=dict(status='PASS_SCOPED_ACTUAL_GRAPH_COMOVING_REDSHIFT',scope='fixed physical nodal upwind, finite domains with ghost escape, no boundary inflow; exact time evolution of represented generator',rows=rows,graph_sha=sha(H/'GRAPH128.npz'),initial_sha=sha(H/'n128_pulse_4.npz'))
(D/'DRIFT.json').write_text(json.dumps(out,indent=2)+'\n')
