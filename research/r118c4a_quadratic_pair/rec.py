"""C4A quadratic direct and stable paired retarded owner on same cells; matched line net flux."""
from pathlib import Path
import json,sys,numpy as np,hashlib
from numpy.polynomial.legendre import leggauss,legval,legder,legroots
from scipy.optimize import brentq
D=Path(__file__).resolve().parent;P=D.parent;Z=P/'r118c3z_refined_retarded';W=P/'r118c3w_common_history';X=P/'r118c3x_three_moments'
sys.path.insert(0,str(D.parents[1]/'src'));sys.path.insert(0,str(W));sys.path.insert(0,str(X))
from common_base import context
from common_pair import p,JumpResponse,thermal_diff
from positive3 import reconstruct
def write(n,x):(D/n).write_text(json.dumps(x,indent=2)+'\n')
def load_module():
 s=(Z/'quadratic_generated.py').read_text()
 old="last=A[-1],limits=np.array(limit).reshape(-1,7))"
 new="last=A[-1],limits=np.array(limit).reshape(-1,7),**({'all_history':A} if lam==0 else {}))"
 assert s.count(old)==1;s=s.replace(old,new)
 ns={'__file__':str(D/'quadratic_direct.py'),'__name__':'c4a_direct'};exec(compile(s,str(Z/'quadratic_generated.py'),'exec'),ns);return ns
def ctx(nt,ref):
 c=context(nt);he=c.he
 if ref>1:
  zz=np.expm1(-he);new=[]
  for l,r,zl,zr in zip(he[:-1],he[1:],zz[:-1],zz[1:]):
   n=ref if zr<1106.6 and zl>1105.5 else 1
   new.extend(np.linspace(l,r,n,endpoint=False))
  new=np.r_[new,he[-1]]
  c.v=np.stack([np.interp(new,he,c.v[:,j]) for j in range(c.v.shape[1])],axis=1);c.he=new
 return c
def tag(nt,lam,ref):return f'q3_{nt}_{lam:g}'+(f'_local{ref}' if ref>1 else '')
def direct(nt,lam,ref):
 ns=load_module();ns['run'](nt,lam,ref)
 if nt==32 and ref==1:
  a=np.load(D/(tag(nt,lam,ref)+'.npz'));b=np.load(Z/(tag(nt,lam,ref)+'.npz'))
  assert np.array_equal(a['rows'],b['rows'])
  write('REPLAY_'+tag(nt,lam,ref)+'.json',dict(bitwise_rows=True,case=tag(nt,lam,ref)))
def weights(U,k):
 a,b,c=U[k:k+3];return [a-3*b+2*c,4*(b-c),2*c-b]
def mass(k):return np.array([1/(k+1)-3/(k+2)+2/(k+3),4/(k+2)-4/(k+3),2/(k+3)-1/(k+2)])
def pair(nt,lam,ref):
 assert lam!=0
 Map=load_module()['Map'];c=ctx(nt,ref);z=np.load(D/(tag(nt,0,ref)+'.npz'));he=z['he'];A=z['all_history'];v=z['rows'];assert np.array_equal(c.he,he)
 nr=c.nr;N=len(he)-1;m=Map(c,lam);m0=Map(c,0.);B=np.zeros((N,nr,314,7));zero=np.zeros((nr,313))
 def owner(u,x,T,angular):
  aa,ww=m.state(u) if angular else (np.ones(nr),c.w);s,H,Tr=c.snap(u,x,T,c.zero);rr,o,_=p.step(s,aa,zero,ww);return rr.dxHII_dln_a,o,JumpResponse(s,aa,ww)
 def apply(o,I):
  a,b,g=o[2].apply(I);return a+b,g
 def geom(u):
  t=m.t(u);return p._planck_difference(c.ef[None,:]/(p.KB_NATIVE_EV_K*c.model.tcmb0_K*np.exp(-u)),t-(u-c.lr))
 dx=dT=0.;rows=[[he[0],0.,0.,0.,0.]];maxroot=maxref=maxmom=0.;minpos=np.inf;limits=0;gl,gw=leggauss(5);cells=0
 for i,r in enumerate(he[1:],1):
  l=he[i-1];h=r-l;mid=(l+r)/2;xl,Tl=v[i-1,1:3];xr,Tr=v[i,1:3];xm=(xl+xr)/2;Tm=(Tl+Tr)/2
  U=m0.mom3(i,l,r,A);V=m.mom3(i,l,r,A)+m.mom3(i,l,r,B)
  for zz,ww in zip(gl,gw):
   f=(zz+1)/2;g=geom(l+h*f)
   for k in range(5):V[k]+=ww/2*g*f**k
  dif=V-U;old=[owner(l,xl,Tl,False),owner(mid,xm,Tm,False),owner(r,xr,Tr,False)];a1=owner(l,xl+dx,Tl+dT,True)
  W0=weights(U,0);WD=weights(dif,0);w=mass(0)
  def diffop(o0,o1,J0,J1):
   a,g=apply(o0,J0);b,h=apply(o1,J0);c,k=apply(o1,J1);return b-a+c,h-g+k
  H=np.interp(mid,c.ge,c.g['h'])*2.1842852410855023e-18;Tgamma=c.model.tcmb0_K*np.exp(-mid);scale=p.COMPTON_GAMMA_PER_T4_S_INV_K4*Tgamma**4/H;A0=scale*xm/(1+xm+c.model.f_he)
  def trial(dn):
   dm=(dx+dn)/2;A1=scale*(xm+dm)/(1+xm+dm+c.model.f_he);dt=thermal_diff(Tl,Tr,dT,A0,A1,Tgamma,h)
   new=[a1,owner(mid,xm+dm,Tm+(dT+dt)/2,True),owner(r,xr+dn,Tr+dt,True)]
   F=sum(w[j]*(new[j][0]-old[j][0])+diffop(old[j],new[j],W0[j],WD[j])[1] for j in range(3))
   return dn-dx-h*F,dt,F,new
  dn=brentq(lambda t:trial(t)[0],dx-1e-6,dx+1e-6,xtol=1e-21,rtol=1e-14);res,dt,F,new=trial(dn);maxroot=max(maxroot,abs(res))
  O=[]
  for k in range(3):
   Wk=weights(U,k);Dk=weights(dif,k);mk=mass(k);out=sum(mk[j]*(new[j][1]-old[j][1])+diffop(old[j],new[j],Wk[j],Dk[j])[0] for j in range(3));O.append(out)
  O=np.array(O);base=A[i-1];M0=np.array([base[...,0],base[...,0]/2+base[...,1]/6,base[...,0]/3+base[...,1]/6+base[...,2]/30])
  fr=1/np.expm1(c.tab.energy_eV/(p.KB_NATIVE_EV_K*c.model.tcmb0_K*np.exp(-r)))
  co,ls,mp=reconstruct(M0+O,fr);limits+=len(ls);B[i-1]=co-base;B[i-1,...,0]=O[0];B[i-1,...,1]=6*O[1]-3*O[0];B[i-1,...,2]=30*O[2]-30*O[1]+5*O[0]
  rec=np.array([B[i-1,...,0],B[i-1,...,0]/2+B[i-1,...,1]/6,B[i-1,...,0]/3+B[i-1,...,1]/6+B[i-1,...,2]/30]);maxmom=max(maxmom,float(np.max(abs(rec-O))))
  stored=(base+B[i-1])[...,:311,:].copy();stored[...,0]+=fr;stored/=fr[None,:,None]
  pa,pb,pc=stored[...,0],stored[...,1],stored[...,2];yy=np.clip(np.divide(-pb,3*pc,out=np.zeros_like(pb),where=pc!=0),-1,1)
  lower=np.minimum(np.minimum(pa-pb+pc,pa+pb+pc),pa+pb*yy+pc*(3*yy*yy-1)/2)
  for ii,jj in np.argwhere(np.any(stored[...,3:]!=0,axis=-1)):
   cc=stored[ii,jj];roots=legroots(legder(cc));roots=roots.real[(abs(roots.imag)<1e-10)&(abs(roots.real)<1)];lower[ii,jj]=np.min(legval(np.r_[-1,1,roots],cc))
  if np.min(lower)<=0:
   write('FAIL_POS_'+tag(nt,lam,ref)+'.json',dict(i=i,min_ratio=float(np.min(lower))));raise ValueError('stored full positivity')
  minpos=min(minpos,float(np.min(lower)));cells+=lower.size
  F0=sum(w[j]*old[j][0]+apply(old[j],W0[j])[1] for j in range(3));maxref=max(maxref,abs(xr-xl-h*F0))
  dx,dT=dn,dt;rows.append([r,dx,dT,F,res])
  if i%128==0:print('quad pair',nt,ref,lam,i,dx,flush=True)
 rows=np.array(rows);assert maxroot<1e-14 and minpos>0 and maxref<1e-14 and maxmom<1e-20
 directpath=D/(tag(nt,lam,ref)+'.npz');d=np.load(directpath);assert np.array_equal(d['he'],he)
 directdelta=float(d['rows'][-1,1]-v[-1,1]);err=float(abs(dx-directdelta))
 out=dict(nt=nt,lam=lam,ref=ref,steps=N,delta_x=float(dx),delta_T=float(dT),direct_delta_x=directdelta,abs_disagreement=err,maxroot=float(maxroot),max_reference_residual=float(maxref),max_weak_moment_abs=maxmom,min_stored_virtual_ratio=minpos,cells_checked=cells,limited=limits,event_splits=m.events,mesh_sha256=hashlib.sha256(he.tobytes()).hexdigest(),scope='stable same quadratic owner, direct and paired share scalar mesh, fixed H H-only, no continuum')
 np.savez_compressed(D/('PAIR_'+tag(nt,lam,ref)+'.npz'),rows=rows,last_signed=B[-1]);write('PAIR_'+tag(nt,lam,ref)+'.json',out);print(out,flush=True)
def line():
 from common_pair import Map
 from scipy.constants import h,c,electron_volt
 ctx0=context(128);z=np.load(W/'base_128.npz');he=z['he'];L,M,R=[z[k] for k in ['L','M','R']];v=z['rows'];m=Map(ctx0,.5);m0=Map(ctx0,0.)
 E=np.array([np.unique(ctx0.es[ctx0.src==j]).item() for j in range(311,314)]);assert np.array_equal(ctx0.ef[311:],E[:2]);nu=E*electron_volt/h
 def sample(tt,i):
  j=np.searchsorted(he[:i],tt,side='right')-1;before=j<0;assert np.max(tt)<he[i-1]
  if i==1:return np.zeros_like(tt)
  j=np.clip(j,0,i-2);w=(tt-he[j])/(he[j+1]-he[j]);src=ctx0.src[None,:]
  f=(1-3*w+2*w*w)*L[j,0,src]+(4*w-4*w*w)*M[j,0,src]+(2*w*w-w)*R[j,0,src]
  return np.where(before,0.,f)
 rows=[]
 for i in np.unique(np.linspace(1,len(he)-1,65).astype(int)):
  u=he[i];I0=sample(m0.t(u),i);tt=m.t(u);I=sample(tt,i)+p._planck_difference(ctx0.ef[None,:]/(p.KB_NATIVE_EV_K*ctx0.model.tcmb0_K*np.exp(-u)),tt-(u-ctx0.lr))
  s,H,Tr=ctx0.snap(u,*v[i,1:3],ctx0.zero);a,w=m.state(u);op=JumpResponse(s,a,w);d=I-I0;_,ind,gas=op.apply(d)
  scale=8*np.pi*(nu/c)**3/(s.nH_cgs*1e6);out=scale*((w*a)@ind[:,311:]);incoming=scale[:2]*((w*a)@d[:,311:]);net=scale[:2]*((w*a)@(ind[:,311:313]-d[:,311:]))
  assert np.linalg.norm(net-(out[:2]-incoming))<1e-12*max(np.linalg.norm(out[:2])+np.linalg.norm(incoming),1e-300)
  _,o0,_=p.step(s,a,I0,w);_,o1,_=p.step(s,a,I,w);ref=scale[:2]*((w*a)@((o1-o0)[:,311:313]-d[:,311:]))
  err=np.linalg.norm(ref-net)/max(np.linalg.norm(net),1e-300)
  rows.append(dict(z=float(np.expm1(-u)),out_number_per_H_du=out.tolist(),in_number_per_H_du=incoming.tolist(),matched_net_number_per_H_du=net.tolist(),matched_net_energy_eV_per_H_du=(net*E[:2]).tolist(),out_energy_eV_per_H_du=(out*E).tolist(),comparator_relative=float(err),gas_response=float(gas)))
 o=dict(energies_eV=E.tolist(),rows=rows,max_comparator_relative=max(x['comparator_relative'] for x in rows),scope='matched Ly-alpha/beta outgoing-minus-incoming occupation crossing flux at fixed gas geometry; gamma outgoing only; not total atomic energy or chemical heat')
 write('MATCHED_LINE.json',o);print('line',len(rows),o['max_comparator_relative'],flush=True)
if __name__=='__main__':
 mode=sys.argv[1]
 if mode=='line':line()
 else:
  nt,lam,ref=int(sys.argv[2]),float(sys.argv[3]),int(sys.argv[4]);{'direct':direct,'pair':pair}[mode](nt,lam,ref)

