"""Recompute matching and residual closure of actual bucketed trajectories."""
import numpy as np,json
from pathlib import Path
D=Path(__file__).resolve().parent
def run():
 rows={};checks=[]
 for f in sorted(D.glob('bucket*_0_*.json')):
  q=D/f.name.replace('_0_','_1_',1);a,b=[json.loads(v.read_text()) for v in [f,q]]
  for k in ['prefix_sha','geometry_sha','rates_sha','steps','rays','depth','predictor_intervals','clock','threshold']:assert a[k]==b[k]
  A,B=[np.load(v.with_suffix('.npz'))['rows'] for v in [f,q]];assert np.array_equal(A[:,0],B[:,0])
  for x in [A,B]:
   res=np.diff(x[:,1])-np.diff(x[:,0])*x[1:,4];checks.append(float(max(abs(res))));assert max(abs(res))<1e-12 and min(x[:,7])>0
  gens=b['ledger']['generations'];rows[f.stem.replace('_0_','_pair_')]=dict(dx=b['x']-a['x'],join=b['join_x']-a['join_x'],rays=b['rays'],steps=b['steps'],gen=b['depth'],predictor=b['predictor_intervals'],max_atomic=max(a['max_atom_res'],b['max_atom_res']),max_mass=float(max(abs(v['mass_residual']) for v in gens)),max_time_moment=float(max(abs(v['first_moment_residual']) for v in gens)),coupled_over_direct=[v['coupled_l1']/v['direct_l1'] for v in gens])
 o=json.loads((D/'LINE_SOURCED.json').read_text());z=[v for row in o['rows'] for v in row['dynamic']]
 line={}
 for tag in ['net_only','local_diagonal']:
  vals=[v for v in z if v['closure']==tag and v['steps']==64];line[tag]=dict(net_escape_range=[min(v['net_escape'] for v in vals),max(v['net_escape'] for v in vals)],external_net_range=[min(v['external_net'] for v in vals),max(v['external_net'] for v in vals)])
 out=dict(rows=rows,max_root=max(checks),line=dict(samples=len(o['rows']),cases=len(z),max_ledger=max(v['relative_ledger'] for v in z),max_res=max(v['max_residual'] for v in z),closures=line),scope='five matched pairs, all generation predictions finite; no convergence sign, no full-network line closure')
 (D/'AUDIT.json').write_text(json.dumps(out,indent=2)+'\n');print(out)
if __name__=='__main__':run()
