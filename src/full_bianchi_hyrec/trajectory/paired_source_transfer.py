"""Research-only exact transfer for one constant positive coefficient pair.

This module records the algebraic primitive

``df/dt = eta * (1 + f) - kappa * f = eta - (kappa - eta) * f``

on a fixed branch with constant nonnegative ``eta`` and ``kappa``.  It is a
formula check, not directional-source authority, a deposition law, or a
production/admission path.  In particular, this module is deliberately not
re-exported by :mod:`full_bianchi_hyrec.trajectory`.

No result is clipped.  Invalid inputs, overflow, and nonfinite results are
rejected fail-closed.
"""
from __future__ import annotations

import math


CLASSIFICATION = "NONAUTHORITATIVE_FORMULA_PRIMITIVE"

# Below this threshold the direct quotient defining phi and its derivative is
# cancellation-sensitive.  Terms through x**8 leave a sub-binary64 remainder
# throughout this interval.
_SERIES_THRESHOLD = 1.0e-2


def _finite_scalar(value: float, *, name: str) -> float:
    if isinstance(value, bool):
        raise ValueError(f"{name} must be a finite real scalar, not bool")
    try:
        result = float(value)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError(f"{name} must be a finite real scalar") from exc
    if not math.isfinite(result):
        raise ValueError(f"{name} must be finite")
    return result


def _validated_primal_inputs(
    f_initial: float,
    eta_s_inv: float,
    kappa_s_inv: float,
    duration_s: float,
) -> tuple[float, float, float, float]:
    f0 = _finite_scalar(f_initial, name="f_initial")
    eta = _finite_scalar(eta_s_inv, name="eta_s_inv")
    kappa = _finite_scalar(kappa_s_inv, name="kappa_s_inv")
    duration = _finite_scalar(duration_s, name="duration_s")
    if min(f0, eta, kappa, duration) < 0.0:
        raise ValueError(
            "f_initial, eta_s_inv, kappa_s_inv, and duration_s "
            "must be nonnegative"
        )
    return f0, eta, kappa, duration


def _finite_sum(terms: tuple[float, ...], *, label: str) -> float:
    if not all(math.isfinite(term) for term in terms):
        raise FloatingPointError(f"{label} overflowed or became nonfinite")
    try:
        result = math.fsum(terms)
    except OverflowError as exc:
        raise FloatingPointError(f"{label} overflowed") from exc
    if not math.isfinite(result):
        raise FloatingPointError(f"{label} is not finite")
    return result


def _phi_series(x: float) -> float:
    """Return ``(1-exp(-x))/x`` by a cancellation-free Horner series."""

    return 1.0 + x * (
        -1.0 / 2.0
        + x
        * (
            1.0 / 6.0
            + x
            * (
                -1.0 / 24.0
                + x
                * (
                    1.0 / 120.0
                    + x
                    * (
                        -1.0 / 720.0
                        + x
                        * (
                            1.0 / 5040.0
                            + x * (-1.0 / 40320.0 + x * (1.0 / 362880.0))
                        )
                    )
                )
            )
        )
    )


def _phi_prime_series(x: float) -> float:
    """Return the derivative of ``(1-exp(-x))/x`` near zero."""

    return -1.0 / 2.0 + x * (
        1.0 / 3.0
        + x
        * (
            -1.0 / 8.0
            + x
            * (
                1.0 / 30.0
                + x
                * (
                    -1.0 / 144.0
                    + x
                    * (
                        1.0 / 840.0
                        + x
                        * (
                            -1.0 / 5760.0
                            + x * (1.0 / 45360.0 + x * (-1.0 / 403200.0))
                        )
                    )
                )
            )
        )
    )


def _transfer_factors(
    chi_s_inv: float,
    duration_s: float,
    *,
    with_chi_derivative: bool,
) -> tuple[float, float, float | None]:
    """Return attenuation, source integral, and optionally ``dS/dchi``.

    With ``x = chi*duration``, the source integral is
    ``S = duration*(1-exp(-x))/x``.  The series branch supplies the exact
    continuous limits ``S=duration`` and ``dS/dchi=-duration**2/2`` at zero.
    """

    chi = float(chi_s_inv)
    duration = float(duration_s)
    x = chi * duration
    if not math.isfinite(x):
        raise FloatingPointError("net optical depth overflowed or became nonfinite")

    try:
        attenuation = math.exp(-x)
    except OverflowError as exc:
        raise FloatingPointError("pair-transfer attenuation overflowed") from exc
    if not math.isfinite(attenuation):
        raise FloatingPointError("pair-transfer attenuation is not finite")

    if abs(x) <= _SERIES_THRESHOLD:
        source_factor = duration * _phi_series(x)
        source_chi_derivative = (
            duration * duration * _phi_prime_series(x)
            if with_chi_derivative
            else None
        )
    else:
        try:
            absorbed = -math.expm1(-x)
        except OverflowError as exc:
            raise FloatingPointError("pair-transfer source integral overflowed") from exc
        source_factor = absorbed / chi
        # dS/dchi = (duration*exp(-chi*duration) - S)/chi.  The
        # cancellation-sensitive neighbourhood is handled by the series above.
        source_chi_derivative = (
            (duration * attenuation - source_factor) / chi
            if with_chi_derivative
            else None
        )

    factors = (attenuation, source_factor)
    if not all(math.isfinite(value) for value in factors):
        raise FloatingPointError("pair-transfer factors overflowed or became nonfinite")
    if source_factor < 0.0:
        raise FloatingPointError("pair-transfer source factor lost positivity")
    if with_chi_derivative and (
        source_chi_derivative is None
        or not math.isfinite(source_chi_derivative)
    ):
        raise FloatingPointError(
            "pair-transfer chi derivative overflowed or became nonfinite"
        )
    return attenuation, source_factor, source_chi_derivative


def constant_positive_pair_transfer(
    *,
    f_initial: float,
    eta_s_inv: float,
    kappa_s_inv: float,
    duration_s: float,
) -> float:
    """Evaluate the exact constant-pair transfer without clipping.

    ``eta_s_inv`` and ``kappa_s_inv`` are individually nonnegative, while the
    net coefficient ``chi = kappa - eta`` may have either sign.  At
    ``chi == 0`` the returned value is the continuous limit
    ``f_initial + eta_s_inv*duration_s``.
    """

    f0, eta, kappa, duration = _validated_primal_inputs(
        f_initial, eta_s_inv, kappa_s_inv, duration_s
    )
    chi = kappa - eta
    attenuation, source_factor, _ = _transfer_factors(
        chi, duration, with_chi_derivative=False
    )
    result = _finite_sum(
        (attenuation * f0, eta * source_factor),
        label="pair-transfer result",
    )
    if result < 0.0:
        raise FloatingPointError("pair-transfer result lost positivity")
    return result


def constant_positive_pair_transfer_jvp(
    *,
    f_initial: float,
    eta_s_inv: float,
    kappa_s_inv: float,
    duration_s: float,
    d_f_initial: float = 0.0,
    d_eta_s_inv: float = 0.0,
    d_kappa_s_inv: float = 0.0,
    d_duration_s: float = 0.0,
) -> float:
    """Analytic fixed-branch JVP of :func:`constant_positive_pair_transfer`.

    The derivative keeps the two positive coefficients independent.  Thus
    ``dchi = d_kappa_s_inv - d_eta_s_inv``; omitting this dependence would
    differentiate a different physical law.  The formula is continuous at
    ``chi == 0`` and does not use a finite-difference fallback.
    """

    f0, eta, kappa, duration = _validated_primal_inputs(
        f_initial, eta_s_inv, kappa_s_inv, duration_s
    )
    tangent_values = (
        _finite_scalar(d_f_initial, name="d_f_initial tangent"),
        _finite_scalar(d_eta_s_inv, name="d_eta_s_inv tangent"),
        _finite_scalar(d_kappa_s_inv, name="d_kappa_s_inv tangent"),
        _finite_scalar(d_duration_s, name="d_duration_s tangent"),
    )
    d_f0, d_eta, d_kappa, d_duration = tangent_values
    d_chi = d_kappa - d_eta
    if not math.isfinite(d_chi):
        raise FloatingPointError("net-coefficient tangent is not finite")

    chi = kappa - eta
    attenuation, source_factor, source_chi_derivative = _transfer_factors(
        chi, duration, with_chi_derivative=True
    )
    assert source_chi_derivative is not None

    chi_partial = _finite_sum(
        (
            -duration * attenuation * f0,
            eta * source_chi_derivative,
        ),
        label="pair-transfer chi partial",
    )
    duration_partial = _finite_sum(
        (-chi * attenuation * f0, eta * attenuation),
        label="pair-transfer duration partial",
    )
    return _finite_sum(
        (
            attenuation * d_f0,
            source_factor * d_eta,
            chi_partial * d_chi,
            duration_partial * d_duration,
        ),
        label="pair-transfer JVP",
    )


__all__ = [
    "CLASSIFICATION",
    "constant_positive_pair_transfer",
    "constant_positive_pair_transfer_jvp",
]
