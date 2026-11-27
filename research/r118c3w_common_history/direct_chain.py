"""Subsequent native virtual-channel direct crossings of an effective test source.
No re-emission or physical packet interpretation of native Schur response.
"""
import numpy as np,json,sys
from pathlib import Path
from scipy.interpolate import CubicSpline
from numpy.polynomial.legendre import leggauss
D=Path(__file__).resolve().parent;P=D.parent/'r118c3v_event_comparator';sys.path.insert(0,str(P))
from spectral_source import B,R,_canonical_twophoton_table,stf
from full_bianchi_hyrec.trajectory.causal_virtual_redshift import _source_edges
def run(nm,nt):
 z=np.load(P/'SPECTRAL_SOURCE.npz');u=z['u'];J=z['J'];E=z['energy'];tab=_canonical_twophoton_table(R);src,ef,es=_source_edges(tab.energy_eV)
 rev=np.full(314,-1,dtype=int);rev[src]=np.arange(len(src));assert np.allclose(ef[:311],E,rtol=0,atol=0)
 g=np.genfromtxt(B/'plusfine.csv',names=True,delimiter=',');ge=np.log(g['a']);F=np.stack([g[f'F{i}{j}'] for i in range(3) for j in range(3)],axis=1).reshape(-1,3,3);fs=CubicSpline(ge,F,axis=0);S=CubicSpline(ge,np.array([stf([g[f'S{i}'][j] for i in range(5)]) for j in range(len(g))]),axis=0);tau=CubicSpline(u,z['Dtau'],axis=0)
 mu,w=leggauss(nm);m,ph=np.meshgrid(mu,np.arange(2*nm)*np.pi/nm,indexing='ij');n=np.stack([np.sqrt(1-m*m)*np.cos(ph),np.sqrt(1-m*m)*np.sin(ph),m],axis=-1).reshape(-1,3);w=np.repeat(w/(4*nm),2*nm)
 ids=np.unique(np.linspace(0,len(u)-1,nt).astype(int));t=u[ids];mid=(t[:-1]+t[1:])/2;birth=(J[ids[1:]]+J[ids[:-1]])/2*np.diff(t)[:,None,None];birth=birth.sum(axis=1)
 grid=np.linspace(t[0],t[-1],2049);inv=np.linalg.inv(fs(grid));endF=np.linalg.inv(fs(t[-1]));rays=len(n);jj=np.arange(311);tot=np.zeros(6);mass=np.zeros(16);count=np.zeros(16,dtype=int);err=0.;maxhit=0
 for k,tt in enumerate(mid):
  q=n@fs(tt);p=q@endF;dr=np.linalg.norm(p,axis=1)*np.exp(tt-t[-1]);stock=w[:,None]*birth[k][None,:]*E[None,:]*dr[:,None];tot[0]+=stock.sum()
  # Relative canonical clock for each local emission ray.
  d=np.linalg.norm(np.einsum('ni,tij->tnj',q,inv),axis=2);ell=grid[:,None]-np.log(d);assert np.min(np.diff(ell,axis=0))>0
  curr=np.broadcast_to(jj,(rays,311)).copy();rem=stock.copy();active=np.ones(curr.shape,bool)
  for gen in range(311):
   if not active.any():break
   dest=rev[curr];unsupported=active&((dest<0)|(dest>=311))
   tot[3]+=rem[unsupported].sum();active&=~unsupported
   safe=np.clip(dest,0,310);target=tt+np.log(E[None,:]/ef[safe])
   hit=active&(target<=ell[-1,:,None]);miss=active&~hit;tot[4]+=rem[miss].sum();active=hit
   if not hit.any():break
   ir,ic=np.where(hit);de=dest[hit];ttarg=target[hit]
   ar=np.empty(len(ir))
   for i in np.unique(ir):
    z0=ir==i;ar[z0]=np.interp(ttarg[z0],ell[:,i],grid)
   # Verify inverse and refine using exact coframe and directional rate.
   for _ in range(2):
    v=np.linalg.solve(np.swapaxes(fs(ar),-1,-2),q[ir,:,None])[...,0];dn=np.linalg.norm(v,axis=1);nh=v/dn[:,None]
    aa=1+np.einsum('ni,nij,nj->n',nh,S(ar),nh);res=ar-np.log(dn)-ttarg
    ar-=res/aa
   v=np.linalg.solve(np.swapaxes(fs(ar),-1,-2),q[ir,:,None])[...,0];dn=np.linalg.norm(v,axis=1);nh=v/dn[:,None];aa=1+np.einsum('ni,nij,nj->n',nh,S(ar),nh)
   err=max(err,float(np.max(abs(ar-np.log(dn)-ttarg))))
   it=np.clip(np.searchsorted(u,ar,side='right')-1,0,len(u)-2);du=ar-u[it];c0=tau.c[:,it,de];op=(((c0[0]*du+c0[1])*du+c0[2])*du+c0[3])/aa
   assert min(op)>-1e-12
   lost=rem[hit]*(-np.expm1(-np.maximum(op,0)));rem[hit]-=lost;tot[1 if gen==0 else 2]+=lost.sum()
   count[min(gen,15)]+=len(lost);mass[min(gen,15)]+=lost.sum();curr[hit]=de;maxhit=max(maxhit,gen+1)
  else:raise ValueError('graph did not terminate')
 errpart=abs(tot[0]-sum(tot[1:5]));assert errpart<1e-13 and err<1e-11
 o=dict(nmu=nm,rays=rays,samples=nt,free=tot[0],first_removed=tot[1],subsequent_removed=tot[2],unsupported=tot[3],not_yet_arrived=tot[4],partition_abs=errpart,clock_residual=err,max_crossings=maxhit,events=count.tolist(),removed_by_generation=mass.tolist(),scope='conditional direct transmission only through actual native virtual frequency graph and optical depths; effective signed source is not a conserved physical packet, no Schur re-emission or new gas heating')
 (D/f'CHAIN_{nm}_{nt}.json').write_text(json.dumps(o,indent=2)+'\n');print(o,flush=True)
if __name__=='__main__':run(int(sys.argv[1]),int(sys.argv[2]))
