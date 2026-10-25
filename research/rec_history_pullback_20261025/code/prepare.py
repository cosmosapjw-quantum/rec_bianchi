"""Preparation only: used-file byte manifests and py_compile; no NumPy import."""
import hashlib,json,py_compile,zipfile
from pathlib import Path
UNIT=Path(__file__).resolve().parents[1];WORK=UNIT.parents[1];INTAKE=WORK/'intake/EXACT_LOCAL_FILES.json'
def ident(p):
 h=hashlib.sha256();size=0
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b);size+=len(b)
 return {'bytes':size,'sha256':h.hexdigest()}
def save(p,x):p.write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')
def main():
 intake=json.loads(INTAKE.read_text())['files'];mapping={'history':'original_full_history','point_K':'KS01_stable_K_candidates','K_intervals':'KS01_K_certificate_arrays','event_rows':'KS01_event_response','accepted_queries':'KS01_accepted_history_witness'};inputs={}
 for key,role in mapping.items():
  item=intake[role];path=Path(item['path']);expected={k:item[k] for k in ('bytes','sha256')}
  if ident(path)!=expected:raise ValueError('ACCEPTED_INPUT_CHANGED:'+role)
  inputs[key]={'path':str(path),'expected_identity':expected,'intake_role':role}
 ks=Path(inputs['point_K']['path']).parents[2];cert=ks/'results/primary001/CERTIFICATE.json'
 oldwork=ks.parents[1];archive=oldwork/'delivery/REC_HISTORY_KS01_S2_20261025_3a67f3e1e40d.zip'
 with zipfile.ZipFile(archive) as z:
  manifest=json.loads(z.read('PAYLOAD_MANIFEST.json'));record=next(x for x in manifest['files'] if x['path']=='research/rec_history_ks_20261025/results/primary001/CERTIFICATE.json')
 expected={k:record[k] for k in ('bytes','sha256')}
 if ident(cert)!=expected:raise ValueError('ACCEPTED_K_CERTIFICATE_CHANGED')
 inputs['K_certificate']={'path':str(cert),'expected_identity':expected,'provenance':'immutable KS01 S2 manifest entry'}
 native=UNIT/'vendor/history_boundary.py';native_expected={k:intake['retained_history_scalar_adapter'][k] for k in ('bytes','sha256')}
 if ident(native)!=native_expected:raise ValueError('NATIVE_VENDOR_BYTE_IDENTITY')
 if ident(UNIT/'vendor/interval.py')['sha256']!='e5b7d9aa94b49234de626672ca1c0e7db694e38885fb40c478880d2f2b904250':raise ValueError('INTERVAL_VENDOR_IDENTITY')
 save(UNIT/'inputs/PATH_MANIFEST.json',{'schema':'PB01_USED_INPUT_PATHS_V1','inputs':inputs,'relocation':'Paths may be supplied by editing this preparation manifest before a new authorized freeze. Raw bytes must match accepted identities. Input paths are not physical metadata.','native_vendor_original_identity':native_expected,'no_source_rebuild_or_solve':True})
 files={f'input/{k}':ident(Path(item['path'])) for k,item in inputs.items()}
 for d in ('code','tests','vendor'):
  for p in sorted((UNIT/d).glob('*.py')):py_compile.compile(str(p),doraise=True);files[str(p.relative_to(UNIT))]=ident(p)
 files['inputs/PATH_MANIFEST.json']=ident(UNIT/'inputs/PATH_MANIFEST.json')
 save(UNIT/'inputs/EXECUTION_IDENTITIES.json',{'schema':'PB01_USED_INPUT_CODE_IDENTITIES_V1','files':files,'requested_model':'gpt-6.1-sol','observed_model':None,'scientific_execution':0})
 save(UNIT/'BUDGET_LEDGER_PENDING.json',{'status':'PREPARED_NOT_RUN','unit_cap_cpu_seconds':50,'unit_cap_wall_seconds':150,'primary_cpu_cap':30,'primary_wall_cap':90,'figures_cpu_cap':10,'figures_wall_cap':30,'reserved_targeted_repair_cpu':5,'reserved_targeted_repair_wall':15,'review_diagnostic_cpu':5,'review_diagnostic_wall':15,'threads':1,'address_space_cap_bytes':1073741824,'operator_action_cap':256,'event_action_cap':512,'linear_RHS':0,'solves':0,'inverses':0,'native':0,'IVP':0,'scientific_execution':0,'known_inherited_accounted_cpu_seconds':32.168987486,'older_costs':'UNKNOWN','preparation_provider_IO_fullturn_remoteCAS':'SEPARATE_UNKNOWN_NOT_ZERO','remaining_budget_is_not_authorization':True})
 print('Prepared used identities and syntax only; scientific execution0.')
if __name__=='__main__':main()
