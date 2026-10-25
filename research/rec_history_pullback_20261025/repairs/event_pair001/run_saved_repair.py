"""One authorized saved-data sign repair; no matvec, source solve or replay."""
from pathlib import Path
from fractions import Fraction as F
import hashlib,json,sys,traceback,resource,os
import numpy as np
D=Path(__file__).resolve().parent;U=D.parents[1];R=U/'results/primary001';H=U/'evidence/implementation_history/event_pair001'
sys.path.insert(0,str(U/'code'))
from event_pair import canonicalize_shared_event
COUNT=0

def save(p,x):p.write_text(json.dumps(x,indent=2,sort_keys=True,allow_nan=False)+'\n')
def ident(p):
 h=hashlib.sha256();n=0
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b);n+=len(b)
 return {'bytes':n,'sha256':h.hexdigest()}
def metric(a,b):
 a=float(a);b=float(b);error=abs(a-b);scale=max(abs(a),abs(b),1e-280);return {'absolute_error':error,'scale':scale,'normalized_error':error/scale,'pass':error/scale<=2e-12}
def original_identity():
 oldmanifest=json.loads((H/'EXECUTION_IDENTITIES.json').read_text())['files'];paths=json.loads((H/'PATH_MANIFEST.json').read_text())['inputs'];used={}
 for key in oldmanifest:
  if key.startswith('input/'):used[key]=Path(paths[key[6:]]['path'])
  elif key=='code/primary.py':used[key]=H/'primary.py'
  elif key=='inputs/PATH_MANIFEST.json':used[key]=H/'PATH_MANIFEST.json'
  else:used[key]=U/key
 actual={k:ident(p) for k,p in used.items()};before=json.loads((U/'evidence/execution/primary001/HASHES_BEFORE.json').read_text());after=json.loads((U/'evidence/execution/primary001/HASHES_AFTER.json').read_text())
 if actual!=oldmanifest or actual!=before or actual!=after:raise ValueError('PRESERVED_ORIGINAL18_IDENTITY_MISMATCH')
 return {'count':len(actual),'preserved_original18_equals_original_before_after':True,'primary_binding':'preserved bc63 source copy; live future primary source is authorized patched version'}

def main():
 global COUNT
 auth=json.loads((U/'evidence/EVENT_PAIR_REPAIR_AUTHORIZATION.json').read_text());assert auth['failure']=='PB01-EVENT-PAIR-001' and auth['new_matvecs']==0
 original=json.loads((R/'SUMMARY.json').read_text());assert original['status']=='FAILED_FROZEN_CRITERION'
 identity=original_identity();save(D/'ORIGINAL18_IDENTITY.json',identity)
 diag=json.loads((U/'diagnostics/event_sign001/DIAGNOSTIC.json').read_text());assert diag['status']=='EXACT_COEFFICIENT_NEGATIVES_WITH_DIFFERENT_POINT_OUTPUT_ROUNDINGS'
 assert all(all(v for key,v in item.items() if key!='shape') for item in diag['coefficient_sign_checks'].values())
 originals=json.loads((R/'FINITE_CASES.json').read_text());assert len(originals)==8
 records=[];all_first4=True
 for old in originals:
  tag=f"d{old['direction']}_t{old['t']:g}";source=R/f'CASE_{tag}_OUTPUTS.npz';paired={};independent={};details={}
  with np.load(source,allow_pickle=False) as z:
   for key in ('event_finite','event_tangent','event_remainder','event_explicit_tangent'):
    value=z[key].copy();independent[key]=value;COUNT+=1
    save(D/'SIGN_ASSIGNMENT_COUNTER.json',{'phase':'BEFORE_SHARED_EVENT_ASSIGNMENT','sign_assignments_charged':COUNT,'sign_assignment_cap':32,'current_case':tag,'current_vector':key,'new_matvecs':0,'new_operator_actions':0,'new_event_actions':0})
    canon=canonicalize_shared_event(value);first4=canon[:4].tobytes()==value[:4].tobytes();exact_pair=canon[4].tobytes()==np.negative(canon[3]).tobytes();assert first4 and exact_pair;all_first4=all_first4 and first4
    paired[key]=canon
    details[key]={'first_four_bytes_unchanged':first4,'radiation_hex':float(value[3]).hex(),'independent_atomic_hex':float(value[4]).hex(),'canonical_atomic_hex':float(canon[4]).hex(),'independent_exact_sum':str(F(float(value[3]))+F(float(value[4]))),'canonical_exact_sum':str(F(float(canon[3]))+F(float(canon[4]))),'atomic_change_exact':str(F(float(canon[4]))-F(float(value[4]))),'canonical_exact_sign_pair':exact_pair}
    np.savez(D/f'PAIR_{tag}_{key}.npz',independent=value,canonical=canon)
    save(D/f'PAIR_{tag}_{key}.json',details[key])
  rawmetrics={name:metric(independent['event_tangent'][i],independent['event_explicit_tangent'][i]) for i,name in enumerate(('F','proper','number','radiation','atomic'))};metrics={name:metric(paired['event_tangent'][i],paired['event_explicit_tangent'][i]) for i,name in enumerate(('F','proper','number','radiation','atomic'))}
  retained={'bridge_pass':old['bridge_pass'],'chart_finite_box_contained':old['chart_finite_box_contained'],'native_numerical_probe_box_contained':old['native_numerical_probe_box_contained'],'exact_fraction_identity':old['exact_fraction_identity']=='PASS'}
  case={'direction':old['direction'],'t':old['t'],'original_primary_pass':old['pass'],'original_event_sign_pair':old['event_sign_pair'],'original_metrics':rawmetrics,'canonical_metrics':metrics,'same_tolerance':2e-12,'retained_unrelated_criteria':retained,'all_four_canonical_pairs':all(v['canonical_exact_sign_pair'] for v in details.values()),'all_four_first4_bytes_unchanged':all(v['first_four_bytes_unchanged'] for v in details.values()),'vector_details':details}
  case['repair_pass']=all(retained.values()) and case['all_four_canonical_pairs'] and case['all_four_first4_bytes_unchanged'] and all(v['pass'] for v in metrics.values());records.append(case);save(D/f'CASE_{tag}_REPAIR.json',case);save(D/'REPAIRED_CASES.json',records)
 assert COUNT==32
 inherited={k:original[k] for k in ('identity_pass','derivative_adjoint_pass','query_interval_pass','event_sign_pair','taylor_nonfloor_orders_pass','source_route_permutation')};assert all(inherited.values()) and original['exact_toy_controls']=='PASS' and max(original['taylor_nonfloor_ratios'].values())>=2
 summary={'schema':'PB01_SAVED_DATA_EVENT_PAIR_REPAIR_V1','status':'PASS_SAVED_DATA_SHARED_EVENT_REPAIR' if all(x['repair_pass'] for x in records) and all_first4 else 'FAILED_SAVED_DATA_REPAIR','original_primary_status':original['status'],'original_primary_exit_code':2,'original_primary_raw_preserved':True,'repaired_cases':len(records),'all_cases_pass':all(x['repair_pass'] for x in records),'sign_assignments':COUNT,'first_four_bytes_unchanged':all_first4,'reused_unrelated_primary_criteria':inherited,'reused_exact_toy_controls':original['exact_toy_controls'],'reused_taylor_nonfloor_ratios':original['taylor_nonfloor_ratios'],'coefficient_interval_exact_sign_pair':'REUSED_DIAGNOSTIC_PASS_SAME_IMMUTABLE_RAW','event_tolerance_unchanged':2e-12,'new_matvecs':0,'new_operator_actions':0,'new_event_actions':0,'new_RHS':0,'solves':0,'inverses':0,'primary_rerun':False,'native':0,'IVP':0,'physical_epsilon':None,'physical_outgoing_bound':None,'root_independent_final_admission':'PENDING','RLIMIT_CPU':list(resource.getrlimit(resource.RLIMIT_CPU)),'RLIMIT_AS':list(resource.getrlimit(resource.RLIMIT_AS)),'thread_environment':{k:os.environ.get(k) for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','BLIS_NUM_THREADS')}}
 save(D/'ACCEPTED_SUMMARY.json',summary);save(D/'SIGN_ASSIGNMENT_COUNTER.json',{'phase':'COMPLETE','sign_assignments':COUNT,'new_matvecs':0,'new_operator_actions':0,'new_event_actions':0});print(json.dumps(summary));return 0 if summary['status'].startswith('PASS_') else 2
try:rc=main()
except BaseException as e:
 save(D/'EXCEPTION.json',{'type':type(e).__name__,'message':str(e),'traceback':traceback.format_exc(),'sign_assignments':COUNT});traceback.print_exc();rc=1
sys.exit(rc)
