"""Independent present-day comoving spectral moments, not an observed spectrum."""
from pathlib import Path
import json,hashlib,numpy as np
from scipy.constants import e,h
D=Path(__file__).resolve().parent
inp=D/'FRESH_HEI.npz';z=np.load(inp);ref=json.loads((D/'FRESH_HEI.json').read_text())
rows=[]
for r in ref['rows']:
 n=r['steps'];q=z[f'q_{n}'];a=z[f'He_N_{n}'];b=z[f'H_N_{n}'];g=z[f'gas_{n}'];bg=z[f'base_{n}'];u=z[f'u_{n}']
 assert np.all(np.diff(q)>0) and np.isfinite(a).all() and np.isfinite(b).all()
 assert abs(b.sum()-r['H_photon_count'])<1e-15
 assert abs(np.max(abs((g-bg)@np.array([-1.,1.])))-r['max_xe_change'])<1e-15
 def stat(v):
  s=float(v.sum());k=float(v@q);neg=float(np.minimum(v,0).sum())
  return dict(net_number_per_H=s,comoving_energy_eV_per_H=k,mean_comoving_energy_eV=k/s,mean_frequency_GHz=k/s*e/h/1e9,negative_net_weight=neg)
 rows.append(dict(steps=n,bins=len(q),z_start=float(np.expm1(-u[0])),z_end=float(np.expm1(-u[-1])),hydrogen=stat(b),helium_carried_plus_fresh=stat(a),new_HeI_absorption_fraction=r['HI_absorptions']/r['fresh_He_2s_photons'],extra_H_event_minus_HI_absorption=sum(r['H_extra_events'])-r['HI_absorptions']))
result=dict(source_sha256=hashlib.sha256(inp.read_bytes()).hexdigest(),scope='Comoving photon-number and energy moments of recorded source diagnostics. He includes carried-in stock and fresh emission; absorption fraction divides total window absorption by fresh photon number, not an isolated fresh-cohort probability. H output is not a full transported/observed spectrum.',rows=rows)
(D/'SPECTRAL_AUDIT.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
