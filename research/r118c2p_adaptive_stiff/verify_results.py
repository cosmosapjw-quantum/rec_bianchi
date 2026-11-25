import json,hashlib,ast
from pathlib import Path
import numpy as np
D=Path(__file__).resolve().parent;H=Path('/home/cosmosapjw/Downloads')
def sha(p):
    with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def j(p):return json.loads(p.read_text())
def inputs(z,k):
    prior=j(D.parent/'r118c2o_stiff_scatter'/f'{z}_{k}.json')
    files=dict(source_sha256=H/'rec_r118c2f_compiled_final'/(z+'.npz'),rates_sha256=Path('archive/inputs/original_hyrec_oct2012/HyRec_Oct2012.zip'),graph_sha256=H/'rec_r118c2k_refined'/z/'GRAPH128.npz',initial_state_sha256=H/'rec_r118c2k_refined'/z/f'n128_{k}_4.npz')
    out={key:sha(p) for key,p in files.items()}
    assert all(out[k]==prior[k] for k in out);return out
p=inputs('z1100','pulse');q=inputs('z900','actual')
a=j(D/'z1100_scatter_bounded.json');b=j(D/'z1100_coupled_bounded.json')
assert all(int((D/f).read_text())==0 for f in ('z1100_scatter_bounded.exit','z1100_coupled_bounded.exit','green.exit','regression.exit'))
assert a['status']=='SCATTER_SCOPED' and b['status']=='COUPLED_SCOPED'
assert all(a[k]==b[k]==v for k,v in p.items())
assert a['duration']==10000 and b['duration']==1
assert len(a['refs'])==3 and len(a['rows'])==4 and len(b['rows'])==2
with np.load(D/'z1100_scatter_bounded.ref.npz') as z:
    ref=z['Radau_2e-07'];den=np.sum(abs(ref))
    for k,v in a['reference_l1_gaps'].items():
        assert abs(float(np.sum(abs(z[k]-ref))/den)-v)<1e-18
assert a['reference_l1_gaps']['BDF_2e-08']<1e-9 and a['rows'][-1]['response_l1_relative']<1e-8
assert all(x['max_local']<=x['target'] and max(x['max_N'],x['max_E'])<1e-11 and x['rows'][-1]['t']==1 for x in b['rows'])
assert b['rows'][1]['state_l1_over_gross']<b['rows'][0]['state_l1_over_gross']
# Initial run reached the stated rows, but timed out before writing final JSON;
# record precisely what survived, without inventing full vectors or completion.
assert all(int((D/f).read_text())==124 for f in ('z900_actual.exit','z1100_pulse.exit'))
log=(D/'z900_actual.log').read_text().splitlines()
sc=[ast.literal_eval(x.split('long scatter ',1)[1]) for x in log if x.startswith('long scatter ')]
ad=[ast.literal_eval(x.split('adaptive ',1)[1]) for x in log if x.startswith('adaptive {')]
refs={x.split(' ')[1]:ast.literal_eval(x[x.index('{'):]) for x in log if x.startswith('reference ')}
assert [x['steps'] for x in sc]==[1,4,16,64,128] and len(refs)==2 and len(ad)==2
assert all(x['status']=='PASS_POSITIVE_CONSERVATIVE' for x in sc)
assert all(x['status']=='COMPLETE' and max(x['max_N'],x['max_E'])<1e-11 and x['max_local']<=x['target'] for x in ad)
assert sc[-1]['response_l1_relative']<3e-6 and ad[-1]['state_l1_over_gross']<ad[0]['state_l1_over_gross']
partial=dict(status='PARTIAL_LOG_ONLY_OUTER_TIMEOUT',bath='z900',kind='actual',original_timeout_s=220,original_exit=124,scatter_duration=10000,coupled_duration=10,completed_scatter_rows=sc,completed_adaptive_rows=ad,reference_log=refs,inputs_readback=q,limitations='full state vectors and reference L1 difference were not serialized before timeout; 1e-3 run unfinished')
(D/'Z900_PARTIAL.json').write_text(json.dumps(partial,indent=2)+'\n')
out=dict(status='PASS_SCOPED_STIFF_REFERENCE_AND_ADAPTIVE_WITH_TIMEOUT_LIMITS',parent='4f23c5d0b93c66e5a2b668aa25b867d09238d19b',z900=partial,z1100_scatter=a,z1100_coupled=b,initial_z1100_strict_reference='TIMEOUT_124; BDF completed, Radau incomplete',production_admission='HOLD_EVOLVING_BACKGROUND_AND_ZERO_STOCK',native_subagent='NOT_RUN',files={x.name:sha(x) for x in D.iterdir() if x.is_file() and x.name not in ('ACCEPTANCE.json','verify.log')})
(D/'ACCEPTANCE.json').write_text(json.dumps(out,indent=2)+'\n')
print('z900 log-only completed rows',len(sc),len(ad),'z1100 structured',len(a['rows']),len(b['rows']),'reference gap',a['reference_l1_gaps']['BDF_2e-08'])
