"""Gas-temperature directional derivatives through native HyRec rates, diffusion and angular Schur owner."""
from pathlib import Path
import sys,numpy as np,json,hashlib,math
from scipy.linalg import solve_banded
D=Path(__file__).resolve().parent;P=D.parent
sys.path[:0]=[str(P/'r118c3w_common_history'),str(P/'r118c3x_three_moments'),str(D.parents[1]/'src')]
from common_base import context,p,JumpResponse
from full_bianchi_hyrec.trajectory.full_2012_atomic_source import _original_escape_factors,accurate_escape_factors
from full_bianchi_hyrec.trajectory.hmla_flrw import LYA_FACT_CM3
from full_bianchi_hyrec.recoil import original_hyrec_native as nd
def rel(x,y):return float(np.linalg.norm(x-y)/max(np.linalg.norm(y),1e-300))
def diffusion(tab,T):
 e=tab[:,0];a=tab[:,1];t=T*nd.K_B_EV_K;v=nd.E21_EV**2*2*t/nd.M_H_EV_C2
 u=np.zeros((311,2));d=u.copy();V=np.array([v,v])
 def bol(z,x):return math.exp(z)*np.array([x[0],x[1]-z*x[0]])
 b=100;u[b]=V*a[b]/(e[b+1]-e[b])**2
 for b in range(101,140):
  d[b]=bol((e[b]-e[b-1])/t,u[b-1])
  u[b]=(V*a[b]-(e[b]-e[b-1])**2*d[b])/((e[b+1] if b<139 else nd.E21_EV)-e[b])**2
 dn2=bol((nd.E21_EV-e[139])/t,u[139])/3
 b=179;d[b]=V*a[b]/(e[b]-e[b-1])**2
 for b in range(178,139,-1):
  u[b]=bol((e[b]-e[b+1])/t,d[b+1])
  d[b]=(V*a[b]-(e[b+1]-e[b])**2*u[b])/(e[b]-(e[b-1] if b>140 else nd.E21_EV))**2
 up2=bol((nd.E21_EV-e[140])/t,d[140])/3
 # Mirror source clipping of negative primal (locally constant clipped branch).
 for z in (u,d):z[z[:,0]<0]=0
 a0=nd.populate_original_hyrec_diffusion(tab,T)
 primal=max(rel(u[:,0],a0.Aup_s_inv),rel(d[:,0],a0.Adn_s_inv),rel(np.array([up2[0],dn2[0]]),np.array([a0.A2p_up_s_inv,a0.A2p_dn_s_inv])))
 assert primal<1e-12,primal
 return u[:,1],d[:,1],up2[1],dn2[1],primal
def jvp(c,s,a,w,I,T):
 w=w/w.sum();tau=s.Dtau;x=s.xHII;x1=1-x
 tab=np.column_stack((c.tab.energy_eV,c.tab.integrated_rates_s_inv.T))
 up,dn,up2,dn2,dpar=diffusion(tab,T)
 rate=c.model.table.evaluate(radiation_temperature_eV_rescaled=s.Tr_eV,matter_to_radiation_temperature_ratio=s.Tm_eV/s.Tr_eV)
 da=rate.d_alpha_d_Tm_over_Tr_m3_s*(s.Tm_eV/s.Tr_eV)*1e6
 dda=rate.d_delta_alpha_d_Tm_over_Tr_m3_s*(s.Tm_eV/s.Tr_eV)*1e6
 ds=s.nH_cgs*(s.saha_ratio*x1*dda+(s.xe*x-s.saha_ratio*x1)*da)
 drr=np.zeros((2,2));drr[1,1]=up2+dn2
 drv=np.zeros_like(s.Trv);dvr=np.zeros_like(s.Tvr)
 dvr[1,139]=-dn2;drv[1,139]=-up[139];dvr[1,140]=-up2;drv[1,140]=-dn[140]
 pi0,_=_original_escape_factors(tau);gamma=pi0*s.Tvv[0];dgamma=up+dn;ok=gamma>0
 dtau=np.divide(tau*dgamma,gamma,out=np.zeros_like(tau),where=ok)
 t=tau[None,:]/a[:,None];dt=dtau[None,:]/a[:,None]
 pi,tr=accurate_escape_factors(t)
 dp0=np.empty_like(t);small=t<.03;q=t[small];dp0[small]=.5+q*(-1/3+q*(1/8+q*(-1/30+q*(1/144-q/840))));q=t[~small];dp0[~small]=(-np.expm1(-q)-q*np.exp(-q))/q**2
 dp=dp0*dt;dtr=np.exp(-t)*dt
 inv=np.divide(pi,gamma[None,:],out=np.broadcast_to(1/(a[:,None]*s.Tvv[0]),pi.shape).copy(),where=ok[None,:])
 # Stable derivative of pi/gamma using d(log gamma) and cancellation at small depth.
 dif=dp0*t-pi; q=t[small];dif[small]=q*q*(-1/6+q*(1/12+q*(-1/40+q*(1/180-q/1008))))
 dinv=np.divide(dif*dgamma[None,:],gamma[None,:]**2,out=np.zeros_like(inv),where=ok[None,:])
 vv=1/(w@inv);dvv=-vv**2*(w@dinv)
 inc=I[:,:311];Ly=I[:,311:];z=w@((1-pi)*inc);dz=w@(-dp*inc);b=vv*x1*z;db=x1*(dvv*z+vv*dz)
 L=LYA_FACT_CM3*s.H_s_inv/(s.nH_cgs*x1);k=np.array([1.664786871919931,1.]);ly=w@(a[:,None]*Ly)
 br=s.sr-3*L*x1*s.incoming_lyman[::-1]*k+3*L*x1*ly[::-1]*k
 dvblock=np.zeros_like(s.Tvv);dvblock[0]=dvv;dvblock[1,101:140]=-up[100:139];dvblock[1,141:180]=-up[140:179];dvblock[2,100:139]=-dn[101:140];dvblock[2,140:179]=-dn[141:180]
 ab=np.zeros_like(s.Tvv);ab[1]=vv;ab[0,1:]=s.Tvv[2,:-1];ab[2,:-1]=s.Tvv[1,1:]
 Z=solve_banded((1,1),ab,s.Tvr.T,check_finite=False);E=s.Trr-s.Trv@Z
 def solve(b,r):
  v=solve_banded((1,1),ab,b,check_finite=False);r=np.linalg.solve(E,r-s.Trv@v);return r,v-Z@r
 def nb(v,block):
  z=np.zeros(311);z[1:]+=v[:-1]*block[1,1:];z[:-1]+=v[1:]*block[2,:-1];return z
 r,v=solve(b,br);rb=ds-drr@r-drv@v;vb=db-dvr.T@r-dvv*v-nb(v,dvblock)
 dr,dv=solve(vb,rb)
 residual=max(np.max(abs(s.Trr@dr+s.Trv@dv-rb)),np.max(abs(s.Tvr.T@dr+vv*dv+nb(dv,s.Tvv)-vb)))/max(np.max(abs(rb)),np.max(abs(vb)),1e-300)
 q=np.divide(-(r@s.Tvr+nb(v,s.Tvv)),x1*gamma,out=np.zeros(311),where=ok)
 dq=np.divide(-(dr@s.Tvr+r@dvr+nb(dv,s.Tvv)+nb(v,dvblock))-q*x1*dgamma,x1*gamma,out=np.zeros(311),where=ok)
 o=inc+(q-inc)*tr;do=dq*tr+(q-inc)*dtr;mask=tau<=1e-30;o[:,mask]=inc[:,mask];do[:,mask]=0.
 lyb=np.exp(-1.8886508433247664/s.Tr_eV);lyg=np.exp(-2.5496786384884356/s.Tr_eV)
 def lyo(r):return np.broadcast_to([r[1]/(3*x1),r[0]/x1*lyb,r[0]/x1*lyg],(len(a),3))
 gas=(r@s.Beta_s_inv-np.sum(s.nH_cgs*(s.saha_ratio*x1*s.DAlpha_cgs+s.Alpha_cgs*(s.xe*x-s.saha_ratio*x1))))/s.H_s_inv
 dg=(dr@s.Beta_s_inv-ds.sum())/s.H_s_inv
 return gas,np.c_[o,lyo(r)],dg,np.c_[do,lyo(dr)],float(residual),dpar
def main():
 c=context(128);z=np.load(P/'r118c4h_goal_adjoint/goal_q3_128_-0.5.npz');he=z['he'];v=z['rows'][:,1:3];c.v=np.stack([np.interp(he,c.he,c.v[:,j]) for j in range(c.v.shape[1])],axis=1);c.he=he
 import importlib.util
 sys.path.insert(0,str(P/'r118c4k_lambda_tangent'))
 spec=importlib.util.spec_from_file_location('prior_rec',P/'r118c4k_lambda_tangent/rec.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
 m=mod.Map(c,-.5);K=P/'r118c4m_analytic_history'/'ANALYTIC_HISTORY.npz';last=np.load(K)['last'];inc=last[:,:,0][:,c.src]
 rows=[]
 for i in [1,63,99,512,918,974,1773]:
  u=he[i];x,T=v[i];a,w=m.state(u);s,H,Tr=c.snap(u,x,T,c.zero)
  for label,I in [('zero',np.zeros_like(inc)),('represented_terminal_stock',inc)]:
   def f(xx,tt):
    ss,_,_=c.snap(u,xx,tt,c.zero);r,o,_=p.step(ss,a,np.zeros_like(I),w);j=JumpResponse(ss,a,w);b,c0,g=j.apply(I);return r.dxHII_dln_a+g,o+b+c0
   G,O,dG,dO,res,dpar=jvp(c,s,a,w,I,T);g,o=f(x,T)
   tests=[]
   for ep in [1e-3,3e-4,1e-4,3e-5]:
    gm,om=f(x,T*np.exp(-ep))
    if T*np.exp(ep)<=Tr:
     gp,op=f(x,T*np.exp(ep));fd=(gp-gm)/(2*ep);fo=(op-om)/(2*ep);kind='centered'
    else:
     gm2,om2=f(x,T*np.exp(-2*ep));fd=(3*g-4*gm+gm2)/(2*ep);fo=(3*o-4*om+om2)/(2*ep);kind='inward'
    tests.append(dict(eps=ep,kind=kind,gas_relative=float(abs(fd-dG)/max(abs(dG),1e-300)),outgoing_relative=rel(fo,dO)))
   ex=min(1e-6,.05*x,.05*(1-x));gx=(f(x+ex,T)[0]-f(x-ex,T)[0])/(2*ex)
   scale=p.COMPTON_GAMMA_PER_T4_S_INV_K4*Tr**4/H;A=scale*x/(1+x+c.model.f_he);Ax=scale*(1+c.model.f_he)/(1+x+c.model.f_he)**2
   J=np.array([[gx,dG/T],[Ax*(Tr-T),-2-A]]);eig=np.linalg.eigvals(J)
   row=dict(step=i,u=float(u),x=float(x),T=float(T),Tr=float(Tr),incident=label,base_gas_gap=float(abs(G-g)/max(abs(g),1e-300)),base_outgoing_relative=rel(O,o),dG=float(dG),dO_norm=float(np.linalg.norm(dO)),matrix_residual=res,diffusion_primal=dpar,tests=tests,thermal_J=J.tolist(),eig=[[float(t.real),float(t.imag)] for t in eig],frozen_T_gas=float(gx),quasisteady_gas=float(gx-J[0,1]*J[1,0]/J[1,1]))
   rows.append(row);print(json.dumps(row),flush=True)
 (D/'RESULT.json').write_text(json.dumps(dict(rows=rows,source_sha=hashlib.sha256(K.read_bytes()).hexdigest(),goal_sha=hashlib.sha256((P/'r118c4h_goal_adjoint/goal_q3_128_-0.5.npz').read_bytes()).hexdigest(),scope='actual fixed geometry angular atomic map, analytic log Tm derivative of original table and diffusion recursion; incident held fixed; local ion/thermal Jacobian not integrated history'),indent=2,allow_nan=False)+'\n')
if __name__=='__main__':main()
