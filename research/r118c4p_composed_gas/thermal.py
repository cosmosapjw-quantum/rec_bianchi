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
def jvp(c,s,a,w,I,T,scale=1.):
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
 br=scale*(s.sr-3*L*x1*s.incoming_lyman[::-1]*k)+3*L*x1*ly[::-1]*k
 dvblock=np.zeros_like(s.Tvv);dvblock[0]=dvv;dvblock[1,101:140]=-up[100:139];dvblock[1,141:180]=-up[140:179];dvblock[2,100:139]=-dn[101:140];dvblock[2,140:179]=-dn[141:180]
 ab=np.zeros_like(s.Tvv);ab[1]=vv;ab[0,1:]=s.Tvv[2,:-1];ab[2,:-1]=s.Tvv[1,1:]
 Z=solve_banded((1,1),ab,s.Tvr.T,check_finite=False);E=s.Trr-s.Trv@Z
 def solve(b,r):
  v=solve_banded((1,1),ab,b,check_finite=False);r=np.linalg.solve(E,r-s.Trv@v);return r,v-Z@r
 def nb(v,block):
  z=np.zeros(311);z[1:]+=v[:-1]*block[1,1:];z[:-1]+=v[1:]*block[2,:-1];return z
 r,v=solve(b,br);rb=scale*ds-drr@r-drv@v;vb=db-dvr.T@r-dvv*v-nb(v,dvblock)
 dr,dv=solve(vb,rb)
 residual=max(np.max(abs(s.Trr@dr+s.Trv@dv-rb)),np.max(abs(s.Tvr.T@dr+vv*dv+nb(dv,s.Tvv)-vb)))/max(np.max(abs(rb)),np.max(abs(vb)),1e-300)
 q=np.divide(-(r@s.Tvr+nb(v,s.Tvv)),x1*gamma,out=np.zeros(311),where=ok)
 dq=np.divide(-(dr@s.Tvr+r@dvr+nb(dv,s.Tvv)+nb(v,dvblock))-q*x1*dgamma,x1*gamma,out=np.zeros(311),where=ok)
 o=inc+(q-inc)*tr;do=dq*tr+(q-inc)*dtr;mask=tau<=1e-30;o[:,mask]=inc[:,mask];do[:,mask]=0.
 lyb=np.exp(-1.8886508433247664/s.Tr_eV);lyg=np.exp(-2.5496786384884356/s.Tr_eV)
 def lyo(r):return np.broadcast_to([r[1]/(3*x1),r[0]/x1*lyb,r[0]/x1*lyg],(len(a),3))
 gas=(r@s.Beta_s_inv-scale*np.sum(s.nH_cgs*(s.saha_ratio*x1*s.DAlpha_cgs+s.Alpha_cgs*(s.xe*x-s.saha_ratio*x1))))/s.H_s_inv
 dg=(dr@s.Beta_s_inv-scale*ds.sum())/s.H_s_inv
 return gas,np.c_[o,lyo(r)],dg,np.c_[do,lyo(dr)],float(residual),dpar
