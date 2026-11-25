import json, pathlib, hashlib, re, shutil
D=pathlib.Path(__file__).resolve().parent
H=pathlib.Path.home()/'Downloads'
R=H/'rec_r118c2j_exterior_final'
S=json.loads((R/'SOURCES.json').read_text())
C=json.loads((R/'RESULTS.json').read_text())
F=json.loads((H/'rec_r118c2j_hat_refine/REFINEMENT.json').read_text())
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
assert len(S)==6 and len(C['cases'])==22 and len(F)==36
assert len({x['case'] for x in C['cases']})==22
for x in C['cases']:
 assert x['max_N']<1e-7 and x['max_E']<1e-6
 for name,digest in x['hashes'].items():
  assert sha(R/x['case']/name)==digest,(x['case'],name)
for x in S:
 assert len(x['production'])==len(x['reference'])==6
 assert x['quadrature_L1']<1e-7 and x['thermal_null']<1e-12
 assert x['proxy_weighted_null_residual']>1e-3
 assert all(v['sign_match'] for v in x['continuum'].values())
 assert all(v['relative']>1 for v in x['continuum'].values())
for bath in ('z900','z1100','z1300'):
 for lane in ('production','reference'):
  q=sorted([x for x in F if x['bath']==bath and x['lane']==lane],key=lambda x:x['subcells'])
  assert len(q)==6 and all(a['projected_error']>b['projected_error'] for a,b in zip(q,q[1:]))
  assert q[-1]['projected_error']<.001
  assert max(x['max_marginal'] for x in q)<1e-11
for name,src in [('SOURCES.json',R/'SOURCES.json'),('RESULTS.json',R/'RESULTS.json'),('REFINEMENT.json',H/'rec_r118c2j_hat_refine/REFINEMENT.json')]:
 shutil.copyfile(src,D/name)
logs={}
for name in ['rec_python','rec_rust','rec_red','rec_green','rec_registry_trial','rec_run_initial','rec_run_final','hat_refine']:
 p=pathlib.Path('/tmp/r118c2j_'+name+'.log')
 if p.exists():
  import gzip
  b=gzip.compress(p.read_bytes(),mtime=0);(D/(name+'.log.gz')).write_bytes(b)
  logs[name]=sha(D/(name+'.log.gz'))
rt=pathlib.Path('/tmp/r118c2j_rec_rust.log').read_text()
assert not re.search(r'test result: FAILED',rt)
n=sum(map(int,re.findall(r'test result: ok\. (\d+) passed',rt)))
assert '14 passed' in pathlib.Path('/tmp/r118c2j_rec_python.log').read_text()
A=dict(status='PASS_SCOPED',scientific_admission='POINT_CLOSURE_HEATING_REJECTED',parent='eeb314d80cc71bb55f400f836de6a83b045144ad',cases=len(C['cases']),steps=sum(x['steps'] for x in C['cases']),max_N=max(x['max_N'] for x in C['cases']),max_E=max(x['max_E'] for x in C['cases']),max_quad=max(x['quadrature_L1'] for x in S),proxy_obstruction=[min(x['proxy_weighted_null_residual'] for x in S),max(x['proxy_weighted_null_residual'] for x in S)],point_error_range=[min(v['relative'] for x in S for v in x['continuum'].values()),max(v['relative'] for x in S for v in x['continuum'].values())],hat128_max=max(x['projected_error'] for x in F if x['subcells']==128),rust_tests=n,python_tests=14,raw_paths=[str(R),str(H/'rec_r118c2j_hat_refine')],logs=logs,files={p.name:sha(p) for p in sorted(D.glob('*.json')) if p.name!='ACCEPTANCE.json'},limitations=['refined action only, not refined dynamic 2s graph','six selected blocks only; fixed bath; full owner swap HOLD'])
(D/'ACCEPTANCE.json').write_text(json.dumps(A,indent=2)+'\n')
print(json.dumps(A,indent=2))
