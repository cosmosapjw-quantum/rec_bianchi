import argparse,json,pathlib,hashlib,time
import numpy as np
from full_bianchi_hyrec.trajectory.standalone import independent_history
from full_bianchi_hyrec.recoil.calibrated_source import Bath,compile_isotropic
P=pathlib.Path
p=argparse.ArgumentParser();p.add_argument('--rates',type=P,required=True);p.add_argument('--out',type=P,required=True);p.add_argument('--workers',type=int,default=4);p.add_argument('--levels',nargs='+',type=int,default=[1,4]);p.add_argument('--only',default='');a=p.parse_args()
a.out.mkdir(exist_ok=False,parents=True)
sha=lambda p:hashlib.sha256(P(p).read_bytes()).hexdigest()
states={}
# Independent integrations from post-Saha, no sampled reference history.
for z in (1300.,3000/2.7255-1,900.):
 name='z'+str(round(z))
 h=independent_history(a.rates,z_end=z,points=301,rtol=1e-10,atol=1e-12)
 states[name]=h['states'][-1]
 (a.out/f'{name}_HISTORY.json').write_text(json.dumps(h,indent=2,allow_nan=False)+'\n')
# Cross-solver independent integration at exactly the main calibration node.
h=independent_history(a.rates,z_end=3000/2.7255-1,points=301,rtol=1e-11,atol=1e-13,method='BDF',initialization='saha')
r=h['states'][-1];s=states['z1100']
print('own HMLA',s,'BDF tighter/Saha',r,flush=True)
cross={k:abs(r[k]-s[k])/max(abs(s[k]),1e-300) for k in ['x_HII','T_m_K','x_1s','n_1s_m3']}
(a.out/'STATES.json').write_text(json.dumps(dict(states=states,tighter_bdf_saha_relative=cross,tighter_bdf_saha=r,radau_status='REJECTED_TRIAL_Tm_over_Tr_outside_table',rate_archive_sha256=sha(a.rates)),indent=2,allow_nan=False)+'\n')
cases={'anchor':Bath(3000.,250e6),**{name:Bath(q['T_m_K'],q['n_1s_m3']) for name,q in states.items()}}
# Bath coverage at the selected state temperatures is explicit.
out=[]
for name,bath in cases.items():
 if a.only and not name.startswith(a.only):continue
 t=time.monotonic();q=compile_isotropic(bath,tuple(a.levels),a.workers)
 dest=a.out/f'{name}.npz';np.savez_compressed(dest,**q)
 row=dict(case=name,T_m_K=bath.T_m_K,n_1s_m3=bath.n_1s_m3,source_sha256=sha(dest),max_marginal=q['max_marginal'],max_same_sym=q['max_same_sym'],direct_x_per_s=q['direct'].tolist(),wall_s=time.monotonic()-t)
 print(row,flush=True);out.append(row)
(a.out/'COMPILE_RESULTS.json').write_text(json.dumps(out,indent=2,allow_nan=False)+'\n')
