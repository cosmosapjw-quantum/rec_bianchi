#!/usr/bin/env python3
"""Execute the frozen HD child only after parent C4 GO; preserve every attempt."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import resource
import signal
import subprocess
import sys
import time

OWN = Path(__file__).resolve().parent
SOURCE = Path('/workspace/scratch/6104ad84b826/survey_literature/lamda_hd_live.dat')
PRIMARY_CPU_S = 60
PRIMARY_WALL_S = 180
RSS_LIMIT_BYTES = 2 * 1024**3
UNIT_CPU_CAP_S = 360


def utc():
    return datetime.now(timezone.utc).isoformat()


def save(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2, allow_nan=False) + '\n')


def limits():
    os.setsid()
    resource.setrlimit(resource.RLIMIT_CPU, (PRIMARY_CPU_S, PRIMARY_CPU_S))
    resource.setrlimit(resource.RLIMIT_AS, (RSS_LIMIT_BYTES, RSS_LIMIT_BYTES))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--attempt', required=True, help='unique new attempt directory basename')
    parser.add_argument('--go', required=True, choices=['C4_GO'], help='parent C4 GO must precede invocation')
    args = parser.parse_args()
    if Path(args.attempt).name != args.attempt or args.attempt in ('', '.', '..'):
        parser.error('attempt must be a simple unique basename')
    cpu_start, wall_start = time.process_time(), time.perf_counter()
    raw = OWN / 'raw'
    raw.mkdir(exist_ok=True)
    prior = []
    spent = 0.0
    for p in sorted(raw.glob('*/EXECUTION.json')):
        receipt = json.loads(p.read_text())
        value = receipt.get('total_debit_cpu_s')
        if not isinstance(value, (float, int)):
            raise RuntimeError('Unbounded previous scientific CPU tail requires parent decision: ' + str(p))
        spent += value
        prior.append({'path': p.relative_to(OWN).as_posix(), 'total_debit_cpu_s': value})
    if spent + PRIMARY_CPU_S > UNIT_CPU_CAP_S:
        raise RuntimeError('HD cumulative remaining cap cannot admit this frozen primary allocation')
    out = raw / args.attempt
    out.mkdir(exist_ok=False)
    command = [sys.executable, str(OWN / 'run_diagnostic.py'), '--source', str(SOURCE), '--output', str(out)]
    env = os.environ.copy()
    thread_keys = ['OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS', 'NUMEXPR_NUM_THREADS', 'VECLIB_MAXIMUM_THREADS', 'BLIS_NUM_THREADS']
    for key in thread_keys:
        env[key] = '1'
    env['MPLBACKEND'] = 'Agg'
    env['MPLCONFIGDIR'] = str(out / 'mpl_config')
    env['PYTHONDONTWRITEBYTECODE'] = '1'
    identities = []
    repo = OWN.parents[2]
    paths = sorted(OWN.glob('*.py')) + [OWN.parent / 'CODING_CONTRACT.md', OWN.parent / 'THEORY.md', OWN.parent / 'EXECUTION_FREEZE.json', SOURCE, repo / 'research/program_expansion_20261025/hd_adapter/lamda_hd.py', repo / 'research/program_expansion_20261025/hd_adapter/raw/source_diagnostic/diagnostics.json']
    for p in paths:
        data = p.read_bytes()
        identities.append({'path': str(p), 'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()})
    preexec = {'schema': 'REC_HD_JOINT_PREEXEC_V1', 'start_utc': utc(), 'command': command, 'cwd': str(repo), 'inputs_and_code': identities, 'limits': {'child_cpu_s': PRIMARY_CPU_S, 'child_wall_s': PRIMARY_WALL_S, 'address_space_bytes': RSS_LIMIT_BYTES, 'threads': 1, 'unit_cumulative_cpu_cap_s': UNIT_CPU_CAP_S}, 'previous_debits': prior, 'previous_debit_cpu_s': spent, 'thread_environment': {key: env[key] for key in thread_keys}, 'environment': {'python': sys.version, 'platform': platform.platform()}, 'requested_execution_identity': 'lower-tier mechanical implementation executor', 'observed_runtime_identity': 'UNKNOWN_NOT_EXPOSED', 'authorization': 'Parent C4 GO required externally; explicit --go C4_GO supplied', 'historical_budget_reset': False, 'new_IVP': False}
    save(out / 'PREEXEC.json', preexec)
    before = resource.getrusage(resource.RUSAGE_CHILDREN)
    child_start = time.perf_counter()
    timed_out = False
    spawn_error = None
    with (out / 'targeted_run.stdout.txt').open('w') as stdout, (out / 'targeted_run.stderr.txt').open('w') as stderr:
        try:
            child = subprocess.Popen(command, cwd=repo, env=env, stdout=stdout, stderr=stderr, preexec_fn=limits)
            try:
                code = child.wait(timeout=PRIMARY_WALL_S)
            except subprocess.TimeoutExpired:
                timed_out = True
                os.killpg(child.pid, signal.SIGKILL)
                code = child.wait()
        except OSError as exc:
            code = 127
            spawn_error = repr(exc)
            stderr.write(spawn_error + '\n')
    child_wall = time.perf_counter() - child_start
    after = resource.getrusage(resource.RUSAGE_CHILDREN)
    child_cpu = (after.ru_utime - before.ru_utime) + (after.ru_stime - before.ru_stime)
    wrapper_cpu = time.process_time() - cpu_start
    debit = child_cpu + wrapper_cpu
    receipt = {'schema': 'REC_HD_JOINT_EXECUTION_V1', 'start_utc': preexec['start_utc'], 'end_utc': utc(), 'command': command, 'exit_code': code, 'wall_timeout': timed_out, 'spawn_error': spawn_error, 'child_inclusive_cpu_s': child_cpu, 'child_user_cpu_s': after.ru_utime - before.ru_utime, 'child_system_cpu_s': after.ru_stime - before.ru_stime, 'child_wall_s': child_wall, 'child_peak_rss_KiB': after.ru_maxrss, 'wrapper_cpu_s': wrapper_cpu, 'wrapper_wall_s': time.perf_counter() - wall_start, 'total_debit_cpu_s': debit, 'unit_previous_debit_cpu_s': spent, 'unit_cumulative_debit_cpu_s': spent + debit, 'unit_remaining_cpu_s': UNIT_CPU_CAP_S - spent - debit, 'measurement_tail': 'Final receipt serialization is unmeasured metadata overhead UNKNOWN_NOT_ZERO; no scientific child remains.', 'limits': preexec['limits'], 'requested_execution_identity': preexec['requested_execution_identity'], 'observed_runtime_identity': 'UNKNOWN_NOT_EXPOSED', 'historical_runs_replayed': 0, 'scientific_status': 'READ_SAVED_DIAGNOSTICS_AND_CONTROLS; EXIT_ZERO_DOES_NOT_PROMOTE_SOURCE_GATE'}
    save(out / 'EXECUTION.json', receipt)
    print(json.dumps(receipt))
    return code if code >= 0 else 128 - code


if __name__ == '__main__':
    raise SystemExit(main())
