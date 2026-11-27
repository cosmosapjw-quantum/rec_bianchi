"""Audit actual weak history projection and baseline provenance."""
import json,numpy as np,hashlib
from pathlib import Path
D=Path(__file__).resolve().parent
def run():
 rows={}
 for n in [32,64,128]:
  q=json.loads((D/f'weak_{n}.json').read_text());z=np.load(D/f'weak_{n}.npz');r=z['rows'];assert np.array_equal(r[:,0],z['he'][1:]) and np.isfinite(r).all() and r[-1,1]==q['x2']
  assert np.max(abs((z['L2']+z['R2'])/2-z['M2']))<1e-24 and q['first_reproduction']<1e-4
  # moments of the stored affine function; second moment in this test is
  # not a separate constraint.
  m0=(z['L2']+z['R2'])/2;m1=(z['L2']+2*z['R2'])/6
  l=4*m0-6*m1;r=6*m1-2*m0
  err=float((np.linalg.norm(l-z['L2'])+np.linalg.norm(r-z['R2']))/max(np.linalg.norm(z['L2'])+np.linalg.norm(z['R2']),1e-300))
  assert err<1e-12
  base=D/f'z1110_n{n}_0.npz' if n==128 else D.parent/f'r118c3p_prehistory/z1110_n{n}_0.npz'
  rows[str(n)]=dict(**q,affine_projection_relative=err,reference_sha=hashlib.sha256(base.read_bytes()).hexdigest())
 a,b,c=[rows[str(n)]['x2'] for n in [32,64,128]]
 en=json.loads((D/'TRANSPORT_ENERGY.json').read_text())['rows'];assert len(en)==9
 for t in en.values():assert abs(t['birth_energy']-t['terminal_total']-t['metric_work'])<1e-14 and t['number_change']==0
 out=dict(rows=rows,relative_32_64=abs(a-b)/abs(b),relative_64_128=abs(b-c)/abs(c),energy_transport=en['16_128'],energy_65_128_relative=abs(en['16_65']['terminal_total']-en['16_128']['terminal_total'])/abs(en['16_128']['terminal_total']),scope='three native-reference weak-history projected calculations, not converged; free-flight energy diagnostic only')
 (D/'AUDIT.json').write_text(json.dumps(out,indent=2)+'\n');print(out,flush=True)
if __name__=='__main__':run()
