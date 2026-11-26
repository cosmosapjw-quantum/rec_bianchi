"""Independent event arrival and corrected accepted residual audit."""
from pathlib import Path
import numpy as np,json,sys
D=Path(__file__).resolve().parent
sys.path.insert(0,str(D.parent/'r118c3h_paired_history'))
from shared_gas_h import B,P,R,_canonical_twophoton_table
from retarded import interpF
from full_bianchi_hyrec.trajectory.causal_virtual_redshift import _source_edges
def main():
 v=np.load(P);eta=-np.log1p(v['z']);g=np.genfromtxt(B/'plusfine.csv',names=True,delimiter=',');ge=np.log(g['a'])
 F=np.stack([g[f'F{i}{j}'] for i in range(3) for j in range(3)],axis=1).reshape(-1,3,3)
 _,ef,es=_source_edges(_canonical_twophoton_table(R).energy_eV);lr=np.log(es/ef)
 rows={}
 for label in [f'correct{n}_{a}' for n in [256,512,1024] for a in [0,1]]+[f'angular32_1024_{a}' for a in [0,1]]:
  z=np.load(D/(label+'.npz'));a=z['rows'].astype(np.longdouble);events=z['events'];n=z['rays'];angular=label.endswith('_1')
  f=F if angular else np.broadcast_to(np.eye(3),F.shape)
  p=n@interpF(ge,f,eta[63]);ii,jj=np.where(np.isfinite(events))
  t=events[ii,jj];mat=interpF(ge,f,t);rr=np.linalg.norm(np.linalg.solve(np.swapaxes(mat,-1,-2),p[ii,:,None])[...,0],axis=1)
  s=np.linalg.norm(np.linalg.solve(interpF(ge,f,eta[0]).T,p.T).T,axis=1)
  roots=t-np.log(rr)-eta[0]+np.log(s[ii])-lr[jj]
  h=np.diff(a[:,0]);res=np.diff(a[:,1])-h*((a[1:,3]+a[:-1,3])/2+a[1:,10])
  L=z['line'];assert min(L[:,0])>=0 and min(L[:,1])>=0
  rows[label]=dict(max_event_root=float(np.max(abs(roots))),max_corrected_residual=float(np.max(abs(res))),max_residual_vs_stored=float(np.max(abs(res-a[1:,5]))),line_signed_error=float(np.max(abs(L[:,2]-L[:,3]))))
  assert rows[label]['max_event_root']<1e-12 and rows[label]['max_corrected_residual']<1e-12
 pairs=json.loads((D/'REFINEMENT.json').read_text());v=[pairs[str(n)]['corrected'] for n in [256,512,1024]]
 order=np.log2(abs((v[0]-v[1])/(v[1]-v[2])))
 j=[json.loads((D/f'angular32_1024_{a}.json').read_text()) for a in [0,1]];low=j[1]['x']-j[0]['x']
 out=dict(rows=rows,apparent_order=float(order),first_order_extrapolation=2*v[2]-v[1],delta_128=v[2],delta_32=low,angular_difference=low-v[2],scope='finite error diagnostics, no certified continuum sign or magnitude')
 (D/'AUDIT.json').write_text(json.dumps(out,indent=2)+'\n');print(out)
if __name__=='__main__':main()
