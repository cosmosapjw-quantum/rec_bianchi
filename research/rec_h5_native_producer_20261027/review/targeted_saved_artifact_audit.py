"""C9: audit saved evidence using exact rationals; never import producer code."""
import hashlib
import json
import os
from pathlib import Path
import resource
import signal
import sys
import time
from fractions import Fraction as F

resource.setrlimit(resource.RLIMIT_CPU, (30, 30))
resource.setrlimit(resource.RLIMIT_AS, (512*1024**2, 512*1024**2))
signal.alarm(60)
if hasattr(os, 'sched_getaffinity'):
    os.sched_setaffinity(0, {min(os.sched_getaffinity(0))})
started = time.process_time()
wall = time.monotonic()
base = Path(__file__).resolve().parents[1]
load = lambda p: json.loads(p.read_text())
identities = {}
def identity(p):
    identities[str(p.relative_to(base))] = {'sha256':hashlib.sha256(p.read_bytes()).hexdigest(), 'bytes':p.stat().st_size}
    return identities[str(p.relative_to(base))]['sha256']

packet_path = base/'results/primary001/REFERENCE_PACKET.json'
packet = load(packet_path)
identity(packet_path)
refs_path = base/'results/primary001/POINT_REFERENCE140.jsonl'
refs = [json.loads(line) for line in refs_path.read_text().splitlines()]
identity(refs_path)
rows = packet['reference_bounds']
assert len(rows) == len(refs) == 313
hashes = {p.name:identity(p) for p in sorted((base/'code').glob('*.py'))}
assert len(hashes) == 6
receipts = {}
for mode in ('primary001', 'controls001'):
    p = base/'results'/mode/'RUN_RECEIPT.json'; r = load(p); identity(p)
    assert r['code_sha256'] == hashes
    assert r['exit_code'] == 0 and not r['wall_timeout']
    assert r['limits']['threads'] == 1
    assert (base/'results'/mode/'stderr.txt').read_bytes() == b''
    receipts[mode] = {'cpu_seconds':r['cpu_seconds'],'wall_seconds':r['wall_seconds'], 'python_version':r['python_version']}
bound = load(base/'results/primary001/SOURCE_BINDINGS.json')
assert [r['binding'] for r in rows] == bound['bindings']
original = load(base.parents[1]/'research/program_expansion_20261025/h5_input_binding/inputs/SOURCE_CONTEXT.json')
for k in ('physical_query_bounds','full_state_K','physical_M2','physical_defect','stability_L','positive_uniform_ode_tube','initial_error','physical_epsilon','physical_outgoing_bound'):
    assert packet[k] is None
assert packet['physical_coverage'] == {'computed':0,'total':313}
assert packet['H6'] == packet['H7'] == 'OPEN'
assert packet['L4'] is False and packet['REI_activation'] is False
contained = 0
intervals = 0
for i,(row,ref) in enumerate(zip(rows,refs)):
    assert row['binding']['incoming_index'] == ref['incoming_index'] == i
    assert all(row['binding'][k] == v for k,v in original['queries'][i].items())
    b = {k:(F(v['lo']),F(v['hi'])) for k,v in row['reference_bounds'].items()}
    for lo,hi in b.values(): assert lo <= hi
    intervals += len(b)
    for k,v in ref['point_reference140'].items():
        assert b[k][0] <= F(v) <= b[k][1], (i,k)
        contained += 1
    assert b['scalar_occupation_K'] == (1,1)
    mag = lambda k:max(abs(b[k][0]),abs(b[k][1]))
    old = F(row['binding']['anchor_representation_radius_exact'])
    assert b['old_anchor_radius'][0] <= old <= b['old_anchor_radius'][1]
    assert b['R_bridge'][1] >= old + mag('J_ref') + mag('B_total')
    coef = F(row['binding']['pointwise_curvature_coefficient_exact'])
    assert b['chord_bound'][1] >= b['M2_ref'][1]*coef
    assert b['chord_bound'][1] >= mag('J_ref')
    assert b['R_bridge_curvature'][1] >= old + b['chord_bound'][1] + mag('B_total')
    assert b['J_ref'][0] > 0 and b['direct_bridge'][1] < 0
    assert b['represented_occupation_lower_bound'][0] > 0
    for k in ('bridge_identity_residual','B_total_identity_residual'):
        assert b[k][0] <= 0 <= b[k][1]
    for k in ('left_endpoint_monotone_proved','x_greater_than_one_proved','represented_reconstruction_positive_proved'):
        assert row['flags'][k]
controls_path = base/'results/controls001/CONTROLS.json'
controls = load(controls_path); identity(controls_path)
assert len(controls['controls']) == 38 and all(r['pass'] for r in controls['controls'])
for name in ('FROZEN_CONTRACT.md','CODING_CONTRACT.md','theory/THEORY.md','implementation/NUMERICAL_DESIGN.md','implementation/SCIENTIFIC_VALIDATION.md','implementation/REPRODUCIBILITY_C8.md','results/primary001/SOURCE_BINDINGS.json','results/primary001/SUMMARY.json','results/controls001/SUMMARY.json'):
    identity(base/name)
result = {'status':'PASS','command':sys.argv,'cwd':os.getcwd(),'source_identities':identities,
          'checks':{'code_receipt_matches':6,'preserved_rows':313,'ordered_finite_exact_rational_intervals':intervals,'saved_point_containments':contained,'exact_radius_and_chord_invariants':313,'saved_controls_pass':38,'physical_null_scope':'PASS'},
          'reused_runs':receipts,'production_or_control_runs':0,'production_imports':0,
          'limits':{'cpu_seconds':30,'wall_seconds':60,'memory_bytes':512*1024**2,'threads':1},
          'cpu_seconds_before_evidence_serialization':time.process_time()-started,'wall_seconds_before_evidence_serialization':time.monotonic()-wall,
          'max_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
          'unmeasured_tail':'startup/imports before timer and final evidence serialization are UNKNOWN_NOT_ZERO'}
(base/'review/TARGETED_SAVED_ARTIFACT_AUDIT.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k != 'source_identities'},indent=2))
