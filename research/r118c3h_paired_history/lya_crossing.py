"""Conditional single-pass Ly-alpha absorbing-screen diagnostic, no native reaction insertion."""
import numpy as np,json,hashlib
from pathlib import Path
from shared_gas_h import B,R,_canonical_twophoton_table,interpF,KB_NATIVE_EV_K,Clock,OriginalHyRecPrimitiveRateTable
D=Path(__file__).resolve().parent
P=D.parent/'r118c3g_causal_shared_gas/ACCEPTED_LOCAL_DIRECTIONAL.npz'
EL=10.198714553953742;A21=6.265e8;LYA_FACT=4.662899067555897e15
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def crossing(q,f,lo,hi,r0,a0,p):
 if not 0<=p<=1 or not 0<lo<=hi or min(f)<0:raise ValueError('crossing domain')
 l=np.maximum(q[:-1],lo);h=np.maximum(l,np.minimum(q[1:],hi))
 # stable factored volume difference
 n=float(f@((h-l)*(h*h+h*l+l*l)/3));u=float(r0/a0*(f@((h-l)*(h+l)*(h*h+l*l)/4)))
 absorbed=p*n;transmitted=(1-p)*n;work=u-EL*n
 return n,u,absorbed,transmitted,work
def main():
 v=np.load(P);eta=v['eta'];out=v['outgoing'];n=v['rays'];w=v['weights0'];Fref=v['reference_F'];rows=v['rows']
 g=np.genfromtxt(B/'plusfine.csv',names=True,delimiter=',');ge=np.log(g['a']);F=np.stack([g[f'F{i}{j}'] for i in range(3) for j in range(3)],axis=1).reshape(-1,3,3)
 m=Clock(h=.6735837,omega_cb=.31242079216478097,omega_r_h2=4.1578740068818545e-5,omega_de_h2=.3119234221656212,omega_b_h2=.02242,y_he_mass=.245,tcmb0_K=2.7255,table=OriginalHyRecPrimitiveRateTable.from_archive(R))
 E=_canonical_twophoton_table(R).energy_eV;edges=np.r_[E[0]*np.sqrt(E[0]/E[1]),np.sqrt(E[:-1]*E[1:]),E[-1]*np.sqrt(E[-1]/E[-2])]
 def rr(u):return np.linalg.norm(np.linalg.solve(interpF(ge,F,u).T,Fref.T)@n.T,axis=0)
 results=[]
 for i,j in [(len(eta)-2,len(eta)-1),(0,len(eta)-1)]:
  a0,a1=np.exp(eta[[i,j]]);r0,r1=rr(eta[i]),rr(eta[j]);u=(eta[i]+eta[j])/2;z=np.expm1(-u);_,nh=m.cosmology(z);H=np.interp(u,ge,g['h'])*2.1842852410855023e-18;x=np.interp(u,rows[:,0],rows[:,1])
  # native HMLA cosmology returns nH in cm^-3; check actual scale via method doc/usage.
  tau=A21*nh*(1-x)/(LYA_FACT*H);p=-np.expm1(-tau)
  fac=np.array([rr(t)/np.exp(t) for t in np.linspace(eta[i],eta[j],17)])
  assert np.all(np.diff(fac,axis=0)<0)
  f=1/np.expm1(E/(KB_NATIVE_EV_K*2.7255/a0))+out[i,:,:311]
  for prob in [0.,.1,float(p)]:
   a=np.array([crossing(edges*a0/r0[k],f[k],EL*a0/r0[k],EL*a1/r1[k],r0[k],a0,prob) for k in range(len(n))]);N,U,absorb,trans,work=w@a
   assert N>0 and work>=0
   nr=(absorb+trans-N)/N;er=(EL*(absorb+trans)+work-U)/U
   assert max(abs(nr),abs(er))<1e-12
   results.append(dict(i=i,j=j,tau=float(tau),p=prob,N=float(N),initial_energy=float(U),excitation=float(EL*absorb),transmitted_energy_at_crossing=float(EL*trans),redshift_work=float(work),number_residual=float(nr),energy_residual=float(er)))
 out=dict(status='SCOPED_CONDITIONAL_LYA_SCREEN',scope='collisionless crossing reconstructed from accepted outgoing spectrum, prescribed ground-state absorption, no reemission, no native chemistry feedback; common canonical measure prefactor omitted',source_sha=sha(P),geometry_sha=sha(B/'plusfine.csv'),rows=results)
 (D/'CROSSING.json').write_text(json.dumps(out,indent=2)+'\n');print(out,flush=True)
if __name__=='__main__':main()
