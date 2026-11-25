import json,hashlib,re
from pathlib import Path
D=Path(__file__).resolve().parent;H=Path('/home/cosmosapjw/Downloads')
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
prior=json.loads((D.parent/'r118c2r_stable_extent/z1100_pulse.json').read_text());out={};rows=[]
for name in ('physical','accelerated'):
 j=json.loads((D/(name+'.json')).read_text());assert j['status']=='COMPLETE_PRESCRIBED_EVOLVING_GRAPH' and int((D/(name+'.exit')).read_text())==0
 for k,p in [('history_sha',H/'rec_r118c2f_compiled_final/z900_HISTORY.json'),('source_sha256',H/'rec_r118c2f_compiled_final/z1100.npz'),('rates_sha256',Path('archive/inputs/original_hyrec_oct2012/HyRec_Oct2012.zip')),('graph_sha256',H/'rec_r118c2k_refined/z1100/GRAPH128.npz'),('initial_state_sha256',H/'rec_r118c2k_refined/z1100/n128_pulse_4.npz')]:
  assert sha(p)==j[k]
  if k in prior:assert j[k]==prior[k]
 for g in j['local_graphs'].values():
  p=Path(g['path']);assert sha(p/'RECEIPT.json')==g['receipt_sha']
  for f,h in g['hashes'].items():assert sha(p/f)==h
 assert j['interpolation']['global_l1']<1e-8 and j['interpolation']['max_edge_rel']<1e-7
 assert j['reference_gap']<1e-15 and len(j['rows'])==2
 for x in j['rows']:assert x['max_local']<=x['target'] and max(x['max_N'],x['max_E'])<1e-11 and x['steps'][-1]['t']==1
 assert j['rows'][1]['error']<j['rows'][0]['error']
 rows+=j['rows'];out[name]=j
b=json.loads((D/'BLOCKS.json').read_text());assert len(b['rows'])==4 and max(x['relative_l1'] for x in b['rows'])>.1
assert all(int((D/x).read_text())==0 for x in ('green.exit','blocks.exit','compile_end.exit','compile_mid.exit','regression.exit'))
res=dict(status='PASS_SCOPED_LOCAL_EVOLVING_GRAPH',parent='9a843ac2fb4fb95ed26bb0e8e1cd8f4af918638c',direct_local_graphs=2,edges=83178,adaptive_runs=len(rows),max_E=max(x['max_E'] for x in rows),fallbacks=sum(x['fallbacks'] for x in rows),cases=out,broad_interpolation_rejected=b,production_admission='HOLD_GLOBAL_RECOMBINATION_OWNER_AND_ZERO_DONOR',native_subagent='NOT_RUN',files={p.name:sha(p) for p in D.iterdir() if p.is_file() and p.name not in ('ACCEPTANCE.json','verify.log')})
(D/'ACCEPTANCE.json').write_text(json.dumps(res,indent=2)+'\n');print({k:v for k,v in res.items() if k not in ('files','cases','broad_interpolation_rejected')})
