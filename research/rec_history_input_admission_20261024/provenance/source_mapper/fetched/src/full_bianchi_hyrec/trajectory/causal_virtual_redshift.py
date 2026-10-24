"""Source-bound HyRec2012 FULL photon-history incoming-face advection.

This module implements the causal *incoming photon* (fplus) operation only.
The 311 zero-width virtual levels, two real atomic levels, and HyRec history
writeback/collision processes belong to separate original-C source owners.
This is not a FULL recombination solver or a substitute for native C.

For q=0 the time/energy/line-bin ownership follows original Oct2012
hydrogen.c::fplus_from_fminus and interp_Dfnu, with DLNA from hyrec_params.h.
An optional constant q = db/d(ln a) axisymmetric Bianchi-I ray experiment
uses the exact three-Killing-momentum relation. This kinematical background
is prescribed, not an Einstein-equation solution. At q != 0 the physical
Planck subtraction must be transported along the same ray: a zero initial
spectral distortion is NOT a zero final distortion.
"""
from __future__ import annotations

from dataclasses import dataclass
import math
import numpy as np

from full_bianchi_hyrec.trajectory.hmla_flrw import KB_NATIVE_EV_K

SOURCE_N_VIRTUAL = 311
SOURCE_N_SUB_LYA = 140
SOURCE_N_SUB_LYB = 271
SOURCE_DLNA = 8.49e-5
SOURCE_LINES_EV = (10.198714553953742, 12.087365397278509, 12.748393192442178)
_SOURCE_OWNER = "Original HyRec October 2012 hydrogen.c:633-716"


@dataclass(frozen=True)
class CausalIncomingResult:
    virtual_distortion: np.ndarray
    lya_lyb_incoming_distortion: np.ndarray
    retarded_eta: np.ndarray
    emission_mu: np.ndarray
    geometric_planck_correction: np.ndarray
    source: str = _SOURCE_OWNER

    def __post_init__(self):
        for key in ("virtual_distortion", "lya_lyb_incoming_distortion",
                    "retarded_eta", "emission_mu",
                    "geometric_planck_correction"):
            a = np.array(getattr(self, key), dtype=np.float64, copy=True)
            if not np.all(np.isfinite(a)):
                raise ValueError(f"nonfinite {key}")
            a.setflags(write=False)
            object.__setattr__(self, key, a)


def _source_edges(energies_eV: np.ndarray):
    e = np.asarray(energies_eV, dtype=np.float64)
    if e.shape != (SOURCE_N_VIRTUAL,) or not np.all(np.isfinite(e)):
        raise ValueError("HyRec FULL requires 311 finite virtual energies")
    if np.any(np.diff(e) <= 0) or np.any(e <= 0):
        raise ValueError("virtual energies must be positive and increasing")
    la, lb, lg = SOURCE_LINES_EV
    if not (e[139] < la < e[140] and e[270] < lb < e[271]
            and e[-1] < lg):
        raise ValueError("HyRec native Ly-alpha/beta/gamma bin ordering violated")
    src = np.arange(1, SOURCE_N_VIRTUAL + 1, dtype=np.intp)
    targets = np.r_[e, (la, lb)]
    source_energy = np.empty(SOURCE_N_VIRTUAL + 2, dtype=np.float64)
    source_energy[:SOURCE_N_VIRTUAL-1] = e[1:]
    # Exactly these native source rows are Lyman accepted-step boundaries.
    for b, source_row, line_energy in ((139, 311, la),
                                       (270, 312, lb),
                                       (310, 313, lg)):
        src[b] = source_row
        source_energy[b] = line_energy
    src = np.r_[src, (140, 271)]
    source_energy[-2:] = e[[140, 271]]
    if not np.all(source_energy > targets):
        raise ValueError("incoming source energy must exceed target energy")
    return src, targets, source_energy


def safe_constant_shear_dlna(
    energies_eV, *, shear_q: float, safety: float=0.975,
) -> float:
    """Conservative CFL-like causal HISTORY condition for constant q.

    For each neighboring frequency jump, the physical emission time must
    precede the final accepted step: d_eta_emission > d_eta_step.
    Along all constant-q directions, d ln E / d ln a in the past is
    bounded by max(1-q,1+2q). Hence the grid-wide sufficient condition

      d_eta_step < min_b ln(E_source_b/E_target_b) / max(1-q,1+2q).

    This is sufficient (not necessary) and does not prove a fully coupled
    atomic/thermal system's stability. Native q=0 uses 8.49e-5 separately.
    """
    if not math.isfinite(shear_q) or not (-.5 < shear_q < 1.):
        raise ValueError("no globally positive directional redshift")
    if not math.isfinite(safety) or not (0 < safety < 1):
        raise ValueError("required strict causal safety factor in (0,1)")
    _, targets, sources = _source_edges(np.asarray(energies_eV))
    source_ratio_min = float(np.min(np.log(sources/targets)))
    max_dir_rate = max(1.0-shear_q,1.0+2.0*shear_q)
    return min(SOURCE_DLNA, safety*source_ratio_min/max_dir_rate)


def _retarded_lookback(logratio: np.ndarray, mu_face: np.ndarray,
                       q: float):
    """Invert exact E_i/E_f with constant q, monotonically in lookback eta.

    E_i/E_f=exp(d) * R; R^2=exp(-2*q*d)*(1-mu_f^2)
                                 +exp(4*q*d)*mu_f^2.
    The source directional expansion H_dir/H = 1 + q*(3*mu^2-1)
    is positive for ALL directions if -1/2<q<1.
    """
    lr, mu = np.broadcast_arrays(np.asarray(logratio, dtype=float),
                                 np.asarray(mu_face, dtype=float))
    if not np.all(np.isfinite(lr)) or np.any(lr <= 0):
        raise ValueError("source redshift logratio must be strictly positive")
    if not np.all(np.isfinite(mu)) or np.any(np.abs(mu) > 1):
        raise ValueError("emission directions must be physical")
    if not math.isfinite(q) or not (-.5 < q < 1.):
        raise ValueError("no globally positive directional redshift")
    if q == 0.0:
        return lr.copy(), mu.copy(), np.zeros(lr.shape, dtype=float)
    min_rate = min(1.0 - q, 1.0 + 2.0*q)
    max_rate = max(1.0 - q, 1.0 + 2.0*q)
    lo = lr/max_rate
    hi = lr/min_rate
    d = np.clip(lr/(1.0+q*(3.0*mu*mu-1.0)), lo, hi)
    mu2 = mu*mu

    def evaluate(z):
        e6 = np.exp(6.0*q*z)
        v = 1.0 + mu2*np.expm1(6.0*q*z)
        log_R = -q*z + .5*np.log(v)
        der = 1.0-q+3.0*q*mu2*e6/v
        return z+log_R-lr, der, log_R

    tol = 5e-14*max(1.0, float(np.max(lr)))
    for _ in range(48):
        val, der, _ = evaluate(d)
        active = np.abs(val) > tol
        if not np.any(active):
            break
        lo = np.where(active & (val < 0), d, lo)
        hi = np.where(active & (val > 0), d, hi)
        next_newton = d-val/der
        candidate = np.where((next_newton > lo) & (next_newton < hi),
                             next_newton, .5*(lo+hi))
        d = np.where(active, candidate, d)
    val, _, log_R = evaluate(d)
    if np.max(np.abs(val)) > 2e-12*max(1.0, float(np.max(lr))):
        raise FloatingPointError("retarded energy root did not converge")
    # Exact unit-vector map, no linearized angular drift.
    mu_emit = mu*np.exp(2.0*q*d-log_R)
    if np.any(np.abs(mu_emit) > 1+2e-12):
        raise FloatingPointError("Killing direction map violates unit sphere")
    mu_emit = np.clip(mu_emit, -1.0, 1.0)
    return d, mu_emit, log_R


def _planck_difference(x: np.ndarray, log_R: np.ndarray):
    """n_P(x*R)-n_P(x), stable for |log R| << 1 and Ly-alpha x ~ 40."""
    if not np.all(np.isfinite(x)) or np.any(x <= 0):
        raise ValueError("positive finite dimensionless photon energy required")
    shifted = x*np.exp(log_R)
    if np.any(shifted > 600) or np.any(x > 600):
        raise ValueError("Planck distortion energy outside validated binary64 domain")
    delta_x = x*np.expm1(log_R)
    return -np.exp(x)*np.expm1(delta_x)/(np.expm1(x)*np.expm1(shifted))


def causal_incoming_from_accepted_histories(
    *, energies_eV, virtual_history, lyman_history,
    z_start: float, iz: int, z_face: float,
    mu_face=(0.0,), mu_grid=(0.0,), shear_q: float=0.0,
    radiation_T_face_K: float | None=None,
    dlna: float=SOURCE_DLNA,
) -> CausalIncomingResult:
    """Return 311 incoming virtual fields + 2 incoming Lyman boundary fields.

    The accepted histories are [N_mu, 311, iz] and [N_mu, 3, iz],
    or [311, iz]/[3, iz] for angularly isotropic data.
    Samples 0..iz-1 are committed; index iz is never read. Time interpolation
    is source C's two-neighbor linear reconstruction. Angle interpolation is
    convex in source emission mu. No synthetic future owner is allowed.

    For nonzero q, delta f means physical photon occupation minus an
    isotropic blackbody at T_rad~a^-1. Its geometric correction is mandatory.
    The caller supplies T_rad(face) and accepts prescribed constant shear.
    Bianchi pre-history before z_start has NO automatically invented BC.
    """
    if not isinstance(iz, (int, np.integer)) or iz < 2:
        raise ValueError("at least 2 accepted past steps required")
    if not (math.isfinite(z_start) and math.isfinite(z_face)
            and z_start >= z_face >= 0):
        raise ValueError("invalid source recombination redshift interval")
    if not math.isfinite(dlna) or not (0 < dlna <= SOURCE_DLNA):
        raise ValueError("history clock requires source-compliant positive DLNA")
    src, target_e, source_e = _source_edges(np.asarray(energies_eV))
    vv = np.asarray(virtual_history, dtype=float)
    ll = np.asarray(lyman_history, dtype=float)
    if vv.ndim == 2:
        vv = vv[None, :, :]
    if ll.ndim == 2:
        ll = ll[None, :, :]
    n_mu = vv.shape[0]
    if (vv.shape != (n_mu, SOURCE_N_VIRTUAL, iz)
        or ll.shape != (n_mu, 3, iz)
        or not np.all(np.isfinite(vv)) or not np.all(np.isfinite(ll))):
        raise ValueError("accepted native virtual/lyman history shapes invalid")
    mu_g = np.asarray(mu_grid, dtype=float)
    mu_f = np.asarray(mu_face, dtype=float)
    if (mu_g.shape != (n_mu,) or mu_f.ndim != 1 or mu_f.size < 1
        or not np.all(np.isfinite(mu_f)) or not np.all(np.isfinite(mu_g))
        or np.any(np.abs(mu_f) > 1) or np.any(np.abs(mu_g) > 1)):
        raise ValueError("direction grid and rays incompatible")
    if n_mu > 1 and np.any(np.diff(mu_g) <= 0):
        raise ValueError("mu grid must strictly increase")
    if shear_q != 0.0:
        if n_mu < 2 or mu_g[0] > -1 or mu_g[-1] < 1:
            raise ValueError("Bianchi needs full directional source history [-1,1]")
        if (radiation_T_face_K is None or not math.isfinite(radiation_T_face_K)
            or radiation_T_face_K <= 0):
            raise ValueError("Bianchi requires source thermal subtraction in K")
    else:
        # For q=0 full mu_grid support is allowed; the geometric correction
        # is identically zero even when the query clock is rounded.
        pass
    eta_start = -math.log1p(z_start)
    eta_face = -math.log1p(z_face)
    # Source-C clock: -log((1+z) E_s/E_f).  Use the ratio for weak-anisotropy
    # root; exact q=0 reproduces its (physical) characteristic relation.
    logratios = np.log(source_e/target_e)
    lookback, emission_mu, log_R = _retarded_lookback(
        logratios[None, :], mu_f[:, None], shear_q)
    eta_emit = eta_face-lookback
    upper_accepted = eta_start+dlna*(iz-1)
    before = eta_emit < eta_start
    # HyRec C interprets pre-zstart incoming delta f as zero/thermal at q=0.
    if shear_q != 0 and np.any(before):
        raise ValueError("anisotropic incoming photon before the source-owned history")
    active = ~before
    if np.any(eta_emit[active] >= upper_accepted):
        raise ValueError("incoming photon would read current/unaccepted future history")
    # Safe gather for non-active points, then mask their contribution.
    # Keep the final physical interpolation *interval* [iz-2, iz-1).
    # Clipping to iz-2 would incorrectly erase the fractional delay near
    # current time and fail exact original-C parity for 2 accepted steps.
    ix = np.maximum((eta_emit-eta_start)/dlna, 0.0)
    ix = np.minimum(ix, np.nextafter(float(iz-1), -math.inf))
    it = np.minimum(np.floor(ix).astype(np.intp), iz-2)
    ft = ix-it
    if n_mu == 1:
        im0 = np.zeros_like(it)
        im1 = im0
        fa = np.zeros_like(ft)
    else:
        im1 = np.searchsorted(mu_g, emission_mu, side="right")
        im1 = np.clip(im1, 1, n_mu-1)
        im0 = im1-1
        fa = (emission_mu-mu_g[im0])/(mu_g[im1]-mu_g[im0])
        # Never silently extrapolate an unrepresented directional source.
        if np.any((fa < -1e-12) | (fa > 1+1e-12)):
            raise ValueError("emission direction requires angular extrapolation")
        fa = np.clip(fa, 0.0, 1.0)
    # Two source-owned history arrays: virtual 311 and Lyman redward 3.
    # Do NOT np.concatenate(vv,ll) here: that would copy N_mu*314*iz
    # accepted-memory doubles on every source evaluation (~27 MB for the
    # validated 17-direction/640-step benchmark). Gather the sparse 313
    # face samples directly from each immutable owner block instead.
    incoming = np.empty(it.shape, dtype=np.float64)
    for cols, hist, offset in (
        (np.flatnonzero(src < SOURCE_N_VIRTUAL), vv, 0),
        (np.flatnonzero(src >= SOURCE_N_VIRTUAL), ll, SOURCE_N_VIRTUAL),
    ):
        if not cols.size:
            continue
        t = it[:, cols]
        w = ft[:, cols]
        a = fa[:, cols]
        rows = (src[cols]-offset)[None,:]
        left = ((1-w)*hist[im0[:,cols], rows, t]
                +w*hist[im0[:,cols], rows, t+1])
        right = ((1-w)*hist[im1[:,cols], rows, t]
                 +w*hist[im1[:,cols], rows, t+1])
        incoming[:,cols] = np.where(
            active[:,cols], left*(1-a)+right*a, 0.0
        )
    geom = np.zeros_like(incoming)
    if shear_q != 0:
        x = target_e[None,:]/(KB_NATIVE_EV_K*radiation_T_face_K)
        geom = _planck_difference(x, log_R)
        incoming = incoming+geom
    return CausalIncomingResult(
        virtual_distortion=incoming[:,:SOURCE_N_VIRTUAL],
        lya_lyb_incoming_distortion=incoming[:,SOURCE_N_VIRTUAL:],
        retarded_eta=eta_emit,
        emission_mu=emission_mu,
        geometric_planck_correction=geom,
    )
