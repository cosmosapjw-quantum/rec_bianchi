import os
for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):os.environ[k]='1'
from pathlib import Path
import sys, json, hashlib, time
import numpy as np
p=Path('research/rec_compton_coupled_20261022/code/analyze_collisions.py')
compile(p.read_text(),str(p),'exec')
sys.path.insert(0,str(p.parent.resolve()))
import analyze_collisions as c
s=time.perf_counter()
r=c.integrate_retained(np.array([0.,1.,2.]),np.array([-1.,-2.,-3.]),np.array([False,True,True]))
assert r['trapezoid']==r['simpson']==-4.
assert r['supported_interval_contribution']==-2.5
assert r['continuation_or_boundary_contribution']==-1.5
assert r['negative_part_trapezoid']==-4. and r['positive_part_trapezoid']==0.
assert r['absolute_throughput_trapezoid']==4.
a=c.AtomicNetwork(uv_cutoff_eV=200)
b=c.CollisionalBudget(a)
Y=np.broadcast_to(a.initial_Y,(3,21)).copy()
T=np.array([1000.,7500.,15000.]); nb=np.array([100.,20.,3.]);H=np.array([3e-17,2e-17,1e-17]);eta=Y@(1+a.q)
raw=np.zeros((3,63));raw[:,40:61]=Y/a.scales;raw[:,62]=np.log(T)
x=np.array([.9,1.2,1.8])
saved=dict(x=x,z=21*np.exp(-x)-1,Y=Y,T_K=T,isotope_scales=a.scales,raw_state=raw,initial_state=raw[0])
d=dict(H_s=H,nb_m3=nb,ne_m3=nb*(Y@a.q),gas_particles_per_baryon=eta,elapsed_Myr=np.array([500.,800.,2000.]))
for k in ('photo_primary_W_m3','rr_cooling_W_m3','dr_cooling_W_m3','compton_selected_W_m3','compton_uv_W_m3'):d[k]=np.zeros(3)
d['work_J_per_baryon_per_x']=3*c.KB_J_K*T*eta
arrays,summary=c._evaluate_grid(saved,d,a,b)
assert arrays['coefficients_SI'].shape==(3,5)
np.testing.assert_array_equal(arrays['in_published_accuracy_domain'],[[False]*5,[False]*3+[True]*2,[True]*5])
assert arrays['ci_dY_dt'].shape==(3,21)
assert arrays['ci_channel_binding_W_m3'].shape==(3,7)
assert arrays['ce_channel_cooling_W_m3'].shape==(3,5)
np.testing.assert_array_equal(arrays['Q_W_m3'][:,c.PROCESS_NAMES.index('ci_total_gas')],np.zeros(3))
assert all(not row['available'] and row['coefficient'] is None for row in summary['unavailable'].values())
assert max(summary['conservation_max_scaled'].values())<1e-13
print(json.dumps(dict(status='PASS_SYNTHETIC_FIXTURES',source_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),checks=['Python syntax','signed positive-weight trapezoid partition versus independent exact values','five fit support flags at 1000/7500/15000 K','native channel dimensions','CI total-gas zero transfer','unavailable values remain null','charge/baryon/isotope/binding closure'],max_scaled_residual=max(summary['conservation_max_scaled'].values()),wall_seconds=time.perf_counter()-s,new_ODE_integrations=0,new_trajectory_postprocessing=0),indent=2))
