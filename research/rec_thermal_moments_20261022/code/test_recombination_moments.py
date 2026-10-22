"""Focused numerical and algebraic checks for recombination_moments.

Run directly from any directory. The evidence is written beside this research
unit. These tests validate the implemented fit/moment contract; independent
atomic cooling data remain a separate scientific comparison.
"""
from __future__ import annotations

import copy
import hashlib
import json
import math
from pathlib import Path
import platform
import sys
import time
from types import SimpleNamespace
import unittest

import numpy as np
import scipy
from scipy.integrate import quad

UNIT = Path(__file__).resolve().parents[1]
DONOR = UNIT.parent / 'rec_rei_hheli_sandbox_20261021'
sys.path.insert(0, str(DONOR / 'code'))
from atomic_network import AtomicNetwork
from recombination_moments import (
    KB_J_K, RecombinationMoments, maxwellian_energy_coefficient)

METRICS = {}


def synthetic_atomic(atomic, dr_row):
    coefficients = copy.deepcopy(atomic.coefficients)
    coefficients['dr'] = {'2:1': dr_row}
    return SimpleNamespace(size=atomic.size, coefficients=coefficients,
        recombination_indices=atomic.recombination_indices,
        Z=atomic.Z, q=atomic.q)


class TestRecombinationMoments(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.atomic = AtomicNetwork()
        cls.moments = RecombinationMoments(cls.atomic)

    def test_pinned_number_rate_parity(self):
        temperatures = np.geomspace(100., 1e6, 129)
        for t in temperatures:
            expected = self.atomic.rates(t, .37)
            actual = self.moments.evaluate(t)
            for name in ('rr_m3_s', 'dr_m3_s'):
                np.testing.assert_array_equal(actual[name], expected[name])
                self.assertEqual(actual[name].dtype, expected[name].dtype)
                self.assertEqual(actual[name].tobytes(), expected[name].tobytes())
        METRICS['number_rate_parity'] = {
            'temperature_nodes': len(temperatures),
            'arrays_compared': 2 * len(temperatures),
            'comparison': 'same dtype, np.array_equal and exact tobytes equality',
            'result': 'PASS'}

    def test_log_derivatives_against_five_point_differences(self):
        h = 1e-4
        comparisons = (
            ('rr_m3_s', 'drr_dlogT'), ('dr_m3_s', 'ddr_dlogT'),
            ('rr_loss_J_m3_s', 'drr_loss_dlogT'),
            ('dr_loss_J_m3_s', 'ddr_loss_dlogT'))
        errors = {derivative: 0. for _field, derivative in comparisons}
        counts = {derivative: 0 for _field, derivative in comparisons}
        for temperature in np.geomspace(125., 8e5, 31):
            center = self.moments.evaluate(temperature)
            around = {j: self.moments.evaluate(temperature * math.exp(j * h))
                      for j in (-2, -1, 1, 2)}
            for field, derivative in comparisons:
                fd = (around[-2][field] - 8 * around[-1][field]
                      + 8 * around[1][field] - around[2][field]) / (12 * h)
                analytic = center[derivative]
                scale = abs(center[field]) + abs(analytic)
                # Subnormal/underflow values have an independent classification
                # check below; do not turn their relative noise into an oracle.
                mask = scale > 1e-250
                error = np.max(abs(fd[mask] - analytic[mask]) / scale[mask],
                               initial=0.)
                errors[derivative] = max(errors[derivative], float(error))
                counts[derivative] += int(np.count_nonzero(mask))
                self.assertLess(error, 2e-6)
        METRICS['analytic_log_derivatives'] = {
            'temperature_nodes': 31, 'five_point_log_step': h,
            'max_scaled_error': errors, 'scalar_checks': counts,
            'threshold': 2e-6, 'result': 'PASS'}

    def test_power_kernel_energy_integrals(self):
        maximum = 0.
        rows = []
        # K(E) proportional to E^p is a positive, T-independent kernel.
        # Direct quadrature of its zeroth and first energy integrals gives a
        # reference independent of the RR/DR formula implementation.
        for p in (-.5, .25, 1., 2.5):
            integral0 = quad(lambda e: e**p * math.exp(-e), 0., np.inf,
                             epsabs=1e-10, epsrel=2e-11)[0]
            integral1 = quad(lambda e: e**(p + 1) * math.exp(-e), 0., np.inf,
                             epsabs=1e-10, epsrel=2e-11)[0]
            for temperature in (100., 1e4, 1e6):
                alpha = 1e-18 * (temperature / 1e4)**(p - .5) * integral0
                dalpha = (p - .5) * alpha
                coefficient = float(maxwellian_energy_coefficient(
                    temperature, alpha, dalpha))
                reference = KB_J_K * temperature * alpha * integral1 / integral0
                error = abs(coefficient - reference) / reference
                maximum = max(maximum, error)
                self.assertLess(error, 1e-9)
                rows.append({'power': p, 'temperature_K': temperature,
                             'relative_error': error})
        METRICS['positive_power_kernel_quadrature'] = {
            'kernel_count': 4, 'evaluations': len(rows),
            'max_relative_error': maximum, 'threshold': 1e-9,
            'result': 'PASS'}

    def test_single_resonance_kinetic_energy(self):
        energy_K = 17000.
        atom = synthetic_atomic(self.atomic, {
            'c_cm3_s_K32': [3e-4], 'E_K': [energy_K]})
        moment = RecombinationMoments(atom)
        count = 0
        for t in (100., 1000., 17000., 1e6):
            result = moment.evaluate(t)
            for index in (8, 11):
                # A delta-function resonance selects exactly k_B E_K,
                # independently of the Maxwellian temperature.
                expected = KB_J_K * energy_K * result['dr_m3_s'][index]
                np.testing.assert_allclose(result['dr_loss_J_m3_s'][index],
                                           expected, rtol=3e-16, atol=0.)
                count += 1
        METRICS['single_resonance_reference'] = {
            'scalar_checks': count, 'energy_K': energy_K, 'result': 'PASS'}

    def test_domain_grid_total_positivity_and_finiteness(self):
        temperatures = np.geomspace(100., 1e6, 1001)
        rr_min = math.inf
        dr_max = 0.
        for t in temperatures:
            result = self.moments.evaluate(t)
            rr = result['rr_m3_s'][self.atomic.recombination_indices]
            rr_loss = result['rr_loss_J_m3_s'][self.atomic.recombination_indices]
            f = rr_loss / (KB_J_K * t * rr)
            self.assertTrue(np.all(f > 0))
            rr_min = min(rr_min, float(f.min()))
            dr_max = max(dr_max, float(result['dr_loss_J_m3_s'].max()))
            for name in ('rr_m3_s', 'dr_m3_s',
                         'rr_loss_J_m3_s', 'dr_loss_J_m3_s'):
                self.assertTrue(np.all(np.isfinite(result[name])))
                self.assertTrue(np.all(result[name] >= 0))
        METRICS['finite_domain_grid'] = {
            'temperature_nodes': len(temperatures), 'domain_K': [100., 1e6],
            'minimum_RR_weighted_energy_factor': rr_min,
            'maximum_DR_loss_J_m3_s': dr_max, 'result': 'PASS',
            'scope': 'finite grid, not interval proof or atomic accuracy'}

    def test_underflow_is_distinct_from_absent_channel(self):
        low = self.moments.evaluate(100.)
        high = self.moments.evaluate(1e6)
        self.assertTrue(low['dr_numerical_zero_mask'][8])
        self.assertFalse(low['dr_structurally_absent_mask'][8])
        self.assertFalse(high['dr_numerical_zero_mask'][8])
        self.assertTrue(low['dr_structurally_absent_mask'][2])
        self.assertFalse(low['dr_numerical_zero_mask'][2])
        METRICS['DR_zero_classification'] = {
            'present_but_underflowed_indices_at_100K':
                np.flatnonzero(low['dr_numerical_zero_mask']).tolist(),
            'structurally_absent_indices':
                np.flatnonzero(low['dr_structurally_absent_mask']).tolist(),
            'result': 'PASS'}

    def test_signed_DR_components_are_not_clipped(self):
        # Preserve a negative fitting component while the total is physical.
        row = {'c_cm3_s_K32': [2e-4, -1e-4], 'E_K': [1000., 3000.]}
        moment = RecombinationMoments(synthetic_atomic(self.atomic, row))
        temperature = 500.
        result = moment.evaluate(temperature)
        exact_rate = (1e-6 * temperature**(-1.5)
                      * (2e-4 * math.exp(-2.) - 1e-4 * math.exp(-6.)))
        self.assertEqual(result['dr_m3_s'][8], exact_rate)
        # At 10000K the same synthetic fit has a positive number rate but
        # a negative energy moment. Reject this inconsistency explicitly.
        with self.assertRaisesRegex(ValueError, 'negative total.*dr_loss'):
            moment.evaluate(10000.)
        METRICS['signed_DR_and_invalid_moment'] = {
            'signed_component_preserved': True,
            'positive_rate_negative_loss_rejected': True, 'result': 'PASS'}

    def test_invalid_temperature_rejected(self):
        inputs = (0., -1., 99.999, 1000000.1, float('nan'), float('inf'), 1j)
        for value in inputs:
            with self.assertRaises((ValueError, TypeError)):
                self.moments.evaluate(value)
        METRICS['invalid_temperature'] = {
            'rejected_cases': len(inputs), 'result': 'PASS'}

    def test_input_sources_unchanged(self):
        # Re-instantiation invokes the donor's authoritative byte manifest.
        same = AtomicNetwork()
        self.assertEqual(same.coefficients, self.atomic.coefficients)
        self.assertEqual(same.model, self.atomic.model)
        METRICS['donor_source_manifest'] = {'result': 'PASS',
            'action': 'donor authoritative _verified_inputs invoked'}


def main():
    start = time.perf_counter()
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestRecombinationMoments)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    files = [Path(__file__), Path(__file__).with_name('recombination_moments.py'),
             DONOR / 'code/atomic_network.py', DONOR / 'data/atomic_coefficients.json']
    evidence = {
        'schema': 'rec.thermal_moments.tests.v1',
        'decision': 'PASS_SCOPED' if result.wasSuccessful() else 'FAIL',
        'tests_run': result.testsRun,
        'failures': [{'test': str(test), 'traceback': trace}
                     for test, trace in result.failures],
        'errors': [{'test': str(test), 'traceback': trace}
                   for test, trace in result.errors],
        'metrics': METRICS,
        'wall_s': time.perf_counter() - start,
        'environment': {'python': sys.version.split()[0], 'numpy': np.__version__,
                        'scipy': scipy.__version__, 'platform': platform.platform()},
        'inputs_and_code': [{'path': str(path.relative_to(UNIT.parent)),
                            'bytes': path.stat().st_size,
                            'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}
                           for path in files],
        'scientific_scope': 'Algebra and implementation of pinned fit-derived '
                            'Maxwellian moments. Independent atomic-energy-loss '
                            'accuracy and cosmological convergence not established.'}
    path = UNIT / 'evidence/moments_tests.json'
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        previous = json.loads(path.read_text())
        history = previous.pop('prior_runs', [])
        evidence['prior_runs'] = history + [previous]
    path.write_text(json.dumps(evidence, indent=2, allow_nan=False) + '\n')
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    raise SystemExit(main())
