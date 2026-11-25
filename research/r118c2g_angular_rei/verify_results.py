"""Verify compact receipts; --raw also rehashes and checks source/output arrays."""
import argparse,gzip,hashlib,json,re
from pathlib import Path
import numpy as np
D=Path(__file__).resolve().parent;home=Path.home()/'Downloads'
def sha(p):
    with open(p,'rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def load(name):return json.loads((D/name).read_text())
def readgz(name):return gzip.decompress((D/name).read_bytes())
p=argparse.ArgumentParser();p.add_argument('--raw',action='store_true');a=p.parse_args()
source=load('SOURCE_RESULTS.json');r=load('RESULTS.json');orig=load('ORIGINAL_BALANCE_TRIAL.json');atom=load('ATOMIC_POINT_RESULTS.json')
normal=json.loads(readgz('REI_INITIAL_NORMAL.json.gz'));tight=json.loads(readgz('REI_INITIAL_TIGHT.json.gz'))
assert len(source)==3 and all(x['pairs']==459 and x['samples']==73304 for x in source)
assert len(r['graphs'])==6 and len(r['cases'])==29 and all(c['status']=='PASS_SCOPED' for c in r['cases'])
assert max(g['moment_l1_relative'][1] for g in r['graphs'])<1e-13
assert max(g['moment_l1_relative'][1] for g in orig['graphs'])>1e-3
assert max(g['isotropic_mass_gap'] for g in r['graphs'])<5e-12
assert all(c['run']['minimum_f']>=0 and c['run']['number_defect']<2e-10 and c['run']['max_be_residual']<=2e-11 for c in r['cases'])
assert len(atom)==6 and all(x['native_inside']==6 and x['native_cross']==2 and x['native_centre']==2 for x in atom)
for key in ('source_number_residual','source_energy_residual','atom_companion_tracked_energy_residual','thermal_null_relative','native_reassembly_relative'):assert max(x[key] for x in atom)<1e-13
assert normal['initial']['z']==20 and not normal['history']['external_history'] and not normal['history']['external_hyrec_runtime']
assert tight['initial']['z']==20
rt=gzip.decompress((D/'logs/r118c2g_rec_cargo.log.gz').read_bytes()).decode()
counts=re.findall(r'test result: (\w+)\. (\d+) passed; (\d+) failed; (\d+) ignored',rt)
assert counts and sum(int(x[1]) for x in counts)==146 and sum(int(x[2]) for x in counts)==0
assert '8 passed' in gzip.decompress((D/'logs/r118c2g_rec_python.log.gz').read_bytes()).decode()
if a.raw:
    for s in source:
        new=home/'rec_r118c2g_angular_source'/(s['case']+'.npz')
        old=home/'rec_r118c2f_compiled_final'/(s['case']+'.npz')
        assert sha(new)==s['sha256']
        with np.load(new) as x,np.load(old) as y:
            for k in ('Q1','Q4','direct'):assert np.array_equal(x[k],y[k])
    for name,v in [('rec_r118c2g_angular_final',r),('rec_r118c2g_angular_trial',orig)]:
        root=home/name
        for g in v['graphs']:assert sha(Path(g['graph_path']))==g['graph_sha256']
        for c in v['cases']:
            assert sha(root/(c['case']+'.case'))==c['case_sha256']
            for f,h in c['hashes'].items():assert sha(root/c['case']/f)==h
        assert sha(Path(v['cases'][0]['command'][0]))==v['binary_sha256']
    assert hashlib.sha256(readgz('REI_INITIAL_NORMAL.json.gz')).hexdigest()==sha(home/'rec_r118c2g_boundary/normal.json')
    assert hashlib.sha256(readgz('REI_INITIAL_TIGHT.json.gz')).hexdigest()==sha(home/'rec_r118c2g_boundary/tight.json')
print('PASS_SCOPED',len(r['cases']),'angular;',len(atom),'point-packet;',146,'Rust;',8,'targeted Python')
