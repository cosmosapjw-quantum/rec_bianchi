import json,hashlib
from pathlib import Path
D=Path(__file__).resolve().parent;P=D.parent/'r118c2w_causal';G=Path('/home/cosmosapjw/Downloads/rec_r118c2w_full_local');R=Path('archive/inputs/original_hyrec_oct2012/HyRec_Oct2012.zip')
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def j(p):return json.loads(Path(p).read_text())
for n in ('green','run','evolve','lumpability','regression'):assert int((D/(n+'.exit')).read_text())==0,n
assert '29 passed' in (D/'regression.log').read_text()
a=j(D/'RESULTS.json');b=j(D/'EVOLUTION.json');c=j(D/'LUMPABILITY.json')
assert a['full_sha']==sha(P/'FULL_128.npz') and a['graph_sha']==sha(G/'GRAPH128.npz') and a['rates_sha']==sha(R)
for path,h in a['source_hashes'].items():assert sha(path)==h==b['source_hashes'][path]
assert len(a['summary'])==14 and len(a['rows'])==630 and len(b['rows'])==36
assert max(x['energy_vector_defect'] for x in a['summary'])<1e-14
assert max(x['max_refined'] for x in a['summary'] if x['level']==0)<1e-10
assert max(x['max_native'] for x in a['summary'] if x['level']==32)<1e-4
assert max(x['max_energy'] for x in a['summary'])<1e-12
assert len(c['rows'])==2 and all(x['duplicate_groups']==14 for x in c['rows'])
assert max(max(x['eigen_reference_relative']) for x in c['rows'])<1e-8
assert all(x['max_lumpability_defect']>.9 for x in c['rows'])
out=dict(status='PASS_SCOPED_REFINED_STATIC_AND_LABELLED_DYNAMICS',parent='4c1dcf2b537e0615b6b5eca7b48f3ca1951842c3',static=a,evolution=b,lumpability=c,regression_tests=29,production_admission='HOLD_REFINED_FULL_OPACITY_AND_DYNAMIC_MODE_IDENTITY',native_subagent='NOT_RUN')
(D/'ACCEPTANCE_CORE.json').write_text(json.dumps(out,indent=2)+'\n');print(out['status'],'samples',len(a['rows']),'dynamic',len(b['rows']))
