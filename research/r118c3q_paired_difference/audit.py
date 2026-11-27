"""Audit all paired finite-amplitude accepted differences and frozen line network."""
import json,numpy as np,hashlib
from pathlib import Path
D=Path(__file__).resolve().parent;P=D.parent/'r118c3p_prehistory'
def run():
 rows={}
 for f in sorted(D.glob('*pair*.json')):
  a=json.loads(f.read_text());z=np.load(f.with_suffix('.npz'));v=z['rows'];ref=z['reference']
  assert np.array_equal(v[:,0],ref[:,0])
  assert np.all(v[1:,7]>0) and np.isfinite(v).all()
  err=float(max(abs(np.diff(v[:,1])-np.diff(v[:,0])*v[1:,3])))
  assert err<1e-14 and a['max_reference_residual']<1e-12
  assert max(abs(v[1:,5]-ref[1:,1]-v[1:,1]))<1e-15
  assert max(abs(v[1:,6]-ref[1:,2]-v[1:,2]))<1e-12
  zstart=1140 if f.stem.startswith('z1140') else 1110
  base=P/f"z{zstart}_n{a['nt']}_0.npz";assert hashlib.sha256(base.read_bytes()).hexdigest()==a['reference_sha']
  q=dict(**a,independent_root=err)
  if a['lam']==1:
   old=json.loads((P/f"z{zstart}_n{a['nt']}_0.json").read_text());new=json.loads((P/f"z{zstart}_n{a['nt']}_1.json").read_text())
   q['old_dx']=new['x']-old['x'];q['dx_reproduction_abs']=abs(q['old_dx']-a['dx'])
   assert q['dx_reproduction_abs']<1e-12
  rows[f.stem]=q
 assert len(rows)==10,len(rows)
 null=rows['pair32_0']['dx'];assert abs(null)<1e-12
 parity={}
 for n in [32,64]:
  a,b=[rows[f'pair{n}_{s}0.5']['dx'] for s in ['','-']]
  parity[str(n)]=dict(even_half=(a+b)/2,odd_half=(a-b)/2,even_over_lambda2=2*(a+b))
 a,b=[rows[f'pair32_{s}1']['dx'] for s in ['','-']];parity['32']['even_one']=(a+b)/2;parity['32']['odd_one']=(a-b)/2
 j=json.loads((D/'LINE_NETWORK.json').read_text());line=[q for r in j['rows'] for q in r['dynamic']]
 assert len(line)==99
 keys=['relative_ledger','line_energy_ledger_eV_H','max_algebraic_residual','max_flux_partition_error','max_residual']
 out=dict(rows=rows,parity=parity,max_root=max(x['independent_root'] for x in rows.values()),max_old_reproduction=max(x['dx_reproduction_abs'] for x in rows.values() if 'dx_reproduction_abs' in x),line=dict(samples=len(j['rows']),runs=len(line),**{k:max(abs(v[k]) for v in line) for k in keys}),scope='paired finite-difference, not exact tangent; same old discrete gas baseline, no continuum donor. Frozen conditional line-equivalent energy only')
 (D/'AUDIT.json').write_text(json.dumps(out,indent=2)+'\n');print({k:v for k,v in out.items() if k!='rows'},flush=True)
if __name__=='__main__':run()
