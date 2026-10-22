"""Maxwellian kinetic-energy moments of the pinned RR/DR rate fits.

For a temperature-independent electron collision kernel and a Maxwellian
electron distribution, the kinetic-energy loss coefficient is

    L(T) = k_B T [3 alpha(T)/2 + d alpha(T)/d ln(T)].

Here alpha has units m^3 s^-1 and L has units J m^3 s^-1. Multiplication by
n_e n_ion gives a proper volume cooling rate in W m^-3. Ionization binding
energy is a separate reservoir: it is deliberately absent from L.

Applying this identity to an empirical number-rate fit defines a conditional
energy-moment closure. Number-rate fit accuracy alone does not bound the
accuracy of its temperature derivative. This module verifies the algebra and
the pinned fit, not an independent atomic cooling calculation.
"""
from __future__ import annotations

import math

import numpy as np

KB_J_K = 1.380649e-23
CM3_M3 = 1e-6


def maxwellian_energy_coefficient(temperature_K, alpha, d_alpha_dlogT):
    """Kinetic-energy moment from a rate and its logarithmic derivative.

The caller owns the Maxwellian/kernel assumptions and temperature domain.
This small algebraic function also supports independently integrated kernels
in verification; it does not infer a cross section from one rate sample.
"""
    temperature = float(temperature_K)
    if not math.isfinite(temperature) or temperature <= 0:
        raise ValueError('temperature must be finite and positive')
    return KB_J_K * temperature * (1.5 * np.asarray(alpha)
                                  + np.asarray(d_alpha_dlogT))


class RecombinationMoments:
    """Prepared RR/DR fits with analytic first and second log derivatives.

    ``atomic`` is the verified donor AtomicNetwork. No donor object is
    changed. Arrays returned by ``evaluate`` follow its length-21 ion order.
    Signed DR fit amplitudes are retained. Positivity is required of the
    total rate and total kinetic-energy loss, not of every fit component.

    A floating zero for a present DR channel can be exponential underflow.
    The returned ``dr_numerical_zero_mask`` and ``dr_structurally_absent_mask``
    distinguish that observation from an absent channel. They do not turn an
    underflowed channel into a mathematical support zero.
    """

    def __init__(self, atomic):
        self.size = int(atomic.size)
        self.indices = np.asarray(atomic.recombination_indices, dtype=int).copy()
        self.domain = tuple(float(x) for x in
                            atomic.coefficients['runtime_temperature_domain_K'])
        rr_rows = [atomic.coefficients['rr'][f'{atomic.Z[i]}:{atomic.q[i]}']
                   for i in self.indices]
        self.rr_parameters = np.asarray([[row[k] for k in
            ('A_cm3_s', 'B', 'T0_K', 'T1_K', 'C', 'T2_K')]
            for row in rr_rows], dtype=float)
        self.dr_rows = []
        for index in self.indices:
            row = atomic.coefficients['dr'].get(
                f'{atomic.Z[index]}:{atomic.q[index]}')
            if row is not None:
                c = np.asarray(row['c_cm3_s_K32'], dtype=float).copy()
                e = np.asarray(row['E_K'], dtype=float).copy()
                if c.ndim != 1 or e.shape != c.shape or c.size == 0:
                    raise ValueError('malformed DR fit vectors')
                if not np.all(np.isfinite(c)) or not np.all(np.isfinite(e)):
                    raise ValueError('nonfinite DR fit coefficients')
                if np.any(e < 0):
                    raise ValueError('DR resonance energies must be nonnegative')
                c.setflags(write=False)
                e.setflags(write=False)
                self.dr_rows.append((int(index), c, e))
        self.dr_present = np.zeros(self.size, dtype=bool)
        for index, _c, _e in self.dr_rows:
            self.dr_present[index] = True
        for array in (self.indices, self.rr_parameters, self.dr_present):
            array.setflags(write=False)

    def evaluate(self, temperature_K):
        """Return rates, kinetic-energy coefficients and d/d ln(T) arrays.

        The rate arithmetic follows the donor formula, including the order of
        its cm^3-to-m^3 conversion. Derived energy coefficients use direct DR
        moment sums, avoiding subtraction of 3 alpha/2 from a steep derivative.
        No clipping or tolerance relaxation is used for a negative fit total.
        """
        if np.iscomplexobj(temperature_K):
            raise ValueError('temperature must be real')
        temperature = float(temperature_K)
        if not math.isfinite(temperature) or not (
                self.domain[0] <= temperature <= self.domain[1]):
            raise ValueError(f'temperature outside supported '
                             f'{self.domain[0]}..{self.domain[1]} K')
        a, b, t0, t1, c, t2 = self.rr_parameters.T
        z = t2 / temperature
        correction = c * np.exp(-z)
        beff = b + correction
        b1 = correction * z
        b2 = b1 * (z - 1)
        u = np.sqrt(temperature / t0)
        v = np.sqrt(temperature / t1)
        # Preserve the donor's number-rate formula and arithmetic order.
        alpha = CM3_M3 * a / (u * (1 + u)**(1 - beff)
                            * (1 + v)**(1 + beff))
        lu, lv = np.log1p(u), np.log1p(v)
        du = u / (2 * (1 + u))
        dv = v / (2 * (1 + v))
        ddu = u / (4 * (1 + u)**2)
        ddv = v / (4 * (1 + v)**2)
        slope = -.5 - (1 - beff) * du - (1 + beff) * dv + b1 * (lu - lv)
        curvature = (-(1 - beff) * ddu - (1 + beff) * ddv
                     + 2 * b1 * (du - dv) + b2 * (lu - lv))
        fields = {name: np.zeros(self.size) for name in (
            'rr_m3_s', 'dr_m3_s', 'drr_dlogT', 'ddr_dlogT',
            'rr_loss_J_m3_s', 'dr_loss_J_m3_s',
            'drr_loss_dlogT', 'ddr_loss_dlogT')}
        fields['rr_m3_s'][self.indices] = alpha
        fields['drr_dlogT'][self.indices] = alpha * slope
        fields['rr_loss_J_m3_s'][self.indices] = (
            KB_J_K * temperature * alpha * (1.5 + slope))
        fields['drr_loss_dlogT'][self.indices] = (
            KB_J_K * temperature * alpha
            * ((1 + slope) * (1.5 + slope) + curvature))
        for index, coeff, energy_K in self.dr_rows:
            exponents = energy_K / temperature
            terms = coeff * np.exp(-exponents)
            prefactor = CM3_M3 * temperature**(-1.5)
            fields['dr_m3_s'][index] = prefactor * np.sum(terms)
            fields['ddr_dlogT'][index] = prefactor * np.sum(
                terms * (exponents - 1.5))
            fields['dr_loss_J_m3_s'][index] = KB_J_K * prefactor * np.sum(
                terms * energy_K)
            fields['ddr_loss_dlogT'][index] = KB_J_K * prefactor * np.sum(
                terms * energy_K * (exponents - 1.5))
        for name, value in fields.items():
            if not np.all(np.isfinite(value)):
                raise ValueError('nonfinite recombination moment: ' + name)
        for name in ('rr_m3_s', 'dr_m3_s',
                     'rr_loss_J_m3_s', 'dr_loss_J_m3_s'):
            if np.any(fields[name] < 0):
                raise ValueError('negative total recombination fit: ' + name)
        fields['dr_structurally_absent_mask'] = ~self.dr_present
        fields['dr_numerical_zero_mask'] = (
            self.dr_present & (fields['dr_m3_s'] == 0))
        return fields
