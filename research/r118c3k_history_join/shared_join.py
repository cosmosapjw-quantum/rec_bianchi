"""Causal midpoint atomic solve with integrated piecewise linear source history."""
import numpy as np,json,sys
from pathlib import Path
from dataclasses import replace
from scipy.optimize import brentq
from numpy.polynomial.legendre import leggauss
D=Path(__file__).resolve().parent
sys.path.insert(0,str(D.parent/'r118c3h_paired_history'))
from shared_gas_h import Clock,stf,B,P,R,sha,OriginalHyRecPrimitiveRateTable,_canonical_twophoton_table,KB_NATIVE_EV_K,COMPTON_GAMMA_PER_T4_S_INV_K4,populate_original_full_atomic
from retarded import raymap,interpF,step
from full_bianchi_hyrec.trajectory.causal_virtual_redshift import _source_edges,_planck_difference
from quadratic import gather,average
sys.path.insert(0,str(D.parent/'r118c3j_integrated_history'))
from line_cell import EL,phase,evolve,A21
def run(angular,nm,nt,label,reset,order):
 v=np.load(P);eta=-np.log1p(v['z']);tab=_canonical_twophoton_table(R);orig=np.r_[v['virtual_out'],v['lyman_out']].T
 m=Clock(h=.6735837,omega_cb=.31242079216478097,omega_r_h2=4.1578740068818545e-5,omega_de_h2=.3119234221656212,omega_b_h2=.02242,y_he_mass=.245,tcmb0_K=2.7255,table=OriginalHyRecPrimitiveRateTable.from_archive(R))
 p=B/'plusfine.csv';g=np.genfromtxt(p,names=True,delimiter=',');ge=np.log(g['a']);F=np.stack([g[f'F{i}{j}'] for i in range(3) for j in range(3)],axis=1).reshape(-1,3,3)
 if not angular:F=np.broadcast_to(np.eye(3),F.shape).copy()
 mu,w=leggauss(nm);M,ph=np.meshgrid(mu,2*np.pi*np.arange(2*nm)/(2*nm),indexing='ij');n=np.stack([np.sqrt(1-M*M)*np.cos(ph),np.sqrt(1-M*M)*np.sin(ph),M],axis=-1).reshape(-1,3);w=np.repeat(w/(4*nm),2*nm)
 start=64;finish=128;times=np.linspace(eta[start-1],eta[finish],nt+1);Fref=interpF(ge,F,times[0]);he=np.r_[eta[:start],times[1:]]
 shape=(len(he)-1,len(n),314)
 L=np.zeros(shape);M=np.zeros(shape);RR=np.zeros(shape);area=np.zeros((len(he),len(n),314))
 for j in range(start-1):
  L[j]=orig[j];RR[j]=orig[j+1];M[j]=(L[j]+RR[j])/2
  area[j+1]=area[j]+(he[j+1]-he[j])*(L[j]+4*M[j]+RR[j])/6
 src,ef,es=_source_edges(tab.energy_eV);lr=np.log(es/ef);p0=n@Fref
 def rays(u):
  ff=interpF(ge,F,u);nf=np.linalg.solve(ff.T,p0.T).T;nf/=np.linalg.norm(nf,axis=1)[:,None];pp=nf@ff
  d=np.broadcast_to(lr[None,:],(len(n),len(lr))).copy()
  for _ in range(40):
   t=u-d
   if t.min()<ge[0] or t.max()>ge[-1]:raise ValueError('coframe domain')
   fm=interpF(ge,F,t);vv=np.linalg.solve(np.swapaxes(fm,-1,-2),np.broadcast_to(pp[:,None,:,None],t.shape+(3,1)))[...,0];Rr=np.log(np.linalg.norm(vv,axis=-1));nd=lr[None,:]-Rr
   if np.max(abs(nd-d))<2e-14:d=nd;break
   d=nd
  else:raise ValueError('retarded convergence')
  return u-d,Rr
 def endpoint(u,inc):
  z=np.expm1(-u);H=np.interp(u,ge,g['h'])*2.1842852410855023e-18;Tr=m.tcmb0_K*(1+z)
  S=stf([np.interp(u,ge,g[f'S{k}']) for k in range(5)]) if angular else np.zeros((3,3))
  nf,ww=raymap(interpF(ge,F,u),Fref,n,w);rates=1+np.einsum('ni,ij,nj->n',nf,S,nf);source=replace(m,H=H);_,nh=source.cosmology(z)
  def eval(x,T):
   snap=populate_original_full_atomic(source,z=z,xHII=x,xe=x,Tm_K=T,incoming_virtual=ww@inc[:,:311],incoming_lyman=ww@inc[:,311:])
   return step(snap,rates,inc,ww)
  return source,z,Tr,nh,ww,eval
 def geom(u,rr):return _planck_difference(ef[None,:]/(KB_NATIVE_EV_K*m.tcmb0_K*np.exp(-u)),rr)
 x=float(v['xHII'][63]);T=float(v['T'][63]);tl,rl=rays(times[0]);inc=gather(he[:start],L[:start-1],M[:start-1],RR[:start-1],tl,src)+geom(times[0],rl)
 so,z,Tr,nh,ww,ev=endpoint(times[0],inc);rr,oo,dd=ev(x,T);L[start-1]=oo if reset else orig[start-1];join_max=float(np.max(abs(oo-orig[start-1])))
 rows=[[times[0],x,T,rr.dxHII_dln_a,0,0,0,float(times[0]-tl.max())]];lines=[]
 for i,u in enumerate(times[1:],start):
  l=he[i-1];h=u-l;mid=(l+u)/2;tr,rg=rays(u);tm,rm=rays(mid)
  assert tr.max()<l and tm.max()<l
  avg=average(he[:i],L[:i-1],M[:i-1],RR[:i-1],area[:i],tl,tr,src)+geom(mid,rm)
  so,z,Tr,nh,ww,ev=endpoint(mid,avg)
  def candidate(xx):
   xm=(x+xx)/2;A=COMPTON_GAMMA_PER_T4_S_INV_K4*Tr**4*xm/(1+xm+m.f_he)/so.H
   tt=(T+h*(A*Tr-(2+A)*T/2))/(1+h*(2+A)/2);rr,_,dd=ev(xm,(T+tt)/2)
   return xx-x-h*rr.dxHII_dln_a,tt,rr.dxHII_dln_a
  width=max(1e-6,10*h*abs(rows[-1][3]));xx=brentq(lambda q:candidate(q)[0],max(1e-10,x-width),min(1-1e-10,x+width),xtol=2e-15,rtol=1e-14);res,tt,fmid=candidate(xx)
  incmid=gather(he[:i],L[:i-1],M[:i-1],RR[:i-1],tm,src)+geom(mid,rm)
  _,_,Trmid,_,_,evmid=endpoint(mid,incmid);rmid,om,dm=evmid((x+xx)/2,(T+tt)/2)
  assert rmid.normalized_matrix_residual<1e-10 and dm<1e-8 and min((1/np.expm1(tab.energy_eV/(KB_NATIVE_EV_K*Trmid))+om[:,:311]).ravel())>=0
  inc=gather(he[:i],L[:i-1],M[:i-1],RR[:i-1],tr,src)+geom(u,rg);so,z,Tr,nh,ww,ev=endpoint(u,inc);rr,out,dd=ev(xx,tt)
  full=1/np.expm1(tab.energy_eV/(KB_NATIVE_EV_K*Tr))+out[:,:311]
  assert min(full.ravel())>=0 and abs(res)<1e-12 and rr.normalized_matrix_residual<1e-10 and dd<1e-8 and tt>0
  RR[i-1]=out;M[i-1]=om if order==2 else (L[i-1]+out)/2;area[i]=area[i-1]+h*(L[i-1]+4*M[i-1]+RR[i-1])/6
  if i<len(he)-1:L[i]=out
  # Independent physical line-cell sample, not used in accepted evolution.
  x1=1-xx;bol=np.exp(-EL/(KB_NATIVE_EV_K*Tr));pop=3*x1*bol+rr.real_departures[1];occ=1/np.expm1(EL/(KB_NATIVE_EV_K*Tr))+(ww@inc[:,311])/ww.sum()
  lines.append([u,x1,pop,occ,nh,Tr]);x,T=xx,tt;tl,rl=tr,rg
  rows.append([u,x,T,rr.dxHII_dln_a,fmid,res,rr.normalized_matrix_residual,float(u-tr.max())])
  if (i-start+1)%128==0:print(label,i-start+1,x,flush=True)
 rows=np.array(rows);lines=np.array(lines);np.savez_compressed(D/(label+'.npz'),rows=rows,line=lines,final=RR[-1],rays=n)
 o=dict(status='SCOPED_INTEGRATED_HISTORY_MIDPOINT',angular=angular,rays=len(n),steps=nt,x=x,T=T,max_xres=float(np.max(abs(rows[:,5]))),max_atom_res=float(np.max(rows[:,6])),min_delay=float(rows[:,7].min()),prefix_sha=sha(P),geometry_sha=sha(p),rates_sha=sha(R),reset=reset,order=order,join_max=join_max,scope='piecewise accepted history; physical midpoint and endpoint; explicit one-sided join; H-only')
 (D/(label+'.json')).write_text(json.dumps(o,indent=2)+'\n');print(o,flush=True)
if __name__=='__main__':
 a,n,k,l,j,o=sys.argv[1:];run(bool(int(a)),int(n),int(k),l,bool(int(j)),int(o))
