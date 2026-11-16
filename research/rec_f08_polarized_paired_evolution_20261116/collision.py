"""Exact elastic Thomson evolution on a degree-four angular quadrature.

The state is a Hermitian transverse 3 x 3 *mass* coherency S_i, with
Tr(S_i) in photons/H at a fixed physical energy.  Angular weights sum to one.
With P_i = 1 - n_i n_i^T and M = sum_i S_i, the frozen-tetrad equation is

    dS_i/dtau = (3/2) w_i P_i M P_i - S_i,
    tau = c sigma_T integral n_e dt.

Positive degree-four-exact weights close the moment equation: its scalar,
real symmetric trace-free, and imaginary antisymmetric parts have decay
rates 0, 3/10, and 1/2.  This module evaluates the resulting exact semigroup.
It neither changes the supplied quadrature nor renormalizes the answer.

Stokes convention: Q = I_theta - I_phi, U = 2 Re C_theta,phi,
V = 2 Im C_theta,phi.  The last convention is stated explicitly because
the sign assigned to circular polarization varies across references.

The caller owns spectral transport, frame transport, and any conversion
between original equal-q-cell masses and physical quadrature masses.
"""
from __future__ import annotations

import math
import numpy as np


def _directions(n):
    n = np.asarray(n, dtype=float)
    if n.ndim != 2 or n.shape[1] != 3 or not len(n) or not np.isfinite(n).all():
        raise ValueError("directions must be a finite nonempty (n, 3) array")
    if np.max(np.abs(np.sum(n * n, axis=1) - 1.0)) > 8e-15:
        raise ValueError("directions must be unit vectors")
    return n


def screen_basis(n):
    """Return (e_theta, e_phi); use a fixed meridian at exact poles."""
    n = _directions(n)
    ep = np.column_stack((-n[:, 1], n[:, 0], np.zeros(len(n))))
    norm = np.linalg.norm(ep, axis=1)
    pole = norm == 0.0
    ep[pole] = (0.0, 1.0, 0.0)
    norm[pole] = 1.0
    ep /= norm[:, None]
    return np.cross(ep, n), ep


def _screens(n):
    et, ep = screen_basis(n)
    return np.stack((et, ep), axis=-1)


def stokes_to_coherency(stokes, n):
    """Convert (..., n, 4) I,Q,U,V masses to (..., n, 3,3)."""
    n = _directions(n)
    s = np.asarray(stokes, dtype=float)
    if s.shape[-2:] != (len(n), 4) or not np.isfinite(s).all():
        raise ValueError("Stokes state must have finite shape (..., n, 4)")
    c = np.empty(s.shape[:-1] + (2, 2), dtype=complex)
    c[..., 0, 0] = (s[..., 0] + s[..., 1]) / 2.0
    c[..., 1, 1] = (s[..., 0] - s[..., 1]) / 2.0
    c[..., 0, 1] = (s[..., 2] + 1j * s[..., 3]) / 2.0
    c[..., 1, 0] = c[..., 0, 1].conj()
    e = _screens(n)
    return np.einsum("iab,...ibc,idc->...iad", e, c, e, optimize=True)


def coherency_to_stokes(coherency, n):
    """Convert (..., n,3,3) transverse coherency masses to I,Q,U,V."""
    n = _directions(n)
    s = np.asarray(coherency)
    if s.shape[-3:] != (len(n), 3, 3) or not np.isfinite(s).all():
        raise ValueError("coherency must have finite shape (..., n, 3, 3)")
    e = _screens(n)
    c = np.einsum("iba,...ibc,icd->...iad", e, s, e, optimize=True)
    return np.stack((
        (c[..., 0, 0] + c[..., 1, 1]).real,
        (c[..., 0, 0] - c[..., 1, 1]).real,
        2.0 * c[..., 0, 1].real,
        2.0 * c[..., 0, 1].imag,
    ), axis=-1)


def validate_quadrature(n, w):
    """Check the moment identities required by this *exact* finite operator.

    The 8e-15 absolute algebra check is inherited from the physical moment
    construction.  It is unrelated to the historical 3% science gate.
    """
    n = _directions(n)
    w = np.asarray(w, dtype=float)
    if w.shape != (len(n),) or not np.isfinite(w).all() or np.min(w) <= 0.0:
        raise ValueError("positive finite angular weights required")
    eye = np.eye(3)
    if abs(float(w.sum()) - 1.0) > 8e-15:
        raise ValueError("angular weights must sum to one")
    if np.max(abs(n.T @ (w[:, None] * n) - eye / 3.0)) > 8e-15:
        raise ValueError("second angular moment is not exact")
    fourth = np.einsum("i,ia,ib,ic,id->abcd", w, n, n, n, n)
    target = (np.einsum("ab,cd->abcd", eye, eye)
              + np.einsum("ac,bd->abcd", eye, eye)
              + np.einsum("ad,bc->abcd", eye, eye)) / 15.0
    if np.max(abs(fourth - target)) > 8e-15:
        raise ValueError("fourth angular moment is not exact")
    return n, w


def _state_and_geometry(coherency, n, w, tau, validate):
    n = _directions(n)
    w = np.asarray(w, dtype=float)
    s = np.asarray(coherency)
    tau = float(tau)
    if not math.isfinite(tau) or tau < 0.0:
        raise ValueError("optical depth must be finite and nonnegative")
    if s.shape[-3:] != (len(n), 3, 3) or not np.isfinite(s).all():
        raise ValueError("coherency must have finite shape (..., n, 3, 3)")
    if w.shape != (len(n),) or not np.isfinite(w).all() or np.min(w) <= 0.0:
        raise ValueError("positive finite angular weights required")
    p = np.eye(3) - n[:, :, None] * n[:, None, :]
    if validate:
        validate_quadrature(n, w)
        scale = max(float(np.max(np.abs(s))), np.finfo(float).tiny)
        if np.max(abs(s - np.swapaxes(s.conj(), -1, -2))) > 3e-14 * scale:
            raise ValueError("non-Hermitian coherency state")
        if np.max(abs(np.einsum("...iab,ib->...ia", s, n))) > 3e-14 * scale:
            raise ValueError("coherency is not transverse to photon directions")
        # Positivity is a precondition for physical states; the linear API also
        # deliberately accepts signed perturbations for independent validation.
    return s, n, w, p, tau


def collision_increment(coherency, n, w, tau, *, validate=True):
    """Return E_tau(S)-S without subtracting two nearly equal large states.

    Input shape may have any leading batch dimensions, e.g. energy bins.
    For very small tau, derive delta-Q/U/V from this increment and add them
    to separately stored Stokes components.  Extracting Q by subtracting
    full Cartesian coherency diagonals can erase a very weak signal.
    """
    s, n, w, p, tau = _state_and_geometry(coherency, n, w, tau, validate)
    if tau == 0.0:
        return np.zeros_like(s)
    m = np.sum(s, axis=-3)
    trace = np.trace(m, axis1=-2, axis2=-1).real
    iso = trace[..., None, None] * np.eye(3) / 3.0
    symmetric = (m.real + np.swapaxes(m.real, -1, -2)) / 2.0
    stf = symmetric - iso
    antisymmetric = (m - np.swapaxes(m, -1, -2)) / 2.0
    a = -math.expm1(-tau)
    b = math.exp(-0.3 * tau) * (-math.expm1(-0.7 * tau)) / 0.7
    c = 2.0 * math.exp(-0.5 * tau) * (-math.expm1(-0.5 * tau))
    # Subtract the isotropic equilibrium before multiplying by small tau.
    equilibrium = 0.5 * trace[..., None, None, None] * w[:, None, None] * p
    anisotropic = b * stf + c * antisymmetric
    gain = 1.5 * w[:, None, None] * np.einsum(
        "iab,...bc,icd->...iad", p, anisotropic, p, optimize=True)
    return -a * (s - equilibrium) + gain


def exact_collision(coherency, n, w, tau, *, validate=True):
    """Advance a frozen physical-tetrad state through optical depth tau."""
    s = np.asarray(coherency)
    return s + collision_increment(s, n, w, tau, validate=validate)


def exact_collision_stokes(stokes, n, w, tau, *, validate=True):
    """Advance persistent Stokes masses while retaining small Q/U/V updates."""
    stokes = np.asarray(stokes, dtype=float)
    s = stokes_to_coherency(stokes, n)
    delta = collision_increment(s, n, w, tau, validate=validate)
    return stokes + coherency_to_stokes(delta, n)
