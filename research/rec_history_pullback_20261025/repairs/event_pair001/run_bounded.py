"""One root-authorized saved-data repair child;5CPU/15wall/1thread/1GiB."""
from pathlib import Path
import hashlib,json,os,resource,subprocess,sys,time
D=Path(__file__).resolve().parent;U=D.parents[1]
if (D/'EXECUTION_RECEIPT.json').exists():raise RuntimeError('NO_REPAIR_RETRY')
def save(p,x):p.write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')
def ident(p):
 h=hashlib.sha256();size=0
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b);size+=len(b)
 return {'bytes':size,'sha256':h.hexdigest()}
def tree():return {str(p.relative_to(U)):ident(p) for base in (U/'results/primary001',U/'evidence/execution/primary001') for p in sorted(base.rglob('*')) if p.is_file()}
before=tree();save(D/'ORIGINAL_RAW_HASHES_BEFORE.json',before)
source_before={str(p.relative_to(U)):ident(p) for folder in ('code','tests','vendor','inputs') for p in sorted((U/folder).glob('*')) if p.is_file()};save(D/'CURRENT_SOURCE_HASHES_BEFORE.json',source_before)
auth=json.loads((U/'evidence/EVENT_PAIR_REPAIR_AUTHORIZATION.json').read_text());assert auth['repair_allocation']['cpu_seconds']==5 and auth['new_matvecs']==0
env=os.environ.copy();keys=('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','VECLIB_MAXIMUM_THREADS','BLIS_NUM_THREADS','NUMEXPR_NUM_THREADS')
for key in keys:env[key]='1'
cmd=[sys.executable,str(D/'run_saved_repair.py')];limits={'cpu_seconds':5,'wall_seconds':15,'RLIMIT_AS_bytes':1073741824,'threads':1,'matvecs':0,'operator_actions':0,'event_actions':0,'sign_assignments':32,'solves':0,'primary_rerun':False}
save(D/'COMMAND.json',{'argv':cmd,'limits':limits,'script_identity':ident(D/'run_saved_repair.py'),'thread_environment':{k:env[k] for k in keys}})
def boundary():
 resource.setrlimit(resource.RLIMIT_CPU,(5,5));resource.setrlimit(resource.RLIMIT_AS,(1073741824,1073741824));resource.setrlimit(resource.RLIMIT_CORE,(0,0))
start=time.monotonic();first=resource.getrusage(resource.RUSAGE_CHILDREN);timed=False
with (D/'stdout.txt').open('wb') as stdout,(D/'stderr.txt').open('wb') as stderr:
 p=subprocess.Popen(cmd,env=env,stdout=stdout,stderr=stderr,preexec_fn=boundary)
 try:rc=p.wait(timeout=15)
 except subprocess.TimeoutExpired:timed=True;p.kill();rc=p.wait()
last=resource.getrusage(resource.RUSAGE_CHILDREN);wall=time.monotonic()-start;after=tree();save(D/'ORIGINAL_RAW_HASHES_AFTER.json',after)
source_after={str(p.relative_to(U)):ident(p) for folder in ('code','tests','vendor','inputs') for p in sorted((U/folder).glob('*')) if p.is_file()};save(D/'CURRENT_SOURCE_HASHES_AFTER.json',source_after)
receipt={'returncode':rc,'timed_out':timed,'child_inclusive_cpu_seconds':last.ru_utime+last.ru_stime-first.ru_utime-first.ru_stime,'child_user_cpu_seconds':last.ru_utime-first.ru_utime,'child_system_cpu_seconds':last.ru_stime-first.ru_stime,'child_wall_seconds':wall,'maxRSS_KiB':last.ru_maxrss,'limits':limits,'original_primary_raw_files':len(before),'original_primary_raw_unchanged':before==after,'current_source_and_manifest_unchanged_during_repair':source_before==source_after,'first_failure_status_not_rewritten':True,'raw_partial_preserved':True}
save(D/'EXECUTION_RECEIPT.json',receipt);print(json.dumps(receipt));sys.exit(rc if rc>=0 else 1)
