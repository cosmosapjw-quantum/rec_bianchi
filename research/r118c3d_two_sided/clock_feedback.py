"""Conditional scalar BASS H(a) -> actual REC HMLA -> new electron clock."""
import hashlib,json,gzip
from pathlib import Path
from dataclasses import dataclass
import numpy as np
from scipy.interpolate import PchipInterpolator
from full_bianchi_hyrec.trajectory.independent_rei_boundary import SharedInventorySource
from full_bianchi_hyrec.trajectory.hmla_flrw import integrate_hmla_hydrogen
from full_bianchi_hyrec.trajectory.primitive_rates import OriginalHyRecPrimitiveRateTable
from full_bianchi_hyrec.trajectory.standalone import ground_state
D=Path(__file__).resolve().parent;B=Path('/home/cosmosapjw/worktrees/bass-r109-native-20261124/research/r118c3d_four_tracks')
P=D.parent/'r118c2g_angular_rei/REI_INITIAL_NORMAL.json.gz';A=Path('archive/inputs/original_hyrec_oct2012/HyRec_Oct2012.zip')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
j=json.loads(gzip.decompress(P.read_bytes()));b=j['background'];h=.674
tab=OriginalHyRecPrimitiveRateTable.from_archive(A)
base=SharedInventorySource(h,b['Omega_m'],b['Omega_r']*h*h,b['Omega_lambda']*h*h,b['Omega_b']*h*h,b['YHe'],b['T0_K'],tab)
@dataclass(frozen=True)
class ClockSource(SharedInventorySource):
    clock:object=None
    def cosmology(self,z):
        _,nh=super().cosmology(z);a=1/(1+z)
        return float(np.exp(self.clock(np.log(a)))),nh
p=B/'early_32768.csv';v=np.genfromtxt(p,names=True,delimiter=',')
clock=PchipInterpolator(np.log(v['a']),np.log(v['h']*b['H0_s']),extrapolate=False)
s=ClockSource(h,b['Omega_m'],b['Omega_r']*h*h,b['Omega_lambda']*h*h,b['Omega_b']*h*h,b['YHe'],b['T0_K'],tab,clock)
out=[]
for tol in (1e-9,1e-11):
 hist=integrate_hmla_hydrogen(s,z_initial=1600.,z_final=20.,points=701,rtol=tol,atol=tol/100,initialization='post_saha')
 rows=[ground_state(s,z,x,t) for z,x,t in zip(hist.z,hist.x_HII,hist.Tm_K)]
 ini=rows[-1];ini.update(x_HeII=0.,x_HeIII=0.,ionizing_photon_stock=0.,ionizing_stock_scope='AX01_source_switch_on_assumption')
 obj=dict(schema='rec_bianchi.rei_initial_state/1',scope='CONDITIONAL_BASS_SCALAR_CLOCK_HMLA_H_ONLY_NOT_FULL',original_donor_sha=sha(P),bass_clock_sha=sha(p),rates_sha=sha(A),background=b,initial=ini,history=dict(history_owner='REC_BIANCHI',external_history=False,external_hubble_clock=True,rtol=tol,atol=tol/100,states=rows))
 f=D/('CLOCK_DONOR_NORMAL.json' if tol==1e-9 else 'CLOCK_DONOR_TIGHT.json');f.write_text(json.dumps(obj,indent=2)+'\n');out.append(dict(tol=tol,sha=sha(f),x=ini['x_HII'],T=ini['T_m_K'],H=ini['H_s']))
 print(out[-1],flush=True)
print('original',j['initial']['x_HII'],j['initial']['T_m_K'])
assert abs(out[0]['x']/out[1]['x']-1)<1e-5 and abs(out[0]['T']/out[1]['T']-1)<1e-5
(D/'CLOCK_FEEDBACK.json').write_text(json.dumps(dict(status='SCOPED_BASS_SCALAR_CLOCK_REC_FEEDBACK',rows=out,original=j['initial'],source_hashes={str(P):sha(P),str(p):sha(p),str(A):sha(A)},scope='prescribed BASS H scalar, neutral helium HMLA, no anisotropic line opacity feedback or full HHe'),indent=2)+'\n')
