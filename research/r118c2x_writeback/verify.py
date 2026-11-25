import hashlib,json
from pathlib import Path
import numpy as np
D=Path(__file__).resolve().parent;P=D.parent/'r118c2w_causal';G=Path('/home/cosmosapjw/Downloads/rec_r118c2w_full_local')
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
for n in ('green','writeback','face_audit','holdout','regression'):assert int((D/(n+'.exit')).read_text())==0
j=json.loads((D/'RESULTS.json').read_text());a=json.loads((D/'FACE_AUDIT.json').read_text());b=json.loads((D/'HOLDOUT.json').read_text());c=json.loads((P/'FULL_LOCAL.json').read_text())
assert j['status']=='SCOPED_CONSERVATIVE_WING_DEFECT_WRITEBACK' and sha(P/'FULL_128.npz')==j['full_sha']==c['full_sha']
assert sha(Path('archive/inputs/original_hyrec_oct2012/HyRec_Oct2012.zip'))==j['rates_sha']
assert sha(G/'GRAPH128.npz')==j['graph_sha']==c['raw_hashes']['GRAPH128.npz']
for n,h in b['hashes'].items():assert sha(Path(b['raw_path'])/n)==h
assert [r['edges'] for r in j['selected']]==[21520,27835]
old=np.load(P/'FULL_128.npz')
for r in j['cases']:
 n=r['case'];v=np.load(D/(n+'.npz'));assert np.array_equal(v['virtual'][:,:96],old['virtual_out'][:,:96])
 assert np.array_equal(v['lyman'][:,:96],old['lyman_out'][:,:96])
 assert len(r['rows'])==17 and all(x['residual']<2e-10 and x['root']<1e-8 for x in r['rows'])
 assert all(abs(x['q_number'])<1e-28 and abs(x['q_energy']+x['heat'])<1e-28 for x in r['rows'])
 assert r['terminal_x']==v['x'][-1] and r['terminal_T']==v['T'][-1]
 if n=='native':assert np.array_equal(v['x'],old['xHII'][:113]) and np.array_equal(v['virtual'],old['virtual_out'][:,:113])
 assert np.all(np.isfinite(v['virtual'])) and np.all((v['x']>0)&(v['x']<1)) and min(v['T'])>0
assert len(a['rows'])==10 and max(x['face_flux_relative'] for x in a['rows'])<1e-8
assert b['rhs_relative']<1e-4 and '25 passed' in (D/'regression.log').read_text()
out=dict(status='PASS_SCOPED_SELECTED_WING_DEFECT_CORRECTION',parent='6540dd31b6be5888d4689fcc3d7aaae312a7a8e8',results=j,face_audit=a,holdout=b,regression_tests=25,production_admission='HOLD_REPLACEMENT_OPACITY_AND_GLOBAL_DIFFUSION_MATCH',native_subagent='NOT_RUN')
(D/'ACCEPTANCE_CORE.json').write_text(json.dumps(out,indent=2)+'\n')
print(out['status'],'max face defect',max(x['face_flux_relative'] for x in a['rows']),'holdout rhs',b['rhs_relative'])
