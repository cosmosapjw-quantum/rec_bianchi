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

from scipy.constants import hbar, e as qe
HBARC=hbar*clight/qe
def stock_occupation(grid,N,energies,a):
    # Convert nodal number/H to a piecewise-interpolated number density in comoving energy.
    # Cell edges are geometric means; number and comoving energies are in eV.
    edges=np.r_[grid[0]**2/np.sqrt(grid[0]*grid[1]),np.sqrt(grid[:-1]*grid[1:]),grid[-1]**2/np.sqrt(grid[-2]*grid[-1])]
    occ=np.pi**2*HBARC**3*cos.nH0_m3*N/(grid**2*np.diff(edges))
    return np.interp(a*energies,grid,occ,left=0.,right=0.)
def inverse_source(y,e,red,HH,hh,grid,HeN,HN):
    a=1/(1+red);x=1-y;xe=x+e;Tr=cos.T0_K*(1+red);T=tm_steady_K(cos,xe,red,HH);t=KB_NATIVE_EV_K*Tr
    L=LAMBDA_2S1S_S_INV;upper=y*np.exp(-Eh/t)+HH*hh[0]/L
    assert upper>=0
    fc=1/np.expm1((Eh-eh)/t);ft=1/np.expm1(eh/t)
    rates=L*wh
    def action(N):
        dc=stock_occupation(grid,N,Eh-eh,a);dt=stock_occupation(grid,N,eh,a)
        assert np.all(fc+dc>=0) and np.all(ft+dt>=0)
        stim=rates*upper*((1+fc)*dt+(1+ft)*dc+dc*dt)
        inv=rates*y*(fc*dt+ft*dc+dc*dt)
        # incremental emission events, relative to exact same frozen-population Planck bath
        return float(stim.sum()),float(inv.sum()),max(float(np.max(abs(dc)/fc)),float(np.max(abs(dt)/ft)))
    sh,ih,rh=action(HN);se,ie,re=action(HeN);sb,ib,rb=action(HN+HeN);G=sb-ib
    # Linear real-level response of the HMLA atom to the extra two-photon net action.
    rt=source.table.evaluate(radiation_temperature_eV_rescaled=t,matter_to_radiation_temperature_ratio=T/Tr)
    bs,bp=rt.beta_s_inv;R=rt.R_2p2s_s_inv;ly=LYA_FACT_CM3*HH/(cos.nH0_m3*(1+red)**3*1e-6*y)
    A=np.array([[bs+L+3*R,-R],[-3*R,bp+ly+R]])
    dx=np.linalg.solve(A,[-G,0.])
    g=(bs*dx[0]+bp*dx[1])/HH
    check=abs(g+(G+L*dx[0]+ly*dx[1])/HH)
    assert check<1e-10*max(abs(g),1e-50)+1e-30
    # Independent detailed-balance test with Planck and Boltzmann populations.
    eq=y*np.exp(-Eh/t);err=float(np.max(abs(eq*(1+fc)*(1+ft)-y*fc*ft))/max(np.max(y*fc*ft),1e-300))
    assert err<1e-12
    return np.array([sh,ih,se,ie,sb,ib,g,rb,err,check])
def thermal_chem(y,e,red,HH,h,Q,inv,old,Cprev):
    x=1-y;xe=x+e;Tr=cos.T0_K*(1+red);T=tm_steady_K(cos,xe,red,HH);cap=1.5*KB_NATIVE_EV_K*(1+cos.fHe+xe)
    gamma=cos.fsR**2/cos.meR**3*4.91466895548409e-22;sc=gamma*Tr**4/HH;B=sc*xe/(1+cos.fHe+xe);Bx=sc*(1+cos.fHe)/(1+cos.fHe+xe)**2
    fun=lambda x,T:source.hydrogen_rhs_ln_a(z=red,x_HII=x,x_e=x+e,Tm_K=T)
    ex=1e-6;et=.001
    fx=(fun(x+ex,T)-fun(x-ex,T))/(2*ex);ft=(fun(x,T+et)-fun(x,T-et))/(2*et)
    M=np.array([[fx,ft],[Bx*(Tr-T),-2-B]])
    rhs=np.array([[0.,Q/cap],[h*inv,0.],[h*inv,Q/cap]])
    out=np.linalg.solve(np.eye(2)-h*M,(old+rhs).T).T
    # exact discrete heat ledger in the conditional linear temperature equation.
    capwork=(cap-Cprev)*old[:,1];source_heat=rhs[:,1]*cap;mix=h*cap*Bx*(Tr-T)*out[:,0];ad=h*cap*2*out[:,1];com=h*cap*B*out[:,1]
    balance=cap*out[:,1]-Cprev*old[:,1]-capwork-source_heat-mix+ad+com
    assert np.max(abs(balance))<1e-18
    return out,cap,np.stack([source_heat,mix,ad,com,capwork,balance],axis=1)

rows=[];arrays={}
for n,bins in [(128,512),(256,1024),(512,2048)]:
 u=np.linspace(u0,u1,n+1);oldgrid=z[f'E_{bins}'];old=z[f'N_{bins}'];grid=np.geomspace(min(oldgrid[0],np.exp(u0)*min(eh.min(),(Eh-eh).min(),Ehe*x.min()))*.98,max(oldgrid[-1],np.exp(u1)*Ehe)*1.02,bins*2)
 initial=deposit(grid,oldgrid,old);assert abs(initial.sum()-old.sum())<1e-15 and abs(initial@grid-old@oldgrid)<1e-16
 N=initial.copy();stock0=np.array([z[f'ybase_{bins}'][-1],he0]);stock= np.array([z[f'y_{bins}'][-1],he0]);base=stock0.copy();hist=[stock.copy()];hb=[base.copy()]
 delta=np.zeros((3,2));dhist=[delta.copy()];ledger=np.zeros((3,6));inv_hist=[];heat_hist=[];cap0=1.5*KB_NATIVE_EV_K*(1+cos.fHe+1-stock[0]+stock[1]);cap=cap0;em=absn=emK=absK=heat=0.;hes=np.zeros(2);hs=np.zeros(2);hsbase=np.zeros(2);HN=np.zeros_like(grid);spliterr=0.;rooterr=0.;t0=time.monotonic()
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
  Q=float(L1@np.maximum(E1-thr,0)+L2@np.maximum(E2-thr,0))
  inv=inverse_source(y,e,red,HH,hh,grid,N,HN)
  delta,cap,bal=thermal_chem(y,e,red,HH,dt,Q,inv[6],delta,cap);ledger+=bal;dhist.append(delta.copy());inv_hist.append(inv);heat_hist.append(Q)
  hist.append(stock.copy());hb.append(base.copy())
 hist=np.array(hist);hb=np.array(hb);dy=hist-hb;nd=float(initial.sum()+em-absn-N.sum());ed=float(initial@grid+emK-absK-N@grid)
 hcount=float(HN.sum()-(2*hs[0]+hs[1]));hclosure=float(hs.sum()-(stock[0]-hist[0,0]+absn))
 assert abs(nd)<1e-12 and abs(ed)<1e-14 and abs(hcount)<1e-12 and abs(hclosure)<1e-10 and spliterr<1e-8
 row=dict(steps=n,bins=len(grid),fresh_He_events=hes.tolist(),HeII_stock_decrease=float(he0-stock[1]),fresh_He_2s_photons=em,HI_absorptions=absn,HI_heat_eV_per_H=heat,max_HI_change=float(max(abs(dy[:,0]))),max_HeII_change=float(max(abs(dy[:,1]))),max_xe_change=float(max(abs(-dy[:,0]+dy[:,1]))),final_xe_change=float(-dy[-1,0]+dy[-1,1]),H_net_events_2s_lya=hs.tolist(),H_baseline_events_2s_lya=hsbase.tolist(),H_extra_events=(hs-hsbase).tolist(),H_photon_count=float(HN.sum()),H_count_defect=hcount,H_rate_stock_defect=hclosure,max_split_error=spliterr,max_root_residual=rooterr,number_defect=nd,comoving_energy_defect=ed,seconds=time.monotonic()-t0)
 inv_hist=np.array(inv_hist);dhist=np.array(dhist);heats=np.array(heat_hist)
 assert abs(heats.sum()-heat)<1e-18 and np.max(abs(dhist[:,0]+dhist[:,1]-dhist[:,2]))<1e-10
 rr=np.expm1(-u[1:]);Hrate=np.array([cos.hubble_s(float(t)) for t in rr]);du=np.diff(u);integrals=(du/Hrate)@inv_hist[:,:6]
 row.update(incremental_two_photon_integrals=integrals.tolist(),inverse_effective_H_source_integral=float(du@inv_hist[:,6]),max_distortion_to_planck=float(max(inv_hist[:,7])),max_detailed_balance_defect=float(max(inv_hist[:,8])),max_schur_identity_defect=float(max(inv_hist[:,9])),linear_heat_only_max_x=float(max(abs(dhist[:,0,0]))),linear_heat_only_max_T_K=float(max(abs(dhist[:,0,1]))),linear_inverse_only_max_x=float(max(abs(dhist[:,1,0]))),linear_inverse_only_max_T_K=float(max(abs(dhist[:,1,1]))),linear_combined_max_x=float(max(abs(dhist[:,2,0]))),linear_combined_max_T_K=float(max(abs(dhist[:,2,1]))),terminal=dhist[-1].tolist(),heat_ledger=ledger.tolist(),energy_stock=(cap*delta[:,1]).tolist())
 arrays[f'linear_{n}']=dhist;arrays[f'inverse_{n}']=inv_hist;arrays[f'heat_{n}']=heats
 rows.append(row);arrays[f'u_{n}']=u;arrays[f'gas_{n}']=hist;arrays[f'base_{n}']=hb;arrays[f'q_{n}']=grid;arrays[f'He_N_{n}']=N;arrays[f'H_N_{n}']=HN;print(row,flush=True)
np.savez_compressed(D/'THERMAL_FEEDBACK.npz',**arrays)
(D/'THERMAL_FEEDBACK.json').write_text(json.dumps(dict(rows=rows,input_sha=hashlib.sha256(p.read_bytes()).hexdigest(),H_2s_table=tab.source_hashes.copy(),scope='C4K source replay plus prescribed-stock incremental two-photon forward/reverse detailed balance and Schur response, linearized HMLA gas/Compton temperature correction about prescribed steady thermal reference; no iterative spectral depletion, no excited-state line transfer or full non-linear thermochemistry'),indent=2)+'\n')
