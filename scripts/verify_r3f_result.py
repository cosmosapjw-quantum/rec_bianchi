"""Post-run science/integrity gate for the source-native R3f H+He sensitivity scan.

Does not rerun heavy native code or mark the result as a REI calculation.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path

SOURCE_SHA="48cd597519606cdafd0ee6405b781d28467cd323278d16596055a8d0577a1d27"
PR94_SHA="6fa5cb83a45ed3599d824ff821b6c8df41dd6d0e78a46cf9b33fde91b933e400"


def verify(folder:Path,expected_mode:str)->dict:
    d=json.loads((folder/'RUN.json').read_text())
    if d.get('schema')!='rec.r3f.native_hyrec_yhe.v1': raise ValueError('unexpected result schema')
    if d.get('mode')!=expected_mode: raise ValueError('run mode mismatch')
    if d.get('status')!='PASS_NATIVE_SOURCE_YHE_SCAN': raise ValueError('run has science failure')
    n={'smoke':7,'local':49,'ncp':97}[expected_mode]
    if d['source_sha256']!=SOURCE_SHA or d['build']['source_sha256']!=SOURCE_SHA: raise ValueError('source hash mismatch')
    if d['source_reference_comparison']['reference_stdout_sha256']!=PR94_SHA: raise ValueError('PR94 reference changed')
    comparison=d['source_reference_comparison']
    if (not comparison['science_equivalent'] or
        not math.isfinite(comparison['max_rel_xe']) or not math.isfinite(comparison['max_rel_Tm_over_Tr']) or
        comparison['max_rel_xe']>1e-9 or comparison['max_rel_Tm_over_Tr']>1e-9):
        raise ValueError('C baseline scientific mismatch')
    if d['science_cases']!=n or d['science_cases_passed']!=n: raise ValueError('missing completed physics cases')
    if len(d['cases'])!=n or len({r['index'] for r in d['cases']})!=n: raise ValueError('duplicate or missing case')
    if any(r['status']!='PASS' or r['rows']!=8001 for r in d['cases']): raise ValueError('native C case failure')
    expected_indices=set((-4,-2,-1,0,1,2,4) if expected_mode=='smoke' else
                         range(-24,25) if expected_mode=='local' else range(-48,49))
    if {r['index'] for r in d['cases']}!=expected_indices: raise ValueError('mode index set mismatch')
    if (not math.isfinite(d['base_YHe']) or not math.isclose(d['base_YHe'],0.2454,rel_tol=0,abs_tol=1e-15)
        or not math.isclose(d['delta_YHe_unit'],0.000125,rel_tol=0,abs_tol=1e-18)):
        raise ValueError('YHe scan base or step mismatch')
    for record in d['cases']:
        if not math.isclose(record['YHe'],d['base_YHe']+record['index']*d['delta_YHe_unit'],rel_tol=0,abs_tol=2e-16):
            raise ValueError('case YHe/index mapping mismatch')
    if expected_mode=='ncp':
        if d['cpu_affinity']<48 or d['workers']>48 or d['workers']>d['cpu_affinity']:
            raise ValueError('unproven NCP resource topology')
        if d['per_case_address_limit_GiB']*d['workers']>112:
            raise ValueError('NCP resource cap exceeded')
    manifest=json.loads((folder/'SHA256_MANIFEST.json').read_text())
    if not isinstance(manifest,dict): raise ValueError('invalid manifest schema')
    for name,entry in manifest.items():
        rel=Path(name)
        if rel.is_absolute() or not rel.parts or any(part in ('','.','..') for part in rel.parts):
            raise ValueError('unsafe manifest path')
        if not isinstance(entry,dict) or set(entry)!={'sha256','size_bytes'}:
            raise ValueError('invalid manifest entry')
    actual={}
    for path in folder.rglob('*'):
        if path.is_symlink(): raise ValueError('symlink forbidden in result tree: '+str(path.relative_to(folder)))
        if path.is_file() and path.name!='SHA256_MANIFEST.json':
            rel=path.relative_to(folder).as_posix()
            actual[rel]={'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
                         'size_bytes':path.stat().st_size}
    if manifest!=actual: raise ValueError('recursive artifact manifest mismatch')
    if not {'RUN.json','CASE_SUMMARY.csv','SOURCE_DERIVATIVES_Z20_1600.csv'}.issubset(manifest):
        raise ValueError('missing scientific output in manifest')
    def check_raw_record(case_dir,meta):
        if not math.isfinite(meta.get('elapsed_s',float('nan'))) or meta['elapsed_s']<0:
            raise ValueError('invalid raw case elapsed time')
        for name,key in (('input.txt','input_sha256'),('stdout.bin','stdout_sha256'),('stderr.bin','stderr_sha256')):
            if hashlib.sha256((case_dir/name).read_bytes()).hexdigest()!=meta.get(key):
                raise ValueError('raw case metadata hash mismatch: '+str(case_dir/name))
        if meta.get('source_sha256')!=SOURCE_SHA:
            raise ValueError('raw case source hash mismatch')
    # Every science case and control retains source bytes and execution metadata.
    expected_indices=(-4,-2,-1,0,1,2,4) if expected_mode=='smoke' else range(-24,25) if expected_mode=='local' else range(-48,49)
    for index in expected_indices:
        record=next((r for r in d['cases'] if r['index']==index),None)
        if record is None: raise ValueError('missing case record')
        raw=record.get('raw_dir')
        if not raw or Path(raw).is_absolute() or '..' in Path(raw).parts:
            raise ValueError('unsafe or missing case raw path')
        case_dir=folder/raw
        if not case_dir.is_dir(): raise ValueError('missing raw case directory')
        meta=json.loads((case_dir/'case.json').read_text())
        if meta.get('status')!='PASS' or meta.get('index')!=index:
            raise ValueError('raw case metadata mismatch')
        check_raw_record(case_dir,meta)
        if meta['input_sha256']!=record['source_input_sha256'] or meta['stdout_sha256']!=record['source_stdout_sha256']:
            raise ValueError('raw case differs from summary record')
    raw_names=set(manifest)
    for name in ('raw_cases/baseline_source/input.txt','raw_cases/baseline_source/stdout.bin',
                 'raw_cases/baseline_source/stderr.bin','raw_cases/baseline_source/case.json'):
        if name not in raw_names: raise ValueError('missing baseline raw evidence: '+name)
    baseline_dir=folder/'raw_cases'/'baseline_source'
    baseline_meta=json.loads((baseline_dir/'case.json').read_text())
    if baseline_meta.get('status')!='PASS' or baseline_meta.get('role')!='baseline_source':
        raise ValueError('baseline raw metadata mismatch')
    check_raw_record(baseline_dir,baseline_meta)
    if baseline_meta['stdout_sha256']!=comparison['current_stdout_sha256']:
        raise ValueError('baseline raw stdout differs from RUN comparison')
    for phase in ('control_serial','control_parallel'):
        for index in (-4,-2,-1,0,1,2,4):
            prefix=f'raw_cases/{phase}_{index:+03d}/'
            if not all(prefix+file in raw_names for file in ('input.txt','stdout.bin','stderr.bin','case.json')):
                raise ValueError('missing control raw evidence: '+prefix)
    controls={}
    for phase in ('control_serial','control_parallel'):
        controls[phase]={}
        for index in (-4,-2,-1,0,1,2,4):
            case_dir=folder/'raw_cases'/f'{phase}_{index:+03d}'
            meta=json.loads((case_dir/'case.json').read_text())
            if meta.get('status')!='PASS' or meta.get('index')!=index:
                raise ValueError('control raw metadata mismatch')
            check_raw_record(case_dir,meta)
            if not math.isclose(meta['YHe'],d['base_YHe']+index*d['delta_YHe_unit'],rel_tol=0,abs_tol=2e-16):
                raise ValueError('control YHe/index mapping mismatch')
            controls[phase][index]=meta['stdout_sha256']
    if controls['control_serial']!=controls['control_parallel']:
        raise ValueError('serial/parallel control stdout byte parity failed')
    if set(d['serial_parallel_control_stdout_sha256']['serial'])!=set(map(str,(-4,-2,-1,0,1,2,4))):
        raise ValueError('RUN control parity record incomplete')
    for index in (-4,-2,-1,0,1,2,4):
        key=str(index)
        if (d['serial_parallel_control_stdout_sha256']['serial'][key]!=controls['control_serial'][index] or
            d['serial_parallel_control_stdout_sha256']['parallel'][key]!=controls['control_parallel'][index]):
            raise ValueError('RUN control parity record differs from raw evidence')
    with (folder/'SOURCE_DERIVATIVES_Z20_1600.csv').open(newline='') as f:
        rows=list(csv.DictReader(f))
    if len(rows)!=1581 or [int(row['zbar']) for row in rows]!=list(range(20,1601)):
        raise ValueError('missing derivative redshift coverage')
    if abs(float(rows[0]['xe0_per_H'])-0.000210349192936)>1e-15:
        raise ValueError('source z20 electron fraction changed')
    # Physics: at fixed omega_bh2, the original hydrogen number density
    # changes as nH proportional (1-YHe). Check the whole CSV independently.
    for row in rows:
        for field in ('xe0_per_H','Tm0_K','dxe_dYhe_Richardson','dTm_K_dYhe_Richardson',
                      'source_dln_nH_dYhe','source_dln_ne_dYhe'):
            if not math.isfinite(float(row[field])): raise ValueError('nonfinite derivative CSV value')
        y=d['base_YHe']
        expected=float(row['dxe_dYhe_Richardson'])/float(row['xe0_per_H'])-1/(1-y)
        if abs(expected-float(row['source_dln_ne_dYhe']))>5e-12:
            raise ValueError('source electron-density derivative identity broken')
    return {'schema':'rec.r3f.postrun_validation.v1',
            'source_hash':SOURCE_SHA,'mode':expected_mode,
            'science_cases':n,'redshift_rows':len(rows),
            'native_HHe_source':'PASS',
            'baseline_match':'PASS_SCIENTIFIC_EQUIVALENCE',
            'artifact_sha256':'PASS',
            'source_density_derivative_identity':'PASS',
            'decision':'PASS_SCOPED_ORIGINAL_HYREC_FULL_Q0_YHE_ONLY'}


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--folder',type=Path,required=True)
    ap.add_argument('--expected-mode',choices=('smoke','local','ncp'),required=True)
    a=ap.parse_args()
    print(json.dumps(verify(a.folder,a.expected_mode),indent=2,sort_keys=True))
