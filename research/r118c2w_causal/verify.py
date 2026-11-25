import json,hashlib
from pathlib import Path
import numpy as np
D=Path(__file__).resolve().parent
H=Path('/home/cosmosapjw/Downloads'); R=D.parents[1]
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
for n in ('compile_mid','compile_end','long','evolving','full_face','full_local','regression'):
 assert int((D/(n+'.exit')).read_text())==0,n
a=json.loads((D/'LONG.json').read_text());b=json.loads((D/'FULL_FACE.json').read_text());c=json.loads((D/'FULL_LOCAL.json').read_text());e=json.loads((D/'EVOLVING.json').read_text())
p=H/'rec_r118c2k_refined/z1100';s=H/'rec_r118c2f_compiled_final'
assert sha(s/'z900_HISTORY.json')==a['history_sha']
assert sha(s/'z1100.npz')==a['source_sha256']
assert sha(R/'archive/inputs/original_hyrec_oct2012/HyRec_Oct2012.zip')==a['rates_sha256']==b['rate_sha']==c['rates_sha']
assert sha(p/'GRAPH128.npz')==a['graph_sha256']==b['graph_sha']
assert sha(p/'n128_pulse_4.npz')==a['initial_state_sha256']
assert sha(s/'STATES.json')==b['history_initial_state_sha']
for key,v in a['local_graphs'].items():
 path=Path(v['path']);assert sha(path/'RECEIPT.json')==v['receipt_sha']
 for name,h in v['hashes'].items():assert sha(path/name)==h
assert e['mid_graph_sha']==a['local_graphs']['mid']['hashes']['GRAPH128.npz']
assert e['end_graph_sha']==a['local_graphs']['end']['hashes']['GRAPH128.npz']
for r,n in zip(e['rows'],(4,8,12,16)):assert sha(D/f'EVOLVING_{n}.npz')==r['stock_sha']
assert e['terminal_bitwise_equal']
assert a['status']=='COMPLETE_SCOPED_10S_STABLE_ZERO'
assert c['status']=='COMPLETE_SCOPED_SAME_FULL_BATH'
for q in (a,c):
 assert [r['steps'] for r in q['rows']]==[4,16,64]
 err=[r['tracked_error'] for r in q['rows']];assert err[0]>err[1]>err[2]
 assert max(r['E'] for r in q['rows'])<1e-12 and max(r['N'] for r in q['rows'])<1e-12
 assert all(r['fallbacks']==0 for r in q['rows'])
for r in b['rows']:
 f=D/f"FULL_{r['n']}.npz";assert sha(f)==r['sha']
 with np.load(f) as v:
  assert np.min(v['stock'])>=0 and np.max(abs(v['incoming']-v['oracle']))<1e-28
 assert max(r['N'],r['E'])<1e-13
assert c['full_sha']==b['rows'][-1]['sha']
for name,h in c['raw_hashes'].items():assert sha(Path(c['raw'])/name)==h
assert '24 passed' in (D/'regression.log').read_text()
j=dict(status='PASS_SCOPED_10S_AND_CAUSAL_FULL_BATH',parent='f69450239e6b159661ba377fbc9361bb67af3306',long=a,full_face=b,full_local=c,evolving=e,regression_tests=24,production_admission='HOLD_TWO_WAY_FULL_RECOIL_AND_BROAD_EVOLUTION',native_subagent='NOT_RUN')
(D/'RESULTS.json').write_text(json.dumps(j,indent=2)+'\n')
print('verified 3+3 local steps, 2 causal face histories, 4 evolving stocks; all exits zero; 24 regression tests')
