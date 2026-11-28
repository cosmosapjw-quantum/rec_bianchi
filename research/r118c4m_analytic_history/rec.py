"""Two analytic event/finite atomic directional history sensitivities on actual 1773-step owner.
D_+ and D_- are both divided by positive eps. Baseline held at accepted gas endpoints.
The finite geometry and LP stencils are not a proof of classical differentiability."""
from pathlib import Path
import sys,json,numpy as np,time,hashlib,os
from numpy.polynomial.legendre import leggauss
from event import Events
from limiter import analytic
D=Path(__file__).resolve().parent;P=D.parent;K=P/'r118c4k_lambda_tangent';H=P/'r118c4h_goal_adjoint';L0=P/'r118c4l_directional_history'
sys.path.insert(0,str(K))
import rec as old
# The file itself is rec.py; executing as __main__ makes the import above resolve the prior module.
Map,C,L,mass=old.Map,old.C,old.L,old.mass
context,p,JumpResponse,reconstruct=old.context,old.p,old.JumpResponse,old.reconstruct
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(n,o):(D/n).write_text(json.dumps(o,indent=2,allow_nan=False)+'\n')
# Same exact C3Z quadrature arithmetic, but reuse geometry for the three histories.
def multi(m,i,l,r,hist):
 c=m.c;he=c.he[:i];nr=m.nr;src=c.src[None,:];h=r-l;nn=len(hist)
 t1=m.t(r);assert np.max(t1)<he[-1]
 u=np.full((nr,313),l);out=np.zeros((nn,5,nr,313));nodes,weights=leggauss(5);ray=np.arange(nr)[:,None]
 for _ in range(len(he)+2):
  active=u<r
  if not active.any():return out
  t=m.t(u);j=np.searchsorted(he,t+2e-14,side='right')-1;before=j<0
  nk=he[np.clip(j+1,0,len(he)-1)];cross=m.ev(m.g,m.ev(m.f,nk)+m.lr)
  end=np.minimum(r,np.where(np.isfinite(cross),cross,r));end=np.where(active,end,u);span=end-u
  if np.any(active&(span<=0)):raise ValueError('event progress')
  if i>1:
   k=np.clip(j,0,len(he)-2);hh=he[k+1]-he[k];coef=np.stack([a[k,ray,src] for a in hist])
   for q,w in zip(nodes,weights):
    x=u+(q+1)*span/2;s=2*np.clip((m.t(x)-he[k])/hh,0,1)-1
    f=coef[...,0]+s*coef[...,1];P0=np.ones_like(s);P1=s
    for z in range(2,7):
     P2=((2*z-1)*s*P1-(z-1)*P0)/z;f+=coef[...,z]*P2;P0,P1=P1,P2
    f=np.where(active&~before,f,0.);zz=(x-l)/h;wt=w*span/(2*h)
    for j in range(5):out[:,j]+=wt*f*zz**j
  u=end
 raise ValueError('too many events')
_WORK=None
def stage_job(args):
 j,u,yy,wj,ang,dwj=args;owner,events,eps=_WORK
 f,o,jr=owner(u,yy,wj,j,*ang);gg=[];oo=[]
 for k,ep in enumerate([1e-6,.01/3000]):
  dv=np.eye(2)[k]*ep;a=owner(u,yy+dv,wj,j,*ang);b=owner(u,yy-dv,wj,j,*ang);gg.append((a[0]-b[0])/(2*ep));oo.append((a[1]-b[1])/(2*ep))
 df=[];dout=[]
 a0,w0,da,dw=events.ang(u)
 for k,sg in enumerate([1,-1]):
  a=owner(u,yy,wj,j,a0+sg*eps*da,w0+sg*eps*dw);ff=(a[0]-f)/eps;oo0=(a[1]-o)/eps
  for l in range(3):
   b,c,g0=jr.apply(dwj[k,l]);oo0[l]+=b+c
   if l==0:ff+=g0
  df.append(ff);dout.append(oo0)
 return f,o,gg,np.stack(oo,axis=-1),np.array(df),np.array(dout)
def run():
 c=context(128);ref=H/'goal_q3_128_-0.5.npz';z=np.load(ref);he=z['he'];N=len(he)-1;assert N==1773
 v=z['rows'][:,1:3].copy();v[:,1]/=3000;c.v=np.stack([np.interp(he,c.he,c.v[:,j]) for j in range(c.v.shape[1])],axis=1);c.he=he;nr=c.nr
 lam=-.5;eps=.001;m,mp,mm=[Map(c,x) for x in [lam,lam+eps,lam-eps]];events=Events(m);print('variational base gap',events.ode_base_gap,flush=True)
 A=np.zeros((N,nr,314,7));DA=np.zeros((2,N,nr,314,7));dy=np.zeros((2,2));dys=[dy.copy()];lims=[];active=[];checks=[];mi0=1e99;resmax=0.;t0=time.monotonic();gl,gw=leggauss(5)
 def ww(U):return np.einsum('kjm,mrc->kjrc',L,U)
 def owner(u,y,w,j,a,wgt):
  x,T=y*np.array([1.,3000]);s,HH,Tr=c.snap(u,x,T,c.zero);rr,o,_=p.step(s,a,np.zeros((nr,313)),wgt);jr=JumpResponse(s,a,wgt);outs=[];ff=None
  for k in range(3):
   aa,bb,gg=jr.apply(w[k]);outs.append(mass[k,j]*o+aa+bb)
   if k==0:ff=mass[0,j]*rr.dxHII_dln_a+gg
  return float(ff),np.array(outs),jr
 def thermal(u,y):
  x,T=y;HH=np.interp(u,c.ge,c.g['h'])*2.1842852410855023e-18;Tr=c.model.tcmb0_K*np.exp(-u)/3000
  sc=p.COMPTON_GAMMA_PER_T4_S_INV_K4*(Tr*3000)**4/HH;b=sc*x/(1+x+c.model.f_he);bx=sc*(1+c.model.f_he)/(1+x+c.model.f_he)**2
  return b*(Tr-T)-2*T,np.array([bx*(Tr-T),-b-2])
 global _WORK
 _WORK=(owner,events,eps)
 import concurrent.futures as cf,multiprocessing as mpctx
 with cf.ProcessPoolExecutor(max_workers=3,mp_context=mpctx.get_context('fork')) as pool:
  for i,r in enumerate(he[1:],1):
   l=he[i-1];h=r-l;mid=(l+r)/2
   U,dU=events.integrate(i,l,r,A,DA)
   if i in [1,32,63,128,512,918,974,1773]:
    u0=m.mom3(i,l,r,A);gap=float(np.max(abs(U-u0))/max(np.max(abs(u0)),1e-300));assert gap<1e-12
    dd=np.stack([(g.mom3(i,l,r,A)-u0)/eps+m.mom3(i,l,r,DA[k]) for k,g in enumerate([mp,mm])])
    gg=np.linalg.norm((dd-dU).reshape(2,-1),axis=1)/np.maximum(np.linalg.norm(dd.reshape(2,-1),axis=1),1e-300)
    checks.append(dict(step=i,nominal_gap=gap,geometry_direction_vs_secant=gg.tolist()))
   for t,wt in zip(gl,gw):
    f=(t+1)/2;u=l+h*f;energy=c.ef[None,:]/(p.KB_NATIVE_EV_K*c.model.tcmb0_K*np.exp(-u))
    B=p._planck_difference(energy,m.t(u)-(u-c.lr))
    _,dt=events.td(u);e=energy*np.exp(m.t(u)-(u-c.lr));occ=1/np.expm1(e);b0=-e*occ*(1+occ)*dt;dB=np.stack([b0,-b0])
    for k in range(5):U[k]+=wt/2*B*f**k;dU[:,k]+=wt/2*dB*f**k
   w=ww(U);dw=np.stack([ww(x) for x in dU]);ang=[m.state(u) for u in [l,mid,r]]
   y0,y1=v[i-1],v[i];O=np.zeros((3,nr,314));F=0.;Gs=[];Os=[];df=np.zeros(2);do=np.zeros((2,3,nr,314))
   args=[(j,u,(1-j/2)*y0+j/2*y1,w[:,j],ang[j],dw[:,:,j]) for j,u in enumerate([l,mid,r])]
   for f,o,gg,oo,gdf,gdo in pool.map(stage_job,args):F+=f;O+=o;Gs.append(gg);Os.append(oo);df+=gdf;do+=gdo
   Cj=np.array([0.,.5,1.]);Gs=np.array(Gs);th,thj=thermal(mid,(y0+y1)/2);G0=np.stack([(1-Cj)@Gs,thj/2]);G1=np.stack([Cj@Gs,thj/2])
   dy1=np.stack([np.linalg.solve(np.eye(2)-h*G1,(np.eye(2)+h*G0)@dy[k]+np.array([h*df[k],0.])) for k in range(2)])
   for k in range(2):
    for j in range(3):do[k]+=np.einsum('krci,i->krc',Os[j],(1-Cj[j])*dy[k]+Cj[j]*dy1[k])
   resmax=max(resmax,float(np.max(abs(y1-y0-h*np.array([F,th])))))
   fr=1/np.expm1(c.tab.energy_eV/(p.KB_NATIVE_EV_K*c.model.tcmb0_K*np.exp(-r)));co,ls,mi=reconstruct(O,fr);A[i-1]=co;mi0=min(mi0,mi);lims.extend([i,*q] for q in ls)
   dc=np.zeros((2,*co.shape));dc[...,:3]=np.einsum('ak,skrc->srca',C,do)
   for q in ls:
    ray,ch=map(int,q[:2]);base=O[:,ray,ch];scale=max(np.max(abs(base)),fr[ch]);localfr=np.ones(311);localfr[0]=fr[ch]/scale;oo=np.zeros((3,1,314));oo[:,0,0]=base/scale
    a0,l0,_=reconstruct(oo,localfr);assert len(l0)==1
    for k in range(2):
     d=do[k,:,ray,ch];mag=max(np.max(abs(d)),1e-300);dd=np.zeros_like(oo);dd[:,0,0]=d/mag;vals=[]
     for ep in [1e-6,1e-7]:
      b,lb,mb=reconstruct(oo+ep*dd,localfr);vals.append((b[0,0]-a0[0,0])/ep);active.append(dict(step=i,ray=ray,channel=ch,direction=[1,-1][k],eps=ep,limited=len(lb),min_positive=mb))
     fd=mag*vals[-1][3:]
     try:
      qd,lh=analytic(base,fr[ch],d,co[ray,ch]);err=float(np.linalg.norm(qd-fd)/max(np.linalg.norm(fd),1e-300))
      ok=bool(err<3e-3)
      active.append(dict(step=i,ray=ray,channel=ch,direction=[1,-1][k],kind='analytic_lp',relative_vs_finite=err,used=ok,iterations=lh,analytic=qd.tolist(),finite=fd.tolist()))
      dc[k,ray,ch,3:]=qd if ok else fd
     except (ValueError,AssertionError,np.linalg.LinAlgError) as err:
      active.append(dict(step=i,ray=ray,channel=ch,direction=[1,-1][k],kind='analytic_lp',used=False,error=str(err),finite=fd.tolist()))
      dc[k,ray,ch,3:]=fd

   DA[:,i-1]=dc;dy=dy1;dys.append(dy.copy())
   if ls:np.savez_compressed(D/f'LP_{i}.npz',O=O,fr=fr,co=co,do=do,dc=dc)
   if i%128==0:print('step',i,'directional',dy.tolist(),'events',events.events,'aligned',len(events.aligned),'seconds',time.monotonic()-t0,flush=True)
   if i%256==0 or i==N:
    tmp=D/'prefix.tmp.npz';np.savez_compressed(tmp,u=he[:i+1],dy=np.array(dys),last=A[i-1],last_d=DA[:,i-1]);os.replace(tmp,D/'PREFIX.npz')
    write('PREFIX.json',dict(steps=i,terminal=dy.tolist(),max_nominal_residual=resmax,min_positive=mi0,limits=len(lims)))
 ex=z['limits'];assert np.array_equal(np.array(lims)[:,:3],ex[:,[0,2,3]])
 dy=np.array(dys);refrows=[]
 for h in [.003,.001,.0003]:
  pref='FD' if h==.003 else 'PREFIX_FD'
  for k,sg in enumerate([1,-1]):
   path=K/f'{pref}_{sg*h:g}.npz';q=np.load(path);n=len(q['u']);assert np.array_equal(q['u'],he[:n]);f=(q['y']-v[:n])/h
   e=abs(f-dy[:n,k]);row=dict(h=h,direction=sg,steps=n-1,terminal_directional=dy[n-1,k].tolist(),terminal_FD=f[-1].tolist(),terminal_gap=e[-1].tolist(),max_gap=e.max(0).tolist(),peak_FD=np.max(abs(f),axis=0).tolist(),source_sha=sha(path))
   if n==len(he):row['same_limiter_keys']=bool(np.array_equal(q['limits'][:,:3],np.array(lims)[:,:3]));row['outgoing_FD_relative']=float(np.linalg.norm((q['last']-A[-1])/h-DA[k,-1])/max(np.linalg.norm((q['last']-A[-1])/h),1e-300))
   refrows.append(row)
 sym=.5*(dy[:,0]-dy[:,1]);cen=np.load(K/'DIRECT_FULL_TANGENT.npz')['dy']
 np.savez_compressed(D/'ANALYTIC_HISTORY.npz',u=he,y=v,dy=dy,last=A[-1],last_d=DA[:,-1],limits=np.array(lims))
 out=dict(steps=N,geometry_stencil=eps,nominal_residual=resmax,min_positive=mi0,limiter_count=len(lims),active=active,checks=checks,FD=refrows,step63=dict(plus=dy[63,0].tolist(),minus=dy[63,1].tolist(),left_slope=(-dy[63,1]).tolist()),nonadditivity_peak=np.max(abs(dy[:,0]+dy[:,1]),axis=0).tolist(),sym_vs_C4K_max=np.max(abs(sym-cen),axis=0).tolist(),seconds=time.monotonic()-t0,variational_base_gap=events.ode_base_gap,events=events.events,inverse_residual=events.inv_res,aligned=events.aligned,lp_analytic_used=sum(x.get('used',False) for x in active),lp_analytic_total=sum(x.get('kind')=='analytic_lp' for x in active),C4L_directional_max_gap=np.max(abs(dy-np.load(L0/'DIRECTIONAL.npz')['dy']),axis=0).tolist(),scope='analytic variational causal-arrival and branch-aware GL5 derivative with implicit inverse interpolation approximation; directional adaptive LP active-row derivative or explicitly logged finite fallback, local atomic and angular JVP finite stencils; actual H-only fixed H full represented history, no classical differentiability claim')
 write('ANALYTIC_HISTORY.json',out);print(json.dumps(out),flush=True)
if __name__=='__main__':run()
