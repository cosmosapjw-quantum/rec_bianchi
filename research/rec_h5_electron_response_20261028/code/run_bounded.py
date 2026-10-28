"""Execute one new-response stage with cumulative child CPU accounting."""
import argparse
import datetime
import hashlib
import importlib.metadata
import json
import math
import os
from pathlib import Path
import platform
import resource
import signal
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('stage', choices=['C6', 'C7', 'C8', 'C8_NATIVE', 'PLOTS'])
    parser.add_argument('--attempt', default='001')
    args = parser.parse_args()
    out = ROOT / 'execution' / (args.stage + '_attempt' + args.attempt)
    out.mkdir(parents=True, exist_ok=False)
    ledger_path = ROOT / 'execution/RESOURCE_LEDGER.json'
    ledger = json.loads(ledger_path.read_text()) if ledger_path.exists() else {
        'schema': 'REC_ELECTRON_RESPONSE_RESOURCES_V1', 'CPU_cap_s': 60,
        'child_wall_cap_s': 30, 'address_space_MiB': 512,
        'prior_unit_budget_transfer': False, 'new_native_calls': 0, 'runs': [],
        'other_costs': 'parent/model/network/metadata/packaging UNKNOWN_NOT_ZERO'}
    used = sum(r['user_CPU_s'] + r['system_CPU_s'] for r in ledger['runs'])
    remaining = 60 - used
    # Prospective C9 improvement. Integer RLIMIT_CPU needs headroom; never
    # authorize a one-second child from a sub-second remaining budget.
    cap = min(30, math.floor(remaining) - 1)
    if cap < 1:
        raise SystemExit('INSUFFICIENT_CPU_BUDGET_WITH_ONE_SECOND_RESERVE')
    env = dict(os.environ)
    for key in ['OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS',
                'NUMEXPR_NUM_THREADS', 'VECLIB_MAXIMUM_THREADS']:
        env[key] = '1'
    env['MPLCONFIGDIR'] = str(ROOT / 'execution/matplotlib_cache')
    env['PYTHONDONTWRITEBYTECODE'] = '1'
    command = [sys.executable, str(ROOT / 'code/study.py'), args.stage, str(out)]
    snapshot = {
        'captured_UTC': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'scope': 'PROSPECTIVE_PRE_EXECUTION_SNAPSHOT',
        'Python': sys.version, 'executable': sys.executable,
        'platform': platform.platform(), 'libc': platform.libc_ver(),
        'packages': {n: importlib.metadata.version(n)
                     for n in ('numpy', 'scipy', 'matplotlib')},
        'code_SHA256': {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                       for p in sorted((ROOT / 'code').glob('*.py'))},
        'input_manifest_SHA256': hashlib.sha256(
            (ROOT / 'INPUT_MANIFEST.json').read_bytes()).hexdigest(),
        'child_environment_overrides': {k: env[k] for k in (
            'OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS',
            'NUMEXPR_NUM_THREADS', 'VECLIB_MAXIMUM_THREADS',
            'MPLCONFIGDIR', 'PYTHONDONTWRITEBYTECODE')},
    }
    snapshot_path = out / 'PRE_EXECUTION_SNAPSHOT.json'
    snapshot_path.write_text(json.dumps(snapshot, indent=2) + '\n')
    def limits():
        os.setsid()
        resource.setrlimit(resource.RLIMIT_CPU, (cap, cap))
        resource.setrlimit(resource.RLIMIT_AS, (512 * 1024**2, 512 * 1024**2))
    start = time.monotonic()
    timed_out = False
    with (out / 'stdout.txt').open('wb') as stdout, (out / 'stderr.txt').open('wb') as stderr:
        child = subprocess.Popen(command, cwd=ROOT, env=env, preexec_fn=limits,
                                 stdout=stdout, stderr=stderr)
        while True:
            pid, status, usage = os.wait4(child.pid, os.WNOHANG)
            if pid:
                break
            if time.monotonic() - start > 30:
                os.killpg(child.pid, signal.SIGKILL)
                pid, status, usage = os.wait4(child.pid, 0)
                timed_out = True
                break
            time.sleep(0.025)
        child.returncode = os.waitstatus_to_exitcode(status)
    receipt = {
        'stage': args.stage, 'attempt': args.attempt, 'command': command,
        'exit_code': child.returncode, 'wall_s': time.monotonic() - start,
        'user_CPU_s': usage.ru_utime, 'system_CPU_s': usage.ru_stime,
        'max_RSS_KiB': usage.ru_maxrss, 'timed_out': timed_out,
        'CPU_limit_s': cap, 'wall_limit_s': 30, 'RLIMIT_AS_bytes': 512 * 1024**2,
        'single_thread': True, 'new_native_calls': 0,
        'snapshot_path': str(snapshot_path.relative_to(ROOT)),
        'snapshot_SHA256': hashlib.sha256(snapshot_path.read_bytes()).hexdigest(),
        'CPU_reserve_policy': 'floor(remaining)-1; soft=hard; measured total checked after exit',
    }
    ledger['runs'].append(receipt)
    ledger['known_child_CPU_s'] = sum(r['user_CPU_s'] + r['system_CPU_s'] for r in ledger['runs'])
    ledger['remaining_CPU_s'] = 60 - ledger['known_child_CPU_s']
    ledger_path.write_text(json.dumps(ledger, indent=2) + '\n')
    (out / 'RESOURCE_RECEIPT.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps(receipt))
    if child.returncode != 0 or ledger['remaining_CPU_s'] < 0:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
