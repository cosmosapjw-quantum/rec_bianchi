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
def run(mode,delta=0.):
 lam=-.5+(delta if mode!='tangent' else 0.);N=1773;c=context(128);ref=H/'goal_q3_128_-0.5.npz';z=np.load(ref);fullhe=z['he'];he=fullhe[:N+1];v=z['rows'][:N+1,1:3].copy();v[:,1]/=3000
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
 def thermal(u,y):
  x,T=y;HH=np.interp(u,c.ge,c.g['h'])*2.1842852410855023e-18;Tr=c.model.tcmb0_K*np.exp(-u)/3000
  sc=p.COMPTON_GAMMA_PER_T4_S_INV_K4*(Tr*3000)**4/HH;b=sc*x/(1+x+c.model.f_he);bx=sc*(1+c.model.f_he)/(1+x+c.model.f_he)**2
  return b*(Tr-T)-2*T,np.array([bx*(Tr-T),-b-2])
 for i,r in enumerate(he[1:],1):
  l=he[i-1];h=r-l;mid=(l+r)/2;U=m.mom3(i,l,r,A)
  if mode=='tangent':
   un,dU,ev,md=moving.integrate(i,l,r,A,DA);events+=ev;mindist=min(mindist,md)
   nominal=float(np.max(abs(un-U))/max(np.max(abs(U)),1e-300));assert nominal<1e-10,(i,nominal)
   if i in [128,512,918,919,960,1200,1773]:
    fd=(mp.mom3(i,l,r,A)-mm.mom3(i,l,r,A))/(2*geoep);base=m.mom3(i,l,r,DA);g=dU-base
    event_checks.append(dict(step=i,nominal_gap=nominal,moving_relative=float(np.linalg.norm(g-fd)/max(np.linalg.norm(fd),1e-300)),moving_norm=float(np.linalg.norm(g)),fd_norm=float(np.linalg.norm(fd)),events=ev,min_boundary_distance=md))
  for t,wt in zip(gl,gw):
   f=(t+1)/2;u=l+h*f;R0=m.t(u)-(u-c.lr);b=p._planck_difference(c.ef[None,:]/(p.KB_NATIVE_EV_K*c.model.tcmb0_K*np.exp(-u)),R0)
   for k in range(5):U[k]+=wt/2*b*f**k
   if mode=='tangent':
    _,dt=moving.td(u,0.);energy=c.ef[None,:]/(p.KB_NATIVE_EV_K*c.model.tcmb0_K*np.exp(-u))*np.exp(R0);occ=1/np.expm1(energy);db=-energy*occ*(1+occ)*dt
    for k in range(5):dU[k]+=wt/2*db*f**k
  w=ww(U);ang=[m.state(u) for u in [l,mid,r]]
  if mode=='tangent':
   y0,y1=v[i-1],v[i];assert np.array_equal(y,y0)
   O=np.zeros((3,nr,314));F=0.;Gs=[];Os=[];ops=[]
   dW=ww(dU);df=0.;do=np.zeros_like(O)
   for j,u in enumerate([l,mid,r]):
    c0=j/2;yy=(1-c0)*y0+c0*y1;f,o,jr=owner(u,yy,w[:,j],j,*ang[j]);F+=f;O+=o
    gg=[];oo=[]
    for k,ep in enumerate([1e-6,.01/3000]):
     dv=np.eye(2)[k]*ep;p0=owner(u,yy+dv,w[:,j],j,*ang[j]);m0=owner(u,yy-dv,w[:,j],j,*ang[j]);gg.append((p0[0]-m0[0])/(2*ep));oo.append((p0[1]-m0[1])/(2*ep))
    Gs.append(gg);Os.append(np.stack(oo,axis=-1))
    # Geometry parameter enters native rate weights and affine response, at fixed gas and incoming moments.
    gp=owner(u,yy,w[:,j],j,*mp.state(u));gm=owner(u,yy,w[:,j],j,*mm.state(u))
    df+=(gp[0]-gm[0])/(2*geoep);do+=(gp[1]-gm[1])/(2*geoep)
    for k in range(3):
     a,b,g0=jr.apply(dW[k,j]);do[k]+=a+b
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
 tag='TANGENT' if mode=='tangent' else f'FD_{delta:g}'
 ys=np.array(ys);obj=dict(mode=mode,delta=delta,steps=N,lam=lam,resmax=resmax,min_positive=mi0,limited=len(lims),seconds=time.monotonic()-t0,source_sha=sha(ref),final=ys[-1].tolist(),max_baseline_gap=float(np.max(abs(ys-v))) if mode=='tangent' else None,scope='full signed weak-history owner at lambda=-0.5, first-order derivative in lambda including geometry, moving GL5 events and active LP; local geometry derivatives from actual spline stencils, not reverse adjoint')
 if mode=='tangent':
  ex=z['limits'];ex=ex[ex[:,0]<=N];assert np.array_equal(np.array(lims)[:,:3],ex[:,[0,2,3]])
  obj.update(terminal_gradient=dy.tolist(),active=active,event_checks=event_checks,moving_events=events,min_event_boundary_distance=mindist,geometry_stencil=geoep)
  # Save only selected actual final history and tangent; actual event source data for separate local replay.
  np.savez_compressed(D/'TANGENT.npz',u=he,y=ys,dy=np.array(dys),last=A[-1],last_tangent=DA[-1],limits=np.array(lims))
 else:np.savez_compressed(D/(tag+'.npz'),u=he,y=ys,last=A[-1],limits=np.array(lims))
 write(tag+'.json',obj);print('DONE',tag,{k:v for k,v in obj.items() if k!='active'},flush=True)
def analyze():
 a=json.loads((D/'TANGENT.json').read_text());t=np.load(D/'TANGENT.npz');rows=[]
 for h in [.003]:
  m=np.load(D/f'FD_{-h:g}.npz');p=np.load(D/f'FD_{h:g}.npz');assert np.array_equal(m['u'],t['u']) and np.array_equal(p['u'],t['u'])
  dy=(p['y']-m['y'])/(2*h);d=t['dy'];dA=(p['last']-m['last'])/(2*h)
  row=dict(eps=h,terminal_FD=dy[-1].tolist(),terminal_gap=(dy[-1]-d[-1]).tolist(),max_history_gas_gap=np.max(abs(dy-d),axis=0).tolist(),final_history_relative=float(np.linalg.norm(dA-t['last_tangent'])/max(np.linalg.norm(t['last_tangent']),1e-300)),minus_limiter_count=len(m['limits']),plus_limiter_count=len(p['limits']),same_limiter_keys=bool(np.array_equal(m['limits'][:,:3],t['limits'][:,:3]) and np.array_equal(p['limits'][:,:3],t['limits'][:,:3])))
  rows.append(row)
 write('LAMBDA_TANGENT.json',dict(tangent=a,finite_difference=rows,scope='actual 1773-step signed lambda derivative with moving GL5 events and active LP directional replay; centered geometry stencils; no reverse adjoint or continuum proof'))
 print(rows,flush=True)
if __name__=='__main__':
 if sys.argv[1]=='analyze':analyze()
 else:
  mode=sys.argv[1];value=float(sys.argv[2]) if len(sys.argv)>2 else 0.
  pre=D/'PRECOMPUTED_FD.json';admitted=False
  if mode=='fd' and pre.is_file():
   import inspect
   for r in json.loads(pre.read_text()):
    if r['h']!=value or r['exit']!=0:continue
    tag=f'FD_{value:g}'
    assert r['run_function_sha']==hashlib.sha256(inspect.getsource(run).encode()).hexdigest()
    assert all(sha(D/(tag+'.'+e))==r[e+'_sha'] for e in ('json','npz'))
    assert sha(D/f'fd_parallel_{value:g}.log')==r['log_sha']
    print('REPLAY_ADMITTED actual parallel FD',r,flush=True);admitted=True;break
  if not admitted:run(mode,value)
