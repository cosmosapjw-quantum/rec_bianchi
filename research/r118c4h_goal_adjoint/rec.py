"""Actual scalar retarded midpoint surrogate with adjoint, and goal-weighted shared mesh."""
from pathlib import Path
import sys,json,numpy as np,hashlib,time
from scipy.linalg import solve_banded
D=Path(__file__).resolve().parent;P=D.parent;G=P/'r118c4g_weighted_arrivals';F=P/'r118c4f_causal_mesh';C4=P/'r118c4d_nested_history';B=P/'r118c4b_global_quadratic';W=P/'r118c3w_common_history'
sys.path[:0]=[str(W),str(P/'r118c3x_three_moments'),str(D.parents[1]/'src')]
from common_base import context,Map,p,JumpResponse
from jump_response import LYA_FACT_CM3
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(n,o):(D/n).write_text(json.dumps(o,indent=2)+'\n')
def action(jr,d):
 a,b,g=jr.apply(d[None,:]);return (a+b)[0],g
def transpose(jr,l,lg):
 s=jr.s;active=s.Dtau>1e-30;tr=jr.tr[0];pi=jr.pi[0];eqbar=np.divide(-tr*l[:311],jr.x1*jr.gamma,out=np.zeros(311),where=(jr.gamma>0)&active)
 rbar=s.Tvr@eqbar+lg*s.Beta_s_inv/s.H_s_inv
 rbar+=np.array([(l[312]*np.exp(-1.8886508433247664/s.Tr_eV)+l[313]*np.exp(-2.5496786384884356/s.Tr_eV))/jr.x1,l[311]/(3*jr.x1)])
 vbar=np.zeros(311);vbar[:-1]+=eqbar[1:]*jr.vv[1,1:];vbar[1:]+=eqbar[:-1]*jr.vv[2,:-1]
 brbar=np.linalg.solve(jr.schur.T,rbar-jr.Z.T@vbar);zbar=vbar-s.Trv.T@brbar
 ab=jr.ab.copy();ab[0,1:]=jr.ab[2,:-1];ab[2,:-1]=jr.ab[0,1:];bvbar=solve_banded((1,1),ab,zbar,check_finite=False)
 ly=LYA_FACT_CM3*s.H_s_inv/(s.nH_cgs*jr.x1)
 return np.r_[np.where(active,(1-tr)*l[:311],l[:311])+jr.vv[0]*jr.x1*(1-pi)*bvbar,3*ly*jr.x1*brbar[1],3*ly*jr.x1*1.664786871919931*brbar[0]]
def mesh():
 c=context(128);q=np.load(G/'weighted_q3_128_0.npz');old=q['he'];rows=q['rows'];A=q['all_history'][:,0];N=len(old)-1;mid=(old[:-1]+old[1:])/2;dt=np.diff(old);src=c.src
 assert max(dt)<min(c.lr);Jidx=np.searchsorted(old,mid[:,None]-c.lr,side='right')-1
 assert np.all(Jidx<np.arange(N)[:,None])
 # Scale temperature coordinate to kelvin / 3000. Exact frozen midpoint approximation, not original weak-history derivative.
 scale=np.array([1.,3000.]);Ms=[];bs=[];OY=[];ops=[];doterr=[]
 rng=np.random.default_rng(11848)
 for i,u in enumerate(mid):
  xx,T=(rows[i,1:3]+rows[i+1,1:3])/2;k=Jidx[i];idx=np.maximum(k,0);frac=(u-c.lr-old[idx])/dt[idx];t=2*np.clip(frac,0,1)-1
  cc=A[idx,src];inc=np.polynomial.legendre.legval(t,cc.T,tensor=False);inc[k<0]=0
  def ev(x,T):
   s,H,Tr=c.snap(u,x,T,c.zero);r,o,_=p.step(s,np.ones(1),np.zeros((1,313)),np.ones(1));jr=JumpResponse(s,np.ones(1),np.ones(1));oo,g=action(jr,inc);return np.r_[r.dxHII_dln_a+g,o[0]+oo],jr,H,Tr
  val,jr,H,Tr=ev(xx,T);dx=(ev(xx+1e-6,T)[0]-ev(xx-1e-6,T)[0])/2e-6;dT=(ev(xx,T+.01)[0]-ev(xx,T-.01)[0])/.02
  h=dt[i];a=p.COMPTON_GAMMA_PER_T4_S_INV_K4*Tr**4/H;aa=a*xx/(1+xx+c.model.f_he);ax=a*(1+c.model.f_he)/(1+xx+c.model.f_he)**2
  J=np.array([[dx[0],dT[0]],[ax*(Tr-T),-2-aa]])*scale[None,:]/scale[:,None]
  E=np.linalg.inv(np.eye(2)-h*J/2);M=E@(np.eye(2)+h*J/2);b=E@np.array([h,0.])
  Oy=np.column_stack([dx[1:],dT[1:]*scale[1]]);Ms.append(M);bs.append(b);OY.append(Oy);ops.append(jr)
  if i%128==0:
   z=rng.normal(size=313);l=rng.normal(size=314);lg=float(rng.normal());a0,b0=action(jr,z);lhs=l@a0+lg*b0;rhs=transpose(jr,l,lg)@z;err=abs(lhs-rhs)/max(abs(lhs),abs(rhs),1e-300);doterr.append(err);assert err<1e-10
  if i%512==0:print('midpoint',i,flush=True)
 Ms=np.array(Ms);bs=np.array(bs);OY=np.array(OY);bar=np.zeros((N,314));ib=np.zeros((N,313));lb=np.array([1.,0.]);forcing=np.empty((N,2))
 for i in reversed(range(N)):
  v=OY[i].T@bar[i]/2;t=lb+v;forcing[i]=t;lb=Ms[i].T@t+v
  z=transpose(ops[i],bar[i],float(bs[i]@t));ib[i]=z;k=Jidx[i];m=k>=0;np.add.at(bar,(k[m],src[m]),z[m])
 # Exact duality within represented midpoint surrogate: independent forward tangent with additive forcing in the next gas state.
 v=rng.normal(size=(N,2));v[:,1]*=.01;v*=1e-9;out=np.zeros((N,314));y=np.zeros(2)
 for i in range(N):
  k=Jidx[i];m=k>=0;I=np.zeros(313);I[m]=out[k[m],src[m]];o,a=action(ops[i],I);yn=Ms[i]@y+bs[i]*a+v[i];out[i]=OY[i]@((y+yn)/2)+o;y=yn
 lhs=y[0];rhs=np.sum(forcing*v);dual=abs(lhs-rhs)/max(abs(lhs),abs(rhs),1e-300);assert dual<1e-8 and np.isfinite(ib).all()
 # Actual source boundary jumps, candidate arrival map, adjoint goal influence.
 jump=np.r_[np.sum(A[:1]*(-1.)**np.arange(A.shape[-1]),axis=-1),np.sum(A[1:]*(-1.)**np.arange(A.shape[-1]),axis=-1)-np.sum(A[:-1],axis=-1)]
 rank=np.sum(abs(jump[:,src])*np.max(abs(ib),axis=0),axis=1);select=np.unique(np.r_[0,np.argsort(-rank,kind='stable')[:31]])
 ev=[]
 for lam in [-.5,0.,.5]:
  m=Map(c,lam)
  for j in range(c.nr):
   f,g=m.f[j],m.g[j];aa=g(f(old[select])[:,None]+c.lr[None,:]);ir,ic=np.where(np.isfinite(aa)&(aa>old[0])&(aa<old[-1]));t=aa[ir,ic];sidx=select[ir];k=np.searchsorted(old,t)-1;k=np.clip(k,0,N-1)
   weights=abs(jump[sidx,src[ic]])*abs(ib[k,ic])*c.w[j]
   ev.append(np.c_[t,weights,sidx,ic,np.full(len(t),lam),np.full(len(t),j)])
 ev=np.concatenate(ev);ev=ev[np.argsort(ev[:,0],kind='stable')];times=ev[:,0];cell=np.clip(np.searchsorted(old,times)-1,0,N-1);w=np.zeros(N);np.maximum.at(w,cell,ev[:,1])
 d=np.load(G/'WEIGHTED_DIFFERENCE.npz');e=np.interp(old,d['u'],d['weighted_even']-d['global_even']);o=np.interp(old,d['u'],d['weighted_odd']-d['global_odd']);v=abs(np.diff(e));r=abs(np.diff(o));defect=v/max(v.sum(),1e-300)+r/max(r.sum(),1e-300)
 # Joint goal/defect rank, plus independent peak-defect coverage. Fixed before owner run.
 goal=defect*(w/max(w.max(),1e-300)+1e-4);first=list(np.argsort(-goal,kind='stable')[:48]);others=[k for k in np.argsort(-defect,kind='stable') if k not in first][:16];order=first+others
 insert=[];records=[]
 for k in order:
  l,r=old[k:k+2];h=r-l;i=np.searchsorted(times,l+.2*h);j=np.searchsorted(times,r-.2*h,side='right')
  if j>i and np.max(ev[i:j,1])>0:
   q=ev[i:j];t,w0,ss,ch,lam,ray=q[np.argmax(q[:,1])];rec=dict(index=int(k),time=float(t),weight=float(w0),source=int(ss),channel=int(ch),lam=float(lam),ray=int(ray),kind='goal')
  else:t=(l+r)/2;rec=dict(index=int(k),time=float(t),kind='midpoint')
  insert.append(t);records.append(rec)
 he=np.sort(np.r_[old,insert]);assert np.all(np.diff(he)>0) and np.array_equal(he[np.searchsorted(he,old)],old) and max(np.diff(he))<min(c.lr)
 np.savez_compressed(D/'GOAL_MESH.npz',he=he,old=old,adjoint_incoming=ib,adjoint_gas_forcing=forcing,source_rank=rank,selected=np.array(order),goal=goal,defect=defect)
 write('GOAL_MESH.json',dict(steps=len(he)-1,old_steps=N,weighted=sum(x['kind']=='goal' for x in records),records=records,source_knots=len(select),candidates=len(ev),dot_check=max(doterr),duality_relative=float(dual),adjoint_terminal_forward=float(lhs),adjoint_terminal_reverse=float(rhs),adjoint_norm=float(np.linalg.norm(ib)),mesh_sha=hashlib.sha256(he.tobytes()).hexdigest(),source_sha=sha(G/'weighted_q3_128_0.npz'),scope='frozen scalar implicit-midpoint tangent with piecewise-constant delayed perturbations and source-owned affine atomic operator; exact adjoint of this surrogate only; not full weak moment/limiter adjoint'))
 print('mesh',len(he)-1,'duality',dual,flush=True)
def run(kind,lam):
 s=(C4/'rec.py').read_text();a="he=np.empty(2*len(oldhe)-1);he[::2]=oldhe;he[1::2]=.5*(oldhe[:-1]+oldhe[1:]);assert np.all(np.diff(he)>0)"
 b="he=np.load(D/'GOAL_MESH.npz')['he'];assert np.array_equal(he[np.searchsorted(he,oldhe)],oldhe)"
 assert s.count(a)==1;s=s.replace(a,b).replace('nested256_','goal_')
 g={'__file__':str(D/'rec.py'),'__name__':'c4h_owner'};exec(compile(s,str(C4/'rec.py'),'exec'),g);g['run'](kind,lam)
def analyze():
 def pair(root,stem):
  za,zb=[np.load(root/f'PAIR_{stem}_{l:g}.npz')['rows'] for l in [-.5,.5]];assert np.array_equal(za[:,0],zb[:,0]);return za[:,0],(za[:,1]+zb[:,1])/.5,zb[:,1]-za[:,1]
 u,x,o=pair(D,'goal_q3_128');v,y,p0=pair(G,'weighted_q3_128');t,z,q=pair(C4,'nested256_q3_128');base=np.load(B/'q3_128_0.npz')['he'];i=np.searchsorted(u,base);j=np.searchsorted(v,base);k=np.searchsorted(t,base);assert np.array_equal(u[i],base) and np.array_equal(v[j],base) and np.array_equal(t[k],base)
 rows=[json.loads((D/f'PAIR_goal_q3_128_{l:g}.json').read_text()) for l in [-.5,.5]];assert rows[0]['mesh_sha256']==rows[1]['mesh_sha256']
 d=x[i]-z[k];d0=y[j]-z[k];np.savez_compressed(D/'GOAL_DIFFERENCE.npz',u=base,goal_even=x[i],weighted_even=y[j],global_even=z[k],goal_odd=o[i],weighted_odd=p0[j],global_odd=q[k])
 out=dict(steps=len(u)-1,even=float(x[-1]),odd=float(o[-1]),global_even=float(z[-1]),global_odd=float(q[-1]),prior_even=float(y[-1]),prior_odd=float(p0[-1]),max_cumulative_vs_global=float(max(abs(d))),prior_max_cumulative_vs_global=float(max(abs(d0))),even_endpoint_abs_vs_global=float(abs(d[-1])),prior_even_endpoint_abs_vs_global=float(abs(d0[-1])),odd_endpoint_abs_vs_global=float(abs(o[-1]-q[-1])),prior_odd_endpoint_abs_vs_global=float(abs(p0[-1]-q[-1])),min_positive=min(r['min_stored_virtual_ratio'] for r in rows),max_direct_error=max(r['abs_disagreement'] for r in rows),cells=sum(r['cells_checked'] for r in rows),pairs=rows,scope='actual fixed H quadratic retarded owner on goal-weighted nested mesh; prior global 2266 is finite comparator')
 write('GOAL_SUMMARY.json',out);print(out,flush=True)
if __name__=='__main__':
 if sys.argv[1]=='mesh':mesh()
 elif sys.argv[1]=='analyze':analyze()
 else:run(sys.argv[1],float(sys.argv[2]))
