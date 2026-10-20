#!/usr/bin/env python3
"""Independent stdlib readback; never imports or executes the solver/comparators."""
import ast
import collections
import hashlib
import json
import math
import resource
import signal
import statistics
import struct
import subprocess
import sys
import tarfile
import time
import xml.etree.ElementTree as ET
import zipfile
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path('/workspace/scratch/45780e6e06f6/rec_bianchi')
RAW = ROOT.parent / 'rec_r3q_intake'
REC = ROOT / 'research/rec_r3r_followup_costs_20261020/receipts'
SOURCE = '1313b1f1b2c081d57bcce9c60e757ef79110df91'
EXPECTED_TREE = '97423cad509a9604269740132a6ad850faf8f19a'
HASHES = {}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def sha(path):
    path = Path(path)
    if str(path) not in HASHES:
        h = hashlib.sha256()
        with path.open('rb') as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b''):
                h.update(chunk)
        HASHES[str(path)] = h.hexdigest()
    return HASHES[str(path)]


def read_json(path):
    return json.loads(Path(path).read_text())


def check(condition, message):
    if not condition:
        raise AssertionError(message)


def git(*args):
    return subprocess.check_output(['git', '-C', str(ROOT), *args])


def verify_file(record):
    p = Path(record['path'])
    check(sha(p) == record['sha256'], 'file digest ' + str(p))
    if 'bytes' in record:
        check(p.stat().st_size == record['bytes'], 'file size ' + str(p))


def read_npz_data(path):
    result = {}
    with zipfile.ZipFile(path) as z:
        for name in z.namelist():
            data = z.read(name)
            check(data[:6] == b'\x93NUMPY', 'NPY magic')
            major = data[6]
            length_bytes = 2 if major == 1 else 4
            header_length = int.from_bytes(data[8:8 + length_bytes], 'little')
            start = 8 + length_bytes
            header = ast.literal_eval(data[start:start + header_length].decode('latin1'))
            check(not header['fortran_order'], 'C-order recorded array required')
            payload = data[start + header_length:]
            result[name.removesuffix('.npy')] = {
                'shape': list(header['shape']), 'dtype': header['descr'],
                'sha256': digest(payload)}
    return result


def main():
    began = time.monotonic()
    for kind, cap in ((resource.RLIMIT_CPU, 10), (resource.RLIMIT_AS, 2 * 1024**3)):
        soft, hard = resource.getrlimit(kind)
        lower = lambda value: cap if value == resource.RLIM_INFINITY else min(value, cap)
        resource.setrlimit(kind, (lower(soft), lower(hard)))
    signal.alarm(25)
    check(git('rev-parse', SOURCE + '^{tree}').decode().strip() == EXPECTED_TREE, 'tree')
    out = {'schema': 'rec.r3r.c9-evidence-readback.v1',
           'created_utc': datetime.now(timezone.utc).isoformat(),
           'audited_source_commit': SOURCE, 'audited_source_tree': EXPECTED_TREE,
           'method': 'independent standard-library byte reads and arithmetic; zero solver imports/runs',
           'script_sha256': sha(__file__), 'formal_attempts': {}}
    for n, wrapper in ((1, 'run_formal_validation.py'), (2, 'run_formal_validation_retry.py')):
        d = RAW / ('formal_validation_%03d' % n)
        v = read_json(d / 'validation.json')
        for name, expected in v['evidence_sha256'].items():
            check(sha(d / name) == expected, 'formal raw ' + str(d / name))
        check(sha(RAW / wrapper) == v['validation_wrapper_sha256'], 'wrapper digest')
        for cmd in v['commands']:
            for stream in ('stdout', 'stderr'):
                check(sha(cmd[stream]) == cmd[stream + '_sha256'], 'command log')
            stem = Path(cmd['stdout']).name.removesuffix('.stdout.log')
            check(read_json(d / (stem + '.execution.json')) == cmd, 'command receipt')
        xml = ET.parse(d / 'tests.xml').getroot()
        suites = list(xml.iter('testsuite'))
        counts = {key: sum(int(x.get(key, 0)) for x in suites)
                  for key in ('tests', 'failures', 'errors', 'skipped')}
        check(counts == {'tests': 61, 'failures': int(n == 1), 'errors': 0, 'skipped': 0}, 'JUnit counts')
        failures = [case.attrib['name'] for case in xml.iter('testcase') if case.find('failure') is not None]
        if n == 1:
            check(failures == ['test_fresh_prefix_reads_source_when_B_can_read_stale_cache'], 'first fixture failure')
        out['formal_attempts'][str(n)] = {
            'source_commit': v['repository_source_commit'], 'status': v['status'],
            'exit_code': v['exit_code'], 'verified_raw_files': len(v['evidence_sha256']),
            'junit': counts, 'failures': failures, 'validation_sha256': sha(d / 'validation.json'),
            'cpu_s': v['process_tree_cpu_s'], 'wall_s': v['wall_s']}
    d = RAW / 'formal_validation_002'
    b = read_json(d / 'benchmark/benchmark.json')
    trace = b['lane_binary64_trace']
    identity = trace['identity']
    check(b['source']['source_commit_sha'] == SOURCE, 'benchmark source')
    for relative, record in b['source']['source_files'].items():
        check(digest(git('show', SOURCE + ':' + relative)) == record['sha256'], 'benchmark Git source')
        verify_file(record)
    for record in b['inputs']['files'].values():
        verify_file(record)
    a = Path(trace['traces']['scalar']['path']).read_bytes()
    c = Path(trace['traces']['numpy']['path']).read_bytes()
    for record in trace['traces'].values():
        verify_file(record)
    check(len(a) == len(c) == 200000, 'lane trace size')
    differing = sum(a[i:i+8] != c[i:i+8] for i in range(0, len(a), 8))
    check(differing == trace['differing_binary64_lanes'] == 0, 'lane bytes')
    check(trace['native_byteorder'] == 'little', 'actual trace endian')
    lanes = struct.unpack('<25000d', a)
    check(all(math.isfinite(x) and 0.0 <= x <= 1.0 for x in lanes), 'lane finite gate')
    order = hashlib.sha256()
    counts = collections.Counter()
    stream_path = Path(b['inputs']['files']['native_stream']['path'])
    with stream_path.open() as stream:
        for line in stream:
            row = line.rstrip('\n').split(',')
            counts[row[0]] += 1
            if row[0] in ('V', 'A', 'L'):
                order.update(('%s,%d,%d\n' % (row[0], int(row[1]), int(row[2]))).encode('ascii'))
    check(order.hexdigest() == trace['ordered_tag_j_bin_sha256'], 'lane encounter order hash')
    check(dict(counts) == identity['verdict']['counts'], 'actual raw row counts')
    measured = [row for row in b['trials'] if row['phase'] == 'measured']
    warmups = [row for row in b['trials'] if row['phase'] == 'warmup']
    check(len(measured) == 10 and len(warmups) == 2, 'trial phase counts')
    check(all(row['identity'] == identity for row in b['trials']), 'all trial identity equality')
    pairs, medians = [], {}
    for index in range(5):
        rows = sorted([x for x in measured if x['round'] == index], key=lambda x: x['position'])
        check(len(rows) == 2, 'complete pair')
        expected_order = ['legacy', 'r3r_numpy'] if index % 2 == 0 else ['r3r_numpy', 'legacy']
        check([r['backend'] for r in rows] == expected_order, 'alternating paired order')
        pair = {r['backend']: r for r in rows}
        pairs.append({'round': index, 'order': expected_order,
                      'legacy_over_r3r_cpu': pair['legacy']['cpu_s'] / pair['r3r_numpy']['cpu_s'],
                      'legacy_over_r3r_wall': pair['legacy']['wall_s'] / pair['r3r_numpy']['wall_s']})
    check(pairs == b['summary']['paired_ratios'], 'paired ratios recomputed')
    for backend in ('legacy', 'r3r_numpy'):
        rows = [x for x in measured if x['backend'] == backend]
        medians[backend] = {'trials': len(rows), 'median_cpu_s': statistics.median(x['cpu_s'] for x in rows),
                            'median_wall_s': statistics.median(x['wall_s'] for x in rows)}
    check(medians == b['summary']['backends'], 'backend medians recomputed')
    ratios = {field: statistics.median(p['legacy_over_r3r_' + field] for p in pairs) for field in ('cpu', 'wall')}
    check(ratios['cpu'] == b['summary']['median_paired_cpu_ratio'], 'CPU median ratio')
    check(ratios['wall'] == b['summary']['median_paired_wall_ratio'], 'wall median ratio')
    rss = {}
    for backend, record in b['fresh_process_rss'].items():
        result = read_json(d / ('benchmark/rss_' + backend + '.stdout.json'))
        check(result == record['result'], 'RSS actual JSON')
        check(result['trial']['identity'] == identity, 'RSS trial identity')
        check(result['source'] == b['source'], 'RSS source')
        check(record['returncode'] == 0, 'RSS exit')
        for kind in ('stdout', 'stderr'):
            suffix = '.stdout.json' if kind == 'stdout' else '.stderr.log'
            check(sha(d / ('benchmark/rss_' + backend + suffix)) == record[kind + '_sha256'], 'RSS log hash')
        rss[backend] = result['peak_rss_bytes']
    out['benchmark'] = {'status': 'PASS_READBACK', 'medians': medians, 'paired_ratios': pairs,
                        'median_paired_ratios': ratios, 'lane_count': len(lanes),
                        'differing_binary64_lanes': differing, 'lane_sha256': digest(a),
                        'max_ratio': max(lanes), 'max_ratio_hex': max(lanes).hex(),
                        'exact_zero_lanes': sum(x == 0.0 for x in lanes),
                        'ordered_tag_j_bin_sha256': order.hexdigest(), 'raw_counts': dict(counts),
                        'fresh_process_rss_bytes': rss, 'warmup_trials_excluded': len(warmups)}
    binding = read_json(d / 'pilot/R3R_BINDING.json')
    supervisor = read_json(d / 'pilot/supervision.json')
    w = read_json(d / 'pilot/worker/verification.json')
    check(binding['before'] == binding['after'] == supervisor['source_binding'], 'whole source binding stable')
    check(binding['before']['source_commit'] == SOURCE and binding['before']['source_tree'] == EXPECTED_TREE, 'pilot Git binding')
    source_digests = binding['before']['source_sha256']
    check(len(source_digests) == 104 and binding['before']['frozen_files_verified'] == 100, 'source closure counts')
    for relative, expected in source_digests.items():
        check(digest(git('show', SOURCE + ':' + relative)) == expected, 'actual Git source ' + relative)
    check(supervisor['runtime_binding_sha256'] == sha(d / 'pilot/R3R_BINDING.json'), 'supervisor binding link')
    check(supervisor['worker_verification_sha256'] == sha(d / 'pilot/worker/verification.json'), 'supervisor verification link')
    check(binding['backend'] == 'numpy' and len(binding['comparator_calls']) == 1, 'actual comparator binding')
    check(w['same_h_parity'] == identity['verdict'], 'pilot vs benchmark same-h verdict')
    check(w['python_result']['extra_accepted'] == 32 and w['python_result']['full_evaluations'] == 128, 'pilot steps')
    check(w['status'] == 'SMOKE_ONLY' and w['python_result']['event'] is None, 'pilot smoke scope')
    check(supervisor['status'] == 'COMPLETED_SCOPED_SMOKE' and supervisor['exit_code'] == 0, 'supervisor result')
    check(sha(d / 'pilot/worker/native_h4_continuation') == w['native_binary_sha256'], 'native binary')
    check(sha(d / 'pilot/worker/liboriginal_full_source.so') == w['common_binary_sha256'], 'common binary')
    for filename, expected in w['partial_accepted_sha256'].items():
        check(sha(d / 'pilot/worker' / filename) == expected, 'accepted output')
    for filename, expected in w['modified_source_sha256'].items():
        check(sha(d / 'pilot/worker/source_extract/HyRec' / filename) == expected, 'actual extracted C source')
    for field in ('native_build', 'common_build', 'native_run'):
        record = w[field]
        check(record['returncode'] == 0, 'compiler/native exit')
        prefix = {'native_build': 'native_build', 'common_build': 'common_build', 'native_run': 'native_oracle'}[field]
        for kind in ('stdout', 'stderr'):
            suffix = '.csv' if field == 'native_run' and kind == 'stdout' else '.txt'
            check(sha(d / ('pilot/worker/' + prefix + '_' + kind + suffix)) == record[kind + '_sha256'], 'compiler/native log')
    same = read_json(REC / 'SAME_OUTPUT_CHECK.json')
    previous = RAW / 'profile32_repaired/worker'
    for filename, record in same['raw_files'].items():
        old_hash, new_hash = sha(previous / filename), sha(d / 'pilot/worker' / filename)
        check(old_hash == new_hash == record['old_sha256'] == record['new_sha256'], 'same raw output')
    old_arrays = read_npz_data(previous / 'python_continuation.npz')
    new_arrays = read_npz_data(d / 'pilot/worker/python_continuation.npz')
    for name, record in same['npz_fields'].items():
        check(old_arrays[name] == new_arrays[name], 'independent NPY payload equality')
        check(new_arrays[name]['sha256'] == record['new_sha256'], 'recorded NPY payload digest')
    previous_v = read_json(previous / 'verification.json')
    for field, record in same['semantic_verification_fields'].items():
        check(previous_v[field] == w[field] == record['value'], 'semantic output field')
    out['pilot'] = {'status': 'PASS_READBACK', 'source_files_verified_against_executed_Git': len(source_digests),
                    'backend': binding['backend'], 'extra_accepted': 32, 'full_evaluations': 128,
                    'scientific_status_preserved': w['status'], 'same_output_raw_files': len(same['raw_files']),
                    'same_output_npz_payload_fields': len(same['npz_fields']),
                    'worker_entry_limits': binding['worker_entry_limits'],
                    'supervision_cpu_s': supervisor['process_tree_cpu_s'], 'supervision_wall_s': supervisor['wall_s']}
    p = read_json(RAW / 'r3r_plots_001/PLOT_GENERATION.json')
    for record in list(p['inputs'].values()) + list(p['files'].values()):
        verify_file(record)
    check(digest(git('show', SOURCE + ':scripts/plot_r3r_audit.py')) == p['generator_source']['sha256'], 'plot source')
    check(p['display_and_data']['max_ratio_float_hex'] == max(lanes).hex(), 'plot max')
    out['plots'] = {'status': 'PASS_HASH_AND_DATA_READBACK', 'files_verified': len(p['files']),
                    'generation_receipt_sha256': sha(RAW / 'r3r_plots_001/PLOT_GENERATION.json'),
                    'original_visual_review_field': p['visual_review'],
                    'independent_human_like_visual_inspection': 'separately documented in C9 review'}
    norm = read_json(REC / 'TEXT_NORMALIZATION.json')
    checked_normalization = []
    for record in norm['changes']:
        before = git('show', SOURCE + ':' + record['path'])
        after = before.rstrip(b'\n') + b'\n'
        check(digest(before) == record['before_sha256'], 'normalization preimage')
        check(digest(after) == record['after_sha256'], 'normalization exact transform')
        row = {'path': record['path'], 'exact_EOF_only_transform': True}
        if record['path'].endswith('.py'):
            old_ast = ast.dump(ast.parse(before.decode()), include_attributes=True)
            new_ast = ast.dump(ast.parse(after.decode()), include_attributes=True)
            check(old_ast == new_ast, 'normalization AST equality')
            check(digest(old_ast.encode()) == record['ast_sha256'], 'normalization AST hash')
            row['AST_with_locations_identical'] = True
        checked_normalization.append(row)
    out['text_normalization'] = checked_normalization
    manifest = read_json(REC / 'RAW_LOGS_MANIFEST.json')
    check(sha(REC / 'FORMAL_RAW_LOGS.tar.gz') == manifest['archive_sha256'], 'raw log archive digest')
    with tarfile.open(REC / 'FORMAL_RAW_LOGS.tar.gz', 'r:gz') as archive:
        members = {m.name: m for m in archive.getmembers() if m.isfile()}
        check(set(members) == set(manifest['files']), 'raw log archive member set')
        for name, record in manifest['files'].items():
            content = archive.extractfile(members[name]).read()
            check(len(content) == record['size'] and digest(content) == record['sha256'] == sha(RAW / name), 'raw log archive member')
    out['archived_raw_logs_verified'] = len(manifest['files'])
    out['unique_local_files_hashed'] = len(HASHES)
    out['status'] = 'PASS_INDEPENDENT_EVIDENCE_READBACK'
    out['resources'] = {'self_cpu_s': time.process_time(), 'wall_s': time.monotonic() - began,
                        'self_peak_rss_bytes': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024,
                        'scope': 'readback auditor only; no solver, test suite or benchmark rerun'}
    target = REC / 'C9_EVIDENCE_READBACK.json'
    with target.open('x') as stream:
        json.dump(out, stream, indent=2, sort_keys=True)
        stream.write('\n')
    print(json.dumps({'status': out['status'], 'output': str(target), 'sha256': sha(target),
                      'verified_formal_raw_files': sum(x['verified_raw_files'] for x in out['formal_attempts'].values()),
                      'source_files': len(source_digests), 'differing_binary64_lanes': differing,
                      'median_paired_cpu_ratio': ratios['cpu'], 'resources': out['resources']}, sort_keys=True))


if __name__ == '__main__':
    main()
