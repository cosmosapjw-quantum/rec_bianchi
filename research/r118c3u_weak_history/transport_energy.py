"""Conditional free-flight transport of native two-photon/Raman departure energy.
Use exact source samples and actual BASS coframe; companion signed source.
No reabsorption or atomic feedback, not escaped spectrum.
"""
import numpy as np,json,sys
from pathlib import Path
from numpy.polynomial.legendre import leggauss
from scipy.interpolate import CubicSpline
D=Path(__file__).resolve().parent;P=D.parent/'r118c3t_second_tangent'
sys.path.insert(0,str(P));import two_photon as t
def run():
 z=np.load(P/'TWO_PHOTON.npz');u=z['u'];src=z['source'];assert src.shape==(128,2,4,3)
 g=np.genfromtxt(t.B/'plusfine.csv',names=True,delimiter=',');ge=np.log(g['a']);F=np.stack([g[f'F{i}{j}'] for i in range(3) for j in range(3)],axis=1).reshape(-1,3,3);s=CubicSpline(ge,F,axis=0)
 rows={}
 for nmu in [4,8,16]:
  m,w=leggauss(nmu);m,ph=np.meshgrid(m,2*np.pi*np.arange(2*nmu)/(2*nmu),indexing='ij');n=np.stack([np.sqrt(1-m*m)*np.cos(ph),np.sqrt(1-m*m)*np.sin(ph),m],axis=-1).reshape(-1,3);w=np.repeat(w/(4*nmu),2*nmu)
  for nt in [33,65,128]:
   ii=np.unique(np.linspace(0,len(u)-1,nt).astype(int));tt=u[ii];v=src[ii];h=np.diff(tt);mid=(tt[:-1]+tt[1:])/2;f=(v[:-1]+v[1:])/2
   # Local isotropic emission direction at each midpoint; canonical momenta
   # propagate freely to terminal coframe. Same direction distribution for
   # the two signed energy reservoirs is a declared conditional choice.
   fm=s(mid);fin=s(tt[-1]);A=np.linalg.solve(fin.T,np.swapaxes(fm,-1,-2));p=np.einsum('mij,nj->mni',A,n);d=np.linalg.norm(p,axis=2)*np.exp(mid[:,None]-tt[-1]);dirs=p/np.linalg.norm(p,axis=2)[:,:,None]
   R=d@w;born=np.sum(f*h[:,None,None,None],axis=0)
   # channel-wise energy integrals at fixed final time
   end=np.sum(f*h[:,None,None,None]*R[:,None,None,None],axis=0)
   # number does not redshift
   end[:,0]=born[:,0];work=born[:,1:]-end[:,1:]
   err=float(np.max(abs(end[:,1]+end[:,2]-end[:,3])));assert err<1e-15
   # terminal radiation pressure trace and STF, sum over channels/processes
   E=f[:,:,3,:].sum(axis=(1,2))*h;Pi=np.einsum('m,mn,n,mni,mnj->ij',E,d,w,dirs,dirs);U=float(end[:,3,:].sum());assert abs(np.trace(Pi)-U)<1e-14
   Pi-=np.eye(3)*U/3
   rows[f'{nmu}_{nt}']=dict(birth_energy=float(born[:,3,:].sum()),terminal_tracked=float(end[:,1,:].sum()),terminal_companion=float(end[:,2,:].sum()),terminal_total=U,metric_work=float(work[:,2,:].sum()),energy_partition_abs=err,STF_norm=float(np.linalg.norm(Pi)),number_change=float(np.max(abs(end[:,0]-born[:,0]))))
 out=dict(rows=rows,scope='conditional isotropic births of actual native net effective tracked/signed companion energy and free transport on BASS coframe. No reabsorption, no cascade emissivity, no escaped spectrum; companion signed energy only.')
 (D/'TRANSPORT_ENERGY.json').write_text(json.dumps(out,indent=2)+'\n');print(out,flush=True)
if __name__=='__main__':run()
