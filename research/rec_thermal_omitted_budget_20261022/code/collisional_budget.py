"""Fixed-path H/He collision budget; this module never integrates an ODE.

HG97 Appendix A (https://arxiv.org/pdf/astro-ph/9612232, pp. 27, 29--30)
supplies CI coefficients in cm^3/s and CE coefficients in erg cm^3/s.
Their SI factors are 1e-6 and 1e-13. Published fit domains are checked even
when a channel has no targets. An explicit continuation returns support and
floating-point underflow flags separately; it is not a validated extension.

CI transfers kinetic energy to the parent's canonical ionization ladder.
The HG97 temperature thresholds remain in the rates, so this is a documented
hybrid. Each CI creates one electron and preserves every nuclear inventory.
CE is optically thin escaping line power. Li CI/CE and HeI CE are unavailable,
not certified zeros; returned totals include only the stated H/He channels.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np

SOURCE_PATH = Path(__file__).resolve().parents[1] / "data/HG97_COLLISIONAL_SOURCE.json"
KB_J_K = 1.380649e-23
_GROUPS = {
    "n": (0,), "H1": (1, 2), "D": (3, 4), "T": (5, 6),
    "He3": (7, 8, 9), "He4": (10, 11, 12),
    "Li6": (13, 14, 15, 16), "Li7": (17, 18, 19, 20),
}


class FitDomainError(ValueError):
    """At least one included fit lacks a published accuracy claim at this T."""

    def __init__(self, temperature_K, processes):
        self.temperature_K = temperature_K
        self.processes = tuple(processes)
        super().__init__(
            f"HG97 temperature {temperature_K:g} K outside published support for "
            + ", ".join(processes)
            + "; use allow_extrapolation=True only for labelled analytic continuation"
        )


def _scalar(value, name, *, positive):
    arr = np.asarray(value)
    if (arr.ndim != 0 or np.iscomplexobj(arr)
            or arr.dtype.kind not in "fiu" or arr.dtype.kind == "b"):
        raise ValueError(f"{name} must be a real scalar")
    result = float(arr)
    if not math.isfinite(result) or (result <= 0 if positive else result < 0):
        raise ValueError(f"{name} must be finite and {'positive' if positive else 'nonnegative'}")
    return result


def _softplus(x):
    return max(x, 0.0) + math.log1p(math.exp(-abs(x)))


def _threshold_over_T(threshold, T):
    # Direct division avoids magnifying a log/exp roundoff error in exp(-chi/T).
    return math.inf if T < threshold / np.finfo(float).max else threshold / T


def _rate_from_log(log_rate):
    value = math.exp(log_rate)
    if not math.isfinite(value):
        raise FloatingPointError("nonfinite collisional coefficient")
    # Every included analytic coefficient is strictly positive at finite T>0.
    return value, value == 0.0


def _product(*factors):
    value = math.prod(factors)
    if not math.isfinite(value):
        raise FloatingPointError("collisional source exceeds finite floating-point range")
    return value, value == 0.0 and all(x > 0 for x in factors)


class CollisionalBudget:
    """Postprocess a native 21-species AtomicNetwork state in physical seconds.

    ``evaluate(Y, T, nb, allow_extrapolation=False)`` returns a dictionary.
    ``dY_dt`` and ``particle_source`` have units s^-1 per baryon. All power
    fields have units W/m^3. ``coefficients`` contains CI in m^3/s and CE in
    J m^3/s. ``validity`` describes only the five included electronic fits;
    its ``in_validated_domain`` means inside the source's published range.
    ``unavailable`` and native masks identify unmodelled Li and HeI CE terms.
    """

    def __init__(self, atomic):
        if atomic.size != 21 or any(tuple(atomic.isotope_groups.get(k, ())) != v
                                    for k, v in _GROUPS.items()):
            raise ValueError("CollisionalBudget requires the parent's native 21-species layout")
        self.atomic = atomic
        self.source = json.loads(SOURCE_PATH.read_text())
        self.q = np.array(atomic.q, dtype=float, copy=True)
        self.energy = np.array(atomic.ionization_energy_J, dtype=float, copy=True)
        self.A = np.array(atomic.A, dtype=float, copy=True)
        if any(x.shape != (21,) or not np.isfinite(x).all()
               for x in (self.q, self.energy, self.A)):
            raise ValueError("invalid parent charge, mass or ionization-energy arrays")
        self.ci_specs = []
        self.ce_specs = []
        for isotope in ("H1", "D", "T", "He3", "He4"):
            indices = _GROUPS[isotope]
            electronic = ("HI",) if isotope in ("H1", "D", "T") else ("HeI", "HeII")
            for lower, upper, channel in zip(indices[:-1], indices[1:], electronic):
                chi = float(self.energy[upper] - self.energy[lower])
                if (self.q[upper] - self.q[lower] != 1
                        or self.A[upper] != self.A[lower] or not math.isfinite(chi) or chi <= 0):
                    raise ValueError("parent CI transition must preserve nuclei and raise charge/energy")
                self.ci_specs.append((isotope, lower, upper, channel, chi))
            self.ce_specs.append((isotope, indices[0] if len(indices) == 2 else indices[1],
                                  "HI" if len(indices) == 2 else "HeII"))
        self.ci_available_mask = np.zeros(21, dtype=bool)
        self.ce_available_mask = np.zeros(21, dtype=bool)
        self.ci_unavailable_mask = np.zeros(21, dtype=bool)
        self.ce_unavailable_mask = np.zeros(21, dtype=bool)
        self.ci_available_mask[[s[1] for s in self.ci_specs]] = True
        self.ce_available_mask[[s[1] for s in self.ce_specs]] = True
        self.ci_unavailable_mask[[13, 14, 15, 17, 18, 19]] = True
        self.ce_unavailable_mask[[7, 10, 13, 14, 15, 17, 18, 19]] = True

    def coefficients(self, T, *, allow_extrapolation=False):
        """Return (five SI coefficient values, per-process source/numeric flags)."""
        T = _scalar(T, "T", positive=True)
        if not isinstance(allow_extrapolation, (bool, np.bool_)):
            raise ValueError("allow_extrapolation must be boolean")
        log_T = math.log(T)
        values, validity = {}, {}
        for kind in ("CI", "CE"):
            block = self.source[kind]
            lo, hi = block["published_temperature_range_K"]
            supported = lo <= T <= hi
            for electronic, p in block["parameters"].items():
                threshold = self.source["threshold_K"][electronic]
                ratio = _threshold_over_T(threshold, T)
                if kind == "CI":
                    log_lambda = math.log(2 * threshold) - log_T
                    log_rate = (math.log(p["A"]) - 1.5 * log_T - ratio
                                - p["b"] * log_lambda
                                - p["e"] * _softplus(p["d"] * (log_lambda - math.log(p["c"]))))
                else:
                    log_rate = (math.log(p["A"]) + p["temperature_power"] * log_T
                                - 0.75 * ratio - _softplus(0.5 * (log_T - math.log(1e5))))
                value, underflow = _rate_from_log(log_rate + math.log(block["cgs_to_SI"]))
                key = kind + "_" + electronic
                values[key] = value
                validity[key] = dict(available=True, in_validated_domain=supported,
                                     extrapolated=not supported, underflow_to_zero=underflow,
                                     published_temperature_range_K=(lo, hi),
                                     units="m3/s" if kind == "CI" else "J m3/s")
        unsupported = [k for k, v in validity.items() if not v["in_validated_domain"]]
        if unsupported and not allow_extrapolation:
            raise FitDomainError(T, unsupported)
        return values, validity

    def evaluate(self, Y, T, nb, allow_extrapolation=False):
        """Evaluate included CI/CE at fixed Y,T,nb; never clip or evolve inputs."""
        arr = np.asarray(Y)
        if arr.shape != (21,) or np.iscomplexobj(arr):
            raise ValueError("Y must be a real native 21-vector")
        Y = np.asarray(arr, dtype=float)
        if not np.isfinite(Y).all() or np.any(Y < 0):
            raise ValueError("Y must be finite and nonnegative; no population clipping is performed")
        nb = _scalar(nb, "nb", positive=False)
        values, validity = self.coefficients(T, allow_extrapolation=allow_extrapolation)
        with np.errstate(over="raise", invalid="raise"):
            electron_abundance = float(self.q @ Y)
        ne, _ = _product(nb, electron_abundance)
        if ne < 0:
            raise ValueError("parent charges produced a negative electron density")
        dY = np.zeros(21)
        ci_rows, ce_rows = [], []
        for isotope, lower, upper, channel, chi in self.ci_specs:
            coefficient = values["CI_" + channel]
            event, event_underflow = _product(ne, coefficient, float(Y[lower]))
            volumetric_event, volume_underflow = _product(nb, event)
            binding, power_underflow = _product(volumetric_event, chi)
            dY[lower] -= event
            dY[upper] += event
            threshold = self.source["threshold_K"][channel]
            ci_rows.append(dict(isotope=isotope, process="CI_" + channel,
                                lower_index=lower, upper_index=upper, coefficient_m3_s=coefficient,
                                event_rate_per_baryon_s=event, event_rate_m3_s=volumetric_event,
                                chi_J=chi, rate_threshold_K=threshold,
                                chi_over_HG_threshold_minus_one=chi / (KB_J_K * threshold) - 1,
                                kinetic_W_m3=-binding, binding_W_m3=binding,
                                event_underflow_to_zero=event_underflow,
                                volume_underflow_to_zero=volume_underflow,
                                power_underflow_to_zero=power_underflow))
        for isotope, index, channel in self.ce_specs:
            coefficient = values["CE_" + channel]
            power, underflow = _product(ne, nb, float(Y[index]), coefficient)
            ce_rows.append(dict(isotope=isotope, process="CE_" + channel, target_index=index,
                                coefficient_J_m3_s=coefficient, cooling_W_m3=power,
                                power_underflow_to_zero=underflow))
        binding = math.fsum(r["binding_W_m3"] for r in ci_rows)
        particle = math.fsum(r["event_rate_per_baryon_s"] for r in ci_rows)
        ce = math.fsum(r["cooling_W_m3"] for r in ce_rows)
        with np.errstate(over="raise", invalid="raise"):
            gradient = nb * float(self.energy @ dY)
            charge_gradient = float(self.q @ dY)
        if not np.isfinite(dY).all() or not all(map(math.isfinite, (binding, particle, ce, gradient))):
            raise FloatingPointError("nonfinite aggregate collisional source")
        unavailable = {key: dict(available=False, coefficient=None,
                                reason="No coefficient in this source-bound H/He budget")
                       for key in self.source["application"]["unavailable"]}
        return dict(dY_dt=dY, particle_source=particle, ne_m3=ne,
                    ci_kinetic_W_m3=-binding, ci_binding_W_m3=binding,
                    ci_binding_gradient_W_m3=gradient, ci_energy_residual_W_m3=0.0,
                    ci_gradient_residual_W_m3=gradient - binding,
                    particle_source_residual_s=charge_gradient - particle,
                    ci_escape_W_m3=0.0, ce_cooling_W_m3=ce,
                    coefficients=values, validity=validity, unavailable=unavailable,
                    all_included_fits_in_domain=all(v["in_validated_domain"] for v in validity.values()),
                    ci_channels=ci_rows, ce_channels=ce_rows,
                    ci_available_mask=self.ci_available_mask.copy(),
                    ci_unavailable_mask=self.ci_unavailable_mask.copy(),
                    ce_available_mask=self.ce_available_mask.copy(),
                    ce_unavailable_mask=self.ce_unavailable_mask.copy())
