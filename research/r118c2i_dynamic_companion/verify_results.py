import argparse,json,hashlib,gzip,re
from pathlib import Path
import numpy as np
D=Path(__file__).resolve().parent;home=Path.home()/'Downloads'
p=argparse.ArgumentParser();p.add_argument('--raw',action='store_true');a=p.parse_args()
def sha(p):
 with open(p,'rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
r=json.loads((D/'RESULTS.json').read_text());cs=r['cases']
assert len(cs)==30 and sum(c['steps'] for c in cs)==147
assert all(c['events']==319 and c['source_rate_relative']<2e-15 for c in cs)
for c in cs:
 assert c['max_number_relative']<(3e-3 if c['collision'] else 1e-12)
 assert c['max_energy_relative']<(3e-3 if c['collision'] else 1e-12)
 assert c['max_source_event_residual']<1e-12
ref=r['references'];assert [x['steps'] for x in ref]==[1,2,4,8,16,32]
ratios=[x['relative_signal_error']/y['relative_signal_error'] for x,y in zip(ref,ref[1:])]
assert all(1.9<x<2.1 for x in ratios)
log=gzip.decompress((D/'logs/r118c2i_rec_cargo.log.gz').read_bytes()).decode()
m=re.findall(r'test result: (\w+)\. (\d+) passed; (\d+) failed; (\d+) ignored',log)
assert sum(int(x[1]) for x in m)==146 and sum(int(x[2]) for x in m)==0
assert '12 passed' in gzip.decompress((D/'logs/r118c2i_rec_py.log.gz').read_bytes()).decode()
if a.raw:
 root=home/'rec_r118c2i_dynamic_trial';compiled=home/'rec_r118c2f_compiled_final'
 assert sha(D.parents[1]/'rust/rec_microphysics/target/release/rec_live_line')==r['binary_sha256']
 for c in cs:
  assert sha(compiled/(c['bath']+'.npz'))==c['source_sha256']
  assert sha(root/f"{c['bath']}_s{c['sub']}.txt")==c['graph_sha256']
  for f,h in c['hashes'].items():assert sha(root/c['case']/f)==h
  with np.load(root/c['case']/'STATE.npz') as q:
   assert np.min(q['tracked_base']+q['tracked_delta'])>=0 and np.min(q['companion_base']+q['companion_delta'])>=0
   assert 0<=q['n2_base']+q['n2_delta']<=q['neutral']
   en=q['tracked_delta']@q['tracked_energy']+q['companion_delta']@q['companion_energy']+np.longdouble(10.198714553953742)*q['n2_delta']+np.longdouble(c['terminal']['bath_energy'])
   assert abs(en-c['terminal']['energy_eV_m3'])<1e-12*max(c['gross_events']*10.2,1e-30)
print('PASS_SCOPED 30 dynamic 2s cases, 147 steps, 146 Rust + 12 Python')
