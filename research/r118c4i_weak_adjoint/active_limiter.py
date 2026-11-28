"""Replay actual signed weak-history up to first active positivity LP and audit its local active set."""
from pathlib import Path
import sys,json,numpy as np,time,hashlib
from numpy.polynomial.legendre import leggauss,legvander,legval,legder,legroots
from scipy.optimize import linprog
D=Path(__file__).resolve().parent;P=D.parent;H=P/'r118c4h_goal_adjoint';W=P/'r118c3w_common_history';Z=P/'r118c3z_refined_retarded'
sys.path[:0]=[str(W),str(P/'r118c3x_three_moments'),str(D.parents[1]/'src')]
from common_base import context,p,JumpResponse
from positive3 import reconstruct
ns={'__file__':str(Z/'quadratic_generated.py'),'__name__':'prior'};exec(compile((Z/'quadratic_generated.py').read_text(),str(Z/'quadratic_generated.py'),'exec'),ns);Map=ns['Map']
C=np.array([[1.,0.,0.],[-3.,6.,0.],[5.,-30.,30.]])
M=np.linalg.inv(C);mass=np.array([[1/(k+1)-3/(k+2)+2/(k+3),4/(k+2)-4/(k+3),2/(k+3)-1/(k+2)] for k in range(3)])
L=np.zeros((3,3,5))
for k in range(3):L[k,0,k:k+3]=[1,-3,2];L[k,1,k:k+3]=[0,4,-4];L[k,2,k:k+3]=[0,-1,2]
def local(O,fr,expected):
 # Normalize to the exact original LP scale, keeping normalization branch fixed.
 c=C@O;c[0]+=fr;scale=max(np.max(abs(c)),fr);x=c/scale;f=fr/scale
 # reproduce actual LP and adaptive grid additions
 def lp(x):
  grid=np.linspace(-1,1,65)
  for it in range(8):
   V=legvander(grid,6);g=V[:,:3]@x;A=np.c_[-V[:,3:],V[:,3:]]
   r=linprog(np.ones(8),A_ub=A,b_ub=g-1e-10,bounds=(0,None),method='highs')
   if not r.success:return None
   h=r.x[:4]-r.x[4:];co=np.r_[x,h];roots=legroots(legder(co));roots=roots.real[(abs(roots.imag)<1e-10)&(abs(roots.real)<1)];zz=np.r_[-1,1,roots];vv=legval(zz,co)
   if vv.min()>0:return co,grid,A,r
   grid=np.unique(np.r_[grid,zz[vv<=0]])
  return None
 r=lp(x);assert r is not None
 co,grid,A,rr=r;assert np.max(abs(co[3:]*scale-expected[3:]))<1e-9*scale
 support=np.flatnonzero(rr.x>1e-9);tight=np.flatnonzero(abs(rr.ineqlin.residual)<1e-8);V=legvander(grid,6);AA=A[np.ix_(tight,support)];rank=int(np.linalg.matrix_rank(AA))
 rows=[];maxi=int(np.argmax(abs(x))) if max(abs(x))>f else -1
 for k in range(3):
  if k==maxi:continue
  v=np.eye(3)[k];rhs=V[tight,:3]@v
  dh=np.linalg.lstsq(AA,rhs,rcond=None)[0] if len(support) else np.empty(0);s=np.zeros(8);s[support]=dh;pred=s[:4]-s[4:]
  for eps in [1e-6,1e-7,1e-8]:
   a,b=lp(x+eps*v),lp(x-eps*v)
   if a is None or b is None:rows.append(dict(k=k,eps=eps,status='INFEASIBLE'));continue
   p=(a[0][3:]-co[3:])/eps;m=(co[3:]-b[0][3:])/eps
   rows.append(dict(k=k,eps=eps,status='OK',one_sided_gap=float(np.linalg.norm(p-m)),frozen_prediction_gap=float(np.linalg.norm((p+m)/2-pred)),same_grid=bool(np.array_equal(a[1],grid) and np.array_equal(b[1],grid)),same_support=bool(np.array_equal(np.flatnonzero(a[3].x>1e-9),support) and np.array_equal(np.flatnonzero(b[3].x>1e-9),support)),linear_constraint_residual=float(np.linalg.norm(AA@dh-rhs)),pred=pred.tolist(),forward=p.tolist(),backward=m.tolist()))
 return dict(scale=float(scale),normalized_full=x.tolist(),normalized_fr=float(f),reproduction_relative=float(np.max(abs(co[3:]*scale-expected[3:]))/scale),grid_points=len(grid),support=support.tolist(),tight=tight.tolist(),rank=rank,rows=rows)
def main():
 lam=float(sys.argv[1]) if len(sys.argv)>1 else -.5;c=context(128);z=np.load(H/f'goal_q3_128_{lam:g}.npz');he=z['he'];v=z['rows'];expected=z['limits'];assert len(expected)>0
 c.v=np.stack([np.interp(he,c.he,c.v[:,j]) for j in range(c.v.shape[1])],axis=1);c.he=he
 nr=c.nr;N=len(he)-1;A=np.zeros((N,nr,314,7));m=Map(c,lam);gl,gw=leggauss(5);mx=0.;tm=time.monotonic()
 for i,r in enumerate(he[1:],1):
  l=he[i-1];h=r-l;mid=(l+r)/2;U=m.mom3(i,l,r,A)
  for t,wt in zip(gl,gw):
   f=(t+1)/2;u=l+h*f;R0=m.t(u)-(u-c.lr);g=p._planck_difference(c.ef[None,:]/(p.KB_NATIVE_EV_K*c.model.tcmb0_K*np.exp(-u)),R0)
   for k in range(5):U[k]+=wt/2*g*f**k
  O=np.zeros((3,nr,314));F=0.;WW=np.einsum('kjm,mrc->kjrc',L,U)
  for j,(u,y) in enumerate([(l,v[i-1,1:3]),(mid,(v[i-1,1:3]+v[i,1:3])/2),(r,v[i,1:3])]):
   s,HH,Tr=c.snap(u,*y,c.zero);a,w=m.state(u);rr,o,_=p.step(s,a,np.zeros((nr,313)),w);jr=JumpResponse(s,a,w)
   for k in range(3):
    aa,b,gg=jr.apply(WW[k,j]);O[k]+=mass[k,j]*o+aa+b
    if k==0:F+=mass[k,j]*rr.dxHII_dln_a+gg
  mx=max(mx,abs(v[i,1]-v[i-1,1]-h*F));fr=1/np.expm1(c.tab.energy_eV/(p.KB_NATIVE_EV_K*c.model.tcmb0_K*np.exp(-r)));co,ls,mi=reconstruct(O,fr);A[i-1]=co
  if i%256==0:print('signed replay',i,'residual',mx,flush=True)
  if ls:
   ex=expected[expected[:,0]==i];assert len(ex)==len(ls) and np.array_equal(np.array(ls)[:,:2],ex[:,2:4])
   rows=[]
   for e in ls:
    k,j=map(int,e[:2]);res=local(O[:,k,j],fr[j],co[k,j]);rows.append(dict(ray=k,channel=j,actual_limit_row=e,**res))
   np.savez_compressed(D/'ACTIVE_LIMITER_INPUT.npz',O=O,fr=fr,co=co,step=np.array(i),lam=np.array(lam))
   obj=dict(lam=lam,step=i,expected_first_step=int(expected[0,0]),u=float(r),n_limited=len(ls),max_gas_replay_residual=float(mx),seconds=time.monotonic()-tm,rows=rows,source_sha=hashlib.sha256((H/f'goal_q3_128_{lam:g}.npz').read_bytes()).hexdigest(),scope='actual signed owner history replay using stored accepted gas endpoints through first active positivity LP; local normalized coefficient derivatives with fixed active grid and LP support; no full signed history adjoint')
   (D/'ACTIVE_LIMITER.json').write_text(json.dumps(obj,indent=2)+'\n');print('ACTIVE',obj,flush=True);return
 raise AssertionError('no active limiter found')
if __name__=='__main__':main()

