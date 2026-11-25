"""Evidence verification for the REC-independent bounded C2F path."""
import pathlib,json,hashlib,gzip,re,sys,numpy as np
d=pathlib.Path(__file__).resolve().parent
read=lambda p:json.loads((d/p).read_text())
sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
s=read('STATES.json');c=read('COMPILE_RESULTS.json');r=read('LIVE_RESULTS.json');h=read('OWNED_HISTORY.json');i=read('ISOLATION.json');p=read('SOURCE_RECEIPT.json');a=read('ANCHOR_PARITY.json')
assert set(s['states'])=={'z1300','z1100','z900'}
for name,q in s['states'].items():
 assert abs(q['x_1s']+q['x_2s']+q['x_2p']+q['x_HII']-1)<2e-14
 assert q['qss_relative_residual']<2e-12 and q['n_1s_m3']==q['n_H_m3']*q['x_1s']
 hh=json.loads(gzip.decompress((d/(name+'_HISTORY.json.gz')).read_bytes()))
 assert hh['history_owner']=='REC_BIANCHI' and not hh['external_history'] and not hh['external_hyrec_runtime']
 assert hh['states'][-1]==q
assert max(s['tighter_bdf_saha_relative'].values())<2e-8
assert len(c)==4 and all(x['max_marginal']<2e-12 and x['max_same_sym']<2e-12 for x in c)
for x in c:
 q=d/(x['case']+'.npz');assert sha(q)==x['source_sha256']
 with np.load(q) as z:
  assert z['pairs'].shape==(459,2)
  for n in (1,4):
   v=z[f'Q{n}'];assert v.shape==(459,n+1,n+1) and np.min(v)>=0 and np.all(np.isfinite(v))
assert max(x['normalized_gap'] for x in a.values())<2e-12
cs=r['cases'];b={q['case']:q for q in cs}
assert len(b)==len(cs)==65 and all(q['status']=='PASS_SCOPED' and q['returncode']==0 for q in cs)
assert sum(q['steps'] for q in cs)==209
assert r['binary_sha256']==p['live_binary_sha256']==i['binary_sha256']
keys=('number_defect','centered_balance_defect','max_be_residual','max_be_number_defect','max_be_centered_defect','max_drift_number','max_drift_centered','max_zone_centered','max_zone_number','partition_number','partition_X','max_iterations')
mx={k:max(q['run'][k] for q in cs) for k in keys}
assert mx['number_defect']<2e-12 and mx['centered_balance_defect']<2e-12
assert mx['max_be_residual']<=2e-11 and mx['max_be_number_defect']<2e-12
assert all(q['run']['min_occupation']>=0 for q in cs)
assert max(mx[k] for k in keys[5:-1])<2e-12
thermal=[q for q in cs if q['kind'] in ('thermal','high_eq')]
assert max(abs(q['metrics']['centered_rate_per_photon']) for q in thermal)<2e-17
live=[q for q in cs if q['drift']];assert len(live)==10
reverse=[q for q in live if q['case'].startswith('live_reverse')]
assert len(reverse)==4 and all(min(q['run'][k] for k in ('red_in','red_out','blue_in','blue_out'))>0 for q in reverse)
assert all(q['run']['interface_atom_heat']==0 for q in live)
physical=[q for q in live if q['case'].startswith('live_physical')]
assert len(physical)==6 and all(q['run']['red_out']>0 and q['run']['blue_in']>0 for q in physical)
seq=[b[f'time_{n}']['metrics']['ode_signal_l1'] for n in (1,2,4,8,16,32)];ratios=[x/y for x,y in zip(seq,seq[1:])]
assert all(1.7<x<2.1 for x in ratios)
assert i['status']=='PASS_ISOLATED_INPUT_TREE' and i['source_state']==s['states']['z1100']
assert set(i['table_members'])=={'HyRec/Alpha_inf.dat','HyRec/R_inf.dat','HyRec/two_photon_tables.dat'}
hs=h['cases'];assert len(hs)==12 and sum(x['steps'] for x in hs)==5760
assert h['binary_sha256']==p['history_binary_sha256']
assert max(q['max_residual'] for q in hs)<2e-10
def count(name):
 t=gzip.decompress((d/'logs'/name).read_bytes()).decode();q=re.findall(r'test result: (\w+)\. (\d+) passed; (\d+) failed;',t)
 assert q and all(x=='ok' and int(z)==0 for x,y,z in q);return sum(int(y) for x,y,z in q)
assert count('rec_all.log.gz')==145 and count('rec_examples.log.gz')==0
assert '25 passed, 2 deselected' in gzip.decompress((d/'logs/py_regression.log.gz').read_bytes()).decode()
if '--raw' in sys.argv:
 for path,digest in p['sources'].items():assert sha(path)==digest
 for q in a.values():assert sha(q['source_path'])==q['source_sha256']
 for q in cs:
  exe,gp,case,out=q['command'];assert sha(exe)==r['binary_sha256'] and sha(gp)==q['graph_sha256'] and sha(case)==q['case_sha256']
  for name,digest in q['hashes'].items():assert sha(pathlib.Path(out)/name)==digest
 for q in hs:assert sha(q['command'][0])==h['binary_sha256'] and sha(q['path'])==q['sha256']
 root=pathlib.Path(p['raw_root'])/'rec_r118c2f_isolated'
 assert sha(root/'atomic_rates.zip')==i['table_archive_sha256'] and sha(root/'result/RECEIPT.json')==i['result_receipt_sha256']
 for name,digest in i['result_hashes'].items():assert sha(root/'result'/name)==digest
result=dict(research_id='R118-C2F-SOURCE-STATE-CALIBRATED-LIVE-RESONANCE-EVOLUTION-01',status='IMPLEMENTATION_VERIFIED_SCOPED',runtime_independence='PASS_ISOLATED_HMLA_AND_SCALAR_LIVE_LINE',full_recombination_status='UNRESOLVED_FULL_INTERIOR_EXTERIOR_ATOMIC_OWNERSHIP',feedback_status='BLOCKED_NO_SELF_CONSISTENT_POPULATION_LINE_THERMAL_COUPLING',science_promotion=False,states=s,source_compilation=c,source_parity=a,live_cases=65,live_steps=209,metrics_max=mx,thermal_null_per_photon_max=max(abs(q['metrics']['centered_rate_per_photon']) for q in thermal),time_signal_errors=seq,time_ratios=ratios,live=[dict(case=q['case'],metrics=q['metrics'],run=q['run']) for q in live],source_action_checks=[dict(case=q['case'],metrics=q['metrics']) for q in cs if 'continuum_error' in q['metrics'] and q['dt']==0],isolation=i,owned_history_cases=12,owned_history_steps=5760,owned_history=hs,rec_rust_tests=145,python_tests=25,provenance=p,next_id='R118-C2G-REC-OWNED-ANGULAR-LINE-AND-ATOMIC-OWNERSHIP-01')
result['receipt_sha256']={str(f.relative_to(d)):sha(f) for f in sorted(d.rglob('*')) if f.is_file() and f.name!='ACCEPTANCE.json' and '__pycache__' not in str(f)}
(d/'ACCEPTANCE.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
print('VERIFIED',result['status'],len(cs),'live cases',len(hs),'owned histories',result['runtime_independence'],mx)
