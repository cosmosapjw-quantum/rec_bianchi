"""Original HyRec Oct-2012 high-z He stages, independently expressed in Python.

This bounded trajectory ends at source index izH0: HeIII Saha followed by
HeII->HeI post-Saha / source predictor-corrector while hydrogen stays in
Saha closure. It does not evolve FULL hydrogen or claim a full history.
Abundances xHeII/xHeIII and xe are per hydrogen nucleus.
"""
from __future__ import annotations

from dataclasses import dataclass
import math

DLNA = 8.49e-5
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
    nh = c.nH0_m3*(1+z)**3
    s = c.fsR**3*c.meR**3*2.414194e21*tr*math.sqrt(tr)*math.exp(-631462.7/tr)/nh
    x3 = 2*s*c.fHe/(1+s+c.fHe)/(1+math.sqrt(1+4*s*c.fHe/(1+s+c.fHe)**2))
    return 1+c.fHe+x3, x3


def saha_heii(c: HyRec2012Cosmology, z: float) -> float:
    """Return xHeII/nH in helium.c::rec_saha_xHeII."""
    tr = c.T0_K*(1+z)/c.fsR**2/c.meR
    nh = c.nH0_m3*(1+z)**3
    s = c.fsR**3*c.meR**3*2.414194e21*tr*math.sqrt(tr)*math.exp(-285325.0/tr)/nh*4
    return 2*s*c.fHe/(1+s)/(1+math.sqrt(1+4*s*c.fHe/(1+s)**2))


def saha_xH1s(c: HyRec2012Cosmology, xHeII: float, z: float) -> float:
    """Neutral hydrogen closure used by HyRec during the He stages."""
    tr=c.T0_K*(1+z)/c.fsR**2/c.meR
    nh=c.nH0_m3*(1+z)**3
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
    nh=c.nH0_m3*(1+z)**3
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
