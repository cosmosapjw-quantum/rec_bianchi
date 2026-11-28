"""Signed trajectory discrepancy and finite-precision baseline audit."""
from pathlib import Path
import numpy as np,json,hashlib
D=Path(__file__).resolve().parent;P=D.parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 cur=D/'COMPOSED.npz';z=np.load(cur);v=z['y'];dy=z['dy'];base=np.load(D/'SMALL_FD_0.npz');assert np.array_equal(base['u'],z['u'][:129]);bg=np.max(abs(base['y']-v[:129]),axis=0)
 rows=[]
 paths=sorted(D.glob('SMALL_FD*.npz'))+sorted((P/'r118c4m_analytic_history').glob('SMALL_FD*.npz'))+sorted((P/'r118c4k_lambda_tangent').glob('*FD*.npz'))
 for path in paths:
  ep=float(path.stem.rsplit('_',1)[1])
  if ep==0:continue
  a=np.load(path);n=min(len(z['u']),len(a['u']));assert np.array_equal(a['u'][:n],z['u'][:n])
  j=0 if ep>0 else 1;fd=(a['y'][:n]-v[:n])/abs(ep);e=fd-dy[:n,j];mx=np.max(abs(e),axis=0)
  row=dict(file=str(path.relative_to(P)),eps=ep,steps=n-1,source_sha=sha(path),max_absolute_gap=mx.tolist(),max_gap_steps=np.argmax(abs(e),axis=0).tolist(),peak_direction=np.max(abs(dy[:n,j]),axis=0).tolist(),terminal_gap=e[-1].tolist(),step99_gap=e[99].tolist(),step63_gap=e[63].tolist())
  if n==129:
   d=(a['y']-base['y'])/abs(ep);row['same_runner_zero_centered_max_gap']=np.max(abs(d-dy[:129,j]),axis=0).tolist()
  if n==len(z['u']):
   ref=(a['last']-z['last'])/abs(ep);row['last_history_relative']=float(np.linalg.norm(ref-z['last_d'][j])/max(np.linalg.norm(ref),1e-300));row['same_limiter_keys']=bool(np.array_equal(a['limits'][:,:3],z['limits'][:,:3]))
  rows.append(row)
 small=[x for x in rows if 'same_runner_zero_centered_max_gap'in x];minus=[x for x in small if x['eps']<0];best=min(minus,key=lambda x:x['max_absolute_gap'][0]);full=[x for x in rows if x['steps']==1773]
 summary=dict(zero_runner_nominal_max_gap=bg.tolist(),minus_small_best=best,full_signed=full,thermal_resolution='small-delta gas temperature difference comparable to floating-point subtraction floor; independent temperature trajectory derivative not certified')
 if (D/'EVENT_DIAGNOSTIC.json').is_file():
  e=json.loads((D/'EVENT_DIAGNOSTIC.json').read_text());summary['event_99_transitions']=[x for x in e['rows'] if x['step']==99]
 (D/'SIGNED_AUDIT.json').write_text(json.dumps(dict(rows=rows,summary=summary,current_sha=sha(cur),zero_sha=sha(D/'SMALL_FD_0.npz'),scope='independent source nonlinear histories and same-runner zero baseline for 128-step prefix only; full finite paths at eps .003; small-eps results preserve finite-amplitude branch transitions and roundoff limits'),indent=2,allow_nan=False)+'\n')
 print(json.dumps(summary,indent=2)[:12000])
if __name__=='__main__':main()
