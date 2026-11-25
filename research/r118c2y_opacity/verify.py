import hashlib,json
from pathlib import Path
import numpy as np
D=Path(__file__).resolve().parent;P=D.parent/'r118c2w_causal';G=Path('/home/cosmosapjw/Downloads/rec_r118c2w_full_local');R=Path('archive/inputs/original_hyrec_oct2012/HyRec_Oct2012.zip')
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def j(p):return json.loads(Path(p).read_text())
for n in ('green','opacity','projection_audit','energy_green','energy_run','energy_audit','regression'):assert int((D/(n+'.exit')).read_text())==0,n
assert '27 passed' in (D/'regression.log').read_text()
a=j(D/'RESULTS.json');b=j(D/'ENERGY_RESULTS.json');p=j(D/'PROJECTION_AUDIT.json');q=j(D/'ENERGY_AUDIT.json');prior=j(P/'FULL_LOCAL.json')
assert a['status']=='SCOPED_POSITIVE_COARSE_OPACITY' and b['status']=='SCOPED_ENERGY_ACTION_OPACITY'
assert a['full_sha']==b['full_sha']==prior['full_sha']==sha(P/'FULL_128.npz')
assert a['rates_sha']==b['rates_sha']==sha(R)
assert a['graph_sha']==b['graph_sha']==sha(G/'GRAPH128.npz')
assert p['source_sha']==q['source_sha']==a['full_sha'] and p['graph_sha']==q['graph_sha']==a['graph_sha']
assert [x['positive_offdiag'] for x in a['projection']]==[4,6]
assert all(x['energy_vector_defect']<1e-15 and x['min_cut']>0 for x in b['projection'])
orig=np.load(P/'FULL_128.npz')
for data,prefix in ((a,''),(b,'energy_')):
 assert len(data['cases'])==3
 for c in data['cases']:
    f=D/(prefix+c['case']+'.npz');v=np.load(f)
    assert np.array_equal(v['virtual'][:,:96],orig['virtual_out'][:,:96])
    assert np.array_equal(v['lyman'][:,:96],orig['lyman_out'][:,:96])
    assert np.all((v['x']>0)&(v['x']<1)) and min(v['T'])>0
    assert len(c['rows'])==17 and all(x['residual']<2e-10 and x['root']<1e-8 and x['face']<1e-8 for x in c['rows'])
    assert all(abs(x['q_number'])<1e-28 and abs(x['q_energy']+x['heat'])<1e-28 and x['tau_ratio_min']>0 for x in c['rows'])
    if c['case']=='native':
        assert np.array_equal(v['x'],orig['xHII'][:113]) and np.array_equal(v['virtual'],orig['virtual_out'][:,:113])
    assert c['terminal_x']==v['x'][-1] and c['terminal_T']==v['T'][-1]
assert len(p['rows'])==len(q['rows'])==15 and max(x['energy_relative'] for x in q['rows'])<1e-12
out=dict(status='PASS_SCOPED_POSITIVE_OPACITY_AND_ENERGY_ACTION_NOT_PRODUCTION',parent='2613f8aa3ae3267aea07fcbca38113cb97c14662',scalar_form=a,energy_action=b,scalar_audit=p,energy_audit=q,regression_tests=27,production_admission='HOLD_BINWISE_COLLISION_ACTION',native_subagent='NOT_RUN')
(D/'ACCEPTANCE_CORE.json').write_text(json.dumps(out,indent=2)+'\n')
print(out['status'],'max energy action error',max(x['energy_relative'] for x in q['rows']))
