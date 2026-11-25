import json,hashlib,math
from pathlib import Path
D=Path(__file__).parent;H=Path('/home/cosmosapjw/Downloads')
def sha(p):
    with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
out={};rows=[];stiff=[]
for n in ('z900_actual','z1100_pulse','z1300_actual'):
    j=json.loads((D/(n+'.json')).read_text());old=json.loads((D.parent/'r118c2n_exact_extent'/(n+'.json')).read_text())
    assert int((D/(n+'.exit')).read_text())==0
    z=j['bath'];k=j['kind']
    for name,p in [('source_sha256',H/'rec_r118c2f_compiled_final'/(z+'.npz')),('rates_sha256',Path('archive/inputs/original_hyrec_oct2012/HyRec_Oct2012.zip')),('graph_sha256',H/'rec_r118c2k_refined'/z/'GRAPH128.npz'),('initial_state_sha256',H/'rec_r118c2k_refined'/z/f'n128_{k}_4.npz')]:
        assert sha(p)==j[name]==old[name]
    rr=j['rows'];ss=j['stiff'];assert len(rr)==6 and len(ss)==5
    assert all(x['status']=='PASS_SCOPED' and max(x['N'],x['E'])<1e-11 for x in rr)
    assert all(x['mprk22']['status']=='PASS_POSITIVE_CONSERVATIVE' and max(x['mprk22']['N'],x['mprk22']['E'])<1e-11 for x in ss)
    order=math.log2(rr[-2]['state_l1_over_gross']/rr[-1]['state_l1_over_gross']);assert 1.95<order<2.05
    out[n]=dict(last=rr[-1],order=order,ssprk2_last=old['rows'][-1],stiff=ss)
    rows+=rr;stiff+=ss
assert out['z900_actual']['stiff'][-1]['ssprk2']['status']=='REJECTED'
assert int((D/'regression.exit').read_text())==0 and '14 passed' in (D/'regression.log').read_text()
res=dict(status='PASS_SCOPED_MPRK22_FROZEN_GRAPH',parent='992449216a2a7638dc90b8e249d9afe42e761e38',coupled_runs=len(rows),scatter_only_runs=len(stiff),legacy_rejections=sum(x['ssprk2']['status']=='REJECTED' for x in stiff),max_coupled_N=max(x['N'] for x in rows),max_coupled_E=max(x['E'] for x in rows),max_linear_residual=max(x['mprk22']['linear_residual'] for x in stiff),cases=out,production_admission='HOLD',native_subagent='NOT_RUN',limitations='strictly positive donor domain; near-depletion convergence may require finer h; large-h positivity not accuracy; full Python suite not run',files={p.name:sha(p) for p in D.iterdir() if p.is_file() and p.name not in ('ACCEPTANCE.json','verify.log')})
(D/'ACCEPTANCE.json').write_text(json.dumps(res,indent=2)+'\n');print({k:v for k,v in res.items() if k not in ('files','cases')})
