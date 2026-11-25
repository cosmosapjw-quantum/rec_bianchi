import json,hashlib,time
from pathlib import Path
import numpy as np
from full_bianchi_hyrec.recoil.calibrated_source import Bath,_job
from evolving import ActualBath,KernelHistory
H=Path('/home/cosmosapjw/Downloads');D=Path(__file__).resolve().parent
p=H/'rec_r118c2f_compiled_final';st=json.loads((p/'STATES.json').read_text())['states'];names=['z900','z1100','z1300']
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
hist=json.loads((p/'z900_HISTORY.json').read_text())['states'];h=ActualBath(hist,st['z1100']);r=h.point(1000.)
dat=[np.load(p/(z+'.npz')) for z in names];assert all(np.array_equal(x['pairs'],dat[0]['pairs']) for x in dat)
T=[st[z]['T_m_K'] for z in names];ns=[st[z]['n_1s_m3'] for z in names]
out=[]
# selected coarse blocks, including two off-diagonal and a same-cell.
for pair in [(0,0),(0,1),(7,16),(10,28)]:
 ix=np.flatnonzero(np.all(dat[0]['pairs']==pair,axis=1))[0]
 raw=np.stack([x['Q4'][ix] for x in dat])
 # some quadrature matrices have structurally zero entries; log-interpolate
 # strictly positive common support, preserve exact structural zeros.
 mask=np.all(raw>0,axis=0);mixed=np.any(raw>0,axis=0)&~mask
 interp=np.zeros_like(raw[0]);interp[mask]=KernelHistory(T,ns,raw[:,mask])(r['T_m_K'],r['n1s'])
 if mixed.any():
  interp[mixed]=np.array([np.interp(r['T_m_K'],T,raw[:,i,j]/np.array(ns))*r['n1s'] for i,j in zip(*np.where(mixed))])
 t=time.monotonic();job=_job((*pair,Bath(r['T_m_K'],r['n1s']),(4,)));direct=job[2][4]
 rel=float(np.sum(abs(interp-direct))/max(np.sum(abs(direct)),1e-300))
 row=dict(pair=pair,relative_l1=rel,sum_direct=float(direct.sum()),sum_interpolated=float(interp.sum()),mixed_support=int(mixed.sum()),seconds=time.monotonic()-t)
 out.append(row);print(row,flush=True)
 np.savez_compressed(D/'BLOCKS.npz',**{str(i):np.asarray([v['sum_direct'],v['sum_interpolated']]) for i,v in enumerate(out)})
 (D/'BLOCKS.json').write_text(json.dumps(dict(status='DIRECT_SUBSET_NOT_FULL_KERNEL',z=1000.,bath=r,rows=out,inputs={str(p/(z+'.npz')):sha(p/(z+'.npz')) for z in names},history_sha=sha(p/'z900_HISTORY.json')),indent=2)+'\n')
