"""Exact scalar weak-history moment map, implicit stage tangent and reverse adjoint.
The scalar branch has no active positivity limiter; active signed branches remain distinct."""
from pathlib import Path
import sys,json,numpy as np,hashlib,time
from scipy.optimize import brentq
from numpy.polynomial.legendre import leggauss,legval,legvander
D=Path(__file__).resolve().parent;P=D.parent;H=P/'r118c4h_goal_adjoint';W=P/'r118c3w_common_history'
sys.path[:0]=[str(W),str(P/'r118c3x_three_moments'),str(D.parents[1]/'src')]
from common_base import context,p,JumpResponse
from positive3 import reconstruct
g={'__file__':str(H/'rec.py'),'__name__':'prior'};exec(compile((H/'rec.py').read_text(),str(H/'rec.py'),'exec'),g);action,transpose=g['action'],g['transpose']
def write(n,o):(D/n).write_text(json.dumps(o,indent=2)+'\n')
R=np.array([[1.,0.,0.],[-3.,6.,0.],[5.,-30.,30.]])
C=np.array([0.,.5,1.]);mass=np.array([[1/(k+1)-3/(k+2)+2/(k+3),4/(k+2)-4/(k+3),2/(k+3)-1/(k+2)] for k in range(3)])
L=np.zeros((3,3,5))
for k in range(3):L[k,0,k:k+3]=[1,-3,2];L[k,1,k:k+3]=[0,4,-4];L[k,2,k:k+3]=[0,-1,2]
def main():
 c=context(128);raw=np.load(H/'goal_q3_128_0.npz');he=raw['he'];A=raw['all_history'][:,0,:];y=raw['rows'][:,1:3]/[1,3000];N=len(he)-1;assert A.shape==(N,314,7) and np.max(abs(A[...,3:]))==0 and len(raw['limits'])==0
 h=np.diff(he);assert max(h)<min(c.lr);src=c.src;gl,gw=leggauss(5);maps=[]
 # Exact affine scalar ray map; split receiving cells at translated source knots.
 for i in range(N):
  l,r=he[i:i+2];span=r-l;u=np.full(313,l);ids=[];chs=[];vals=[]
  for z0 in range(100):
   active=u<r
   if not active.any():break
   j=np.searchsorted(he,u-c.lr+2e-14,side='right')-1;k=np.clip(j,0,N-1);cross=he[np.clip(j+1,0,N)]+c.lr;end=np.where(active,np.minimum(r,cross),u);dt=end-u
   assert np.all(dt[active]>0),(i,z0)
   m=active&(j>=0);ch=np.flatnonzero(m);jj=j[m];assert np.all(jj<i)
   if len(ch):
    xx=u[ch,None]+(gl+1)*dt[ch,None]/2;v=(xx-l)/span;t=2*np.clip((xx-c.lr[ch,None]-he[jj,None])/h[jj,None],0,1)-1
    leg=legvander(t,2);power=v[...,None]**np.arange(5);weight=gw[None,:]*dt[ch,None]/(2*span);w=np.einsum('na,nak,naj->nkj',weight,power,leg)
    ids.append(jj);chs.append(ch);vals.append(w)
   u=end
  else:raise RuntimeError('event segmentation cap')
  maps.append((np.concatenate(ids) if ids else np.empty(0,int),np.concatenate(chs) if chs else np.empty(0,int),np.concatenate(vals) if vals else np.empty((0,5,3))))
 def inc(i,hist):
  ids,ch,w=maps[i];U=np.zeros((313,5));np.add.at(U,ch,np.einsum('nkj,nj->nk',w,hist[ids,src[ch]]));return U.T
 def scatter(i,bar,d):
  ids,ch,w=maps[i];q=np.einsum('nkj,nk->nj',w,d.T[ch]);np.add.at(bar,(ids,src[ch]),q)
 def owner(u,yy,ww,j):
  xx,T=yy*np.array([1.,3000.]);s,HH,Tr=c.snap(u,xx,T,c.zero);r,o,_=p.step(s,np.ones(1),np.zeros((1,313)),np.ones(1));jr=JumpResponse(s,np.ones(1),np.ones(1))
  oo=[];gg=None
  for k in range(3):
   a,b=action(jr,ww[k]);oo.append(mass[k,j]*o[0]+a)
   if k==0:gg=mass[0,j]*r.dxHII_dln_a+b
  return float(gg),np.array(oo),jr
 def thermal(mid,yy):
  x,T=yy;u=mid;HH=np.interp(u,c.ge,c.g['h'])*2.1842852410855023e-18;Tr=c.model.tcmb0_K*np.exp(-u)/3000;scale=p.COMPTON_GAMMA_PER_T4_S_INV_K4*(Tr*3000)**4/HH;B=scale*x/(1+x+c.model.f_he);Bx=scale*(1+c.model.f_he)/(1+x+c.model.f_he)**2
  return B*(Tr-T)-2*T,np.array([Bx*(Tr-T),-B-2])
 M=[];inv=[];op=[];Ograd=[];maxres=0.;maxO=0.;maxOp=0.;dot=[];rng=np.random.default_rng(11849);t0=time.monotonic();nominal=[]
 for i in range(N):
  l,r=he[i:i+2];dt=h[i];mid=(l+r)/2;U=inc(i,A[...,:3]);ww=np.einsum('kjm,mc->kjc',L,U)
  y0,y1=y[i:i+2];gg=0.;O=np.zeros((3,314));Gs=[];Os=[];js=[]
  for j,u in enumerate([l,mid,r]):
   yy=(1-C[j])*y0+C[j]*y1;w=ww[:,j];gg0,o,jr=owner(u,yy,w,j);gg+=gg0;O+=o;js.append(jr)
   ds=[];es=[]
   for k,eps in enumerate([1e-6,.01/3000]):
    v=np.eye(2)[k]*eps;gp,op0,_=owner(u,yy+v,w,j);gm,om0,_=owner(u,yy-v,w,j);ds.append((gp-gm)/(2*eps));es.append((op0-om0)/(2*eps))
   Gs.append(ds);Os.append(np.stack(es,axis=-1))
  th,thj=thermal(mid,(y0+y1)/2);Gs=np.array(Gs);G0=np.stack([(1-C)@Gs,thj/2]);G1=np.stack([C@Gs,thj/2]);a=np.linalg.inv(np.eye(2)-dt*G1);b=a@(np.eye(2)+dt*G0)
  M.append(b);inv.append(a);op.append(js);Ograd.append(Os);res=y1-y0-dt*np.array([gg,th]);maxres=max(maxres,float(np.max(abs(res))))
  co=np.einsum('ak,kc->ca',R,O);err=np.max(abs(co-A[i,:,:3]));norm=max(np.max(abs(A[i,:,:3])),1e-300);maxO=max(maxO,float(err));maxOp=max(maxOp,float(err/norm))
  if i%256==0:
   da=rng.normal(size=(N,314,3))*1e-9;z=rng.normal(size=(5,313));q=inc(i,da);b0=np.zeros_like(da);scatter(i,b0,z);a0=float(np.sum(q*z));bb=float(np.sum(da*b0));e=abs(a0-bb)/max(abs(a0),abs(bb),1e-300);dot.append(e);assert e<1e-11
   print('weak',i,'res',maxres,'mom_rel',maxOp,flush=True)
 M=np.array(M);inv=np.array(inv);Ograd=np.array(Ograd)
 # Scalar mapped history differs by native inverse-map floating rounding only; report measured parity, not bitwise.
 assert maxres<1e-12 and maxOp<1e-7,(maxres,maxOp)
 def forward(ini,force,external=None):
  hist=np.zeros((N,314,3));ys=np.empty((N+1,2));ys[0]=ini
  for i in range(N):
   U=inc(i,hist)
   if external is not None:U+=external[i]
   w=np.einsum('kjm,mc->kjc',L,U);gas=0.;dO=np.zeros((3,314));yy=ys[i]
   for j in range(3):gas+=action(op[i][j],w[0,j])[1]
   yn=M[i]@yy+inv[i]@np.array([h[i]*gas,0.])+force[i];ys[i+1]=yn
   for j in range(3):
    dz=(1-C[j])*yy+C[j]*yn
    for k in range(3):dO[k]+=Ograd[i,j,k]@dz+action(op[i][j],w[k,j])[0]
   hist[i]=np.einsum('ak,kc->ca',R,dO)
  return ys,hist
 def reverse():
  bar=np.zeros((N,314,3));lam=np.array([1.,0.]);forcing=np.empty((N,2));inbar=np.empty((N,5,313))
  for i in reversed(range(N)):
   Obar=np.einsum('ak,ca->kc',R,bar[i]);left=np.zeros(2);right=lam.copy();Ubar=np.zeros((5,313))
   for j in range(3):
    v=np.einsum('kci,kc->i',Ograd[i,j],Obar);left+=(1-C[j])*v;right+=C[j]*v
    for k in range(3):Ubar+=L[k,j,:,None]*transpose(op[i][j],Obar[k],0.)[None,:]
   forcing[i]=right;v=inv[i].T@right
   for j in range(3):Ubar+=L[0,j,:,None]*transpose(op[i][j],np.zeros(314),h[i]*v[0])[None,:]
   inbar[i]=Ubar;scatter(i,bar,Ubar);lam=left+M[i].T@right
  return lam,forcing,inbar
 la,bf,bi=reverse();f=rng.normal(size=(N,2))*1e-10;f[:,1]*=.01;ini=np.array([1e-8,2e-10]);ext=np.zeros((N,5,313))
 # physically small random incoming source perturbation in a few channels, independent from gas force
 for i in rng.choice(N,32,replace=False):ext[i,:,rng.integers(0,313)]=rng.normal(size=5)*1e-30
 yy,_=forward(ini,f,ext);lhs=yy[-1,0];rhs=la@ini+np.sum(bf*f)+np.sum(bi*ext);duality=abs(lhs-rhs)/max(abs(lhs),abs(rhs),1e-300);assert duality<1e-8
 init_resp=[]
 for j in range(2):
  z,_=forward(np.eye(2)[j],np.zeros((N,2)));init_resp.append(float(z[-1,0]))
 assert np.linalg.norm(np.array(init_resp)-la)<1e-8*max(np.linalg.norm(la),1e-300)
 # Independent nonlinear replay of exact weak scalar branch, with actual original source and reconstruction.
 def nonlinear(ini):
  yy=y[0]+ini;hist=np.zeros((N,314,3));Y=[yy.copy()];mr=1e99;maxroot=0.;lim=0
  for i in range(N):
   l,r=he[i:i+2];mid=(l+r)/2;dt=h[i];U=inc(i,hist);w=np.einsum('kjm,mc->kjc',L,U);a=owner(l,yy,w[:,0],0)
   def trial(dx,ret=False):
    xm=yy[0]+dx/2;T0=yy[1];HH=np.interp(mid,c.ge,c.g['h'])*2.1842852410855023e-18;Tr=c.model.tcmb0_K*np.exp(-mid)/3000;sc=p.COMPTON_GAMMA_PER_T4_S_INV_K4*(Tr*3000)**4/HH;B=sc*xm/(1+xm+c.model.f_he);T=T0+dt*(B*(Tr-T0)-2*T0)/(1+dt*(2+B)/2);yn=np.array([yy[0]+dx,T]);b=owner(mid,(yy+yn)/2,w[:,1],1);cc=owner(r,yn,w[:,2],2);res=dx-dt*(a[0]+b[0]+cc[0]);return (res,yn,a[1]+b[1]+cc[1]) if ret else res
   width=max(1e-4,4*abs(y[i+1,0]-y[i,0]));dx=brentq(trial,max(-width,-.99*yy[0]),min(width,.99*(1-yy[0])),xtol=1e-19,rtol=1e-14);res,yn,O=trial(dx,True);fr=1/np.expm1(c.tab.energy_eV/(p.KB_NATIVE_EV_K*c.model.tcmb0_K*np.exp(-r)));co,ls,mi=reconstruct(O[:,None,:],fr);lim+=len(ls);assert len(ls)==0
   hist[i]=co[0,:,:3];yy=yn;Y.append(yy.copy());maxroot=max(maxroot,abs(res));mr=min(mr,mi)
   if i%512==0:print('replay',float(ini[0]),i,flush=True)
  return np.array(Y),dict(perturbation=ini.tolist(),min_positive=mr,maxroot=maxroot,limited=lim)
 # matched scalar replay and centered perturbation of initial x; same explicit source clock and interpolation.
 yp=[]
 for x0 in [0.,-1e-6,1e-6]:
  z,r0=nonlinear(np.array([x0,0.]));yp.append(z);nominal.append(r0)
 fd=(yp[2][-1,0]-yp[1][-1,0])/2e-6;replay_gap=float(np.max(abs(yp[0]-y)))
 assert replay_gap<1e-9
 # Active limiter audit: actual source-shaped scalar cell rescaled with manufactured moments, not a claim about signed branch.
 # Preserve positivity constraints and test directional finite differences along branch.
 active=[]
 for j in [0,77,155,233,310]:
  # Full polynomial with positive mean, negative quadratic minimum; LP may legitimately reject.
  fr=np.ones(311);O=np.zeros((3,1,314));O[0,0,j]=1.;O[1,0,j]=.5;O[2,0,j]=.4
  # use a synthetic full history near the admissible moment cone; sample several c2.
  for c2 in [4.1,4.2,4.5,5.]:
   O[2,0,j]=1/3+c2/30
   try:
    co,ls,mi=reconstruct(O,fr)
    if not ls:continue
    eps=1e-7;v=np.zeros_like(O);v[0,0,j]=1;v[1,0,j]=.5;v[2,0,j]=1/3
    plus,l1,m1=reconstruct(O+eps*v,fr);minus,l2,m2=reconstruct(O-eps*v,fr);dp=(plus-co)/eps;dm=(co-minus)/eps
    active.append(dict(channel=j,c2=c2,limited=len(ls),min_ratio=mi,one_sided_gap=float(np.linalg.norm(dp-dm)),plus_limited=len(l1),minus_limited=len(l2),moment_preservation=float(np.linalg.norm(np.einsum('ka,ca->kc',np.linalg.inv(R),dp[0,:,:3])-v[:,0]))));break
   except ValueError:continue
 np.savez_compressed(D/'WEAK_ADJOINT.npz',u=he,initial_gradient=la,gas_forcing=bf,incoming_adjoint=bi,baseline_replay=yp[0],initial_minus=yp[1],initial_plus=yp[2])
 write('WEAK_ADJOINT.json',dict(steps=N,source_sha=hashlib.sha256((H/'goal_q3_128_0.npz').read_bytes()).hexdigest(),max_nominal_residual=maxres,max_moment_abs=maxO,max_moment_relative=maxOp,max_map_transpose=max(dot),duality_relative=float(duality),terminal_forward=float(lhs),terminal_adjoint=float(rhs),initial_gradient=la.tolist(),initial_x_FD=float(fd),initial_x_FD_gap=float(abs(fd-la[0])),baseline_replay_max_scaled_gap=replay_gap,nonlinear_runs=nominal,active_limiter_synthetic_audit=active,seconds=time.monotonic()-t0,scope='actual scalar weak-history 5 receiving moments, 3-stage implicit gas and original outgoing moment reconstruction, branch inactive; affine scalar delay map analytically aligned; active LP audit synthetic and not full signed-branch adjoint'))
 print('RESULT',json.loads((D/'WEAK_ADJOINT.json').read_text()),flush=True)
if __name__=='__main__':main()
