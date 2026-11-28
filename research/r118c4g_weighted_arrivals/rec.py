"""Weighted causal source-history arrivals and conservative diagnostic helium photon redistribution."""
from pathlib import Path
import sys,json,numpy as np,hashlib
from scipy.special import betainc,beta
from scipy.optimize import brentq
D=Path(__file__).resolve().parent;P=D.parent;F=P/'r118c4f_causal_mesh';E=P/'r118c4e_early_events';C4=P/'r118c4d_nested_history';B=P/'r118c4b_global_quadratic';W=P/'r118c3w_common_history'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(n,o):(D/n).write_text(json.dumps(o,indent=2)+'\n')
sys.path[:0]=[str(W),str(P/'r118c3x_three_moments'),str(D.parents[1]/'src')]
from common_base import context,Map,p,JumpResponse
def mesh():
 c=context(128);q=np.load(F/'causal_q3_128_0.npz');old=q['he'];rows=q['rows'];A=q['all_history'][:,0];base=np.load(B/'q3_128_0.npz')['he'];assert np.array_equal(c.he,base) and np.array_equal(old[np.searchsorted(old,base)],base)
 # At each actual source boundary: right start minus left end; initial incoming history zero.
 left=np.sum(A,axis=-1);right=np.sum(A*(-1.)**np.arange(A.shape[-1]),axis=-1);jump=np.r_[right[:1],right[1:]-left[:-1]]
 assert jump.shape==(len(old)-1,314)
 # Fixed gas/geometry scalar rate Jacobian via actual source operator unit responses at 9 snapshots.
 ids=np.unique(np.linspace(0,len(old)-1,9).astype(int));sens=[]
 for i in ids:
  ss,H,Tr=c.snap(float(old[i]),float(rows[i,1]),float(rows[i,2]),c.zero);jr=JumpResponse(ss,np.ones(c.nr),c.w)
  jj=np.array([jr.apply(np.broadcast_to(v,(c.nr,313)))[2] for v in np.eye(313)])
  rng=np.random.default_rng(11847+i);v=rng.normal(size=313);a=jr.apply(np.broadcast_to(v,(c.nr,313)))[2];b=jj@v;assert abs(a-b)<1e-11*max(1,abs(a),abs(b))
  sens.append(jj)
 sens=np.array(sens);absj=abs(jump[:,c.src]);mean_s=np.max(abs(sens),axis=0);source_rank=np.sum(absj*mean_s,axis=1);select=np.unique(np.r_[0,np.argsort(-source_rank,kind='stable')[:31]])
 # Event weights approximate scalar gas response, multiplied by physical ray weight at start.
 # All actual retarded knot splitting still performed by the owner, not just selected events.
 ev=[]
 for lam in [-.5,0.,.5]:
  m=Map(c,lam)
  for j in range(c.nr):
   f,g=m.f[j],m.g[j]
   aa=g(f(old[select])[:,None]+c.lr[None,:]);ir,ic=np.where(np.isfinite(aa)&(aa>old[0])&(aa<old[-1]));t=aa[ir,ic];srcidx=select[ir]
   ss=np.array([np.interp(tt,old[ids],abs(sens[:,ch])) for tt,ch in zip(t,ic)])
   weights=absj[srcidx,ic]*ss*c.w[j]
   ev.append(np.c_[t,weights,srcidx,ic,np.full(len(t),lam),np.full(len(t),j)])
 a=np.concatenate(ev);a=a[np.argsort(a[:,0],kind='stable')];t=a[:,0]
 d=np.load(F/'CAUSAL_DIFFERENCE.npz');assert np.array_equal(d['u'],base)
 even=np.interp(old,base,d['causal_even']-d['global_even']);odd=np.interp(old,base,d['causal_odd']-d['global_odd']);e=abs(np.diff(even));o=abs(np.diff(odd));score=e/max(e.sum(),1e-300)+o/max(o.sum(),1e-300)
 order=np.argsort(-score,kind='stable')[:96];insert=[];rr=[]
 maps={lam:Map(c,lam) for lam in [-.5,0.,.5]}
 for k in order:
  l,r=old[k:k+2];h=r-l;lo=np.searchsorted(t,l+.2*h);hi=np.searchsorted(t,r-.2*h,side='right')
  if hi>lo and np.max(a[lo:hi,1])>0:
   q0=a[lo:hi];v=q0[np.argmax(q0[:,1])];n,weight,src0,ch,lam,j=v;src0,ch,j=int(src0),int(ch),int(j);f=maps[float(lam)].f[j];err=abs(float(f(n))-float(f(old[src0]))-c.lr[ch]);assert err<1e-12
   r0=dict(index=int(k),time=float(n),source_index=src0,channel=ch,lam=float(lam),ray=j,weight=float(weight),forward_residual=float(err),kind='weighted')
  else:n=(l+r)/2;r0=dict(index=int(k),time=float(n),kind='midpoint')
  assert l+.199*h<n<r-.199*h;insert.append(n);rr.append(r0)
 he=np.sort(np.r_[old,insert]);assert np.all(np.diff(he)>0) and np.array_equal(he[np.searchsorted(he,old)],old) and max(np.diff(he))<min(c.lr)
 np.savez_compressed(D/'WEIGHTED_MESH.npz',he=he,old=old,source_indices=select,source_rank=source_rank,sensitivity=sens,sensitivity_u=old[ids],selected=np.array(order),insert=np.array(insert),score=score)
 write('MESH.json',dict(prior_steps=len(old)-1,steps=len(he)-1,weighted=sum(r['kind']=='weighted' for r in rr),midpoint=sum(r['kind']=='midpoint' for r in rr),event_candidates=len(a),selected_source_knots=len(select),selected_score_fraction=float(score[order].sum()/score.sum()),max_forward_residual=max([r['forward_residual'] for r in rr if r['kind']=='weighted'] or [0.]),min_spacing=float(min(np.diff(he))),min_lag=float(min(c.lr)),mesh_sha=hashlib.sha256(he.tobytes()).hexdigest(),source_history_sha=sha(F/'causal_q3_128_0.npz'),records=rr,scope='actual scalar outgoing history boundary jump and actual gas response magnitude; weights are scalar proxy for anisotropic response, 32 selected source knots and all channels/rays; shared mesh and all original source knot splits preserved'))
 print('weighted mesh',len(he)-1,rr[:2],flush=True)
def run(kind,lam):
 s=(F/'rec.py').read_text();s=s[:s.index('\ndef analyze():')];s=s.replace("F=P/'r118c4f_causal_mesh';","") if False else s
 # use prior C4F generator with the new mesh and new output prefix, without invoking its old mesh method.
 s=s.replace("D/'CAUSAL_MESH.npz'","D/'WEIGHTED_MESH.npz'").replace("'causal_'","'weighted_'")
 ns={'__file__':str(D/'rec.py'),'__name__':'c4g_owner'};exec(compile(s,str(F/'rec.py'),'exec'),ns);ns['run'](kind,lam)
def analyze():
 def pair(root,stem):
  za,zb=[np.load(root/f'PAIR_{stem}_{l:g}.npz')['rows'] for l in [-.5,.5]];assert np.array_equal(za[:,0],zb[:,0]);return za[:,0],(za[:,1]+zb[:,1])/.5,zb[:,1]-za[:,1]
 u,x,o=pair(D,'weighted_q3_128');v,y,p=pair(F,'causal_q3_128');t,z,q=pair(C4,'nested256_q3_128');base=np.load(B/'q3_128_0.npz')['he'];i=np.searchsorted(u,base);j=np.searchsorted(v,base);k=np.searchsorted(t,base);assert np.array_equal(u[i],base) and np.array_equal(v[j],base) and np.array_equal(t[k],base)
 rows=[json.loads((D/f'PAIR_weighted_q3_128_{l:g}.json').read_text()) for l in [-.5,.5]];assert rows[0]['mesh_sha256']==rows[1]['mesh_sha256']
 d=x[i]-z[k];d0=y[j]-z[k];j0=int(np.argmax(abs(d)));np.savez_compressed(D/'WEIGHTED_DIFFERENCE.npz',u=base,weighted_even=x[i],causal_even=y[j],global_even=z[k],weighted_odd=o[i],causal_odd=p[j],global_odd=q[k])
 out=dict(steps=len(u)-1,even=float(x[-1]),odd=float(o[-1]),global_even=float(z[-1]),global_odd=float(q[-1]),causal_even=float(y[-1]),causal_odd=float(p[-1]),max_cumulative_vs_global=float(max(abs(d))),prior_max_cumulative_vs_global=float(max(abs(d0))),even_endpoint_abs_vs_global=float(abs(d[-1])),prior_even_endpoint_abs_vs_global=float(abs(d0[-1])),odd_endpoint_abs_vs_global=float(abs(o[-1]-q[-1])),prior_odd_endpoint_abs_vs_global=float(abs(p[-1]-q[-1])),z_max_disagreement=float(np.expm1(-base[j0])),min_positive=min(r['min_stored_virtual_ratio'] for r in rows),max_direct_error=max(r['abs_disagreement'] for r in rows),cells=sum(r['cells_checked'] for r in rows),pairs=rows,scope='finite nested mesh with actual source-weighted arrivals; global 2266 comparator not continuum')
 write('WEIGHTED_SUMMARY.json',out);print(out,flush=True)
def helium():
 raw=np.load(F/'HELIUM_CHANNELS.npz');u=raw['u'];stage=raw['stage'];mask=(stage[:-1]=='HeII_RECOMBINATION')&(stage[1:]=='HeII_RECOMBINATION');net=raw['net_cell'][mask];a=np.exp((u[:-1]+u[1:])[mask]/2);en=raw['energy'];assert net.shape[1]==2
 n=np.sum(net,axis=0);x,w=np.polynomial.legendre.leggauss(96);x=(x+1)/2;w=w/2;rows=[];spectra={}
 threshold=13.598434599702;ae=np.exp(u[1:][mask][-1]);z_end=1/ae-1
 for m in [1,3,5]:
  dens=x**(m-1)*(1-x)**(m-1)/beta(m,m);weights=w*dens;assert abs(sum(weights)-1)<1e-13 and abs(weights@x-.5)<1e-13
  ee=(a[:,None]*en[0]*x[None,:]);nn=2*net[:,0,None]*weights[None,:];es=a*en[1];ns=net[:,1]
  expected_n=float(2*n[0]+n[1]);expected_e=float(np.sum(a*(net@en)));intrinsic=float(n@en)
  # analytic signed tail moments at emission, and at end of actual HeII history.
  def tail(lo):
   lo=np.clip(lo,0,1);p=1-betainc(m,m,lo);q=.5*(1-betainc(m+1,m,lo));return p,q
  pr,er=tail(threshold/en[0]);nr0=2*n[0]*pr+n[1]*(en[1]>threshold);er0=2*n[0]*en[0]*er+n[1]*en[1]*(en[1]>threshold)
  pr,er=tail(threshold*ae/(a*en[0]));nr_end=float(np.sum(2*net[:,0]*pr+net[:,1]*(es/ae>threshold)));e_end=float(np.sum(2*net[:,0]*en[0]*a/ae*er+net[:,1]*es/ae*(es/ae>threshold)))
  for bins in [256,512,1024]:
   center=np.geomspace(min(float(ee.min()),float(es.min()))*.99,max(float(ee.max()),float(es.max()))*1.01,bins);hist=np.zeros(bins)
   def deposit(e,q):
    e=e.ravel();q=q.ravel();i=np.searchsorted(center,e,side='right')-1;assert min(i)>=0 and max(i)<bins-1;t=(e-center[i])/(center[i+1]-center[i]);np.add.at(hist,i,q*(1-t));np.add.at(hist,i+1,q*t)
   deposit(ee,nn);deposit(es,ns)
   nerr=float(sum(hist)-expected_n);eerr=float(hist@center-expected_e);assert abs(nerr)<1e-12 and abs(eerr)<1e-13
   key=f'beta{m}_{bins}';spectra[key+'_E']=center;spectra[key+'_N']=hist
   # free-streaming present-day number spectral CDF is profile-dependent, even though energy fixed.
   rows.append(dict(profile=f'Beta({m},{m})',bins=bins,net_photons_per_H=expected_n,emission_energy_per_H=intrinsic,comoving_energy_per_H=expected_e,number_defect=nerr,energy_defect=eerr,above_H_threshold_emission_photons_per_H=float(nr0),above_H_threshold_emission_energy_per_H=float(er0),above_threshold_at_HeII_end_photons_per_H=nr_end,above_threshold_at_HeII_end_energy_per_H=e_end,possible_threshold_crossings_per_H=float(nr0-nr_end),z_end=float(z_end)))
 np.savez_compressed(D/'HELIUM_SPECTRAL_PROXY.npz',**spectra)
 write('HELIUM_SPECTRAL_PROXY.json',dict(rows=rows,source_sha=sha(F/'HELIUM_CHANNELS.npz'),scope='prescribed symmetric two-photon profile family and effective 2p line; actual signed effective event rates, collisionless redshift and conservative deposition; not physical HeI profile or feedback/absorption solver; threshold crossings are kinematic only'))
 print(rows[::3],flush=True)
if __name__=='__main__':
 if sys.argv[1]=='mesh':mesh()
 elif sys.argv[1]=='helium':helium()
 elif sys.argv[1]=='analyze':analyze()
 else:run(sys.argv[1],float(sys.argv[2]))
