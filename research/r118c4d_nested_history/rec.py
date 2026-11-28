"""Nested dyadic retarded native H-only owner; independent actual HHe energy ledger."""
from pathlib import Path
import sys,json,numpy as np,hashlib,subprocess,io
D=Path(__file__).resolve().parent;P=D.parent;A=P/'r118c4a_quadratic_pair';Z=P/'r118c3z_refined_retarded';B=P/'r118c4b_global_quadratic'
sys.path.insert(0,str(D.parents[1]/'src'));sys.path.insert(0,str(P/'r118c3w_common_history'));sys.path.insert(0,str(P/'r118c3x_three_moments'))
from common_base import context
from positive3 import reconstruct as orig_reconstruct
def write(n,o):(D/n).write_text(json.dumps(o,indent=2)+'\n')
def run(kind,lam):
 old=np.load(B/'q3_128_0.npz');oldhe=old['he'];he=np.empty(2*len(oldhe)-1);he[::2]=oldhe;he[1::2]=.5*(oldhe[:-1]+oldhe[1:]);assert np.all(np.diff(he)>0)
 def ctx(nt):
  c=context(nt);assert np.array_equal(c.he,oldhe);assert max(np.diff(he))<min(c.lr)
  c.v=np.stack([np.interp(he,c.he,c.v[:,j]) for j in range(c.v.shape[1])],axis=1);c.he=he.copy();return c
 pp=P/'r118c3x_three_moments/positive3.py';z=pp.read_text();assert z.count('range(8)')==1 and z.count("method='highs'")==1
 z=z.replace('range(8)','range(32)').replace("method='highs'","method='highs',options={'primal_feasibility_tolerance':1e-10,'dual_feasibility_tolerance':1e-10}");ns0={};exec(compile(z,str(pp),'exec'),ns0)
 fallback=[]
 def recon(O,fr):
  try:return orig_reconstruct(O,fr)
  except ValueError as e:
   fallback.append(dict(original=str(e)));print('default positivity LP failed, try tighter feasibility',e,flush=True)
   return ns0['reconstruct'](O,fr)
 s=(A/'rec.py').read_text()
 def rep(a,b):
  nonlocal s
  assert s.count(a)==1,(a,s.count(a));s=s.replace(a,b)
 rep("s=(Z/'quadratic_generated.py').read_text()","s=(Z/'quadratic_generated.py').read_text().replace(\"tag=f'q3_\",\"tag=\\\"nested256_\\\"+f'q3_\")")
 rep("ns={'__file__':str(D/'quadratic_direct.py'),'__name__':'c4a_direct'};exec(compile(s,str(Z/'quadratic_generated.py'),'exec'),ns);return ns","ns={'__file__':str(D/'quadratic_direct.py'),'__name__':'c4d_direct'};exec(compile(s,str(Z/'quadratic_generated.py'),'exec'),ns);ns['context']=context;ns['reconstruct']=reconstruct;return ns")
 rep("def tag(nt,lam,ref):return f'q3_{nt}_{lam:g}'","def tag(nt,lam,ref):return 'nested256_'+f'q3_{nt}_{lam:g}'")
 ns={'__file__':str(D/'rec.py'),'__name__':'c4d_pair'};exec(compile(s,str(A/'rec.py'),'exec'),ns);ns['context']=ctx;ns['reconstruct']=recon
 try:ns[kind](128,lam,1)
 finally:write(f'LP_{kind}_{lam:g}.json',dict(kind=kind,lam=lam,fallback=fallback,old_mesh_sha256=hashlib.sha256(oldhe.tobytes()).hexdigest(),nested_mesh_sha256=hashlib.sha256(he.tobytes()).hexdigest(),steps=len(he)-1,source_sha256=hashlib.sha256((A/'rec.py').read_bytes()).hexdigest()))
def analyze():
 old=[json.loads((B/f'PAIR_q3_128_{l:g}.json').read_text()) for l in [-.5,.5]]
 direct=[json.loads(p.read_text()) for p in sorted(D.glob('nested256_q3_128_*.json'))];pairs=[json.loads(p.read_text()) for p in sorted(D.glob('PAIR_nested256_q3_128_*.json'))]
 o=dict(direct=direct,pairs=pairs,prior_128_even=(old[0]['delta_x']+old[1]['delta_x'])/.5,prior_128_odd=old[1]['delta_x']-old[0]['delta_x'],scope='nested exact dyadic refinement, same H-only owner and clock, finite amplitude; no continuum proof')
 if len(pairs)==2:
  a,b=sorted(pairs,key=lambda x:x['lam']);assert a['mesh_sha256']==b['mesh_sha256'];o.update(even=(a['delta_x']+b['delta_x'])/.5,odd=b['delta_x']-a['delta_x'],min_positive=min(a['min_stored_virtual_ratio'],b['min_stored_virtual_ratio']),max_direct_error=max(a['abs_disagreement'],b['abs_disagreement']),cells=a['cells_checked']+b['cells_checked'])
  # Compare the actual stable signed response at shared mesh nodes.
  za,zb=[np.load(D/f'PAIR_nested256_q3_128_{l:g}.npz') for l in [-.5,.5]];oa,ob=[np.load(B/f'PAIR_q3_128_{l:g}.npz') for l in [-.5,.5]]
  nr=za['rows'];pr=oa['rows'];assert np.array_equal(nr[::2,0],pr[:,0]);new=(za['rows'][:,1]+zb['rows'][:,1])/.5;prior=(oa['rows'][:,1]+ob['rows'][:,1])/.5;dd=new[::2]-prior
  # localization by cumulative response, not independent local truncation estimate.
  j=int(np.argmax(abs(dd)));o.update(max_cumulative_disagreement=float(abs(dd[j])),redshift_max_cumulative_disagreement=float(np.expm1(-pr[j,0])),endpoint_difference=float(dd[-1]),relative_change=float(abs(o['even']-o['prior_128_even'])/abs(o['even'])))
  np.savez_compressed(D/'NESTED_DIFFERENCE.npz',u=pr[:,0],new_even=new[::2],old_even=prior,difference=dd)
 write('NESTED_SUMMARY.json',o);print(o,flush=True)
def ledger():
 repo=Path.home()/'worktrees/rei-htt-thomson-20261124';rev='0e624af4668c7722759ccf781d91e15362b6d451';p='research/r118c3u_positive_owner/birth_1024_32ray/'
 def blob(n):return subprocess.check_output(['git','-C',str(repo),'show',rev+':'+n])
 raw=blob(p+'history.csv');src=blob('research/r118c3u_positive_owner/metric_bridge.rs');ret=blob(p+'RETURN.txt');h=np.genfromtxt(io.BytesIO(raw),names=True,delimiter=',',dtype=np.longdouble);assert len(h)==484 and h['accepted'][-1]==483 and 'status=COMPLETE' in ret.decode()
 # Native source formula, physical units eV/H. Long-double contractions of recorded binary64 values.
 f=np.longdouble('.2454')/(4*(1-np.longdouble('.2454')));k=np.longdouble('8.617333262145e-5');chi=np.array([13.598434599702,f*24.587389011,f*(24.587389011+54.41776)],dtype=np.longdouble)
 x=np.stack([h['xHII'],h['xHeII'],h['xHeIII']],axis=1);xe=x@np.array([1,f,2*f],dtype=np.longdouble);b=x@chi;w=1.5*k*h['T']*(1+f+xe)
 E=h['w']+h['b']+h['primary']+h['cool']+h['spec'];E0=E[0];work=h['thermal_work']+h['photon_work']+h['boundary']+h['secondary_work'];recon=E-E0-h['source']+work
 trace=h['secPxx']+h['secPyy']+h['secPzz'];secondary=h['cool']+h['spec'];expected=h['ne'][0]*(h['a'][0]/h['a'])**3*xe/xe[0]
 cols=['w','b','primary','cool','spec','source','thermal_work','photon_work','boundary','secondary_work'];delta={c:float(h[c][-1]-h[c][0]) for c in cols};du=np.diff(np.log(h['a']));local=np.diff(E)-np.diff(h['source'])+np.diff(work)
 assert max(abs(recon-h['ledger']))<1e-13
 assert max(abs(trace-secondary))<1e-13
 out=dict(pinned_REI=rev,history_sha256=hashlib.sha256(raw).hexdigest(),bridge_sha256=hashlib.sha256(src).hexdigest(),accepted=483,delta=delta,gas_energy_change=float((h['w']+h['b'])[-1]-(h['w']+h['b'])[0]),radiation_stock_change=float((h['primary']+secondary)[-1]-(h['primary']+secondary)[0]),total_work_change=float(work[-1]-work[0]),ledger_max=float(max(abs(recon))),ledger_reconstruction_max_abs=float(max(abs(recon-h['ledger']))),local_residual_max=float(max(abs(local))),local_residual_sum=float(sum(local)),pressure_trace_max_abs=float(max(abs(trace-secondary))),binding_reconstruction_max_abs=float(max(abs(b-h['b']))),thermal_reconstruction_max_abs=float(max(abs(w-h['w']))),charge_ne_relative=float(max(abs(expected/h['ne']-1))),scope='actual C3U native reionization HHe gas and signed primary/secondary stocks; independent ledger reconstruction; not primordial recombination radiation or full DG3 source ledger')
 np.savez_compressed(D/'ENERGY_LEDGER.npz',u=np.log(h['a']),E=E,reconstructed=recon,recorded=h['ledger'],thermal=h['w'],binding=h['b'],primary=h['primary'],cool=h['cool'],spec=h['spec'],source=h['source'],work=work,local=local,trace=trace,secondary=secondary)
 write('HHE_ENERGY_LEDGER.json',out);print(out,flush=True)
if __name__=='__main__':
 if sys.argv[1]=='ledger':ledger()
 elif sys.argv[1]=='analyze':analyze()
 else:run(sys.argv[1],float(sys.argv[2]))
