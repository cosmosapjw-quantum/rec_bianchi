import numpy as np
from scipy.constants import c, h, physical_constants

from full_bianchi_hyrec.recoil.recoil_bridge import (
    exact_rayleigh_recoil_moments,
    load_v033_line_center,
    classify_v033_bridge,
    compute_line_bridge_audit,
)

M_H = physical_constants["atomic mass constant"][0] * 1.00782503223
NU_ALPHA = c / (1215.6701e-10)


def test_exact_rayleigh_recoil_mean_has_basko_limit():
    b_d = 2.3468181806822746e-5
    g = h * NU_ALPHA / (M_H * c**2 * b_d)
    moments = exact_rayleigh_recoil_moments(g, b_d, angular_order=256)

    assert abs(moments["mean_delta_x"] + g) / g < 2e-8
    assert abs(moments["second_delta_x"] / g**2 - 7/5) < 1e-7


def test_v033_is_not_the_microscopic_event_limit():
    v033 = load_v033_line_center()
    moments = exact_rayleigh_recoil_moments(
        v033["g"], v033["b_D"], angular_order=256
    )
    decision = classify_v033_bridge(v033, moments)

    assert decision["classification"] == "GATE_INVALID_FOR_EXACT_EVENT"
    assert decision["relative_mismatch"] > 0.5
    assert abs(
        v033["M1_per_scattering"]
        - (v033["b_D"] - v033["g"]) * v033["M2_per_scattering"]
    ) < 2e-11


def test_shift_only_hummer_line_audit_reproduces_baseline_but_fails_microreversibility():
    audit = compute_line_bridge_audit(
        back_order=12,
        middle_order=80,
        forward_order=20,
        u_order=48,
    )

    assert audit["no_recoil_line_column_vs_v032_relative"] < 2e-6
    assert audit["shift_only_pair_balance_relative"] > 1e-7
    assert audit["shift_only_vs_v033_drift_relative"] > 0.5
