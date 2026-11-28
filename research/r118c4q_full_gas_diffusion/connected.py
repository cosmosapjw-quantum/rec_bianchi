"""Exact budget obstruction certificate and strictly positive connected diffusion proxy."""
from pathlib import Path
import numpy as np,json,hashlib
from scipy.optimize import nnls
from scipy.linalg import eigvalsh
D=Path(__file__).resolve().parent
def main():
 src=D/'DIFFUSION.npz';a=np.load(src);e=a['energy'];de=np.diff(e);ids=np.r_[np.arange(40),np.arange(41,81)];M=np.zeros((81,80));M[np.arange(80),np.arange(80)]=1;M[np.arange(1,81),np.arange(80)]=1;M=M[ids];inv=np.linalg.inv(M);assert np.array_equal(inv,np.rint(inv))
 meta=json.loads((D/'DIFFUSION.json').read_text());rows=[];arrays={}
 for r in meta['rows']:
  k=f"{r['step']}_{r['ratio']:g}";g=a[k][:,0];b=a[k+'_budget'][:,0];scale=b.max();v=int(np.argmin(g));y=inv[v];cert=float(y@b/scale);assert np.max(abs(y@M-np.eye(80)[v]))==0
  if r['exact_negative_edges']>0:assert cert<0
  pi=np.exp(-(e-e[40])/(r['T']*8.617343e-5));pi[40]*=3;pi/=pi.sum()
  # Compare actual native thermal constant below if it differs: use imported authoritative constant.
  from thermal import nd
  pi=np.exp(-(e-e[40])/(r['T']*nd.K_B_EV_K));pi[40]*=3;pi/=pi.sum()
  base=np.array([min(b[M[:,i]>0]) for i in range(80)])
  for eps in [0.,1e-8,1e-4,1e-2]:
   lo=eps*base;g1=nnls(M/b[:,None]*scale,1-M@lo/b,maxiter=2000)[0]*scale+lo
   c=g1/de**2;Q=np.zeros((81,81))
   for j,vv in enumerate(c):Q[j+1,j]=vv/pi[j];Q[j,j+1]=vv/pi[j+1]
   np.fill_diagonal(Q,-Q.sum(axis=0));mag=float(np.max(abs(Q)));R=Q/mag;sim=R*np.sqrt(pi[None,:]/pi[:,None]);ev=eigvalsh((sim+sim.T)/2)
   err=(M@g1-b)/b;db=R*pi[None,:];row=dict(step=r['step'],ratio=r['ratio'],floor=eps,certificate_edge=v,certificate_value=cert,exact_budget_feasible=bool(r['exact_negative_edges']==0),min_conductance=float(c.min()),connected=bool(np.all(c>0)),rms_budget=float(np.sqrt(np.mean(err**2))),max_budget=float(np.max(abs(err))),normalized_spectral_gap=float(-ev[-2]),zero_eigenvalues=int(np.sum(abs(ev)<1e-12)),equilibrium_res=float(np.max(abs(R@pi))/pi.max()),detailed_balance=float(np.linalg.norm(db-db.T)/np.linalg.norm(db)),symmetry=float(np.linalg.norm(sim-sim.T)/np.linalg.norm(sim)))
   assert row['equilibrium_res']<1e-12 and row['detailed_balance']<1e-12
   if eps>0:assert row['connected']
   rows.append(row);arrays[k+f'_{eps:g}']=g1
 (D/'CONNECTED.json').write_text(json.dumps(dict(rows=rows,diffusion_sha=hashlib.sha256(src.read_bytes()).hexdigest(),scope='exact Farkas certificate for nonnegative conductance impossibility under native fixed budgets; positive floor-constrained NNLS gives connected reversible finite proxy, budgets not exact at cold T'),indent=2,allow_nan=False)+'\n')
 np.savez_compressed(D/'CONNECTED.npz',**arrays);print(json.dumps([x for x in rows if x['step']==1773 and x['ratio']==.25],indent=2))
if __name__=='__main__':main()
