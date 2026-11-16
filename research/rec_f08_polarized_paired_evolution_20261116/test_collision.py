"""Independent physical checks of the exact polarized Thomson semigroup."""
import math
from pathlib import Path
import sys
import unittest
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "rec_tetrad_thomson_repair_20261116"))
from thomson_l4 import weights_l4
from thomson_tetrad import tetrad_grid, physical_weights
from collision import (
    screen_basis, stokes_to_coherency, coherency_to_stokes,
    exact_collision, exact_collision_stokes, collision_increment,
    validate_quadrature,
)


def independent_jones_gain(c, n, w):
    """All incoming/outgoing screen pairs; no 3x3 moment decomposition."""
    et, ep = screen_basis(n)
    e = np.stack((et, ep), axis=-1)
    jones = np.einsum("ika,jkb->ijab", e, e)
    return 1.5 * w[:, None, None] * np.einsum(
        "ijab,...jbc,ijdc->...iad", jones, c, jones, optimize=True)


def independent_uniformization(c, n, w, tau):
    """Poisson sum e^-tau sum tau^k K^k/k! of an explicit Jones kernel."""
    term = c.copy()
    out = math.exp(-tau) * term
    coefficient = math.exp(-tau)
    for k in range(1, 80):
        term = independent_jones_gain(term, n, w)
        coefficient *= tau / k
        out += coefficient * term
        if coefficient < 2e-19:
            break
    return out


class CollisionPhysicsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        path = HERE.parent / "rec_f08_native_thomson_polarization_20261115/source_inputs/F08_ORIGINAL_SOURCE_Q128.csv"
        cls.q = np.loadtxt(path, delimiter=",", skiprows=1)[:, 1:]
        cls.w = weights_l4(cls.q)
        cls.n, jac = tetrad_grid(cls.q, np.array([1.01, .99, 1.]) * 1e-14, 8.875e10)
        cls.pw = physical_weights(cls.q, cls.n, jac, 4)
        rng = np.random.default_rng(20261116)
        z = rng.normal(size=(3, 128, 2, 2)) + 1j * rng.normal(size=(3, 128, 2, 2))
        cls.local = z @ np.swapaxes(z.conj(), -1, -2)
        cls.local /= np.trace(cls.local, axis1=-2, axis2=-1).real.sum(axis=-1)[:, None, None, None]
        et, ep = screen_basis(cls.n)
        cls.e = np.stack((et, ep), axis=-1)
        cls.s = np.einsum("iab,...ibc,idc->...iad", cls.e, cls.local, cls.e)

    def test_physical_moment_contract(self):
        validate_quadrature(self.n, self.pw)
        with self.assertRaisesRegex(ValueError, "second angular moment"):
            validate_quadrature(self.q, np.full(128, 1 / 128))

    def test_stokes_complex_roundtrip_and_sign(self):
        stokes = coherency_to_stokes(self.s, self.n)
        restored = stokes_to_coherency(stokes, self.n)
        np.testing.assert_allclose(restored, self.s, rtol=2e-15, atol=6e-18)
        expected_v = 2 * self.local[..., 0, 1].imag
        np.testing.assert_allclose(stokes[..., 3], expected_v, atol=6e-18)

    def test_independent_explicit_jones_poisson_solution(self):
        expected = independent_uniformization(self.local, self.n, self.pw, .7)
        actual = exact_collision(self.s, self.n, self.pw, .7)
        local = np.einsum("iba,...ibc,icd->...iad", self.e, actual, self.e)
        np.testing.assert_allclose(local, expected, rtol=3e-14, atol=9e-18)

    def test_semigroup_composition(self):
        twice = exact_collision(exact_collision(self.s, self.n, self.pw, .2), self.n, self.pw, .5)
        once = exact_collision(self.s, self.n, self.pw, .7)
        np.testing.assert_allclose(twice, once, rtol=2e-14, atol=9e-18)

    def test_photon_and_elastic_energy_conserved_per_frequency(self):
        out = exact_collision(self.s, self.n, self.pw, 3.5)
        before = np.trace(self.s, axis1=-2, axis2=-1).real.sum(axis=-1)
        after = np.trace(out, axis1=-2, axis2=-1).real.sum(axis=-1)
        np.testing.assert_allclose(after, before, rtol=3e-15, atol=3e-15)
        energy_ev = np.array([10.0, 13.7, 19.3])
        self.assertLess(abs(float(np.dot(energy_ev, after - before))), 6e-14)

    def test_positivity_transversality_and_stokes_cone(self):
        for tau in (1e-10, .7, 50.0):
            out = exact_collision(self.s, self.n, self.pw, tau)
            self.assertGreater(float(np.linalg.eigvalsh(out).min()), -8e-18)
            self.assertLess(float(np.max(abs(np.einsum("...iab,ib->...ia", out, self.n)))), 9e-18)
            stokes = coherency_to_stokes(out, self.n)
            self.assertLess(float(np.max(np.linalg.norm(stokes[..., 1:], axis=-1) - stokes[..., 0])), 9e-18)

    def test_isotropic_fixed_point(self):
        stokes = np.zeros((128, 4))
        stokes[:, 0] = self.pw
        for tau in (1e-12, 1.0, 500.0):
            out = exact_collision_stokes(stokes, self.n, self.pw, tau)
            np.testing.assert_allclose(out, stokes, rtol=2e-15, atol=5e-18)

    def test_optically_thick_equilibrium(self):
        out = exact_collision(self.s, self.n, self.pw, 500.0)
        projectors = np.eye(3) - self.n[:, :, None] * self.n[:, None, :]
        expected = np.broadcast_to(.5 * self.pw[:, None, None] * projectors, self.s.shape)
        np.testing.assert_allclose(out, expected, rtol=5e-14, atol=8e-18)

    def test_tiny_tau_analytic_quadrupole_polarization(self):
        a, tau = 3e-7, 1e-12
        stokes = np.zeros((128, 4))
        stokes[:, 0] = self.w * (1 + a * (3 * self.q[:, 2] ** 2 - 1) / 2)
        s = stokes_to_coherency(stokes, self.q)
        delta = coherency_to_stokes(collision_increment(s, self.q, self.w, tau), self.q)
        b = math.exp(-.3 * tau) * (-math.expm1(-.7 * tau)) / .7
        expected_q = -3 * a / 20 * self.w * (1 - self.q[:, 2] ** 2) * b
        np.testing.assert_allclose(delta[:, 1], expected_q, rtol=3e-8, atol=3e-29)
        self.assertLess(float(np.max(abs(delta[:, 2:]))), 3e-29)
        advanced = exact_collision_stokes(stokes, self.q, self.w, tau)
        np.testing.assert_allclose(advanced[:, 1], expected_q, rtol=3e-8, atol=3e-29)

    def test_zero_step_is_exact_and_empty_spectrum_stays_zero(self):
        np.testing.assert_array_equal(exact_collision(self.s, self.n, self.pw, 0), self.s)
        zeros = np.zeros((17, 128, 3, 3), dtype=complex)
        np.testing.assert_array_equal(exact_collision(zeros, self.n, self.pw, 1), zeros)

    def test_domain_errors_are_not_disabled_by_python_optimized_mode(self):
        for tau in (-1.0, float("nan"), float("inf")):
            with self.assertRaisesRegex(ValueError, "optical depth"):
                exact_collision(self.s, self.n, self.pw, tau)
        bad = self.pw.copy(); bad[0] = -1
        with self.assertRaisesRegex(ValueError, "positive"):
            exact_collision(self.s, self.n, bad, .1)
        bad = self.s.copy(); bad[..., 0, 1] += .1
        with self.assertRaisesRegex(ValueError, "Hermitian"):
            exact_collision(bad, self.n, self.pw, .1)


if __name__ == "__main__":
    unittest.main()
