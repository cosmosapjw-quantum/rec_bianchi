import argparse,pathlib,json,subprocess,math,time,hashlib
import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import brentq
from scipy.constants import h,k
from full_bianchi_hyrec.standalone_line import prepare,export_graph,initial,export_case,sha
P=pathlib.Path
p=argparse.ArgumentParser();p.add_argument('--compiled',type=P,required=True);p.add_argument('--binary',type=P,required=True);p.add_argument('--out',type=P,required=True);p.add_argument('--only',default='');a=p.parse_args()
a.out.mkdir(exist_ok=False,parents=True);exe=a.binary.resolve();ss=json.loads((a.compiled/'STATES.json').read_text())['states']
cases=[]
def add(bath,sub,kind,dt,steps,name=None,drift=None):
    cases.append(dict(case=name or f'{bath}_s{sub}_{kind}_t{dt:g}_n{steps}',bath=bath,sub=sub,kind=kind,dt=dt,steps=steps,drift=drift))
for b in ('anchor','z1300','z1100','z900'):
    for sub in (1,4):
        for kind in ('hot','cold','narrow','thermal'):
            add(b,sub,kind,0.,0)
for sub in (1,4):
    for kind in ('hot','cold','narrow','thermal','high_eq','zero','pulse'):
        add('z1100',sub,kind,2.,4)
for n in (1,2,4,8,16,32):
    add('z1100',1,'narrow',2.,n,name=f'time_{n}')
for dt in (1e2,1e4,1e6):
    add('z1100',1,'radiation',dt,2,name=f'stiff_{dt:g}')
for n in (4,8,16,32):
    add('z1100',4,'pulse',2.,n,name=f'live_reverse_{n}',drift=(8,80.,1e-4,-1e-4))
for sub in (1,4):
    for dt in (1.,100.,1e4):
        H=ss['z1100']['H_s'];add('z1100',sub,'radiation',dt,4,name=f'live_physical_s{sub}_{dt:g}',drift=(8,80.,-H*dt,-H*dt))
cache={}
def ref(q,f):
    # independently invert finite BE quadrature, using Newton in vectorized
    # padded arrays (weights=0 outside each node's support).
    w=q['_w'];z=q['_z'];u=f/(1+f)/np.sum(w*z,axis=1)
    for _ in range(12):
        y=u[:,None]*z;v=np.sum(w*y/(1-y),axis=1)
        d=np.sum(w*z/(1-y)**2,axis=1);du=(v-f)/d;u-=du
        if np.max(abs(du)/np.maximum(abs(u),1e-300))<8e-16:break
    A=1+f
    flux=q['K']*A[:,None]*A[None,:]*(u[None,:]-u[:,None])
    return flux.sum(axis=1)/q['g'],float(np.sum(np.triu(flux,1)*(q['x'][:,None]-q['x'][None,:]))),float(np.sum(abs(np.triu(flux,1)*(q['x'][:,None]-q['x'][None,:]))))
results=[]
for ca in cases:
 name=ca['case']
 if not name.startswith(a.only):continue
 key=(ca['bath'],ca['sub'])
 if key not in cache:
    with np.load(a.compiled/(ca['bath']+'.npz')) as data:
        d={k:data[k] for k in data.files};q=prepare(d,ca['sub'])
    maxq=max(len(w) for w in q['w'])
    q['_w']=np.array([np.pad(w,(0,maxq-len(w))) for w in q['w']]);q['_z']=np.array([np.pad(w,(0,maxq-len(w)),constant_values=1.) for w in q['z']])
    gp=a.out/(ca['bath']+f"_s{ca['sub']}.txt");export_graph(q,gp);cache[key]=(q,d,gp)
 q,d,gp=cache[key];f=initial(q,ca['kind'],ss.get(ca['bath'],{}).get('T_r_K'))
 case=a.out/(name+'.case');dest=a.out/name;export_case(case,q,f,ca['dt'],ca['steps'],drift=ca['drift'])
 cmd=[str(exe),str(gp),str(case),str(dest)];t=time.monotonic();proc=subprocess.run(cmd,text=True,capture_output=True,timeout=120)
 r=dict(ca,command=cmd,returncode=proc.returncode,graph_sha256=sha(gp),case_sha256=sha(case),stderr=proc.stderr[-1400:],wall_s=time.monotonic()-t)
 if proc.returncode:
    r['status']='REJECTED_NATIVE';results.append(r);print(name,r['status'],r['stderr'],flush=True);continue
 m=dict(v.split('=',1) for v in (dest/'run.txt').read_text().splitlines())
 for k0,v in list(m.items()):
    try:
        x=float(v)
        if math.isfinite(x):m[k0]=x
    except ValueError:pass
 state=np.genfromtxt(dest/'state.tsv',names=True,delimiter='\t');N=float(q['g']@f);ref_rate,ref_x,gross=ref(q,f)
 scale=max(np.max(abs(ref_rate)),max(f)*1e-14,1e-300)
 met=dict(action_gap=float(np.max(abs(state['initial_rate']-ref_rate))/scale),action_absolute_per_max_f=float(np.max(abs(state['initial_rate']-ref_rate))/max(max(f),1e-300)),centered_rate_per_photon=float(m['initial_X_rate']/max(N,1e-300)),initial_x_rate_python=ref_x,number=N)
 if ca['kind'] in ('hot','cold','narrow'):
    i={'hot':0,'cold':1,'narrow':2}[ca['kind']];met['continuum_error']=abs(m['initial_X_rate']-d['direct'][i])/abs(d['direct'][i]);met['direct_x_rate']=float(d['direct'][i])
 if name.startswith('time_'):
    # DOP853 direct finite-graph ODE at identical bath; moderate interval.
    ode=solve_ivp(lambda t,x:ref(q,x)[0],(0,ca['dt']),f,method='DOP853',rtol=5e-12,atol=1e-13)
    assert ode.success
    met['ode_signal_l1']=float(np.sum(q['g']*abs(state['final_f']-ode.y[:,-1]))/np.sum(q['g']*abs(ode.y[:,-1]-f)))
 if ca['drift']:
    met['projection_to_collision']=float((abs(m['core_projection_X'])+abs(m['exterior_projection_X']))/max(abs(m['collision_X']),1e-300))
    met['balance_to_collision']=float(m['centered_absolute_defect']/max(abs(m['collision_X']),1e-300))
 r.update(status='PASS_SCOPED',metrics=met,run=m,hashes={f.name:sha(f) for f in dest.iterdir()})
 assert m['min_occupation']>=0 and m['number_defect']<2e-9 and m['centered_balance_defect']<2e-9 and m['max_be_residual']<=2e-11
 assert m['max_free_increase']<1e-9*max(N,1e-300)
 if ca['kind'] not in ('thermal','high_eq','zero'):assert met['action_gap']<2e-7,(name,met)
 else:assert met['action_absolute_per_max_f']<2e-13,(name,met)
 if name.startswith('live_reverse'):assert min(m[k0] for k0 in ('red_in','red_out','blue_in','blue_out'))>0
 if ca['drift']:assert max(m[k0] for k0 in ('max_drift_number','max_drift_centered','max_zone_centered','max_zone_number','partition_number','partition_X'))<2e-12
 results.append(r);print(name,'PASS',m['max_be_residual'],m['collision_energy_j_m3'],met.get('continuum_error',''),met.get('ode_signal_l1',''),flush=True)
(a.out/'RESULTS.json').write_text(json.dumps(dict(binary_sha256=sha(exe),cases=results),indent=2,allow_nan=False)+'\n')
print('DONE',len(results),flush=True)
