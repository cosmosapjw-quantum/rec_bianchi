import json,hashlib
from pathlib import Path
D=Path(__file__).resolve().parent;H=Path('/home/cosmosapjw/Downloads')
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
rows=[];cases={}
for n in ('z900_actual','z1100_pulse'):
 p=D/(n+'.json');j=json.loads(p.read_text());prior=json.loads((D.parent/'r118c2o_stiff_scatter'/(n+'.json')).read_text())
 assert int(p.with_suffix('.exit').read_text())==0 and j['status']=='SCOPED_PRESCRIBED_BATH'
 z=j['bath'];k=j['kind']
 for name,f in [('source_sha256',H/'rec_r118c2f_compiled_final'/(z+'.npz')),('rates_sha256',Path('archive/inputs/original_hyrec_oct2012/HyRec_Oct2012.zip')),('graph_sha256',H/'rec_r118c2k_refined'/z/'GRAPH128.npz'),('initial_state_sha256',H/'rec_r118c2k_refined'/z/f'n128_{k}_4.npz')]:
  assert sha(f)==j[name]==prior[name]
 assert j['duration']==1 and j['bath_relative_change']==1e-5 and len(j['rows'])==2 and j['reference_gap']<1e-15
 assert len(j['tiny_checks'])>=8 and max(x['relative'] for x in j['tiny_checks'])<2e-12
 for r in j['rows']:
  assert r['rows'][-1]['t']==1 and r['max_local']<=r['target'] and max(r['max_N'],r['max_E'])<1e-11
 assert j['rows'][-1]['state_l1_over_gross']<j['rows'][0]['state_l1_over_gross']
 rows.extend(j['rows']);cases[n]=j
assert int((D/'regression.exit').read_text())==0
res=dict(status='PASS_SCOPED_STABLE_ACTIVITY_PRESCRIBED_BATH',parent='8d4489b84839dc9d605679db84d6984acfb442ac',cases=cases,adaptive_runs=len(rows),mpmath_checks=sum(len(x['tiny_checks']) for x in cases.values()),max_mp_relative=max(v['relative'] for x in cases.values() for v in x['tiny_checks']),max_N=max(r['max_N'] for r in rows),max_E=max(r['max_E'] for r in rows),production_admission='HOLD_FULL_EVOLVING_BATH_AND_SOURCE_RATES',native_subagent='NOT_RUN',files={p.name:sha(p) for p in D.iterdir() if p.is_file() and p.name not in ('ACCEPTANCE.json','verify.log')})
(D/'ACCEPTANCE.json').write_text(json.dumps(res,indent=2)+'\n');print({k:v for k,v in res.items() if k not in ('files','cases')})
