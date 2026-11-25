"""Actual 2s paired source on the existing calibrated scalar COM collision grid.
Fixed material temperature and Planck companion reservoir; HII/2p frozen.
Rescale COM time by live n1s/n1s_anchor, exact because density enters linearly.
Independent state/event ledger, no legacy overlapping line diffusion."""
import argparse,hashlib,json,math,subprocess,time
from pathlib import Path
import numpy as np
from scipy.constants import h,k,e
from full_bianchi_hyrec.trajectory.atomic_two_s_live import TwoSNetwork
from full_bianchi_hyrec.standalone_line import prepare,initial,export_graph,export_case
p=argparse.ArgumentParser();p.add_argument('--compiled',type=Path,required=True);p.add_argument('--binary',type=Path,required=True);p.add_argument('--rates',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
root=a.out.resolve();root.mkdir(exist_ok=False,parents=True);exe=a.binary.resolve()
def sha(p):
    with open(p,'rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
states=json.loads((a.compiled/'STATES.json').read_text())['states'];rows=[]
for bath in ('z1300','z1100','z900'):
    state=states[bath]
    with np.load(a.compiled/(bath+'.npz')) as z:data={k:z[k] for k in z.files}
    for sub in (1,4):
        q=prepare(data,sub);net=TwoSNetwork(a.rates,q,state['T_r_K']);graph=root/f'{bath}_s{sub}.txt';export_graph(q,graph)
        tasks=[('actual',1.,4,True),('hot',1.,4,True),('vacuum',.01,4,False)]
        if bath=='z1100' and sub==4:tasks.extend([('actual',1.,n,True) for n in (1,2,8,16)])
        for kind,dt,steps,collision in tasks:
            name=f'{bath}_s{sub}_{kind}_t{dt:g}_n{steps}';dest=root/name;dest.mkdir()
            if kind=='actual':f=initial(q,'radiation',state['T_r_K'])
            elif kind=='hot':f=initial(q,'hot')
            else:f=np.zeros_like(q['g'])
            n2=state['n_H_m3']*state['x_2s'];neutral=state['n_H_m3']*(state['x_1s']+state['x_2s'])
            n20=n2;N0=float(q['g']@f)
            E0=float((q['g']*f)@net.e_ev)+net.transition_eV*n2
            cn=0.;cu=0.;bath_u=0.;gross=0.;gross_energy=0.;source_res=0.;atom_res=0.;root_res=0.;hist=[];t0=time.monotonic()
            def do_reaction(f,n2,ds):
                nonlocal_dummy=None
                return net.step(f,n2,neutral,ds)
            for s in range(steps):
                for half in (0,1):
                    r=do_reaction(f,n2,dt/(2*steps));f=r.f;n2=r.n2
                    cn+=r.companion_n;cu+=r.companion_u_eV_m3;gross+=r.gross_events;gross_energy+=r.gross_events*net.transition_eV
                    source_res=max(source_res,r.max_node_residual);atom_res=max(atom_res,r.atom_residual)
                    if half==0 and collision:
                        # At fixed T, original conductance proportional to n1s.
                        # Use existing scalar native collision, with live n1s time scale.
                        ds=dt/steps*(neutral-n2)/q['n1s']
                        c=dest/f'{s:03d}.case';o=dest/f'{s:03d}_collision'
                        export_case(c,q,f,ds,1)
                        proc=subprocess.run([str(exe),str(graph),str(c),str(o)],capture_output=True,text=True,timeout=30)
                        if proc.returncode:raise RuntimeError(proc.stderr)
                        st=np.genfromtxt(o/'state.tsv',names=True,delimiter='\t');f=st['final_f']
                        run=dict(l.split('=',1) for l in (o/'run.txt').read_text().splitlines())
                        bath_u-=float(run['collision_energy_j_m3'])/e;root_res=max(root_res,float(run['max_be_residual']))
                N=float(q['g']@f);U=float((q['g']*f)@net.e_ev)
                dn=(N-N0)+(n2-n20);de=(U+net.transition_eV*n2)-E0+cu+bath_u
                # Normalize by total stored mass/energy and separately report
                # event-scale errors so tiny net transfers are not hidden.
                assert np.min(f)>=0 and 0<=n2<=neutral
                assert abs(dn)<2e-10*max(N0,n20,N,1e-100) and abs(de)<2e-10*max(E0,U,1e-100)
                hist.append(dict(step=s+1,time_s=(s+1)*dt/steps,n2=n2,n1s=neutral-n2,N=N,U_eV_m3=U,companion_n=cn,companion_u_eV_m3=cu,material_bath_u_eV_m3=bath_u,number_defect=dn,energy_defect_eV_m3=de,number_event_relative=abs(dn)/max(gross,1e-100),energy_event_relative=abs(de)/max(gross_energy,1e-100)))
            np.savez_compressed(dest/'FINAL.npz',f=f,n2=n2,neutral=neutral)
            (dest/'HISTORY.json').write_text(json.dumps(hist,indent=2,allow_nan=False)+'\n')
            r=dict(case=name,bath=bath,subcells=sub,kind=kind,dt=dt,steps=steps,collision=collision,initial_n2=n20,terminal=hist[-1],gross_events=gross,max_node_residual=source_res,max_atom_residual=atom_res,max_be_residual=root_res,wall_s=time.monotonic()-t0,source_sha256=sha(a.compiled/(bath+'.npz')),graph_sha256=sha(graph),hashes={str(p.relative_to(dest)):sha(p) for p in sorted(dest.rglob('*')) if p.is_file()})
            print(name,r['terminal'],'node/atom',source_res,atom_res,flush=True);rows.append(r)
            (root/'RESULTS.json').write_text(json.dumps(dict(scope='2s_1s_live_source_and_scalar_COM_fixed_T_fixed_companion',status='PASS_SCOPED',binary_sha256=sha(exe),rate_archive_sha256=sha(a.rates),cases=rows),indent=2,allow_nan=False)+'\n')
