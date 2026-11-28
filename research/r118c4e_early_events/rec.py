"""Early targeted nested retarded H owner and independent primordial helium energy demand."""
from pathlib import Path
import sys,json,numpy as np,hashlib
D=Path(__file__).resolve().parent;P=D.parent;C4=P/'r118c4d_nested_history';B=P/'r118c4b_global_quadratic'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(n,o):(D/n).write_text(json.dumps(o,indent=2)+'\n')
src=(C4/'rec.py').read_text();a="he=np.empty(2*len(oldhe)-1);he[::2]=oldhe;he[1::2]=.5*(oldhe[:-1]+oldhe[1:]);assert np.all(np.diff(he)>0)"
b="parts=[np.linspace(l,r,4 if np.expm1(-l)>=1108.5 else 1,endpoint=False) for l,r in zip(oldhe[:-1],oldhe[1:])];he=np.r_[np.concatenate(parts),oldhe[-1]];assert np.all(np.diff(he)>0) and np.array_equal(he[np.searchsorted(he,oldhe)],oldhe)"
assert src.count(a)==1
src=src.replace(a,b).replace('nested256_','early4_')
ns={'__file__':str(D/'rec.py'),'__name__':'c4e_owner'};exec(compile(src,str(C4/'rec.py'),'exec'),ns)
def run(kind,lam):ns['run'](kind,lam)
def analyze():
 old=[json.loads((B/f'PAIR_q3_128_{l:g}.json').read_text()) for l in [-.5,.5]]
 d4=json.loads((C4/'NESTED_SUMMARY.json').read_text());direct=[json.loads(p.read_text()) for p in sorted(D.glob('early4_q3_128_*.json'))];pairs=[json.loads(p.read_text()) for p in sorted(D.glob('PAIR_early4_q3_128_*.json'))]
 o=dict(direct=direct,pairs=pairs,prior128_even=(old[0]['delta_x']+old[1]['delta_x'])/.5,prior128_odd=old[1]['delta_x']-old[0]['delta_x'],prior256_even=d4['even'],prior256_odd=d4['odd'],scope='same H-only fixed H retarded quadratic owner; early refinement z>=1108.5, no continuum proof')
 if len(pairs)==2:
  a,b=sorted(pairs,key=lambda x:x['lam']);assert a['mesh_sha256']==b['mesh_sha256'];o.update(even=(a['delta_x']+b['delta_x'])/.5,odd=b['delta_x']-a['delta_x'],min_positive=min(a['min_stored_virtual_ratio'],b['min_stored_virtual_ratio']),max_direct_error=max(a['abs_disagreement'],b['abs_disagreement']),cells=a['cells_checked']+b['cells_checked'])
  za,zb=[np.load(D/f'PAIR_early4_q3_128_{l:g}.npz') for l in [-.5,.5]];oa,ob=[np.load(B/f'PAIR_q3_128_{l:g}.npz') for l in [-.5,.5]];ga,gb=[np.load(C4/f'PAIR_nested256_q3_128_{l:g}.npz') for l in [-.5,.5]]
  pr=oa['rows'];nr=za['rows'];ix=np.searchsorted(nr[:,0],pr[:,0]);assert np.array_equal(nr[ix,0],pr[:,0]);assert np.array_equal(ga['rows'][::2,0],pr[:,0])
  new=(za['rows'][:,1]+zb['rows'][:,1])/.5;prior=(oa['rows'][:,1]+ob['rows'][:,1])/.5;glob=(ga['rows'][:,1]+gb['rows'][:,1])/.5;dd=new[ix]-prior;ddg=glob[::2]-prior;de=new[ix]-glob[::2]
  j=int(np.argmax(abs(dd)));j2=int(np.argmax(abs(de)));o.update(max_cumulative_disagreement=float(abs(dd[j])),redshift_max_cumulative_disagreement=float(np.expm1(-pr[j,0])),max_disagreement_vs_global=float(abs(de[j2])),redshift_max_vs_global=float(np.expm1(-pr[j2,0])),endpoint_difference=float(dd[-1]),fraction_global_endpoint_change=float(dd[-1]/ddg[-1]),odd_endpoint_relative_change=float(abs(o['odd']-o['prior256_odd'])/max(abs(o['odd']),1e-300)))
  np.savez_compressed(D/'EARLY_DIFFERENCE.npz',u=pr[:,0],old_even=prior,early_even=new[ix],global_even=glob[::2],early_minus_old=dd,global_minus_old=ddg,early_minus_global=de)
 write('EARLY_SUMMARY.json',o);print(o,flush=True)
def helium():
 sys.path.insert(0,str(D.parents[1]/'src'))
 from full_bianchi_hyrec.trajectory.primordial_2012_helium import HyRec2012Cosmology,integrate_helium_stages,KB_EV_K,DLNA
 import full_bianchi_hyrec.trajectory.primordial_2012_helium as owner
 c=HyRec2012Cosmology();h=integrate_helium_stages(c);ld=np.longdouble
 z=np.array(h.z,ld);u=-np.log1p(z);xe=np.array(h.xe,ld);x=np.array(h.xHII,ld);hei=np.array(h.xHeI,ld);heii=np.array(h.xHeII,ld);heiii=np.array(h.xHeIII,ld);T=np.array(h.Tm_K,ld);Tr=ld(c.T0_K)*(1+z);f=ld(c.fHe);H=np.array([c.hubble_s(float(v)) for v in z],ld)
 assert np.max(abs(hei+heii+heiii-f))<1e-14 and np.max(abs(x+heii+2*heiii-xe))<1e-14
 chiH,chiI,chiII=map(ld,['13.598434599702','24.587389011','54.41776']);w=ld('1.5')*ld(KB_EV_K)*T*(1+f+xe);b=chiH*x+chiI*heii+(chiI+chiII)*heiii
 gamma=ld('4.91466895548409e-22');qc=ld('1.5')*ld(KB_EV_K)*gamma*Tr**4*xe*(Tr-T)/H
 # Source sets T=Tr exactly on HeIII Saha stage; avoid spurious roundoff-driven huge Compton term.
 stage=np.array(h.stage);qc[stage=='HeIII_SAHA']=0
 du=np.diff(u);work=(w[:-1]+w[1:])*du;com=.5*(qc[:-1]+qc[1:])*du;dw=np.diff(w);db=np.diff(b);req=com-work-dw-db
 # Q_rad is net non-Compton energy leaving gas required by first law, not emitted spectrum.
 rows=[]
 for name in ['HeIII_SAHA','HeII_RECOMBINATION']:
  mask=(stage[:-1]==name)&(stage[1:]==name);assert mask.any();inds=np.where(mask)[0];d=dict(stage=name,cells=int(sum(mask)),z_start=float(z[inds[0]]),z_end=float(z[inds[-1]+1]),thermal_change=float(sum(dw[mask])),binding_change=float(sum(db[mask])),expansion_work=float(sum(work[mask])),compton_input=float(sum(com[mask])),required_net_noncompton_out=float(sum(req[mask])),positive_required=float(sum(np.maximum(req[mask],0))),negative_required=float(sum(np.minimum(req[mask],0))),max_charge_error=float(max(abs(x+heii+2*heiii-xe))))
  rows.append(d)
 # Compare integral on every other endpoint; finite quadrature only, no independent photon solver.
 idx=np.unique(np.r_[np.arange(0,len(z),2),len(z)-1]);dt=np.diff(u[idx]);W=np.sum((w[idx][:-1]+w[idx][1:])*dt);Q=np.sum((qc[idx][:-1]+qc[idx][1:])*dt/2);req2=Q-W-(w[-1]+b[-1]-w[0]-b[0])
 out=dict(points=len(z),fHe_per_H=float(f),source_module_sha256=sha(Path(owner.__file__)),source_helium_sha=h.source_sha256,source_verification_sha256=sha(P/'rec_r3g_primordial_20261016/helium_stage_001/verification.json'),stage_rows=rows,full_required_net_noncompton_out=float(sum(req)),coarse_quadrature_change=float(req2-sum(req)),transition_cells=int(np.count_nonzero(stage[:-1]!=stage[1:])),source_thermal_rule='HeIII T=Trad lock (Compton heat not resolved); HeII source steady-state T',scope='source-owned primordial He stage histories; ideal-gas+ionization first-law required net non-Compton energy, not an independent radiative emissivity or full HHe spectral closure; Saha/T lock limits physical interpretation')
 np.savez_compressed(D/'HELIUM_ENERGY.npz',z=z,u=u,xe=xe,xHII=x,xHeI=hei,xHeII=heii,xHeIII=heiii,T=T,Tr=Tr,w=w,b=b,qc=qc,required_cell=req,work_cell=work,compton_cell=com,stage=stage)
 write('PRIMORDIAL_HE_ENERGY.json',out);print(out,flush=True)
if __name__=='__main__':
 if sys.argv[1]=='helium':helium()
 elif sys.argv[1]=='analyze':analyze()
 else:run(sys.argv[1],float(sys.argv[2]))
