"""Negative controls for the immutable H2 U5 offline audit."""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "src"))
from verify_r3i_h2_u5_saved_result import (
    validate_record_order, causal_link_indices, thermal_latch_condition,
    remaining_budget, EVENT_IZ, START_IZ)
from r3i_u5_average_forensic import numerical_gates, phi80


def _owner(raw, *, b=8, tau=1.4358657226114e-6):
    return {"bin": b, "raw": raw, "tau": tau, "A80": "1.8832233175448e-14",
            "phi64": float(phi80(tau)), "phi80": str(phi80(tau)),
            "phi_bound": 1.e-10, "raw_reconstruction_absolute": 0.,
            "source_reconstruction_absolute": 0., "Q": 5.94e-9,
            "incoming": 1.45e-14}


def test_original_failure_is_not_promoted_by_roundoff_gate():
    p = _owner(1.8832003375371853e-14)
    c = _owner(1.8832463107232585e-14)
    gate = numerical_gates(p, c, 0.)
    assert gate["original_gate"]["status"] == "FAIL"
    assert gate["decimal80_ieee_gate"]["status"] == "PASS"


def test_large_raw_perturbation_fails_roundoff_gate():
    gate = numerical_gates(_owner(1.e-8), _owner(1.8832463107232585e-14), 0.)
    assert gate["original_gate"]["status"] == "FAIL"
    assert gate["decimal80_ieee_gate"]["status"] == "FAIL"


@pytest.mark.parametrize("b,tau", [(150, 1.4e-6), (8, 1.e-3)])
def test_diffusion_or_outside_tau_domain_is_hold(b, tau):
    gate = numerical_gates(_owner(1.e-14, b=b, tau=tau),
                           _owner(2.e-14, b=b, tau=tau), 0.)
    assert gate["decimal80_ieee_gate"]["status"] == "HOLD_OUTSIDE_DIAGNOSTIC_DOMAIN"


def test_duplicate_or_missing_spectral_record_fails():
    phase, i, col, b = validate_record_order("STEP", ["STEP", "0"],
                                             phase="STEP", i=0, col=2006, bin_index=0)
    assert phase == "SPECTRUM"
    phase, i, col, b = validate_record_order("V", ["V", "0", "0", "1e-9"],
                                             phase=phase, i=i, col=col, bin_index=b)
    with pytest.raises(ArithmeticError, match="C_SPECTRAL_ORDER"):
        validate_record_order("V", ["V", "0", "0", "1e-9"],
                              phase=phase, i=i, col=col, bin_index=b)
    with pytest.raises(ArithmeticError, match="C_SPECTRAL_ORDER"):
        validate_record_order("V", ["V", "0", "2", "1e-9"],
                              phase=phase, i=i, col=col, bin_index=b)


def test_missing_step_record_fails():
    with pytest.raises(ArithmeticError, match="C_STEP_ORDER"):
        validate_record_order("STEP", ["STEP", "1"], phase="STEP", i=0,
                              col=2006, bin_index=0)


def test_thermal_switch_is_one_time_latch():
    event = EVENT_IZ - START_IZ
    assert thermal_latch_condition(event-1, 0.0004997842898611937, False)
    assert not thermal_latch_condition(event-1, 0.0004997842898611937, True)
    assert not thermal_latch_condition(event-1, 0.0005000545426558922, False)
    assert thermal_latch_condition(event, 0.0005000545426558922, True)
    assert not thermal_latch_condition(event, 0.0004999870062093459, True)
    # The saved second input legitimately drops below the trigger.
    assert thermal_latch_condition(event+1, 0.0004999870062093459, True)
    assert not thermal_latch_condition(event+1, 0.0004999870062093459, False)
    assert not thermal_latch_condition(event+1, float("nan"), True)


def test_missing_thermal_event_record_fails_at_event_step():
    event = EVENT_IZ - START_IZ
    with pytest.raises(ArithmeticError, match="C_THERMAL_EVENT_MISSING"):
        validate_record_order("STEP", ["STEP", str(event)], phase="STEP", i=event,
                              col=2006, bin_index=0)


def test_cumulative_cap_debits_prior_cost_and_is_bounded():
    assert remaining_budget(120.315836, 179.17210247197) == (290, 480)
    with pytest.raises(ArithmeticError, match="AUDIT_CUMULATIVE_BUDGET_EXHAUSTED"):
        remaining_budget(451., 0.)
