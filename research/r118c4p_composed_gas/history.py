"""Two analytic event/finite atomic directional history sensitivities on actual 1773-step owner.
D_+ and D_- are both divided by positive eps. Baseline held at accepted gas endpoints.
The finite geometry and LP stencils are not a proof of classical differentiability."""
from pathlib import Path
import sys,json,numpy as np,time,hashlib,os
from numpy.polynomial.legendre import leggauss
sys.path.insert(0,str(Path(__file__).resolve().parent.parent/"r118c4n_exact_spline_atomic"))
from event import Events
from atomic_x import jvp as xjvp
from thermal import jvp as tjvp
sys.path.insert(0,str(Path(__file__).resolve().parent.parent/"r118c4m_analytic_history"))
from limiter import analytic
D=Path(__file__).resolve().parent;P=D.parent;K=P/'r118c4k_lambda_tangent';H=P/'r118c4h_goal_adjoint';L0=P/'r118c4l_directional_history';M0=P/'r118c4m_analytic_history'
sys.path.insert(0,str(K))
import rec as old
from atomic import apply as atomic_apply
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
 j,u,yy,wj,ang,dwj=args;owner,events,eps,c=_WORK
 f,o,jr=owner(u,yy,wj,j,*ang);gg=[];oo=[]
 x,T=yy*np.array([1.,3000]);s,HH,Tr=c.snap(u,x,T,c.zero);a,w,da,dw=events.ang(u)
 # Same represented a,w as owner, not the derivative object's rounded variant.
 aa,ww=ang
 gx=[];gt=[];ox=[];ot=[];basegap=0.;res=0.
 for k in range(3):
  G,O,dG,dO=xjvp(s,aa,ww,wj[k],mass[k,j])
  H,Q,dH,dQ,rr,dp=tjvp(c,s,aa,ww,wj[k],T,mass[k,j])
  gx.append(dG);gt.append(dH*3000/T);ox.append(dO);ot.append(dQ*3000/T)
  basegap=max(basegap,float(np.linalg.norm(O-o[k])/max(np.linalg.norm(o[k]),1e-300)),float(np.linalg.norm(Q-o[k])/max(np.linalg.norm(o[k]),1e-300)))
  res=max(res,rr)
 gg=[gx[0],gt[0]];oo=[np.array(ox),np.array(ot)]
 gascheck=None
 # Independent source-rebuilt finite columns on exact selected endpoint stages.
 if j==2 and int(np.argmin(abs(c.he-u))) in [1,32,63,99,128]:
  errs=[]
  for k,ep in enumerate([1e-6,.01/3000]):
   dv=np.eye(2)[k]*ep;ap=owner(u,yy+dv,wj,j,*ang);am=owner(u,yy-dv,wj,j,*ang);gfd=(ap[0]-am[0])/(2*ep);ofd=(ap[1]-am[1])/(2*ep)
   errs.append(dict(column=k,gas_relative=float(abs(gfd-gg[k])/max(abs(gg[k]),1e-300)),outgoing_relative=float(np.linalg.norm(ofd-oo[k])/max(np.linalg.norm(oo[k]),1e-300))))
  gascheck=dict(u=float(u),errors=errs)
 df=[];dout=[];nom=0.;ng=0.
 for k,sg in enumerate([1,-1]):
  v=[];q=0.
  for l in range(3):
   G,O,dG,dO=atomic_apply(s,a,w,sg*da,sg*dw,wj[l],dwj[k,l],mass[l,j])
   nom=max(nom,float(np.linalg.norm(O-o[l])/max(np.linalg.norm(o[l]),1e-300)))
   if l==0:q=dG;ng=max(ng,abs(G-f))
   v.append(dO)
  df.append(q);dout.append(v)
 # Compare selected source points independently: baseline original step + homogeneous JumpResponse.
 check=None
 if abs(u-c.he[np.argmin(abs(c.he-u))])<1e-14 and int(np.argmin(abs(c.he-u))) in [63,99,918,974,1773]:
  aa=owner(u,yy,wj,j,a+eps*da,w+eps*dw);bb=owner(u,yy,wj,j,a-eps*da,w-eps*dw)
  oldfd=(aa[1]-bb[1])/(2*eps);gfd=(aa[0]-bb[0])/(2*eps)
  gnew=[];onew=[]
  for l in range(3):
   _,_,dG,dO=atomic_apply(s,a,w,da,dw,wj[l],np.zeros_like(wj[l]),mass[l,j]);onew.append(dO)
   if l==0:gnew=dG
  check=dict(u=float(u),stage=j,relative=float(np.linalg.norm(np.array(onew)-oldfd)/max(np.linalg.norm(oldfd),1e-300)),gas_abs=float(abs(gnew-gfd)))
 return f,o,gg,np.stack(oo,axis=-1),np.array(df),np.array(dout),nom,ng,check,basegap,res,gascheck
def run():
 c=context(128);ref=H/'goal_q3_128_-0.5.npz';z=np.load(ref);he=z['he'];N=128;assert len(he)==1774
 v=z['rows'][:,1:3].copy();v[:,1]/=3000;c.v=np.stack([np.interp(he,c.he,c.v[:,j]) for j in range(c.v.shape[1])],axis=1);c.he=he;nr=c.nr
 lam=-.5;eps=.001;m,mp,mm=[Map(c,x) for x in [lam,lam+eps,lam-eps]];events=Events(m);print('variational base gap',events.ode_base_gap,flush=True)
 from scipy.interpolate import CubicSpline
 checks_spline=[]
 for j in [0,10,22,31]:
  g=m.g[j];dx=events.moving[j].dx;q=(g.x[1:-2:31]+g.x[2:-1:31])/2;d=events.moving[j](q)
  for ep in [.003,.001,.0003]:
   gp=CubicSpline(g.x+ep*dx,m.D.x,extrapolate=False);gm=CubicSpline(g.x-ep*dx,m.D.x,extrapolate=False)
   fd=(gp(q)-gm(q))/(2*ep);checks_spline.append(dict(ray=j,eps=ep,max_abs=float(np.max(abs(fd-d))),relative=float(np.linalg.norm(fd-d)/max(np.linalg.norm(d),1e-300))))
 write('SPLINE_AUDIT.json',dict(rows=checks_spline,scope='represented knot motion only, y fixed, independent SciPy recomputation'))

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
 _WORK=(owner,events,eps,c);atomic_checks=[];atomic_base_gap=0.;atomic_gas_gap=0.;gas_checks=[];gas_base_gap=0.;gas_matrix_res=0.
 import concurrent.futures as cf,multiprocessing as mpctx
 with cf.ProcessPoolExecutor(max_workers=3,mp_context=mpctx.get_context('fork')) as pool:
  for i,r in enumerate(he[1:N+1],1):
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
   for f,o,gg,oo,gdf,gdo,nom,ng,ck,bgap,rres,gcheck in pool.map(stage_job,args):
    gas_base_gap=max(gas_base_gap,bgap);gas_matrix_res=max(gas_matrix_res,rres)
    if gcheck is not None:gas_checks.append(gcheck)
    F+=f;O+=o;Gs.append(gg);Os.append(oo);df+=gdf;do+=gdo
    atomic_base_gap=max(atomic_base_gap,nom);atomic_gas_gap=max(atomic_gas_gap,ng)
    if ck is not None:atomic_checks.append(ck)

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
 dy=np.array(dys);prior=P/'r118c4n_exact_spline_atomic'/'EXACT_HISTORY.npz';old=np.load(prior);assert np.array_equal(he[:N+1],old['u'][:N+1]);g=dy-old['dy'][:N+1]
 refs=[]
 for ep in [.003,.001,.0003]:
  for k,sg in enumerate([1,-1]):
   path=K/f'{"FD" if ep==.003 else "PREFIX_FD"}_{sg*ep:g}.npz';q=np.load(path);n=min(len(q['u']),N+1);assert np.array_equal(q['u'][:n],he[:n]);f=(q['y'][:n]-v[:n])/ep;err=f-dy[:n,k]
   refs.append(dict(eps=ep,direction=sg,steps=n-1,terminal=dy[n-1,k].tolist(),fd=f[-1].tolist(),max_gap=np.max(abs(err),axis=0).tolist(),source_sha=sha(path)))
 np.savez_compressed(D/'COMPOSED.npz',u=he[:N+1],y=v[:N+1],dy=dy,last=A[N-1],last_d=DA[:,N-1],limits=np.array(lims))
 out=dict(steps=N,seconds=time.monotonic()-t0,nominal_residual=resmax,min_positive=mi0,limiter_count=len(lims),gas_base_gap=gas_base_gap,gas_matrix_residual=gas_matrix_res,gas_checks=gas_checks,prior_direction_max_gap=np.max(abs(g),axis=0).tolist(),prior_direction_max=np.max(abs(old['dy'][:N+1]),axis=0).tolist(),terminal=dy[-1].tolist(),finite_refs=refs,prior_sha=sha(prior),baseline_sha=sha(ref),scope='128 actual steps of C4N event/retarded history, analytic abundance and temperature gas columns, fixed H, accepted baseline endpoints; not full 1773 steps or autonomous owner')
 write('COMPOSED.json',out);print(json.dumps(out),flush=True)
if __name__=='__main__':run()
