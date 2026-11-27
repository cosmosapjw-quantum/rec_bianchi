"""Audit exact event ledger and partial second-order weak response.
Recompute actual native tau at every event using interpolated reference gas;
test interpolation error in outgoing impulse mass. Rebuild chains independently.
"""
import sys,json,numpy as np
from pathlib import Path
from dataclasses import replace
D=Path(__file__).resolve().parent
sys.path.insert(0,str(D.parent/'r118c3r_retarded_tangent'))
from frozen import p
def run():
 rows={};g=np.genfromtxt(p.B/'plusfine.csv',names=True,delimiter=',');ge=np.log(g['a'])
 m=p.Clock(h=.6735837,omega_cb=.31242079216478097,omega_r_h2=4.1578740068818545e-5,omega_de_h2=.3119234221656212,omega_b_h2=.02242,y_he_mass=.245,tcmb0_K=2.7255,table=p.OriginalHyRecPrimitiveRateTable.from_archive(p.R))
 tab=p._canonical_twophoton_table(p.R);src,ef,es=p._source_edges(tab.energy_eV);lr=np.log(es/ef)
 # For each stored arrival, check exact native direct propagation to next
 # arrival (if present) against interpolated tau. Use independent dictionary
 # keyed by rounded time/channel/generation; channel map injective.
 inv={int(s):k for k,s in enumerate(src)};zero=np.zeros(313)
 for n in [32,64]:
  a=json.loads((D/f'impulse_{n}.json').read_text());z=np.load(D/f'impulse_{n}.npz');t=z['event_time'];k=z['event_channel'];amp=z['event_mass'];gen=z['event_generation'];v=np.load(D.parent/f'r118c3p_prehistory/z1110_n{n}_0.npz')['rows']
  assert len(t)==3536 and max(gen)==31 and np.all(np.diff(t)>=0)
  # Sum exact masses at each key to handle coincident paths, should be unique.
  lookup={}
  for i,(u,j,h) in enumerate(zip(t,k,gen)):lookup.setdefault((round(float(u),13),int(j),int(h)),[]).append(i)
  errs=[];l1=0.;res=0.;checks=0;max_abs=0.
  # Check all first generations + every 17th subsequent event (bounded).
  for i in range(len(t)):
   if gen[i]!=1 and i%17:continue
   j=int(k[i]);u=float(t[i]);h=int(gen[i])
   if j>=311 or j not in inv:continue
   jj=inv[j];up=u+lr[jj];ids=lookup.get((round(up,13),jj,h+1),[])
   if not ids:continue
   # For coincident paths use only uniquely identifiable records.
   if len(ids)!=1:continue
   xx,T=[np.interp(u,v[:,0],v[:,k]) for k in [1,2]];H=np.interp(u,ge,g['h'])*2.1842852410855023e-18
   s=p.populate_original_full_atomic(replace(m,H=H),z=np.expm1(-u),xHII=xx,xe=xx,Tm_K=T,incoming_virtual=zero[:311],incoming_lyman=zero[311:])
   expect=np.exp(-s.Dtau[j])*amp[i];actual=amp[ids[0]];den=float(np.sum(abs(expect)));err=float(np.sum(abs(actual-expect)))
   l1+=den;res+=err;max_abs=max(max_abs,err);checks+=1
   if den>1e-30:errs.append(err/den)
  assert checks>50
  # Absolute mass mismatch is the useful metric for nearly opaque channels.
  rows[str(n)]=dict(event_count=len(t),max_generation=int(max(gen)),checked_transitions=checks,weighted_mass_relative=res/max(l1,1e-300),max_absolute_mass_error=max_abs,max_relative_above_1e_30=max(errs),regular_mean=a['max_regular_mean'],impulse_mean=a['max_event_mean'],regular_x2=a['regular_x2'],impulse_x2=a['impulse_x2'],partial_x2=a['partial_x2'],max_coupled_ratio=max(v['coupled_relative'] for v in a['affine_checks']))
 en=json.loads((D/'PHYSICAL_RESERVOIR.json').read_text())['runs']
 o=dict(rows=rows,regular_relative=abs(rows['32']['regular_x2']-rows['64']['regular_x2'])/abs(rows['64']['regular_x2']),impulse_relative=abs(rows['32']['impulse_x2']-rows['64']['impulse_x2'])/abs(rows['64']['impulse_x2']),partial_relative=abs(rows['32']['partial_x2']-rows['64']['partial_x2'])/abs(rows['64']['partial_x2']),energy_threshold_relative=abs(en['16']['threshold_binding_change_eV_H']-en['32']['threshold_binding_change_eV_H'])/abs(en['32']['threshold_binding_change_eV_H']),scope='actual reference-gas event tau recomputation; partial first-order outgoing action only; second-order output feedback unresolved. Threshold binding energy only, not full physical radiation reservoir')
 (D/'AUDIT.json').write_text(json.dumps(o,indent=2)+'\n');print(o,flush=True)
if __name__=='__main__':run()
