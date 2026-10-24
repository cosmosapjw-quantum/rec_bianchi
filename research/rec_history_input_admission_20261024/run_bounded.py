"""Single-child bounded execution; wall timeout, rlimits and inclusive rusage."""
import argparse,hashlib,json,os,resource,subprocess,sys,time
from pathlib import Path

ROOT=Path(__file__).resolve().parent
def main():
 p=argparse.ArgumentParser();p.add_argument('label');p.add_argument('--cpu',type=int,required=True);p.add_argument('--wall',type=int,required=True);p.add_argument('command',nargs=argparse.REMAINDER);a=p.parse_args()
 if not a.command:raise ValueError('command required')
 path=ROOT/'execution'/a.label;path.mkdir(parents=True,exist_ok=False)
 sources={x.name:hashlib.sha256(x.read_bytes()).hexdigest() for x in ROOT.glob('*.py')}
 for x in [ROOT/'FROZEN_CONTRACT.md',ROOT/'PREEXEC_ADDENDUM.md']:sources[x.name]=hashlib.sha256(x.read_bytes()).hexdigest()
 (path/'SOURCE_IDENTITIES.json').write_text(json.dumps(sources,indent=2)+'\n')
 def limits():
  resource.setrlimit(resource.RLIMIT_CPU,(a.cpu,a.cpu+1))
  resource.setrlimit(resource.RLIMIT_AS,(1024**3,1024**3))
 env=dict(os.environ)
 for key in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS']:env[key]='1'
 before=resource.getrusage(resource.RUSAGE_CHILDREN);self0=time.process_time();start=time.monotonic();timed=False
 with (path/'stdout.log').open('xb') as out,(path/'stderr.log').open('xb') as err:
  try:r=subprocess.run(a.command,cwd=ROOT,stdout=out,stderr=err,env=env,preexec_fn=limits,timeout=a.wall);code=r.returncode
  except subprocess.TimeoutExpired:code=-999;timed=True
 after=resource.getrusage(resource.RUSAGE_CHILDREN)
 receipt=dict(returncode=code,timed_out=timed,wall_seconds=time.monotonic()-start,
  inclusive_cpu_seconds=(after.ru_utime+after.ru_stime-before.ru_utime-before.ru_stime)+(time.process_time()-self0),
  child_peak_rss_KiB=after.ru_maxrss,cpu_cap=a.cpu,wall_cap=a.wall,address_space_cap_bytes=1024**3,threads=1,
  enforcement='single_child_RLIMIT_CPU_RLIMIT_AS_wall_timeout',live_aggregate_monitor=False,command=a.command)
 (path/'RESOURCE_RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
 if code:print((path/'stderr.log').read_text(),file=sys.stderr)
 raise SystemExit(code!=0)
if __name__=='__main__':main()
