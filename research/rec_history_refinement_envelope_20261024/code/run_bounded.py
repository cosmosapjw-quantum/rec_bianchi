"""Single-child controller with cumulative remaining-allocation checks.

Adapted from the retained02R runner. This module imports no numerical library.
CPU enforcement is process-local RLIMIT_CPU; resource accounting is post-exit
inclusive RUSAGE_CHILDREN. No live aggregate enforcement is claimed.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import resource
import shutil
import signal
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
THREADS = ['OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS', 'NUMEXPR_NUM_THREADS', 'VECLIB_MAXIMUM_THREADS']
ALLOCATIONS = {'primary': (16.0, 45.0), 'review': (6.0, 15.0), 'figures': (8.0, 30.0)}


def write(p, d):
    p.write_text(json.dumps(d, indent=2, allow_nan=False)+'\n')


def snapshot(out):
    rows = []
    paths = [p for folder in ['code', 'inputs'] for p in (ROOT/folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts]
    paths += [ROOT/n for n in ['FROZEN_CONTRACT.md', 'THEORY.md', 'ENVIRONMENT.json']]
    for p in sorted(paths):
        b = p.read_bytes()
        rel = p.relative_to(ROOT)
        target = out/'source_snapshot'/rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(b)
        rows.append({'path': str(rel), 'bytes': len(b), 'sha256': hashlib.sha256(b).hexdigest()})
    write(out/'SOURCE_INPUT_SNAPSHOT.json', rows)
    return rows


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--cpu', type=float, required=True)
    p.add_argument('--wall', type=float, required=True)
    p.add_argument('label')
    p.add_argument('command', nargs=argparse.REMAINDER)
    a = p.parse_args()
    phase = next((s for s in ALLOCATIONS if a.label.startswith(s)), None)
    if phase is None or '/' in a.label or not a.command or a.cpu <= 0 or a.wall <= 0:
        raise ValueError('BOUNDED_COMMAND_REQUIRED')
    previous = []
    for path in (ROOT/'execution').glob('*/RESOURCE_RECEIPT.json'):
        previous.append(json.loads(path.read_text()))
    # Unfinished prior attempts have no accountable remaining budget: return.
    for path in (ROOT/'execution').glob('*/COMMAND.json'):
        if not (path.parent/'RESOURCE_RECEIPT.json').exists():
            raise ValueError('PRIOR_ATTEMPT_INCOMPLETE_RETURN_TO_ASTRA')
    spent_cpu = sum(r['inclusive_cpu_seconds'] for r in previous)
    spent_wall = sum(r['wall_seconds'] for r in previous)
    phase_cpu = sum(r['inclusive_cpu_seconds'] for r in previous if r['phase'] == phase)
    phase_wall = sum(r['wall_seconds'] for r in previous if r['phase'] == phase)
    cpu = min(a.cpu, 30-spent_cpu, ALLOCATIONS[phase][0]-phase_cpu)
    wall = min(a.wall, 90-spent_wall, ALLOCATIONS[phase][1]-phase_wall)
    # Integer rlimit is rounded down, never beyond the remaining budget.
    cap = math.floor(cpu)
    if cap < 1 or wall <= 0:
        raise ValueError('BUDGET_EXHAUSTED_RETURN_TO_ASTRA')
    out = ROOT/'execution'/a.label
    out.mkdir(parents=True, exist_ok=False)
    rows = snapshot(out)
    env = os.environ.copy()
    env.update({k: '1' for k in THREADS})
    env['PYTHONDONTWRITEBYTECODE'] = '1'
    env['MPLCONFIGDIR'] = str(out/'matplotlib_config')
    env['MPLBACKEND'] = 'Agg'
    info = {'label': a.label, 'phase': phase, 'command': a.command, 'cwd': str(ROOT),
            'environment': {k: env[k] for k in THREADS+['PYTHONDONTWRITEBYTECODE', 'MPLCONFIGDIR', 'MPLBACKEND']},
            'started_utc': datetime.now(timezone.utc).isoformat(), 'cpu_cap': cap, 'wall_cap': wall,
            'requested_cpu_cap': a.cpu, 'requested_wall_cap': a.wall, 'address_space_cap_bytes': 1024**3,
            'cumulative_prior_cpu_seconds': spent_cpu, 'cumulative_prior_wall_seconds': spent_wall,
            'requested_executor_role': 'lower-tier mechanical implementation/run owner', 'tool_observed_model': None}
    write(out/'COMMAND.json', info)
    def limits():
        resource.setrlimit(resource.RLIMIT_CPU, (cap, cap))
        resource.setrlimit(resource.RLIMIT_AS, (1024**3, 1024**3))
        os.setsid()
    before = resource.getrusage(resource.RUSAGE_CHILDREN)
    started = time.monotonic()
    timed_out, rc, failure = False, None, None
    try:
        with (out/'stdout.txt').open('xb') as stdout, (out/'stderr.txt').open('xb') as stderr:
            child = subprocess.Popen(a.command, cwd=ROOT, env=env, stdout=stdout, stderr=stderr, preexec_fn=limits)
            try:
                rc = child.wait(timeout=wall)
            except subprocess.TimeoutExpired:
                timed_out = True
                os.killpg(child.pid, signal.SIGKILL)
                rc = child.wait()
    except Exception as exc:
        failure = repr(exc)
    elapsed = time.monotonic()-started
    after = resource.getrusage(resource.RUSAGE_CHILDREN)
    cpu_used = after.ru_utime+after.ru_stime-before.ru_utime-before.ru_stime
    receipt = {**info, 'returncode': rc, 'timed_out': timed_out, 'controller_exception': failure,
               'wall_seconds': elapsed, 'inclusive_cpu_seconds': cpu_used,
               'child_peak_rss_KiB': after.ru_maxrss, 'finished_utc': datetime.now(timezone.utc).isoformat(),
               'measurement': 'postexit inclusive RUSAGE_CHILDREN delta CPU; process-scope RSS highwater',
               'enforcement': 'process-local CPU/AS limits, process-group wall timeout, cumulative remaining allocation checked before launch',
               'live_aggregate_monitor': False, 'post_snapshot_changed': []}
    for row in rows:
        q = ROOT/row['path']
        if not q.exists() or hashlib.sha256(q.read_bytes()).hexdigest() != row['sha256']:
            receipt['post_snapshot_changed'].append(row['path'])
    write(out/'RESOURCE_RECEIPT.json', receipt)
    ledger_path = ROOT/'BUDGET_LEDGER.json'
    ledger = json.loads(ledger_path.read_text())
    ledger['local_executions'].append({'label': a.label, 'phase': phase, 'resource_receipt': str(out.relative_to(ROOT)/'RESOURCE_RECEIPT.json'),
                                       'cpu_seconds': cpu_used, 'execution_wall_seconds': elapsed, 'returncode': rc,
                                       'status': 'CHILD_EXIT_ZERO' if rc == 0 else 'FAILED_RETURN_TO_ASTRA'})
    ledger['spent'] = {'cpu_seconds': spent_cpu+cpu_used, 'execution_wall_seconds': spent_wall+elapsed}
    ledger['remaining'] = {'cpu_seconds': 30-spent_cpu-cpu_used, 'execution_wall_seconds': 90-spent_wall-elapsed}
    ledger['allocation_remaining'] = {}
    for name, (lcpu, lwall) in ALLOCATIONS.items():
        records = previous+[receipt]
        ledger['allocation_remaining'][name] = {'cpu_seconds': lcpu-sum(r['inclusive_cpu_seconds'] for r in records if r['phase'] == name),
                                                'wall_seconds': lwall-sum(r['wall_seconds'] for r in records if r['phase'] == name)}
    write(ledger_path, ledger)
    print(json.dumps(receipt, indent=2, allow_nan=False))
    return 1 if rc is None else rc if rc >= 0 else 128-rc


if __name__ == '__main__':
    sys.exit(main())
