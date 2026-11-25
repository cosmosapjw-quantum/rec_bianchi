import json,hashlib
from pathlib import Path
import numpy as np
D=Path(__file__).parent;K=Path('/home/cosmosapjw/Downloads/rec_r118c2k_refined');L=D.parent/'r118c2l_time_order';compiled=Path('/home/cosmosapjw/Downloads/rec_r118c2f_compiled_final')
def sha(p):
    with open(p,'rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
cases={}; rows=[]
for p in sorted(D.glob('z*.json')):
    j=json.loads(p.read_text()); assert int(p.with_suffix('.exit').read_text())==0
    assert j['n']==128 and len(j['rows'])==3
    bath=j['bath'];kind=j['kind'];prior=json.loads((L/(bath+'_'+kind+'.json')).read_text())
    for field in ['source_sha256','rates_sha256','graph_sha256','initial_state_sha256']:assert j[field]==prior[field]
    assert sha(compiled/(bath+'.npz'))==j['source_sha256']
    assert sha(K/bath/'GRAPH128.npz')==j['graph_sha256']
    assert sha(K/bath/f'n128_{kind}_4.npz')==j['initial_state_sha256']
    assert sha(Path('archive/inputs/original_hyrec_oct2012/HyRec_Oct2012.zip'))==j['rates_sha256']
    rr=j['rows'];assert [r['target'] for r in rr]==[1e-3,1e-4,1e-5]
    assert all(r['max_error']<=r['target'] and max(r['max_N'],r['max_E'])<1e-11 for r in rr)
    for r in rr:
        assert r['accepted']==len(r['rows']) and r['rows'][-1]['t']==j['physical_duration_s']
        h=np.array([x['h'] for x in r['rows']]);t=np.array([x['t'] for x in r['rows']]);assert np.all(h>0) and np.all(np.diff(t)>0)
        assert abs(h.sum()-j['physical_duration_s'])<1e-13
    assert all(a['delta_n2_rel']>b['delta_n2_rel'] for a,b in zip(rr,rr[1:]))
    cases[p.stem]=dict(duration=j['physical_duration_s'],reference_max_diff=j['reference_state_max_diff'],
        targets=[{k:v for k,v in r.items() if k!='rows'} for r in rr])
    rows+=rr
assert len(cases)==4 and len(rows)==12
assert '9 passed' in (D/'green.log').read_text()
assert '1 failed' in (D/'first_green_failed.log').read_text()
res=dict(status='PASS_SCOPED_ADAPTIVE_FROZEN_GRAPH',parent='b2e7b8d51e317030dffa50835b54b08242cf2ce7',cases=cases,runs=len(rows),
    accepted_steps=sum(r['accepted'] for r in rows),max_N=max(r['max_N'] for r in rows),max_E=max(r['max_E'] for r in rows),
    full_suite_exit=int((D/'full_tests.exit').read_text()),full_suite_status='TIMEOUT_NOT_PASS',
    production_admission='HOLD',reference='two tolerances, same finite graph; no rigorous a posteriori global bound',
    files={p.name:sha(p) for p in D.iterdir() if p.is_file() and p.name not in ('ACCEPTANCE.json','verify.log')})
(D/'ACCEPTANCE.json').write_text(json.dumps(res,indent=2)+'\n');print({k:v for k,v in res.items() if k not in ('files','cases')})
