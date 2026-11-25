"""Independent DOP853 reference for the finite source-only two-level graph."""
import argparse,json,math
from pathlib import Path
import numpy as np
from scipy.integrate import solve_ivp
from full_bianchi_hyrec.standalone_line import prepare,initial
from full_bianchi_hyrec.trajectory.atomic_two_s_live import TwoSNetwork
p=argparse.ArgumentParser();p.add_argument('--compiled',type=Path,required=True);p.add_argument('--rates',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
state=json.loads((a.compiled/'STATES.json').read_text())['states']['z1100']
with np.load(a.compiled/'z1100.npz') as z:q=prepare({k:z[k] for k in z.files},4)
net=TwoSNetwork(a.rates,q,state['T_r_K']);idx=net.active
f=initial(q,'radiation',state['T_r_K']);f0=q['z0'];n20=state['x_2s']*state['n_H_m3'];neutral=(state['x_1s']+state['x_2s'])*state['n_H_m3']
def point(i,average):
    z=q['z'][i];w=q['w'][i];alpha=average/(w@z)/(1+average)
    for _ in range(12):
        y=alpha*z
        alpha-=(w@(y/(1-y))-average)/(w@(z/(1-y)**2))
    v=alpha*net.znode[i]
    return v/(1-v)
def rhs(t,y):
    n2=y[0]*n20;avg=y[1:]*f0
    occ=np.array([point(i,x) for i,x in zip(idx,avg)])
    flux=net.A[idx]*n2-(net.B[idx]*(neutral-n2)-net.A[idx]*n2)*occ
    return np.r_[-math.fsum(flux)/n20,flux/q['g'][idx]/f0]
y0=np.r_[1.,f[idx]/f0];ref=solve_ivp(rhs,(0,1),y0,method='DOP853',rtol=3e-13,atol=1e-14)
assert ref.success
end=ref.y[:,-1];rows=[]
for steps in (1,2,4,8,16,32,64):
    x=f.copy();n=n20
    for _ in range(steps):
        s=net.step(x,n,neutral,1/steps);x=s.f;n=s.n2
    err=abs(n/n20-end[0])/abs(end[0]-1)
    gap=np.max(abs(x[idx]/f0-end[1:]))
    rows.append(dict(steps=steps,n2=n,relative_excited_signal_error=err,max_scaled_f_error=float(gap)))
    print(rows[-1])
assert all(a['relative_excited_signal_error']>b['relative_excited_signal_error'] for a,b in zip(rows,rows[1:]))
a.out.write_text(json.dumps(dict(scope='finite source-only two-level DOP853 reference',reference_n2=float(end[0]*n20),reference_steps=len(ref.t)-1,rows=rows),indent=2)+'\n')
