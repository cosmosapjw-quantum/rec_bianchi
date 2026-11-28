"""Nonlinear H/He abundance feedback with paired spectral correction in native effective atom."""
from pathlib import Path
import numpy as np,json,time,hashlib
D=Path(__file__).resolve().parent;K=D.parent/'r118c4m_analytic_history'
src=(K/'instrumented_depletion.py').read_text()
a=src.index('rows=[];arrays={}')
g={'__file__':str(K/'instrumented_depletion.py'),'__name__':'prior'}
exec(compile(src[:a],str(K/'instrumented_depletion.py'),'exec'),g)
globals().update({k:v for k,v in g.items() if k not in ['__file__','__name__','D','K']})
ref=np.load(K/'DEPLETION.npz');rows=[];arrays={}
for n,bins in [(128,512),(256,1024),(512,2048)]:
 u=ref[f'u_{n}'];grid=ref[f'q_{n}'];oldgrid=z[f'E_{bins}'];old=z[f'N_{bins}'];initial=deposit(grid,oldgrid,old);assert abs(initial.sum()-old.sum())<1e-15 and abs(initial@grid-old@oldgrid)<1e-16
 N=initial.copy();HN=np.zeros_like(grid);corr=HN.copy();stock=ref[f'gas_{n}'][0].copy();hist=[stock.copy()];base=ref[f'gas_{n}'];integ=np.zeros(5);em=ab=emK=abK=heat=0.;Hemit=np.zeros(2);Henergy=0.;maxroot=0.;itmax=0;minmargin=1.;max_pairres=0.;max_q=0.;max_subthreshold=0.;max_he_res=0.;max_ledger=0.;t0=time.monotonic()
 for i,(l,r) in enumerate(zip(u[:-1],u[1:]),1):
  dt=r-l;mid=(l+r)/2;am=np.exp(mid);red=np.expm1(-r);HH=cos.hubble_s(red)
  def tau(ul,ur):
   end=np.maximum(ul,np.minimum(ur,np.log(grid/thr)));d=end-ul;mi=(ul+end)/2;tau=np.zeros_like(grid)
   for sign in [-1,1]:
    t=mi+sign*d/(2*np.sqrt(3));a=np.exp(t);tau+=clight*cos.nH0_m3/a**3/np.array([cos.hubble_s(float(v)) for v in np.expm1(-t)])*sigma(grid/a)*d/2
   return tau,grid/np.exp(mi)
  K1,E1=tau(l,mid);K2,E2=tau(mid,r);shape=deposit(grid,am*Ehe*x,2*w)
  def evaluate(y):
   e=brentq(lambda v:v-stock[1]-dt*helium_rhs(cos,y,v,HH,red),0.,cos.fHe*(1-1e-12),xtol=1e-18,rtol=1e-14)
   hh,rhs=h_split(y,e,red,HH);hhe=he_split(y,e,red,HH);birth=-dt*hhe[0]*shape
   L1=N*(-np.expm1(-K1*y));tmp=N-L1+birth;L2=tmp*(-np.expm1(-K2*y));newN=tmp-L2
   Hbirth=deposit(grid,am*np.r_[eh,Eh-eh,Eh],dt*np.r_[hh[0]*wh,hh[0]*wh,hh[1]])
   newHN=HN+Hbirth
   nc,dg,its,res,margin=depletion_step(y,e,red,HH,hh,grid,newN+newHN,corr,dt)
   residual=y-stock[0]+dt*rhs+(L1+L2).sum()+dt*dg[2]
   return residual,e,hh,hhe,birth,L1,L2,newN,newHN,nc,dg,its,res,margin,Hbirth
  y0=base[i,0];width=max(1e-6,8*abs(stock[0]-base[i-1,0]),2e-5)
  lo=max(1e-10,y0-width);hi=min(.5,y0+width)
  for _ in range(6):
   if evaluate(lo)[0]*evaluate(hi)[0]<=0:break
   width*=2;lo=max(1e-10,y0-width);hi=min(.5,y0+width)
  else:raise ValueError('nonlinear feedback root bracket')
  y=brentq(lambda y:evaluate(y)[0],lo,hi,xtol=1e-16,rtol=1e-14);rr,e,hh,hhe,birth,L1,L2,N,HN,corr,dg,its,res,margin,Hbirth=evaluate(y)
  maxroot=max(maxroot,abs(rr));itmax=max(itmax,its);minmargin=min(minmargin,margin);max_pairres=max(max_pairres,res)
  max_he_res=max(max_he_res,abs(e-stock[1]-dt*helium_rhs(cos,y,e,HH,red)));stock=np.array([y,e]);hist.append(stock.copy())
  # All newly emitted H and correction photons must stay below continuum threshold.
  above=grid>=thr*np.exp(l);leak=float(np.sum(abs(HN[above]))+np.sum(abs(corr[above])));max_subthreshold=max(max_subthreshold,leak);assert leak<1e-24
  integ+=dt*dg[:5];em+=float(birth.sum());emK+=float(birth@grid);ab+=float((L1+L2).sum());abK+=float((L1+L2)@grid);heat+=float(L1@np.maximum(E1-thr,0)+L2@np.maximum(E2-thr,0));Hemit+=dt*hh;Henergy+=float(Hbirth@grid)
  max_ledger=max(max_ledger,abs(float(corr.sum()-integ[3])),abs(float(corr@grid-integ[4])))
 hist=np.array(hist);nd=float(initial.sum()+em-ab+2*Hemit[0]+Hemit[1]+integ[3]-(N+HN+corr).sum())
 ed=float(initial@grid+emK-abK+Henergy+integ[4]-(N+HN+corr)@grid)
 hc=float(Hemit.sum()-(hist[-1,0]-hist[0,0]+ab+integ[2]));refd=ref[f'depl_gas_{n}'][:,2,0]
 delta=base[:,0]-hist[:,0];assert len(refd)==len(delta)-1
 assert abs(nd)<1e-12 and abs(ed)<1e-14 and abs(hc)<1e-10 and maxroot<1e-14
 row=dict(steps=n,bins=len(grid),paired_integral=float(integ[2]),max_xHII_change=float(max(abs(delta))),terminal_xHII_change=float(delta[-1]),C4M_linear_max_x=float(max(abs(refd))),max_gap_to_C4M_linear=float(max(abs(delta[1:]-refd))),helium_change=float(hist[-1,1]-base[-1,1]),HI_absorption=ab,HI_heat_eV_H=heat,H_emission_events=Hemit.tolist(),max_root_residual=maxroot,max_He_residual=max_he_res,min_occupation_ratio=minmargin,max_fixed_point= max_pairres,max_iterations=itmax,number_ledger=nd,comoving_energy_ledger=ed,H_abundance_ledger=hc,max_correction_ledger=max_ledger,above_HI_stock_max=max_subthreshold,seconds=time.monotonic()-t0)
 rows.append(row);arrays[f'u_{n}']=u;arrays[f'gas_{n}']=hist;arrays[f'base_{n}']=base;arrays[f'correction_{n}']=corr;arrays[f'N_{n}']=N;arrays[f'HN_{n}']=HN;arrays[f'q_{n}']=grid;print(row,flush=True)
np.savez_compressed(D/'COUPLED_FEEDBACK.npz',**arrays)
(D/'COUPLED_FEEDBACK.json').write_text(json.dumps(dict(rows=rows,source_sha=hashlib.sha256((K/'instrumented_depletion.py').read_bytes()).hexdigest(),reference_sha=hashlib.sha256((K/'DEPLETION.npz').read_bytes()).hexdigest(),scope='Nonlinear coupled H/He effective abundance, original HI absorption/He and H emission recomputed in root, implicit paired spectral correction. Fixed cosmology, steady temperature and approximate effective HMLA Schur populations, no Ly-alpha transfer/full HyRec. H photons below HI threshold checked.'),indent=2,allow_nan=False)+'\n')
