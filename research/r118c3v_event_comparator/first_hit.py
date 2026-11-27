"""Conditional first native virtual-bin crossing of tracked signed source.
No re-emission/dense Schur chain; companion is classified, not newly charged.
"""
import numpy as np,json,sys
from pathlib import Path
from scipy.interpolate import CubicSpline
from numpy.polynomial.legendre import leggauss
D=Path(__file__).resolve().parent
from spectral_source import B,R,_canonical_twophoton_table,stf
from full_bianchi_hyrec.trajectory.causal_virtual_redshift import _source_edges
def run():
 z=np.load(D/'SPECTRAL_SOURCE.npz');u=z['u'];J=z['J'];E=z['energy'];threshold=z['thresholds'];tab=_canonical_twophoton_table(R);src,ef,es=_source_edges(tab.energy_eV);lr=np.log(es/ef);rev={int(s):k for k,s in enumerate(src)}
 g=np.genfromtxt(B/'plusfine.csv',names=True,delimiter=',');ge=np.log(g['a']);F=np.stack([g[f'F{i}{j}'] for i in range(3) for j in range(3)],axis=1).reshape(-1,3,3);fs=CubicSpline(ge,F,axis=0);S=CubicSpline(ge,np.array([stf([g[f'S{i}'][j] for i in range(5)]) for j in range(len(g))]),axis=0);tau=CubicSpline(u,z['Dtau'],axis=0)
 # Every emission sampled as local isotropic signed birth; energy partition at final time
 # uses the photon redshift before/after first hit, not a second gas source.
 rows={}
 for nm in [4,8]:
  mu,w=leggauss(nm);m,ph=np.meshgrid(mu,np.arange(2*nm)*np.pi/nm,indexing='ij');n=np.stack([np.sqrt(1-m*m)*np.cos(ph),np.sqrt(1-m*m)*np.sin(ph),m],axis=-1).reshape(-1,3);w=np.repeat(w/(4*nm),2*nm)
  for nt in [65,128]:
   ids=np.unique(np.linspace(0,len(u)-1,nt).astype(int));t=u[ids];Dta=z['Dtau'];allj=J[ids];dt=np.diff(t);mid=(t[1:]+t[:-1])/2;birth=(allj[1:]+allj[:-1])/2*dt[:,None,None]
   # aggregate by virtual bin, retain all three signed channels in source.
   total=np.zeros(7);absolute=np.zeros(7);count=0
   for k,tt in enumerate(mid):
    f0=fs(tt);q=n@f0;last=q@np.linalg.inv(fs(t[-1]));dlast=np.linalg.norm(last,axis=1)*np.exp(tt-t[-1]);b=birth[k].sum(axis=0)
    # signed tracked energy, terminal hypothetical free value. First hit
    # removes fraction at arrival, remainder redshifts to final time.
    for j,ej in enumerate(E):
     val=b[j]*w;endE=val*ej*dlast
     total[0]+=np.sum(val)*ej;total[1]+=np.sum(endE)
     dest=rev.get(j,-1)
     if not 0<=dest<311:
      total[4]+=np.sum(endE);absolute[4]+=np.sum(abs(endE));continue
     # Solve crossing q/a norm; actual first arrival at native E_f.
     lo=np.full(len(n),tt);hi=np.full(len(n),t[-1])
     target=ef[dest]/es[dest];ok=dlast<=target
     if not ok.any():
      total[3]+=np.sum(endE);absolute[3]+=np.sum(abs(endE));continue
     # vector bisection only of actual crossing rays; use coframe spline.
     qi=q[ok];a0=lo[ok];a1=hi[ok]
     for _ in range(32):
      h0=(a0+a1)/2;v=np.linalg.solve(np.swapaxes(fs(h0),-1,-2),qi[...,None])[...,0];dd=np.linalg.norm(v,axis=1)*np.exp(tt-h0);m=dd>target;a0=np.where(m,h0,a0);a1=np.where(m,a1,h0)
     ar=(a0+a1)/2;v=np.linalg.solve(np.swapaxes(fs(ar),-1,-2),qi[...,None])[...,0];nh=v/np.linalg.norm(v,axis=1)[:,None];aa=1+np.einsum('ni,nij,nj->n',nh,S(ar),nh)
     # Cubic interpolate only the selected channel; clamp tiny negative
     # interpolation overshoot as a diagnostic error, reject substantive.
     op=tau(ar)[:,dest]/aa;assert np.min(op)>-1e-12
     T=np.exp(-np.maximum(op,0));absorbed=endE[ok]*(1-T);surv=endE[ok]*T
     total[2]+=absorbed.sum();total[5]+=surv.sum();total[3]+=endE[~ok].sum();absolute[2]+=np.sum(abs(absorbed));absolute[5]+=np.sum(abs(surv));absolute[3]+=np.sum(abs(endE[~ok]));count+=int(ok.sum())
   err=abs(total[1]-sum(total[2:6]));assert err<1e-13
   C=threshold[:,None]-E;comp=birth*C[None,:,:]
   o=dict(nmu=nm,samples=len(t),first_arrival_rays=count,tracked_birth=total[0],tracked_terminal_free=total[1],conditional_removed_at_terminal_equivalent=total[2],not_yet_arrived=total[3],unsupported_destination=total[4],first_transmitted_terminal_equivalent=total[5],partition_residual=err,absolute_removed=absolute[2],companion_signed_energy=float(comp.sum()),companion_positive_frequency_energy=float(np.sum(np.where(C>0,comp,0))),companion_raman_energy=float(np.sum(np.where(C<0,comp,0))),scope='conditional first-crossing direct attenuation of native effective departure flux treated as a test source; no dense re-emission, actual companion bath not an independent emitted spectrum; no feedback or double count')
   rows[f'{nm}_{nt}']=o;print(o,flush=True)
 (D/'FIRST_HIT.json').write_text(json.dumps(dict(rows=rows),indent=2)+'\n')
if __name__=='__main__':run()
