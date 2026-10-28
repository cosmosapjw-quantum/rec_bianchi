"""Independent C9 controls; original scientific campaigns are not executed."""
from pathlib import Path
from fractions import Fraction as F
from decimal import Decimal
import copy
import hashlib
import importlib.util
import json
import resource
import subprocess
import sys
import tempfile
import time

BASE = Path('/workspace/scratch/e0012d8fd22a')
REPO = BASE / 'rec_bianchi'
NEW = REPO / 'research/rec_hd_joint_interval_20261029'
OLD = REPO / 'research/rec_hd_print_precision_20261029'
OUT = BASE / 'review'
START = time.monotonic()
R0 = resource.getrusage(resource.RUSAGE_SELF)
C0 = resource.getrusage(resource.RUSAGE_CHILDREN)


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


j = module('c9_joint_interval', NEW / 'joint_interval.py')
p = module('c9_precision', OLD / 'precision_audit.py')


def independent_feasible(delta, radii, line, scale):
    """Difference constraints via exact Bellman-Ford; no interval recurrence."""
    n = len(delta)
    zero = n + 1
    edges = []
    for v in range(n + 1):
        edges += [(zero, v, scale * radii[v]),
                  (v, zero, scale * radii[v])]
    for v in range(n):
        edges += [(v, v + 1, -delta[v] + scale * line[v]),
                  (v + 1, v, delta[v] + scale * line[v])]
    distance = [F(0)] * (n + 2)
    for unused in range(n + 2):
        changed = False
        for u, v, w in edges:
            if distance[v] > distance[u] + w:
                distance[v] = distance[u] + w
                changed = True
        if not changed:
            return True
    return False


def verify_witness(delta, radii, line, scale, witness):
    assert witness['feasible']
    x, y = witness['x'], witness['y']
    assert len(x) == len(radii) and len(y) == len(delta)
    assert all(abs(xi) <= scale * ri for xi, ri in zip(x, radii))
    assert all(abs(yi) <= scale * si for yi, si in zip(y, line))
    assert all(delta[k] + x[k + 1] - x[k] == y[k]
               for k in range(len(delta)))


models = [
    ('empty', [], [F(0)], []),
    ('all_zero_n3', [F(0)] * 3, [F(0)] * 4, [F(0)] * 3),
    ('zero_denominator_interior', [F(0), F(1), F(0)], [F(0)] * 4, [F(0)] * 3),
    ('three_edge_mixed', [F(2), F(-3), F(2)], [F(1), F(0), F(2), F(1)], [F(1, 2), F(1), F(0)]),
    ('four_edge_joint_constraint', [F(1), F(1), F(1), F(1)], [F(1)] * 5, [F(0)] * 4),
    ('photon_width_only', [F(2, 3), F(-7, 5), F(1, 9)], [F(0)] * 4, [F(1, 3), F(7, 5), F(1, 18)]),
]
model_results = []
comparisons = 0
for name, delta, radii, line in models:
    cert = j.segment_certificate(delta, radii, line)
    minimum = cert['lambda_min']
    scales = {F(0), F(1), F(3, 2)}
    if minimum is not None:
        scales |= {minimum, minimum + F(1, 101)}
        if minimum:
            scales.add(max(F(0), minimum - F(1, 101)))
    decisions = []
    for scale in sorted(scales):
        primary = j.reachability(delta, radii, line, scale)
        independent = independent_feasible(delta, radii, line, scale)
        assert primary['feasible'] == independent, (name, scale)
        assert j.segment_certificate(delta, radii, line, scale)['feasible'] == independent
        if primary['feasible']:
            verify_witness(delta, radii, line, scale, primary)
        decisions.append({'scale': str(scale), 'feasible': independent})
        comparisons += 1
    if minimum is not None:
        assert independent_feasible(delta, radii, line, minimum)
        if minimum:
            assert not independent_feasible(delta, radii, line, minimum / 2)
    model_results.append({'model': name, 'minimum_kind': cert['minimum_scale_kind'],
                          'minimum': None if minimum is None else str(minimum),
                          'decisions': decisions})

fixture = json.loads((NEW / 'source_literals.json').read_text())
raw_path = BASE / 'acquisition/hd.dat'
raw = raw_path.read_bytes()
raw_hash = hashlib.sha256(raw).hexdigest()
assert len(raw) == 2289 and raw_hash == j.SOURCE_SHA256
lines = raw.decode('ascii').splitlines()
level_start = lines.index('!LEVEL + ENERGIES(cm^-1) + WEIGHT + J (or other quantum numbers)') + 1
photon_start = lines.index('!TRANS + U + L + A(s^-1) + FREQ(GHz) + E_u/k(K)') + 1
raw_terms = [lines[level_start + k].split()[1] for k in range(9)]
raw_photons = [lines[photon_start + k].split()[4] for k in range(8)]
assert raw_terms == [r['w_cm_minus_1'] for r in fixture['levels']]
assert raw_photons == [r['nu_GHz'] for r in fixture['radiative_lines']]
delta = [100 * F(299792458) * (F(raw_terms[k + 1]) - F(raw_terms[k]))
         - 10**9 * F(raw_photons[k]) for k in range(8)]
# Direct independently encoded constant half-quanta for this exact raw table.
radii = [F(299792458, 20000000)] * 9
line = [F(5)] * 8
assert all(j.half_quantum(token) == F(1, 2 * 10**9) for token in raw_terms)
assert all(j.half_quantum(token) == F(1, 2 * 10**8) for token in raw_photons)
ratios = [(abs(sum(delta[p:q])) / (radii[p] + radii[q] + sum(line[p:q])), p, q)
          for p in range(8) for q in range(p + 1, 9)]
minimum, pmax, qmax = max(ratios)
assert (minimum, pmax, qmax) == (F(9137862803786, 174896229), 5, 6)
assert independent_feasible(delta, radii, line, minimum)
assert not independent_feasible(delta, radii, line, minimum - F(1, 10**12))
assert not independent_feasible(delta, radii, line, F(1))
api_raw = j.source_certificate(fixture, raw_path)
api_fixture = j.source_certificate(fixture)
assert api_raw['source_identity']['raw_verified_this_execution'] is True
assert api_fixture['source_identity']['raw_verified_this_execution'] is False
assert api_raw['source_identity']['input_mode'] == 'PINNED_RAW_PLUS_FIXTURE'
assert api_fixture['source_identity']['input_mode'] == 'EXTRACTED_LITERAL_FIXTURE_ONLY'
assert api_raw['all_segments']['lambda_min'] == minimum
verify_witness(delta, radii, line, minimum, api_raw['minimum_scale_witness'])
assert not api_raw['physical_admission'] and not api_fixture['physical_admission']

def reject(call):
    try:
        call()
    except ValueError:
        return
    raise AssertionError('expected ValueError')


changed = copy.deepcopy(fixture)
changed['levels'][1]['w_cm_minus_1'] = '89.227931612'
reject(lambda: j.source_certificate(changed, raw_path))
for bad in ('NaN', '-Infinity', 'Infinity', 'sNaN'):
    reject(lambda bad=bad: j.exact(Decimal(bad)))
reject(lambda: j.reachability([0], [1, 1], [1], F(-1)))
reject(lambda: j.segment_certificate([0], [1, 1], [1], '1/0'))

def spcat_row(frequency='2674986.0000', uncertainty='0.0300', elo='0.0000', tag=3501):
    return (f'{frequency:>13}{uncertainty:>8}{"-9.1234":>8}{2:2d}'
            f'{elo:>10}{3:3d}{tag:7d}{101:4d}' + '  1  0'.ljust(24))


nonfinite_rejections = 0
for field in ('frequency', 'uncertainty', 'elo'):
    for token in ('Infinity', '-Infinity', 'NaN', 'sNaN'):
        reject(lambda field=field, token=token: p.parse_spcat_line(spcat_row(**{field: token})))
        nonfinite_rejections += 1
assert p.parse_spcat_line(spcat_row(tag=-3501))['measured_tag']
assert not p.parse_spcat_line(spcat_row(tag=3501))['measured_tag']

cli_results = []
with tempfile.TemporaryDirectory(prefix='rec_final_c9_') as td:
    temp = Path(td)
    for mode in ('raw', 'fixture'):
        target = temp / mode / 'nested/certificate.json'
        command = [sys.executable, str(NEW / 'joint_interval.py'), '--output', str(target)]
        if mode == 'raw':
            command += ['--lamda', str(raw_path)]
        completed = subprocess.run(command, capture_output=True, text=True)
        assert completed.returncode == 0, completed.stderr
        value = json.loads(target.read_text())
        assert value['source_identity']['raw_verified_this_execution'] == (mode == 'raw')
        assert value['all_segments']['lambda_min'] == str(minimum)
        cli_results.append({'mode': mode, 'command': command, 'exit_code': completed.returncode,
                            'stderr': completed.stderr, 'result_sha256': hashlib.sha256(target.read_bytes()).hexdigest(),
                            'source_identity': value['source_identity'], 'minimum': value['all_segments']['lambda_min']})
    target = temp / 'old/results/certificate.json'
    command = [sys.executable, str(OLD / 'precision_audit.py'), '--output', str(target)]
    completed = subprocess.run(command, capture_output=True, text=True)
    assert completed.returncode == 0, completed.stderr
    old_cert = json.loads(target.read_text())
    ancestor = json.loads(subprocess.run(['git', 'show', '67d8baa092f18b7c1bbf8dfe9e255f8b43b45998:research/rec_hd_print_precision_20261029/RESULT_SUMMARY.json'],
                                        cwd=REPO, capture_output=True, text=True, check=True).stdout)
    assert old_cert['rounding_only_fail_count'] == 7
    assert [F(x['delta_Hz']) for x in old_cert['print_rows']] == [F(x['signed_delta_Hz']) for x in ancestor['rows']]
    cli_results.append({'mode': 'repaired_legacy_fresh_output', 'command': command,
                        'exit_code': completed.returncode, 'stderr': completed.stderr,
                        'finite_results_match_ancestor': True, 'old_gate_fail_count': 7})
    corrupted = temp / 'mutated_hd.dat'
    corrupted.write_bytes(raw[:-1] + bytes([raw[-1] ^ 1]))
    reject(lambda: j.extract_pinned_lamda(corrupted))

R1 = resource.getrusage(resource.RUSAGE_SELF)
C1 = resource.getrusage(resource.RUSAGE_CHILDREN)
record = {
    'schema': 'REC_HD_JOINT_INTERVAL_INDEPENDENT_C9_CONTROLS_V1',
    'reviewer': '/root/independent_hd_review', 'status': 'PASS_SCOPED',
    'models': model_results, 'implementation_vs_Bellman_Ford_decisions': comparisons,
    'raw_source_sha256': raw_hash, 'raw_source_bytes': len(raw), 'raw_literal_match_count': 17,
    'independent_source_minimum_scale': str(minimum), 'maximizing_segment': [pmax, qmax],
    'source_minimum_boundary': 'feasible exactly; infeasible at minimum-1e-12',
    'raw_and_fixture_flags_distinct': True, 'changed_raw_and_changed_fixture_with_raw': 'REJECTED',
    'SPCAT_nonfinite_rejections': nonfinite_rejections, 'measured_tag_controls': 'PRESERVED',
    'old_missing_directory_regression': 'CLOSED_FINITE_RESULTS_UNCHANGED', 'cli_results': cli_results,
    'resources': {'wall_s': time.monotonic() - START,
                  'self_cpu_s': (R1.ru_utime + R1.ru_stime) - (R0.ru_utime + R0.ru_stime),
                  'child_cpu_s': (C1.ru_utime + C1.ru_stime) - (C0.ru_utime + C0.ru_stime),
                  'self_peak_rss_kib': R1.ru_maxrss, 'child_peak_rss_kib': C1.ru_maxrss,
                  'measurement_scope': 'controls until immediately before receipt serialization; full child processes counted'},
    'input_identities': {str(path.relative_to(REPO)): hashlib.sha256(path.read_bytes()).hexdigest()
                         for path in (NEW / 'joint_interval.py', NEW / 'tests/test_joint_interval.py',
                                      NEW / 'source_literals.json', NEW / 'CODING_CONTRACT.json',
                                      OLD / 'precision_audit.py', OLD / 'tests/test_regression_repair.py')},
    'execution_source_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    'historical_stationary_native_IVP_runs': 0, 'provider_or_model_cost': 'UNKNOWN_NOT_ZERO',
}
(OUT / 'FINAL_CODE_CONTROLS.json').write_text(json.dumps(record, indent=2) + '\n')
print(json.dumps(record, indent=2))
