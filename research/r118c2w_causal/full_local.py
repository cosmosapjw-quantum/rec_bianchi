"""Local 2s/scattering response in same prescribed causal FULL bath.
No return of new recoil/atomic response to FULL accepted history.
"""
import sys,json,hashlib,time
from pathlib import Path
import numpy as np
from scipy.integrate import solve_ivp
from scipy.constants import h,c,e,k
from full_bianchi_hyrec.trajectory.hmla_flrw import HMLAFlrwSource,KB_NATIVE_EV_K
from full_bianchi_hyrec.trajectory.primitive_rates import OriginalHyRecPrimitiveRateTable
from full_bianchi_hyrec.trajectory.full_2012_atomic_source import _canonical_twophoton_table,populate_original_full_atomic,complete_original_full_atomic
from full_bianchi_hyrec.trajectory.causal_virtual_redshift import causal_incoming_from_accepted_histories,_source_edges
from full_bianchi_hyrec.recoil.calibrated_source import Bath,compile_isotropic
from full_bianchi_hyrec.standalone_line import prepare
from full_bianchi_hyrec.trajectory.atomic_refined_owner import RefinedTwoS,compile_integrals,assemble,Scatter
from full_bianchi_hyrec.trajectory.atomic_dynamic_companion import State,L
D=Path(__file__).resolve().parent
for q in ('r118c2u_boundaries','r118c2v_stable_zero','r118c2r_stable_extent','r118c2q_activity_bath'):
 sys.path.insert(0,str(D.parent/q))
from boundary import JoinedDrift
from reaction_boundary import BoundaryReaction
from stable_zero import IncrementScatter
from extent_map import coupled_step
from stable_activity import bath_at
R=Path('archive/inputs/original_hyrec_oct2012/HyRec_Oct2012.zip')
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
source=D/'FULL_128.npz';v=np.load(source);rec=json.loads((D/'FULL_FACE.json').read_text());assert sha(source)==rec['rows'][-1]['sha']
model=HMLAFlrwSource(h=.6735837,omega_cb=.31242079216478097,omega_r_h2=4.1578740068818545e-5,omega_de_h2=.3119234221656212,omega_b_h2=.02242,y_he_mass=.245,tcmb0_K=2.7255,table=OriginalHyRecPrimitiveRateTable.from_archive(R))
energy=_canonical_twophoton_table(R).energy_eV;idx=96;z0=float(v['z'][idx]);u0=float(v['u'][idx]);dlna=float(v['u'][1]-v['u'][0])
inc=causal_incoming_from_accepted_histories(energies_eV=energy,virtual_history=v['virtual_out'][:,:idx],lyman_history=v['lyman_out'][:,:idx],z_start=float(v['z'][0]),iz=idx,z_face=z0,dlna=dlna,shear_q=0.)
assert inc.virtual_distortion[0,-1]==v['incoming'][idx]
x0=float(v['xHII'][idx]);T0=float(v['T'][idx]);H0,nh0=model.cosmology(z0);neutral=L(nh0*(1-x0))
snap=populate_original_full_atomic(model,z=z0,xHII=x0,xe=x0,Tm_K=T0,incoming_virtual=inc.virtual_distortion[0],incoming_lyman=inc.lya_lyb_incoming_distortion[0])
full=complete_original_full_atomic(snap)
assert np.array_equal(full.outgoing_virtual,v['virtual_out'][:,idx])
out=Path('/home/cosmosapjw/Downloads/rec_r118c2w_full_local');out.mkdir(exist_ok=False)
bath=Bath(T0,float(neutral));t0=time.monotonic()
data=compile_isotropic(bath,(4,),2);np.savez_compressed(out/'SOURCE.npz',**data)
q=prepare(data,4);net=RefinedTwoS(R,q,128);integ=compile_integrals(net,bath);edges,report=assemble(net,data,integ);sc=Scatter(net,edges)
np.savez_compressed(out/'GRAPH128.npz',i=sc.i,j=sc.j,K=sc.K,new=sc.new,cross=sc.cross,et=net.et,gt=net.gt,ec=net.ec,gc=net.gc,events=np.array(net.events,dtype=L))
prior=np.load('/home/cosmosapjw/Downloads/rec_r118c2k_refined/z1100/GRAPH128.npz')
for key in ('i','j','et','gt','ec','gc','events'):assert np.array_equal(prior[key],np.load(out/'GRAPH128.npz')[key]),key
print('compiled FULL bath',z0,T0,float(neutral),len(sc.i),time.monotonic()-t0,flush=True)
# Positive projection of actual average distortions, using separate intervals
# across real line discontinuities (piecewise linear within each segment;
# end values constant until next line). Companion Planck closure explicit.
lines=[0.,10.198714553953742,12.087365397278509,13.6]
def distortion(ee):
 ee=np.asarray(ee,dtype=L);d=np.zeros_like(ee)
 for lo,hi in zip(lines[:-1],lines[1:]):
  sel=(energy>=lo)&(energy<hi);tar=(ee>=lo)&(ee<hi)
  d[tar]=np.interp(np.asarray(ee[tar],float),energy[sel],full.average_virtual[sel])
 return d
n2=L(nh0)*(L(full.real_departures[0])+L(1-x0)*np.exp(-net.transition/L(snap.Tr_eV)))
assert 0<n2<neutral
base=net.initial(L(model.tcmb0_K)*(1+L(z0)),neutral,n2,tracked_temperature=L(model.tcmb0_K)*(1+L(z0)))
ft=base.nt/net.gt;ft[net.ncore:]+=distortion(net.et[net.ncore:])
for i,(ww,xx) in enumerate(zip(net.w,net.q['xx'])):
 en=L(h)*(L(net.q['nu'])+L(net.q['dnu'])*np.asarray(xx,dtype=L))/L(e);ft[i]+=ww@distortion(en)
assert np.min(ft)>0
base.nt=net.gt*ft
np.savez_compressed(out/'INITIAL.npz',nt=base.nt,nc=base.nc,n2=base.n2,neutral=base.neutral)
nt,nc=len(base.nt),len(base.nc);drift=JoinedDrift(net.et,net.gt,net.ec,net.gc)
ii,jj,sg,rate,_=map(np.asarray,zip(*net.events));ii=ii.astype(int);jj=jj.astype(int);sg=sg.astype(L);rate=rate.astype(L)
du=solve_ivp(lambda t,y:[model.cosmology((1+z0)*np.exp(-y[0])-1)[0]],(0,10.),[0.],rtol=1e-12,atol=1e-27,dense_output=True);assert du.success
def u(t):return L(du.sol(t)[0])
def z(t):return float((1+L(z0))*np.exp(-u(t))-1)
src,targets,ens=_source_edges(energy);delay=float(np.log(ens[-3]/targets[-3]));assert src[-3]==313
fac=L(8*np.pi)*(drift.e.max()/L('1.239841874331e-4'))**3*L(1e6)
def influx(t):
    eta=u0+float(u(t));ret=eta-delay;assert ret<v['u'][idx]
    # Only already accepted prefix; no future emission history.
    f=L(np.interp(ret,v['u'][:idx],v['lyman_out'][2,:idx])) if ret>=0 else L(0)
    tr=L(KB_NATIVE_EV_K)*L(model.tcmb0_K)*(1+L(z(t)))
    return np.exp(3*u(t))*fac*(1/np.expm1(drift.e.max()/tr)+f)
def at(t,s):
    eta=u0+float(u(t));T=float(np.interp(eta,v['u'],v['T']));x=float(np.interp(eta,v['u'],v['xHII']));_,nh=model.cosmology(z(t))
    dil=np.exp(-3*u(t));st=s.clone();st.nt=s.nt*dil;st.nc=s.nc*dil;st.dt=s.dt*dil;st.dc=s.dc*dil;st.d2=s.d2*dil;st.n2=base.n2*dil;st.neutral=L(nh*(1-x))
    n,scatter=bath_at(net,sc,st,T);n.q['n1s']=float(st.neutral);scatter.K=sc.K*(st.neutral/neutral)
    return st,n,scatter,dil
def gmap(s,t0,t1):
    a,l=drift.affine(np.r_[s.nt,s.nc],np.r_[s.dt,s.dc],u(t1)-u(t0),influx((t0+t1)/2))
    s.dt=a[:nt].copy();s.dc=a[nt:].copy();return l
def step(s,t,dt):
    a=gmap(s,t,t+dt/2);st,n,sc1,dil=at(t+dt/2,s);before=st.clone()
    l=coupled_step(BoundaryReaction(n,st),IncrementScatter(sc1,st),st,dt)
    s.dt+=(st.dt-before.dt)/dil;s.dc+=(st.dc-before.dc)/dil;s.d2+=(st.d2-before.d2)/dil
    b=gmap(s,t+dt/2,t+dt)
    for k in ('gross','bath','cross','new_energy'):l[k]/=dil
    return {**l,**{k:a[k]+b[k] for k in a}}
scale=max(base.n2,L('1e-30'))
def rhs(t,y):
    v0=np.asarray(y,dtype=L)*scale;s=base.clone();s.dt=v0[:nt];s.dc=v0[nt:nt+nc];s.d2=v0[-10]
    st,n,sct,dil=at(t,s)
    f=n.point_values(st);fc=(st.nc+st.dc)/n.gc;b=st.n2+st.d2
    F=rate*(b*(1+f[ii])*(fc[jj]+(sg==1))-(st.neutral-b)*f[ii]*(fc[jj]+(sg==-1)))
    ds,flux,gross=sct.rhs(st);np.add.at(ds,ii,F);cs=np.zeros(nc,dtype=L);np.add.at(cs,jj,sg*F);en=flux@sct.de
    H=model.cosmology(z(t))[0];ff=H*drift.rate*np.r_[s.nt+s.dt,s.nc+s.dc];inj=H*influx(t);dx=drift.divergence(ff);dx[drift.top]+=inj*drift.topw;esc=ff[drift.escape].sum()
    return np.asarray(np.r_[ds/dil+dx[:nt],cs/dil+dx[nt:],-F.sum()/dil,flux[sct.cross].sum()/dil,flux[sct.new]@sct.de[sct.new]/dil,-en/dil,esc,esc*drift.ghost,ff@drift.de,inj,inj*drift.e.max(),ff@drift.cross_weight]/scale,float)
refs=[]
for tol in (3e-10,3e-11):
 sol=solve_ivp(rhs,(0,10.),np.zeros(nt+nc+10),method='DOP853',rtol=tol,atol=tol/100);assert sol.success
 refs.append(np.asarray(sol.y[:,-1],dtype=L)*scale);print('reference',tol,sol.nfev,flush=True)
ref=refs[-1];rows=[]
receipt=dict(status='SCOPED_RUNNING',scope='actual accepted short FULL history at column96; local two-photon/scatter graph, projected FULL virtual averages, thermal companion; bath prescribed; no recoil writeback',full_sha=sha(source),rates_sha=sha(R),raw=str(out),raw_hashes={p.name:sha(p) for p in out.iterdir() if p.is_file()},z0=z0,z_end=z(10.),T0=T0,T_end=float(np.interp(u0+float(u(10.)),v['u'],v['T'])),n2=float(n2),initial_influx=float(influx(0)),final_influx=float(influx(10.)),reference_gap=float(np.max(abs(refs[0]-ref))),rows=rows)
def save(): (D/'FULL_LOCAL.json').write_text(json.dumps(receipt,indent=2,allow_nan=False)+'\n')
save()
for nsteps in (4,16,64):
 s=base.clone();led=None;dt=10./nsteps
 for i in range(nsteps):
  v0=step(s,i*dt,dt)
  led=v0 if led is None else {k:max(led[k],v0[k]) if k=='max_root' else led[k]+v0[k] for k in led}
 dx=np.r_[s.dt,s.dc,s.d2,led['cross'],led['new_energy'],led['bath'],led['escape_N'],led['escape_U'],led['work'],led['in_N'],led['in_U'],led['cross_N']]
 N=abs(s.dt.sum()+s.d2+led['cross_N']-led['in_N'])/max(led['gross']+led['cross_N']+led['in_N'],L('1e-300'))
 En=abs(s.dt@net.et+s.dc@net.ec+s.d2*net.transition+led['bath']+led['escape_U']+led['work']-led['in_U'])/max(led['gross']*net.transition+led['escape_U']+led['work']+led['in_U'],L('1e-300'))
 row=dict(steps=nsteps,tracked_error=float(np.sum(abs(dx[:nt]-ref[:nt]))/np.sum(abs(ref[:nt]))),atomic_error=float(abs(dx[-10]-ref[-10])),N=float(N),E=float(En),in_N=float(led['in_N']),fallbacks=int(led['roundoff_fallbacks']))
 assert min(s.nt+s.dt)>0 and min(s.nc+s.dc)>0 and max(N,En)<1e-11
 rows.append(row);print(row,flush=True);save()
receipt['status']='COMPLETE_SCOPED_SAME_FULL_BATH';save()
