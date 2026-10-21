import json,math,sys,hashlib
from pathlib import Path
import pilot
run=Path(sys.argv[1]);out=Path(sys.argv[2]);out.mkdir(exist_ok=False)
root=run/'donor'/pilot.ROOT_NAME
if len(sys.argv)>3:
 reference=json.loads(Path(sys.argv[3]).read_text()); new_controls=0
else:
 pilot.init_worker(root,out/'leases',caches=False)
 reference=pilot.physics_case({'signed_sigma':.002,'signed_pi':.0004},16); new_controls=1
saved=json.loads((run/'case_024/result.json').read_text())
# Entire deterministic physics payload, not CPU/wall metadata.
# JSON preserves binary64 values here but maps donor tuple containers to lists.
# Compare the declared JSON content relation, without numerical tolerances.
assert json.loads(json.dumps(reference,allow_nan=False))==saved,'CACHE_OVERLAY_CHANGED_PHYSICAL_OUTPUT'
allr=[json.loads(p.read_text()) for p in sorted(run.glob('case_*/result.json'))]
maxs=max(abs(r['initial_normalized']['signed_sigma_frobenius']-r['case']['signed_sigma']) for r in allr)
maxp=max(abs(r['initial_normalized']['signed_pi_frobenius']-r['case']['signed_pi']) for r in allr)
assert max(maxs,maxp)<3e-16
for r in allr:
 assert -1<=r['initial_A']<=2
 assert len(r['history'])==16
 assert all(0<=q['x_HII']<=1 and 0<=q['x_HeII']<=1 and 10000<=q['Tgas_K']<=24000 for q in r['history'])
 assert all(abs(q['Sigma_frobenius']-math.sqrt(2)*q['Sigma'])<1e-15 for q in r['history'])
 # Source pressure sum before norm, never sum of separate norms.
 assert all(abs(q['Pi_total_source']-sum(q[k] for k in ('Pi_gamma','Pi_nu','Pi_massive','Pi_UV')))<1e-25 for q in r['history'])
obj={'status':'PASS_SCOPED_SERIAL','native_subagent':'NOT_RUN','new_correctness_control_runs':new_controls,'earlier_control_attempts':2,'new_benchmarks':0,
 'cached_vs_original_entire_physics_payload_equal':True,'initial_target_max_abs':{'Sigma':maxs,'Pi':maxp},
 'cases':len(allr),'history_rows':sum(len(r['history']) for r in allr),
 'max_number_ledger_perH':max(r['errors']['photochemical_number_abs_max'] for r in allr),
 'max_energy_ledger_eV_perH':max(r['errors']['photochemical_energy_eV_H_abs_max'] for r in allr),
 'global_Qa':'NOT_CLOSED','numerical_convergence_new_sweep':'NOT_ESTABLISHED',
 'performance_acceleration':'NOT_MEASURED','scope':'short warm LRS C15 only'}
pilot.write_new(out/'VALIDATION.json',obj)
pilot.write_new(out/'ORIGINAL_CONTROL.json',reference)
print(json.dumps(obj,indent=2))
