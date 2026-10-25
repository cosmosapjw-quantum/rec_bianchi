"""Saved-array/scalar sign readback only; no matrix-vector products or solves."""
from pathlib import Path
from fractions import Fraction as F
import hashlib,json,math,os,resource
import numpy as np
D=Path(__file__).resolve().parent;U=D.parents[1];R=U/'results/primary001'
def ident(p):
 h=hashlib.sha256();n=0
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b);n+=len(b)
 return {'bytes':n,'sha256':h.hexdigest()}
def save(p,x):p.write_text(json.dumps(x,indent=2,sort_keys=True,allow_nan=False)+'\n')
# Recreate only the used file locators; no original code/source import.
paths=json.loads((U/'inputs/PATH_MANIFEST.json').read_text())['inputs'];used={f'input/{k}':Path(v['path']) if Path(v['path']).is_absolute() else U/v['path'] for k,v in paths.items()}
for folder in ('code','tests','vendor'):
 for p in sorted((U/folder).glob('*.py')):used[str(p.relative_to(U))]=p
used['inputs/PATH_MANIFEST.json']=U/'inputs/PATH_MANIFEST.json'
actual={k:ident(p) for k,p in used.items()};before=json.loads((U/'evidence/execution/primary001/HASHES_BEFORE.json').read_text());after=json.loads((U/'evidence/execution/primary001/HASHES_AFTER.json').read_text());expected=json.loads((U/'inputs/EXECUTION_IDENTITIES.json').read_text())['files']
identity={'used_file_count':len(actual),'equals_original_before':actual==before,'equals_original_after':actual==after,'equals_current_execution_manifest':actual==expected,'drift':{k:actual[k] for k in actual if actual[k]!=before.get(k)}}
assert all(identity[k] for k in ('equals_original_before','equals_original_after','equals_current_execution_manifest'))
coeff={}
with np.load(R/'EVENT_COMPOSITION.npz',allow_pickle=False) as z:
 for key in ('event_hat','endpoint_hat','query_hat'):
  a=z[key];coeff[key]={'shape':list(a.shape),'atomic_equals_exact_negated_radiation':bool(np.array_equal(a[4],-a[3]))}
 for prefix in ('event','endpoint','query'):
  lo=z[prefix+'_lo'];hi=z[prefix+'_hi'];coeff[prefix+'_interval']={'lower_atomic_equals_negated_radiation_upper':bool(np.array_equal(lo[4],-hi[3])),'upper_atomic_equals_negated_radiation_lower':bool(np.array_equal(hi[4],-lo[3]))}
ks=Path(paths['event_rows']['path'])
with np.load(ks,allow_pickle=False) as z:
 coeff['KS01_stored_rows']={'atomic_hat_exact_negative':bool(np.array_equal(z['atomic_hat'],-z['radiation_hat'])),'atomic_lo_exact_negative_rad_hi':bool(np.array_equal(z['atomic_lo'],-z['radiation_hi'])),'atomic_hi_exact_negative_rad_lo':bool(np.array_equal(z['atomic_hi'],-z['radiation_lo']))}
case_records=[]
for p in sorted(R.glob('CASE_*_OUTPUTS.npz')):
 record={'file':str(p.relative_to(U)),'saved_file_identity':ident(p),'scalars':{}}
 with np.load(p,allow_pickle=False) as z:
  for key in ('event_finite','event_tangent','event_remainder','event_explicit_tangent'):
   a=z[key];rad=float(a[3]);atom=float(a[4]);rf=F(rad);af=F(atom);s=rf+af;diff=rf-af;scale=max(abs(rf),abs(af),F(1,10**280));ulp=max(math.ulp(rad),math.ulp(atom));uf=F(ulp)
   record['scalars'][key]={'radiation_float':rad,'atomic_float':atom,'radiation_hex':rad.hex(),'atomic_hex':atom.hex(),'negated_radiation_hex':(-rad).hex(),'exact_fraction_radiation':str(rf),'exact_fraction_atomic':str(af),'exact_fraction_sum':str(s),'exact_fraction_radiation_minus_atomic':str(diff),'exact_fraction_atomic_minus_expected_neg_radiation':str(af-(-rf)),'exact_negative':atom==-rad,'relative_discrepancy':float(abs(s)/scale),'ulp_scale':ulp,'absolute_discrepancy_in_max_ULPs':float(abs(s)/uf) if uf else None,'both_exact_zero':rad==0 and atom==0}
 case_records.append(record)
coeff_pass=all(all(v for k,v in item.items() if k!='shape') for item in coeff.values())
original_mismatch=sum(not case['scalars'][key]['exact_negative'] for case in case_records for key in ('event_finite','event_tangent','event_remainder'))
x={'schema':'PB01_EVENT_SIGN_SAVED_EVIDENCE_DIAGNOSIS_V1','status':'EXACT_COEFFICIENT_NEGATIVES_WITH_DIFFERENT_POINT_OUTPUT_ROUNDINGS' if coeff_pass and original_mismatch else 'RETURN_TO_ROOT','input_identity':identity,'coefficient_sign_checks':coeff,'case_count':len(case_records),'original_checked_scalar_pair_mismatches':original_mismatch,'independent_explicit_tangent_pair_mismatches':sum(not c['scalars']['event_explicit_tangent']['exact_negative'] for c in case_records),'interpretation':'Coefficients and paired interval endpoints are exact sign partners. The saved independent five-row matrix-vector point outputs do not always retain bitwise sign pairing; their exact Fraction residuals are reported. No BLAS action was rerun and no claim about a particular internal BLAS kernel is made. Coupled-sign repair is not performed.','new_operator_actions':0,'new_event_actions':0,'new_matvec':0,'new_solves':0,'source_modules_imported':0,'repair_performed':False,'RLIMIT_CPU':list(resource.getrlimit(resource.RLIMIT_CPU)),'RLIMIT_AS':list(resource.getrlimit(resource.RLIMIT_AS)),'thread_environment':{k:os.environ.get(k) for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','BLIS_NUM_THREADS')},'cases':case_records}
save(D/'DIAGNOSTIC.json',x);print(json.dumps({'status':x['status'],'cases':len(case_records),'original_scalar_mismatches':original_mismatch,'coefficient_signs_all_exact':coeff_pass,'used_identity_count':len(actual),'all_identity_equal':actual==before==after==expected,'new_matvec':0}))
