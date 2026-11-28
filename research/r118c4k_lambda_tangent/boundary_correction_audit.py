"""Full signed lambda tangent including moving-event GL5 derivative and nonlinear verification."""
from pathlib import Path
import sys,json,numpy as np,time,hashlib
from scipy.optimize import brentq
from numpy.polynomial.legendre import leggauss
D=Path(__file__).resolve().parent;P=D.parent;I=P/'r118c4i_weak_adjoint';H=P/'r118c4h_goal_adjoint';W=P/'r118c3w_common_history'
sys.path[:0]=[str(W),str(P/'r118c3x_three_moments'),str(D.parents[1]/'src')]
from common_base import context,p,JumpResponse
from positive3 import reconstruct
from moving import Moving
g={'__file__':str(I/'active_limiter.py'),'__name__':'prior'};exec(compile((I/'active_limiter.py').read_text(),str(I/'active_limiter.py'),'exec'),g);Map,C,L,mass=g['Map'],g['C'],g['L'],g['mass']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(n,o):(D/n).write_text(json.dumps(o,indent=2)+'\n')
_WORK=None
def stage_job(args):
 # Forked local stage workers; history is communicated only through the
 # already formed moment arrays. Preserve j-ordered sum in the main solve.
 j,u,yy,wj,ang,dwj=args;owner,mm,mp,geoep=_WORK
 f,o,jr=owner(u,yy,wj,j,*ang);gg=[];oo=[]
 for k,ep in enumerate([1e-6,.01/3000]):
  dv=np.eye(2)[k]*ep;p0=owner(u,yy+dv,wj,j,*ang);m0=owner(u,yy-dv,wj,j,*ang);gg.append((p0[0]-m0[0])/(2*ep));oo.append((p0[1]-m0[1])/(2*ep))
 gp=owner(u,yy,wj,j,*mp.state(u));gm=owner(u,yy,wj,j,*mm.state(u))
 df=(gp[0]-gm[0])/(2*geoep);do=(gp[1]-gm[1])/(2*geoep)
 # Return contributions separately to preserve the original addition order.
 terms=[]
 for k in range(3):
  a,b,g0=jr.apply(dwj[k]);terms.append((a+b,g0))
 return f,o,gg,np.stack(oo,axis=-1),df,do,terms
def run(mode,delta=0.):
 lam=-.5+(delta if mode!='tangent' else 0.);N=64;c=context(128);ref=H/'goal_q3_128_-0.5.npz';z=np.load(ref);fullhe=z['he'];he=fullhe[:N+1];v=z['rows'][:N+1,1:3].copy();v[:,1]/=3000
 c.v=np.stack([np.interp(fullhe,c.he,c.v[:,j]) for j in range(c.v.shape[1])],axis=1);c.he=fullhe;nr=c.nr;m=Map(c,lam);gl,gw=leggauss(5)
 if mode=='tangent':
  geoep=1e-3;mm,mp=Map(c,lam-geoep),Map(c,lam+geoep);moving=Moving(m,mm,mp,geoep);event_checks=[];events=0;mindist=1.
 A=np.zeros((N,nr,314,7));DA=np.zeros_like(A) if mode=='tangent' else None
 y=v[0].copy();dy=np.zeros(2);ys=[y.copy()];dys=[dy.copy()];resmax=0.;mi0=1e99;lims=[];active=[];t0=time.monotonic()
 def ww(U):return np.einsum('kjm,mrc->kjrc',L,U)
 def owner(u,y,w,j,a,wgt):
  x,T=y*np.array([1.,3000]);s,HH,Tr=c.snap(u,x,T,c.zero);rr,o,_=p.step(s,a,np.zeros((nr,313)),wgt);jr=JumpResponse(s,a,wgt)
  outs=[];ff=None
  for k in range(3):
   aa,bb,gg=jr.apply(w[k]);outs.append(mass[k,j]*o+aa+bb)
   if k==0:ff=mass[0,j]*rr.dxHII_dln_a+gg
  return float(ff),np.array(outs),jr
 pool=None
 if mode=='tangent':
  global _WORK
  _WORK=(owner,mm,mp,geoep)
  import concurrent.futures as cf,multiprocessing as mpctx
  pool=cf.ProcessPoolExecutor(max_workers=3,mp_context=mpctx.get_context('fork'))
 def thermal(u,y):
  x,T=y;HH=np.interp(u,c.ge,c.g['h'])*2.1842852410855023e-18;Tr=c.model.tcmb0_K*np.exp(-u)/3000
  sc=p.COMPTON_GAMMA_PER_T4_S_INV_K4*(Tr*3000)**4/HH;b=sc*x/(1+x+c.model.f_he);bx=sc*(1+c.model.f_he)/(1+x+c.model.f_he)**2
  return b*(Tr-T)-2*T,np.array([bx*(Tr-T),-b-2])
 for i,r in enumerate(he[1:],1):
  l=he[i-1];h=r-l;mid=(l+r)/2;U=m.mom3(i,l,r,A)
  if mode=='tangent':
   # Alternative bounded diagnostic: directly difference actual moving weak maps.
   dU=(mp.mom3(i,l,r,A)-mm.mom3(i,l,r,A))/(2*geoep)+m.mom3(i,l,r,DA)
   if i in [32,63,128,256]:
    un,ana,ev,md=moving.integrate(i,l,r,A,DA)
    event_checks.append(dict(step=i,nominal_gap=float(np.max(abs(un-U))),moving_vs_secant=float(np.linalg.norm(ana-dU)/max(np.linalg.norm(dU),1e-300))))
  for t,wt in zip(gl,gw):
   f=(t+1)/2;u=l+h*f;R0=m.t(u)-(u-c.lr);b=p._planck_difference(c.ef[None,:]/(p.KB_NATIVE_EV_K*c.model.tcmb0_K*np.exp(-u)),R0)
   for k in range(5):U[k]+=wt/2*b*f**k
   if mode=='tangent':
    energy=c.ef[None,:]/(p.KB_NATIVE_EV_K*c.model.tcmb0_K*np.exp(-u));db=(p._planck_difference(energy,mp.t(u)-(u-c.lr))-p._planck_difference(energy,mm.t(u)-(u-c.lr)))/(2*geoep)
    for k in range(5):dU[k]+=wt/2*db*f**k
  w=ww(U);ang=[m.state(u) for u in [l,mid,r]]
  if mode=='tangent' and i==63:
   # Actual prefix history, independently probe map derivative at the first large transient.
   from scipy.integrate import solve_ivp
   from scipy.interpolate import CubicSpline
   lo,hi=m.D.x[0],m.D.x[-1];t0g=c.he[0];grid=m.D.x
   def rhs(tt,z):
    d,vv=z.reshape(2,3,3);S=c.clock.S(tt);return np.stack([-lam*S@d,-S@d-lam*S@vv]).ravel()
   init=np.stack([np.eye(3),np.zeros((3,3))]).ravel()
   a0=solve_ivp(rhs,(t0g,lo),init,method='DOP853',rtol=2e-13,atol=2e-15,dense_output=True)
   b0=solve_ivp(rhs,(t0g,hi),init,method='DOP853',rtol=2e-13,atol=2e-15,dense_output=True)
   Z=np.empty((len(grid),18));sel=grid<t0g;Z[sel]=a0.sol(grid[sel]).T;Z[~sel]=b0.sol(grid[~sel]).T
   z0=Z.reshape(-1,2,3,3);g0=np.einsum('tij,nj->tni',z0[:,0],c.n);g1=np.einsum('tij,nj->tni',z0[:,1],c.n);dfl=-np.sum(g0*g1,axis=-1)/np.sum(g0*g0,axis=-1)
   fs=[CubicSpline(grid,dfl[:,j],extrapolate=False) for j in range(nr)]
   class Variational(Moving):
    def evald(self,kind,t,dt):
     f=getattr(self.m,kind);q=self.ev(f,t)
     if kind=='f':
      return q,self.ev(fs,t)+np.stack([v(t[j],1) for j,v in enumerate(f)])*dt
     df=self.ev(fs,q);dq=np.stack([v(q[j],1) for j,v in enumerate(self.m.f)])
     return q,(dt-df)/dq
   def force(M):
    w0=ww(M);res=[]
    for j,u0 in enumerate([l,mid,r]):
     y0,y1=v[i-1],v[i];c0=j/2;yy=(1-c0)*y0+c0*y1
     _,_,jr=owner(u0,yy,w[:,j],j,*ang[j]);_,_,gg=jr.apply(w0[0,j]);res.append(gg)
    return float(sum(res))
   # Center convention for an exact receiver-boundary event: average the
   # interior and exterior topology derivatives, preserving the jump term.
   corr=np.zeros_like(dU);aligned=[];he0=c.he[:i];ray=np.arange(nr)[:,None];src=c.src[None,:]
   for side,uu in [('left',l),('right',r)]:
    t=m.t(uu);j0=np.searchsorted(he0,t);jl=np.clip(j0-1,0,len(he0)-1);jr0=np.clip(j0,0,len(he0)-1)
    j=np.where(abs(t-he0[jl])<abs(t-he0[jr0]),jl,jr0);sk=he0[j];cr=m.ev(m.g,m.ev(m.f,sk)+m.lr)
    near=np.isfinite(cr)&(abs(cr-uu)<1e-13)
    dsk=m.ev(fs,sk);dcr=m.ev(fs,cr);den=np.stack([f(cr[k],1) for k,f in enumerate(m.f)]);dr=(dsk-dcr)/den
    js=np.searchsorted(he0,t+2e-14,side='right')-1
    for ri,ci in np.argwhere(near):
     k=int(j[ri,ci]);ch=int(c.src[ci]);assert k<len(he0)-1
     before=float(np.sum(A[k-1,ri,ch])) if k else 0.
     after=float(A[k,ri,ch]@((-1.)**np.arange(A.shape[-1])))
     present=(cr[ri,ci]>l and js[ri,ci]<k) if side=='left' else cr[ri,ci]<r
     zeta=(uu-l)/h;v0=(.5-float(present))*(before-after)*dr[ri,ci]/h
     corr[:,ri,ci]+=v0*zeta**np.arange(5)
     aligned.append(dict(side=side,ray=int(ri),channel=int(ci),knot=k,distance=float(cr[ri,ci]-uu),jump=before-after,arrival_derivative=float(dr[ri,ci]),present=bool(present)))
   out=[];history=m.mom3(i,l,r,DA)
   for eps0 in [1e-3,3e-4,1e-4,3e-5]:
    m0,p0=Map(c,lam-eps0),Map(c,lam+eps0)
    sec=(p0.mom3(i,l,r,A)-m0.mom3(i,l,r,A))/(2*eps0)+history
    for label,mm0 in [('centered_inverse',Moving(m,m0,p0,eps0)),('variational_implicit',Variational(m,m0,p0,eps0))]:
     _,d0,e0,md0=mm0.integrate(i,l,r,A,DA)
     out.append(dict(h=eps0,method=label,relative=float(np.linalg.norm(d0-sec)/max(np.linalg.norm(sec),1e-300)),gas_force=force(d0),gas_secant=force(sec),gas_force_gap=force(d0)-force(sec),events=e0,min_boundary_distance=md0))
     c0=d0+corr
     out.append(dict(h=eps0,method=label+'_center_boundary',relative=float(np.linalg.norm(c0-sec)/max(np.linalg.norm(sec),1e-300)),gas_force=force(c0),gas_secant=force(sec),gas_force_gap=force(c0)-force(sec),events=e0,min_boundary_distance=md0))
   write('BOUNDARY_CORRECTION_AUDIT.json',dict(step=i,u=float(r),rows=out,aligned=aligned,scope='actual step-63 direct-history prefix; compare source geometry map derivative and gas projection only, excluding Planck and local angular owner terms'))
   print('BOUNDARY_CORRECTION_AUDIT',out,flush=True)

  if mode=='tangent':
   y0,y1=v[i-1],v[i];assert np.array_equal(y,y0)
   O=np.zeros((3,nr,314));F=0.;Gs=[];Os=[];ops=[]
   dW=ww(dU);df=0.;do=np.zeros_like(O)
   args=[]
   for j,u in enumerate([l,mid,r]):
    c0=j/2;yy=(1-c0)*y0+c0*y1;args.append((j,u,yy,w[:,j],ang[j],dW[:,j]))
   for f,o,gg,oo,gdf,gdo,terms in pool.map(stage_job,args):
    F+=f;O+=o;Gs.append(gg);Os.append(oo);df+=gdf;do+=gdo
    for k,(ab,g0) in enumerate(terms):
     do[k]+=ab
     if k==0:df+=g0
   Cj=np.array([0.,.5,1.]);Gs=np.array(Gs);th,thj=thermal(mid,(y0+y1)/2)
   G0=np.stack([(1-Cj)@Gs,thj/2]);G1=np.stack([Cj@Gs,thj/2]);dy1=np.linalg.solve(np.eye(2)-h*G1,(np.eye(2)+h*G0)@dy+np.array([h*df,0.]))
   for j in range(3):do+=np.einsum('krci,i->krc',Os[j],(1-Cj[j])*dy+Cj[j]*dy1)
   resmax=max(resmax,float(np.max(abs(y1-y0-h*np.array([F,th])))));yn=y1
  else:
   y0=y;f0,o0,jr=owner(l,y0,w[:,0],0,*ang[0])
   def trial(dx,ret=False):
    xm=y0[0]+dx/2;T0=y0[1];HH=np.interp(mid,c.ge,c.g['h'])*2.1842852410855023e-18;Tr=c.model.tcmb0_K*np.exp(-mid)/3000;sc=p.COMPTON_GAMMA_PER_T4_S_INV_K4*(Tr*3000)**4/HH;b=sc*xm/(1+xm+c.model.f_he)
    T=T0+h*(b*(Tr-T0)-2*T0)/(1+h*(2+b)/2);yn=np.array([y0[0]+dx,T]);f1,o1,_=owner(mid,(y0+yn)/2,w[:,1],1,*ang[1]);f2,o2,_=owner(r,yn,w[:,2],2,*ang[2]);res=dx-h*(f0+f1+f2)
    return (res,yn,o0+o1+o2) if ret else res
   width=max(1e-4,4*abs(v[i,0]-v[i-1,0]));dx=brentq(trial,max(-width,-.99*y0[0]),min(width,.99*(1-y0[0])),xtol=1e-19,rtol=1e-14);res,yn,O=trial(dx,True);resmax=max(resmax,abs(res))
  fr=1/np.expm1(c.tab.energy_eV/(p.KB_NATIVE_EV_K*c.model.tcmb0_K*np.exp(-r)));co,ls,mi=reconstruct(O,fr);A[i-1]=co;mi0=min(mi0,mi)
  lims.extend([i,*q] for q in ls)
  if mode=='tangent':
   dc=np.zeros_like(co);dc[...,:3]=np.einsum('ak,krc->rca',C,do)
   # Active LP: actual directional perturbation of the full original reconstruction, including scale and moving constraint nodes.
   for q in ls:
    ray,ch=map(int,q[:2]);base=O[:,ray,ch];d=do[:,ray,ch];scale=max(np.max(abs(base)),fr[ch]);mag=max(np.max(abs(d)),1e-300)
    # Relative local displacement 1e-6 and 1e-7. Use one-channel reconstruction with correct local Planck floor.
    localfr=np.ones(311);localfr[0]=fr[ch]/scale;oo=np.zeros((3,1,314));oo[:,0,0]=base/scale;dd=np.zeros_like(oo);dd[:,0,0]=d/mag
    a0,l0,_=reconstruct(oo,localfr);assert len(l0)==1
    rec=dict(step=i,ray=ray,channel=ch,scale=float(scale),direction_norm=float(mag),checks=[])
    for ep in [1e-6,1e-7]:
     a,la,ma=reconstruct(oo+ep*dd,localfr);b,lb,mb=reconstruct(oo-ep*dd,localfr);p1=(a[0,0]-a0[0,0])/ep;m1=(a0[0,0]-b[0,0])/ep
     rec['checks'].append(dict(eps=ep,one_sided_gap=float(np.linalg.norm(p1-m1)),plus_limited=len(la),minus_limited=len(lb),plus_min=ma,minus_min=mb,center=((p1+m1)/2).tolist()))
    dc[ray,ch,3:]=mag*np.array(rec['checks'][-1]['center'][3:]);active.append(rec)
   DA[i-1]=dc;dy=dy1;dys.append(dy.copy())
  y=yn;ys.append(y.copy())
  if i%128==0:print(mode,delta,i,'limited',len(lims),'x',y[0],flush=True)
  if mode=='tangent' and (i%256==0 or i in (1772,1773)):
   # Preserve finite-prefix evidence before advancing. Not a full restart checkpoint.
   np.savez_compressed(D/'BOUNDARY_LOCAL_PREFIX.npz',u=he[:i+1],y=np.array(ys),dy=np.array(dys),last=A[i-1],last_tangent=DA[i-1],limits=np.array(lims))
   write('BOUNDARY_LOCAL_PREFIX.json',dict(steps=i,terminal_gradient=dy.tolist(),resmax=resmax,min_positive=mi0,active=active,event_checks=event_checks,endpoint_fallback=moving.endpoint_fallback,scope='finite completed prefix; no full restart state'))
 if pool is not None:pool.shutdown()

 tag='BOUNDARY_LOCAL_TANGENT' if mode=='tangent' else f'FD_{delta:g}'
 ys=np.array(ys);obj=dict(mode=mode,delta=delta,steps=N,lam=lam,resmax=resmax,min_positive=mi0,limited=len(lims),seconds=time.monotonic()-t0,source_sha=sha(ref),final=ys[-1].tolist(),max_baseline_gap=float(np.max(abs(ys-v))) if mode=='tangent' else None,scope='full signed weak-history owner at lambda=-0.5, first-order derivative in lambda including geometry, moving GL5 events and active LP; local geometry derivatives from actual spline stencils, not reverse adjoint')
 if mode=='tangent':
  ex=z['limits'];ex=ex[ex[:,0]<=N];assert len(lims)==len(ex)==0
  obj.update(terminal_gradient=dy.tolist(),active=active,event_checks=event_checks,moving_events=events,min_event_boundary_distance=mindist,geometry_stencil=geoep,endpoint_fallback=moving.endpoint_fallback,stage_workers=3)
  # Save only selected actual final history and tangent; actual event source data for separate local replay.
  np.savez_compressed(D/'BOUNDARY_LOCAL_TANGENT.npz',u=he,y=ys,dy=np.array(dys),last=A[-1],last_tangent=DA[-1],limits=np.array(lims))
 else:np.savez_compressed(D/(tag+'.npz'),u=he,y=ys,last=A[-1],limits=np.array(lims))
 write(tag+'.json',obj);print('DONE',tag,{k:v for k,v in obj.items() if k!='active'},flush=True)
def analyze():
 a=json.loads((D/'TANGENT.json').read_text());t=np.load(D/'BOUNDARY_LOCAL_TANGENT.npz');rows=[]
 for h in [.003]:
  m=np.load(D/f'FD_{-h:g}.npz');p=np.load(D/f'FD_{h:g}.npz');assert np.array_equal(m['u'],t['u']) and np.array_equal(p['u'],t['u'])
  dy=(p['y']-m['y'])/(2*h);d=t['dy'];dA=(p['last']-m['last'])/(2*h)
  row=dict(eps=h,terminal_FD=dy[-1].tolist(),terminal_gap=(dy[-1]-d[-1]).tolist(),max_history_gas_gap=np.max(abs(dy-d),axis=0).tolist(),final_history_relative=float(np.linalg.norm(dA-t['last_tangent'])/max(np.linalg.norm(t['last_tangent']),1e-300)),minus_limiter_count=len(m['limits']),plus_limiter_count=len(p['limits']),same_limiter_keys=bool(np.array_equal(m['limits'][:,:3],t['limits'][:,:3]) and np.array_equal(p['limits'][:,:3],t['limits'][:,:3])))
  rows.append(row)
 write('LAMBDA_TANGENT.json',dict(tangent=a,finite_difference=rows,scope='actual 1773-step signed lambda derivative with moving GL5 events and active LP directional replay; centered geometry stencils; no reverse adjoint or continuum proof'))
 print(rows,flush=True)
if __name__=='__main__':run('tangent')
