import json,hashlib,math
from pathlib import Path
D=Path(__file__).parent;K=Path('/home/cosmosapjw/Downloads/rec_r118c2k_refined');C=Path('/home/cosmosapjw/Downloads/rec_r118c2f_compiled_final')
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
cases={}; rows=[];stiff=[]
for name in ('z900_actual','z1100_pulse','z1300_actual'):
    p=D/(name+'.json');j=json.loads(p.read_text());old=json.loads((D/(name+'_v1.json')).read_text())
    assert int(p.with_suffix('.exit').read_text())==0
    b=j['bath'];k=j['kind'];r=j['rows'];s=j['stiff_source']
    for field,file in [('source_sha256',C/(b+'.npz')),('rates_sha256',Path('archive/inputs/original_hyrec_oct2012/HyRec_Oct2012.zip')),('graph_sha256',K/b/'GRAPH128.npz'),('initial_state_sha256',K/b/f'n128_{k}_4.npz')]:
        assert j[field]==old[field]==sha(file)
    assert j['physical_duration_s']==1 and [x['steps'] for x in r]==[1,2,4,8,16,32]
    assert all(x['status']=='PASS_SCOPED' and max(x['N'],x['E'])<1e-11 and x['max_root']<1e-10 for x in r)
    assert all(x['status']=='PASS_SCOPED_SOURCE_ONLY' and max(x['N'],x['E'])<1e-11 for x in s)
    orders=[math.log2(a['state_l1_over_gross']/b['state_l1_over_gross']) for a,b in zip(r,r[1:])]
    assert 1.95<orders[-1]<2.05
    cases[name]=dict(state_orders=orders,last=r[-1],stiff=s,reference_max_diff=j['reference_state_max_diff'])
    rows+=r;stiff+=s
assert json.loads((D/'z1300_actual_v1.json').read_text())['stiff_source'][-1]['status']=='REJECTED'
assert cases['z1300_actual']['stiff'][-1]['roundoff_fallbacks']>0
assert '12 passed' in (D/'green_final.log').read_text() and int((D/'green_final.exit').read_text())==0
res=dict(status='PASS_SCOPED_FROZEN_GRAPH_AND_SOURCE_STIFF_LANE',parent='567ad5eb50804ba2a0ba3ef08d984b244c8d1476',cases=cases,coupled_runs=len(rows),source_only_runs=len(stiff),max_coupled_N=max(x['N'] for x in rows),max_coupled_E=max(x['E'] for x in rows),max_source_N=max(x['N'] for x in stiff),max_source_E=max(x['E'] for x in stiff),production_admission='HOLD',limitations='finite graph; near-equilibrium fallback is explicitly finite-precision heuristic; SSPRK2 scatter CFL remains; full Python suite not run this turn',files={p.name:sha(p) for p in D.iterdir() if p.is_file() and p.name not in ('ACCEPTANCE.json','verify.log')})
(D/'ACCEPTANCE.json').write_text(json.dumps(res,indent=2)+'\n');print({k:v for k,v in res.items() if k not in ('cases','files')})
