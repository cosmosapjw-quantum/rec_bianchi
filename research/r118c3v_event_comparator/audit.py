import json,numpy as np,sys
from pathlib import Path
D=Path(__file__).resolve().parent
from finite_event import Map,Context
from scipy.integrate import solve_ivp
from spectral_source import R,_canonical_twophoton_table
from full_bianchi_hyrec.trajectory.causal_virtual_redshift import _source_edges
def run():
 data={(int(q['nt']),float(q['lambda_'])):q for f in D.glob('pair_*.json') for q in [json.loads(f.read_text())]}
 rows=[]
 for n in [32,64,128]:
  for ep in [.25,.5]:
   if (n,ep) not in data:continue
   a,b=data[n,ep],data[n,-ep];zero=data.get((n,0),{}).get('dx')
   rows.append(dict(nt=n,eps=ep,even=(a['dx']+b['dx'])/(2*ep**2),odd=(a['dx']-b['dx'])/(2*ep),zero_corrected=(a['dx']+b['dx']-2*zero)/(2*ep**2) if zero is not None else None,max_reference_residual=max(a['max_reference_residual'],b['max_reference_residual']),max_root=max(a['max_root'],b['max_root']),event_splits=[a['event_splits'],b['event_splits']]))
 c=Context(32);m=Map(c,.5)
 # Independent dense ODE evaluation at off-grid receiving points and retarded roots.
 lo=c.he[0]-max(c.lr)-.002;hi=c.he[-1];t0=c.he[0];rhs=lambda u,z:(-.5*c.clock.S(u)@z.reshape(3,3)).ravel()
 L=solve_ivp(rhs,(t0,lo),np.eye(3).ravel(),method='DOP853',rtol=2e-13,atol=2e-15,dense_output=True);H=solve_ivp(rhs,(t0,hi),np.eye(3).ravel(),method='DOP853',rtol=2e-13,atol=2e-15,dense_output=True)
 def ell(u,n):
  M=(L if u<t0 else H).sol(u).reshape(3,3);return u-np.log(np.linalg.norm(M@n))
 errs=[]
 for u in (c.he[:-1]+.371*np.diff(c.he))[::23]:
  ts=m.t(u)
  for i,j in [(0,0),(5,100),(12,222),(31,312)]:
   errs.append(abs(ell(ts[i,j],c.n[i])+c.lr[j]-ell(u,c.n[i])))
 z=np.load(D/'SPECTRAL_SOURCE.npz');src,ef,es=_source_edges(_canonical_twophoton_table(R).energy_eV)
 mask=(src>=0)&(src<len(z['energy']))
 energy_source_error=float(np.max(abs(es[mask]-z['energy'][src[mask]])))
 hit=json.loads((D/'FIRST_HIT.json').read_text())
 out=dict(rows=rows,max_dense_retarded_equation_residual=max(errs),tracked_source_energy_map_abs_eV=energy_source_error,first_hit=hit,scope='finite amplitude paired response, fixed H reference, nonidentical scalar baseline integrator; first crossing conditional test only')
 (D/'AUDIT.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
if __name__=='__main__':run()
