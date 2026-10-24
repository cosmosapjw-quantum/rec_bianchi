"""Single-child execution controller; no numerical libraries imported here.

Use only after root GO. Example:
python code/run_bounded.py --cpu 16 --wall 45 primary001 python code/verify_primary.py --output results/primary001
Measured postexit child rusage includes descendants waited for by that child;
no live aggregate monitor is claimed. The intended commands spawn no children.
"""
import argparse,hashlib,json,math,os,resource,shutil,signal,subprocess,sys,time
from datetime import datetime,timezone
from pathlib import Path
R=Path(__file__).resolve().parents[1]
THREAD_KEYS=['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS','VECLIB_MAXIMUM_THREADS']

def snapshot(out):
    rows=[]
    for folder in ['code','inputs','vendor']:
        for p in sorted((R/folder).rglob('*')):
            if not p.is_file() or '__pycache__' in p.parts:continue
            data=p.read_bytes();rel=p.relative_to(R);dest=out/'source_snapshot'/rel;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data)
            rows.append({'path':str(rel),'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()})
    for p in [R/'FROZEN_CONTRACT.md']:
        data=p.read_bytes();dest=out/'source_snapshot'/p.name;dest.write_bytes(data);rows.append({'path':p.name,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()})
    (out/'SOURCE_INPUT_SNAPSHOT.json').write_text(json.dumps(rows,indent=2)+'\n');return rows

def main():
    p=argparse.ArgumentParser();p.add_argument('--cpu',type=int,required=True);p.add_argument('--wall',type=float,required=True);p.add_argument('label');p.add_argument('command',nargs=argparse.REMAINDER);a=p.parse_args()
    if not a.command or a.cpu<=0 or a.wall<=0:raise ValueError('BOUNDED_COMMAND_REQUIRED')
    if '/' in a.label or a.label in ['.','..']:raise ValueError('LABEL_MUST_BE_SIMPLE')
    out=R/'execution'/a.label;out.mkdir(parents=True,exist_ok=False);snapshot(out)
    env=os.environ.copy();env.update({k:'1' for k in THREAD_KEYS});env['PYTHONDONTWRITEBYTECODE']='1'
    def limits():
        resource.setrlimit(resource.RLIMIT_CPU,(a.cpu,a.cpu));resource.setrlimit(resource.RLIMIT_AS,(1024**3,1024**3));os.setsid()
    before=resource.getrusage(resource.RUSAGE_CHILDREN);start=time.monotonic();utc=datetime.now(timezone.utc).isoformat();timed_out=False
    info={'command':a.command,'cwd':str(R),'environment':{k:env[k] for k in THREAD_KEYS+['PYTHONDONTWRITEBYTECODE']},'started_utc':utc,'cpu_cap':a.cpu,'wall_cap':a.wall,'address_space_cap_bytes':1024**3,'single_child':True}
    (out/'COMMAND.json').write_text(json.dumps(info,indent=2)+'\n')
    with (out/'stdout.txt').open('xb') as stdout,(out/'stderr.txt').open('xb') as stderr:
        child=subprocess.Popen(a.command,cwd=R,env=env,stdout=stdout,stderr=stderr,preexec_fn=limits)
        try:rc=child.wait(timeout=a.wall)
        except subprocess.TimeoutExpired:
            timed_out=True;os.killpg(child.pid,signal.SIGKILL);rc=child.wait()
    elapsed=time.monotonic()-start;after=resource.getrusage(resource.RUSAGE_CHILDREN)
    receipt={**info,'returncode':rc,'timed_out':timed_out,'wall_seconds':elapsed,'finished_utc':datetime.now(timezone.utc).isoformat(),'inclusive_cpu_seconds':after.ru_utime+after.ru_stime-before.ru_utime-before.ru_stime,'child_peak_rss_KiB':after.ru_maxrss,'measurement':'postexit_getrusage_RUSAGE_CHILDREN_delta_CPU; ru_maxrss_process_scope_highwater','enforcement':'single_child_RLIMIT_CPU_RLIMIT_AS_process_group_wall_timeout','live_aggregate_monitor':False,'post_snapshot_changed':[]}
    saved=json.loads((out/'SOURCE_INPUT_SNAPSHOT.json').read_text())
    for row in saved:
        pth=R/row['path']
        if not pth.exists() or hashlib.sha256(pth.read_bytes()).hexdigest()!=row['sha256']:receipt['post_snapshot_changed'].append(row['path'])
    (out/'RESOURCE_RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2));return rc if rc>=0 else 128-rc
if __name__=='__main__':sys.exit(main())
