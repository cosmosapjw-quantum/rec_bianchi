"""Execute one preserved attempt under the cumulative REC-HISTORY-01 allocation."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import resource
import shutil
import signal
import subprocess
import time

ROOT = Path(__file__).resolve().parents[1]
CPU_LIMIT, WALL_LIMIT, RSS_LIMIT = 60.0, 180.0, 1024**3


def session_usage(session):
    """Live session CPU includes already-waited descendants, without double counting."""
    ticks, rss = 0, 0
    for entry in Path('/proc').iterdir():
        if not entry.name.isdecimal():
            continue
        try:
            fields = (entry/'stat').read_text().rsplit(') ', 1)[1].split()
            if int(fields[3]) != session:
                continue
            ticks += sum(int(fields[i]) for i in (11, 12, 13, 14))
            rss += int(fields[21])*os.sysconf('SC_PAGE_SIZE')
        except (OSError, ValueError, IndexError):
            continue
    return ticks/os.sysconf('SC_CLK_TCK'), rss


def cpu_usage(kind):
    r = resource.getrusage(kind)
    return r.ru_utime+r.ru_stime


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--label', required=True)
    parser.add_argument('--timeout', type=float, default=90.0)
    parser.add_argument('command', nargs=argparse.REMAINDER)
    args = parser.parse_args()
    command = args.command[1:] if args.command[:1] == ['--'] else args.command
    if not command or '/' in args.label or args.label in ('.', '..'):
        raise ValueError('explicit command and simple unique attempt label required')
    previous = [json.loads(p.read_text()) for p in (ROOT/'execution').glob('*/RESOURCE_RECEIPT.json')]
    used_cpu = sum(r['charged_cpu_seconds'] for r in previous)
    used_wall = sum(r['wall_seconds'] for r in previous)
    remaining_cpu, remaining_wall = CPU_LIMIT-used_cpu, WALL_LIMIT-used_wall
    if min(remaining_cpu, remaining_wall, args.timeout) <= 0:
        raise RuntimeError('cumulative allocation exhausted')
    attempt = ROOT/'execution'/args.label
    attempt.mkdir(parents=True, exist_ok=False)
    snapshot = attempt/'source_snapshot'
    identities = {}
    for p in [ROOT/'FROZEN_CONTRACT.md', ROOT/'PREEXEC_ADDENDUM.md', *sorted((ROOT/'code').glob('*.py'))]:
        relative = p.relative_to(ROOT)
        target = snapshot/relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(p, target)
        identities[str(relative)] = hashlib.sha256(p.read_bytes()).hexdigest()
    env = os.environ.copy()
    for name in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','BLIS_NUM_THREADS',
                 'VECLIB_MAXIMUM_THREADS','NUMEXPR_NUM_THREADS'):
        env[name] = '1'
    env['MPLCONFIGDIR'] = str(attempt/'matplotlib_cache')
    env['PYTHONDONTWRITEBYTECODE'] = '1'

    def limits():
        # Address-space bound is stricter than the requested per-process RSS cap.
        resource.setrlimit(resource.RLIMIT_AS, (RSS_LIMIT, RSS_LIMIT))
        hard_cpu = max(1, math.ceil(remaining_cpu))
        resource.setrlimit(resource.RLIMIT_CPU, (hard_cpu, hard_cpu))

    start_cpu = cpu_usage(resource.RUSAGE_CHILDREN)
    start_self = cpu_usage(resource.RUSAGE_SELF)
    start = time.perf_counter()
    kill_reason = None
    peak_live_rss = 0
    peak_live_cpu = 0.0
    with (attempt/'stdout.log').open('x') as stdout, (attempt/'stderr.log').open('x') as stderr:
        process = subprocess.Popen(command, stdout=stdout, stderr=stderr, env=env,
                                   start_new_session=True, preexec_fn=limits)
        while process.poll() is None:
            live_cpu, live_rss = session_usage(process.pid)
            peak_live_cpu = max(peak_live_cpu, live_cpu)
            peak_live_rss = max(peak_live_rss, live_rss)
            elapsed = time.perf_counter()-start
            self_cpu = cpu_usage(resource.RUSAGE_SELF)-start_self
            if elapsed > min(args.timeout, remaining_wall):
                kill_reason = 'WALL_LIMIT'
            elif live_cpu+self_cpu > remaining_cpu:
                kill_reason = 'CPU_LIMIT'
            elif live_rss > RSS_LIMIT:
                kill_reason = 'SESSION_RSS_LIMIT'
            if kill_reason:
                os.killpg(process.pid, signal.SIGKILL)
                break
            time.sleep(.025)
        returncode = process.wait()
    wall = time.perf_counter()-start
    child_cpu = cpu_usage(resource.RUSAGE_CHILDREN)-start_cpu
    controller_cpu = cpu_usage(resource.RUSAGE_SELF)-start_self
    charged_cpu = child_cpu+controller_cpu
    child_rusage = resource.getrusage(resource.RUSAGE_CHILDREN)
    receipt = dict(label=args.label, command=command, cwd=os.getcwd(), returncode=returncode,
                   kill_reason=kill_reason, wall_seconds=wall, child_cpu_seconds=child_cpu,
                   controller_cpu_seconds=controller_cpu, charged_cpu_seconds=charged_cpu,
                   child_peak_rss_KiB=child_rusage.ru_maxrss, peak_live_session_rss_bytes=peak_live_rss,
                   peak_live_session_cpu_seconds=peak_live_cpu, threads=1,
                   cpu_before_seconds=used_cpu, wall_before_seconds=used_wall,
                   cumulative_cpu_seconds=used_cpu+charged_cpu, cumulative_wall_seconds=used_wall+wall,
                   allocation=dict(cpu_seconds=CPU_LIMIT,wall_seconds=WALL_LIMIT,rss_bytes=RSS_LIMIT),
                   enforcement='90s maximum primary wall, cumulative live session CPU, session RSS, per-process RLIMIT_AS and RLIMIT_CPU',
                   pythonpath=env.get('PYTHONPATH'), source_sha256=identities,
                   status='PASS_RESOURCE' if kill_reason is None and used_cpu+charged_cpu <= CPU_LIMIT
                   and used_wall+wall <= WALL_LIMIT and child_rusage.ru_maxrss*1024 <= RSS_LIMIT else 'FAILED_PRESERVED')
    (attempt/'RESOURCE_RECEIPT.json').write_text(json.dumps(receipt, indent=2)+'\n')
    print(json.dumps(receipt, indent=2))
    return returncode if returncode else (0 if receipt['status']=='PASS_RESOURCE' else 1)


if __name__ == '__main__':
    raise SystemExit(main())
