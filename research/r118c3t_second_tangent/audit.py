"""Audit projected impulse recurrence and actual saved gas results."""
import sys,json,numpy as np
from pathlib import Path
D=Path(__file__).resolve().parent
from regular import Context
def run():
 rows={}
 for n in [32,64]:
  c=Context(n);p=np.load(D/f'events_{n}.npz');he=p['he'];assert np.array_equal(he,c.he)
  A=np.zeros_like(p['feedback_A']);B=A.copy();timeN=timeV=0.;l1A=l1B=0.
  for i,u in enumerate(he):
   t=u+c.lr;ok=t<=he[-1];j=np.searchsorted(he,t[ok],side='right')-1;j=np.minimum(j,len(he)-2);s=(t[ok]-he[j])/(he[j+1]-he[j]);ch=np.flatnonzero(ok)
   aa=p['out_A'][i,c.src[ok]];bb=p['out_B'][i,c.src[ok]]
   if len(ch) and np.any(aa!=0):assert min(j)>i
   np.add.at(A,(j,ch),(1-s)*aa);np.add.at(A,(j+1,ch),s*aa)
   np.add.at(B,(j,ch),(1-s)*bb);np.add.at(B,(j+1,ch),s*bb)
   timeN+=np.sum(aa*(t[ok]-he[0]));timeV+=np.sum(bb*(t[ok]-he[0]));l1A+=np.sum(abs(aa));l1B+=np.sum(abs(bb))
  errB=float(np.sum(abs(B-p['feedback_B']))/max(l1B,1e-300));assert errB<1e-12
  # The A residual is the additional exact-time T1 first-order cross source;
  # compare its norm to the total cross-source L1 upper bound.
  q=json.loads((D/f'events_{n}.json').read_text());cross=float(np.sum(abs(A-p['feedback_A'])));assert cross<=q['ledger']['cross_l1']*(1+1e-10)
  mA=float(abs(np.sum(A*(he-he[0])[:,None])-timeN)/max(l1A*(he[-1]-he[0]),1e-300));mB=float(abs(np.sum(B*(he-he[0])[:,None])-timeV)/max(l1B*(he[-1]-he[0]),1e-300));assert max(mA,mB)<1e-12
  rr=[]
  for tag in ['', '_events']:
   z=np.load(D/f'regular_{n}{tag}.npz');o=json.loads((D/f'regular_{n}{tag}.json').read_text());assert np.array_equal(z['rows'][:,0],he[1:]) and np.isfinite(z['rows']).all() and abs(z['rows'][-1,1]-o['x2'])<1e-24
   assert o['first_reproduction_relative']<1e-4
   if tag:assert np.array_equal(z['rows'][:,5:7],p['gas_jump'][1:])
   rr.append(o['x2'])
  rows[str(n)]=dict(B_recurrence_relative=errB,A_cross_residual_L1=cross,affine_time_A=mA,affine_time_B=mB,x2_regular=rr[0],x2_events=rr[1],gas_jump_l1=q['gas_jump_l1'],max_native_jet_second_relative=max(v['second_relative'] for tag in ['', '_events'] for v in json.loads((D/f'regular_{n}{tag}.json').read_text())['jet_checks']))
 a,b=rows['32'],rows['64'];q=json.loads((D/'TWO_PHOTON.json').read_text());assert q['samples']==128 and q['max_source_energy_relative']<1e-14
 out=dict(rows=rows,regular_sign_changes=bool(a['x2_regular']*b['x2_regular']<0),event_refinement_relative=abs(a['x2_events']-b['x2_events'])/abs(b['x2_events']),two_photon_samples=q['samples'],scope='discrete projected singular ledger verified, order-two continuum not converged; time projection and source knot derivative interpolation remain model/numerics obligations')
 (D/'AUDIT.json').write_text(json.dumps(out,indent=2)+'\n');print(out,flush=True)
if __name__=='__main__':run()
