"""One separately authorized saved-data figure child; no source/solve execution."""
import json,os,resource,subprocess,sys,time
from pathlib import Path
from common import UNIT,used_files,identity,save

def main():
 ready=UNIT/'evidence/FIGURES_RUN_READY.json'
 if not ready.is_file() or json.loads(ready.read_text()).get('authorization')!='FIGURES_RUN_READY':raise RuntimeError('SEPARATE_ROOT_FIGURE_AUTHORIZATION_REQUIRED')
 ev=UNIT/'evidence/execution/figures001';out=UNIT/'results/figures001'
 if ev.exists() or out.exists():raise RuntimeError('FIRST_FIGURES_MUST_BE_PRESERVED')
 ev.mkdir(parents=True);before={k:identity(p) for k,p in used_files().items()};save(ev/'HASHES_BEFORE.json',before)
 env=os.environ.copy();keys=('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','VECLIB_MAXIMUM_THREADS','NUMEXPR_NUM_THREADS','BLIS_NUM_THREADS')
 for k in keys:env[k]='1'
 cmd=[sys.executable,str(UNIT/'code/figures.py'),'--results',str(UNIT/'results/primary001'),'--out',str(out)];limits={'cpu_seconds':10,'wall_seconds':30,'RLIMIT_AS_bytes':1073741824,'threads':1,'point_operator_actions':0,'event_actions':0,'source_rebuild':0,'solves':0}
 save(ev/'COMMAND.json',{'argv':cmd,'limits':limits,'thread_environment':{k:env[k] for k in keys}})
 def boundary():
  resource.setrlimit(resource.RLIMIT_CPU,(10,10));resource.setrlimit(resource.RLIMIT_AS,(1073741824,1073741824));resource.setrlimit(resource.RLIMIT_CORE,(0,0))
 initial=resource.getrusage(resource.RUSAGE_CHILDREN);start=time.monotonic();timed=False
 with (ev/'stdout.txt').open('wb') as stdout,(ev/'stderr.txt').open('wb') as stderr:
  child=subprocess.Popen(cmd,env=env,stdout=stdout,stderr=stderr,preexec_fn=boundary)
  try:code=child.wait(timeout=30)
  except subprocess.TimeoutExpired:timed=True;child.kill();code=child.wait()
 final=resource.getrusage(resource.RUSAGE_CHILDREN);after={k:identity(p) for k,p in used_files().items()};save(ev/'HASHES_AFTER.json',after)
 receipt={'returncode':code,'timed_out':timed,'child_inclusive_cpu_seconds':final.ru_utime+final.ru_stime-initial.ru_utime-initial.ru_stime,'child_user_cpu_seconds':final.ru_utime-initial.ru_utime,'child_system_cpu_seconds':final.ru_stime-initial.ru_stime,'child_wall_seconds':time.monotonic()-start,'child_maxRSS_KiB':final.ru_maxrss,'limits':limits,'source_and_input_hashes_unchanged':before==after,'first_figures_preserved':True}
 save(ev/'EXECUTION_RECEIPT.json',receipt)
 if out.is_dir():save(ev/'FIRST_ASSET_IDENTITIES.json',{str(p.relative_to(UNIT)):identity(p) for p in sorted(out.glob('*')) if p.is_file()})
 print(json.dumps(receipt));return code if code>=0 else 1
if __name__=='__main__':sys.exit(main())
