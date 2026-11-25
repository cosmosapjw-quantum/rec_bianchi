"""Own HMLA history to the REI z=20 boundary; exact shared inventory.
No external ionization/temperature history. Neutral-He H-only model.
The source rate tables and interpolation are unchanged.
"""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import argparse,hashlib,json,math
from .hmla_flrw import HMLAFlrwSource,integrate_hmla_hydrogen
from .primitive_rates import OriginalHyRecPrimitiveRateTable
from .rei_initial_boundary import REIConditionalIC
from .standalone import ground_state

@dataclass(frozen=True)
class SharedInventorySource(HMLAFlrwSource):
    """Use REI AX01's clock and nucleon-mass inventory, not HyRec's
    rounded density conversions. Atomic tables still use their original
    temperature/rate conventions."""
    @property
    def f_he(self):return self.y_he_mass/(4*(1-self.y_he_mass))
    @property
    def H0_s(self):return 100*self.h*1e5/3.0856775814913673e24
    @property
    def n_h0_m3(self):
        # Same CGS constants as REI igm_background.rs.
        rho=3*self.H0_s**2/(8*math.pi*6.67430e-8)
        return (1-self.y_he_mass)*(self.omega_b_h2/self.h**2)*rho/1.67262192595e-24*1e6
    def cosmology(self,z):
        a1=1+z
        H=self.H0_s*math.sqrt(self.omega_cb*a1**3+self.omega_r_h2/self.h**2*a1**4+self.omega_de_h2/self.h**2)
        return H,self.n_h0_m3*a1**3

def shared_handoff(archive,scenario,*,points=701,rtol=1e-10,atol=1e-12,initialization="post_saha"):
    ic=REIConditionalIC.from_scenario(Path(scenario));tab=OriginalHyRecPrimitiveRateTable.from_archive(archive)
    h=ic.h
    s=SharedInventorySource(h,ic.omega_m,ic.omega_r*h*h,ic.omega_lambda*h*h,ic.omega_b_h2,ic.helium_mass_fraction,ic.tcmb0_K,tab)
    hist=integrate_hmla_hydrogen(s,z_initial=1600,z_final=ic.z_ref,points=points,rtol=rtol,atol=atol,initialization=initialization)
    states=[ground_state(s,z,x,t) for z,x,t in zip(hist.z,hist.x_HII,hist.Tm_K)]
    q=states[-1]
    if q['z']!=20.:raise ValueError("incorrect boundary")
    return dict(schema="rec_bianchi.rei_initial_state/1",scope="HMLA2s2p_neutral_He_FLRW_to_REI_boundary_not_FULL",scenario_sha256=ic.scenario_sha256,background=dict(H0_s=s.H0_s,n_H0_m3=s.n_h0_m3,f_He=s.f_he,Omega_m=ic.omega_m,Omega_r=ic.omega_r,Omega_lambda=ic.omega_lambda,Omega_b=ic.omega_b_h2/h**2,T0_K=ic.tcmb0_K,YHe=ic.helium_mass_fraction,inventory="REI_AX01_H_4He_mp"),initial=dict(q,x_HeII=0.,x_HeIII=0.,ionizing_photon_stock=0.,ionizing_stock_scope="AX01_source_switch_on_assumption"),history=dict(history_owner="REC_BIANCHI",external_history=False,external_hyrec_runtime=False,initialization=initialization,rtol=rtol,atol=atol,rate_hashes=dict(tab.source_hashes),states=states))
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--rates',type=Path,required=True);p.add_argument('--scenario',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--rtol',type=float,default=1e-10);p.add_argument('--atol',type=float,default=1e-12);p.add_argument('--initialization',choices=['post_saha','saha'],default='post_saha');a=p.parse_args()
    v=shared_handoff(a.rates,a.scenario,rtol=a.rtol,atol=a.atol,initialization=a.initialization)
    with a.out.open('x') as f:json.dump(v,f,indent=2,allow_nan=False)
if __name__=='__main__':main()
