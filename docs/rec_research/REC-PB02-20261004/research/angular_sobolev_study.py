#!/usr/bin/env python3
"""Conditional local angular Sobolev research, not a Bianchi RT solver."""
import json,csv,math
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'evidence';OUT.mkdir(exist_ok=True)
plan=json.loads((ROOT/'research/ANGULAR_EXPERIMENT_PLAN.json').read_text())
def angular(nmu,nphi):
 mu,w=np.polynomial.legendre.leggauss(nmu);phi=np.arange(nphi)*2*np.pi/nphi
 x=np.sqrt(1-mu[:,None]**2)*np.cos(phi);y=np.sqrt(1-mu[:,None]**2)*np.sin(phi)
 q=x*x-y*y;weights=np.broadcast_to(w[:,None]/(2*nphi),q.shape)
 return q,weights

def p(tau):return -np.expm1(-tau)/tau

def average(tau0,eps,nmu,nphi):
 q,w=angular(nmu,nphi);h=1+eps*q
 if np.min(h)<=0:raise ValueError('directional expansion must be strictly positive')
 return float(np.sum(w*p(tau0/h)))
rows=[];checks=[]
for tau in plan['tau0_grid']:
 iso=float(p(tau))
 for eps in plan['epsilon_grid']:
  v=[average(tau,eps,*n) for n in plan['quadrature']]
  six=float(np.mean(p(tau/(1+eps*np.array([1.,1.,-1.,-1.,0.,0.])))))
  delta2=-tau*math.exp(-tau)*2*eps**2/15
  rows.append(dict(tau0=tau,epsilon=eps,p_isotropic=iso,p_16=v[0],p_32=v[1],p_64=v[2],delta=v[2]-iso,delta_second_order=delta2,p_six_axes=six))
  checks.append(abs(v[2]-v[1])<=plan['checks']['convergence_abs'])
  checks.append(v[2]-iso<=plan['checks']['jensen_positive_tolerance'])
  if eps==0:checks.append(abs(v[2]-iso)<=plan['checks']['isotropic_abs'])
  if eps==.01 and tau in (.1,1,10):checks.append(abs((v[2]-iso)/delta2-1)<plan['checks']['second_order_relative_at_epsilon_0.01'])
q,w=angular(32,64)
moments={'mean_q':float(np.sum(w*q)),'mean_q2':float(np.sum(w*q*q)),'exact_q2':4/15,'six_axes_q2':2/3,'six_axes_bias_factor':2.5}
checks += [abs(moments['mean_q'])<1e-14,abs(moments['mean_q2']-4/15)<1e-14]
with (OUT/'angular_sobolev_points.csv').open('w') as f:
 dw=csv.DictWriter(f,fieldnames=list(rows[0]));dw.writeheader();dw.writerows(rows)
result={'experiment_id':'E3','kind':'exploratory','status':'PASS' if all(checks) else 'FAIL','point_count':len(rows),'checks':len(checks),'failed':sum(not x for x in checks),'max_32_64_abs_difference':max(abs(r['p_64']-r['p_32']) for r in rows),'max_Jensen_excess':max(r['delta'] for r in rows),'moments':moments,'claim_ceiling':'conditional local Sobolev angular escape only; no line transfer, population feedback, or cosmological history'}
(OUT/'ANGULAR_STUDY_RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
fig,ax=plt.subplots(1,2,figsize=(11.5,4.3),layout='constrained')
es=np.linspace(0,.4,101)
for tau in (.1,1,10):
 iso=p(tau);vals=np.array([average(tau,e,32,64) for e in es]);ax[0].plot(es,(vals/iso-1),label=fr'$\tau_0={tau:g}$')
ax[0].set(xlabel=r'Shear amplitude $\epsilon$: $\sigma/H=\mathrm{diag}(\epsilon,-\epsilon,0)$',ylabel=r'$\langle P\rangle/P(H)-1$',title='Finite optical depth: shear reduces escape')
ax[0].legend();ax[0].grid(alpha=.25)
tau=1;iso=p(tau);full=np.array([average(tau,e,32,64) for e in es]);six=np.array([np.mean(p(tau/(1+e*np.array([1,1,-1,-1,0,0])))) for e in es]);series=-tau*np.exp(-tau)*2*es**2/15
ax[1].plot(es,full-iso,label='Converged angular quadrature');ax[1].plot(es,six-iso,'--',label='Six Cartesian axes');ax[1].plot(es,series,':',label='Derived quadratic term')
ax[1].set(xlabel=r'$\epsilon$',ylabel=r'$\langle P\rangle-P(H)$',title=r'$\tau_0=1$: second angular moment is insufficient')
ax[1].legend(fontsize=8);ax[1].grid(alpha=.25)
fig.suptitle('Conditional local Sobolev model — fixed isotropic populations, all directional expansion positive',fontsize=10)
fig.savefig(OUT/'angular_sobolev_conditional.png',dpi=180);fig.savefig(OUT/'angular_sobolev_conditional.svg');plt.close(fig)
print(json.dumps(result,indent=2));assert all(checks)
