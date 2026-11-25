"""Direct positive event angular lift and native evolution on actual REC baths.
Independent isotropic source action, edge-array oracle, numerical convergence.
All raw compiled angular source and binary graphs retained on workstation."""
import argparse,hashlib,json,math,pathlib,struct,subprocess,time
import numpy as np
from scipy.integrate import lebedev_rule
from scipy.constants import h,k
from full_bianchi_hyrec.recoil.calibrated_angular import assemble
from full_bianchi_hyrec.standalone_line import prepare,initial,line
P=pathlib.Path
p=argparse.ArgumentParser();p.add_argument('--source',type=P,required=True);p.add_argument('--binary',type=P,required=True);p.add_argument('--out',type=P,required=True);p.add_argument('--only',default='');a=p.parse_args()
a.out.mkdir(exist_ok=False,parents=True);exe=a.binary.resolve();sha=lambda p:hashlib.sha256(P(p).read_bytes()).hexdigest()
def export_graph(path,q,d,w,ed):
    na=len(w);n=len(q['x'])*na
    with path.open('xb') as f:
        f.write(struct.pack('<8sIIdd',b'RECAWG01',n,len(ed['K']),q['nu'],q['dnu']))
        for i,x in enumerate(q['x']):
            for j in range(na):
                ww=q['w'][i];zz=q['z'][i];f.write(struct.pack('<5dI',x,q['g'][i]*w[j],*d[j],len(ww)));f.write(np.asarray(ww,dtype='<f8').tobytes());f.write(np.asarray(zz,dtype='<f8').tobytes())
        z=np.empty(len(ed['K']),dtype=[('i','<u4'),('j','<u4'),('k','<f8')]);z['i']=ed['i'];z['j']=ed['j'];z['k']=ed['K'];f.write(z.tobytes())
def initial_angular(q,d,kind):
    if kind in ('hot','thermal','narrow'):return np.repeat(initial(q,kind)[:,None],len(d),axis=1)
    out=np.zeros((len(q['x']),len(d)))
    for i,(x,w,z) in enumerate(zip(q['xx'],q['w'],q['z'])):
        if kind=='dipole':
            A=.15*(1+.2*d[:,0][None,:]+.1*np.tanh(x[:,None]/3))
        elif kind=='dilute':
            A=q['z0']*(1+.2*d[:,0][None,:]+.1*np.tanh(x[:,None]/3))
        elif kind=='vacuum':
            A=.2*(1+.2*np.tanh(x[:,None]/3))*np.broadcast_to((d[:,0]>0)[None,:],(len(x),len(d)))
        else:raise ValueError(kind)
        v=A*z[:,None];out[i]=w@(v/(1-v))
    return out
def reference(q,d,w,ed,f):
    na=len(w);g=np.repeat(q['g'],na)*np.tile(w,len(q['x']));x=np.repeat(q['x'],na);dr=np.tile(d,(len(q['x']),1));moment=(1+q['dnu']/q['nu']*x)[:,None]*dr
    # Independent vectorized inverse with supported Gauss quadrature; same
    # source graph, not a continuum reference.
    maxq=max(map(len,q['w']));W=np.array([np.pad(v,(0,maxq-len(v))) for v in q['w']]);Z=np.array([np.pad(v,(0,maxq-len(v)),constant_values=1) for v in q['z']])
    f=f.reshape(len(q['x']),na);A=f/(1+f)/np.sum(W*Z,axis=1)[:,None]
    for _ in range(12):
        y=A[:,:,None]*Z[:,None,:];r=np.sum(W[:,None,:]*y/(1-y),axis=2)-f;da=np.sum(W[:,None,:]*Z[:,None,:]/(1-y)**2,axis=2)
        delta=r/da;A-=delta
        if np.max(abs(delta)/np.maximum(abs(A),1e-300))<1e-15:break
    f=f.ravel();A=A.ravel();i=ed['i'];j=ed['j']
    v=ed['K']*(1+f[i])*(1+f[j])*(A[j]-A[i])
    rate=(np.bincount(i,weights=v,minlength=len(f))-np.bincount(j,weights=v,minlength=len(f)))/g
    dx=x[i]-x[j];dp=moment[i]-moment[j];ex=float(np.sum(v*dx));p=np.sum(v[:,None]*dp,axis=0)
    return rate,ex,p,float(np.sum(abs(v*dx))),float(np.sum(abs(v[:,None]*dp))),float(g@f)
def native(name,path,q,d,w,ed,f,dt,steps):
    case=a.out/(name+'.case');case.write_text(f'rec_angular_line_case_v1\n{dt:.17g} {steps}\n'+line(f))
    dest=a.out/name;cmd=[str(exe),str(path),str(case),str(dest)]
    proc=subprocess.run(cmd,capture_output=True,text=True,timeout=100)
    if proc.returncode:
        return dict(case=name,status='REJECTED_NATIVE',command=cmd,error=proc.stderr,dt=dt,steps=steps)
    m=dict(x.split('=',1) for x in (dest/'run.txt').read_text().splitlines())
    for key,v in list(m.items()):
        try:
            z=float(v)
            if math.isfinite(z):m[key]=z
        except ValueError:pass
    st=np.genfromtxt(dest/'state.tsv',names=True,delimiter='\t');r,e,p,gx,gp,N=reference(q,d,w,ed,f)
    rms=float(np.sum(abs(st['initial_rate']-r))/max(np.sum(abs(r)),np.sum(abs(f))*1e-12,1e-300))
    eerr=abs(m['initial_X_rate']-e)/max(gx,N*1e-15,1e-300);perr=np.max(abs(np.array([m['initial_P_rate_'+s] for s in 'xyz'])-p))/max(gp,N*1e-15,1e-300)
    assert m['minimum_f']>=0 and m['number_defect']<2e-10 and m['max_be_residual']<=2e-11
    assert m['initial_force_defect']<2e-10 and m['initial_number_defect']<2e-10
    assert m['max_free_increase']<max(N,1e-300)*1e-9
    assert rms<2e-3 and eerr<2e-3 and perr<2e-3,(name,rms,eerr,perr)
    return dict(case=name,status='PASS_SCOPED',command=cmd,dt=dt,steps=steps,run=m,metrics=dict(action_gap=rms,centered_gap=eerr,momentum_gap=float(perr),N=N,centered_per_photon=m['initial_X_rate']/max(N,1e-300),momentum_per_photon=[m['initial_P_rate_'+s]/max(N,1e-300) for s in 'xyz']),case_sha256=sha(case),hashes={p.name:sha(p) for p in dest.iterdir()})
graphs=[];results=[]
# 1/4-subcell actual source. Restrict finest angular graph to 70 nodes
# per direction for bounded workload.
for bath,sub,order in [('z1100',1,3),('z1100',1,5),('z1100',1,7),('z1100',4,5),('z1300',1,5),('z900',1,5)]:
    name=f'{bath}_s{sub}_o{order}'
    if not name.startswith(a.only):continue
    with np.load(a.source/(bath+'.npz')) as z:data={k:z[k] for k in z.files if not k.startswith('K') or k==f'K{sub}'}
    q=prepare(data,sub);d,w=lebedev_rule(order);d=d.T;w=w/(4*np.pi)
    t=time.monotonic();ed=assemble(data,sub,d,w);gp=a.out/(name+'.bin');export_graph(gp,q,d,w,ed)
    graph={k:v.tolist() if hasattr(v,'tolist') else v for k,v in ed.items() if k not in ('i','j','K')}
    # angular measure row proof: isotropic action should exactly reduce
    # to the original frequency graph, including same-node null edges.
    i,j=ed['i'],ed['j'];fi=i//len(w);fj=j//len(w)
    mask=fi!=fj;agg=np.bincount(fi[mask]*len(q['x'])+fj[mask],weights=ed['K'][mask],minlength=len(q['x'])**2).reshape(q['K'].shape)
    ref=np.triu(q['K'],1);err=float(np.sum(abs(agg-ref))/np.sum(ref))
    assert err<5e-12
    graph.update(case=name,bath=bath,sub=sub,order=order,edges=len(ed['K']),isotropic_mass_gap=err,graph_path=str(gp),graph_sha256=sha(gp),wall_s=time.monotonic()-t)
    graphs.append(graph);print('graph',graph,flush=True)
    (a.out/'GRAPHS.json').write_text(json.dumps(graphs,indent=2,allow_nan=False)+'\n')
    tasks=[('thermal',0.,0),('hot',0.,0),('dipole',.25,2),('dilute',.5,2)]
    if bath=='z1100' and order==3 and sub==1:tasks += [('vacuum',.1,1),('dipole',.25,1),('dipole',.25,4),('dipole',.25,8)]
    if bath=='z1100' and order==7 and sub==1:tasks += [('dilute',100.,2)]
    for kind,dt,steps in tasks:
        f=initial_angular(q,d,kind).ravel();label=name+f'_{kind}_t{dt:g}_n{steps}'
        r=native(label,gp,q,d,w,ed,f,dt,steps);r.update(graph=name,kind=kind)
        if r['status']=='PASS_SCOPED' and kind=='hot':
            r['metrics']['direct_source_error']=abs(r['run']['initial_X_rate']-data['direct'][0])/abs(data['direct'][0])
        results.append(r);print(label,r['status'],r.get('error',''),r.get('metrics',{}),flush=True)
        (a.out/'RESULTS.json').write_text(json.dumps(dict(binary_sha256=sha(exe),graphs=graphs,cases=results),indent=2,allow_nan=False)+'\n')
