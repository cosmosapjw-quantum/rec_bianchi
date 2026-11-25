import json,hashlib,math
from pathlib import Path
D=Path(__file__).resolve().parent;H=Path('/home/cosmosapjw/Downloads')
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
rows=[];stiff=[];cases={}
for name in ('z900_actual','z1100_pulse','z1300_actual'):
 p=D/(name+'.json');j=json.loads(p.read_text());prior=json.loads((D.parent/'r118c2o_stiff_scatter'/(name+'.json')).read_text())
 assert int(p.with_suffix('.exit').read_text())==0 and j['status']=='SCOPED_COMPLETE'
 z=j['bath'];k=j['kind']
 for key,fn in [('source_sha256',H/'rec_r118c2f_compiled_final'/(z+'.npz')),('rates_sha256',Path('archive/inputs/original_hyrec_oct2012/HyRec_Oct2012.zip')),('graph_sha256',H/'rec_r118c2k_refined'/z/'GRAPH128.npz'),('initial_state_sha256',H/'rec_r118c2k_refined'/z/f'n128_{k}_4.npz')]:
  assert sha(fn)==j[key]==prior[key]
 assert len(j['tiny_checks'])==18 and {x['kind'] for x in j['tiny_checks']}=={-1,1}
 assert max(x['relative'] for x in j['tiny_checks'])<1e-11
 assert j['reference_gap']<1e-15
 assert [r['steps'] for r in j['rows']]==[1,4,16] and [r['h'] for r in j['stiff']]==[10.,100.]
 assert all(r['status']=='PASS' and max(r['N'],r['E'])<1e-11 and r['roundoff_fallbacks']==0 for r in j['rows']+j['stiff'])
 order=math.log(j['rows'][1]['error']/j['rows'][2]['error'],4);assert 1.95<order<2.05
 j['observed_order_4_to_16']=order;cases[name]=j;rows+=j['rows'];stiff+=j['stiff']
assert all(int((D/x).read_text())==0 for x in ('local_green.exit','regression.exit'))
assert all(int((D/(x+'.first_failed.exit')).read_text())==1 for x in cases)
assert 'nonpositive relaxation rate' in (D/'z900_diagnostic.log').read_text()
res=dict(status='PASS_SCOPED_EVENT_LOCAL_STABLE_EXTENT',parent='ebe0341e6ac542a2c95de6c7436b60fb688cd512',cases=cases,source_only_runs=len(stiff),coupled_runs=len(rows),mpmath_checks=54,max_mp_relative=max(x['relative'] for j in cases.values() for x in j['tiny_checks']),max_N_coupled=max(r['N'] for r in rows),max_E_coupled=max(r['E'] for r in rows),max_E_source=max(r['E'] for r in stiff),fallbacks=sum(r['roundoff_fallbacks'] for r in rows+stiff),production_admission='HOLD_FULL_EVOLVING_GRAPH_ZERO_DONOR',native_subagent='NOT_RUN',files={p.name:sha(p) for p in D.iterdir() if p.is_file() and p.name not in ('ACCEPTANCE.json','verify.log')})
(D/'ACCEPTANCE.json').write_text(json.dumps(res,indent=2)+'\n');print({k:v for k,v in res.items() if k not in ('files','cases')})
