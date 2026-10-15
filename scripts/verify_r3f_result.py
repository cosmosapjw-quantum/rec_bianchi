"""Post-run science/integrity gate for the source-native R3f H+He sensitivity scan.

Does not rerun heavy native code or mark the result as a REI calculation.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
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
    if not d['source_reference_comparison']['science_equivalent']: raise ValueError('C baseline scientific mismatch')
    if d['science_cases']!=n or d['science_cases_passed']!=n: raise ValueError('missing completed physics cases')
    if len(d['cases'])!=n or len({r['index'] for r in d['cases']})!=n: raise ValueError('duplicate or missing case')
    if any(r['status']!='PASS' or r['rows']!=8001 for r in d['cases']): raise ValueError('native C case failure')
    if expected_mode=='ncp':
        if d['cpu_affinity']<48 or d['workers']>48 or d['workers']>d['cpu_affinity']:
            raise ValueError('unproven NCP resource topology')
        if d['per_case_address_limit_GiB']*d['workers']>112:
            raise ValueError('NCP resource cap exceeded')
    manifest=json.loads((folder/'SHA256_MANIFEST.json').read_text())
    for name,sha in manifest.items():
        if Path(name).name!=name or not (folder/name).is_file(): raise ValueError('invalid manifest path')
        if hashlib.sha256((folder/name).read_bytes()).hexdigest()!=sha:
            raise ValueError('artifact hash mismatch: '+name)
    if not {'RUN.json','CASE_SUMMARY.csv','SOURCE_DERIVATIVES_Z20_1600.csv'}.issubset(manifest):
        raise ValueError('missing scientific output in manifest')
    with (folder/'SOURCE_DERIVATIVES_Z20_1600.csv').open(newline='') as f:
        rows=list(csv.DictReader(f))
    if len(rows)!=1581 or int(rows[0]['zbar'])!=20 or int(rows[-1]['zbar'])!=1600:
        raise ValueError('missing derivative redshift coverage')
    if abs(float(rows[0]['xe0_per_H'])-0.000210349192936)>1e-15:
        raise ValueError('source z20 electron fraction changed')
    # Physics: at fixed omega_bh2, the original hydrogen number density
    # changes as nH proportional (1-YHe). Check the whole CSV independently.
    for row in rows:
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
