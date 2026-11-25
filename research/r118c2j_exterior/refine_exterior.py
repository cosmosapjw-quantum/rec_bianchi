"""Independent positive hat lift of same physical six blocks.
Direct continuum source evaluated on the same quadrature. Compare exact
sampled nodal activity and projected thermal-hat activity separately.
This is a refinement diagnostic, not yet a dynamic companion owner swap.
"""
import argparse,json,time,hashlib
from pathlib import Path
import numpy as np
from scipy.constants import h,k,c,e
from numpy.polynomial.legendre import leggauss
from full_bianchi_hyrec.standalone_line import prepare
from full_bianchi_hyrec.trajectory.atomic_dynamic_companion import DynamicTwoS
from full_bianchi_hyrec.trajectory.atomic_physical_exterior import physical_blocks
from full_bianchi_hyrec.recoil.calibrated_source import Bath,PCC,EX,angular,uv_nodes,density
p=argparse.ArgumentParser();p.add_argument('--compiled',type=Path,required=True);p.add_argument('--rates',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
a.out.mkdir(exist_ok=False);rows=[]
levels=(4,8,16,32,64,128)
def project_nodes(edges,T,Tr):
 u,w=leggauss(24);u=(1+u)/2;w=w/2
 g=np.zeros(len(edges));mass=np.zeros_like(g);zmean=np.zeros_like(g);xs=[[] for _ in g];ws=[[] for _ in g]
 for i,(lo,hi) in enumerate(zip(edges[:-1],edges[1:])):
  x=lo+(hi-lo)*u;nu=PCC.nu_abs+PCC.dnu*x;wt=(hi-lo)*w*nu**2
  for j,b in [(i,1-u),(i+1,u)]:
   xs[j].extend(x);ws[j].extend(wt*b)
 z=np.exp(-h*PCC.dnu*edges/(k*T));f=np.zeros(len(edges))
 for j,(x,wt) in enumerate(zip(xs,ws)):
  x=np.array(x);wt=np.array(wt);wt/=wt.sum()
  zz=np.exp(-h*PCC.dnu*x/(k*T));target=wt@(1/np.expm1(h*(PCC.nu_abs+PCC.dnu*x)/(k*Tr)))
  alpha=target/(wt@zz)/(1+target)
  for _ in range(8):
   v=alpha*zz;alpha-=(wt@(v/(1-v))-target)/(wt@(zz/(1-v)**2))
  v=alpha*z[j];f[j]=v/(1-v)
 return f
def lift(nt,ns,D,a,b,n):
 xa=(nt-PCC.nu_abs)/PCC.dnu;xb=(ns-PCC.nu_abs)/PCC.dnu
 t=n*(xa-a[0])/(a[1]-a[0]);s=n*(xb-b[0])/(b[1]-b[0])
 i=np.minimum(t.astype(int),n-1);j=np.minimum(s.astype(int),n-1);t-=i;s-=j
 if min(t.min(),s.min())<0 or max(t.max(),s.max())>1:raise ValueError('hat support')
 idx=i*(n+1)+j;K=np.zeros((n+1)**2)
 for off,w in [(0,(1-t)*(1-s)),(1,(1-t)*s),(n+1,t*(1-s)),(n+2,t*s)]:K+=np.bincount(idx+off,weights=D*w,minlength=len(K))
 return K.reshape(n+1,n+1)
for bathname in ('z1100','z1300','z900'):
 with np.load(a.compiled/(bathname+'.npz')) as data:q=prepare(dict(data),4)
 net=DynamicTwoS(a.rates,q);bath=Bath(q['T'],q['n1s'])
 for lane in ('production','reference'):
  par=EX.LANES[lane];mu,wmu=angular(par);Ks={n:[] for n in levels};direct=np.zeros(2);mass=0.;max_marg=0.
  t0=time.monotonic()
  for typ,I,J,b1,b2 in physical_blocks(net):
   nt,ns,ww=uv_nodes(b1,b2,par,.08);xt=(nt-PCC.nu_abs)/PCC.dnu;xs=(ns-PCC.nu_abs)/PCC.dnu
   DD=np.zeros_like(ww)
   for j in range(0,len(mu),8):
    m=mu[j:j+8,None];D=density(nt[None,:],ns[None,:],m,bath)*(wmu[j:j+8,None]*.75*(1+m*m))*ww[None,:]*(8*np.pi*PCC.dnu/c**3/bath.z0)
    DD+=D.sum(axis=0)
   mass+=DD.sum()
   for j,sg in enumerate((1.,-1.)):
    Tr=q['T']*(1+sg*.001);ft=1/np.expm1(h*nt/(k*Tr));fs=1/np.expm1(h*ns/(k*Tr))
    at=np.exp(-h*nt/(k*Tr)+h*(nt-PCC.nu_abs)/(k*q['T']))
    az=np.exp(-h*ns/(k*Tr)+h*(ns-PCC.nu_abs)/(k*q['T']))
    direct[j]+=np.sum(DD*(1+ft)*(1+fs)*(az-at)*(xt-xs))
   for n in levels:
    K=lift(nt,ns,DD,b1,b2,n);x=np.linspace(*b1,n+1);y=np.linspace(*b2,n+1)
    marg=max(abs(K.sum()-DD.sum()),abs(K.sum(axis=1)@x-DD@xt),abs(K.sum(axis=0)@y-DD@xs))/DD.sum()
    max_marg=max(max_marg,float(marg));assert np.min(K)>=0 and marg<1e-10
    Ks[n].append((K,x,y))
  for n in levels:
   val=np.zeros((2,2))
   for K,x,y in Ks[n]:
    zt=np.exp(-h*PCC.dnu*x/(k*q['T']));zs=np.exp(-h*PCC.dnu*y/(k*q['T']))
    for j,sg in enumerate((1.,-1.)):
     Tr=q['T']*(1+sg*.001)
     for v,projection in enumerate((False,True)):
      if projection:ft=project_nodes(x,q['T'],Tr);fs=project_nodes(y,q['T'],Tr)
      else:ft=1/np.expm1(h*(PCC.nu_abs+PCC.dnu*x)/(k*Tr));fs=1/np.expm1(h*(PCC.nu_abs+PCC.dnu*y)/(k*Tr))
      at=ft/(zt*(1+ft));az=fs/(zs*(1+fs))
      val[j,v]+=np.sum(K*(1+ft[:,None])*(1+fs[None,:])*(az[None,:]-at[:,None])*(x[:,None]-y[None,:]))
   row=dict(bath=bathname,lane=lane,subcells=n,conductance=mass,direct=direct.tolist(),sampled=val[:,0].tolist(),projected=val[:,1].tolist(),sampled_error=float(np.max(abs(val[:,0]/direct-1))),projected_error=float(np.max(abs(val[:,1]/direct-1))),max_marginal=max_marg)
   rows.append(row);print(row,flush=True)
  (a.out/'REFINEMENT.json').write_text(json.dumps(rows,indent=2,allow_nan=False)+'\n')
  print('elapsed',bathname,lane,time.monotonic()-t0,flush=True)
