import json,hashlib
from pathlib import Path
import numpy as np
D=Path(__file__).resolve().parent;P=D.parent/'r118c2w_causal';G=Path('/home/cosmosapjw/Downloads/rec_r118c2w_full_local');R=Path('archive/inputs/original_hyrec_oct2012/HyRec_Oct2012.zip')
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
for n in ('green','run','regression'):assert int((D/(n+'.exit')).read_text())==0
assert '30 passed' in (D/'regression.log').read_text()
a=json.loads((D/'RESULTS.json').read_text())
assert a['full_sha']==sha(P/'FULL_128.npz') and a['graph_sha']==sha(G/'GRAPH128.npz') and a['rates_sha']==sha(R)
for p,h in a['source_hashes'].items():assert sha(p)==h
assert (a['mode_count'],a['unique_energy'],a['selected_edges'])==(568,554,27835)
assert a['clock_end']<a['delay'] and len(a['rows'])==8
for name in ('native','replacement'):
 rows=[r for r in a['rows'] if r['case']==name and not r.get('grouped')]
 assert [r['steps'] for r in rows]==[8,32,128] and rows[-1]['relative']<1e-9
 assert all(r['min_stock']>0 and max(r['number_residual'],r['energy_residual'])<1e-10 for r in rows)
 p=np.load(D/(name+'_state.npz'));e=p['e'];n=len(e);d=p['increment'];ref=p['reference']
 assert n==568 and len(np.unique(p['ids']))==568 and np.min(p['base']+d[:n])>0
 assert abs(float(np.sum(abs(d[:n]-ref[:n]))/np.sum(abs(ref[:n])))-rows[-1]['relative'])<1e-15
 group=[r for r in a['rows'] if r['case']==name and r.get('grouped')][0]
 assert group['relative']>1e-3 and max(group['number_residual'],group['energy_residual'])<1e-10
out=dict(status='PASS_SCOPED_LABELLED_CAUSAL_WING',parent='b1966a467b5c4f960e242e0372ae53aaa9f5b082',results=a,regression_tests=30,production_admission='HOLD_REFINED_FULL_OPACITY_REAL_2P_WRITEBACK',native_subagent='NOT_RUN')
(D/'ACCEPTANCE_CORE.json').write_text(json.dumps(out,indent=2)+'\n');print(out['status'])
