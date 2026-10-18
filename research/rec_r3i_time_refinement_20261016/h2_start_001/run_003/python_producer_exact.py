"""Independent h/2 HyRec2012 source-clock start unit.

Pure source expressions copied from frozen R3g He/full-start modules; those
modules remain unchanged. No checkpoint interpolation or C state import.

Original HyRec Oct-2012 high-z He stages, independently expressed in Python.

This bounded trajectory ends at source index izH0: HeIII Saha followed by
HeII->HeI post-Saha / source predictor-corrector while hydrogen stays in
Saha closure. It does not evolve FULL hydrogen or claim a full history.
Abundances xHeII/xHeIII and xe are per hydrogen nucleus.
"""
from __future__ import annotations

from dataclasses import dataclass
import math

DLNA = 8.49e-5/2
SOURCE_DLNA = DLNA
ZSTART = 8000.0
TR_MAX_EV = 0.4
KB_EV_K = 8.617343e-5
DXHEII_MAX = 1.0e-5
SOURCE_HISTORY_SHA256 = "8ffe38f0431fcd1ae04b55f855f36e8643b1c5eb33a947f581f95d628611f976"
SOURCE_HELIUM_SHA256 = "1db7a9845e1f5a3052153bf94c1b98bf908cf16715641cbd14c810e5df6a5ece"


@dataclass(frozen=True)
class HyRec2012Cosmology:
    T0_K: float = 2.7255
    omega_b_h2: float = 0.0224
    omega_m_h2: float = 0.14309694000000003
    omega_k_h2: float = 0.0
    omega_de_h2: float = 0.31113726660800006
    w0: float = -1.0
    wa: float = 0.0
    YHe: float = 0.2454
    N_eff: float = 3.03821934419124
    fsR: float = 1.0
    meR: float = 1.0

    def __post_init__(self):
        vals = tuple(float(getattr(self, k)) for k in self.__dataclass_fields__)
        if not all(math.isfinite(v) for v in vals):
            raise ValueError("nonfinite cosmology")
        if not (self.T0_K > 0 and self.omega_b_h2 > 0 and self.omega_m_h2 > 0
                and self.YHe > 0 and self.YHe < 0.5 and self.N_eff >= 0
                and self.fsR > 0 and self.meR > 0):
            raise ValueError("cosmology outside original HyRec physical domain")

    @property
    def nH0_m3(self) -> float:
        return 11.223846333047 * self.omega_b_h2 * (1.0-self.YHe)

    @property
    def fHe(self) -> float:
        return self.YHe / ((1.0-self.YHe)*3.97153)

    @property
    def izH0(self) -> int:
        return math.floor(1.0 + math.log((KB_EV_K*self.T0_K
            /self.fsR**2/self.meR)*8001.0/TR_MAX_EV)/DLNA)

    def redshift(self, iz: int) -> float:
        return (1.0+ZSTART)*math.exp(-DLNA*iz)-1.0

    def hubble_s(self, z: float) -> float:
        a1 = 1.0+z
        # Same density sum and conversion constants as history.c.
        rho_m = self.omega_m_h2*a1**3
        rho_k = self.omega_k_h2*a1**2
        rho_de = self.omega_de_h2*a1**(3*(1+self.w0))*math.exp(
            3*self.wa*(math.log(a1)-1.0+1.0/a1))
        rho_gamma = 4.48162687719e-7*self.T0_K**4*a1**4
        rho_nu = 0.227107317660239*rho_gamma*self.N_eff
        return 3.2407792896393e-18*math.sqrt(rho_m+rho_k+rho_de+rho_gamma+rho_nu)


def saha_heii_iii(c: HyRec2012Cosmology, z: float) -> tuple[float, float]:
    """Return (xe, xHeIII) using helium.c::rec_xesaha_HeII_III."""
    tr = c.T0_K*(1+z)/c.fsR**2/c.meR
    a = 1+z
    nh = c.nH0_m3*a*a*a
    s = c.fsR**3*c.meR**3*2.414194e21*tr*math.sqrt(tr)*math.exp(-631462.7/tr)/nh
    x3 = 2*s*c.fHe/(1+s+c.fHe)/(1+math.sqrt(1+4*s*c.fHe/(1+s+c.fHe)**2))
    return 1+c.fHe+x3, x3


def saha_heii(c: HyRec2012Cosmology, z: float) -> float:
    """Return xHeII/nH in helium.c::rec_saha_xHeII."""
    tr = c.T0_K*(1+z)/c.fsR**2/c.meR
    a = 1+z
    nh = c.nH0_m3*a*a*a
    s = c.fsR**3*c.meR**3*2.414194e21*tr*math.sqrt(tr)*math.exp(-285325.0/tr)/nh*4
    return 2*s*c.fHe/(1+s)/(1+math.sqrt(1+4*s*c.fHe/(1+s)/(1+s)))


def saha_xH1s(c: HyRec2012Cosmology, xHeII: float, z: float) -> float:
    """Neutral hydrogen closure used by HyRec during the He stages."""
    tr=c.T0_K*(1+z)/c.fsR**2/c.meR
    a=1+z
    nh=c.nH0_m3*a*a*a
    s=c.fsR**3*c.meR**3*2.4127161187130e21*tr*math.sqrt(tr)*math.exp(-157801.37882/tr)/nh
    if s == 0:
        return 1.0
    if s > 1e5:
        return (1+xHeII)/s-(xHeII*xHeII+3*xHeII+2)/(s*s)
    return 1-2/(1+xHeII/s+math.sqrt((1+xHeII/s)**2+4/s))


def helium_rhs(c: HyRec2012Cosmology, xH1s: float, xHeII: float,
               H: float, z: float) -> float:
    """Source helium.c rate dxHeII/d ln(a), including H continuum opacity."""
    tr=c.T0_K*(1+z)/c.fsR**2/c.meR
    a=1+z
    nh=c.nH0_m3*a*a*a
    xe=xHeII+(1-xH1s)
    xHeI=c.fHe-xHeII
    if xHeI < 0:
        raise ValueError("helium abundance exceeds source fHe")
    s0=c.fsR**3*c.meR**3*2.414194e21*tr*math.sqrt(tr)/nh*4
    s=s0*math.exp(-285325.0/tr)
    y2s=math.exp(46090.0/tr)/s0
    y2p=3*math.exp(39101.0/tr)/s0
    etacinv=c.fsR**3*c.meR**3*9.15776e28*H/nh/xH1s
    g=(1.976e6/(1-math.exp(-6989/tr))
       +6.03e6/math.expm1(19754/tr)+1.06e8/math.expm1(21539/tr)
       +2.18e6/math.expm1(28496/tr)+3.37e7/math.expm1(29224/tr)
       +1.04e6/math.expm1(32414/tr)+1.51e7/math.expm1(32781/tr))
    g*=c.fsR**5*c.meR
    tau=4.277e-14*nh/H*xHeI/(c.fsR*c.meR**2)
    dnuline=g*tau/(4*math.pi**2)
    tauc=dnuline/etacinv
    enh=math.sqrt(1+math.pi**2*tauc)+7.74*tauc/(1+70*tauc)
    pesc=enh/tau
    pesc+=(1-math.exp(-1.023e-7*tau))*(0.964525*math.exp(2947/tr)
            -enh*math.exp(-6.14e13*c.fsR**2*c.meR/etacinv))/tau
    ydown=c.fsR**8*c.meR*50.94*y2s+c.fsR**5*c.meR*1.7989e9*y2p*pesc
    return ydown*(xHeI*s-xHeII*xe)/H


def tm_steady_K(c: HyRec2012Cosmology, xe: float, z: float, H: float) -> float:
    tr=c.T0_K*(1+z)
    gamma=c.fsR**2/c.meR**3*4.91466895548409e-22
    return tr/(1+H/(gamma*tr**4)*(1+xe+c.fHe)/xe)


@dataclass(frozen=True)
class HeliumStageHistory:
    iz: tuple[int, ...]
    z: tuple[float, ...]
    xe: tuple[float, ...]
    xHII: tuple[float, ...]
    xHeI: tuple[float, ...]
    xHeII: tuple[float, ...]
    xHeIII: tuple[float, ...]
    Tm_K: tuple[float, ...]
    helium_rhs_dln_a: tuple[float, ...]
    stage: tuple[str, ...]
    update_method: tuple[str, ...]
    post_saha: tuple[bool, ...]
    source_sha256: str = SOURCE_HELIUM_SHA256

    def __post_init__(self):
        n=len(self.iz)
        if n < 5 or any(len(getattr(self,k)) != n for k in
                ("z","xe","xHII","xHeI","xHeII","xHeIII","Tm_K","helium_rhs_dln_a","stage","update_method","post_saha")):
            raise ValueError("inconsistent or too short helium stage history")


def integrate_helium_stages(c: HyRec2012Cosmology=HyRec2012Cosmology()) -> HeliumStageHistory:
    """Reconstruct native HeIII Saha and HeII->HeI source stages through izH0.

    Matches native index ownership, post-Saha finite differences and the
    source's two-step 1.25/-0.25 predictor update. Hydrogen is algebraically
    Saha-closed; matter T is source steady state in the HeII stage.
    """
    zs=[]; xeout=[]; tms=[]; xhe=[]; rhsout=[]; stages=[]; methods=[]; psflags=[]
    iz=0; delta=c.fHe
    while iz <= c.izH0+2 and delta > 1e-8:
        z=c.redshift(iz)
        xe,delta=saha_heii_iii(c,z)
        zs.append(z); xeout.append(xe); tms.append(c.T0_K*(1+z)); rhsout.append(0.0)
        xhe.append(math.nan); stages.append("HeIII_SAHA"); methods.append("SAHA_ALGEBRAIC"); psflags.append(False)
        iz+=1
    if iz < 4:
        raise ArithmeticError("source HeIII stage ended before derivative seed exists")
    # Exact source finite-difference derivative seeds from xe outputs (HeIII fraction).
    dprev2=(xeout[iz-2]-xeout[iz-4])/(2*DLNA)
    dprev=(xeout[iz-1]-xeout[iz-3])/(2*DLNA)
    z=c.redshift(iz-1)
    xh=saha_heii(c,z); post=True
    while iz <= c.izH0:
        zin=c.redshift(iz-1)
        h=c.hubble_s(zin)
        xH1s=saha_xH1s(c,xh,zin)
        rhs=helium_rhs(c,xH1s,xh,h,zin)
        update_method="POST_SAHA" if post else "SOURCE_PREDICTOR"
        if post:
            # history.c::rec_get_xe_next1_He owns this endpoint expression.
            zout=(1.0+zin)*math.exp(-DLNA)-1.0
            h_out=c.hubble_s(zout)
            saha=saha_heii(c,zout)
            dsaha=(1+zout)*(saha_heii(c,zout-0.5)-saha_heii(c,zout+0.5))
            dxe=0.01*(c.fHe-saha)
            if not (dxe > 0 and saha-dxe >= 0 and saha+dxe <= c.fHe):
                raise ArithmeticError("post-Saha derivative perturbation leaves physical helium domain")
            hp=saha_xH1s(c,saha+dxe,zout)
            hm=saha_xH1s(c,saha-dxe,zout)
            df=(helium_rhs(c,hp,saha+dxe,h_out,zout)
                -helium_rhs(c,hm,saha-dxe,h_out,zout))/(2*dxe)
            if df == 0 or not math.isfinite(df):
                raise ArithmeticError("singular/nonfinite source post-Saha Jacobian")
            xh=saha+dsaha/df
            if abs(xh-saha)>DXHEII_MAX:
                post=False
        else:
            xh += DLNA*(1.25*rhs-0.25*dprev2)
        dprev2,dprev=dprev,rhs
        z=c.redshift(iz)
        xH1s=saha_xH1s(c,xh,z)
        xhii=1-xH1s
        xe_i=xhii+xh
        tm=tm_steady_K(c,xe_i,z,c.hubble_s(z))
        if not all(math.isfinite(q) for q in (xh,xhii,xe_i,tm)) or not (0 <= xh <= c.fHe and 0 <= xhii <= 1 and tm>0):
            raise ArithmeticError(f"invalid source helium state at index {iz}")
        xeout.append(xe_i); tms.append(tm); xhe.append(xh); rhsout.append(rhs)
        zs.append(z); stages.append("HeII_RECOMBINATION")
        methods.append(update_method); psflags.append(post); iz+=1
    # helium species are stored as abundances per H nucleus; xHeIII is derived
    # from total helium ledger during its Saha stage and zero after it.
    xhei=[]; xheii=[]; xheiii=[]; xhii=[]
    for i,stage in enumerate(stages):
        if stage == "HeIII_SAHA":
            # Native xe = 1 + fHe + xHeIII during the doubly ionized stage.
            q=xeout[i]-(1+c.fHe)
            xheiii.append(q); xheii.append(c.fHe-q); xhei.append(0.0); xhii.append(1.0)
        else:
            xheiii.append(0.0); xheii.append(xhe[i]); xhei.append(c.fHe-xhe[i]); xhii.append(xeout[i]-xhe[i])
    return HeliumStageHistory(tuple(range(len(zs))),tuple(zs),tuple(xeout),tuple(xhii),
        tuple(xhei),tuple(xheii),tuple(xheiii),tuple(tms),tuple(rhsout),tuple(stages),tuple(methods),tuple(psflags))


# Bounded FULL source algorithm, using the local refined clock above.
from dataclasses import dataclass
import math
from typing import Callable

import numpy as np

from full_bianchi_hyrec.trajectory.causal_virtual_redshift import (
    causal_incoming_from_accepted_histories,
)
from full_bianchi_hyrec.trajectory.full_2012_atomic_source import (
    NVIRT, _canonical_twophoton_table, complete_original_full_atomic,
    populate_original_full_atomic,
)
from full_bianchi_hyrec.trajectory.hmla_flrw import HMLAFlrwSource, KB_NATIVE_EV_K


N_ACCEPTED = 8
MAX_FULL_EVALUATIONS = 40
XHEII_MIN = 1.e-6
DXHII_MAX = 3.e-4
_SOURCE_INDEX_START = 36446


@dataclass(frozen=True)
class FullStartHistory:
    """Nine accepted state nodes and eight committed source columns."""

    iz: np.ndarray
    z: np.ndarray
    xH1s: np.ndarray
    xHII: np.ndarray
    xHeII: np.ndarray
    xe: np.ndarray
    Tm_K: np.ndarray
    helium_rhs_dln_a: np.ndarray
    hydrogen_rhs_dln_a: np.ndarray
    post_saha: np.ndarray
    virtual_out: np.ndarray
    lyman_out: np.ndarray
    matrix_residual: np.ndarray
    average_virtual: np.ndarray
    full_evaluations: int
    source_mode: str = "INDEPENDENT_PYTHON_HYREC2012_H2_FULL_HHE_EIGHT_ACCEPTED_START_STEPS"

    def __post_init__(self):
        n=N_ACCEPTED+1
        for name in ("iz","z","xH1s","xHII","xHeII","xe","Tm_K","post_saha"):
            a=np.asarray(getattr(self,name))
            if a.shape!=(n,):
                raise ValueError(f"{name} must have {n} state nodes")
            if name!="post_saha" and not np.all(np.isfinite(a)):
                raise ValueError(f"nonfinite {name}")
            a=np.array(a,copy=True); a.setflags(write=False)
            object.__setattr__(self,name,a)
        for name in ("helium_rhs_dln_a","hydrogen_rhs_dln_a"):
            a=np.asarray(getattr(self,name))
            if a.shape!=(N_ACCEPTED,) or not np.all(np.isfinite(a)):
                raise ValueError(f"{name} must contain the eight accepted input RHS values")
            a=np.array(a,copy=True); a.setflags(write=False)
            object.__setattr__(self,name,a)
        for name,shape in (("virtual_out",(NVIRT,N_ACCEPTED)),
                           ("average_virtual",(NVIRT,N_ACCEPTED)),
                           ("lyman_out",(3,N_ACCEPTED)),
                           ("matrix_residual",(N_ACCEPTED,))):
            a=np.asarray(getattr(self,name),dtype=float)
            if a.shape!=shape or not np.all(np.isfinite(a)):
                raise ValueError(f"invalid {name} shape or values")
            a=np.array(a,copy=True); a.setflags(write=False)
            object.__setattr__(self,name,a)
        if self.full_evaluations>MAX_FULL_EVALUATIONS:
            raise ValueError("FULL atomic evaluation cap exceeded")


def make_hmla_source(c: HyRec2012Cosmology, rate_table) -> HMLAFlrwSource:
    """Bind the pre-existing atomic source to the exact R3f HyRec FLRW inputs."""
    ogamma=4.48162687719e-7*c.T0_K**4
    radiation=ogamma*(1.+0.227107317660239*c.N_eff)
    h=math.sqrt(c.omega_m_h2+c.omega_k_h2+radiation+c.omega_de_h2)
    if not (h>0 and math.isfinite(h)):
        raise ValueError("invalid source Hubble normalization")
    return HMLAFlrwSource(
        h=h,omega_cb=c.omega_m_h2/h**2,
        omega_r_h2=radiation,omega_de_h2=c.omega_de_h2,
        omega_b_h2=c.omega_b_h2,y_he_mass=c.YHe,
        tcmb0_K=c.T0_K,table=rate_table,
    )


def source_native_derivative_seeds(helium: HeliumStageHistory, start: int):
    """Map U1's output-row RHS storage onto the source input-time seeds.

    U1 appends each derivative evaluated at i-1 alongside the accepted
    output state at i. Therefore its row i contains f(i-1), a convention
    that matters at the He-to-joint-HHe boundary.
    """
    if not isinstance(start,int) or start<3 or len(helium.iz)<=start:
        raise ValueError("U1 history lacks source derivative seed rows")
    h=SOURCE_DLNA
    dHe_prev=float(helium.helium_rhs_dln_a[start])
    dHe_prev2=float(helium.helium_rhs_dln_a[start-1])
    dH_prev=(float(helium.xe[start])-float(helium.xe[start-2]))/(2*h)-dHe_prev
    dH_prev2=(float(helium.xe[start-1])-float(helium.xe[start-3]))/(2*h)-dHe_prev2
    vals=(dHe_prev,dHe_prev2,dH_prev,dH_prev2)
    if not all(math.isfinite(v) for v in vals):
        raise ValueError("nonfinite source-native derivative seed")
    return vals


def integrate_full_start_eight(
    helium: HeliumStageHistory, c: HyRec2012Cosmology, source: HMLAFlrwSource,
    *, max_full_evaluations: int=MAX_FULL_EVALUATIONS,
    common_input_oracle: Callable | None = None,
) -> FullStartHistory:
    """Independently integrate eight accepted H+He steps from U1 endpoint.

    Source-owned helium is advanced by the native two-step 1.25/-0.25 rule.
    Each current FULL photon column is committed once. Post-Saha hydrogen
    probes at the next node read only accepted columns and discard all trial
    outgoing spectra. The source's hydrogen switch is applied to the NEXT
    accepted node after its correction is measured.
    """
    if max_full_evaluations<1 or max_full_evaluations>MAX_FULL_EVALUATIONS:
        raise ValueError("FULL evaluation cap must be in [1,40]")
    start=_SOURCE_INDEX_START
    if (helium.iz[-1]!=start or abs(helium.z[-1]-c.redshift(start))>2e-12
            or len(helium.iz)<=start):
        raise ValueError("U1 checkpoint is not the frozen izH0 endpoint")
    if helium.stage[start]!="HeII_RECOMBINATION":
        raise ValueError("unexpected helium source stage at H start")
    if not (helium.xHeII[start]>XHEII_MIN):
        raise ValueError("U2 contract requires joint H+He source branch")
    if not math.isclose(SOURCE_DLNA,8.49e-5/2,rel_tol=0.,abs_tol=0.):
        raise ArithmeticError("native HyRec clock changed")

    table=_canonical_twophoton_table(source.table.archive_path)
    n=N_ACCEPTED+1
    iz=np.arange(start,start+n,dtype=np.int64)
    z=np.array([c.redshift(int(i)) for i in iz])
    x1=np.empty(n); xh=np.empty(n); xhe=np.empty(n); xe=np.empty(n); tm=np.empty(n)
    fhe=np.full(n,np.nan); fh=np.full(n,np.nan); post=np.empty(n,dtype=bool)
    # NaN sentinels make any accidental read of a not-yet-accepted column fail.
    vout=np.full((NVIRT,N_ACCEPTED),np.nan)
    avgout=np.full((NVIRT,N_ACCEPTED),np.nan)
    lyout=np.full((3,N_ACCEPTED),np.nan)
    residual=np.empty(N_ACCEPTED)
    # U1 values and exactly source-derived He/H derivative seeds.
    xhe[0]=helium.xHeII[start]
    x1[0]=saha_xH1s(c,xhe[0],z[0])
    xh[0]=1.-x1[0]
    xe[0]=xh[0]+xhe[0]
    tm[0]=helium.Tm_K[start]
    dHe_prev,dHe_prev2,dH_prev,dH_prev2=source_native_derivative_seeds(helium,start)
    post[0]=True
    full_evals=0

    # Causal inputs use only columns already accepted before the call.
    def incoming(j):
        if j<2:
            return np.zeros(NVIRT),np.zeros(2)
        result=causal_incoming_from_accepted_histories(
            energies_eV=table.energy_eV,virtual_history=vout[:,:j],
            lyman_history=lyout[:,:j],z_start=float(z[0]),iz=j,
            z_face=float(z[j]),dlna=SOURCE_DLNA,shear_q=0.)
        return result.virtual_distortion[0],result.lya_lyb_incoming_distortion[0]

    def full_rhs(j, xHII, xHeII, Tm):
        nonlocal full_evals
        if full_evals>=max_full_evaluations:
            raise RuntimeError("FULL_EVALUATION_CAP")
        if not (0<=j<N_ACCEPTED+1):
            raise IndexError("FULL state index outside bounded interval")
        tr_k=c.T0_K*(1.+z[j])
        if Tm==tr_k:
            # Keep the exact physical boundary Tm=Tr inside the inclusive
            # binary64 table domain despite the separately rounded products
            # KB*(T0*(1+z)) and (KB*T0)*(1+z) in the source adapter.
            Tm=math.nextafter(float(Tm),0.)
        fv,fl=incoming(j)
        snap=populate_original_full_atomic(
            source,z=float(z[j]),xHII=float(xHII),
            xe=float(xHII+xHeII),Tm_K=float(Tm),
            incoming_virtual=fv,incoming_lyman=fl)
        out=complete_original_full_atomic(snap)
        full_evals+=1
        if common_input_oracle is not None:
            expected=common_input_oracle(
                j,float(z[j]),float(xHII),float(xHeII),float(Tm),
                vout[:,:j],lyout[:,:j])
            rhs_c=float(expected["rhs"])
            rhs_scaled=abs(out.dxHII_dln_a-rhs_c)/max(1.,abs(rhs_c))
            metrics=expected.get("metrics")
            if metrics is not None:
                metrics["evaluations"]+=1
                metrics["max_rhs_scaled"]=max(metrics["max_rhs_scaled"],rhs_scaled)
            if rhs_scaled>2.e-10:
                raise ArithmeticError(
                    f"COMMON_INPUT_FULL_RHS_PARITY step={j} scaled={rhs_scaled:.17g}"
                )
            vc=np.asarray(expected["virtual"],dtype=float)
            ac=np.asarray(expected["average"],dtype=float)
            lc=np.asarray(expected["lyman"],dtype=float)
            if vc.shape!=(NVIRT,) or ac.shape!=(NVIRT,) or lc.shape!=(3,):
                raise ValueError("common-input C oracle spectrum shape mismatch")
            tr_ev=KB_NATIVE_EV_K*c.T0_K*(1.+z[j])
            fbb_v=1./np.expm1(table.energy_eV/tr_ev)
            line_energy=np.array((10.198714553953742,12.087365397278509,
                                  12.748393192442178))
            fbb_l=1./np.expm1(line_energy/tr_ev)
            vtol=1.e-7*np.maximum(np.abs(out.outgoing_virtual),np.abs(vc))+1.e-10*fbb_v
            atol=1.e-7*np.maximum(np.abs(out.average_virtual),np.abs(ac))+1.e-10*fbb_v
            ltol=1.e-7*np.maximum(np.abs(out.outgoing_lyman),np.abs(lc))+1.e-10*fbb_l
            bad_v=np.flatnonzero(np.abs(out.outgoing_virtual-vc)>vtol)
            bad_a=np.flatnonzero(np.abs(out.average_virtual-ac)>atol)
            bad_l=np.flatnonzero(np.abs(out.outgoing_lyman-lc)>ltol)
            if metrics is not None:
                metrics["max_virtual_tolerance_ratio"]=max(
                    metrics["max_virtual_tolerance_ratio"],
                    float(np.max(np.abs(out.outgoing_virtual-vc)/vtol)))
                metrics["max_average_tolerance_ratio"]=max(
                    metrics["max_average_tolerance_ratio"],
                    float(np.max(np.abs(out.average_virtual-ac)/atol)))
                metrics["max_lyman_tolerance_ratio"]=max(
                    metrics["max_lyman_tolerance_ratio"],
                    float(np.max(np.abs(out.outgoing_lyman-lc)/ltol)))
            if bad_v.size or bad_a.size or bad_l.size:
                detail=(f"virtual_bin={int(bad_v[0])}" if bad_v.size else
                        f"average_bin={int(bad_a[0])}" if bad_a.size else
                        f"lyman_bin={int(bad_l[0])}")
                raise ArithmeticError(f"COMMON_INPUT_PHOTON_PARITY step={j} {detail}")
        return out

    for j in range(N_ACCEPTED):
        if xhe[j]<=XHEII_MIN:
            raise RuntimeError(f"UNEXPECTED_H_ONLY_BRANCH at accepted step {j}")
        H=c.hubble_s(float(z[j]))
        dHe=helium_rhs(c,float(x1[j]),float(xhe[j]),H,float(z[j]))
        fhe[j]=dHe
        # The exact native joint He update consumes the derivative two steps ago.
        xhe[j+1]=xhe[j]+SOURCE_DLNA*(1.25*dHe-0.25*dHe_prev2)
        if not math.isfinite(xhe[j+1]):
            raise FloatingPointError(f"nonfinite helium state at accepted step {j}")

        # Current accepted source column. Commit only this outgoing result.
        current=full_rhs(j,float(xh[j]),float(xhe[j]),float(tm[j]))
        vout[:,j]=current.outgoing_virtual
        avgout[:,j]=current.average_virtual
        lyout[:,j]=current.outgoing_lyman
        fh[j]=current.dxHII_dln_a
        residual[j]=current.normalized_matrix_residual
        if residual[j]>2.e-10:
            raise FloatingPointError(f"Schur residual at accepted step {j}")

        znext=float(z[j+1])
        if post[j]:
            q=saha_xH1s(c,float(xhe[j+1]),znext)  # neutral H1s source closure
            qp=(1.+znext)*(saha_xH1s(c,float(xhe[j+1]),znext-0.5)
                            -saha_xH1s(c,float(xhe[j+1]),znext+0.5))
            deltaHe=0.01*(c.fHe-float(xhe[j+1]))
            if deltaHe==0 or not math.isfinite(deltaHe):
                raise FloatingPointError("invalid source helium post-Saha probe")
            x1p=saha_xH1s(c,float(xhe[j+1])+deltaHe,znext)
            x1m=saha_xH1s(c,float(xhe[j+1])-deltaHe,znext)
            dSaha_dHe=(x1p-x1m)/(2*deltaHe)
            fHe_center=helium_rhs(c,q,float(xhe[j+1]),
                                  c.hubble_s(znext),znext)
            qp+=dSaha_dHe*fHe_center
            # Source H post-Saha uses its own accepted prior radiation history;
            # each FULL evaluation's outgoing candidate is deliberately discarded.
            X=1.-q
            Tr=c.T0_K*(1.+znext)
            F0=full_rhs(j+1,X,float(xhe[j+1]),Tr).dxHII_dln_a
            deltaH=0.01*q
            if not (deltaH>0 and deltaH<X and X+deltaH<1):
                raise FloatingPointError("invalid hydrogen post-Saha probe")
            Fp=full_rhs(j+1,X+deltaH,float(xhe[j+1]),Tr).dxHII_dln_a
            Fm=full_rhs(j+1,X-deltaH,float(xhe[j+1]),Tr).dxHII_dln_a
            J=(Fp-Fm)/(2*deltaH)
            if J==0 or not math.isfinite(J):
                raise FloatingPointError("singular FULL hydrogen post-Saha Jacobian")
            x1next=q+(qp+F0)/J
            # Branch is changed only after the current next-node value is formed.
            post[j+1]=abs(x1next-q)<=DXHII_MAX
            x1[j+1]=x1next
            xh[j+1]=1.-x1[j+1]
            fh[j+1]=F0
        else:
            post[j+1]=False
            # ODE branch at the accepted input uses the already evaluated FULL RHS.
            xh[j+1]=xh[j]+SOURCE_DLNA*(1.25*fh[j]-0.25*dH_prev2)
            x1[j+1]=1.-xh[j+1]
        xe[j+1]=xh[j+1]+xhe[j+1]
        tm[j+1]=tm_steady_K(c,xe[j+1],znext,c.hubble_s(znext))
        if not (0<=xhe[j+1]<=c.fHe and 0<=xh[j+1]<=1 and tm[j+1]>0
                and all(math.isfinite(a) for a in (xe[j+1],tm[j+1]))):
            raise FloatingPointError(f"nonphysical accepted H+He node {j+1}")
        dHe_prev2=dHe_prev; dHe_prev=dHe
        dH_prev2=dH_prev
        if math.isfinite(fh[j]): dH_prev=fh[j]
        if abs((xh[j+1]+xhe[j+1])-xe[j+1])>5e-13:
            raise ArithmeticError("electron ledger mismatch")
        if abs((c.fHe-xhe[j+1])+xhe[j+1]-c.fHe)>5e-13:
            raise ArithmeticError("helium nucleus ledger mismatch")

    return FullStartHistory(
        iz=iz,z=z,xH1s=x1,xHII=xh,xHeII=xhe,xe=xe,Tm_K=tm,
        helium_rhs_dln_a=fhe[:N_ACCEPTED],hydrogen_rhs_dln_a=fh[:N_ACCEPTED],post_saha=post,
        virtual_out=vout,lyman_out=lyout,matrix_residual=residual,
        average_virtual=avgout,
        full_evaluations=full_evals,
    )
