"""Locate dominant paired time-quadrature discrepancy using first-source arrivals."""
from pathlib import Path
import sys,numpy as np,json
D=Path(__file__).resolve().parent
sys.path.insert(0,str(D.parent/'r118c3h_paired_history'))
sys.path.insert(0,str(D.parent/'r118c3i_event_quadrature'))
from shared_gas_h import Clock,OriginalHyRecPrimitiveRateTable,B,P,R,_canonical_twophoton_table
from retarded import interpF
from full_bianchi_hyrec.trajectory.causal_virtual_redshift import _source_edges
from events import event_times
from numpy.polynomial.legendre import leggauss
def run():
 a,b=[np.load(D/f'full128_{k}.npz')['rows'] for k in [0,1]];c,d=[np.load(D/f'full256_{k}.npz')['rows'] for k in [0,1]]
 assert np.array_equal(a[:,0],c[::2,0])
 h=np.diff(a[:,0]);hf=np.diff(c[:,0]);err=h*(b[1:,4]-a[1:,4])-(hf*(d[1:,4]-c[1:,4])).reshape(-1,2).sum(axis=1)
 g=np.genfromtxt(B/'plusfine.csv',names=True,delimiter=',');ge=np.log(g['a']);F=np.stack([g[f'F{i}{j}'] for i in range(3) for j in range(3)],axis=1).reshape(-1,3,3)
 v=np.load(P);eta=-np.log1p(v['z']);src,ef,es=_source_edges(_canonical_twophoton_table(R).energy_eV);lr=np.log(es/ef)
 mu,w=leggauss(8);M,ph=np.meshgrid(mu,2*np.pi*np.arange(16)/16,indexing='ij');n=np.stack([np.sqrt(1-M*M)*np.cos(ph),np.sqrt(1-M*M)*np.sin(ph),M],axis=-1).reshape(-1,3)
 counts=np.zeros(len(h),int)
 for f in [F,np.broadcast_to(np.eye(3),F.shape)]:
  ev=event_times(ge,f,interpF(ge,f,eta[0]),n,eta[0],lr,eta[0],eta[128]);counts+=np.histogram(ev[np.isfinite(ev)],bins=a[:,0])[0]
 hit=counts>0
 m=Clock(h=.6735837,omega_cb=.31242079216478097,omega_r_h2=4.1578740068818545e-5,omega_de_h2=.3119234221656212,omega_b_h2=.02242,y_he_mass=.245,tcmb0_K=2.7255,table=OriginalHyRecPrimitiveRateTable.from_archive(R))
 z=v['z'];H=np.interp(-np.log1p(z),ge,g['h'])*2.1842852410855023e-18;old=np.array([m.cosmology(x)[0] for x in z])
 o=dict(integrated_pair_difference=float(err.sum()),paired_endpoint_difference=float((b[-1,1]-a[-1,1])-(d[-1,1]-c[-1,1])),event_count=int(counts.sum()),event_intervals=int(hit.sum()),abs_error_fraction_at_events=float(np.sum(abs(err[hit]))/np.sum(abs(err))),max_local_error=float(max(abs(err))),H_ratio_range=[float(min(H/old)),float(max(H/old))],scope='local paired integrated RHS discrepancy, event correlation only not proof of error mechanism; BASS H differs from historical FLRW baseline')
 (D/'EVENT_AUDIT.json').write_text(json.dumps(o,indent=2)+'\n');print(o)
if __name__=='__main__':run()
