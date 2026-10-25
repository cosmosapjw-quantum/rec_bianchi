"""One root-authorized diagnostic child, cap1CPU/5wall, no retry."""
from pathlib import Path
import hashlib,json,os,resource,subprocess,sys,time
D=Path(__file__).resolve().parent
if (D/'EXECUTION_RECEIPT.json').exists():raise RuntimeError('NO_DIAGNOSTIC_RETRY')
def save(p,x):p.write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')
env=os.environ.copy();keys=('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','VECLIB_MAXIMUM_THREADS','BLIS_NUM_THREADS','NUMEXPR_NUM_THREADS')
for k in keys:env[k]='1'
cmd=[sys.executable,str(D/'readback.py')];limits={'CPU_seconds':1,'wall_seconds':5,'RLIMIT_AS_bytes':1073741824,'threads':1,'operator_actions':0,'event_actions':0,'matvec':0,'solves':0}
save(D/'COMMAND.json',{'argv':cmd,'limits':limits,'thread_environment':{k:env[k] for k in keys}})
def boundary():
 resource.setrlimit(resource.RLIMIT_CPU,(1,1));resource.setrlimit(resource.RLIMIT_AS,(1073741824,1073741824));resource.setrlimit(resource.RLIMIT_CORE,(0,0))
start=time.monotonic();first=resource.getrusage(resource.RUSAGE_CHILDREN);timed=False
with (D/'stdout.txt').open('wb') as stdout,(D/'stderr.txt').open('wb') as stderr:
 p=subprocess.Popen(cmd,env=env,stdout=stdout,stderr=stderr,preexec_fn=boundary)
 try:rc=p.wait(timeout=5)
 except subprocess.TimeoutExpired:timed=True;p.kill();rc=p.wait()
last=resource.getrusage(resource.RUSAGE_CHILDREN)
r={'returncode':rc,'timed_out':timed,'child_inclusive_cpu_seconds':last.ru_utime+last.ru_stime-first.ru_utime-first.ru_stime,'child_user_cpu_seconds':last.ru_utime-first.ru_utime,'child_system_cpu_seconds':last.ru_stime-first.ru_stime,'child_wall_seconds':time.monotonic()-start,'maxRSS_KiB':last.ru_maxrss,'limits':limits,'allocation':'root review/diagnostic5CPU15wall; this child1CPU5wall','original_primary_code_results_and_manifest_changed':False,'raw_preserved':True}
save(D/'EXECUTION_RECEIPT.json',r);print(json.dumps(r));sys.exit(rc if rc>=0 else 1)
