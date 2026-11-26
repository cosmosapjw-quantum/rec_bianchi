import json,hashlib
from pathlib import Path
import numpy as np
D=Path(__file__).resolve().parent;P=D.parent/'r118c2w_causal';G=Path('/home/cosmosapjw/Downloads/rec_r118c2w_full_local');R=Path('archive/inputs/original_hyrec_oct2012/HyRec_Oct2012.zip')
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def j(p):return json.loads(Path(p).read_text())
for n in ('green','train','feasibility','dual','run_fit','fit_audit','regression'):assert int((D/(n+'.exit')).read_text())==0,n
assert '28 passed' in (D/'regression.log').read_text()
a=j(D/'FIT.json');b=j(D/'FEASIBILITY.json');c=j(D/'RESULTS.json');q=j(D/'PROJECTION_AUDIT.json')
assert a['status']=='SCOPED_POSITIVE_MINIMAX' and c['status']=='SCOPED_FITTED_COARSE_OPACITY'
assert a['full_sha']==c['full_sha']==q['source_sha']==sha(P/'FULL_128.npz')
assert a['graph_sha']==c['graph_sha']==q['graph_sha']==sha(G/'GRAPH128.npz')
assert a['rates_sha']==c['rates_sha']==sha(R)
for path,h in a['source_hashes'].items():assert sha(path)==h==b['source_hashes'][path]
assert len(a['rows'])==len(b['rows'])==70
assert sum(x['train'] for x in a['rows'])==30
assert max(abs(x['dual_gap']) for x in b['rows'])<1e-9 and max(x['dual_lower'] for x in b['rows'])>.37
for info in a['stats']:assert info['energy_vector_defect']<1e-14 and info['train_worst']<info['baseline_worst']
f=np.load(D/'FIT.npz')
for k in ('g0','g1'):
 g=f[k];assert min(g.ravel())>=0 and np.array_equal(g,g.T) and np.all(np.diag(g)==0)
orig=np.load(P/'FULL_128.npz')
assert len(c['cases'])==3 and len(q['rows'])==15
for case in c['cases']:
 v=np.load(D/(case['case']+'.npz'));assert np.array_equal(v['virtual'][:,:96],orig['virtual_out'][:,:96])
 assert np.array_equal(v['lyman'][:,:96],orig['lyman_out'][:,:96])
 assert np.all((v['x']>0)&(v['x']<1)) and min(v['T'])>0
 assert len(case['rows'])==17 and all(x['residual']<2e-10 and x['root']<1e-8 and x['face']<1e-8 for x in case['rows'])
 assert all(abs(x['q_number'])<1e-28 and abs(x['q_energy']+x['heat'])<1e-28 and x['tau_ratio_min']>0 for x in case['rows'])
 if case['case']=='native':assert np.array_equal(v['x'],orig['xHII'][:113]) and np.array_equal(v['virtual'],orig['virtual_out'][:,:113])
assert max(x['energy_relative'] for x in q['rows'])<1e-12
out=dict(status='PASS_SCOPED_POSITIVE_MINIMAX_AND_FEASIBILITY_HOLD_PRODUCTION',parent='4d13a263d680d19a7e9d261b1e77ea0438650133',fit=a,feasibility=b,trajectory=c,audit=q,regression_tests=28,production_admission='HOLD_COARSE_REPRESENTABILITY',native_subagent='NOT_RUN')
(D/'ACCEPTANCE_CORE.json').write_text(json.dumps(out,indent=2)+'\n');print(out['status'],'max dual gap',max(abs(x['dual_gap']) for x in b['rows']))
