"""Verify actual C4I surviving spectrum support at the C4J HMLA handoff."""
from pathlib import Path
import json,hashlib,numpy as np
D=Path(__file__).resolve().parent
p=D.parent/'r118c4i_weak_adjoint/HI_FEEDBACK.npz'
c=json.loads((D/'HMLA_CONTINUATION.json').read_text())
rows=[]
with np.load(p) as z:
 a=np.exp(z['u'][-1]);thr=13.598434599702
 for bins in (512,1024,2048):
  e=z[f'E_{bins}']/a;N=z[f'N_{bins}'];above=e>thr
  net=float(N[above].sum());total=float(N.sum());absolute=float(abs(N[above]).sum())
  rr=[r for r in c['rows'] if r['bins']==bins];g=max(abs(r['absorbed_per_H']-net) for r in rr)
  assert g<1e-28
  rows.append(dict(bins=bins,above_threshold_bins=int(above.sum()),net_above_per_H=net,absolute_above_per_H=absolute,total_net_per_H=total,fraction_above=net/total,max_absorbed_gap=g))
out=dict(rows=rows,threshold_eV=thr,z=c['rows'][0]['z_start'],input_sha=hashlib.sha256(p.read_bytes()).hexdigest(),scope='audit actual surviving spectrum only; all above-threshold net stock consumed in bounded HMLA continuation; no assertion about fresh helium emissivity')
(D/'HANDOFF_THRESHOLD_AUDIT.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
