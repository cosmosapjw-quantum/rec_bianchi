#!/usr/bin/env python3
"""Bounded new R3S contracts only; no REC trajectory or old campaign rerun.

The optional prior receipt carries failed-attempt cost forward. The fixed R3O
monitor is reused with a fork-local lower-only rlimit adapter; its clocks and
thresholds are unchanged. This parent is single-threaded.
"""
from __future__ import annotations

import resource
import time

ENTRY_WALL = time.monotonic()
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import platform
import re
import signal
import subprocess
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[3]
NODE = ROOT / 'research/rec_r3s_ncp_campaign_20261021'
CPU_S, WALL_S, MEMORY_BYTES = 60., 180., 2 * 1024**3


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def dump(path, value):
    with Path(path).open('x') as stream:
        json.dump(value, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write('\n')
        stream.flush()
        os.fsync(stream.fileno())


def lower(kind, requested):
    soft, hard = resource.getrlimit(kind)
    hard = requested if hard == resource.RLIM_INFINITY else min(requested, hard)
    soft = hard if soft == resource.RLIM_INFINITY else min(soft, hard)
    resource.setrlimit(kind, (soft, hard))


class LowerOnlyResource:
    def __getattr__(self, name):
        return getattr(resource, name)

    def setrlimit(self, kind, requested):
        soft, hard = resource.getrlimit(kind)
        rs, rh = requested
        hard = rh if hard == resource.RLIM_INFINITY else min(hard, rh)
        soft = rs if soft == resource.RLIM_INFINITY else min(soft, rs)
        resource.setrlimit(kind, (min(soft, hard), hard))


def closure(commit, paths):
    def git(*argv):
        return subprocess.check_output(['git', *argv], cwd=ROOT, timeout=10)
    if git('rev-parse', 'HEAD').decode().strip() != commit:
        raise ValueError('R3S_VALIDATION_SOURCE_HEAD_MISMATCH')
    records = {}
    for item in git('ls-tree', '-rz', commit, '--', *sorted(paths)).split(b'\0'):
        if not item:
            continue
        meta, raw_name = item.split(b'\t', 1)
        mode, kind, blob = meta.decode().split()
        name = raw_name.decode()
        content = (ROOT / name).read_bytes()
        observed = hashlib.sha1(b'blob '+str(len(content)).encode()+b'\0'+content).hexdigest()
        if kind != 'blob' or observed != blob:
            raise ValueError('R3S_VALIDATION_FIXED_GIT_BLOB_MISMATCH:'+name)
        records[name] = {'git_blob': blob, 'mode': mode, 'bytes': len(content),
                         'sha256': hashlib.sha256(content).hexdigest()}
    if set(records) != set(paths):
        raise ValueError('R3S_VALIDATION_SOURCE_CLOSURE_INCOMPLETE')
    return {'commit': commit, 'tree': git('rev-parse', commit+'^{tree}').decode().strip(),
            'files': records, 'file_count': len(records)}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--expected-commit', required=True)
    ap.add_argument('--output', type=Path, required=True)
    ap.add_argument('--allocation-id', required=True)
    ap.add_argument('--prior-receipt', type=Path)
    ap.add_argument('--prior-sha256')
    ap.add_argument('--test-node', action='append')
    args = ap.parse_args()
    if not re.fullmatch(r'[0-9a-f]{40}', args.expected_commit):
        raise ValueError('FULL_SOURCE_SHA_REQUIRED')
    if not re.fullmatch(r'REC_R3S_LOCAL_VALIDATION_[A-Z0-9_]+', args.allocation_id):
        raise ValueError('R3S_LOCAL_ALLOCATION_REQUIRED')
    out = args.output.resolve()
    if out == ROOT or ROOT in out.parents:
        raise ValueError('VALIDATION_OUTPUT_MUST_BE_OUTSIDE_FIXED_REPOSITORY')
    prior_cpu = prior_wall = 0.
    if bool(args.prior_receipt) != bool(args.prior_sha256):
        raise ValueError('PRIOR_RECEIPT_AND_SHA_REQUIRED_TOGETHER')
    if args.prior_receipt:
        if sha(args.prior_receipt) != args.prior_sha256:
            raise ValueError('PRIOR_RECEIPT_HASH_MISMATCH')
        prior = json.loads(args.prior_receipt.read_text())
        if prior['allocation_id'] != args.allocation_id or prior['total_envelope'] != {
                'cpu_s': CPU_S, 'wall_s': WALL_S, 'per_process_as_bytes': MEMORY_BYTES}:
            raise ValueError('PRIOR_ALLOCATION_IDENTITY_MISMATCH')
        prior_cpu, prior_wall = prior['process_tree_cpu_s'], prior['wall_s']
        if not (0 <= prior_cpu < CPU_S-2 and 0 <= prior_wall < WALL_S-3):
            raise ValueError('PRIOR_ALLOCATION_EXHAUSTED_OR_INVALID')
    out.mkdir(parents=True, exist_ok=False)
    cache = out / 'empty-supervisor-pycache'
    cache.mkdir()
    sys.pycache_prefix = str(cache)
    sys.dont_write_bytecode = True
    inherited = {'cpu': list(resource.getrlimit(resource.RLIMIT_CPU)),
                 'as': list(resource.getrlimit(resource.RLIMIT_AS))}
    lower(resource.RLIMIT_CPU, max(1, math.floor(CPU_S-prior_cpu)))
    lower(resource.RLIMIT_AS, MEMORY_BYTES)
    def expired(*_):
        raise TimeoutError('R3S_LOCAL_WHOLE_WALL_CAP')
    signal.signal(signal.SIGALRM, expired)
    signal.setitimer(signal.ITIMER_REAL, max(.001, WALL_S-prior_wall-(time.monotonic()-ENTRY_WALL)))
    sys.path.insert(0, str(ROOT / 'scripts'))
    import build_r3o_rust as support
    budget = support.Budget(out, cpu_s=CPU_S, wall_s=WALL_S, memory_bytes=MEMORY_BYTES)
    budget.start_cpu = -prior_cpu
    budget.start_wall = ENTRY_WALL-prior_wall
    nodes = args.test_node or ['tests/test_r3s_ncp_campaign.py']
    if any(not re.fullmatch(r'tests/test_r3s_ncp_campaign\.py(?:::[A-Za-z0-9_\[\].-]+)?', n) for n in nodes):
        raise ValueError('ONLY_NEW_R3S_TESTS_ALLOWED')
    record = {'schema': 'rec.r3s.local-validation.v1', 'status': 'FAILED',
              'allocation_id': args.allocation_id,
              'prior_receipt_sha256': args.prior_sha256,
              'prior_cpu_s': prior_cpu, 'prior_wall_s': prior_wall,
              'total_envelope': {'cpu_s': CPU_S, 'wall_s': WALL_S,
                                 'per_process_as_bytes': MEMORY_BYTES},
              'source_commit': args.expected_commit,
              'command_scope': 'new R3S dummy scheduler contracts only',
              'new_scientific_integrations': 0, 'new_accepted_steps': 0,
              'new_REC_benchmark_trials': 0, 'NCP_execution': 'NOT_RUN',
              'inherited_limits': inherited,
              'effective_limits': {'cpu': list(resource.getrlimit(resource.RLIMIT_CPU)),
                                   'as': list(resource.getrlimit(resource.RLIMIT_AS))},
              'environment': {'python': sys.version, 'executable': sys.executable,
                              'platform': platform.platform(), 'hostname': platform.node(),
                              'affinity': sorted(os.sched_getaffinity(0))},
              'wrapper_sha256': sha(__file__), 'first_failure': None,
              'wall_accounting': 'cumulative active supervised intervals, including preflight and final evidence hashing; editing pauses excluded'}
    code = 2
    try:
        budget.check()
        binding = json.loads((ROOT/'research/rec_r3r_followup_costs_20261020/receipts/formal_validation_002/pilot/R3R_BINDING.json').read_text())
        paths = set(binding['after']['source_sha256'])
        paths.update(['scripts/run_r3s_ncp_campaign.py', 'tests/test_r3s_ncp_campaign.py',
                      'scripts/benchmark_r3r_stream_audit.py', 'tests/test_r3r_stream_audit.py',
                      'research/rec_r3s_ncp_campaign_20261021/CAMPAIGN.json',
                      '.github/workflows/verify-r3s-ncp-campaign.yml', str(Path(__file__).relative_to(ROOT))])
        paths.update(str(p.relative_to(ROOT)) for p in (ROOT/'tests/fixtures/r3r_actual32').iterdir() if p.is_file())
        before = closure(args.expected_commit, paths)
        dump(out/'SOURCE_BEFORE.json', before)
        record['source_tree'] = before['tree']
        env = os.environ.copy()
        for name in ['OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS',
                     'NUMEXPR_NUM_THREADS', 'RAYON_NUM_THREADS']:
            env[name] = '1'
        env['PYTEST_DISABLE_PLUGIN_AUTOLOAD'] = '1'
        env.pop('PYTEST_ADDOPTS', None)
        env.pop('PYTEST_PLUGINS', None)
        child_cache = out/'empty-pytest-pycache'
        child_cache.mkdir()
        command = [sys.executable, '-B', '-X', 'pycache_prefix='+str(child_cache),
                   '-m', 'pytest', '-q', '-p', 'no:cacheprovider', *nodes,
                   '--basetemp='+str(out/'pytest-work'), '--junitxml='+str(out/'tests.xml')]
        original_resource = support.resource
        support.resource = LowerOnlyResource()
        try:
            budget.run(command, cwd=ROOT, env=env, label='tests')
        finally:
            support.resource = original_resource
        after = closure(args.expected_commit, paths)
        dump(out/'SOURCE_AFTER.json', after)
        if before != after:
            raise ValueError('R3S_VALIDATION_SOURCE_CHANGED')
        cases = ET.parse(out/'tests.xml').findall('.//testcase')
        counts = {'cases': len(cases), 'failures': sum(c.find('failure') is not None for c in cases),
                  'errors': sum(c.find('error') is not None for c in cases),
                  'skips': sum(c.find('skipped') is not None for c in cases)}
        counts['passes'] = counts['cases']-counts['failures']-counts['errors']-counts['skips']
        record['test_counts'] = counts
        if counts['passes'] < 1 or counts['failures'] or counts['errors']:
            raise ValueError('R3S_VALIDATION_JUNIT_GATE')
        record.update(status='COMPLETED_SCOPED', source_input_identity='UNCHANGED',
                      source_files_verified=len(paths))
        code = 0
    except BaseException as exc:
        record['first_failure'] = {'type': type(exc).__name__, 'message': str(exc)}
    finally:
        record['commands'] = budget.commands
        record['evidence_sha256'] = {str(p.relative_to(out)): sha(p) for p in sorted(out.rglob('*'))
                                    if p.is_file() and p.suffix != '.pyc'}
        code = support.finalize_resource_record(record, budget, code, 'R3S_LOCAL_VALIDATION')
        record['new_execution_cpu_s'] = record['process_tree_cpu_s']-prior_cpu
        record['new_execution_wall_s'] = record['wall_s']-prior_wall
        dump(out/'validation.json', record)
        signal.setitimer(signal.ITIMER_REAL, 0.)
    print(json.dumps({'status': record['status'], 'exit_code': code,
                      'process_tree_cpu_s': record['process_tree_cpu_s'], 'wall_s': record['wall_s'],
                      'first_failure': record['first_failure'], 'receipt': str(out/'validation.json')}))
    return code


if __name__ == '__main__':
    raise SystemExit(main())
