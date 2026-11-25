"""Full actual high-side 2s table and dynamically evolved companion modes.
Core COM optional, no overlapping virtual-state diffusion/escape."""
import argparse,hashlib,json,time,subprocess
from pathlib import Path
import numpy as np
from scipy.integrate import solve_ivp
from full_bianchi_hyrec.trajectory.atomic_dynamic_companion import DynamicTwoS,State,L
from full_bianchi_hyrec.standalone_line import prepare,export_graph,export_case
p=argparse.ArgumentParser();p.add_argument('--compiled',type=Path,required=True);p.add_argument('--rates',type=Path,required=True);p.add_argument('--binary',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
root=a.out.resolve();root.mkdir(exist_ok=False);exe=a.binary.resolve()
def sha(p):
 with open(p,'rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
states=json.loads((a.compiled/'STATES.json').read_text())['states'];rows=[];references=[]
for bath in ('z1300','z1100','z900'):
 st=states[bath]
 with np.load(a.compiled/(bath+'.npz')) as d:data={k:d[k] for k in d.files}
 for sub in (1,4):
  q=prepare(data,sub);net=DynamicTwoS(a.rates,q)
  assert net.source_rate_relative<2e-15
  neutral=st['n_H_m3']*(st['x_1s']+st['x_2s']);n2=st['n_H_m3']*st['x_2s']
  graph=root/f'{bath}_s{sub}.txt';export_graph(q,graph)
  tasks=[('thermal',.1,2,False),('actual',.1,4,False),('hot',.1,4,True),('vacuum',.01,4,False)]
  if bath=='z1100' and sub==4:tasks += [('actual',.1,n,False) for n in (1,2,8,16,32)]+[('empty_companion',.01,4,False)]
  def initial(kind):
   if kind=='thermal':return net.initial(q['T'],neutral,equilibrium=True)
   if kind=='vacuum':return net.initial(st['T_r_K'],neutral,n2,tracked_vacuum=True)
   if kind=='empty_companion':return net.initial(st['T_r_K'],neutral,n2,companion_scale=0.)
   return net.initial(st['T_r_K'],neutral,n2,tracked_temperature=q['T']*1.001 if kind=='hot' else st['T_r_K'])
  for kind,duration,steps,collision in tasks:
   name=f'{bath}_s{sub}_{kind}_t{duration:g}_n{steps}';dest=root/name;dest.mkdir()
   s=initial(kind);start=s.clone();gross=0.;bath_energy=L(0);hist=[];mx=0.;t0=time.monotonic()
   for i in range(steps):
    r=net.step(s,duration/steps);gross+=r['gross'];mx=max(mx,r['max_event_residual'])
    if collision:
     f=np.asarray((s.nt[:net.ncore]+s.dt[:net.ncore])/net.gt[:net.ncore],dtype=float)
     case=dest/f'{i:03d}.case';out=dest/f'{i:03d}_collision'
     ds=duration/steps*float((s.neutral-s.n2-s.d2)/q['n1s'])
     export_case(case,q,f,ds,1)
     proc=subprocess.run([str(exe),str(graph),str(case),str(out)],capture_output=True,text=True,timeout=30)
     if proc.returncode:raise RuntimeError(proc.stderr)
     r0=np.genfromtxt(out/'state.tsv',names=True,delimiter='\t')
     df=np.asarray(r0['final_f'],dtype=L)-np.asarray(f,dtype=L)
     s.dt[:net.ncore]+=net.gt[:net.ncore]*df
     m=dict(v.split('=',1) for v in (out/'run.txt').read_text().splitlines())
     bath_energy-=L(m['collision_energy_j_m3'])/L('1.602176634e-19')
    dn=np.sum(s.dt)+s.d2
    de=s.dt@net.et+s.dc@net.ec+net.transition*s.d2+bath_energy
    assert np.min(s.nt+s.dt)>=0 and np.min(s.nc+s.dc)>=0 and 0<=s.n2+s.d2<=s.neutral
    scale=max(gross,1e-300)
    hist.append(dict(step=i+1,time_s=duration*(i+1)/steps,n2=float(s.n2+s.d2),delta_n2=float(s.d2),delta_N_tracked=float(np.sum(s.dt)),delta_N_companion=float(np.sum(s.dc)),energy_eV_m3=float(de),number_relative=float(abs(dn)/scale),energy_relative=float(abs(de)/(scale*net.transition)),source_event_number_relative=r['number_relative'],source_event_energy_relative=r['energy_relative'],companion_max_relative=float(np.max(abs(s.dc)/np.maximum(s.nc,L('1e-4900')))) if kind!='empty_companion' else None,bath_energy=float(bath_energy),max_event_residual=mx))
   # Verify absolute dynamic perturbations without subtracting giant baselines.
   np.savez_compressed(dest/'STATE.npz',tracked_energy=net.et,companion_energy=net.ec,tracked_g=net.gt,companion_g=net.gc,tracked_base=s.nt,companion_base=s.nc,tracked_delta=s.dt,companion_delta=s.dc,n2_base=s.n2,n2_delta=s.d2,neutral=s.neutral)
   (dest/'HISTORY.json').write_text(json.dumps(hist,indent=2,allow_nan=False)+'\n')
   row=dict(case=name,bath=bath,sub=sub,kind=kind,steps=steps,duration=duration,collision=collision,events=len(net.events),tracked_modes=len(net.et),companion_modes=len(net.ec),source_rate_relative=net.source_rate_relative,gross_events=gross,terminal=hist[-1],max_number_relative=max(v['number_relative'] for v in hist),max_energy_relative=max(v['energy_relative'] for v in hist),max_source_event_residual=mx,wall_s=time.monotonic()-t0,source_sha256=sha(a.compiled/(bath+'.npz')),graph_sha256=sha(graph),hashes={str(f.relative_to(dest)):sha(f) for f in dest.rglob('*') if f.is_file()})
   assert row['max_number_relative']<(3e-3 if collision else 1e-12) and row['max_energy_relative']<(3e-3 if collision else 1e-12)
   if kind=='thermal':assert abs(float(s.d2))/float(start.n2)<1e-10
   rows.append(row);print(name,row['terminal'],'gross',gross,flush=True)
  if bath=='z1100' and sub==4:
   s=initial('actual');scale=float(s.n2);nt=len(s.nt);nc=len(s.nc)
   ii=np.array([v[0] for v in net.events]);jj=np.array([v[1] for v in net.events]);sg=np.array([v[2] for v in net.events],dtype=L);rate=np.array([v[3] for v in net.events],dtype=L)
   # Vectorized independent RHS, not the split implicit event root.
   def rhs(t,y):
    u=np.asarray(y,dtype=L)*L(scale);b=s.n2+u[-1]
    ft=(s.nt+u[:nt])/net.gt
    for i in np.unique(ii[ii<net.ncore]):
     z=net.z[i];w=net.w[i];f=ft[i];alpha=f/(w@z)/(1+f)
     for _ in range(8):
      v=alpha*z;alpha-=(w@(v/(1-v))-f)/(w@(z/(1-v)**2))
     v=alpha*net.zi[i];ft[i]=v/(1-v)
    fc=(s.nc+u[nt:nt+nc])/net.gc
    v=rate*(b*(1+ft[ii])*(fc[jj]+(sg==1))-(s.neutral-b)*ft[ii]*(fc[jj]+(sg==-1)))
    r=np.zeros(nt+nc+1,dtype=L);np.add.at(r,ii,v);np.add.at(r,nt+jj,sg*v);r[-1]=-np.sum(v)
    return np.asarray(r/L(scale),dtype=float)
   ode=solve_ivp(rhs,(0,.1),np.zeros(nt+nc+1),method='DOP853',rtol=2e-11,atol=1e-13)
   assert ode.success
   y=ode.y[:,-1]
   for r in rows:
    if r['bath']==bath and r['sub']==4 and r['kind']=='actual' and not r['collision']:
     ref=float(y[-1]*scale);err=abs(r['terminal']['delta_n2']-ref)/abs(ref)
     references.append(dict(steps=r['steps'],reference_delta_n2=ref,relative_signal_error=err,reference_steps=len(ode.t)-1))
   references.sort(key=lambda x:x['steps']);print('REFERENCE',references,flush=True)
(root/'RESULTS.json').write_text(json.dumps(dict(scope='actual full 2s table dynamic tracked/companion auxiliary phase mode closure',binary_sha256=sha(exe),rate_archive_sha256=sha(a.rates),cases=rows,references=references),indent=2,allow_nan=False)+'\n')
