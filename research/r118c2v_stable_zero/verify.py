import json,hashlib,math
from pathlib import Path
D=Path(__file__).resolve().parent;H=Path('/home/cosmosapjw/Downloads')
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def j(p):return json.loads(p.read_text())
a=j(D/'RESULTS.json');c=j(D/'COUPLED.json');d=j(D/'DEPLETED_COUPLED.json');b=j(D/'NATIVE_FACE.json');t=j(D/'HOLDOUTS.json')
assert all(int((D/f).read_text())==0 for f in ('green.exit','reaction_green.exit','actual.exit','coupled.exit','depleted_coupled.exit','native_face.exit','compile_z1000.exit','compile_z1200.exit','holdouts.exit','regression.exit'))
assert a['status']=='SCOPED_INCREMENT_ZERO_MPRK'
assert c['status']==d['status']=='COMPLETE_SCOPED_STABLE_ZERO_COUPLED'
assert b['status']=='PASS_SCOPED_NATIVE_FROZEN_FACE' and t['status']=='SCOPED_TWO_FULL_GRAPH_HOLDOUTS'
for k,fn in [('source_sha256',H/'rec_r118c2f_compiled_final/z1100.npz'),('rates_sha256',Path('archive/inputs/original_hyrec_oct2012/HyRec_Oct2012.zip')),('graph_sha256',H/'rec_r118c2k_refined/z1100/GRAPH128.npz'),('initial_state_sha256',H/'rec_r118c2k_refined/z1100/n128_pulse_4.npz')]:
 assert sha(fn)==a[k]==c[k]==d[k]
assert b['graph_sha']==a['graph_sha256'] and b['initial_state_sha']==a['initial_state_sha256']
assert sha(Path('research/rec_line_native_owner_20261023/inputs/ORIGINAL_HYREC_TRAJECTORY_SNAPSHOT.csv'))==b['snapshot_sha']
for r in (c,d):
 for g in r['local_graphs'].values():
  root=Path(g['path']);assert sha(root/'RECEIPT.json')==g['receipt_sha']
  for f,h in g['hashes'].items():assert sha(root/f)==h
 assert [x['steps'] for x in r['rows']]==[1,4,16]
 assert all(max(x['N'],x['E'])<1e-11 and x['fallbacks']==0 for x in r['rows'])
 assert r['rows'][-1]['tracked_error']<r['rows'][0]['tracked_error']
assert len(d['depleted_nodes'])==16
for k,v in a['cases'].items():
 assert [r['steps'] for r in v['rows']]==[1,4,16,64]
 assert all(r['min_stock']>=0 and max(r['N'],r['E'])<1e-11 for r in v['rows'])
 assert v['rows'][-1]['error']<v['rows'][0]['error']
 if k=='depleted':assert all(r['filled']==12 and r['zeros']==4 for r in v['rows'])
assert len(b['rows'])==4 and b['occupation_ratio']>900
assert max(r['incoming_response_relative'] for r in b['rows'])<1e-12
for name,src in t['sources'].items():
 p=H/('rec_r118c2v_'+name);assert sha(p/'RECEIPT.json')==src['receipt_sha']
 for f,h in src['hashes'].items():assert sha(p/f)==h
for name,h in zip(('z900','z1100','z1300'),t['anchors_sha']):assert sha(H/'rec_r118c2k_refined'/name/'GRAPH128.npz')==h
assert len(t['rows'])==12
for r in t['rows']:
 suf=2 if r['probe']=='thermal' else 4
 assert sha(H/'rec_r118c2k_refined/z1100'/f"n128_{r['probe']}_{suf}.npz")==r['state_sha']
 if r['scope']=='refined':assert r['new_energy_relative']<1e-3
assert '20 passed' in (D/'regression.log').read_text()
res=dict(status='PASS_SCOPED_STABLE_ZERO_COUPLED_AND_FROZEN_FACE',parent='4a603b28525f5a5d0a12acf5621ce88f149c52e7',scattering=a,positive_coupled=c,depleted_coupled=d,frozen_face=b,holdouts=t,regression_tests=20,production_admission='HOLD_EVOLVING_NATIVE_FULL_BOUNDARY_AND_WHOLE_HISTORY',native_subagent='NOT_RUN',files={f.name:sha(f) for f in sorted(D.iterdir()) if f.is_file() and f.name not in ('ACCEPTANCE.json','verify.log')})
(D/'ACCEPTANCE.json').write_text(json.dumps(res,indent=2)+'\n');print(res['status'],len(res['files']))
