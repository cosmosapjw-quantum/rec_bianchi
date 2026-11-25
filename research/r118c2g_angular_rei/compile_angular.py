import argparse,pathlib,json,time,hashlib
import numpy as np
from full_bianchi_hyrec.recoil.calibrated_source import Bath
from full_bianchi_hyrec.recoil.calibrated_angular import compile_angular
p=argparse.ArgumentParser();p.add_argument('--states',type=pathlib.Path,required=True);p.add_argument('--out',type=pathlib.Path,required=True);p.add_argument('--workers',type=int,default=4);a=p.parse_args()
a.out.mkdir(exist_ok=False,parents=True);states=json.loads(a.states.read_text())['states'];rows=[]
for name in ('z1100','z1300','z900'):
    q=states[name];bath=Bath(q['T_m_K'],q['n_1s_m3']);t=time.monotonic();v=compile_angular(bath,(1,4),a.workers)
    path=a.out/(name+'.npz');np.savez_compressed(path,**v)
    row=dict(case=name,source_state=q,pairs=len(v['pairs']),samples=len(v['mu']),max_marginal=v['max_marginal'],max_same_sym=v['max_same_sym'],sha256=hashlib.sha256(path.read_bytes()).hexdigest(),wall_s=time.monotonic()-t)
    print(row,flush=True);rows.append(row)
(a.out/'SOURCE_RESULTS.json').write_text(json.dumps(rows,indent=2)+'\n')
