"""C3I causal shared H-only gas with an exact first-prefix arrival correction."""
import numpy as np,json,hashlib,sys
from pathlib import Path
from dataclasses import replace
from scipy.optimize import brentq
from numpy.polynomial.legendre import leggauss
D=Path(__file__).resolve().parent
sys.path.insert(0,str(D.parent/'r118c3h_paired_history'))
from shared_gas_h import Clock,stf,thermal_endpoint,B,P,R,sha,OriginalHyRecPrimitiveRateTable,_canonical_twophoton_table,KB_NATIVE_EV_K,COMPTON_GAMMA_PER_T4_S_INV_K4,populate_original_full_atomic
from retarded import raymap,interpF,incoming_canonical,step
from full_bianchi_hyrec.trajectory.causal_virtual_redshift import _source_edges
from events import event_times,correction
from line_pair import line_pair
def run(angular,nm,nt,label,correct=True):
 v=np.load(P);eta=-np.log1p(v['z']);tab=_canonical_twophoton_table(R);orig=np.r_[v['virtual_out'],v['lyman_out']].T
 m=Clock(h=.6735837,omega_cb=.31242079216478097,omega_r_h2=4.1578740068818545e-5,omega_de_h2=.3119234221656212,omega_b_h2=.02242,y_he_mass=.245,tcmb0_K=2.7255,table=OriginalHyRecPrimitiveRateTable.from_archive(R))
 p=B/'plusfine.csv';g=np.genfromtxt(p,names=True,delimiter=',');ge=np.log(g['a'])
 F=np.stack([g[f'F{i}{j}'] for i in range(3) for j in range(3)],axis=1).reshape(-1,3,3)
 if not angular:F=np.broadcast_to(np.eye(3),F.shape).copy()
 mu,w=leggauss(nm);M,Phi=np.meshgrid(mu,2*np.pi*np.arange(2*nm)/(2*nm),indexing='ij');n=np.stack([np.sqrt(1-M*M)*np.cos(Phi),np.sqrt(1-M*M)*np.sin(Phi),M],axis=-1).reshape(-1,3);w=np.repeat(w/(4*nm),2*nm)
 start=64;finish=128;times=np.linspace(eta[start-1],eta[finish],nt+1);Fref=interpF(ge,F,times[0]);he=np.r_[eta[:start],times[1:]]
 hist=np.zeros((len(he),len(n),314));hist[:start]=orig[:start,None,:]
 src,ef,es=_source_edges(tab.energy_eV);ev=event_times(ge,F,Fref,n,eta[0],np.log(es/ef),times[0],times[-1])
 def endpoint(u,i):
  zz=np.expm1(-u);H=np.interp(u,ge,g['h'])*2.1842852410855023e-18;Tr=m.tcmb0_K*(1+zz)
  S=stf([np.interp(u,ge,g[f'S{k}']) for k in range(5)]) if angular else np.zeros((3,3))
  nf,ww=raymap(interpF(ge,F,u),Fref,n,w);rates=1+np.einsum('ni,ij,nj->n',nf,S,nf)
  inc,delay=incoming_canonical(ge,F,u,Fref,n,tab.energy_eV,he[:i],hist[:i],Tr,'linear')
  source=replace(m,H=H);_,nh=source.cosmology(zz)
  def evaluate(x,T,shift=None):
   a=inc if shift is None else inc+shift
   snap=populate_original_full_atomic(source,z=zz,xHII=x,xe=x,Tm_K=T,incoming_virtual=ww@a[:,:311],incoming_lyman=ww@a[:,311:])
   r,out,defect=step(snap,rates,a,ww)
   return r,out,defect
  def diag(x,r):return line_pair(1-x,r.real_departures[1],KB_NATIVE_EV_K*Tr,H,nh*1e-6,rates,inc[:,311],ww)
  return source,zz,Tr,delay,evaluate,diag
 x=float(v['xHII'][63]);T=float(v['T'][63])
 source,z,Tr,delay,evaluate,diag=endpoint(times[0],start)
 rr,oo,dd=evaluate(x,T);fprev=rr.dxHII_dln_a;gprev=source.thermal_rhs_ln_a(z,x,T)
 rows=[[times[0],x,T,fprev,gprev,0,0,dd,rr.normalized_matrix_residual,float(delay.min()),0]];lines=[diag(x,rr)]
 for i,u in enumerate(times[1:],start):
  h=u-he[i-1];source,z,Tr,delay,evaluate,diag=endpoint(u,i)
  assert delay.min()>h
  shift=correction(ev,he[i-1],u,orig[0,src]) if correct else None
  has=shift is not None and np.any(shift)
  def candidate(xx):
   A=COMPTON_GAMMA_PER_T4_S_INV_K4*Tr**4*xx/(1+xx+m.f_he)/source.H
   tt=thermal_endpoint(T,gprev,A,Tr,h,'trap');rr,oo,dd=evaluate(xx,tt);f=rr.dxHII_dln_a
   cf=evaluate(xx,tt,shift)[0].dxHII_dln_a-f if has else 0.
   resid=xx-x-h*(.5*(fprev+f)+cf)
   return resid,tt,rr,oo,dd,cf
  width=max(1e-6,10*h*abs(fprev));xx=brentq(lambda q:candidate(q)[0],max(1e-10,x-width),min(1-1e-10,x+width),xtol=2e-15,rtol=1e-14)
  resid,tt,rr,out,defect,cf=candidate(xx);gg=source.thermal_rhs_ln_a(z,xx,tt)
  tres=tt-T-h*.5*(gprev+gg)
  full=1/np.expm1(tab.energy_eV/(KB_NATIVE_EV_K*Tr))+out[:,:311]
  assert 0<xx<1 and tt>0 and min(full.ravel())>=0 and abs(resid)<1e-12 and abs(tres)<1e-8 and defect<1e-8 and rr.normalized_matrix_residual<1e-10
  x,T,fprev,gprev=xx,tt,rr.dxHII_dln_a,gg;hist[i]=out
  rows.append([u,x,T,fprev,gprev,resid,tres,defect,rr.normalized_matrix_residual,float(delay.min()),cf]);lines.append(diag(x,rr))
  if (i-start+1)%128==0:print(label,i-start+1,x,flush=True)
 rows=np.array(rows);lines=np.array(lines)
 # Gross terms separately nonnegative, stable detailed balance compare; signed net uses stable arithmetic.
 np.savez_compressed(D/(label+'.npz'),rows=rows,line=lines,events=ev,final=hist[-1],rays=n)
 out=dict(status='SCOPED_FIRST_PREFIX_EVENT_CORRECTION',angular=angular,rays=len(n),steps=nt,correct=correct,x=x,T=T,event_count=int(np.isfinite(ev).sum()),integrated_jump_correction=float(np.diff(rows[:,0])@rows[1:,10]),max_xres=float(np.max(abs(rows[:,5]))),max_atom_res=float(np.max(rows[:,8])),line_native_max_abs=float(np.max(abs(lines[:,2]-lines[:,3]))),line_native_rel=float(np.max(abs(lines[:,2]-lines[:,3]))/max(np.max(abs(lines[:,3])),1e-300)),line_pair_res=float(np.max(abs(lines[:,4]))),prefix_sha=sha(P),geometry_sha=sha(p),rates_sha=sha(R),scope='first-prefix jump correction with endpoint affine gain, physical uncorrected outgoing; line pair diagnostic, no feedback')
 (D/(label+'.json')).write_text(json.dumps(out,indent=2)+'\n');print(out,flush=True)
if __name__=='__main__':
 a,n,k,l=sys.argv[1:];run(bool(int(a)),int(n),int(k),l)
