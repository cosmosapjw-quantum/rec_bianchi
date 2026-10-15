"""Source-qualified primordial recombination -> conditional REI initial-state bridge.

An independently evolved *primordial* FLRW full HyRec history yields xe = ne/nH
and gas temperature. REI zbar=20 has a distinct conditional starting
state and an optional zero stellar ionizing-photon stock. This bridge
computes a typed q=0 counterfactual and never overwrites a REI owner.

Original 2012 HyRec internally assumes massless neutrinos, effective
fHe=Y/[(1-Y)*3.97153] and nH0=11.223846333047 obh2 (1-Y) m^-3.
REI's locked idealized H/4He inventory uses proton-mass density and
fHe=Y/[4(1-Y)] and H²=H0²[Om a^-3+Or a^-4+OL].
Report small normalization differences; do not silently claim identical
atomic chemistry when clocks/cosmologies differ. User units remain SI.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import math
from pathlib import Path
from typing import Mapping

import numpy as np

H100_PER_S = 1.e7/3.0856775814913673e24
HYREC_H100_PER_S = 3.2407792896393e-18
HYREC_RADIATION_H2_PER_K4 = 4.48162687719e-7
HYREC_NU_DENSITY_FACTOR = 0.227107317660239
HYREC_NH0_PER_OMBH2 = 11.223846333047
K_B_J_K=1.380649e-23
C_M_S=299792458.
SIGMA_T_M2=6.6524587321e-29
G_SI=6.67430e-11
PROTON_KG=1.67262192369e-27


@dataclass(frozen=True)
class REIConditionalIC:
    scenario_sha256: str
    h: float
    omega_m: float
    omega_r: float
    omega_lambda: float
    omega_b_h2: float
    helium_mass_fraction: float
    tcmb0_K: float
    z_ref: float
    x_HII: float
    x_HeII: float
    x_HeIII: float
    Tgas_K: float
    method_identity: str = "rei.axbi.scenario_lock.v1"

    @classmethod
    def from_scenario(cls, path: Path) -> "REIConditionalIC":
        source=path.read_bytes()
        data=json.loads(source)
        if data.get("schema")!="rei.axbi.scenario_lock.v1":
            raise ValueError("unexpected REI science source schema")
        c=data["cosmology"]
        ini=data["gas_initial"]
        h=float(c["h0_km_s_mpc"])/100
        om=float(c["omega_m"])
        orad=float(c["omega_r"])
        ol=1-om-orad
        y=float(c["helium_mass_fraction"])
        tcmb=float(c["tcmb0_k"])
        obh2=.0224  # Explicit source in REI omega_b_formula, validated below
        expr=str(c["omega_b_formula"])
        if expr!="0.0224/(0.674^2)" or abs(h-.674)>1e-13:
            raise ValueError("REI baryon source formula changed; no blind substitution")
        if str(ini["temperature_k_formula"]) != (
            "2.7255*21^2/(150*(0.0224/0.023)^0.4)"
        ):
            raise ValueError("REI thermal initial source has changed")
        z=float(data["interval"]["zbar_start"])
        if z != 20.:
            raise ValueError("REI initial boundary no longer at zbar=20")
        T=tcmb*(1+z)**2/(150*(obh2/.023)**.4)
        fractions=[float(ini[k]) for k in ("x_HII","x_HeII","x_HeIII")]
        if not (0<=fractions[0]<=1 and 0<=fractions[1]<=1
                and 0<=fractions[2]<=1
                and fractions[1]+fractions[2]<=1):
            raise ValueError("nonphysical REI ionic census")
        if str(data["gas_initial"]["kind"])!="DECLARED_APPROXIMATE_CONDITIONAL_IC_NOT_REC_DONOR":
            raise ValueError("REI provenance mode changed; verify authority")
        return cls(
            scenario_sha256=hashlib.sha256(source).hexdigest(),
            h=h,omega_m=om,omega_r=orad,omega_lambda=ol,
            omega_b_h2=obh2,helium_mass_fraction=y,tcmb0_K=tcmb,
            z_ref=z,x_HII=fractions[0],x_HeII=fractions[1],
            x_HeIII=fractions[2],Tgas_K=T,
        )

    @property
    def f_he_rei(self):
        return self.helium_mass_fraction/(4*(1-self.helium_mass_fraction))

    @property
    def f_he_original_hyrec(self):
        return self.helium_mass_fraction/(3.97153*(1-self.helium_mass_fraction))

    @property
    def actual_electron_fraction(self):
        return self.x_HII+self.f_he_rei*(self.x_HeII+2*self.x_HeIII)

    def matched_hyrec2012_parameters(self):
        """Preserve REI homogeneous H(z) by source-equivalent massless N_eff.

        Matching the total radiation density uses an *effective* massless
        neutrino count, not a measurement or a claim of neutrino physics.
        """
        omegah2=self.h**2
        ogammah2=HYREC_RADIATION_H2_PER_K4*self.tcmb0_K**4
        nu=((self.omega_r*omegah2/ogammah2)-1)/HYREC_NU_DENSITY_FACTOR
        if not (math.isfinite(nu) and 0<nu<5):
            raise ValueError("REI effective massless radiation N_eff invalid")
        return {
            "T0_K":self.tcmb0_K,
            "omega_b_h2":self.omega_b_h2,
            "omega_cb_h2":self.omega_m*omegah2,
            "omega_k_h2":0.,
            "omega_lambda_h2":self.omega_lambda*omegah2,
            "w0":-1.,
            "wa":0.,
            "YHe":self.helium_mass_fraction,
            "N_eff_massless_equivalent":nu,
            "fsR":1.0,"meR":1.0,
        }

    def densities_at(self,z=None):
        if z is None: z=self.z_ref
        if not math.isfinite(z) or z<0:
            raise ValueError("invalid positive cosmological redshift")
        h0=100*self.h*1e5/3.0856775814913673e24
        rho_crit=3*h0*h0/(8*math.pi*G_SI)
        ob=self.omega_b_h2/self.h**2
        nh0=(1-self.helium_mass_fraction)*ob*rho_crit/PROTON_KG
        nh=nh0*(1+z)**3
        nh_hyrec0=HYREC_NH0_PER_OMBH2*self.omega_b_h2*(1-self.helium_mass_fraction)
        nh_hyrec=nh_hyrec0*(1+z)**3
        H=h0*math.sqrt(self.omega_m*(1+z)**3+
                       self.omega_r*(1+z)**4+self.omega_lambda)
        return {
            "H_s_inv":H,
            "nH_REI_m3":nh,
            "nH_HyRec_m3":nh_hyrec,
            "relative_nH_donor_minus_rei":nh_hyrec/nh-1,
            "fHe_REI":self.f_he_rei,
            "fHe_HyRec":self.f_he_original_hyrec,
        }


def _state_metrics(ic: REIConditionalIC, *, x_e:float, Tgas_K:float) -> dict:
    if not (math.isfinite(x_e) and math.isfinite(Tgas_K)
            and 0<=x_e<=1+2*ic.f_he_rei and Tgas_K>0):
        raise ValueError("nonphysical supplied ionization or temperature")
    rho=ic.densities_at()
    nH=rho["nH_REI_m3"]
    electron=nH*x_e
    return {
        "electron_density_m3":electron,
        "electron_density_cm3":electron*1e-6,
        "thomson_scattering_rate_s_inv":C_M_S*SIGMA_T_M2*electron,
        "thomson_optical_depth_rate_per_ln_a":
            C_M_S*SIGMA_T_M2*electron/rho["H_s_inv"],
        "thermal_energy_J_m3":1.5*nH*K_B_J_K*Tgas_K*(
            1+ic.f_he_rei+x_e
        ),
        "temperature_K":Tgas_K,
        "electron_fraction_per_H":x_e,
    }


def construct_rei_matched_donor(
    ic: REIConditionalIC, *, source_z:np.ndarray,
    source_xe:np.ndarray,source_Tr_ratio:np.ndarray,
    native_source_sha256:str,
) -> dict:
    """Evaluate q0 donor-vs-conditional REI at zbar=20.

    At z20 original HyRec integrates hydrogen after switching off helium
    (XHeII_MIN=1e-6), but direct output is xe_total only. The projected
    recipient xHII := xe_total is CONDITIONAL on neutral helium.
    It is not a proven independent source HeII abundance.
    """
    a=np.asarray(source_z,dtype=float)
    x=np.asarray(source_xe,dtype=float)
    r=np.asarray(source_Tr_ratio,dtype=float)
    if a.ndim!=1 or a.size<2 or a.shape!=x.shape or a.shape!=r.shape:
        raise ValueError("HyRec full history arrays must align")
    if (np.any(~np.isfinite(a)) or np.any(~np.isfinite(x))
        or np.any(~np.isfinite(r))
        or np.any(np.diff(a)>=0)
        or np.any(x<0) or np.any(r<=0)):
        raise ValueError("invalid decreasing z and positive history")
    matches=np.flatnonzero(a==ic.z_ref)
    if matches.size!=1:
        raise ValueError("exact original HyRec native z=20 row not present")
    index=int(matches[0])
    xe=float(x[index])
    Tgas=float(r[index]*ic.tcmb0_K*(1+ic.z_ref))
    reference=_state_metrics(ic,x_e=ic.actual_electron_fraction,Tgas_K=ic.Tgas_K)
    donor=_state_metrics(ic,x_e=xe,Tgas_K=Tgas)
    return {
        "schema":"rec.rei.primordial_reference_boundary.v1",
        "recombination_reference":"source-executed original HyRec2012 FULL FLRW including H+He",
        "source_sha256":native_source_sha256,
        "rei_scenario_sha256":ic.scenario_sha256,
        "reference_clock":"mean FLRW redshift zbar=a^-1-1; NOT observed-direction redshift",
        "source_cosmology":ic.matched_hyrec2012_parameters(),
        "normalization_mismatch":ic.densities_at(),
        "zbar":ic.z_ref,
        "published_rei_approximate_initial":reference,
        "hyrec_full_conditional_projection":donor,
        "donor_minus_baseline":{
            "xe_absolute":xe-reference["electron_fraction_per_H"],
            "xe_fractional":xe/reference["electron_fraction_per_H"]-1,
            "Tgas_K":Tgas-reference["temperature_K"],
            "Tgas_fractional":Tgas/reference["temperature_K"]-1,
            "ne_m3":donor["electron_density_m3"]-reference["electron_density_m3"],
            "optical_depth_rate_fractional":
                donor["thomson_optical_depth_rate_per_ln_a"]/
                  reference["thomson_optical_depth_rate_per_ln_a"]-1,
            "thermal_energy_fractional":
                donor["thermal_energy_J_m3"]/
                  reference["thermal_energy_J_m3"]-1,
        },
        "helium_projected_species":{
            "xHII_candidate":xe,
            "xHeII":0.0,
            "xHeIII":0.0,
            "qualifier":"Assuming neutral He at z=20 (source late H-only switch), not independent source He fractions",
        },
        "ionizing_photons":"REI initial ionizing stock remains its declared astrophysical zero; no transfer from nonionizing CMB/recombination spectral photons",
        "decision":"REI_REFERENCE_COUNTERFACTUAL_NOT_ADOPTED",
        "physics_limitations":[
            "REI kinematical family is user-locked to zbar20->4 only",
            "Original HyRec2012 FLRW massless-neutrino radiation matched by effective N_eff and slight nH/fHe mass normalization differences disclosed",
            "REI source ionizing emissivity and X-ray heating are not propagated from primordial epoch",
            "Native REI gas time evolution and observables are NOT recomputed at this donor IC",
            "No anisotropic q-ref recombination history inferred from q=0 donor",
        ],
    }


def shear_extrapolation_guard(ic: REIConditionalIC, *, qrefs=(0.,-.005,.005,-.01,.01),
                              redshifts=(20.,100.,600.,1100.)):
    """COUNTERFACTUAL extension of a z20 REI prescribed stress-free model.

    The physical adoption domain ends at z20: higher-z numbers are diagnostic
    mathematical consequences ONLY, not cosmological solutions or physical
    primordial shear constraints.
    """
    a_start=1/(1+ic.z_ref)
    h0=100*ic.h*1e5/3.0856775814913673e24
    def h_flrw(z):
        return h0*math.sqrt(
            ic.omega_m*(1+z)**3+ic.omega_r*(1+z)**4+ic.omega_lambda
        )
    href=h_flrw(ic.z_ref)
    rows=[]
    for q in qrefs:
        for z in redshifts:
            shear=q*href*((1+z)/(1+ic.z_ref))**3
            H=math.hypot(h_flrw(z),shear)
            sigma=shear/H
            rows.append({
                "q_ref":q,"zbar_formal":z,"signed_sigma_over_H":sigma,
                "H_perp_over_H":1-sigma,
                "H_parallel_over_H":1+2*sigma,
                "directional_monotone_redshift":bool(1-sigma>0 and 1+2*sigma>0),
                "ratio_shear_squared_to_hflrw_squared":(shear/h_flrw(z))**2,
                "within_REI_physical_domain":z<=ic.z_ref
            })
    return {
        "schema":"rec.rei.formal_shear_backextrapolation.v1",
        "accepted_physical_zbar_range":[4.,ic.z_ref],
        "extrapolated_to_primordial_epoch":"COUNTERFACTUAL_NOT_PHYSICALLY_ADMITTED",
        "metric":"-+++ normal-comoving LRS Bianchi I, a_perp=a exp(-b), a_parallel=a exp(2b)",
        "source_equations":"s(z)=qref Hflrw(zref)[(1+z)/(1+zref)]^3; H^2=Hflrw^2+s^2",
        "rows":rows,
    }
