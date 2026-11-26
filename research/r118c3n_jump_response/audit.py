"""Check actual split history trajectories and line conservation."""
import numpy as np,json
from pathlib import Path
D=Path(__file__).resolve().parent
def run():
 rows={};checks={}
 for n,g in [(128,3),(256,3),(512,3),(256,1)]:
  labels=[f'split{n}_{i}_g{g}' for i in [0,1]]
  a,b=[json.loads((D/(l+'.json')).read_text()) for l in labels]
  for k in ['prefix_sha','geometry_sha','rates_sha','steps','rays','depth','clock']:assert a[k]==b[k]
  x,y=[np.load(D/(l+'.npz'))['rows'] for l in labels];assert np.array_equal(x[:,0],y[:,0])
  for lab,v in zip(labels,[x,y]):
   assert np.all(np.diff(v[:,0])>0) and np.all(v[:,7]>0)
   z=np.diff(v[:,1])-np.diff(v[:,0])*v[1:,4];checks[lab]=float(max(abs(z)));assert checks[lab]<1e-12
  rows[f'{n}_g{g}']=dict(delta=b['x']-a['x'],join=b['join_x']-a['join_x'],deltaT=b['T']-a['T'],xoff=a['x'],xon=b['x'],max_atom=max(a['max_atom_res'],b['max_atom_res']),first_direct=b['ledger']['first_direct_L1'],first_coupled=b['ledger']['first_coupled_L1'],envelope=b['ledger']['sampled_gain_integrated_envelope'],coupled_envelope=b['ledger']['sampled_coupled_envelope'],chains=b['ledger']['chains'])
 line=json.loads((D/'LINE_DYNAMIC.json').read_text());l=[v for row in line['rows'] for v in row['dynamic']]
 conv=[]
 for row in line['rows']:
  a,b,c,d=row['dynamic'];conv.append(abs(c['net_escape']-d['net_escape'])/max(abs(d['net_escape']),1e-300))
 o=dict(rows=rows,checks=checks,direct_chain_effect=rows['256_g3']['delta']-rows['256_g1']['delta'],line=dict(samples=len(line['rows']),max_ledger=max(v['relative_ledger'] for v in l),max_residual=max(v['max_residual'] for v in l),max_32_to64_relative_net_change=max(conv),net_range=[min(r['dynamic'][-1]['net_escape'] for r in line['rows']),max(r['dynamic'][-1]['net_escape'] for r in line['rows'])]),scope='fixed actual prior gas prediction used only for jump decomposition; actual atom and gas self-evolved. Sampled coupled envelope not a rigorous bound on continuum or all subsequent generations.')
 (D/'AUDIT.json').write_text(json.dumps(o,indent=2)+'\n');print(o)
if __name__=='__main__':run()
