import json,hashlib,math
from pathlib import Path
D=Path(__file__).resolve().parent;H=Path('/home/cosmosapjw/Downloads')
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def j(p):return json.loads(p.read_text())
z=j(D/'ZERO.json');b=j(D/'BOUNDARY.json');c=j(D/'JOINED_COUPLED.json');a=j(D/'ACTION.json');p=j(D.parent/'r118c2t_cosmological/COUPLED.json')
assert all(int((D/f).read_text())==0 for f in ('green.exit','zero.exit','boundary.exit','joined.exit','action.exit','regression.exit'))
assert z['status']=='SCOPED_ZERO_SAFE_MPRK' and c['status']=='COMPLETE_SCOPED_JOINED_BOUNDARY_COUPLED'
for k,fn in [('source_sha256',H/'rec_r118c2f_compiled_final/z1100.npz'),('rates_sha256',Path('archive/inputs/original_hyrec_oct2012/HyRec_Oct2012.zip')),('graph_sha256',H/'rec_r118c2k_refined/z1100/GRAPH128.npz'),('initial_state_sha256',H/'rec_r118c2k_refined/z1100/n128_pulse_4.npz')]:
 assert sha(fn)==p[k]==z[k]==c[k]
assert b['graph_sha']==z['graph_sha256'] and b['initial_sha']==z['initial_state_sha256']
for g in c['local_graphs'].values():
 r=Path(g['path']);assert sha(r/'RECEIPT.json')==g['receipt_sha']
 for f,h in g['hashes'].items():assert sha(r/f)==h
assert len(z['cases'])==2 and all(x['reference_status']=='COMPLETE' for x in z['cases'].values())
d=z['cases']['depleted'];assert d['initial_zeros']==16 and all(r['filled']==12 and r['zeros']==4 for r in d['rows'])
for x in z['cases'].values():assert all(r['min_stock']>=0 and max(r['number_relative'],r['energy_relative'])<1e-11 for r in x['rows'])
assert all(max(r['number_defect'],r['energy_defect'])<1e-14 and r['ledger']['cross_N']>0 for r in b['cases'])
assert all(max(r['N'],r['E'])<1e-11 for r in c['rows'])
assert len(a['rows'])==6
for name,h in zip(('z900','z1300'),a['broad_graph_sha']):assert sha(H/'rec_r118c2k_refined'/name/'GRAPH128.npz')==h
for r in a['rows']:
 suf=2 if r['case']=='thermal' else 4
 assert sha(H/'rec_r118c2k_refined/z1100'/f"n128_{r['case']}_{suf}.npz")==r['state_sha']
assert sha(H/'rec_r118c2s_mid/GRAPH128.npz')==a['local_mid_sha']
assert '18 passed' in (D/'regression.log').read_text()
res=dict(status='PASS_SCOPED_ZERO_DONOR_JOINED_BOUNDARY',parent='d0cca33f5751d9a57a86f5b2fba9709c98180303',zero=z,boundary=b,coupled=c,action=a,regression_tests=18,zero_order_4_16=math.log(d['rows'][1]['state_error']/d['rows'][2]['state_error'],4),production_admission='HOLD_NATIVE_LINE_FACE_BOUNDARY_AND_STABLE_ZERO_DONOR_COMBINED_OWNER',native_subagent='NOT_RUN',files={f.name:sha(f) for f in D.iterdir() if f.is_file() and f.name not in ('ACCEPTANCE.json','verify.log')})
(D/'ACCEPTANCE.json').write_text(json.dumps(res,indent=2)+'\n');print(res['status'],res['zero_order_4_16'])
