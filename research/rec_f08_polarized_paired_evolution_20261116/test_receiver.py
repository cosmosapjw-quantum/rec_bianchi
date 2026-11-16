"""Physical contracts of the normalized native-q Thomson receiver.

The finite-frame normalized map is a nonlinear semigroup. Its nonlinearity
witness is reported as a diagnostic; it is not tested as a linear operator.
These checks introduce no production/continuum-admission tolerance.
"""
from pathlib import Path
import json
import math
import unittest

import numpy as np

from receiver import (
    C_CM_S, FHE, SIGMA_T_CM2, collision_stage, collide_native,
    electron_density, tetrad_grid,
)


class NativeReceiverTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        here = Path(__file__).resolve().parent
        path = here.parent / "rec_f08_native_thomson_polarization_20261115/source_inputs/F08_ORIGINAL_SOURCE_Q128.csv"
        cls.q = np.loadtxt(path, delimiter=",", skiprows=1)[:, 1:]
        cls.H = np.array([1.01, 0.99, 1.0]) * 1e-14
        cls.t = 1e11
        cls.n, cls.J = tetrad_grid(cls.q, cls.H, cls.t)
        rng = np.random.default_rng(2026111608)
        cls.state = np.zeros((17, 128, 4))
        intensity = rng.lognormal(mean=-9.0, sigma=0.9, size=(17, 128))
        polarization = rng.normal(size=(17, 128, 3))
        polarization /= np.linalg.norm(polarization, axis=-1, keepdims=True)
        fraction = rng.uniform(0.0, 0.92, size=(17, 128, 1))
        cls.state[..., 0] = intensity
        cls.state[..., 1:] = intensity[..., None] * fraction * polarization
        # Keep genuinely empty physical energy groups in the batched contract.
        cls.state[[0, 16]] = 0.0

    def advance(self, state, tau):
        return collide_native(state, self.q, self.H, self.t, tau)

    def test_zero_optical_depth_preserves_native_bytes(self):
        before = self.state.copy()
        result, diagnostic = self.advance(before, 0.0)
        self.assertEqual(result.tobytes(), before.tobytes())
        self.assertEqual(diagnostic["max_group_number_relative"], 0.0)
        self.assertEqual(diagnostic["max_inverse_projection_raw_relative_drift"], 0.0)
        empty = np.zeros_like(before)
        out, _ = self.advance(empty, 0.7)
        self.assertEqual(out.tobytes(), empty.tobytes())

    def test_local_isotropy_has_native_mass_proportional_to_jacobian(self):
        isotropic = np.zeros((4, 128, 4))
        amplitude = np.array([0.0, 2e-5, 3e-3, 1e-7])
        isotropic[..., 0] = amplitude[:, None] * self.J[None, :]
        for tau in (1e-9, 0.7, 50.0):
            with self.subTest(tau=tau):
                result, _ = self.advance(isotropic, tau)
                scale = float(np.max(isotropic[..., 0]))
                np.testing.assert_allclose(result, isotropic, rtol=8e-15, atol=8e-16 * scale)

    def test_each_energy_inventory_and_arbitrary_photo_rate_are_conserved(self):
        result, diagnostic = self.advance(self.state, 0.7)
        before = self.state[..., 0].sum(axis=-1)
        after = result[..., 0].sum(axis=-1)
        np.testing.assert_allclose(after, before, rtol=4e-15, atol=0.0)
        # Independent arbitrary nonnegative cross-section tables for three
        # species: elastic angular scattering cannot change their scalar rate
        # at fixed spectral energy, gas state, and density.
        rng = np.random.default_rng(38408)
        sigma = rng.uniform(0.0, 7e-18, size=(3, 17))
        sigma[0, :4] = 0.0
        sigma[1, :7] = 0.0
        sigma[2, :10] = 0.0
        rates_before = C_CM_S * (sigma @ before)
        rates_after = C_CM_S * (sigma @ after)
        np.testing.assert_allclose(rates_after, rates_before, rtol=4e-15, atol=0.0)
        energies = np.linspace(10.0, 20.0, 17)
        np.testing.assert_allclose(energies @ after, energies @ before, rtol=4e-15, atol=0.0)
        self.assertLessEqual(diagnostic["max_group_number_relative"], 128 * np.finfo(float).eps)

    def test_physical_polarized_states_remain_positive_semidefinite(self):
        for tau in (1e-10, 0.7, 50.0):
            with self.subTest(tau=tau):
                result, _ = self.advance(self.state, tau)
                i, q, u, v = np.moveaxis(result, -1, 0)
                c = np.empty(result.shape[:-1] + (2, 2), dtype=complex)
                c[..., 0, 0] = 0.5 * (i + q)
                c[..., 1, 1] = 0.5 * (i - q)
                c[..., 0, 1] = 0.5 * (u + 1j * v)
                c[..., 1, 0] = 0.5 * (u - 1j * v)
                scale = float(i.max())
                self.assertGreaterEqual(float(np.linalg.eigvalsh(c).min()), -2e-15 * scale)
                self.assertLessEqual(float(np.max(np.sqrt(q*q + u*u + v*v) - i)), 4e-15 * scale)
                self.assertGreaterEqual(float(i.min()), 0.0)

    def test_normalized_map_fixed_frame_semigroup(self):
        first, _ = self.advance(self.state, 0.2)
        twice, _ = self.advance(first, 0.5)
        once, _ = self.advance(self.state, 0.7)
        scale = float(self.state[..., 0].max())
        np.testing.assert_allclose(twice, once, rtol=3e-14, atol=3e-16 * scale)

    def test_nonlinearity_is_quantified_as_a_closure_diagnostic(self):
        # Individually positive angular fields, deliberately with different
        # angular content and no negative-intensity linearity probes.
        a = np.zeros((128, 4))
        b = np.zeros((128, 4))
        a[:, 0] = self.J * (0.2 + 1.8 * self.q[:, 2] ** 4)
        b[:, 0] = self.J * (0.4 + 2.3 * self.q[:, 0] ** 6)
        a[:, 1] = 0.3 * a[:, 0]
        b[:, 2] = 0.2 * b[:, 0]
        fa, da = self.advance(a, 0.7)
        fb, db = self.advance(b, 0.7)
        fab, dab = self.advance(a + b, 0.7)
        defect = float(np.max(np.abs(fab - fa - fb)))
        relative = defect / float(np.max((a + b)[:, 0]))
        self.assertTrue(math.isfinite(relative))
        print(json.dumps({
            "diagnostic": "native_normalized_closure_nonlinearity",
            "tau": 0.7,
            "max_abs_additivity_defect": defect,
            "max_relative_additivity_defect": relative,
            "raw_normalization_drift_a": da["max_inverse_projection_raw_relative_drift"],
            "raw_normalization_drift_b": db["max_inverse_projection_raw_relative_drift"],
            "raw_normalization_drift_a_plus_b": dab["max_inverse_projection_raw_relative_drift"],
            "linearity_claim": False,
        }, sort_keys=True))

    def test_original_electron_density_and_proper_clock(self):
        gas = np.array([0.9, 0.3, 0.6, 13.2, 0.0])
        expected_n_h = 1e-4 * math.exp(-(self.H[0] + self.H[1] + self.H[2]) * self.t)
        expected_ne = expected_n_h * (0.9 + 0.083 * (0.3 + 2.0 * 0.6))
        actual_ne = electron_density(gas, self.H, self.t)
        self.assertAlmostEqual(actual_ne / expected_ne, 1.0, delta=3e-15)
        zeros = np.zeros((128, 4))
        _, _, _, diagnostic = collision_stage(
            self.state, zeros, zeros, self.q, self.H, gas, self.t, 625000000.0)
        expected_tau = 29979245800.0 * 6.6524587051e-25 * expected_ne * 625000000.0
        self.assertAlmostEqual(diagnostic["n_e_cm3"] / expected_ne, 1.0, delta=3e-15)
        self.assertAlmostEqual(diagnostic["tau"] / expected_tau, 1.0, delta=3e-15)
        self.assertEqual(diagnostic["dt_s"], 625000000.0)
        self.assertEqual(diagnostic["time_s"], self.t)
        self.assertEqual(FHE, 0.083)
        self.assertEqual(SIGMA_T_CM2, 6.6524587051e-25)

    def test_guard_number_and_energy_moments_are_separately_conserved(self):
        gas = np.array([0.9, 0.3, 0.6, 13.2, 0.0])
        gn = np.zeros((128, 4))
        gn[:, 0] = 2e-6 * (0.4 + self.J * (1 + 0.4 * self.q[:, 0]**2))
        gn[:, 1] = 0.2 * gn[:, 0]
        gn[:, 2] = 0.1 * gn[:, 0]
        # Direction-dependent mean energies strictly within the guard domain.
        gu = gn * (3.0 + 4.0 * self.q[:, 2]**2)[:, None]
        n_before = math.fsum(gn[:, 0])
        u_before = math.fsum(gu[:, 0])
        _, out_n, out_u, _ = collision_stage(
            self.state, gn, gu, self.q, self.H, gas, self.t, 625000000.0)
        self.assertAlmostEqual(math.fsum(out_n[:, 0]) / n_before, 1.0, delta=4e-15)
        self.assertAlmostEqual(math.fsum(out_u[:, 0]) / u_before, 1.0, delta=4e-15)
        self.assertTrue(np.all(out_n[:, 0] > 0.0))
        self.assertTrue(np.all(out_u[:, 0] < 10.0 * out_n[:, 0]))
        self.assertTrue(np.all(out_u[:, 0] >= 0.0))

    def test_empty_guard_remains_exactly_empty(self):
        zeros = np.zeros((128, 4))
        _, gn, gu, _ = collision_stage(
            self.state, zeros, zeros, self.q, self.H,
            [0.9, 0.3, 0.6, 13.2, 0.0], self.t, 625000000.0)
        self.assertEqual(gn.tobytes(), zeros.tobytes())
        self.assertEqual(gu.tobytes(), zeros.tobytes())

    def test_impossible_native_gas_fractions_are_rejected(self):
        cases = [(-0.01, 0.3, 0.6), (1.01, 0.3, 0.6),
                 (0.9, -0.01, 0.6), (0.9, 0.3, -0.01),
                 (0.9, 0.6, 0.6), (float("nan"), 0.3, 0.6),
                 (0.9, float("inf"), 0.0)]
        zeros = np.zeros((128, 4))
        for fractions in cases:
            with self.subTest(fractions=fractions):
                with self.assertRaisesRegex(ValueError, "original domain"):
                    collision_stage(self.state, zeros, zeros, self.q, self.H,
                                    [*fractions, 13.2, 0.0], self.t, 625000000.0)

    def test_invalid_guard_energy_is_rejected_even_at_zero_tau(self):
        gn = np.zeros((128, 4))
        gn[:, 0] = 1e-6
        for factor in (10.0, 11.0):
            with self.subTest(factor=factor):
                with self.assertRaisesRegex(ValueError, "guard domain"):
                    collision_stage(self.state, gn, factor * gn, self.q, self.H,
                                    [0.9, 0.3, 0.6, 13.2, 0.0], self.t,
                                    625000000.0, sigma_scale=0.0)
        with self.assertRaisesRegex(ValueError, "guard domain"):
            collision_stage(self.state, np.zeros_like(gn), gn, self.q, self.H,
                            [0.9, 0.3, 0.6, 13.2, 0.0], self.t,
                            625000000.0, sigma_scale=0.0)


if __name__ == "__main__":
    unittest.main()
