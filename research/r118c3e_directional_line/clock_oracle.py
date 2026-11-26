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
D=Path(__file__).resolve().parent;B=Path('/home/cosmosapjw/worktrees/bass-r109-native-20261124/research/r118c3e_geometry_tracks')
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


from scipy.integrate import solve_ivp
results=[]
for case in ('zerofine','plusfine'):
 p=B/(case+'.csv');v=np.genfromtxt(p,names=True,delimiter=',')
 clock=PchipInterpolator(np.log(v['a']),np.log(v['h']*b['H0_s']),extrapolate=False)
 s=ClockSource(h,b['Omega_m'],b['Omega_r']*h*h,b['Omega_lambda']*h*h,b['Omega_b']*h*h,b['YHe'],b['T0_K'],tab,clock)
 x0=s.hydrogen_post_saha_initial(1600.);T0=s.initial_Tm_steady_K(1600.,x0)
 def rhs(u,v):
    z=np.expm1(-u);x,T=v
    return [s.hydrogen_rhs_ln_a(z=z,x_HII=x,x_e=x,Tm_K=T),s.thermal_rhs_ln_a(z,x,T)]
 for method,tol in [('BDF',1e-11),('BDF',3e-13)]:
    q=solve_ivp(rhs,(-np.log(1601.),-np.log(21.)),[x0,T0],method=method,rtol=tol,atol=[tol/100,tol],first_step=1e-9,max_step=.005);assert q.success
    x,T=q.y[:,-1];row=dict(case=case,method=method,tol=tol,x=float(x),T=float(T),nfev=q.nfev,clock_sha=sha(p));results.append(row);print(row,flush=True)
(D/'CLOCK_ORACLE.json').write_text(json.dumps(dict(status='SCOPED_TIGHT_TEMPERATURE_DONOR_ORACLE',rows=results,scope='direct-state BDF with independent temperature tolerance, exact same scalar H clock; no fixed absolute T floor'),indent=2)+'\n')
