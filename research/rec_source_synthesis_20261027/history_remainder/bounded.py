"""Frozen one-thread bounded child process and actual cumulative cost receipt."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import resource
import signal
import subprocess
import sys
import time

HERE=Path(__file__).resolve().parent
THREAD_KEYS=('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS',
             'VECLIB_MAXIMUM_THREADS','BLIS_NUM_THREADS')


def utc():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def main():
    if len(sys.argv)!=2 or sys.argv[1] not in ('primary','plot'):
        raise SystemExit('usage: python bounded.py {primary|plot}')
    phase=sys.argv[1];freeze=json.loads((HERE/'freeze.json').read_text())
    config=freeze['phases'][phase];evidence=HERE/'evidence';evidence.mkdir(exist_ok=True)
    receipt_path=evidence/(phase+'001.receipt.json')
    if receipt_path.exists():
        raise SystemExit('NO_BLIND_REPLAY: receipt already exists')
    previous=[]
    for path in evidence.glob('*.receipt.json'):
        previous.append(json.loads(path.read_text()))
    if any(r['controlled_cpu_s']=='UNKNOWN_NOT_ZERO' for r in previous):
        raise SystemExit('UNKNOWN_PREVIOUS_DEBIT: stop for authority')
    prior=sum(r['controlled_cpu_s'] for r in previous)
    if prior+config['cpu_limit_s']>freeze['cumulative_cpu_limit_s']:
        raise SystemExit('CUMULATIVE_BUDGET_INSUFFICIENT')
    start=utc();clock=time.monotonic();self_before=resource.getrusage(resource.RUSAGE_SELF)
    child_before=resource.getrusage(resource.RUSAGE_CHILDREN)
    receipt=dict(schema='REC_HISTORY_BOUNDED_RECEIPT_V1',phase=phase,start_utc=start,
                 command=config['command'],cwd=str(HERE),cpu_limit_s=config['cpu_limit_s'],
                 wall_limit_s=config['wall_limit_s'],memory_limit_bytes=freeze['memory_limit_bytes'],
                 cumulative_cap_s=freeze['cumulative_cpu_limit_s'],prior_controlled_cpu_s=prior,
                 requested_model='gpt-6.1-sol',actual_runtime_model='UNKNOWN_NOT_EXPOSED',
                 frozen_code_and_input_identities=freeze['identities'],status='ERROR',exit_code=None,
                 non_scientific_metadata_io_cost='UNKNOWN_NOT_ZERO')
    env=os.environ.copy();env.update({key:'1' for key in THREAD_KEYS})
    env.update(PYTHONHASHSEED='0',MPLBACKEND='Agg',MPLCONFIGDIR=str(HERE/'evidence'/'mplconfig'))
    receipt['environment']={key:env[key] for key in (*THREAD_KEYS,'PYTHONHASHSEED','MPLBACKEND','MPLCONFIGDIR')}
    def limits():
        resource.setrlimit(resource.RLIMIT_CPU,(config['cpu_limit_s'],config['cpu_limit_s']))
        resource.setrlimit(resource.RLIMIT_AS,(freeze['memory_limit_bytes'],freeze['memory_limit_bytes']))
    try:
        for item in freeze['identities']:
            path=Path(item['path']);data=path.read_bytes()
            if len(data)!=item['bytes'] or hashlib.sha256(data).hexdigest()!=item['sha256']:
                raise ValueError('FROZEN_IDENTITY_MISMATCH:'+str(path))
        with (evidence/(phase+'001.stdout.txt')).open('w') as stdout, (evidence/(phase+'001.stderr.txt')).open('w') as stderr:
            process=subprocess.Popen(config['command'],cwd=HERE,env=env,stdout=stdout,stderr=stderr,
                                     preexec_fn=limits,start_new_session=True)
            try:
                receipt['exit_code']=process.wait(timeout=config['wall_limit_s'])
            except subprocess.TimeoutExpired:
                os.killpg(process.pid,signal.SIGKILL);process.wait()
                receipt['exit_code']=process.returncode;receipt['error']='WALL_TIMEOUT'
            receipt['status']='PASS' if receipt['exit_code']==0 else 'FAILED_ATTEMPT_PRESERVED'
    except Exception as exc:
        receipt['error']=repr(exc)
    finally:
        child_after=resource.getrusage(resource.RUSAGE_CHILDREN);self_after=resource.getrusage(resource.RUSAGE_SELF)
        child_cpu=(child_after.ru_utime+child_after.ru_stime)-(child_before.ru_utime+child_before.ru_stime)
        supervisor_cpu=(self_after.ru_utime+self_after.ru_stime)-(self_before.ru_utime+self_before.ru_stime)
        receipt.update(end_utc=utc(),wall_s=time.monotonic()-clock,child_cpu_s=child_cpu,
                       supervisor_cpu_s=supervisor_cpu,controlled_cpu_s=child_cpu+supervisor_cpu,
                       cumulative_controlled_cpu_s=prior+child_cpu+supervisor_cpu,
                       child_max_rss_kib=child_after.ru_maxrss,supervisor_max_rss_kib=self_after.ru_maxrss)
        receipt['output_identities']=[]
        for directory in (HERE/'results',HERE/'figures'):
            if directory.exists():
                for path in sorted(directory.rglob('*')):
                    if path.is_file():
                        data=path.read_bytes();receipt['output_identities'].append(dict(path=str(path.relative_to(HERE)),bytes=len(data),sha256=hashlib.sha256(data).hexdigest()))
        receipt_path.write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
        print(json.dumps(receipt,sort_keys=True))
    if receipt['status']!='PASS':
        raise SystemExit(1)


if __name__=='__main__':
    main()
