"""Continue actual surviving HeI net photons into original HMLA-valid temperature domain.
Coupled HMLA H, source HeII, and HI continuum opacity; thermal steady closure, no new photons."""
from pathlib import Path
import sys,json,hashlib,numpy as np,time
from scipy.constants import c as clight
from scipy.optimize import brentq
D=Path(__file__).resolve().parent;P=D.parent;I=P/'r118c4i_weak_adjoint';H=P/'r118c4h_goal_adjoint'
sys.path.insert(0,str(D.parents[1]/'src'));sys.path.insert(0,str(P/'r118c3w_common_history'))
from common_base import context
from full_bianchi_hyrec.trajectory.primordial_2012_helium import HyRec2012Cosmology,integrate_helium_stages,helium_rhs,tm_steady_K
from full_bianchi_hyrec.trajectory.primordial_2012_full_start import make_hmla_source
from full_bianchi_hyrec.trajectory.hmla_flrw import KB_NATIVE_EV_K
g={'__file__':str(H/'helium.py'),'__name__':'prior'};exec(compile((H/'helium.py').read_text(),str(H/'helium.py'),'exec'),g);sigma=g['sigma']
cos=HyRec2012Cosmology();he=integrate_helium_stages(cos);c=context(128);source=make_hmla_source(cos,c.model.table)
p=I/'HI_FEEDBACK.npz';z=np.load(p);u0=float(z['u'][-1]);u1=-np.log(1501.);z0=np.expm1(-u0);assert abs(he.z[-1]-z0)<1e-9
he0=float(he.xHeII[-1]);assert he0>0
assert KB_NATIVE_EV_K*cos.T0_K*np.exp(-u0)<=.4
thr=13.598434599702;rows=[];arr={}
def run(n,bins):
 u=np.linspace(u0,u1,n+1);q=z[f'E_{bins}'];N=z[f'N_{bins}'].copy();N0=N.copy();y0=np.array([z[f'ybase_{bins}'][-1],he0]);y1=np.array([z[f'y_{bins}'][-1],he0]);Y0=[y0.copy()];Y1=[y1.copy()];absorbed=heat=abs_com=0.;maxres=0.;minp=1.;tm0=time.monotonic()
 for l,r in zip(u[:-1],u[1:]):
  dt=r-l;red=np.expm1(-r);HH=cos.hubble_s(red)
  end=np.maximum(l,np.minimum(r,np.log(q/thr)));dur=end-l;mid=(l+end)/2;K=np.zeros_like(q)
  for sign in [-1,1]:
   t=mid+sign*dur/(2*np.sqrt(3));a=np.exp(t);K+=clight*cos.nH0_m3/a**3/np.array([cos.hubble_s(float(v)) for v in np.expm1(-t)])*sigma(q/a)*dur/2
  def loss(y):return N*(-np.expm1(-K*y))
  def solve(old,photons):
   def hsolve(y):
    return brentq(lambda e:e-old[1]-dt*helium_rhs(cos,y,e,HH,red),0.,cos.fHe*(1-1e-12),xtol=1e-18,rtol=1e-14)
   def residual(y):
    e=hsolve(y);x=1-y;xe=x+e;T=tm_steady_K(cos,xe,red,HH);dx=source.hydrogen_rhs_ln_a(z=red,x_HII=x,x_e=xe,Tm_K=T)
    return y-old[0]+dt*dx+(float(loss(y).sum()) if photons else 0.)
   yy=brentq(residual,1e-9,1-1e-9,xtol=1e-16,rtol=1e-14);ee=hsolve(yy);return np.array([yy,ee]),max(abs(residual(yy)),abs(ee-old[1]-dt*helium_rhs(cos,yy,ee,HH,red)))
  y0,e0=solve(y0,False);y1,e1=solve(y1,True);L=loss(y1[0]);N-=L
  absorbed+=float(L.sum());heat+=float(L@np.maximum(q/np.exp(mid)-thr,0));abs_com+=float(L@q);maxres=max(maxres,e0,e1);minp=min(minp,*y0,*y1);Y0.append(y0.copy());Y1.append(y1.copy())
 Y0=np.array(Y0);Y1=np.array(Y1);diff=Y1-Y0;nd=float(N0.sum()-N.sum()-absorbed);ed=float(N0@q-N@q-abs_com);assert abs(nd)<1e-12 and abs(ed)<1e-14 and minp>0 and maxres<1e-9
 row=dict(steps=n,bins=bins,z_start=float(z0),z_end=1500.,initial_HeII_per_H=he0,initial_HI_difference=float(diff[0,0]),final_HI_difference=float(diff[-1,0]),final_HeII_difference=float(diff[-1,1]),max_HI_difference=float(max(abs(diff[:,0]))),max_HeII_difference=float(max(abs(diff[:,1]))),max_electron_difference=float(max(abs(-diff[:,0]+diff[:,1]))),final_base=Y0[-1].tolist(),final_feedback=Y1[-1].tolist(),absorbed_per_H=absorbed,heat_eV_per_H=heat,initial_net_photons=float(N0.sum()),final_net_photons=float(N.sum()),number_defect=nd,comoving_energy_defect=ed,root_residual=maxres,seconds=time.monotonic()-tm0)
 arr[f'u_{n}_{bins}']=u;arr[f'base_{n}_{bins}']=Y0;arr[f'fed_{n}_{bins}']=Y1;arr[f'final_N_{n}_{bins}']=N;print(row,flush=True);return row
for n,bins in [(128,512),(256,512),(256,1024),(256,2048),(512,2048)]:rows.append(run(n,bins))
np.savez_compressed(D/'HMLA_CONTINUATION.npz',**arr)
(D/'HMLA_CONTINUATION.json').write_text(json.dumps(dict(rows=rows,input_sha=hashlib.sha256(p.read_bytes()).hexdigest(),scope='actual surviving C4I HeI two-photon net spectrum, source HMLA excited-level effective kinetics and helium_rhs, coupled neutral HI absorption through z=1500, Tm steady bath closure; no new He emissions, photon recycling, or heat feedback; no complete HyRec FULL model'),indent=2)+'\n')
