"""Actual KHW direct physical exterior coupling; no native proxy promotion."""
import argparse,hashlib,json,time,subprocess
from pathlib import Path
import numpy as np
from scipy.constants import h,e
from full_bianchi_hyrec.standalone_line import prepare,export_graph,export_case
from full_bianchi_hyrec.trajectory.atomic_dynamic_companion import DynamicTwoS,L
from full_bianchi_hyrec.trajectory.atomic_physical_exterior import compile_blocks,ExteriorPairs
from full_bianchi_hyrec.trajectory.hyrec_two_photon_raman import OriginalHyRecTwoPhotonRamanTable
from full_bianchi_hyrec.recoil.original_hyrec_native import populate_original_hyrec_diffusion,build_native_diffusion_network,schur_reduce_line_centre,inferred_log_cell_edges_eV,inferred_photon_mode_measure_m3,physical_number_map_residual
p=argparse.ArgumentParser();p.add_argument('--compiled',type=Path,required=True);p.add_argument('--rates',type=Path,required=True);p.add_argument('--binary',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
root=a.out.resolve();root.mkdir(exist_ok=False);exe=a.binary.resolve()
def sha(p):
 with open(p,'rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
states=json.loads((a.compiled/'STATES.json').read_text())['states'];results=[];sources=[]
tab=OriginalHyRecTwoPhotonRamanTable.from_archive(a.rates);raw=np.column_stack([tab.energy_eV,tab.integrated_rates_s_inv.T])
for bath in ('z1100','z1300','z900'):
 st=states[bath]
 with np.load(a.compiled/(bath+'.npz')) as z:data={k:z[k] for k in z.files}
 for sub in (1,4):
  q=prepare(data,sub);net=DynamicTwoS(a.rates,q)
  t=time.monotonic();ep,prod=compile_blocks(net,'production');er,ref=compile_blocks(net,'reference')
  assert [(i,j) for i,j,K in ep]==[(i,j) for i,j,K in er]
  kp=np.array([K for i,j,K in ep]);kr=np.array([K for i,j,K in er])
  mass_gap=float(np.sum(abs(kp-kr))/np.sum(kr))
  direct_p=np.sum([r['direct_centered'] for r in prod],axis=0);direct_r=np.sum([r['direct_centered'] for r in ref],axis=0)
  direct_gap=float(np.max(abs(direct_p/direct_r-1)))
  # Native proxy conservation obstruction, unchanged coordinate definition.
  native=build_native_diffusion_network(populate_original_hyrec_diffusion(raw,q['T']))
  proxy=physical_number_map_residual(schur_reduce_line_centre(native),inferred_photon_mode_measure_m3(inferred_log_cell_edges_eV(tab.energy_eV)))
  pairs=ExteriorPairs(net,er);neutral=st['n_H_m3']*(st['x_1s']+st['x_2s']);n2=st['n_H_m3']*st['x_2s']
  errors={}
  for kind,sg in [('hot',1),('cold',-1)]:
   s=net.initial(q['T']*(1+sg*.001),neutral,n2)
   E,gross=pairs.action(s);dE=direct_r[0 if sg==1 else 1]*h*q['dnu']/e
   errors[kind]=dict(represented_eV_m3_s=E,continuum_eV_m3_s=float(dE),relative=abs(E/dE-1),sign_match=bool(E*dE>0))
  s=net.initial(q['T'],neutral,equilibrium=True);E,g=pairs.action(s);thermal=abs(E)/g
  source=dict(bath=bath,sub=sub,production=prod,reference=ref,edges=len(er),quadrature_L1=mass_gap,direct_quadrature_gap=direct_gap,proxy_weighted_null_residual=proxy,thermal_null=thermal,continuum=errors,elapsed=time.monotonic()-t,source_sha256=sha(a.compiled/(bath+'.npz')))
  sources.append(source);print('SOURCE',bath,sub,mass_gap,direct_gap,proxy,thermal,errors,flush=True)
  (root/'SOURCES.json').write_text(json.dumps(sources,indent=2,allow_nan=False)+'\n')
  # Positive graph and physical source are valid scoped even if the exterior
  # point-centre closure is not yet quantitatively converged. Keep discrepancy.
  assert mass_gap<.02 and direct_gap<.02 and thermal<1e-11
  assert all(x['sign_match'] for x in errors.values())
  graph=root/f'{bath}_s{sub}.txt';export_graph(q,graph)
  tasks=[('actual',.1,4,True),('pulse',.1,4,True),('thermal',.1,4,False)]
  if bath=='z1100' and sub==4:tasks.extend([('pulse',.1,n,True) for n in (1,2,8,16)])
  for kind,duration,nsteps,core in tasks:
   name=f'{bath}_s{sub}_{kind}_n{nsteps}';dest=root/name;dest.mkdir()
   s=net.initial(q['T'],neutral,equilibrium=True) if kind=='thermal' else net.initial(st['T_r_K'],neutral,n2)
   if kind=='pulse':
    for typ,I,J,A,B in [(x['kind'],x['i'],x['j'],x['a'],x['b']) for x in ref]:
     if typ=='cross':s.dt[J[0]]+=s.nt[J[0]]*L('.25')
   initial=s.clone();gross=0.;scatter_gross=0.;bath_energy=L(0);cross=L(0);hist=[]
   for i in range(nsteps):
    dt=duration/nsteps
    r=net.step(s,dt);gross+=r['gross']
    a0=pairs.step(s,dt);scatter_gross+=a0['gross'];bath_energy+=L(a0['bath_energy_eV_m3']);cross+=L(a0['cross_into_core'])
    if core:
     f=np.asarray((s.nt[:net.ncore]+s.dt[:net.ncore])/net.gt[:net.ncore],dtype=float)
     c=dest/f'{i:03d}.case';o=dest/f'{i:03d}_collision'
     export_case(c,q,f,dt*float((s.neutral-s.n2-s.d2)/q['n1s']),1)
     subprocess.run([str(exe),str(graph),str(c),str(o)],check=True,capture_output=True,timeout=30)
     b=np.genfromtxt(o/'state.tsv',names=True,delimiter='\t');s.dt[:net.ncore]+=net.gt[:net.ncore]*(np.asarray(b['final_f'],dtype=L)-np.asarray(f,dtype=L))
     run=dict(x.split('=',1) for x in (o/'run.txt').read_text().splitlines())
     bath_energy-=L(run['collision_energy_j_m3'])/L('1.602176634e-19')
    dn=s.dt-initial.dt;dc=s.dc-initial.dc;da=s.d2-initial.d2
    nd=np.sum(dn)+da;de=dn@net.et+dc@net.ec+net.transition*da+bath_energy
    scale=max(gross+scatter_gross,1e-300)
    hist.append(dict(step=i+1,n2=float(s.n2+s.d2),cross_into_core=float(cross),gross_atomic=gross,gross_exterior=scatter_gross,number_relative=float(abs(nd)/scale),energy_relative=float(abs(de)/(scale*net.transition)),bath_energy=float(bath_energy),exterior_pair=a0))
    assert np.min(s.nt+s.dt)>=0 and np.min(s.nc+s.dc)>=0 and 0<=s.n2+s.d2<=s.neutral
   np.savez_compressed(dest/'STATE.npz',tracked_base=s.nt,companion_base=s.nc,tracked_initial_delta=initial.dt,tracked_delta=s.dt,companion_delta=s.dc,n2_delta=s.d2,n2_initial_delta=initial.d2,et=net.et,ec=net.ec)
   (dest/'HISTORY.json').write_text(json.dumps(hist,indent=2,allow_nan=False)+'\n')
   row=dict(case=name,bath=bath,sub=sub,kind=kind,steps=nsteps,core=core,terminal=hist[-1],max_N=max(x['number_relative'] for x in hist),max_E=max(x['energy_relative'] for x in hist),max_pair_res=max(x['exterior_pair']['max_event_residual'] for x in hist),graph_sha256=sha(graph),hashes={str(f.relative_to(dest)):sha(f) for f in dest.rglob('*') if f.is_file()})
   assert row['max_N']<3e-3 and row['max_E']<3e-3
   results.append(row);print('RUN',name,row['terminal'],flush=True)
   (root/'RESULTS.json').write_text(json.dumps(dict(scope='six selected disjoint physical KHW exterior blocks plus full finite 2s source and optional core COM',source_count=len(sources),binary_sha256=sha(exe),rate_archive_sha256=sha(a.rates),cases=results),indent=2,allow_nan=False)+'\n')
