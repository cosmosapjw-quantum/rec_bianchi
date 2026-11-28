"""Conditional HI ground-state detailed-balance kinetics with actual HeI two-photon source.
He history and thermal radiation bath remain prescribed; no added 2p channel."""
from pathlib import Path
import sys,json,hashlib,numpy as np,time
from scipy.constants import c as clight,h as planck,electron_volt,k as kb
from scipy.special import roots_laguerre
D=Path(__file__).resolve().parent;P=D.parent;H=P/'r118c4h_goal_adjoint';F=P/'r118c4f_causal_mesh'
g={'__file__':str(H/'helium.py'),'__name__':'prior'};exec(compile((H/'helium.py').read_text(),str(H/'helium.py'),'exec'),g);sigma,profile=g['sigma'],g['profile'];cos=g['HyRec2012Cosmology']();hist=g['integrate_helium_stages'](cos)
z=np.load(F/'HELIUM_CHANNELS.npz');u=z['u'];net=z['net_cell'];en=z['energy'];stage=z['stage'];assert np.array_equal(np.array(hist.z),z['z']);ix=np.where((stage[:-1]=='HeII_RECOMBINATION')&(stage[1:]=='HeII_RECOMBINATION'))[0]
a=np.exp(u);zz=z['z'];H0=np.array([cos.hubble_s(float(v)) for v in zz]);he=np.array(hist.xHeII);T=cos.T0_K/a;nh=cos.nH0_m3/a**3
thr=13.598434599702;S=cos.fsR**3*cos.meR**3*2.4127161187130e21*T*np.sqrt(T)*np.exp(-157801.37882/T)/nh
# Exact algebraic neutral fraction of ground-state Saha relation y S=(1-y)(1-y+xHe).
B=S+2+he;eq=2*(1+he)/(B+np.sqrt(B*B-4*(1+he)));ref=np.array([g['saha_xH1s'](cos,float(he[j]),float(zz[j])) for j in np.r_[ix,ix[-1]+1]])
assert np.all(np.isfinite(eq[ix])) and np.all(eq[ix]>0)
# Planck photon number density / energy, multiplied by c sigma, integrated via Laguerre.
v,w=roots_laguerre(48);Te=kb*T[ix+1]/electron_volt;E=thr+Te[:,None]*v;g0=thr/Te;fac=8*np.pi*electron_volt**3/(planck**3*clight**2)
Gamma=fac*Te*np.exp(-g0)*np.sum(w[None,:]*E**2*sigma(E)/(1-np.exp(-g0[:,None]-v)),axis=1)
assert np.all(Gamma>0)
x,w=np.polynomial.legendre.leggauss(128);x=(x+1)/2;w=w/2;w*=profile(x);w/=w.sum();assert abs(w@x-.5)<1e-13
rows=[];arrays={}
for bins in [512,1024,2048]:
 grid=np.geomspace(a[ix[0]]*en[0]*min(x)*.98,a[ix[-1]+1]*en[0]*1.02,bins);N=np.zeros(bins);Nfixed=N.copy();delta=0.;base=0.;ys=[eq[ix[0]]];yb=[eq[ix[0]]];diffs=[0.];ion=heat=em=emK=absK=0.;ion0=heat0=0.;rootmax=0.;signed_min=0.;nneg=0;maxit=0
 for jj,i in enumerate(ix):
  l,r=u[i:i+2];m=(l+r)/2;dt=r-l;am=np.exp(m);E0=am*en[0]*x;Q=2*net[i,0]*w;em+=Q.sum();emK+=Q@E0
  born=np.zeros(bins);k=np.searchsorted(grid,E0)-1;t=(E0-grid[k])/(grid[k+1]-grid[k]);np.add.at(born,k,Q*(1-t));np.add.at(born,k+1,Q*t)
  # Integrate each half only above threshold; unknown endpoint neutral fraction factors out.
  def coeff(ul,ur):
   end=np.maximum(ul,np.minimum(ur,np.log(grid/thr)));d=end-ul;mid=(ul+end)/2;tau=np.zeros(bins)
   for sign in [-1,1]:
    v=mid+sign*d/(2*np.sqrt(3));aa=np.exp(v);tau+=clight*cos.nH0_m3/aa**3/np.interp(v,u,H0)*sigma(grid/aa)*d/2
   return tau,grid/np.exp(mid)
  K1,E1=coeff(l,m);K2,E2=coeff(m,r)
  def losses(N,y):
   L1=N*(-np.expm1(-K1*y));X=N-L1+born;L2=X*(-np.expm1(-K2*y));return L1,L2,X-L2
  # implicit backward Euler on detailed-balance neutral fraction; write delta about exact moving equilibrium
  ee=eq[i+1];s=S[i+1];aa=1+(2+he[i+1]-2*ee)/s;lam=dt*Gamma[jj]/H0[i+1];shift=eq[i]-ee
  def solve(old,with_photon):
   global rootmax,maxit
   d=(old+shift)/(1+lam*aa)
   for it in range(8):
    y=ee+d
    assert y>0 and y<1
    if with_photon:
     L1,L2,_=losses(N,y);loss=float(np.sum(L1)+np.sum(L2))
     # d total absorbed / dy = old*(K1+K2)*exp(-(K1+K2)y)+birth*K2*exp(-K2 y)
     dl=float(np.sum(N*(K1+K2)*np.exp(-(K1+K2)*y)+born*K2*np.exp(-K2*y)))
    else:loss=dl=0.
    res=d-(old+shift)+lam*(aa*d-d*d/s)+loss
    step=res/(1+lam*(aa-2*d/s)+dl);d-=step
    if abs(step)<1e-17*max(abs(d),1e-12):break
   maxit=max(maxit,it+1);rootmax=max(rootmax,abs(res));return d
  base=solve(base,False);delta=solve(delta,True);y1=ee+delta;yb1=ee+base
  L1,L2,N=losses(N,y1);l1,l2,Nfixed=losses(Nfixed,eq[i+1]);ion+=L1.sum()+L2.sum();heat+=L1@np.maximum(E1-thr,0)+L2@np.maximum(E2-thr,0);absK+=(L1+L2)@grid;ion0+=l1.sum()+l2.sum();heat0+=l1@np.maximum(E1-thr,0)+l2@np.maximum(E2-thr,0);signed_min=min(signed_min,float(N.min()));nneg+=int(np.any(N<0))
  ys.append(y1);yb.append(yb1);diffs.append(delta-base) # stable signed neutral response
 nd=em-ion-N.sum();ed=emK-absK-N@grid;assert abs(nd)<1e-12 and abs(ed)<1e-14 and min(ys)>0 and max(ys)<1
 row=dict(bins=bins,net_emitted=float(em),absorbed_coupled=float(ion),absorbed_frozen=float(ion0),heat_coupled_eV_per_H=float(heat),heat_frozen_eV_per_H=float(heat0),max_abs_delta_HI=float(max(abs(np.array(diffs)))),terminal_delta_HI=float(diffs[-1]),max_relative_delta_HI=float(max(abs(np.array(diffs)/np.array(yb)))),baseline_max_lag_from_saha=float(max(abs(np.array(yb)-eq[np.r_[ix,ix[-1]+1]]))),number_balance=float(nd),comoving_energy_balance=float(ed),max_root_abs=float(rootmax),max_newton_iters=maxit,signed_spectrum_min=signed_min,signed_negative_cells=nneg)
 rows.append(row);arrays[f'y_{bins}']=ys;arrays[f'ybase_{bins}']=yb;arrays[f'delta_{bins}']=diffs;arrays[f'E_{bins}']=grid;arrays[f'N_{bins}']=N;print(row,flush=True)
np.savez_compressed(D/'HI_FEEDBACK.npz',u=u[np.r_[ix,ix[-1]+1]],eq=eq[np.r_[ix,ix[-1]+1]],Gamma=Gamma,**arrays)
(D/'HI_FEEDBACK.json').write_text(json.dumps(dict(rows=rows,source_sha=hashlib.sha256((F/'HELIUM_CHANNELS.npz').read_bytes()).hexdigest(),Gamma_min=float(min(Gamma)),Gamma_max=float(max(Gamma)),max_saha_difference=float(max(abs(eq[np.r_[ix,ix[-1]+1]]-ref))),scope='prescribed net HeI two-photon emission and fixed HeII/blackbody bath, exact ground-state continuum photoionization + detailed-balance inverse rate, matched no injection, implicit HI abundance-opacity feedback; not full HMLA/HyRec excited-level kinetics, He response, recombination photon recycling or thermal feedback'),indent=2)+'\n')
