"""Run the two independent exact C4K nonlinear lambda checks while tangent evolves.
The original driver later verifies the actual result hashes instead of repeating them."""
from pathlib import Path
import os,sys,subprocess,json,hashlib,inspect,time,concurrent.futures as cf
import rec
D=Path(__file__).resolve().parent
fun_sha=hashlib.sha256(inspect.getsource(rec.run).encode()).hexdigest()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def job(h):
 tag=f'FD_{h:g}';log=D/f'fd_parallel_{h:g}.log';cmd=[sys.executable,'-u','-c',f'import rec;rec.run("fd",{h!r})']
 tm=time.monotonic()
 with log.open('w') as f:r=subprocess.run(cmd,cwd=D,stdout=f,stderr=subprocess.STDOUT,timeout=650)
 out=dict(h=h,exit=r.returncode,seconds=time.monotonic()-tm,cmd=cmd,run_function_sha=fun_sha,log_sha=sha(log))
 if r.returncode==0:
  for ext in ['json','npz']:out[ext+'_sha']=sha(D/(tag+'.'+ext))
 print(out,flush=True);return out
with cf.ThreadPoolExecutor(max_workers=2) as ex:rows=list(ex.map(job,[-.003,.003]))
(D/'PRECOMPUTED_FD.json').write_text(json.dumps(rows,indent=2)+'\n')
assert all(x['exit']==0 for x in rows)
