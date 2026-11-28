"""Reversible positive edge conductance alternative to native cold diffusion recurrence."""
from pathlib import Path
import sys,json,numpy as np,hashlib
from scipy.optimize import nnls
from scipy.linalg import solve
D=Path(__file__).resolve().parent;P=D.parent
from thermal import context,p
from full_bianchi_hyrec.recoil import original_hyrec_native as nd
def main():
 c=context(128);ref=P/'r118c4h_goal_adjoint/goal_q3_128_-0.5.npz';z=np.load(ref);he=z['he'];tab=np.column_stack((c.tab.energy_eV,c.tab.integrated_rates_s_inv.T))
 e0=tab[100:180,0];e=np.insert(e0,40,nd.E21_EV);deg=np.ones(81);deg[40]=3.;de=np.diff(e);assert np.all(de>0)
 ids=np.r_[np.arange(40),np.arange(41,81)]
 inc=np.zeros((81,80));inc[np.arange(80),np.arange(80)]=1;inc[np.arange(1,81),np.arange(80)]=1;M=inc[ids]
 rows=[];arrays={}
 for step in [63,918,1773]:
  Tr=c.model.tcmb0_K*np.exp(-he[step])
  for rat in [.25,.4,.44,.45,.5,.8,1.]:
   T=rat*Tr;te=T*nd.K_B_EV_K;pi=deg*np.exp(-(e-e[40])/te);pi/=pi.sum()
   b=pi[ids]*(nd.E21_EV**2*2*te/nd.M_H_EV_C2)*tab[100:180,1]
   assert np.all(b>0)
   # Exact unique solution (80 constraints, 80 edges, two arms from outside).
   scale=b.max();g=np.linalg.solve(M,b/scale)*scale
   exact_res=float(np.linalg.norm(M@g-b)/np.linalg.norm(b))
   # Relative budget NNLS using positive normalization per vertex; exact native rate budgets are not relaxed silently.
   gr,rs=nnls(M/b[:,None]*scale,np.ones(80),maxiter=2000);gp=gr*scale
   cons=gp/de**2;Q=np.zeros((81,81))
   for i,v in enumerate(cons):Q[i+1,i]=v/pi[i];Q[i,i+1]=v/pi[i+1]
   np.fill_diagonal(Q,-Q.sum(axis=0))
   mag=np.max(abs(Q));R=Q/mag
   db=Q*pi[None,:];res=float(np.linalg.norm(db-db.T)/max(np.linalg.norm(db),1e-300))
   be=solve(np.eye(81)-10*R,np.linspace(1,2,81));native=None
   try:
    r=nd.populate_original_hyrec_diffusion(tab,T);net=nd.build_native_diffusion_network(r);perm=np.r_[np.arange(40),80,np.arange(40,80)]
    nQ=net.generator_s_inv[np.ix_(perm,perm)]
    native=float(np.linalg.norm(Q-nQ)/max(np.linalg.norm(nQ),1e-300))
   except FloatingPointError:pass
   berr=(M@gp-b)/b
   row=dict(step=step,ratio=rat,T=float(T),native_accepted=native is not None,native_relative_if_accepted=native,exact_negative_edges=int(np.sum(g < -1e-12*scale)),exact_min_scaled=float(g.min()/scale),exact_budget_residual=exact_res,nnls_relative_rms=float(np.sqrt(np.mean(berr**2))),nnls_max_relative=float(np.max(abs(berr))),nnls_zero_edges=int(np.sum(gp==0)),number_relative=float(np.max(abs(R.sum(axis=0)))),equilibrium_relative=float(np.max(abs(R@pi))/max(pi)),detailed_balance_relative=res,min_BE=float(be.min()),BE_mass_gap=float(abs(be.sum()-np.linspace(1,2,81).sum())))
   assert row['number_relative']<1e-12 and row['equilibrium_relative']<1e-12 and res<1e-12 and be.min()>0 and row['BE_mass_gap']<1e-10
   rows.append(row);arrays[f'{step}_{rat:g}']=np.c_[g,gp];arrays[f'{step}_{rat:g}_budget']=np.c_[b,M@gp]
   print(json.dumps(row),flush=True)
 np.savez_compressed(D/'DIFFUSION.npz',energy=e,**arrays)
 (D/'DIFFUSION.json').write_text(json.dumps(dict(rows=rows,source_sha=hashlib.sha256(ref.read_bytes()).hexdigest(),table_sha=hashlib.sha256(tab.tobytes()).hexdigest(),scope='source-owned primitive virtual-level proxy, exact signed local second moment edge solution versus relative budget NNLS reversible alternative; no full transfer or replacement claim'),indent=2,allow_nan=False)+'\n')
if __name__=='__main__':main()
