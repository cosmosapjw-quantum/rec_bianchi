"""Source-measure adapter for the F08 native photon receiver.

This is a conditional, nonlinear collocation closure.  The exact linear
physical-mass semigroup lives in collision.py.  Here A=w/J converts the
original equal-q-cell samples, and the inverse projection is normalized
separately at each *physical* energy.  Its extra scalar extinction and raw
normalization drift are explicit diagnostics, not hidden conservation fixes.
"""
from __future__ import annotations
from pathlib import Path
import sys
import numpy as np

BASE = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE.parent / "rec_tetrad_thomson_repair_20261116"))
from thomson_tetrad import tetrad_grid, physical_weights
from collision import collision_increment, stokes_to_coherency, coherency_to_stokes

C_CM_S = 29979245800.0
SIGMA_T_CM2 = 6.6524587051e-25
FHE = 0.083

def electron_density(gas, H, time_s):
    xh, he2, he3 = np.asarray(gas, float)[:3]
    if not (0 <= xh <= 1 and 0 <= he2 and 0 <= he3 and he2 + he3 <= 1):
        raise ValueError("native H/He fractions outside original domain")
    nH = 1e-4 * np.exp(-float(np.sum(H)) * time_s)
    return nH * (xh + FHE * (he2 + 2 * he3))

def cone_diagnostics(stokes):
    a = np.asarray(stokes, float)
    scale = max(float(np.max(a[..., 0])), np.finfo(float).tiny)
    if not np.isfinite(a).all():
        raise ValueError("nonfinite persistent Stokes state")
    defect = np.linalg.norm(a[..., 1:], axis=-1) - a[..., 0]
    maximum = max(0.0, float(np.max(defect))) / scale
    if float(np.min(a[..., 0])) < 0 or maximum > 256 * np.finfo(float).eps:
        raise ValueError("persistent photon Stokes cone")
    return maximum

def collide_native(stokes, q, H, time_s, tau, degree=4):
    """Advance q-cell Stokes, keeping every physical-energy group total.

    Shape (...,128,4), with no coupling between leading energy-group axes.
    The formula is evaluated as an increment to preserve weak Q/U.
    """
    a = np.asarray(stokes, float)
    if a.shape[-2:] != (128, 4):
        raise ValueError("original q128 Stokes shape")
    cone_diagnostics(a)
    n, J = tetrad_grid(q, H, time_s)
    w = physical_weights(q, n, J, degree)
    A = w / J
    total = np.sum(a[..., 0], axis=-1)
    physical = stokes_to_coherency(a * A[:, None], n)
    delta = coherency_to_stokes(collision_increment(physical, n, w, tau), n) / A[:, None]
    raw = np.sum(delta[..., 0], axis=-1)
    r = np.divide(raw, total, out=np.zeros_like(total), where=total > 0)
    if np.any(r <= -1):
        raise ValueError("inverse projection has nonpositive group total")
    change = (delta - r[..., None, None] * a) / (1 + r[..., None, None])
    result = a + change
    post = np.sum(result[..., 0], axis=-1)
    relative = np.divide(abs(post - total), total, out=np.zeros_like(total), where=total > 0)
    cone = cone_diagnostics(result)
    if np.max(relative) > 128 * np.finfo(float).eps:
        raise ValueError("elastic per-energy-group number conservation")
    return result, {
        "max_group_number_relative": float(np.max(relative)),
        "max_inverse_projection_raw_relative_drift": float(np.max(abs(r))),
        "max_effective_extra_extinction": float(np.max(abs(r))) / tau if tau > 0 else 0.0,
        "max_stokes_cone_violation_scaled": cone,
        "min_physical_weight": float(w.min()),
    }

def collision_stage(stokes, guard_n, guard_u, q, H, gas, t, dt, degree=4, sigma_scale=1.0):
    """Post-native Lie split, same actual endpoint electrons and proper dt.

    The below-10-eV guard retains the owner's two-moment description.  Its
    photon number and energy moments receive separately conserved collisions;
    no claim of an energy-resolved guard spectrum is made.
    """
    ne = electron_density(gas, H, t)
    tau = sigma_scale * C_CM_S * SIGMA_T_CM2 * ne * dt
    # Single batched call: physical-energy bins followed by the two guard moments.
    packed = np.concatenate((stokes, guard_n[None], guard_u[None]), axis=0)
    advanced, diagnostic = collide_native(packed, q, H, t, tau, degree)
    out, gn, gu = advanced[:-2], advanced[-2], advanced[-1]
    active = gn[:, 0] > 0
    if np.any(gu[active, 0] >= 10 * gn[active, 0]) or np.any(gu[~active, 0] != 0):
        raise ValueError("inherited below-10-eV guard domain")
    guard_joint_cone = cone_diagnostics(10 * gn - gu)
    diagnostic.update({"n_e_cm3": float(ne), "tau": float(tau), "dt_s": float(dt),
                       "time_s": float(t), "quadrature_degree": degree,
                       "guard_10N_minus_U_cone_violation_scaled": guard_joint_cone})
    return out, gn, gu, diagnostic
