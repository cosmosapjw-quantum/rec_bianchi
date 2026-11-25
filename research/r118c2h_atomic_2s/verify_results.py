import argparse,json,hashlib,re,gzip
from pathlib import Path
D=Path(__file__).resolve().parent;home=Path.home()/'Downloads'
p=argparse.ArgumentParser();p.add_argument('--raw',action='store_true');a=p.parse_args()
def sha(p):
    with open(p,'rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
r=json.loads((D/'RESULTS.json').read_text());o=json.loads((D/'ODE_REFERENCE.json').read_text())
assert len(r['cases'])==22 and sum(c['steps'] for c in r['cases'])==99 and r['status']=='PASS_SCOPED'
assert max(c['max_node_residual'] for c in r['cases'])<3e-4
assert max(c['max_atom_residual'] for c in r['cases'])<1e-9
assert max(c['terminal']['energy_event_relative'] for c in r['cases'])<3e-4
assert max(c['terminal']['number_event_relative'] for c in r['cases'])<3e-4
assert len(o['rows'])==7
ratios=[x['relative_excited_signal_error']/y['relative_excited_signal_error'] for x,y in zip(o['rows'],o['rows'][1:])]
assert min(ratios)>1.9 and max(ratios)<2.1
log=gzip.decompress((D/'logs/r118c2h_rec_cargo.log.gz').read_bytes()).decode();m=re.findall(r'test result: (\w+)\. (\d+) passed; (\d+) failed; (\d+) ignored',log)
assert sum(int(x[1]) for x in m)==146 and sum(int(x[2]) for x in m)==0
assert '10 passed' in gzip.decompress((D/'logs/r118c2h_rec_py.log.gz').read_bytes()).decode()
if a.raw:
    root=home/'rec_r118c2h_atomic_trial';compiled=home/'rec_r118c2f_compiled_final'
    assert sha(D.parents[1]/'rust/rec_microphysics/target/release/rec_live_line')==r['binary_sha256']
    for c in r['cases']:
        assert sha(compiled/(c['bath']+'.npz'))==c['source_sha256']
        assert sha(root/f"{c['bath']}_s{c['subcells']}.txt")==c['graph_sha256']
        for f,h in c['hashes'].items():assert sha(root/c['case']/f)==h
print('PASS_SCOPED 22 actual source/COM cases, 99 steps, first-order ODE check; 146 Rust + 10 Python')
