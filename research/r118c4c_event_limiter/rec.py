"""C4C same 64-grid owner; isolate event alignment and high-degree limiter."""
from pathlib import Path
import sys,json,numpy as np,hashlib,subprocess,io
D=Path(__file__).resolve().parent;P=D.parent;A=P/'r118c4a_quadratic_pair';Z=P/'r118c3z_refined_retarded'
sys.path.insert(0,str(D.parents[1]/'src'));sys.path.insert(0,str(P/'r118c3w_common_history'));sys.path.insert(0,str(P/'r118c3x_three_moments'))
from common_base import context
from positive3 import reconstruct as orig_reconstruct
def write(n,o):(D/n).write_text(json.dumps(o,indent=2)+'\n')
def run(mode,kind,lam):
 assert mode in ['degree8','degree8tight','aligned']
 deg=8 if mode.startswith('degree8') else 6
 def ctx(nt):
  c=context(nt)
  if mode=='aligned':
   old=c.he.copy();he=old.copy();arr=old[0]+c.lr[[237,238]];sel=[]
   for u in arr:
    j=int(np.argmin(abs(he-u)));assert 0<j<len(he)-1;sel.append(j);he[j]=u
   assert len(set(sel))==2 and np.all(np.diff(he)>0) and max(np.diff(he))<min(c.lr)
   c.v=np.stack([np.interp(he,old,c.v[:,j]) for j in range(c.v.shape[1])],axis=1);c.he=he
  return c
 def recon(O,fr):return reconstruct_checked(O,fr,degree=deg)
 reconstruct_checked=orig_reconstruct
 if mode=='degree8tight':
  pp=P/'r118c3x_three_moments/positive3.py';z=pp.read_text();assert z.count('range(8)')==1 and z.count("method='highs'")==1
  z=z.replace('range(8)','range(32)').replace("method='highs'","method='highs',options={'primal_feasibility_tolerance':1e-10,'dual_feasibility_tolerance':1e-10}")
  ns0={};exec(compile(z,str(pp),'exec'),ns0);reconstruct_checked=ns0['reconstruct']
 s=(A/'rec.py').read_text()
 def rep(a,b):
  nonlocal s
  assert s.count(a)==1,(a,s.count(a));s=s.replace(a,b)
 rep("s=(Z/'quadratic_generated.py').read_text()","s=(Z/'quadratic_generated.py').read_text().replace('314,7','314,"+str(deg+1)+"').replace(\"tag=f'q3_\",\"tag=\\\""+mode+"_\\\"+f'q3_\")")
 rep("ns={'__file__':str(D/'quadratic_direct.py'),'__name__':'c4a_direct'};exec(compile(s,str(Z/'quadratic_generated.py'),'exec'),ns);return ns","ns={'__file__':str(D/'quadratic_direct.py'),'__name__':'c4c_direct'};exec(compile(s,str(Z/'quadratic_generated.py'),'exec'),ns);ns['context']=context;ns['reconstruct']=reconstruct;return ns")
 rep("def tag(nt,lam,ref):return f'q3_{nt}_{lam:g}'","def tag(nt,lam,ref):return '"+mode+"_'+f'q3_{nt}_{lam:g}'")
 s=s.replace('B=np.zeros((N,nr,314,7))','B=np.zeros((N,nr,314,'+str(deg+1)+'))')
 ns={'__file__':str(D/'rec.py'),'__name__':'c4c_pair'};exec(compile(s,str(A/'rec.py'),'exec'),ns);ns['context']=ctx;ns['reconstruct']=recon
 ns[kind](64,lam,1)
def analysis():
 prev=json.loads((A/'FINAL_PAIR_SUMMARY.json').read_text());print('prior',prev,flush=True)
 rows=[]
 for mode in ['degree8','degree8tight','aligned']:
  direct=[json.loads((D/f'{mode}_q3_64_{lam:g}.json').read_text()) for lam in [0.,-.5,.5] if (D/f'{mode}_q3_64_{lam:g}.json').exists()]
  pairs=[json.loads((D/f'PAIR_{mode}_q3_64_{lam:g}.json').read_text()) for lam in [-.5,.5] if (D/f'PAIR_{mode}_q3_64_{lam:g}.json').exists()]
  row=dict(mode=mode,direct=direct,pairs=pairs)
  if len(pairs)==2:
   a,b=pairs;assert a['mesh_sha256']==b['mesh_sha256'];row.update(even=(a['delta_x']+b['delta_x'])/.5,odd=b['delta_x']-a['delta_x'],cells=sum(p['cells_checked'] for p in pairs),min_positive=min(p['min_stored_virtual_ratio'] for p in pairs),max_direct_error=max(p['abs_disagreement'] for p in pairs))
  if len(direct)==3:
   src=np.load(D/f'{mode}_q3_64_0.npz');he=src['he'];base=np.load(A/'q3_64_0.npz')['he'];assert len(he)==len(base)
   row.update(mesh_changes=int(np.count_nonzero(he!=base)),max_mesh_shift=float(np.max(abs(he-base))),limited=[int(p['limited_cells']) for p in direct])
   row['limit_events']={}
   for lam in [-.5,.5]:
    v=np.load(D/f'{mode}_q3_64_{lam:g}.npz')['limits'];row['limit_events'][str(lam)]={str(int(j)):int(np.count_nonzero(v[:,3]==j)) for j in np.unique(v[:,3])}
  rows.append(row)
 write('ISOLATION.json',dict(rows=rows,scope='only source-cell reconstruction degree and two receiving scalar-onset knots varied; no fully event-aligned continuum'))
 print(rows,flush=True)
def donor():
 # Actual native point rows from exact REI C4A final commit, conditional zero-photo. Recompute derivative in independent physical energy observable.
 repo=Path.home()/'worktrees/rei-htt-thomson-20261124';rev='6fc8823bd531b2d62bf43ab5c2269c2c8d748349';prefix='research/r118c4a_native_chemistry/'
 def blob(n):return subprocess.check_output(['git','-C',str(repo),'show',rev+':'+prefix+n])
 raw=blob('POINT.csv');x=np.genfromtxt(io.BytesIO(raw),names=True,delimiter=',');hraw=blob('ACTUAL_HISTORY.csv');h=np.genfromtxt(io.BytesIO(hraw),names=True,delimiter=',')
 f=.2454/(4*(1-.2454));chi=np.array([13.598434599702,f*24.587389011,f*(24.587389011+54.41776)]);C=np.array([1,f,2*f]);rows=[]
 for i in np.unique(x['snapshot']).astype(int):
  v=x[x['snapshot']==i];r=v[v['col']==-1][0];q=np.array([r[k] for k in ['x','y','z','w']]);rates=np.array([r[k] for k in ['fx','fy','fz','fw']]);ne=h['nh_m3'][i]*(C@q[:3]);kappa=299792458*6.6524587051e-29*ne/(2.1842852410855023e-18*h['h'][i])
  def observable(t):
   f0=np.array([t[k] for k in ['fx','fy','fz','fw']]);return np.array([C@f0[:3],f0[3],chi@f0[:3],f0[3]+chi@f0[:3]])
  f0=observable(r);scale=np.array([h['xHII'][0],1e-4,1e-4,h['w_eV_per_H'][0]]);Js=[]
  for ep in [.02,.01,.005,.0025]:
   J=[]
   for j in range(4):
    def get(e):
     rr=v[(v['col']==j)&np.isclose(v['eps'],e,rtol=1e-12,atol=1e-16)];assert len(rr)>=1;return observable(rr[0])
    if np.any((v['col']==j)&np.isclose(v['eps'],-ep,rtol=1e-12,atol=1e-16)):a=(get(ep)-get(-ep))/(2*ep)
    else:a=(-3*f0+4*get(ep)-get(2*ep))/(2*ep)
    J.append(a/scale[j])
   Js.append(np.array(J).T)
  J=Js[-1];assert np.linalg.norm(J[3]-J[1]-J[2])<1e-9
  rows.append(dict(snapshot=int(i),xe=float(C@q[:3]),opacity=float(kappa),energy_eV_H=float(q[3]+chi@q[:3]),rates_per_du=dict(zip(['xe','thermal_eV_H','binding_eV_H','gas_eV_H'],f0.tolist())),jacobian=J.tolist(),FD_refine=[float(np.linalg.norm(a-b)/np.linalg.norm(b)) for a,b in zip(Js[:-1],Js[1:])],native_charge_res_max=float(max(abs(v['charge_res']))),native_energy_res_max=float(max(abs(v['energy_res'])))))
 write('HHE_ENERGY_RESPONSE.json',dict(pinned_REI=rev,point_sha256=hashlib.sha256(raw).hexdigest(),history_sha256=hashlib.sha256(hraw).hexdigest(),binding_gradient=chi.tolist(),charge_gradient=C.tolist(),rows=rows,scope='actual prior native zero-photo point evaluations; energy/charge observable Jacobian independently reconstructed; no full primordial HHe evolution or radiation closure'))
 print(rows,flush=True)
if __name__=='__main__':
 if sys.argv[1]=='analyze':analysis()
 elif sys.argv[1]=='donor':donor()
 else:run(sys.argv[1],sys.argv[2],float(sys.argv[3]))
