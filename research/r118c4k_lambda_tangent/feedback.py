"""Fresh source-owned HeI 2s emission, HMLA effective H emission ledger and HI continuum recycling.
Fixed thermal steady closure, no H excited-state spectral absorption or full multilevel radiative feedback."""
from pathlib import Path
import sys,json,hashlib,numpy as np,math,time
from scipy.constants import c as clight
from scipy.optimize import brentq
D=Path(__file__).resolve().parent;P=D.parent;I=P/'r118c4i_weak_adjoint';J=P/'r118c4j_signed_tangent';H=P/'r118c4h_goal_adjoint'
sys.path[:0]=[str(D.parents[1]/'src'),str(P/'r118c3w_common_history')]
from common_base import context
from full_bianchi_hyrec.trajectory.primordial_2012_helium import HyRec2012Cosmology,integrate_helium_stages,helium_rhs,tm_steady_K
from full_bianchi_hyrec.trajectory.primordial_2012_full_start import make_hmla_source
from full_bianchi_hyrec.trajectory.hmla_flrw import KB_NATIVE_EV_K,LYA_FACT_CM3,LAMBDA_2S1S_S_INV
from full_bianchi_hyrec.trajectory.primitive_rates import SAHA_COEFFICIENT_CGS,IONIZATION_ENERGY_EV
g={'__file__':str(H/'helium.py'),'__name__':'prior'};exec(compile((H/'helium.py').read_text(),str(H/'helium.py'),'exec'),g);sigma=g['sigma'];profile=g['profile']
cos=HyRec2012Cosmology();he=integrate_helium_stages(cos);c=context(128);source=make_hmla_source(cos,c.model.table)
p=I/'HI_FEEDBACK.npz';z=np.load(p);u0=float(z['u'][-1]);u1=-np.log(1501.);z0=np.expm1(-u0);he0=float(he.xHeII[-1]);assert abs(he.z[-1]-z0)<1e-9 and KB_NATIVE_EV_K*cos.T0_K*np.exp(-u0)<=.4
thr=13.598434599702;Ehe=KB_NATIVE_EV_K*(285325-46090);Eh=.75*IONIZATION_ENERGY_EV
x,w=np.polynomial.legendre.leggauss(96);x=(x+1)/2;w=w/2*profile(x);w/=w.sum();assert abs(w@x-.5)<1e-14
# Exact original HyRec integrated 2s weights, symmetrize pair energies for the diagnostic spontaneous profile.
tab=c.tab;sel=tab.energy_eV<Eh;eh=tab.energy_eV[sel];wh=tab.A2s_s_inv[sel];wh=wh/wh.sum()
assert len(eh)>0 and abs(wh.sum()-1)<1e-14 and np.all((eh>0)&(eh<Eh))
def he_split(y,e,red,HH):
 tr=cos.T0_K*(1+red);nh=cos.nH0_m3*(1+red)**3;xe=e+(1-y);xhei=cos.fHe-e
 s0=2.414194e21*tr*math.sqrt(tr)/nh*4;s=s0*math.exp(-285325/tr);y2s=math.exp(46090/tr)/s0;y2p=3*math.exp(39101/tr)/s0
 eta=9.15776e28*HH/nh/y
 gg=(1.976e6/(1-math.exp(-6989/tr))+6.03e6/math.expm1(19754/tr)+1.06e8/math.expm1(21539/tr)+2.18e6/math.expm1(28496/tr)+3.37e7/math.expm1(29224/tr)+1.04e6/math.expm1(32414/tr)+1.51e7/math.expm1(32781/tr))
 tau=4.277e-14*nh/HH*xhei;tauc=gg*tau/(4*math.pi**2)/eta;enh=math.sqrt(1+math.pi**2*tauc)+7.74*tauc/(1+70*tauc)
 pesc=enh/tau+(1-math.exp(-1.023e-7*tau))*(.964525*math.exp(2947/tr)-enh*math.exp(-6.14e13/eta))/tau
 a=50.94*y2s;b=1.7989e9*y2p*pesc;f=(xhei*s-e*xe)/HH
 r=np.array([a*f,b*f]);return r
def h_split(y,e,red,HH):
 x=1-y;xe=x+e;T=tm_steady_K(cos,xe,red,HH);Tr=cos.T0_K*(1+red);t=KB_NATIVE_EV_K*Tr;n=cos.nH0_m3*(1+red)**3*1e-6
 rt=source.table.evaluate(radiation_temperature_eV_rescaled=t,matter_to_radiation_temperature_ratio=T/Tr)
 al=rt.alpha_m3_s*1e6;da=rt.delta_alpha_m3_s*1e6;bS,bP=rt.beta_s_inv;R=rt.R_2p2s_s_inv;L=LAMBDA_2S1S_S_INV;ly=LYA_FACT_CM3*HH/(n*y)
 S=SAHA_COEFFICIENT_CGS*t*np.sqrt(t)*np.exp(-IONIZATION_ENERGY_EV/t)/n
 src=n*(S*y*da+al*(xe*x-S*y))
 det=(bS+L)*(bP+ly)+R*(bS+L+3*bP+3*ly)
 r=np.array([L*((bP+R+ly)*src[0]+R*src[1]),ly*(3*R*src[0]+(bS+3*R+L)*src[1])])/det/HH
 rhs=source.hydrogen_rhs_ln_a(z=red,x_HII=x,x_e=xe,Tm_K=T)
 return r,rhs
def deposit(grid,E,w):
 k=np.searchsorted(grid,E)-1;assert min(k)>=0 and max(k)<len(grid)-1
 f=(E-grid[k])/(grid[k+1]-grid[k]);out=np.zeros(len(grid));np.add.at(out,k,w*(1-f));np.add.at(out,k+1,w*f);return out
rows=[];arrays={}
for n,bins in [(128,512),(256,1024),(512,2048)]:
 u=np.linspace(u0,u1,n+1);oldgrid=z[f'E_{bins}'];old=z[f'N_{bins}'];grid=np.geomspace(min(oldgrid[0],np.exp(u0)*min(eh.min(),(Eh-eh).min(),Ehe*x.min()))*.98,max(oldgrid[-1],np.exp(u1)*Ehe)*1.02,bins*2)
 initial=deposit(grid,oldgrid,old);assert abs(initial.sum()-old.sum())<1e-15 and abs(initial@grid-old@oldgrid)<1e-16
 N=initial.copy();stock0=np.array([z[f'ybase_{bins}'][-1],he0]);stock= np.array([z[f'y_{bins}'][-1],he0]);base=stock0.copy();hist=[stock.copy()];hb=[base.copy()]
 em=absn=emK=absK=heat=0.;hes=np.zeros(2);hs=np.zeros(2);hsbase=np.zeros(2);HN=np.zeros_like(grid);spliterr=0.;rooterr=0.;t0=time.monotonic()
 for l,r in zip(u[:-1],u[1:]):
  dt=r-l;mid=(l+r)/2;am=np.exp(mid);red=np.expm1(-r);HH=cos.hubble_s(red)
  def tau(ul,ur):
   end=np.maximum(ul,np.minimum(ur,np.log(grid/thr)));d=end-ul;mi=(ul+end)/2;tau=np.zeros_like(grid)
   for sign in [-1,1]:
    t=mi+sign*d/(2*np.sqrt(3));a=np.exp(t);tau+=clight*cos.nH0_m3/a**3/np.array([cos.hubble_s(float(v)) for v in np.expm1(-t)])*sigma(grid/a)*d/2
   return tau,grid/np.exp(mi)
  K1,E1=tau(l,mid);K2,E2=tau(mid,r)
  shape=deposit(grid,am*Ehe*x,2*w)
  def eval_state(old,y,fresh):
   e=brentq(lambda v:v-old[1]-dt*helium_rhs(cos,y,v,HH,red),0.,cos.fHe*(1-1e-12),xtol=1e-18,rtol=1e-14)
   hhe=he_split(y,e,red,HH);h,rhs=h_split(y,e,red,HH);birth=-dt*hhe[0]*shape if fresh else np.zeros_like(N)
   L1=N*(-np.expm1(-K1*y)) if fresh else np.zeros_like(N);T=N-L1+birth;L2=T*(-np.expm1(-K2*y)) if fresh else np.zeros_like(N)
   res=y-old[0]+dt*rhs+(L1+L2).sum()
   return res,e,hhe,h,birth,L1,L2,T-L2
  def solve(old,fresh):
   lo=1e-9;hi=min(.5,max(.05,2*old[0]+.01));f=lambda y:eval_state(old,y,fresh)[0]
   while f(lo)*f(hi)>0 and hi<.5:hi=min(.5,2*hi)
   y=brentq(f,lo,hi,xtol=1e-16,rtol=1e-14);return y,eval_state(old,y,fresh)
  y,b0=solve(base,False);base=np.array([y,b0[1]])
  y,b1=solve(stock,True);res,e,hhe,hh,birth,L1,L2,N=b1;stock=np.array([y,e])
  rooterr=max(rooterr,abs(res),abs(b0[0]));spliterr=max(spliterr,abs(hhe.sum()-helium_rhs(cos,y,e,HH,red)),abs(hh.sum()+h_split(y,e,red,HH)[1]))
  hes-=dt*hhe;hs+=dt*hh;hsbase+=dt*b0[3];em+=float(birth.sum());emK+=float(birth@grid);absn+=float((L1+L2).sum());absK+=float((L1+L2)@grid);heat+=float(L1@np.maximum(E1-thr,0)+L2@np.maximum(E2-thr,0))
  # H net 2s and Ly-alpha spectral output is a diagnostic, not fed back into the effective atom.
  HN+=deposit(grid,am*np.r_[eh,Eh-eh,Eh],dt*np.r_[hh[0]*wh,hh[0]*wh,hh[1]])
  hist.append(stock.copy());hb.append(base.copy())
 hist=np.array(hist);hb=np.array(hb);dy=hist-hb;nd=float(initial.sum()+em-absn-N.sum());ed=float(initial@grid+emK-absK-N@grid)
 hcount=float(HN.sum()-(2*hs[0]+hs[1]));hclosure=float(hs.sum()-(stock[0]-hist[0,0]+absn))
 assert abs(nd)<1e-12 and abs(ed)<1e-14 and abs(hcount)<1e-12 and abs(hclosure)<1e-10 and spliterr<1e-8
 row=dict(steps=n,bins=len(grid),fresh_He_events=hes.tolist(),HeII_stock_decrease=float(he0-stock[1]),fresh_He_2s_photons=em,HI_absorptions=absn,HI_heat_eV_per_H=heat,max_HI_change=float(max(abs(dy[:,0]))),max_HeII_change=float(max(abs(dy[:,1]))),max_xe_change=float(max(abs(-dy[:,0]+dy[:,1]))),final_xe_change=float(-dy[-1,0]+dy[-1,1]),H_net_events_2s_lya=hs.tolist(),H_baseline_events_2s_lya=hsbase.tolist(),H_extra_events=(hs-hsbase).tolist(),H_photon_count=float(HN.sum()),H_count_defect=hcount,H_rate_stock_defect=hclosure,max_split_error=spliterr,max_root_residual=rooterr,number_defect=nd,comoving_energy_defect=ed,seconds=time.monotonic()-t0)
 rows.append(row);arrays[f'u_{n}']=u;arrays[f'gas_{n}']=hist;arrays[f'base_{n}']=hb;arrays[f'q_{n}']=grid;arrays[f'He_N_{n}']=N;arrays[f'H_N_{n}']=HN;print(row,flush=True)
np.savez_compressed(D/'FRESH_HEI.npz',**arrays)
(D/'FRESH_HEI.json').write_text(json.dumps(dict(rows=rows,input_sha=hashlib.sha256(p.read_bytes()).hexdigest(),H_2s_table=tab.source_hashes.copy(),scope='fresh HeI net 2s source from actual helium RHS split, H continuum absorption in HMLA-valid window and coupled H/He ionization; H 2s/Ly-alpha net emissivity from effective 2-level Schur solve and original spontaneous 2s shape diagnostic; no H excited-state feedback, thermal feedback or new He 2p double counting'),indent=2)+'\n')
