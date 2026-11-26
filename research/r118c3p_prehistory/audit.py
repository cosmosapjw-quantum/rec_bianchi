"""Reconstruct actual prehistory pairs and native shared Schur line evidence."""
import json,numpy as np
from pathlib import Path
D=Path(__file__).resolve().parent
def run():
 rows={}
 for n,z,nm in [(32,1110,4),(64,1110,4),(32,1140,4),(64,1140,4),(32,1110,8)]:
  fmt=f'z{z}_n{n}_{{}}'+('_128ray' if nm==8 else '')
  a,b=[json.loads((D/(fmt.format(j)+'.json')).read_text()) for j in [0,1]]
  for k in ['prefix_sha','geometry_sha','rates_sha','steps','rays','zstart','donor_sha','initial_x','initial_T','prefix_steps']:assert a[k]==b[k]
  x,y=[np.load(D/(fmt.format(j)+'.npz'))['rows'] for j in [0,1]];assert np.array_equal(x[:,0],y[:,0])
  root=max(max(abs(np.diff(v[:,1])-np.diff(v[:,0])*v[1:,4])) for v in [x,y])
  assert root<1e-12 and min(x[:,7].min(),y[:,7].min())>0
  rows[fmt.format('pair')]=dict(dx=b['x']-a['x'],window_dx=b['window_x']-a['window_x'],local_dx=(b['x']-b['window_x'])-(a['x']-a['window_x']),deltaT=b['T']-a['T'],prefix_steps=a['prefix_steps'],total_steps=len(x)-1,root=float(root),atomic=max(a['max_atom_res'],b['max_atom_res']),initial_x=a['initial_x'],window_out_difference=[a['window_out'],b['window_out']])
 line=json.loads((D/'LINE_SCHUR.json').read_text());l=[q for a in line['rows'] for q in a['dynamic']]
 c={}
 for tag in ['schur','bare_diagonal']:
  z=[q for q in l if q['closure']==tag and q['steps']==64]
  c[tag]=dict(loss_range=[min(q['loss'] for q in z),max(q['loss'] for q in z)],escape_range=[min(q['net_escape'] for q in z),max(q['net_escape'] for q in z)],external_net_range=[min(q['external_net'] for q in z),max(q['external_net'] for q in z)])
 out=dict(rows=rows,line=dict(samples=len(line['rows']),cases=len(l),max_ledger=max(q['relative_ledger'] for q in l),max_res=max(q['max_residual'] for q in l),max_net_match=max(q['net_error'] for q in line['rows']),closures=c),scope='actual H-only earlier starts, no reset, first boundary still zero; not continuum certified; frozen native Schur line dynamic cell not full native trajectory insertion')
 (D/'AUDIT.json').write_text(json.dumps(out,indent=2)+'\n');print(out)
if __name__=='__main__':run()
