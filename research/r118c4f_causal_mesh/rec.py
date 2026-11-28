"""C4F actual causal ray-delay mesh and primordial helium effective emission-rate decomposition."""
from pathlib import Path
import sys,json,numpy as np,hashlib,math
D=Path(__file__).resolve().parent;P=D.parent;E=P/'r118c4e_early_events';C4=P/'r118c4d_nested_history';B=P/'r118c4b_global_quadratic';W=P/'r118c3w_common_history'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(n,o):(D/n).write_text(json.dumps(o,indent=2)+'\n')
sys.path[:0]=[str(W),str(P/'r118c3x_three_moments'),str(D.parents[1]/'src')]
from common_base import context,Map
def mesh():
 c=context(128);old=np.load(E/'early4_q3_128_0.npz')['he'];base=np.load(B/'q3_128_0.npz')['he'];assert np.array_equal(c.he,base);assert np.array_equal(old[np.searchsorted(old,base)],base)
 ed=np.load(E/'EARLY_DIFFERENCE.npz');assert np.array_equal(ed['u'],base)
 def pair(root,stem):
  z0,z1=[np.load(root/f'PAIR_{stem}_{l:g}.npz')['rows'] for l in [-.5,.5]];assert np.array_equal(z0[:,0],z1[:,0]);return z0[:,0],z1[:,1]-z0[:,1]
 u,o=pair(E,'early4_q3_128');v,g=pair(C4,'nested256_q3_128');assert np.array_equal(u,old)
 # Use prior numerical defect only to rank candidate cells, never to infer a true local truncation error.
 de=np.interp(old,base,ed['early_minus_global']);do=o-np.interp(old,v,g);score=abs(np.diff(de))+.5*abs(np.diff(do));order=np.argsort(-score,kind='stable')[:96]
 evs=[]
 # First generation starts at the zero incoming-history boundary. Second-generation kinematic candidates
 # use successive positive lags on the same ray; not all transitions necessarily have nonzero coupling.
 for lam in [-.5,0.,.5]:
  m=Map(c,lam)
  for j in range(c.nr):
   f,g0=m.f[j],m.g[j];x=float(f(old[0]))
   a=g0(x+c.lr);b=g0(x+c.lr[:,None]+c.lr[None,:]);a=a[np.isfinite(a)];b=b[np.isfinite(b)]
   for gen,vals in [(1,a),(2,b)]:
    vals=vals[(vals>old[0])&(vals<old[-1])]
    if len(vals):evs.append(np.c_[vals,np.full(len(vals),gen),np.full(len(vals),lam),np.full(len(vals),j)])
 ev=np.concatenate(evs);ev=ev[np.argsort(ev[:,0],kind='stable')];t=ev[:,0];insert=[];rows=[]
 for k in order:
  l,r=old[k:k+2];h=r-l;i=np.searchsorted(t,l+.25*h);j=np.searchsorted(t,r-.25*h,side='right')
  if j>i:
   # First-generation events take priority; otherwise nearest second-generation kinematic candidate.
   sub=ev[i:j];first=sub[sub[:,1]==1];q=first if len(first) else sub;q=q[np.argmin(abs(q[:,0]-(l+r)/2))];n=float(q[0]);gen=int(q[1]);lam=float(q[2]);ray=int(q[3])
  else:n=(l+r)/2;gen=0;lam=None;ray=None
  assert l+.249*h<n<r-.249*h;insert.append(n);rows.append(dict(index=int(k),time=n,z=float(np.expm1(-n)),generation=gen,lam=lam,ray=ray,defect_score=float(score[k])))
 he=np.sort(np.r_[old,insert]);assert np.all(np.diff(he)>0) and np.array_equal(he[np.searchsorted(he,old)],old) and max(np.diff(he))<min(c.lr)
 np.savez_compressed(D/'CAUSAL_MESH.npz',he=he,old=old,base=base,selected=np.array(order),insert=np.array(insert),score=score)
 write('MESH.json',dict(prior_steps=len(old)-1,steps=len(he)-1,selected=len(rows),first=sum(r['generation']==1 for r in rows),second=sum(r['generation']==2 for r in rows),midpoint=sum(r['generation']==0 for r in rows),event_candidates=len(ev),min_spacing=float(min(np.diff(he))),max_step=float(max(np.diff(he))),min_lag=float(min(c.lr)),mesh_sha=hashlib.sha256(he.tobytes()).hexdigest(),old_sha=sha(E/'early4_q3_128_0.npz'),records=rows,scope='subset of kinematic first/second generation arrivals selected on prior numerical defect; actual retarded source knot splitting retained for all ray/channels; not all candidates necessarily nonzero discontinuities'))
 print('mesh',len(he)-1,[(i,sum(r['generation']==i for r in rows)) for i in [0,1,2]],flush=True)
def run(kind,lam):
 src=(C4/'rec.py').read_text();a="he=np.empty(2*len(oldhe)-1);he[::2]=oldhe;he[1::2]=.5*(oldhe[:-1]+oldhe[1:]);assert np.all(np.diff(he)>0)"
 b="he=np.load(D/'CAUSAL_MESH.npz')['he'];assert np.array_equal(he[np.searchsorted(he,oldhe)],oldhe)"
 assert src.count(a)==1;src=src.replace(a,b).replace('nested256_','causal_')
 g={'__file__':str(D/'rec.py'),'__name__':'c4f_owner'};exec(compile(src,str(C4/'rec.py'),'exec'),g);g['run'](kind,lam)
def analyze():
 rows={k:json.loads((D/f'PAIR_causal_q3_128_{l:g}.json').read_text()) for k,l in [('minus',-.5),('plus',.5)]};a,b=rows['minus'],rows['plus'];assert a['mesh_sha256']==b['mesh_sha256']
 old=json.loads((E/'EARLY_SUMMARY.json').read_text());gl=json.loads((C4/'NESTED_SUMMARY.json').read_text())
 def pair(root,stem):
  za,zb=[np.load(root/f'PAIR_{stem}_{l:g}.npz')['rows'] for l in [-.5,.5]];assert np.array_equal(za[:,0],zb[:,0]);return za[:,0],(za[:,1]+zb[:,1])/.5,zb[:,1]-za[:,1]
 u,x,o=pair(D,'causal_q3_128');v,y,p=pair(E,'early4_q3_128');t,z,q=pair(C4,'nested256_q3_128');base=np.load(B/'q3_128_0.npz')['he'];i=np.searchsorted(u,base);j=np.searchsorted(v,base);k=np.searchsorted(t,base);assert np.array_equal(u[i],base) and np.array_equal(v[j],base) and np.array_equal(t[k],base)
 d=x[i]-z[k];d0=y[j]-z[k];j0=int(np.argmax(abs(d)));np.savez_compressed(D/'CAUSAL_DIFFERENCE.npz',u=base,causal_even=x[i],early_even=y[j],global_even=z[k],causal_odd=o[i],early_odd=p[j],global_odd=q[k])
 out=dict(pairs=rows,steps=a['steps'],even=(a['delta_x']+b['delta_x'])/.5,odd=b['delta_x']-a['delta_x'],early_even=old['even'],early_odd=old['odd'],global_even=gl['even'],global_odd=gl['odd'],max_cumulative_vs_global=float(max(abs(d))),previous_max_cumulative_vs_global=float(max(abs(d0))),z_max_disagreement=float(np.expm1(-base[j0])),even_endpoint_abs_vs_global=float(abs(d[-1])),early_endpoint_abs_vs_global=float(abs(d0[-1])),odd_endpoint_abs_vs_global=float(abs(o[-1]-q[-1])),early_odd_endpoint_abs_vs_global=float(abs(p[-1]-q[-1])),min_positive=min(a['min_stored_virtual_ratio'],b['min_stored_virtual_ratio']),max_direct_error=max(a['abs_disagreement'],b['abs_disagreement']),cells=a['cells_checked']+b['cells_checked'],scope='same H-only fixed H weak quadratic owner; finite mesh comparison, not continuum or local order proof')
 write('CAUSAL_SUMMARY.json',out);print(out,flush=True)
def helium():
 from full_bianchi_hyrec.trajectory.primordial_2012_helium import HyRec2012Cosmology,integrate_helium_stages,helium_rhs,saha_xH1s,KB_EV_K
 import full_bianchi_hyrec.trajectory.primordial_2012_helium as owner
 c=HyRec2012Cosmology();h=integrate_helium_stages(c);raw=np.load(E/'HELIUM_ENERGY.npz');z=np.array(h.z);u=-np.log1p(z);assert np.max(abs(raw['z']-z))==0
 stage=np.array(h.stage);method=np.array(h.update_method);ii=np.flatnonzero(stage=='HeII_RECOMBINATION')
 rates=np.zeros((len(z),2));original=np.zeros(len(z));details=np.zeros((len(z),4))
 for i in ii:
  zz=z[i];xhe=h.xHeII[i];xh=saha_xH1s(c,xhe,zz);HH=c.hubble_s(zz);tr=c.T0_K*(1+zz)/c.fsR**2/c.meR;nh=c.nH0_m3*(1+zz)**3;xe=xhe+1-xh;xhei=c.fHe-xhe
  s0=c.fsR**3*c.meR**3*2.414194e21*tr*math.sqrt(tr)/nh*4;s=s0*math.exp(-285325.0/tr);y2s=math.exp(46090.0/tr)/s0;y2p=3*math.exp(39101.0/tr)/s0
  etacinv=c.fsR**3*c.meR**3*9.15776e28*HH/nh/xh
  g=(1.976e6/(1-math.exp(-6989/tr))+6.03e6/math.expm1(19754/tr)+1.06e8/math.expm1(21539/tr)+2.18e6/math.expm1(28496/tr)+3.37e7/math.expm1(29224/tr)+1.04e6/math.expm1(32414/tr)+1.51e7/math.expm1(32781/tr))*c.fsR**5*c.meR
  tau=4.277e-14*nh/HH*xhei/(c.fsR*c.meR**2);tauc=g*tau/(4*math.pi**2)/etacinv;enh=math.sqrt(1+math.pi**2*tauc)+7.74*tauc/(1+70*tauc);pesc=enh/tau+(1-math.exp(-1.023e-7*tau))*(.964525*math.exp(2947/tr)-enh*math.exp(-6.14e13*c.fsR**2*c.meR/etacinv))/tau
  a=c.fsR**8*c.meR*50.94*y2s;b=c.fsR**5*c.meR*1.7989e9*y2p*pesc;f=(xhei*s-xhe*xe)/HH;rates[i]=[a*f,b*f];original[i]=helium_rhs(c,xh,xhe,HH,zz);details[i]=[tau,pesc,a,b]
 assert max(abs(rates.sum(1)-original))<=1e-12*max(abs(original))
 energy=KB_EV_K*np.array([285325-46090,285325-39101]);du=np.diff(u);net=-.5*(rates[:-1]+rates[1:])*du[:,None];hx=np.array(h.xHeII);db=-np.diff(hx)
 rows=[]
 for label,mask in [('all_HeII',(stage[:-1]=='HeII_RECOMBINATION')&(stage[1:]=='HeII_RECOMBINATION')),('predictor',(method[:-1]=='SOURCE_PREDICTOR')&(method[1:]=='SOURCE_PREDICTOR')),('post_Saha',(method[:-1]=='POST_SAHA')&(method[1:]=='POST_SAHA'))]:
  assert mask.any();n=net[mask].sum(0);stock=float(db[mask].sum());req=float(raw['required_cell'][mask].sum());y=net[mask]@energy;rows.append(dict(scope=label,intervals=int(sum(mask)),net_events_per_H=n.tolist(),net_events_per_He=(n/c.fHe).tolist(),HeII_stock_decrease=stock,net_rate_minus_stock=float(sum(n)-stock),energy_proxy_per_H=float(n@energy),first_law_required_per_H=req,missing_or_excess_energy_proxy=float(req-n@energy),positive_energy_proxy=float(np.maximum(y,0).sum()),negative_energy_proxy=float(np.minimum(y,0).sum())))
 np.savez_compressed(D/'HELIUM_CHANNELS.npz',u=u,z=z,rates=rates,source_rate=original,details=details,net_cell=net,energy=energy,stage=stage,method=method)
 write('HELIUM_CHANNELS.json',dict(source_sha=sha(Path(owner.__file__)),history_sha=sha(E/'HELIUM_ENERGY.npz'),max_rate_split_abs=float(max(abs(rates.sum(1)-original))),energy_proxy_eV=energy.tolist(),rows=rows,scope='source effective net 2s/two-photon and 2p+escape channel proxies; escape includes continuum/intercombination corrections, not actual resolved photons or spectral emissivity; HeIII, cascades, kinetic/feedback work absent'))
 print(rows,flush=True)
if __name__=='__main__':
 if sys.argv[1]=='mesh':mesh()
 elif sys.argv[1]=='analyze':analyze()
 elif sys.argv[1]=='helium':helium()
 else:run(sys.argv[1],float(sys.argv[2]))
