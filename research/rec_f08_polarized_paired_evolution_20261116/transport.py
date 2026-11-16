"""Polarized counterpart of the immutable original F08 native endpoint.

Counts are per H nucleus in the original equal-q cells, not physical-angle
quadrature masses.  This module preserves the original source Jacobian and
fixed physical-energy hat remap.  It adds parallel transport of Q/U and
applies the actual native H/He absorption factors equally to I,Q,U,V.

For constant diagonal H, n=q exp(-Ht)/g and the spherical-screen connection
has Omega=integral cos(theta) d(phi).  Hence (Q+iU)_1=exp(-2iOmega)(Q+iU)_0.
The connection is integrated by four-point Gauss-Legendre quadrature on
each endpoint interval.  Its integration error is not an interval bound.
"""
from __future__ import annotations

import math
import numpy as np

SOURCE_RATE_PER_H_S = 5e-15
BIRTH_ENERGY_EV = 13.7
F_HE = .083
INITIAL_NH_CM3 = 1e-4
_GL_NODES, _GL_WEIGHTS = np.polynomial.legendre.leggauss(4)


def physical_directions(q, h, t):
    """Return instantaneous directions, energy ratio g, and dOmega_n/dOmega_q."""
    q, h, t = np.asarray(q, float), np.asarray(h, float), float(t)
    if q.shape != (128, 3) or h.shape != (3,) or not np.isfinite(q).all() or not np.isfinite(h).all():
        raise ValueError("original finite q128 and three diagonal H rates required")
    if np.max(abs(np.sum(q*q, axis=1)-1)) > 8e-15:
        raise ValueError("original q labels must be unit vectors")
    if not math.isfinite(t) or t < 0 or np.min(h) < 0:
        raise ValueError("original expanding-background time/rate domain")
    a = np.exp(-h*t)
    g = np.sqrt(np.sum((q*a)**2, axis=1))
    if not np.isfinite(g).all() or np.min(g) <= 0 or np.prod(a) <= 0:
        raise ValueError("singular or underflowed tetrad map")
    return q*a/g[:, None], g, np.prod(a)/g**3


def native_g_point(q, h, t):
    """Mirror paired_runtime::g_point's *binary64 expression order*.

    The mathematically equal norm(q*exp(-Ht)) is not numerically identical
    to sqrt(sum q_i*q_i*exp((-2*H_i)*t)).  A one-ulp difference is amplified
    by the original very narrow near-HI energy hats.  Python ``sum`` on
    3.12 and numpy reductions are deliberately avoided for this source map.
    Screen directions continue to use their geometric normalization above.
    """
    physical_directions(q,h,t)  # validate the original geometry contract
    h = tuple(float(x) for x in h)
    t = float(t)
    result = []
    for ray in q:
        total = 0.0
        for i in range(3):
            qi = float(ray[i])
            total += (qi*qi)*math.exp((-2.0*h[i])*t)
        result.append(math.sqrt(total))
    return np.asarray(result)


def native_source_j(q, h, t, *, g=None):
    """Original scalar source Jacobian, before sequential normalization."""
    h = tuple(float(x) for x in h)
    t = float(t)
    if g is None:
        g = native_g_point(q,h,t)
    g = np.asarray(g,float)
    if g.shape != (128,) or not np.isfinite(g).all() or np.min(g)<=0:
        raise ValueError('original native g domain')
    volume = math.exp(-((h[0]+h[1])+h[2])*t)
    return np.asarray([volume/((float(x)*float(x))*float(x)) for x in g])


def _native_source_weights(jacobian):
    total = 0.0
    for x in jacobian:
        total += float(x)
    if not math.isfinite(total) or total<=0:
        raise ValueError('PAIRED_SOURCE_RANGE')
    return np.asarray([float(x)/total for x in jacobian])


def screen_rotation_angle(q, h, t0, t1):
    """Connection integral Omega; exactly zero for an axisymmetric x-y plane."""
    h = np.asarray(h, float)
    _, _, _ = physical_directions(q, h, t0)
    if not math.isfinite(t1) or t1 < t0:
        raise ValueError("screen transport requires a forward finite time interval")
    if h[0] == h[1] or t1 == t0:
        return np.zeros(len(q))
    midpoint, half = (t0+t1)/2, (t1-t0)/2
    omega = np.zeros(len(q))
    for x, w in zip(_GL_NODES, _GL_WEIGHTS):
        n, _, _ = physical_directions(q, h, midpoint + half*x)
        denominator = n[:, 0]**2 + n[:, 1]**2
        connection = np.divide(
            n[:, 2]*(h[0]-h[1])*n[:, 0]*n[:, 1], denominator,
            out=np.zeros(len(q)), where=denominator > 0)
        omega += half*w*connection
    return omega


def rotate_stokes(stokes, omega):
    """Rotate all screen Q/U components, preserving I, V, and polarization norm."""
    s = np.asarray(stokes, float)
    omega = np.asarray(omega, float)
    if s.shape[-2:] != (len(omega), 4) or not np.isfinite(s).all() or not np.isfinite(omega).all():
        raise ValueError("finite Stokes (..., nray, 4) and per-ray connection required")
    out = s.copy()
    co, si = np.cos(2*omega), np.sin(2*omega)
    out[..., 1] = co*s[..., 1] + si*s[..., 2]
    out[..., 2] = co*s[..., 2] - si*s[..., 1]
    return out


def _totals(stokes, guard_n, guard_u, nodes):
    # Match the original direction-major compensated native reductions in
    # physical meaning.  Native byte identity is not assumed for Python fsum.
    n = math.fsum(stokes[..., 0].ravel()) + math.fsum(guard_n[:, 0])
    u = math.fsum((stokes[..., 0]*nodes[:, None]).ravel()) + math.fsum(guard_u[:, 0])
    return n, u


def _cone_violation(*arrays):
    return max(float(np.max(np.linalg.norm(a[..., 1:], axis=-1)-a[..., 0])) for a in arrays)


def _validate_state(stokes, guard_n, guard_u, nodes):
    s, gn, gu, en = (np.asarray(a, float) for a in (stokes, guard_n, guard_u, nodes))
    if en.shape != (17,) or not np.isfinite(en).all() or not np.all(np.diff(en)>0):
        raise ValueError("original 17 strictly ordered physical energy nodes required")
    if en[0] != 10 or en[-1] != 20 or en[12] != BIRTH_ENERGY_EV:
        raise ValueError("original F08 energy boundaries/birth-node identity")
    if s.shape != (17,128,4) or gn.shape != (128,4) or gu.shape != (128,4):
        raise ValueError("source spectral/guard Stokes shape")
    if not all(np.isfinite(a).all() for a in (s,gn,gu)):
        raise ValueError("finite source Stokes state required")
    if min(float(np.min(a[...,0])) for a in (s,gn,gu)) < 0:
        raise ValueError("negative photon or energy intensity")
    scale = max(float(np.max(a[...,0])) for a in (s,gn,gu))
    if _cone_violation(s,gn,gu) > 3e-14*max(scale, np.finfo(float).tiny):
        raise ValueError("incoming Stokes state outside physical cone")
    if np.any((gn[:,0]==0) & (gu[:,0]!=0)) or np.any(gu[:,0] >= 10*gn[:,0], where=gn[:,0]>0):
        raise ValueError("lower-guard photon/energy domain")
    return s, gn, gu, en


def advance_native_endpoint(stokes, guard_n, guard_u, q, H, nodes, audit):
    """Advance one actual paired_runtime endpoint from its native audit.

    Return (stokes, guard_n, guard_u, diagnostics).  ``audit`` is the native
    site_audit object for an accepted endpoint, with endpoint time_s and dt_s,
    source_n/u, group_indices, and point_factors.  Each caller must use the
    two accepted half-endpoint audits rather than the rejected full-step
    comparison audit when it advances the native paired_trial state.

    The original F08 source rate, energy, clock, helium fraction, nH, and Hmean
    are checked here.  No opacity or H/He state is obtained from another source.
    """
    s, gn, gu, nodes = _validate_state(stokes, guard_n, guard_u, nodes)
    H = np.asarray(H,float)
    t1, dt = float(audit['time_s']), float(audit['dt_s'])
    t0 = t1-dt
    if not math.isfinite(dt) or dt <= 0 or not math.isfinite(t1) or t0 < 0:
        raise ValueError("original endpoint proper-time domain")
    # Match native scalar arithmetic for the ill-conditioned spectral hats;
    # the independently normalized geometric n is used only for spin rotation.
    g0 = native_g_point(q,H,t0)
    g1 = native_g_point(q,H,t1)
    jac1 = native_source_j(q,H,t1,g=g1)
    hsum = (float(H[0])+float(H[1]))+float(H[2])
    expected = {
        'source_n': dt*SOURCE_RATE_PER_H_S,
        'source_u': dt*SOURCE_RATE_PER_H_S*BIRTH_ENERGY_EV,
        'n_h_cm3': INITIAL_NH_CM3*math.exp(-hsum*t1),
        'f_he': F_HE,
        'h_mean_per_s': hsum/3,
    }
    for name, value in expected.items():
        actual = float(audit[name])
        if not math.isfinite(actual) or not math.isclose(actual, value, rel_tol=2e-13, abs_tol=0):
            raise ValueError('original F08 audit/source mismatch: '+name)
    ratio = g1/g0
    omega = screen_rotation_angle(q,H,t0,t1)
    rotated = rotate_stokes(s,omega)
    out = np.zeros_like(s)
    gn_out = rotate_stokes(gn,omega)
    gu_out = rotate_stokes(gu,omega)*ratio[:,None]
    n_before,u_before = _totals(s,gn,gu,nodes)
    exact_red_u = math.fsum((s[...,0]*nodes[:,None]*ratio[None,:]).ravel()) + math.fsum(gu[:,0]*ratio)
    # The scalar owner tests every energy-node hat.  Only the two bracketing
    # hats are nonzero, so this is the same linear positive point map.
    for d in range(128):
        for j, energy in enumerate(nodes):
            if not np.any(rotated[j,d]):
                continue
            e = energy*ratio[d]
            value = rotated[j,d]
            if e > nodes[-1]:
                raise ValueError('PAIRED_UPPER_GUARD_UNIMPLEMENTED')
            if e < nodes[0]:
                gn_out[d] += value
                gu_out[d] += e*value
                continue
            k = int(np.searchsorted(nodes,e,side='right')-1)
            if k == len(nodes)-1:
                out[k,d] += value
            else:
                # Evaluate both original hats independently, matching their
                # definitions instead of constructing the second by subtraction.
                left = (nodes[k+1]-e)/(nodes[k+1]-nodes[k])
                right = (e-nodes[k])/(nodes[k+1]-nodes[k])
                out[k,d] += left*value
                out[k+1,d] += right*value
    n_transport,u_transport = _totals(out,gn_out,gu_out,nodes)
    source_n,source_u = float(audit['source_n']),float(audit['source_u'])
    source_weights = _native_source_weights(jac1)
    out[12,:,0] += source_n*source_weights
    n_source,u_source = _totals(out,gn_out,gu_out,nodes)
    indices = np.asarray(audit['group_indices'])
    factors = np.asarray(audit['point_factors'],float)
    if indices.ndim != 1 or factors.shape != indices.shape or not np.issubdtype(indices.dtype,np.integer):
        raise ValueError('native absorption-factor indexing')
    if len(set(indices.tolist())) != len(indices) or np.any(indices<0) or np.any(indices>=len(nodes)):
        raise ValueError('native absorption-factor index range/duplicates')
    if not np.isfinite(factors).all() or np.any(factors<0) or np.any(factors>1+8e-15):
        raise ValueError('native absorption probability domain')
    missing = set(np.flatnonzero(out[...,0].sum(axis=1)>0)) - set(indices.tolist())
    if missing:
        raise ValueError('populated spectral groups absent from native audit')
    pre_abs_n = out[...,0].sum(axis=1)
    absorbed_n = math.fsum(pre_abs_n[indices]*(1-factors))
    absorbed_u = math.fsum(pre_abs_n[indices]*(1-factors)*nodes[indices])
    out[indices] *= factors[:,None,None]
    n_after,u_after = _totals(out,gn_out,gu_out,nodes)
    diagnostics = {
        't0_s':t0,'t1_s':t1,'dt_s':dt,
        'max_screen_connection_rad':float(np.max(abs(omega))),
        'N_before_per_H':n_before,'N_transport_per_H':n_transport,
        'N_source_added_per_H':source_n,'N_after_per_H':n_after,
        'N_absorbed_per_H':absorbed_n,
        'U_before_eV_per_H':u_before,'U_transport_eV_per_H':u_transport,
        'U_source_added_eV_per_H':source_u,'U_after_eV_per_H':u_after,
        'U_absorbed_eV_per_H':absorbed_u,
        'redshift_work_eV_per_H':u_before-u_transport,
        'remap_number_residual_per_H':n_transport-n_before,
        'remap_energy_residual_eV_per_H':u_transport-exact_red_u,
        'source_number_residual_per_H':n_source-n_transport-source_n,
        'source_energy_residual_eV_per_H':u_source-u_transport-source_u,
        'number_ledger_residual_per_H':n_after+absorbed_n-n_before-source_n,
        'energy_ledger_residual_eV_per_H':u_after+absorbed_u-u_transport-source_u,
        'max_stokes_cone_violation':_cone_violation(out,gn_out,gu_out),
        'source_measure':'ORIGINAL_EQUAL_Q_CELL_J_NORMALIZED',
        'native_point_arithmetic':'SOURCE_SCALAR_BINARY64_ORDER_G_AND_J',
        'screen_transport':'TRIAXIAL_DIAGONAL_GL4_CONNECTION',
    }
    return out,gn_out,gu_out,diagnostics
