import hashlib,json,re
from pathlib import Path
import numpy as np
D=Path(__file__).resolve().parent;H=Path('/home/cosmosapjw/Downloads')
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
d=json.loads((D/'DRIFT.json').read_text());c=json.loads((D/'COUPLED.json').read_text());a=json.loads((D/'ANCHORS.json').read_text())
assert d['status']=='PASS_SCOPED_ACTUAL_GRAPH_COMOVING_REDSHIFT' and len(d['rows'])==4
assert c['status']=='COMPLETE_SCOPED_COMOVING_COUPLED' and [r['steps'] for r in c['rows']]==[1,4,16]
assert all(int((D/f).read_text())==0 for f in ('green.exit','drift.exit','coupled.exit','anchor.exit','regression.exit'))
prior=json.loads((D.parent/'r118c2s_evolving/physical.json').read_text())
for k,p in [('history_sha',H/'rec_r118c2f_compiled_final/z900_HISTORY.json'),('source_sha256',H/'rec_r118c2f_compiled_final/z1100.npz'),('rates_sha256',Path('archive/inputs/original_hyrec_oct2012/HyRec_Oct2012.zip')),('graph_sha256',H/'rec_r118c2k_refined/z1100/GRAPH128.npz'),('initial_state_sha256',H/'rec_r118c2k_refined/z1100/n128_pulse_4.npz')]:
 assert sha(p)==c[k]==prior[k]
assert d['graph_sha']==c['graph_sha256'] and d['initial_sha']==c['initial_state_sha256']
for x in c['local_graphs'].values():
 p=Path(x['path']);assert sha(p/'RECEIPT.json')==x['receipt_sha']
 for f,h in x['hashes'].items():assert sha(p/f)==h
assert a['history_sha']==c['history_sha'] and sha(H/'rec_r118c2f_compiled_final/STATES.json')==a['states_sha']
assert len(a['leaves'])==16 and a['direct_temperatures']==65 and all(x['holdout_status']=='PASS_SAMPLED' and x['status']=='MIDPOINT_ACCEPT' for x in a['leaves'])
assert all(max(x['N'],x['E'])<1e-11 and x['fallbacks']==0 for x in c['rows'])
order=float(np.log(c['rows'][1]['tracked_error']/c['rows'][2]['tracked_error'])/np.log(4))
assert 1.9<order<2.1
res=dict(status='PASS_SCOPED_COMOVING_DRIFT_AND_LOCAL_COUPLED',parent='690070ea28e2f013b233cd43f13b2dc27adf9bf9',drift=d,coupled=c,anchor_subset=a,tracked_order_4_16=order,regression_tests=17,max_drift_state_relative=max(x['state_relative'] for x in d['rows']),max_drift_ledger_relative=max(x['ledger_relative'] for x in d['rows']),max_coupled_E=max(x['E'] for x in c['rows']),production_admission='HOLD_FULL_BOUNDARY_INFLOW_ZERO_DONOR_SCATTER_AND_GLOBAL_BATH',native_subagent='NOT_RUN',files={p.name:sha(p) for p in D.iterdir() if p.is_file() and p.name not in ('ACCEPTANCE.json','verify.log')})
assert '17 passed' in (D/'regression.log').read_text()
(D/'ACCEPTANCE.json').write_text(json.dumps(res,indent=2)+'\n')
print({k:v for k,v in res.items() if k not in ('files','drift','coupled','anchor_subset')})
