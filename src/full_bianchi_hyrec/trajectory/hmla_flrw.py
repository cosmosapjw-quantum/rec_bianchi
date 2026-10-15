"""Source-backed FLRW *hydrogen-only* HyRec EMLA2s2p dynamics.

This is a FIRST INDEPENDENT REC H+matter-temperature ODE, not HyRec FULL:
it uses original Oct2012 effective 2s/2p primitive rates and quasi-steady
generalized Peebles C factors, Ly-alpha Sobolev without diffusion,
two-photon 2s->1s decay, and Compton+adiabatic matter cooling. Helium
recombination, line feedback and time-dependent Ly-alpha transport are
NOT implemented here. Helium is neutral in this bounded z=1600..600 lane,
but neutral helium density remains in the thermal heat capacity.

Public units: H[s^-1], nH[m^-3], z dimensionless, Tm,Tr Kelvin, rate
alpha[m^3/s], beta,R[s^-1]. The native original C source uses nH[cm^-3],
alpha[cm^3/s], T[ eV ]. Conventions are converted explicitly.
"""
from __future__ import annotations
from dataclasses import dataclass
import math
from pathlib import Path

import numpy as np
from scipy.integrate import solve_ivp

from full_bianchi_hyrec.trajectory.primitive_rates import (
    OriginalHyRecPrimitiveRateTable,
    SAHA_COEFFICIENT_CGS,
    IONIZATION_ENERGY_EV,
)
from full_bianchi_hyrec.trajectory.recombination_reference import (
    hyrec_source_hubble_per_s,
    hyrec_source_hydrogen_number_density_m3,
)

# C-source hydrogen.c, May2012/OCT2012. No fitted modern constants.
KB_NATIVE_EV_K=8.617343e-5
LYA_FACT_CM3=4.662899067555897e15
LAMBDA_2S1S_S_INV=8.2206
COMPTON_GAMMA_PER_T4_S_INV_K4=4.91466895548409e-22


@dataclass(frozen=True)
class HMLAFlrwSource:
    h: float
    omega_cb: float
    omega_r_h2: float
    omega_de_h2: float
    omega_b_h2: float
    y_he_mass: float
    tcmb0_K: float
    table: OriginalHyRecPrimitiveRateTable

    def __post_init__(self):
        vals=(self.h,self.omega_cb,self.omega_r_h2,self.omega_de_h2,
              self.omega_b_h2,self.y_he_mass,self.tcmb0_K)
        if not all(math.isfinite(x) for x in vals) or min(vals[:2])<=0 or self.omega_b_h2<=0:
            raise ValueError("nonfinite or invalid source cosmology")
        if not (0<self.y_he_mass<1 and self.tcmb0_K>0):
            raise ValueError("invalid helium fraction/Tcmb")
        if not math.isclose(
            self.omega_cb*self.h*self.h+self.omega_r_h2+self.omega_de_h2,
            self.h*self.h,rel_tol=3e-12,
        ):
            raise ValueError("source cosmology flat density closure mismatch")

    @property
    def f_he(self):
        return self.y_he_mass/((1-self.y_he_mass)*3.97153)

    def cosmology(self,z):
        return (
            hyrec_source_hubble_per_s(
                z=z,h=self.h,omega_cb=self.omega_cb,
                omega_r_h2=self.omega_r_h2,omega_de_h2=self.omega_de_h2),
            hyrec_source_hydrogen_number_density_m3(
                z=z,omega_b_h2=self.omega_b_h2,y_he_mass=self.y_he_mass)
        )

    def hydrogen_rhs_ln_a(
        self, *, z: float, x_HII: float,
        x_e: float, Tm_K: float, fsR: float=1.,meR:float=1.,
    ) -> float:
        """Equation from original HyRec2012 hydrogen.c::rec_HMLA_dxHIIdlna.

        This is the non-FULL quasi-steady EMLA2s2p RHS. Source 2s2p
        effective rates are original 2012 tables, not hardcoded RECFAST
        Case B. At high optical depth the denominator is re-expressed
        as a sum of nonnegative terms to avoid cross-rate cancellation.
        """
        if not all(math.isfinite(v) for v in (z,x_HII,x_e,Tm_K,fsR,meR)):
            raise ValueError("nonfinite source hydrogen state")
        if not (z>=0 and 0<=x_HII<1 and x_e>=x_HII and Tm_K>0 and fsR>0 and meR>0):
            raise ValueError("invalid physical hydrogen state")
        H,nH_m3=self.cosmology(z)
        nH_cm3=nH_m3*1e-6
        Tr_K=self.tcmb0_K*(1+z)
        ratio=Tm_K/Tr_K
        # Native source uses Tr in eV and rescales energy levels by fsR² meR.
        Tr_eV=KB_NATIVE_EV_K*Tr_K/(fsR*fsR*meR)
        rates=self.table.evaluate(
            radiation_temperature_eV_rescaled=Tr_eV,
            matter_to_radiation_temperature_ratio=ratio,fsR=fsR,meR=meR)
        alpha=rates.alpha_m3_s*1e6
        dalpha=rates.delta_alpha_m3_s*1e6
        betaS,betaP=map(float,rates.beta_s_inv)
        R=float(rates.R_2p2s_s_inv)
        lam=LAMBDA_2S1S_S_INV*fsR**8*meR
        ly=LYA_FACT_CM3*(fsR*fsR*meR)**3*H/(nH_cm3*(1-x_HII))
        # Symmetric positive Schur-complement denominator, equivalent to
        # original C: (betaS+3R+lam)(betaP+R+ly)-3R^2.
        denominator=(betaS+lam)*(betaP+ly)+R*(betaS+lam+3*betaP+3*ly)
        if not math.isfinite(denominator) or denominator<=0:
            raise FloatingPointError("unphysical real-level Schur complement")
        c2s=(lam*(betaP+R+ly)+3*R*ly)/denominator
        c2p=(ly*(betaS+3*R+lam)+R*lam)/denominator
        s=SAHA_COEFFICIENT_CGS*(fsR*meR)**3*Tr_eV*math.sqrt(Tr_eV)*math.exp(
            -IONIZATION_ENERGY_EV/Tr_eV)/nH_cm3
        dxe2=x_e*x_HII-s*(1-x_HII)
        res=-nH_cm3/H*(
            (s*(1-x_HII)*dalpha[0]+alpha[0]*dxe2)*c2s
           +(s*(1-x_HII)*dalpha[1]+alpha[1]*dxe2)*c2p
        )
        if not math.isfinite(res):
            raise FloatingPointError("nonfinite hydrogen source RHS")
        return float(res)

    def hydrogen_rhs_ln_a_many(
        self, *, z:float, x_HII:np.ndarray,
        x_e:np.ndarray, Tm_K:float,
    ) -> np.ndarray:
        """Vectorized common-(z,Tm) source for independent x-state batches.

        The *same* original HyRec rate table is evaluated ONCE, while the
        Ly-alpha escape factor varies correctly with each hydrogen neutral
        fraction. No angle-dependent collision or shared chemical evolution
        is assumed; every state is independent under common background.
        """
        x=np.asarray(x_HII,dtype=float)
        xe=np.asarray(x_e,dtype=float)
        if x.ndim!=1 or x.size<1 or xe.shape!=x.shape:
            raise ValueError("batch requires equal nonempty one-dimensional ion states")
        if (not np.all(np.isfinite(x)) or not np.all(np.isfinite(xe))
            or np.any(x<0) or np.any(x>=1) or np.any(xe<x)):
            raise ValueError("invalid physically paired ionization batch")
        if not (math.isfinite(z) and z>=0 and math.isfinite(Tm_K) and Tm_K>0):
            raise ValueError("invalid batch time and matter temperature")
        H,nH=self.cosmology(z)
        nc=nH*1e-6
        Tr=KB_NATIVE_EV_K*self.tcmb0_K*(1+z)
        rates=self.table.evaluate(
            radiation_temperature_eV_rescaled=Tr,
            matter_to_radiation_temperature_ratio=Tm_K/(self.tcmb0_K*(1+z)),
        )
        a=rates.alpha_m3_s*1e6
        da=rates.delta_alpha_m3_s*1e6
        bs,bp=map(float,rates.beta_s_inv)
        r=float(rates.R_2p2s_s_inv)
        lam=LAMBDA_2S1S_S_INV
        ly=LYA_FACT_CM3*H/(nc*(1-x))
        den=(bs+lam)*(bp+ly)+r*(bs+lam+3*bp+3*ly)
        if np.any(den<=0) or not np.all(np.isfinite(den)):
            raise FloatingPointError("invalid batch Schur complement")
        cs=(lam*(bp+r+ly)+3*r*ly)/den
        cp=(ly*(bs+3*r+lam)+r*lam)/den
        saha=SAHA_COEFFICIENT_CGS*Tr*math.sqrt(Tr)*math.exp(
            -IONIZATION_ENERGY_EV/Tr)/nc
        d2=xe*x-saha*(1-x)
        result=-nc/H*(
            (saha*(1-x)*da[0]+a[0]*d2)*cs
            +(saha*(1-x)*da[1]+a[1]*d2)*cp
        )
        if not np.all(np.isfinite(result)):
            raise FloatingPointError("nonfinite vector source")
        out=np.asarray(result,dtype=float)
        out.setflags(write=False)
        return out

    def saha_initial_hii(self,z:float)->float:
        """Hydrogen-only x^2/(1-x)=Saha(T_rad,n_H), helium neutral."""
        if not math.isfinite(z) or z<=0:
            raise ValueError("invalid starting redshift")
        _,nH=self.cosmology(z)
        Tr=KB_NATIVE_EV_K*self.tcmb0_K*(1+z)
        S=SAHA_COEFFICIENT_CGS*Tr**1.5*math.exp(
            -IONIZATION_ENERGY_EV/Tr)/(nH*1e-6)
        if not S>0:
            raise FloatingPointError("underflowed Saha initial condition")
        return float(2/(1+math.sqrt(1+4/S)))

    def hydrogen_post_saha_initial(self,z:float)->float:
        """First-order non-equilibrium post-Saha correction in original spirit.

        For x^2/(1-x)=s(T_r,n_H), the hydrogen-only Saha derivative is
          x_eq'=(1.5-EI/Tr)/(2/x_eq+1/(1-x_eq)), eta=ln a.
        Quasi-static source f(x) linearized at Saha gives
          delta_x = (x_eq'-f(x_eq))/f_x(x_eq).
        f_x is evaluated with a symmetric *source-local* step, not by
        differentiating a borrowed reference xe curve. This initialization
        is applicable while the linear correction is small compared with
        the neutral fraction; otherwise initialization fails closed.
        """
        x_eq=self.saha_initial_hii(z)
        Tr=KB_NATIVE_EV_K*self.tcmb0_K*(1+z)
        dxeq=(1.5-IONIZATION_ENERGY_EV/Tr)/(2/x_eq+1/(1-x_eq))
        step=0.01*(1-x_eq)
        if not (1e-14<step<min(x_eq,1-x_eq)*0.5):
            raise ValueError("post-Saha expansion outside local linear regime")
        Tm=self.initial_Tm_steady_K(z,x_eq)
        def f(x):
            return self.hydrogen_rhs_ln_a(z=z,x_HII=x,x_e=x,Tm_K=Tm)
        f0=f(x_eq)
        derivative=(f(x_eq+step)-f(x_eq-step))/(2*step)
        if not math.isfinite(derivative) or derivative>=0.:
            raise FloatingPointError("non-stable post-Saha source linearization")
        correction=(dxeq-f0)/derivative
        initial=x_eq+correction
        if not (0<initial<1 and abs(correction)<0.1*(1-x_eq)):
            raise ValueError("post-Saha correction no longer local")
        return float(initial)

    def initial_Tm_steady_K(self,z:float,xe:float)->float:
        H,_=self.cosmology(z)
        Tr=self.tcmb0_K*(1+z)
        rate=COMPTON_GAMMA_PER_T4_S_INV_K4*Tr**4*xe/(1+xe+self.f_he)
        return float(Tr/(1+H/rate))

    def thermal_rhs_ln_a(self,z:float,xe:float,Tm_K:float)->float:
        """Compton+adiabatic source, without HyRec FULL collision heat."""
        H,_=self.cosmology(z)
        Tr=self.tcmb0_K*(1+z)
        if not (0<xe<=1+2*self.f_he and Tm_K>0):
            raise ValueError("invalid gas temperature or electron fraction")
        coeff=COMPTON_GAMMA_PER_T4_S_INV_K4*Tr**4*xe/(1+xe+self.f_he)
        return float(-2*Tm_K+coeff/H*(Tr-Tm_K))


@dataclass(frozen=True)
class HMLAHistory:
    z: np.ndarray
    x_HII: np.ndarray
    Tm_K: np.ndarray
    source_mode: str = "REC_HMLA2s2p_H_ONLY_PLUS_TM_NOT_FULL"

    def __post_init__(self):
        n=len(self.z)
        if n<2 or self.x_HII.shape!=(n,) or self.Tm_K.shape!=(n,):
            raise ValueError("history shape mismatch")
        if not np.all(np.isfinite(self.x_HII)) or not np.all(np.isfinite(self.Tm_K)):
            raise ValueError("nonfinite gas history")
        if np.any(self.x_HII<0) or np.any(self.x_HII>1) or np.any(self.Tm_K<=0):
            raise ValueError("nonphysical hydrogen ionization/temperature history")
        for name in ("z","x_HII","Tm_K"):
            v=np.array(getattr(self,name),copy=True)
            v.setflags(write=False)
            object.__setattr__(self,name,v)


def integrate_hmla_hydrogen(
    source:HMLAFlrwSource, *,
    z_initial:float=1600., z_final:float=600.,
    points:int=101,rtol:float=2e-7,atol:float=2e-9,
    method:str="BDF",
    initialization:str="post_saha",
) -> HMLAHistory:
    """Independent local H+Tm trajectory, helium explicitly neutral.

    EMLA2s2p physical scope; z_initial should be below table upper
    temperature edge. Neither upstream reference x_e(z) nor T_m(z) is used
    as boundary condition or interpolation inside this solver.
    """
    if not (math.isfinite(z_initial) and math.isfinite(z_final)
            and z_initial>z_final>=0 and points>=2
            and method in ("BDF","Radau") and initialization in ("saha","post_saha")
            and 0<rtol<1e-2 and atol>0):
        raise ValueError("invalid scientific integration contract")
    eta0=-math.log1p(z_initial)
    eta1=-math.log1p(z_final)
    x0=(source.hydrogen_post_saha_initial(z_initial)
        if initialization=="post_saha" else source.saha_initial_hii(z_initial))
    T0=source.initial_Tm_steady_K(z_initial,x0)
    grid=np.linspace(eta0,eta1,points)

    def rhs(eta,y):
        z=math.expm1(-eta)
        x=float(y[0]);Tm=float(y[1])
        # Bounds are physical checks, not a positivity projection. Reject
        # genuinely nonphysical solver states rather than silently clipping.
        return [
            source.hydrogen_rhs_ln_a(z=z,x_HII=x,x_e=x,Tm_K=Tm),
            source.thermal_rhs_ln_a(z,x,Tm),
        ]

    # A physical temperature has K units and can be many thousands, while x
    # is dimensionless. A single common absolute tolerance must not silently
    # give Tm the same 1e-9 K criterion as x.
    out=solve_ivp(rhs,(eta0,eta1),[x0,T0],
        method=method,rtol=rtol,atol=[atol,max(1e-6,atol*1e4)],
        t_eval=grid)
    if not out.success:
        raise RuntimeError(f"independent HMLA evolution failed: {out.message}")
    return HMLAHistory(
        z=np.expm1(-out.t),
        x_HII=out.y[0],
        Tm_K=out.y[1],
    )
