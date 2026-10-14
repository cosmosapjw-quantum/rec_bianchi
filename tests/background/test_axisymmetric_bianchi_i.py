"""C5/C6: executable, source-specific LRS Bianchi I geometry tests."""
from __future__ import annotations

import math

import mpmath as mp
import numpy as np
import pytest

from full_bianchi_hyrec.background import (
    AxisymmetricBianchiIBackground,
    BianchiIModelParameters,
    axisymmetric_photon_map,
    normal_frame_characteristic,
)


def _reference_dt_db(model, a1, a2):
    mp.mp.dps = 65
    hi = mp.mpf(model.cosmology.h0_per_s)
    om = mp.mpf(model.cosmology.omega_m)
    orad = mp.mpf(model.cosmology.omega_r)
    ol = mp.mpf(model.cosmology.omega_lambda)
    ar = mp.mpf(model.a_ref)
    q = mp.mpf(model.q_ref)
    Href = hi * mp.sqrt(om / ar**3 + orad / ar**4 + ol)
    a_left, a_right = mp.mpf(a1), mp.mpf(a2)
    d = mp.log(a_right / a_left)

    def terms(x):
        a = a_left * mp.exp(x)
        hf = hi * mp.sqrt(om / a**3 + orad / a**4 + ol)
        s = q * Href * (ar / a)**3
        H = hf if model.same_h else mp.sqrt(hf**2 + s**2)
        return 1 / H, s / H

    dt = mp.quad(lambda x: terms(x)[0], [0, d])
    db = mp.quad(lambda x: terms(x)[1], [0, d])
    return float(dt), float(db)


@pytest.mark.parametrize("q", [0.0, 0.005, -0.005, 0.01, -0.01])
def test_actual_early_accepted_interval_matches_independent_quadrature(q):
    model = AxisymmetricBianchiIBackground(q_ref=q)
    a1, a2 = 0.04761905043465769, 0.04761905047098814
    result = model.interval(a1, a2)
    dt, db = _reference_dt_db(model, a1, a2)
    assert result.delta_t_s > 0
    assert abs(result.delta_t_s / dt - 1) < 1e-9
    if q == 0:
        assert result.delta_b == 0
    else:
        assert abs((result.delta_b - db) / db) < 1e-9
        assert math.copysign(1.0, result.delta_b) == math.copysign(1.0, q)


def test_real_preserved_plus_case_improves_native_cumulative_subtraction():
    model = AxisymmetricBianchiIBackground(q_ref=0.01)
    result = model.interval(0.04761905043465769, 0.04761905047098814)
    reference = 6446090.47917345198980877374506304136
    old_saved = 6446090.361918509
    assert abs(result.delta_t_s / reference - 1.0) < 1e-9
    assert abs(old_saved / reference - 1.0) > 1e-8


@pytest.mark.parametrize("q", [0.0, 0.005, 0.01])
def test_shear_sign_is_odd_and_background_clock_even(q):
    p = AxisymmetricBianchiIBackground(q_ref=q)
    m = AxisymmetricBianchiIBackground(q_ref=-q)
    a1, a2 = 0.0601, 0.0611
    i, j = p.interval(a1, a2), m.interval(a1, a2)
    assert i.delta_t_s == j.delta_t_s
    assert i.delta_b == -j.delta_b or q == 0
    assert p.point(a2).H_s_inv == m.point(a2).H_s_inv


@pytest.mark.parametrize("same_h", [False, True])
def test_piecewise_composition_and_origin_value(same_h):
    model = AxisymmetricBianchiIBackground(q_ref=0.01, same_h=same_h)
    a0, a1, a2 = model.a_ref, 0.0851, model.a_end
    p, q = model.interval(a0, a1), model.interval(a1, a2)
    r = model.interval(a0, a2)
    assert abs(math.fsum([p.delta_t_s, q.delta_t_s]) / r.delta_t_s - 1) < 2e-12
    assert abs(math.fsum([p.delta_b, q.delta_b]) / r.delta_b - 1) < 2e-12
    start = model.point(a0)
    assert start.t_s == 0
    assert start.b == 0


def test_sequence_exposes_actual_snapshots_and_characteristics():
    model = AxisymmetricBianchiIBackground(q_ref=0.01)
    eta = np.log(np.array([model.a_ref, 0.0501, 0.06, 0.08, 0.1]) / model.a_ref)
    seq = model.snapshots(eta)
    assert seq.bianchi_type == "I"
    assert seq.model_name == "Bianchi_I_axisymmetric_prescribed_clock"
    assert len(seq.source_sha256) == 64
    for a, tau in zip([model.a_ref, 0.0501, 0.06, 0.08, 0.1], eta):
        s = seq.snapshot_at_tau(tau)
        pt = model.point(a)
        np.testing.assert_allclose(s.sigma_s_inv, np.diag([-pt.s_s_inv, -pt.s_s_inv, 2 * pt.s_s_inv]), rtol=2e-13, atol=0.0)
        assert s.H_s_inv == pt.H_s_inv
        assert s.cosmic_time_s == pt.t_s
        assert s.bianchi_type == "I"
        assert s.branch_flags["prescribed_non_tilted_bianchi_i"]
        assert not np.any(s.beta_H)
        characteristic = normal_frame_characteristic(s, np.array([0.0, 0.0, 1.0]))
        assert abs(characteristic.R_normal_s_inv + s.H_s_inv + 2 * pt.s_s_inv) <= 1e-14 * s.H_s_inv


def test_finite_photon_map_identity_mirror_and_jacobian():
    p = AxisymmetricBianchiIBackground(q_ref=0.005)
    inc = p.interval(0.0501, 0.061)
    for mu in [-1.0, -0.57, 0.0, 0.3, 1.0]:
        result = axisymmetric_photon_map(mu, inc)
        assert result["energy_ratio"] > 0
        assert abs(result["mu_final"]) <= 1.0
        assert result["solid_angle_jacobian"] > 0
        mu_prime = result["mu_final"]
        eps = 1e-6
        mu_up = axisymmetric_photon_map(min(1.0, mu + eps), inc)["mu_final"]
        mu_dn = axisymmetric_photon_map(max(-1.0, mu - eps), inc)["mu_final"]
        if abs(mu) < 1:
            assert abs((mu_up - mu_dn)/(2*eps)/result["solid_angle_jacobian"]-1) < 2e-9


def test_model_identity_changes_and_inputs_fail_closed():
    baseline = AxisymmetricBianchiIBackground(0.01)
    negative = AxisymmetricBianchiIBackground(-0.01)
    same_h = AxisymmetricBianchiIBackground(0.01, same_h=True)
    assert len({baseline.source_sha256, negative.source_sha256, same_h.source_sha256}) == 3
    for args in [
        (baseline.a_ref - 1e-3, 0.06),
        (0.07, 0.06),
        (0.06, baseline.a_end + 0.1),
        (float("nan"), 0.06),
    ]:
        with pytest.raises(ValueError):
            baseline.interval(*args)
    with pytest.raises(ValueError):
        AxisymmetricBianchiIBackground(float("nan"))
    with pytest.raises(ValueError):
        BianchiIModelParameters(1.0, -0.1, 0.1, 1.0)


def test_one_ulp_interval_near_origin():
    model = AxisymmetricBianchiIBackground(q_ref=0.0)
    a1 = model.a_ref
    a2 = math.nextafter(a1, math.inf)
    r = model.interval(a1, a2)
    assert r.delta_l > 0
    assert r.delta_t_s > 0
    assert r.delta_b == 0
