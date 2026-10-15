"""Source-identified cross-code primordial recombination reference comparisons.

A comparator, not a recombinant solver. Reference output from official
HyRec2012/HyRec2 and RECFAST must never be relabeled as the locally evolving
Full-Bianchi-HyRec solution. At a fixed FLRW cosmology, electron abundance
is xe = ne/n_H including HeII and twice HeIII; it is NOT HII fraction.

The original HyRec October-2012 output third column is Tm/(T0*(1+z)).
HyRec-2 (2020) third column is Tm [K]. RECFAST output has no Tm.
Every interpolation checks the shared redshift domain and does not extrapolate.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import hashlib
import math
from pathlib import Path
from typing import Sequence

import numpy as np


class RecombinationReferenceKind(str, Enum):
    HYREC_2012 = "HyRec_2012_FULL"
    HYREC2_2020 = "HyRec2_2020"
    RECFAST_17 = "RECFAST_1.7"


@dataclass(frozen=True)
class PrimordialReferenceHistory:
    """Immutable published/reference executable result, never a native REC history."""
    kind: RecombinationReferenceKind
    redshift: np.ndarray
    xe_per_hydrogen: np.ndarray
    matter_temperature_K: np.ndarray | None
    y_he_mass: float
    cmb_temperature_K: float
    source_identity: str
    cosmology_sha256: str
    input_sha256: str
    output_sha256: str

    def __post_init__(self):
        if not isinstance(self.kind, RecombinationReferenceKind):
            raise TypeError("kind must be a known upstream executable")
        if not isinstance(self.source_identity, str) or not self.source_identity:
            raise ValueError("upstream source identity required")
        for key in ("cosmology_sha256", "input_sha256", "output_sha256"):
            h = getattr(self, key)
            if not isinstance(h, str) or len(h)!=64 or any(c not in "0123456789abcdef" for c in h):
                raise ValueError(f"{key}: full lowercase SHA256 required")
        z=np.asarray(self.redshift,dtype=float)
        xe=np.asarray(self.xe_per_hydrogen,dtype=float)
        if z.ndim!=1 or len(z)<10 or xe.shape!=z.shape:
            raise ValueError("redshift and electron fraction require equal 1D scientific history")
        if (not np.all(np.isfinite(z)) or not np.all(np.isfinite(xe))
            or not np.all(np.diff(z)<0) or z[-1]<0):
            raise ValueError("reference redshift must decrease, be finite and nonnegative")
        if not math.isfinite(self.y_he_mass) or not 0<self.y_he_mass<1:
            raise ValueError("valid primordial He mass fraction required")
        if not math.isfinite(self.cmb_temperature_K) or self.cmb_temperature_K<=0:
            raise ValueError("valid CMB T0[K] required")
        # The older HyRec-2 convention uses mass-per-H 3.97153; neutral-He
        # abundance by number n_He/n_H ~ Y/(3.97153*(1-Y)).
        f_he=self.y_he_mass/(3.97153*(1-self.y_he_mass))
        if np.min(xe)<0 or np.max(xe)>1.+2.*f_he+2e-5:
            raise ValueError("unphysical free-electron fraction: xe is ne/nH, not xHII")
        zz=np.array(z,copy=True)
        xxx=np.array(xe,copy=True)
        zz.setflags(write=False)
        xxx.setflags(write=False)
        object.__setattr__(self,"redshift",zz)
        object.__setattr__(self,"xe_per_hydrogen",xxx)
        if self.matter_temperature_K is not None:
            matter=np.asarray(self.matter_temperature_K,dtype=float)
            if matter.shape!=zz.shape or not np.all(np.isfinite(matter)) or np.any(matter<=0):
                raise ValueError("invalid matter-temperature curve in Kelvin")
            mt=np.array(matter,copy=True)
            mt.setflags(write=False)
            object.__setattr__(self,"matter_temperature_K",mt)

    @classmethod
    def from_native_output(
        cls, filename: str | Path, *, kind: RecombinationReferenceKind,
        y_he_mass: float, cmb_temperature_K: float,
        source_identity: str, cosmology_sha256: str, input_sha256: str,
    ) -> "PrimordialReferenceHistory":
        p=Path(filename)
        source=p.read_bytes()
        matrix=np.loadtxt(p,dtype=float)
        if matrix.ndim!=2 or matrix.shape[1]!=(2 if kind is RecombinationReferenceKind.RECFAST_17 else 3):
            raise ValueError("upstream reference has wrong column count")
        z=matrix[:,0]
        Tm=None
        if kind is RecombinationReferenceKind.HYREC_2012:
            # Native stdout stores Tm/T_r, NOT physical matter temperature.
            Tm=matrix[:,2]*float(cmb_temperature_K)*(1+z)
        elif kind is RecombinationReferenceKind.HYREC2_2020:
            Tm=matrix[:,2]
        return cls(
            kind=kind,redshift=z,xe_per_hydrogen=matrix[:,1],
            matter_temperature_K=Tm,
            y_he_mass=y_he_mass,cmb_temperature_K=cmb_temperature_K,
            source_identity=source_identity,
            cosmology_sha256=cosmology_sha256,input_sha256=input_sha256,
            output_sha256=hashlib.sha256(source).hexdigest(),
        )

    def evaluate(self, z: Sequence[float] | np.ndarray, *, property: str="xe") -> np.ndarray:
        zz=np.asarray(z,dtype=float)
        if zz.ndim!=1 or len(zz)<1 or not np.all(np.isfinite(zz)):
            raise ValueError("query redshift requires 1D finite points")
        if np.any(zz<self.redshift[-1]) or np.any(zz>self.redshift[0]):
            raise ValueError("out-of-range redshift: no silent recombination extrapolation")
        if property=="xe":
            data=self.xe_per_hydrogen
        elif property=="T_m_K" and self.matter_temperature_K is not None:
            data=self.matter_temperature_K
        else:
            raise ValueError("requested observable not present in upstream output")
        return np.interp(zz,self.redshift[::-1],data[::-1])

    @property
    def helium_number_ratio(self) -> float:
        return self.y_he_mass/(3.97153*(1.-self.y_he_mass))


def compare_primordial_references(
    authority: PrimordialReferenceHistory,
    candidate: PrimordialReferenceHistory,
    *,
    z_min: float,z_max: float,step: float=10.,
) -> dict:
    """Identically sampled reference-to-reference differences only.

    No automatic REC solver science admission may follow this function.
    """
    if authority.kind is candidate.kind:
        raise ValueError("comparison requires different independent reference binaries")
    if authority.cosmology_sha256!=candidate.cosmology_sha256:
        raise ValueError("source cosmology identity mismatch: do not compare different universes")
    if not math.isclose(authority.cmb_temperature_K,candidate.cmb_temperature_K,rel_tol=0,abs_tol=1e-12):
        raise ValueError("T_CMB cosmological mismatch")
    if not math.isclose(authority.y_he_mass,candidate.y_he_mass,rel_tol=0,abs_tol=1e-14):
        raise ValueError("helium cosmological mismatch")
    if not all(math.isfinite(v) for v in (z_min,z_max,step)) or not 0<=z_min<z_max or step<=0:
        raise ValueError("invalid reference comparison redshift range")
    z=np.arange(z_min,z_max+0.5*step,step)
    if z[-1]>z_max+1e-9:
        z=z[z<=z_max+1e-9]
    x=authority.evaluate(z)
    y=candidate.evaluate(z)
    if np.any(x<=0):
        raise ValueError("nonpositive reference electron fraction")
    diff=(y-x)/x
    if authority.matter_temperature_K is not None and candidate.matter_temperature_K is not None:
        t1=authority.evaluate(z,property="T_m_K")
        t2=candidate.evaluate(z,property="T_m_K")
        matter_abs_rel=np.abs(t2/t1-1.)
        Tm={"maximum_relative_difference":float(np.max(matter_abs_rel)),
            "redshift_at_max":float(z[int(np.argmax(matter_abs_rel))])}
    else:
        Tm={"status":"NOT_AVAILABLE_UPSTREAM"}
    i=int(np.argmax(abs(diff)))
    return {
        "classification":"REFERENCE_TO_REFERENCE_ONLY_NOT_CURRENT_REC_SOLVER",
        "reference":authority.kind.value,
        "candidate":candidate.kind.value,
        "ref_output_sha256":authority.output_sha256,
        "candidate_output_sha256":candidate.output_sha256,
        "z_min":float(z_min),"z_max":float(z_max),"redshift_step":float(step),"n_comparisons":len(z),
        "maximum_abs_relative_xe_difference":float(abs(diff[i])),
        "signed_relative_difference_at_max":float(diff[i]),
        "redshift_at_max":float(z[i]),
        "max_relative_matter_temperature":Tm,
        "scientific_admission":"REFERENCE_CODES_ONLY",
    }


def original_hyrec_atomic_table_supported_redshift(
    *,cmb_temperature_K:float,Tr_min_eV:float=.004,Tr_max_eV:float=.4
) -> tuple[float,float]:
    """Physical Tr=k_B T0 (1+z), fsR=meR=1. Not ionization-history coverage."""
    KB_EV_PER_K=8.617333262145e-5
    if not math.isfinite(cmb_temperature_K) or cmb_temperature_K<=0:
        raise ValueError("invalid CMB temperature")
    if not 0<Tr_min_eV<Tr_max_eV:
        raise ValueError("invalid source atomic-grid domain")
    Tmin=Tr_min_eV/(KB_EV_PER_K*cmb_temperature_K)-1.
    Tmax=Tr_max_eV/(KB_EV_PER_K*cmb_temperature_K)-1.
    return float(Tmin),float(Tmax)


def electron_fraction_from_species(
    *, x_HII: float, x_HeII_per_nH: float,
    x_HeIII_per_nH: float, helium_number_per_hydrogen: float,
) -> float:
    """Compute xe=ne/nH from *separately identified* hydrogen/helium ions.

    x_HII=n_HII/n_H, whereas helium inputs are n_HeII/n_H and
    n_HeIII/n_H, NOT fractions normalized to the helium abundance.
    The inverse xe -> three species is underdetermined; no such inversion
    is supplied by this comparison-only reference module.
    """
    v=(x_HII,x_HeII_per_nH,x_HeIII_per_nH,helium_number_per_hydrogen)
    if not all(math.isfinite(x) for x in v):
        raise ValueError("nonfinite hydrogen/helium composition")
    if not (0<=x_HII<=1 and x_HeII_per_nH>=0 and x_HeIII_per_nH>=0
            and helium_number_per_hydrogen>=0):
        raise ValueError("invalid H/He ionization fractions")
    if x_HeII_per_nH+x_HeIII_per_nH>helium_number_per_hydrogen+1e-14:
        raise ValueError("helium nuclei ledger exceeds n_He/n_H")
    return float(x_HII+x_HeII_per_nH+2*x_HeIII_per_nH)



def hyrec_source_equivalent_flrw_background(
    *, h: float, omega_cb: float,
    omega_r_h2: float, omega_de_h2: float,
    z_start: float=3000., z_end: float=600.,
):
    """Build source-specific FLRW q=0 geometry over primordial recombination.

    Inputs follow the original HyRec/HyRec-2 convention, NOT the default
    late-time Bianchi-I z=20->4 fixture. No atom populations are evolved.
    """
    from full_bianchi_hyrec.background.axisymmetric_bianchi_i import (
        AxisymmetricBianchiIBackground,BianchiIModelParameters,
    )
    values=(h,omega_cb,omega_r_h2,omega_de_h2,z_start,z_end)
    if not all(math.isfinite(v) for v in values):
        raise ValueError("nonfinite HyRec FLRW cosmology")
    if not 0<h and 0<omega_cb and 0<=omega_r_h2 and 0<=omega_de_h2:
        raise ValueError("invalid positive input densities")
    if not z_start>z_end>=0:
        raise ValueError("primordial recombination z_start must exceed z_end")
    # HyRec's scalar input source fixes a spatially flat, massless-neutrino
    # reference here. A non-closing Omega_cb+Omega_r+Omega_Lambda silently
    # gives a *different* H(z) from the claimed input h, even at z=0.
    density_sum=omega_cb*h*h+omega_r_h2+omega_de_h2
    if not math.isclose(density_sum,h*h,rel_tol=2e-12,abs_tol=0.):
        raise ValueError("source FLRW density closure mismatch")
    m=BianchiIModelParameters(
        h0_per_s=3.2407792896393e-18*h,
        omega_m=omega_cb,
        omega_r=omega_r_h2/(h*h),
        omega_lambda=omega_de_h2/(h*h),
    )
    return AxisymmetricBianchiIBackground(
        q_ref=0.,a_ref=1./(1.+z_start),a_end=1./(1.+z_end),
        cells=2048,cosmology=m,
    )


def hyrec_source_hubble_per_s(
    *, z: float, h: float, omega_cb: float,
    omega_r_h2: float, omega_de_h2: float,
) -> float:
    """Exact background expression from HyRec's cgs-normalized H(z) routine.

    Flat common reference without massive neutrinos or curvature:
    H=3.2407792896393e-18 sqrt[omega_cb_h2(1+z)^3
                               +omega_r_h2(1+z)^4+omega_de_h2].
    """
    x=(z,h,omega_cb,omega_r_h2,omega_de_h2)
    if not all(math.isfinite(v) for v in x) or z<0 or h<=0:
        raise ValueError("invalid FLRW reference redshift or h")
    if min(omega_cb,omega_r_h2,omega_de_h2)<0:
        raise ValueError("negative FLRW density")
    return 3.2407792896393e-18*math.sqrt(
        omega_cb*h*h*(1+z)**3+omega_r_h2*(1+z)**4+omega_de_h2
    )


def hyrec_source_hydrogen_number_density_m3(
    *, z: float, omega_b_h2: float, y_he_mass: float,
) -> float:
    """Original HyRec 2012 nH0=11.223846333047*omega_b_h2*(1-Y) m^-3.

    HyRec-2 writes the same number as 11.223846333047e-6 cm^-3,
    so converting the latter with 1e6 gives identical SI n_H.
    """
    if not all(math.isfinite(v) for v in (z,omega_b_h2,y_he_mass)):
        raise ValueError("nonfinite hydrogen source normalization")
    if z<0 or omega_b_h2<=0 or not 0<y_he_mass<1:
        raise ValueError("invalid redshift, baryon density or helium mass fraction")
    return float(
        11.223846333047*omega_b_h2*(1.-y_he_mass)*(1.+z)**3
    )
