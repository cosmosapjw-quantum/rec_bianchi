"""Authorized targeted resume: reuse36source+25map rows; no whole rerun."""
from __future__ import annotations
import argparse
from collections import Counter
from datetime import datetime, timezone
import difflib
import hashlib
import json
import math
from pathlib import Path
import time
import traceback
import numpy as np
import line_source as model
import run_line01 as run

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_NEW = {'local_map_rows':2,'direct_comparisons':6,'finite_reference_roots':2,
                'plot_tracks':3,'plot_map_outputs':243,'invalid_input_checks':18}


def read_rows(path):
    return [json.loads(line) for line in path.read_text().splitlines()]


def run_resume():
    parser=argparse.ArgumentParser()
    parser.add_argument('--execute',action='store_true')
    args=parser.parse_args()
    if not args.execute:
        parser.error('Explicit parent targeted-resume authorization required')
    old=ROOT/'results/attempt001'
    old_metrics=json.loads((old/'METRICS.json').read_text())
    if old_metrics['status']!='FAIL' or old_metrics['counts']!={'source_rows':36,'local_map_rows':25}:
        raise ValueError('Unexpected original attempt state; no automatic resume')
    old_manifest=json.loads((old/'RAW_MANIFEST.json').read_text())
    for entry in old_manifest['files']:
        p=ROOT/entry['path']
        if p.stat().st_size!=entry['bytes'] or run.sha(p)!=entry['sha256']:
            raise ValueError('Original failed evidence changed: '+str(p))
    original_code=json.loads((ROOT/'evidence/attempt001_code/SHA256.json').read_text())
    for fn,entry in original_code['files'].items():
        if run.sha(ROOT/'evidence/attempt001_code'/fn)!=entry['sha256']:
            raise ValueError('Pre-fix source bytes changed')
    folder=ROOT/'results/resume001'
    folder.mkdir(parents=True,exist_ok=False)
    before=ROOT/'evidence/attempt001_code/line_source.py'
    after=ROOT/'code/line_source.py'
    diff=''.join(difflib.unified_diff(before.read_text().splitlines(keepends=True),
        after.read_text().splitlines(keepends=True),fromfile='attempt001/line_source.py',
        tofile='resume001/line_source.py'))
    with (folder/'CODE_PATCH.diff').open('x') as f:f.write(diff)
    run.dump(folder/'START.json',{'schema':'line01.targeted_resume.v1',
        'utc':datetime.now(timezone.utc).isoformat(),
        'reason':'Outward1ULP endpoint rounding for native z0 below ulp(omega); formulas/tolerances unchanged',
        'parent_authorized':True,'original_status':'FAIL_RETAINED',
        'original_raw_manifest_sha256':run.sha(old/'RAW_MANIFEST.json'),
        'original_files_verified_unchanged':len(old_manifest['files']),
        'original_code_preserved':'evidence/attempt001_code/',
        'core_pre_sha256':run.sha(before),'core_post_sha256':run.sha(after),
        'code_sha256':{str(p.relative_to(ROOT)):run.sha(p) for p in sorted((ROOT/'code').glob('*.py'))},
        'reused_completed_rows':{'source_rows':36,'local_map_rows':25},
        'planned_new_rows':EXPECTED_NEW,'source_formula_change':False,'tolerance_change':False,
        'whole_campaign_rerun':False})
    prior_checks=json.loads((old/'ACCEPTANCE.json').read_text())['checks']
    run.ACCEPTANCE.extend(prior_checks)
    run.OBSERVED.update(old_metrics['counts'])
    starting_counts=run.OBSERVED.copy()
    evidence={name:run.Evidence(folder/(name+'.jsonl')) for name in
              ('local_maps_new','direct_checks','finite_references','rejections','plot_samples')}
    source_rows=read_rows(old/'sources.jsonl')
    local_rows=read_rows(old/'local_maps.jsonl')
    native_metadata=json.loads((old/'NATIVE_STATE_RECONSTRUCTION.json').read_text())
    states=[]
    for row in source_rows:
        nH=(float(native_metadata['source_decimal_fields']['nH_cm3'])*1e6
            if row['id'].startswith('native_') else row['N_m3'])
        state=model.LineState(row['card_id'],row['population_scope'],row['n_l_m3'],row['n_u_m3'],
            row['H_s_inv'],row['f_plus'],np.asarray(row['S']),row['state_provenance'],
            row['angular_provenance'],n_H_reference_m3=nH)
        states.append((row['id'],state,row['driving'],row['shear_fixture']))
    seed=local_rows[-1]
    z,omega=seed['z0'],1.0
    lower,upper=-omega+min(z,0),min(0,-omega+max(z,0))
    fun=lambda u:math.fsum((u,z*math.expm1(u),omega))
    run.dump(folder/'FAILURE_DIAGNOSIS.json',{'failed_id':'local_native_omega1','z0':z,
        'omega':omega,'rounded_lower':lower,'rounded_upper':upper,
        'F_lower':fun(lower),'F_upper':fun(upper),
        'outward_lower':math.nextafter(lower,-math.inf),
        'outward_upper':min(0,math.nextafter(upper,math.inf)),
        'F_outward_lower':fun(math.nextafter(lower,-math.inf)),
        'F_outward_upper':fun(min(0,math.nextafter(upper,math.inf))),
        'classification':'FLOAT_ENDPOINT_BRACKET_COLLAPSE; NOT_PHYSICAL_DOMAIN_FAILURE'})
    exception=None
    started=time.monotonic()
    try:
        for omega in (1.0,5.0):
            row=model.thick_local_step(card_id=seed['card_id'],population_scope=seed['population_scope'],
                N_m3=seed['N_m3'],x0=seed['x0'],H_s_inv=seed['H_s_inv'],f_plus=seed['f_plus'],
                S=np.asarray(seed['S']),omega=omega)
            identifier=f'local_native_omega{omega:g}'
            row.update(id=identifier,driving='saved_native_state',row_role='LOCAL_THICK_MAP',
                repair_role='FAILED_ROW_RETRY' if omega==1.0 else 'PREVIOUSLY_UNEXECUTED_ROW')
            oracle=run.high_precision_map(row)
            row['W0_oracle']=oracle
            evidence['local_maps_new'].append(row)
            local_rows.append(row)
            run.OBSERVED['local_map_rows']+=1
            run.check('W0_endpoint',oracle['endpoint_absolute_error'],5e-11*abs(row['y0'])+64*run.EPS*abs(row['x_eq']),context=identifier)
            run.check('W0_packet',oracle['packet_absolute_error'],5e-13*row['N_m3']*abs(row['y0'])+64*run.EPS*abs(row['delta_n_gamma_m3']),context=identifier)
            run.check('log_root',abs(row['log_root_residual']),5e-13*(1+row['omega']+abs(row['z0'])),context=identifier)
            run.check('path_gate',row['path_depth_ratio']>=model.THICK_THRESHOLD,True,relation='==',context=identifier)
            lo,hi=sorted((row['x0'],row['x_eq']))
            run.check('monotone_no_overshoot',lo-64*run.EPS<=row['x1']<=hi+64*run.EPS,True,relation='==',context=identifier)
            run.check('map_population_domain',-64*run.EPS<=row['x1']<row['g']/row['b'],True,relation='==',context=identifier)
            run.check('map_signed_packet',row['delta_n_gamma_m3']*row['y0']>=0,True,relation='==',context=identifier)
            for key in ('atom_number_residual','photon_upper_residual','energy_residual'):
                run.check('map_'+key,abs(row[key]),0.0,context=identifier)
        donor=run.direct_comparisons(evidence['direct_checks'],states,source_rows)
        run.dump(folder/'DONOR_AST_REUSE.json',donor)
        run.finite_references(evidence['finite_references'],local_rows)
        run.rejection_checks(evidence['rejections'],states[0][1])
        run.plot_tracks(evidence['plot_samples'],folder)
        for key,value in run.EXPECTED.items():
            run.check('fixed_count_'+key,run.OBSERVED[key],value,relation='==')
        for key,value in EXPECTED_NEW.items():
            run.check('resume_count_'+key,run.OBSERVED[key]-starting_counts[key],value,relation='==')
        run.check('map_outputs_total',25+model.COUNTERS['local_map_outputs'],270,relation='==')
        run.check('no_source_recomputation',model.COUNTERS['source_rows'],0,relation='==')
        run.check('unique_source_ids',len({r['id'] for r in source_rows}),36,relation='==')
        run.check('unique_local_map_ids',len({r['id'] for r in local_rows}),27,relation='==')
    except BaseException:
        exception=traceback.format_exc()
        with (folder/'FAILURE_TRACEBACK.txt').open('x') as f:f.write(exception)
    finally:
        for handle in evidence.values():handle.close()
        failures=[r for r in run.ACCEPTANCE if not r['pass']]
        run.dump(folder/'ACCEPTANCE.json',{'checks':run.ACCEPTANCE,'passed':len(run.ACCEPTANCE)-len(failures),
            'failed':len(failures),'failures':failures,'reused_original_checks':len(prior_checks)})
        unchanged=True
        for entry in old_manifest['files']:
            if run.sha(ROOT/entry['path'])!=entry['sha256']:unchanged=False
        metrics={'schema':'line01.targeted_resume_result.v1',
            'status':'FAIL' if exception or failures or not unchanged else 'PASS_AFTER_TARGETED_ROUNDING_REPAIR',
            'original_attempt_status':'FAIL_RETAINED','original_raw_unchanged':unchanged,
            'aggregate_completed_counts':dict(run.OBSERVED),
            'new_counts':dict(run.OBSERVED-starting_counts),
            'new_model_counters':dict(model.COUNTERS),
            'original_model_counters_including_failed_probe':old_metrics['model_counters'],
            'new_angular_counters':dict(model.angular.COUNTERS),
            'raw_new_row_counts':{k:v.rows for k,v in evidence.items()},
            'old_source_rows_recomputed':0,'old_successful_map_rows_recomputed':0,
            'failed_native_omega1_retried_once':True,
            'exception':exception,'acceptance_passed':len(run.ACCEPTANCE)-len(failures),
            'acceptance_failed':len(failures),'elapsed_wall_s':time.monotonic()-started,
            'old_campaign_reruns':0,'new_cosmological_IVP_calls':0,'new_local_IVP_calls':0,'native_runtime_calls':0,
            'Physical':'HOLD','REC_U5':['HOLD_9_FAIL','HOLD_8_FAIL'],'global_convergence':'NOT_RUN',
            'production':'NOT_APPROVED','REI_activation':False}
        run.dump(folder/'METRICS.json',metrics)
        files=[p for p in sorted(folder.rglob('*')) if p.is_file()]
        run.dump(folder/'RAW_MANIFEST.json',{'schema':'line01.targeted_resume_manifest.v1',
            'files':[{'path':str(p.relative_to(ROOT)),'bytes':p.stat().st_size,'sha256':run.sha(p)} for p in files],
            'original_failed_attempt':'results/attempt001/','original_raw_unchanged':unchanged})
    print(json.dumps({'status':metrics['status'],'new_counts':metrics['new_counts'],
        'aggregate_completed_counts':metrics['aggregate_completed_counts'],
        'acceptance_failed':metrics['acceptance_failed'],'elapsed_wall_s':metrics['elapsed_wall_s']},indent=2))
    return 0 if metrics['status'].startswith('PASS') else 1


if __name__=='__main__':
    raise SystemExit(run_resume())
