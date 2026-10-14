"""Finite-interval normal-comoving axisymmetric Bianchi-I background.

Scientific lane: prescribed density-fixed LRS Bianchi I (or explicit same-H
counterfactual), NOT an Einstein--matter backreaction solution or an adopted
REI production driver.  Physical clock t is in proper seconds from a_ref.
Both dt/dL=1/H and db/dL=s/H are evaluated using the same positive-rate
cubic Hermite interpolant over the supplied scale-factor interval.

No large cumulative times or separately rounded global logarithms are
subtracted to reconstruct a short physical step.
"""
from __future__ import annotations

from dataclasses import dataclass, field
import bisect
import hashlib
import json
import math
from typing import Sequence

import numpy as np

from .sequence import BackgroundSnapshotSequence

_METHOD = "rec_lrs_bianchi_i_positive_rate_hermite_1"
_AREF = 1.0 / 21.0
_AEND = 0.2


@dataclass(frozen=True, slots=True)
class BianchiIModelParameters:
    h0_per_s: float = 67.4 * 1e5 / 3.0856775814913673e24
    omega_m: float = 0.315
    omega_r: float = 9.2e-5
    omega_lambda: float = 1.0 - 0.315 - 9.2e-5

    def __post_init__(self):
        data = (self.h0_per_s, self.omega_m, self.omega_r, self.omega_lambda)
        if not all(math.isfinite(v) for v in data) or self.h0_per_s <= 0:
            raise ValueError("cosmological parameters must be finite, h0 positive")
        if min(self.omega_m, self.omega_r, self.omega_lambda) < 0:
            raise ValueError("density coefficients must be nonnegative")
        if self.omega_m + self.omega_r + self.omega_lambda <= 0:
            raise ValueError("positive H^2 required")

    def hubble_flrw(self, a: float) -> float:
        if not math.isfinite(a) or a <= 0:
            raise ValueError("a must be positive and finite")
        H = self.h0_per_s * math.sqrt(
            self.omega_m / a**3 + self.omega_r / a**4 + self.omega_lambda
        )
        if not math.isfinite(H) or H <= 0:
            raise ValueError("nonpositive or nonfinite H_FLRW")
        return H


@dataclass(frozen=True, slots=True)
class FiniteBianchiIIncrement:
    a1: float
    a2: float
    delta_l: float
    delta_t_s: float
    delta_b: float
    cells_crossed: int
    method_identity: str = _METHOD


@dataclass(frozen=True, slots=True)
class BianchiIPhysicalPoint:
    a: float
    b: float
    t_s: float
    H_s_inv: float
    s_s_inv: float
    sigma_ratio: float
    deceleration_q: float


def _moments(z: float) -> tuple[float, float, float, float]:
    """Integral y^n exp(-z*y) from 0 to 1, n=0..3; small positive z."""
    if not math.isfinite(z) or not 0 <= z <= 0.1:
        raise ValueError("exponential moment is outside validated small-z domain")
    vals = []
    for n in range(4):
        term = 1.0
        terms = []
        for k in range(22):
            terms.append(term / (n + k + 1))
            term *= -z / (k + 1)
        vals.append(math.fsum(terms))
    return tuple(vals)


def _coeff(f0: float, f1: float, d0: float, d1: float, h: float):
    diff = f1 - f0
    return (
        f0, h*d0,
        3*diff - h*(2*d0+d1),
        -2*diff + h*(d0+d1),
    )


def _segment(coeff, u: float, v: float, h: float, s_left: float):
    """Integrate one Hermite cell segment without cumulative cancellation."""
    if not all(math.isfinite(x) for x in (u, v, h, s_left)):
        raise ValueError("nonfinite segment")
    if not (0 <= u <= 1 and 0 < v and u+v <= 1+5e-12 and h > 0):
        raise ValueError("invalid or out-of-cell segment")
    c0, c1, c2, c3 = coeff
    a0 = ((c3*u+c2)*u+c1)*u+c0
    a1 = v*(c1+2*c2*u+3*c3*u*u)
    a2 = v*v*(c2+3*c3*u)
    a3 = v*v*v*c3
    dL = h*v
    dt = dL*math.fsum((a0, a1/2, a2/3, a3/4))
    if not math.isfinite(dt) or dt <= 0:
        raise ValueError("nonpositive or nonfinite proper interval")
    if s_left == 0:
        return dt, 0.0
    m = _moments(3*dL)
    db = dL*s_left*math.fsum((a0*m[0],a1*m[1],a2*m[2],a3*m[3]))
    if not math.isfinite(db):
        raise ValueError("nonfinite shear increment")
    return dt, db


@dataclass(frozen=True, slots=True)
class AxisymmetricBianchiIBackground:
    """Versioned positive-clock supplier; finite component validation only."""

    q_ref: float
    cells: int = 1024
    same_h: bool = False
    cosmology: BianchiIModelParameters = field(default_factory=BianchiIModelParameters)
    a_ref: float = _AREF
    a_end: float = _AEND
    b_ref: float = 0.0
    t_ref_s: float = 0.0
    _h: float = field(init=False, repr=False)
    _l_end: float = field(init=False, repr=False)
    _s_ref: float = field(init=False, repr=False)
    _knots: tuple[float, ...] = field(init=False, repr=False)
    _coefficients: tuple[tuple[float, ...], ...] = field(init=False, repr=False)
    _source_sha256: str = field(init=False, repr=False)

    def __post_init__(self):
        vals=(self.q_ref,self.a_ref,self.a_end,self.b_ref,self.t_ref_s)
        if not all(math.isfinite(v) for v in vals):
            raise ValueError("nonfinite background parameter")
        if not 0 < self.a_ref < self.a_end:
            raise ValueError("invalid expanding a domain")
        if self.cells not in (1024, 2048):
            raise ValueError("only validated 1024 or 2048 Hermite mesh")
        if not isinstance(self.cosmology,BianchiIModelParameters):
            raise TypeError("cosmology requires BianchiIModelParameters")
        object.__setattr__(self,"same_h",bool(self.same_h))
        L=math.log(self.a_end/self.a_ref)
        h=L/self.cells
        if 30537*math.exp(3*h)*h**4/384 >= 1:
            raise ValueError("the exact-node positivity premise fails")
        s_ref=self.q_ref*self.cosmology.hubble_flrw(self.a_ref)
        object.__setattr__(self,"_l_end",L)
        object.__setattr__(self,"_h",h)
        object.__setattr__(self,"_s_ref",s_ref)
        knots=tuple(
            self.a_ref if j==0 else self.a_end if j==self.cells
            else self.a_ref*math.exp(j*h)
            for j in range(self.cells+1)
        )
        if not all(y>x for x,y in zip(knots,knots[1:])):
            raise ValueError("non-monotone binary64 table knots")
        object.__setattr__(self,"_knots",knots)
        coeffs=[]
        for j in range(self.cells):
            f0,d0=self._rate_slope(j*h)
            f1,d1=self._rate_slope((j+1)*h)
            coeffs.append(_coeff(f0,f1,d0,d1,h))
        object.__setattr__(self,"_coefficients",tuple(coeffs))
        identity=(
            _METHOD,self.cells,int(self.same_h),*(
                x.hex() for x in (self.q_ref,self.a_ref,self.a_end,self.b_ref,
                self.t_ref_s,self.cosmology.h0_per_s,self.cosmology.omega_m,
                self.cosmology.omega_r,self.cosmology.omega_lambda)
            )
        )
        object.__setattr__(
            self,"_source_sha256",hashlib.sha256(
                json.dumps(identity,separators=(",",":")).encode("utf-8")
            ).hexdigest()
        )

    @property
    def source_sha256(self) -> str:
        """Identity for this numerical *model*, not the REI native binary."""
        return self._source_sha256

    def _rate_slope(self,L:float):
        c=self.cosmology
        e3=math.exp(-3*L);e4=math.exp(-4*L);e6=math.exp(-6*L)
        terms=(c.h0_per_s**2*c.omega_lambda,
               c.h0_per_s**2*c.omega_m/self.a_ref**3*e3,
               c.h0_per_s**2*c.omega_r/self.a_ref**4*e4,
               0.0 if self.same_h else self._s_ref**2*e6)
        S=math.fsum(terms)
        if not math.isfinite(S) or S<=0:
            raise ValueError("nonpositive rate squared")
        F=1/math.sqrt(S)
        weighted=math.fsum((3*terms[1],4*terms[2],6*terms[3]))/S
        return F, 0.5*weighted*F

    def interval(self,a1:float,a2:float) -> FiniteBianchiIIncrement:
        if not all(math.isfinite(a) for a in (a1,a2)):
            raise ValueError("nonfinite endpoints")
        if not self.a_ref <= a1 < a2 <= self.a_end:
            raise ValueError("endpoints outside expanding domain or reversed")
        dl=math.log1p((a2-a1)/a1)
        if dl <= 0:
            raise ValueError("collapsed interval in supplied binary64 endpoints")
        idx=max(0,min(self.cells-1,bisect.bisect_right(self._knots,a1)-1))
        curr=a1; dt_parts=[];db_parts=[];counts=0
        while curr < a2:
            if idx>=self.cells:
                raise ValueError("background table exhausted before a2")
            left_node=self._knots[idx]
            right=min(a2,self._knots[idx+1])
            if right <= curr:
                raise ValueError("stagnation on binary64 table interval")
            u=math.log1p((curr-left_node)/left_node)/self._h
            v=math.log1p((right-curr)/curr)/self._h
            s_left=self._s_ref*(self.a_ref/curr)**3
            dt,db=_segment(self._coefficients[idx],u,v,self._h,s_left)
            dt_parts.append(dt);db_parts.append(db)
            curr=right;idx+=1;counts+=1
            if counts>self.cells+1:
                raise ValueError("cell traversal exceeded finite bound")
        dt=math.fsum(dt_parts);db=math.fsum(db_parts)
        return FiniteBianchiIIncrement(a1,a2,dl,dt,db,counts)

    def point(self,a:float)->BianchiIPhysicalPoint:
        if not math.isfinite(a) or not self.a_ref<=a<=self.a_end:
            raise ValueError("point outside background domain")
        if a==self.a_ref:
            dt=0.0;db=0.0
        else:
            inc=self.interval(self.a_ref,a);dt=inc.delta_t_s;db=inc.delta_b
        L=math.log(a/self.a_ref)
        F,dF=self._rate_slope(L)
        H=1/F
        s=self._s_ref*(self.a_ref/a)**3
        m1=2*dF/F
        return BianchiIPhysicalPoint(
            a=a,b=self.b_ref+db,t_s=self.t_ref_s+dt,
            H_s_inv=H,s_s_inv=s,sigma_ratio=s/H,deceleration_q=-1+0.5*m1
        )

    def snapshots(self,eta_grid:Sequence[float],eta_anchor:float=0.0):
        """Build real BackgroundSnapshotSequence nodes usable by REC transport.

        eta_grid = eta_anchor + ln(a/a_ref). This is a prescribed *geometry*
        supplier, NOT a backreacting Bianchi-I matter/HyRec evolution.
        """
        eta=np.asarray(eta_grid,dtype=float)
        if eta.ndim!=1 or eta.size<2 or not np.all(np.isfinite(eta)):
            raise ValueError("eta_grid requires finite 1D nodes")
        if not np.all(np.diff(eta)>0):
            raise ValueError("eta must be increasing")
        if not math.isfinite(eta_anchor) or float(eta[0])!=eta_anchor:
            raise ValueError("eta_grid first node must equal eta_anchor")
        L=np.asarray(eta-eta_anchor)
        if L[-1] > self._l_end + 8*math.ulp(self._l_end) or L[0]<0:
            raise ValueError("eta_grid exceeds physical model domain")
        # Only accept the representable round-trip of the exact upper endpoint.
        points=[]
        for l in L:
            a=self.a_ref*math.exp(float(l))
            if a>self.a_end and abs(a-self.a_end)<=2*math.ulp(self.a_end):
                a=self.a_end
            points.append(self.point(a))
        n=len(points)
        sigma=np.zeros((n,3,3))
        for i,p in enumerate(points):
            sigma[i]=np.diag([-p.s_s_inv,-p.s_s_inv,2*p.s_s_inv])
        empty33=np.zeros_like(sigma)
        empty3=np.zeros((n,3))
        return BackgroundSnapshotSequence(
            model_name="Bianchi_I_axisymmetric_prescribed_clock",
            chart_id="lrs_bianchi_i_prescribed",
            bianchi_type="I",
            tau=eta,cosmic_time_s=np.asarray([p.t_s for p in points]),
            H_s_inv=np.asarray([p.H_s_inv for p in points]),
            q=np.asarray([p.deceleration_q for p in points]),
            sigma_s_inv=sigma,N_s_inv=empty33,A_s_inv=empty3,
            frame_rotation_s_inv=empty3,beta_H=empty3,D0_beta_H_s_inv=empty3,
            source_path="model://rec_lrs_bianchi_i_positive_rate_hermite_1",
            source_sha256=self.source_sha256,
            provenance={
                "model":"prescribed physical-density-fixed" if not self.same_h
                         else "explicit same-H diagnostic",
                "method_identity":_METHOD,
                "time_coordinate":"tau=eta_anchor+ln(a/a_ref); proper seconds since t_ref_s",
                "coupled_Einstein_matter":"NOT_CLAIMED",
            },
            provider_branch_flags={
                "prescribed_non_tilted_bianchi_i":True,
                "geometry_background_only":True,
                "no_backreaction":True,
            },
        )


def axisymmetric_photon_map(mu_initial:float,inc:FiniteBianchiIIncrement):
    """Exact null energy, axial direction and solid-angle map; no scattering."""
    if not math.isfinite(mu_initial) or abs(mu_initial)>1:
        raise ValueError("initial direction cosine must lie in [-1,1]")
    B=inc.delta_b
    if not math.isfinite(inc.delta_l) or not math.isfinite(B):
        raise ValueError("nonfinite null-map increment")
    ep=math.exp(2*B);ez=math.exp(-4*B)
    R=math.sqrt(ep*(1-mu_initial*mu_initial)+ez*mu_initial*mu_initial)
    if not math.isfinite(R) or R<=0:
        raise ValueError("invalid Bianchi-I null-map factor")
    mu_final=mu_initial*math.sqrt(ez)/R
    return {
        "energy_ratio":math.exp(-inc.delta_l)*R,
        "mu_final":max(-1.0,min(1.0,mu_final)),
        "solid_angle_jacobian":R**-3,
    }
