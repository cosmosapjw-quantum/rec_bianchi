import json,math,hashlib
from pathlib import Path
D=Path(__file__).parent
cases={}; all_rows=[]
for p in sorted(D.glob('z*.json')):
    j=json.loads(p.read_text());rows=j['rows'];assert len(rows)==10 and j['n']==128 and j['physical_duration_s']==.1
    assert j['reference_state_max_diff']<3e-18
    a=[v for v in rows if v['method']=='BE+SSP2'];b=[v for v in rows if v['method']=='midpoint+SSP2'];assert [v['steps'] for v in a]==[1,2,4,8,16]==[v['steps'] for v in b]
    assert max(max(v['N'],v['E'],v['event_residual']) for v in rows)<1e-11
    if j['kind']!='thermal':
        p0=[math.log2(x['delta_n2_rel']/y['delta_n2_rel']) for x,y in zip(a,a[1:])];p1=[math.log2(x['delta_n2_rel']/y['delta_n2_rel']) for x,y in zip(b,b[1:])];assert min(p0)>.9 and max(p0)<1.1 and min(p1)>1.95 and max(p1)<2.05 and b[-1]['delta_n2_rel']<1e-8
    else:
        p0=p1=None;assert max(v['state_l1_over_gross'] for v in rows)<1e-18
    cases[p.stem]=dict(order_BE=p0,order_midpoint=p1,BE16=a[-1]['delta_n2_rel'],midpoint16=b[-1]['delta_n2_rel'],ref_delta_n2=j['reference_delta_n2'],ref_max_diff=j['reference_state_max_diff'],midpoint16_state_l1_over_gross=b[-1]['state_l1_over_gross'],midpoint16_abs_n2_error=abs(b[-1]['delta_n2']-j['reference_delta_n2']))
    all_rows+=rows
assert len(cases)==5 and len(all_rows)==50
out=dict(status='PASS_SCOPED_FROZEN_GRAPH',parent='91df4b2a3ddcd86a9319823061ab3d580866c62d',cases=cases,runs=len(all_rows),max_N=max(v['N'] for v in all_rows),max_E=max(v['E'] for v in all_rows),max_event_residual=max(v['event_residual'] for v in all_rows),production_owner_swap='HOLD',unconditional_positivity='FALSE',tests_log=(D/'tests.log').read_text().strip(),files={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(D.iterdir()) if p.is_file() and p.name not in ('ACCEPTANCE.json','verify.log')})
(D/'ACCEPTANCE.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items() if k!='files'},indent=2))
