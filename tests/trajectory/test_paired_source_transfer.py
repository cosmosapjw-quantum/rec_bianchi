from __future__ import annotations

from decimal import Decimal, localcontext
import hashlib
import json
import math
import random
import sys

import pytest

from full_bianchi_hyrec.trajectory.paired_source_transfer import (
    CLASSIFICATION,
    constant_positive_pair_transfer,
    constant_positive_pair_transfer_jvp,
)


def _decimal_transfer(
    *,
    f_initial: float,
    eta_s_inv: float,
    kappa_s_inv: float,
    duration_s: float,
) -> float:
    """High-precision oracle for the exact binary64 inputs."""

    with localcontext() as context:
        context.prec = 100
        f0 = Decimal.from_float(f_initial)
        eta = Decimal.from_float(eta_s_inv)
        # Match the primitive's binary64 subtraction before evaluating the law.
        chi = Decimal.from_float(kappa_s_inv - eta_s_inv)
        duration = Decimal.from_float(duration_s)
        if chi.is_zero():
            result = f0 + eta * duration
        else:
            attenuation = (-chi * duration).exp()
            result = attenuation * f0 + eta * (Decimal(1) - attenuation) / chi
        return float(result)


def _arguments() -> dict[str, float]:
    return {
        "f_initial": 0.37,
        "eta_s_inv": 0.41,
        "kappa_s_inv": 0.83,
        "duration_s": 0.29,
    }


def _conditioning_sweep_cases() -> list[tuple[str, dict[str, float]]]:
    """Return the byte-pinned five-stratum empirical oracle domain."""

    rng = random.Random(20260831)

    def log_uniform(lower: float, upper: float) -> float:
        return 10.0 ** rng.uniform(lower, upper)

    def common() -> float:
        return log_uniform(-12.0, 4.0)

    cases: list[tuple[str, dict[str, float]]] = []
    for _ in range(100):
        eta = common()
        cases.append(
            (
                "zero",
                {
                    "f_initial": common(),
                    "eta_s_inv": eta,
                    "kappa_s_inv": eta,
                    "duration_s": log_uniform(-12.0, 3.0),
                },
            )
        )
    for index in range(100):
        eta = common()
        sign = -1.0 if index % 2 else 1.0
        delta = sign * log_uniform(-16.0, -3.0)
        cases.append(
            (
                "near_equal",
                {
                    "f_initial": common(),
                    "eta_s_inv": eta,
                    "kappa_s_inv": eta * (1.0 + delta),
                    "duration_s": log_uniform(-12.0, 3.0),
                },
            )
        )
    for _ in range(100):
        duration = log_uniform(-8.0, 3.0)
        target_optical_depth = log_uniform(-12.0, math.log10(600.0))
        eta = common()
        cases.append(
            (
                "positive_x",
                {
                    "f_initial": common(),
                    "eta_s_inv": eta,
                    "kappa_s_inv": eta + target_optical_depth / duration,
                    "duration_s": duration,
                },
            )
        )
    for _ in range(100):
        duration = log_uniform(-8.0, 3.0)
        target_optical_depth = log_uniform(-12.0, math.log10(600.0))
        kappa = common()
        cases.append(
            (
                "negative_x",
                {
                    "f_initial": common(),
                    "eta_s_inv": kappa + target_optical_depth / duration,
                    "kappa_s_inv": kappa,
                    "duration_s": duration,
                },
            )
        )
    for _ in range(100):
        cases.append(
            (
                "independent",
                {
                    "f_initial": log_uniform(-8.0, 2.0),
                    "eta_s_inv": log_uniform(-8.0, 2.0),
                    "kappa_s_inv": log_uniform(-8.0, 2.0),
                    "duration_s": log_uniform(-8.0, 0.7),
                },
            )
        )
    return cases


def _decimal_transfer_120_and_optical_depth(
    arguments: dict[str, float],
) -> tuple[float, float]:
    """Evaluate the exact binary64 inputs at Decimal precision 120."""

    with localcontext() as context:
        context.prec = 120
        f0 = Decimal.from_float(arguments["f_initial"])
        eta = Decimal.from_float(arguments["eta_s_inv"])
        # The implementation owns this binary64 subtraction, so the oracle
        # starts from exactly the same rounded chi before doing exact algebra.
        chi = Decimal.from_float(
            arguments["kappa_s_inv"] - arguments["eta_s_inv"]
        )
        duration = Decimal.from_float(arguments["duration_s"])
        optical_depth = chi * duration
        if chi.is_zero():
            result = f0 + eta * duration
        else:
            attenuation = (-optical_depth).exp()
            result = (
                attenuation * f0
                + eta * (Decimal(1) - attenuation) / chi
            )
        return float(result), float(optical_depth)


def test_primitive_is_explicitly_nonauthoritative_and_not_production_admission() -> None:
    assert CLASSIFICATION == "NONAUTHORITATIVE_FORMULA_PRIMITIVE"


@pytest.mark.parametrize(
    ("eta", "kappa", "duration"),
    [
        (0.4, 0.9, 0.7),
        (0.75, 0.75, 1.25),
        (0.9, 0.2, 0.6),
        (1.0, math.nextafter(1.0, math.inf), 2.0),
        (1.0, math.nextafter(1.0, -math.inf), 2.0),
    ],
)
def test_exact_transfer_matches_high_precision_oracle_across_net_opacity_signs(
    eta: float,
    kappa: float,
    duration: float,
) -> None:
    arguments = {
        "f_initial": 0.31,
        "eta_s_inv": eta,
        "kappa_s_inv": kappa,
        "duration_s": duration,
    }
    actual = constant_positive_pair_transfer(**arguments)
    expected = _decimal_transfer(**arguments)
    assert math.isclose(actual, expected, rel_tol=3.0e-15, abs_tol=2.0e-16)
    assert actual >= 0.0


def test_conditioning_aware_decimal_sweep_has_pinned_empirical_domain() -> None:
    """Check a bounded empirical domain without claiming cross-libm identity.

    The exponential branch has relative condition proportional to
    ``abs(chi*duration)`` for large negative optical depth.  Consequently this
    regression uses a conditioning-aware binary64 envelope.  Factor eight is
    an empirical test allowance on this declared, hash-pinned 500-case domain;
    it is neither a production tolerance nor a proof about other libm builds.
    """

    cases = _conditioning_sweep_cases()
    assert len(cases) == 500
    assert {name: sum(row_name == name for row_name, _ in cases) for name in {
        "zero",
        "near_equal",
        "positive_x",
        "negative_x",
        "independent",
    }} == {
        "zero": 100,
        "near_equal": 100,
        "positive_x": 100,
        "negative_x": 100,
        "independent": 100,
    }
    canonical_cases = json.dumps(
        cases,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")
    assert hashlib.sha256(canonical_cases).hexdigest() == (
        "887dd1611afd8374c35b4c8c159c4a6f1357aff8374ef9bb97fd649894dbd49d"
    )

    epsilon = sys.float_info.epsilon
    optical_depths: list[float] = []
    scaled_relative_errors: list[float] = []
    for _, arguments in cases:
        actual = constant_positive_pair_transfer(**arguments)
        expected, optical_depth = _decimal_transfer_120_and_optical_depth(
            arguments
        )
        assert expected > 0.0
        relative_error = abs(actual - expected) / abs(expected)
        scale = epsilon * max(1.0, abs(optical_depth))
        assert relative_error <= 8.0 * scale
        optical_depths.append(optical_depth)
        scaled_relative_errors.append(relative_error / scale)

    # These counts pin the intended conditioning coverage without pinning a
    # particular platform's libm rounding at the worst individual case.
    assert [
        sum(abs(value) <= limit for value in optical_depths)
        for limit in (1.0, 10.0, 100.0, 600.0)
    ] == [445, 461, 480, 500]
    assert min(optical_depths) < -300.0
    assert max(scaled_relative_errors) <= 8.0


def test_zero_net_opacity_uses_exact_linear_limit() -> None:
    assert constant_positive_pair_transfer(
        f_initial=0.25,
        eta_s_inv=0.75,
        kappa_s_inv=0.75,
        duration_s=2.0,
    ) == 1.75


def test_negative_net_opacity_is_positive_and_is_not_clipped() -> None:
    result = constant_positive_pair_transfer(
        f_initial=2.0,
        eta_s_inv=4.0,
        kappa_s_inv=1.0,
        duration_s=0.5,
    )
    expected = _decimal_transfer(
        f_initial=2.0,
        eta_s_inv=4.0,
        kappa_s_inv=1.0,
        duration_s=0.5,
    )
    assert result > 2.0
    assert result == pytest.approx(expected, rel=3.0e-15)


@pytest.mark.parametrize(
    "arguments,direction,step",
    [
        (
            _arguments(),
            {
                "d_f_initial": -0.21,
                "d_eta_s_inv": 0.33,
                "d_kappa_s_inv": -0.17,
                "d_duration_s": 0.09,
            },
            2.0e-7,
        ),
        (
            {
                "f_initial": 0.37,
                "eta_s_inv": 0.4,
                "kappa_s_inv": 0.4000001,
                "duration_s": 0.7,
            },
            {
                "d_f_initial": 0.13,
                "d_eta_s_inv": -0.19,
                "d_kappa_s_inv": 0.23,
                "d_duration_s": -0.11,
            },
            1.0e-7,
        ),
        (
            {
                "f_initial": 0.7,
                "eta_s_inv": 0.8,
                "kappa_s_inv": 0.2,
                "duration_s": 0.4,
            },
            {
                "d_f_initial": -0.2,
                "d_eta_s_inv": 0.1,
                "d_kappa_s_inv": 0.3,
                "d_duration_s": 0.15,
            },
            2.0e-7,
        ),
    ],
)
def test_fixed_branch_jvp_matches_centered_directional_difference(
    arguments: dict[str, float],
    direction: dict[str, float],
    step: float,
) -> None:
    analytic = constant_positive_pair_transfer_jvp(**arguments, **direction)
    primal_names = ("f_initial", "eta_s_inv", "kappa_s_inv", "duration_s")
    tangent_names = (
        "d_f_initial",
        "d_eta_s_inv",
        "d_kappa_s_inv",
        "d_duration_s",
    )
    plus = {
        name: arguments[name] + step * direction[tangent]
        for name, tangent in zip(primal_names, tangent_names, strict=True)
    }
    minus = {
        name: arguments[name] - step * direction[tangent]
        for name, tangent in zip(primal_names, tangent_names, strict=True)
    }
    difference = (
        constant_positive_pair_transfer(**plus)
        - constant_positive_pair_transfer(**minus)
    ) / (2.0 * step)
    assert analytic == pytest.approx(difference, rel=2.0e-8, abs=2.0e-10)


def test_zero_net_opacity_jvp_has_stable_closed_form() -> None:
    arguments = {
        "f_initial": 0.25,
        "eta_s_inv": 0.75,
        "kappa_s_inv": 0.75,
        "duration_s": 2.0,
    }
    direction = {
        "d_f_initial": 0.3,
        "d_eta_s_inv": -0.2,
        "d_kappa_s_inv": 0.4,
        "d_duration_s": 0.1,
    }
    d_chi = direction["d_kappa_s_inv"] - direction["d_eta_s_inv"]
    f_chi = (
        -arguments["duration_s"] * arguments["f_initial"]
        - 0.5
        * arguments["eta_s_inv"]
        * arguments["duration_s"] ** 2
    )
    expected = math.fsum(
        (
            direction["d_f_initial"],
            arguments["duration_s"] * direction["d_eta_s_inv"],
            f_chi * d_chi,
            arguments["eta_s_inv"] * direction["d_duration_s"],
        )
    )
    assert constant_positive_pair_transfer_jvp(
        **arguments, **direction
    ) == pytest.approx(expected, rel=0.0, abs=2.0e-16)


@pytest.mark.parametrize(
    "update",
    [
        {"f_initial": -1.0},
        {"eta_s_inv": -1.0},
        {"kappa_s_inv": -1.0},
        {"duration_s": -1.0},
        {"eta_s_inv": float("nan")},
        {"kappa_s_inv": float("inf")},
        {"duration_s": True},
    ],
)
def test_primal_rejects_invalid_inputs(update: dict[str, float]) -> None:
    arguments = _arguments()
    arguments.update(update)
    with pytest.raises(ValueError):
        constant_positive_pair_transfer(**arguments)


def test_overflow_is_rejected_instead_of_clipped_or_returned() -> None:
    with pytest.raises(FloatingPointError, match="overflow|finite"):
        constant_positive_pair_transfer(
            f_initial=1.0,
            eta_s_inv=1.0e308,
            kappa_s_inv=0.0,
            duration_s=10.0,
        )
    with pytest.raises(FloatingPointError, match="overflow|finite"):
        constant_positive_pair_transfer(
            f_initial=0.0,
            eta_s_inv=1.0e308,
            kappa_s_inv=1.0e308,
            duration_s=10.0,
        )


def test_jvp_rejects_nonfinite_tangent_and_tangent_overflow() -> None:
    with pytest.raises(ValueError, match="tangent"):
        constant_positive_pair_transfer_jvp(
            **_arguments(), d_eta_s_inv=float("nan")
        )
    with pytest.raises(FloatingPointError, match="tangent|finite"):
        constant_positive_pair_transfer_jvp(
            **_arguments(), d_eta_s_inv=-1.0e308, d_kappa_s_inv=1.0e308
        )
