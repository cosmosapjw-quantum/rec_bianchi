"""Native prescribed LRS Bianchi I, no external recombination state.
Different source (reduced TLA) than independent HMLA trajectory."""
import pathlib,subprocess,json,hashlib,argparse,numpy as np
P=pathlib.Path
p=argparse.ArgumentParser();p.add_argument('--binary',type=P,required=True);p.add_argument('--out',type=P,required=True);a=p.parse_args()
a.out.mkdir(exist_ok=False);exe=a.binary.resolve();sha=lambda f:hashlib.sha256(P(f).read_bytes()).hexdigest()
rows=[]
for s in (0.,.01,-.01):
 for n in (128,256,512,1024):
  name=f's{s:g}_n{n}';dest=a.out/(name+'.tsv')
  cmd=[str(exe),'1600','900',str(n),str(s)]
  with dest.open('w') as f:r=subprocess.run(cmd,stdout=f,stderr=subprocess.PIPE,text=True,timeout=120)
  if r.returncode:raise RuntimeError(r.stderr)
  data=np.genfromtxt(dest,names=True,delimiter='\t')
  assert len(data)==n+1 and np.all(np.isfinite(data['T_m_K'])) and np.min(data['T_m_K'])>0
  assert np.all((data['x_HII']>=0)&(data['x_HII']<=1)) and np.max(abs(data['matched_correction_j_per_H']))==0
  assert np.max(abs(data['x_HII']+data['x_HI']-1))<1e-14
  row=dict(case=name,shear=s,steps=n,command=cmd,path=str(dest),sha256=sha(dest),x_HII_end=float(data['x_HII'][-1]),T_m_end=float(data['T_m_K'][-1]),max_residual=float(np.max(abs(data['residual']))),max_heat_residual_j_per_H=float(np.max(abs(data['thermal_defect_j_per_H']))),T_min_end=float(data['T_min_K'][-1]),T_max_end=float(data['T_max_K'][-1]))
  rows.append(row);print(row,flush=True)
(a.out/'OWNED_HISTORY.json').write_text(json.dumps(dict(binary_sha256=sha(exe),cases=rows),indent=2,allow_nan=False)+'\n')
