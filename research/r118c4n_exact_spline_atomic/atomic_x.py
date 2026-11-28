"""Source-owned fixed-T H-only abundance JVP, analytic at fixed angular geometry and incident field.
Separate from the already-running full angular/spline history. No derivative of T-dependent rate tables."""
from pathlib import Path
import sys,numpy as np,json,hashlib,time
from scipy.linalg import solve_banded
D=Path(__file__).resolve().parent;P=D.parent;K=P/'r118c4m_analytic_history';sys.path[:0]=[str(P/'r118c3w_common_history'),str(P/'r118c3x_three_moments'),str(D.parents[1]/'src')]
from common_base import context,p,JumpResponse
from full_bianchi_hyrec.trajectory.full_2012_atomic_source import _original_escape_factors,accurate_escape_factors
from full_bianchi_hyrec.trajectory.hmla_flrw import LYA_FACT_CM3
def jvp(s,a,w,I,scale=1.):
 w=w/w.sum();tau=s.Dtau;x=s.xHII;x1=1-x;assert s.xe==x
 pi0,_=_original_escape_factors(tau);gamma=pi0*s.Tvv[0];ok=gamma>0;t=tau[None,:]/a[:,None];dt=-t/x1
 pi,tr=accurate_escape_factors(t);dp0=np.empty_like(t);small=t<.03;q=t[small];dp0[small]=.5+q*(-1/3+q*(1/8+q*(-1/30+q*(1/144-q/840))));q=t[~small];dp0[~small]=(-np.expm1(-q)-q*np.exp(-q))/q**2;dp=dp0*dt;dtr=np.exp(-t)*dt
 inv=np.divide(pi,gamma[None,:],out=np.broadcast_to(1/(a[:,None]*s.Tvv[0]),pi.shape).copy(),where=ok[None,:])
 dinv=np.divide(dp,gamma[None,:],out=-inv/x1,where=ok[None,:])
 vv=1/(w@inv);dvv=-vv**2*(w@dinv)
 inc=I[:,:311];Ly=I[:,311:];z=w@((1-pi)*inc);dz=w@(-dp*inc);b=vv*x1*z;db=(dvv*x1-vv)*z+vv*x1*dz
 L=LYA_FACT_CM3*s.H_s_inv/(s.nH_cgs*x1);c=np.array([1.664786871919931,1.]);ly=w@(a[:,None]*Ly)
 br=scale*(s.sr-3*L*x1*s.incoming_lyman[::-1]*c)+3*L*x1*ly[::-1]*c
 dsrc=s.nH_cgs*(-s.saha_ratio*s.DAlpha_cgs+s.Alpha_cgs*(2*x+s.saha_ratio))
 # Original Trr contains beta, mixing, couplings and Ly escape. Only L depends on x.
 lyb=np.exp(-1.8886508433247664/s.Tr_eV);lyg=np.exp(-2.5496786384884356/s.Tr_eV)
 drr=np.diag([3*L/x1*(1.664786871919931*lyb+1.953125*lyg),L/x1])
 ab=np.zeros_like(s.Tvv);ab[1]=vv;ab[0,1:]=s.Tvv[2,:-1];ab[2,:-1]=s.Tvv[1,1:]
 Z=solve_banded((1,1),ab,s.Tvr.T,check_finite=False);E=s.Trr-s.Trv@Z
 def solve(b,r):
  v=solve_banded((1,1),ab,b,check_finite=False);r=np.linalg.solve(E,r-s.Trv@v);return r,v-Z@r
 r,v=solve(b,br);dr,dv=solve(db-dvv*v,scale*dsrc-drr@r)
 def eq(r,v):
  neigh=np.zeros(311);neigh[1:]+=v[:-1]*s.Tvv[1,1:];neigh[:-1]+=v[1:]*s.Tvv[2,:-1]
  return np.divide(-(r@s.Tvr+neigh),x1*gamma,out=np.zeros(311),where=ok)
 q=eq(r,v);dq=eq(dr,dv)+q/x1
 o=inc+(q-inc)*tr;do=dq*tr+(q-inc)*dtr;mask=tau<=1e-30;o[:,mask]=inc[:,mask];do[:,mask]=0.
 def ly(r):return np.broadcast_to([r[1]/(3*x1),r[0]/x1*lyb,r[0]/x1*lyg],(len(a),3))
 gas=(r@s.Beta_s_inv-scale*np.sum(s.nH_cgs*(s.saha_ratio*x1*s.DAlpha_cgs+s.Alpha_cgs*(s.xe*x-s.saha_ratio*x1))))/s.H_s_inv
 dg=(dr@s.Beta_s_inv-scale*dsrc.sum())/s.H_s_inv
 return gas,np.c_[o,ly(r)],dg,np.c_[do,ly(dr)+ly(r)/x1]
def main():
 c=context(128);z=np.load(P/'r118c4h_goal_adjoint/goal_q3_128_-0.5.npz');he=z['he'];v=z['rows'][:,1:3];c.v=np.stack([np.interp(he,c.he,c.v[:,j]) for j in range(c.v.shape[1])],axis=1);c.he=he
 # Import actual map class without rec name collision.
 import importlib.util
 sys.path.insert(0,str(P/"r118c4k_lambda_tangent"))
 spec=importlib.util.spec_from_file_location('prior_rec',P/'r118c4k_lambda_tangent/rec.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
 m=mod.Map(c,-.5);last=np.load(K/'ANALYTIC_HISTORY.npz')['last'];inc=last[:,:,0][:,c.src];assert inc.shape==(c.nr,313)
 rows=[]
 for i in [1,63,99,512,918,974,1773]:
  u=he[i];x,T=v[i];a,w=m.state(u);s,_,_=c.snap(u,x,T,c.zero)
  for label,I in [('zero',np.zeros_like(inc)),('represented_terminal_stock',inc)]:
   def f(xx):
    s,_,_=c.snap(u,xx,T,c.zero);r,o,_=p.step(s,a,np.zeros_like(I),w);j=JumpResponse(s,a,w);b,c0,g=j.apply(I);return r.dxHII_dln_a+g,o+b+c0
   G,O,dG,dO=jvp(s,a,w,I);g,o=f(x);tests=[]
   for ep in [1e-5,3e-6,1e-6]:
    gp,op=f(x+ep);gm,om=f(x-ep);fd=(gp-gm)/(2*ep);fo=(op-om)/(2*ep)
    tests.append(dict(eps=ep,gas_relative=float(abs(fd-dG)/max(abs(dG),1e-300)),outgoing_relative=float(np.linalg.norm(fo-dO)/max(np.linalg.norm(dO),1e-300))))
   rows.append(dict(step=i,u=float(u),x=float(x),T=float(T),incident=label,base_gas_gap=float(abs(G-g)),base_outgoing_relative=float(np.linalg.norm(O-o)/max(np.linalg.norm(o),1e-300)),dG=float(dG),dO_norm=float(np.linalg.norm(dO)),tests=tests))
   print(rows[-1],flush=True)
 (D/'ATOMIC_X_JVP.json').write_text(json.dumps(dict(rows=rows,source_sha=hashlib.sha256((K/'ANALYTIC_HISTORY.npz').read_bytes()).hexdigest(),scope='analytic fixed-temperature H-only abundance derivative at actual gas/geometry snapshots; terminal represented stock used as controlled nonzero incident fixture, not actual retarded field at every step; no T derivative or full history integration'),indent=2,allow_nan=False)+'\n')
if __name__=='__main__':main()
