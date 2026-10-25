"""One root-authorized saved-data H-layout correction:4CPU/10wall, no retry."""
from pathlib import Path
import hashlib,json,os,resource,subprocess,sys,time,shutil,difflib
D=Path(__file__).resolve().parent;U=D.parents[1]
if (D/'EXECUTION_RECEIPT.json').exists():raise RuntimeError('NO_LAYOUT_RETRY')
def save(p,x):p.write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')
def ident(p):b=p.read_bytes();return {'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def sourcehashes():return {str(p.relative_to(U)):ident(p) for folder in ('code','tests','vendor','inputs') for p in sorted((U/folder).glob('*')) if p.is_file()}
before=sourcehashes();save(D/'CURRENT_SOURCE_HASHES_BEFORE.json',before);first=json.loads((U/'evidence/execution/figures001/FIRST_ASSET_IDENTITIES.json').read_text())
for n,v in first.items():assert ident(U/n)==v
shutil.copyfile(U/'code/figures.py',D/'ORIGINAL_FIGURES.py')
(D/'LAYOUT_DIFF.diff').write_text(''.join(difflib.unified_diff((U/'code/figures.py').read_text().splitlines(True),(D/'plot_saved.py').read_text().splitlines(True),fromfile='original/code/figures.py',tofile='layout002/plot_saved.py')))
save(D/'ROOT_REVIEW_FINDING.json',{'root_and_same_reviewer_actual_PNG_finding':'Second figure constrained layout compressed both axes to roughly100px at outer edges, large central blank, clipped title/labels, overlapping x ticks','first_cell_margins_query_gains':'ACTUAL_PNG_PASS_NOT_RERENDERED','authorized_change':'explicit subplot margins/spacing, constrained_layout off, four fixed left x ticks, legends outside data; numeric arrays/scales/thresholds/tolerance unchanged','first_PNGs_preserved':True,'new_science_actions':0})
out=U/'results/figures002';assert not out.exists();env=os.environ.copy();keys=('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','VECLIB_MAXIMUM_THREADS','BLIS_NUM_THREADS','NUMEXPR_NUM_THREADS')
for k in keys:env[k]='1'
cmd=[sys.executable,str(D/'plot_saved.py'),'--results',str(U/'results/primary001'),'--out',str(out)];limits={'cpu_seconds':4,'wall_seconds':10,'RLIMIT_AS_bytes':1073741824,'threads':1,'matvecs':0,'source_rebuild':0,'solves':0}
save(D/'COMMAND.json',{'argv':cmd,'limits':limits,'plot_source_identity':ident(D/'plot_saved.py'),'thread_environment':{k:env[k] for k in keys}})
def boundary():
 resource.setrlimit(resource.RLIMIT_CPU,(4,4));resource.setrlimit(resource.RLIMIT_AS,(1073741824,1073741824));resource.setrlimit(resource.RLIMIT_CORE,(0,0))
start=time.monotonic();first_usage=resource.getrusage(resource.RUSAGE_CHILDREN);timed=False
with (D/'stdout.txt').open('wb') as stdout,(D/'stderr.txt').open('wb') as stderr:
 p=subprocess.Popen(cmd,env=env,stdout=stdout,stderr=stderr,preexec_fn=boundary)
 try:rc=p.wait(timeout=10)
 except subprocess.TimeoutExpired:timed=True;p.kill();rc=p.wait()
last=resource.getrusage(resource.RUSAGE_CHILDREN);wall=time.monotonic()-start;after=sourcehashes();save(D/'CURRENT_SOURCE_HASHES_AFTER.json',after)
for n,v in first.items():assert ident(U/n)==v
receipt={'returncode':rc,'timed_out':timed,'child_inclusive_cpu_seconds':last.ru_utime+last.ru_stime-first_usage.ru_utime-first_usage.ru_stime,'child_user_cpu_seconds':last.ru_utime-first_usage.ru_utime,'child_system_cpu_seconds':last.ru_stime-first_usage.ru_stime,'child_wall_seconds':wall,'maxRSS_KiB':last.ru_maxrss,'limits':limits,'original_source_and_manifest_unchanged':before==after,'original_first_assets_hash_unchanged':True,'only_second_figure_rendered':True,'own_script_identity':ident(D/'plot_saved.py')}
save(D/'EXECUTION_RECEIPT.json',receipt)
if out.is_dir():save(D/'ASSET_IDENTITIES.json',{str(p.relative_to(U)):ident(p) for p in sorted(out.glob('*')) if p.is_file()})
print(json.dumps(receipt));sys.exit(rc if rc>=0 else 1)
