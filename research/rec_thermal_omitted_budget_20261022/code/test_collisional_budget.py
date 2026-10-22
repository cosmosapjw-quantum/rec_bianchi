"""Focused source/unit, accounting, domain and numerical-boundary checks."""
import copy
import json
import math
from pathlib import Path
import re
import sys
import unittest

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "rec_rei_hheli_sandbox_20261021/code"))
from atomic_network import AtomicNetwork
from collisional_budget import CollisionalBudget, FitDomainError, KB_J_K


def cgs_reference(T):
    # Direct cgs forms transcribed independently from HG97 pp. 29--30.
    out = {}
    for label, threshold, A, b, c, d, e in (
        ("HI", 157807., 21.11, 1.089, .354, .874, 1.101),
        ("HeI", 285335., 32.38, 1.146, .416, .987, 1.056),
        ("HeII", 631515., 19.95, 1.089, .553, .735, 1.275),
    ):
        lam = 2 * threshold / T
        out["CI_" + label] = A * T**-1.5 * math.exp(-lam/2) * lam**-b / (1+(lam/c)**d)**e
    out["CE_HI"] = 7.5e-19 * math.exp(-.75*157807/T) / (1+math.sqrt(T/1e5))
    out["CE_HeII"] = 5.54e-17 * T**-.397 * math.exp(-.75*631515/T) / (1+math.sqrt(T/1e5))
    return out


class TestCollisionalBudget(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.atomic = AtomicNetwork()
        cls.budget = CollisionalBudget(cls.atomic)
        cls.Y = np.linspace(.001, .021, 21)
        cls.Y /= cls.atomic.A @ cls.Y

    def assert_relative(self, actual, expected, tolerance=8e-14):
        self.assertLessEqual(abs(actual-expected), tolerance * abs(expected))

    def test_independent_cgs_to_si_coefficients(self):
        for T in (1e4, 2e4, 1e5, 5e5):
            values, flags = self.budget.coefficients(T)
            for name, cgs in cgs_reference(T).items():
                self.assert_relative(values[name], cgs * (1e-6 if name.startswith("CI") else 1e-13))
                self.assertTrue(flags[name]["in_validated_domain"])

    def test_independent_wolfram_high_precision_fixture(self):
        evidence = Path(__file__).resolve().parents[1] / "evidence/WOLFRAM_CHECK.json"
        fixture = json.loads(evidence.read_text())["parsed"]["HG97_CI_m3_s_reference"]
        self.assertEqual([r["T_K"] for r in fixture], [10000, 14177, 100000])
        for row in fixture:
            values, _ = self.budget.coefficients(row["T_K"])
            for channel in ("HI", "HeI", "HeII"):
                reference = float(re.sub(r"`[^*]*", "", row[channel]).replace("*^", "e"))
                self.assert_relative(values["CI_"+channel], reference)

    def test_native_channel_conservation_charge_and_energy(self):
        original = self.Y.copy()
        r = self.budget.evaluate(self.Y, 2e4, .25)
        np.testing.assert_array_equal(self.Y, original)
        self.assertEqual(len(r["ci_channels"]), 7)
        self.assertEqual(len(r["ce_channels"]), 5)
        for c in r["ci_channels"]:
            dY = np.zeros(21)
            dY[c["lower_index"]] = -c["event_rate_per_baryon_s"]
            dY[c["upper_index"]] = c["event_rate_per_baryon_s"]
            self.assertEqual(dY.sum(), 0)
            self.assertLessEqual(abs(self.atomic.A @ dY),
                                 3e-15 * self.atomic.A[c["lower_index"]] * c["event_rate_per_baryon_s"])
            self.assert_relative(self.atomic.q @ dY, c["event_rate_per_baryon_s"])
            self.assert_relative(.25 * (self.atomic.ionization_energy_J @ dY), c["binding_W_m3"])
            self.assertEqual(c["kinetic_W_m3"] + c["binding_W_m3"], 0)
        for indices in self.atomic.isotope_groups.values():
            scale = max(abs(r["dY_dt"][list(indices)]).max(), 1e-300)
            self.assertLessEqual(abs(r["dY_dt"][list(indices)].sum()), 3e-15*scale)
        self.assert_relative(self.atomic.q @ r["dY_dt"], r["particle_source"])
        self.assert_relative((1+self.atomic.q) @ r["dY_dt"], r["particle_source"])
        self.assertEqual(r["ci_kinetic_W_m3"] + r["ci_binding_W_m3"], 0)
        self.assert_relative(r["ci_binding_gradient_W_m3"], r["ci_binding_W_m3"])
        self.assertEqual(r["ci_escape_W_m3"], 0)

    def test_volume_power_against_cgs_densities(self):
        T, nb = 2e4, .25
        r = self.budget.evaluate(self.Y, T, nb)
        reference = cgs_reference(T)
        ne_cm3 = nb * (self.atomic.q @ self.Y) / 1e6
        ci_erg_cm3_s = 0.
        for c in r["ci_channels"]:
            target_cm3 = nb * self.Y[c["lower_index"]] / 1e6
            ci_erg_cm3_s += ne_cm3 * target_cm3 * reference[c["process"]] * c["chi_J"] * 1e7
        ce_erg_cm3_s = sum(ne_cm3 * nb*self.Y[c["target_index"]]/1e6 * reference[c["process"]]
                          for c in r["ce_channels"])
        self.assert_relative(-r["ci_kinetic_W_m3"], ci_erg_cm3_s * .1)
        self.assert_relative(r["ce_cooling_W_m3"], ce_erg_cm3_s * .1)

    def test_shared_electronic_rates_and_canonical_energy_hybrid(self):
        modified = copy.copy(self.atomic)
        modified.ionization_energy_J = self.atomic.ionization_energy_J.copy()
        modified.ionization_energy_J[1:3] *= 1.013
        r = CollisionalBudget(modified).evaluate(self.Y, 2e4, .25)
        hydrogen = [c for c in r["ci_channels"] if c["process"] == "CI_HI"]
        self.assertEqual(len({c["coefficient_m3_s"] for c in hydrogen}), 1)
        self.assertNotEqual(hydrogen[0]["chi_J"], hydrogen[1]["chi_J"])
        self.assertNotEqual(hydrogen[0]["chi_J"], KB_J_K * 157807)
        for name in ("CI_HeI", "CI_HeII"):
            self.assertEqual(len({c["coefficient_m3_s"] for c in r["ci_channels"] if c["process"] == name}), 1)
        self.assert_relative(r["ci_binding_gradient_W_m3"], r["ci_binding_W_m3"])

    def test_domain_errors_and_explicit_continuation_flags(self):
        for T in (1050., 5000., 9999., 500001., 1e9):
            with self.assertRaises(FitDomainError):
                self.budget.evaluate(self.Y, T, .25)
        values, flags = self.budget.coefficients(1050., allow_extrapolation=True)
        self.assertGreater(values["CI_HI"], 0)
        self.assertFalse(flags["CI_HI"]["underflow_to_zero"])
        self.assertTrue(all(v["extrapolated"] for v in flags.values()))
        _, flags = self.budget.coefficients(5000., allow_extrapolation=True)
        self.assertFalse(flags["CI_HI"]["in_validated_domain"])
        self.assertTrue(flags["CE_HI"]["in_validated_domain"])
        _, flags = self.budget.coefficients(1e9, allow_extrapolation=True)
        self.assertTrue(flags["CI_HeII"]["in_validated_domain"])
        self.assertFalse(flags["CE_HeII"]["in_validated_domain"])

    def test_extreme_temperatures_underflow_is_not_source_support(self):
        for T in (np.nextafter(0., 1.), 1., 100., 1050., 1e9, np.finfo(float).max):
            values, flags = self.budget.coefficients(T, allow_extrapolation=True)
            self.assertTrue(all(math.isfinite(v) and v >= 0 for v in values.values()))
            for key, value in values.items():
                self.assertEqual(flags[key]["underflow_to_zero"], value == 0)
        r = self.budget.evaluate(self.Y, 100., .25, allow_extrapolation=True)
        self.assertTrue(r["validity"]["CI_HI"]["underflow_to_zero"])
        self.assertFalse(r["validity"]["CI_HI"]["in_validated_domain"])

    def test_invalid_input_rejection(self):
        for T in (0., -1., float("nan"), float("inf"), [1e4], 1e4+0j, True):
            with self.assertRaises(ValueError):
                self.budget.evaluate(self.Y, T, .25, allow_extrapolation=True)
        for nb in (-1., float("nan"), float("inf"), [.25], True):
            with self.assertRaises(ValueError):
                self.budget.evaluate(self.Y, 1e4, nb)
        for bad in (-1e-100, float("nan"), float("inf")):
            Y = self.Y.copy(); Y[3] = bad
            with self.assertRaises(ValueError):
                self.budget.evaluate(Y, 1e4, .25)
        for Y in (self.Y[:-1], self.Y.reshape(3, 7), self.Y.astype(complex)):
            with self.assertRaises(ValueError):
                self.budget.evaluate(Y, 1e4, .25)
        with self.assertRaises(ValueError):
            self.budget.coefficients(1e4, allow_extrapolation="yes")

    def test_unavailable_channels_are_not_certified_zero(self):
        r = self.budget.evaluate(self.Y, 1e4, .25)
        for name in ("CI_LiI", "CI_LiII", "CI_LiIII", "CE_HeI"):
            self.assertFalse(r["unavailable"][name]["available"])
            self.assertIsNone(r["unavailable"][name]["coefficient"])
        np.testing.assert_array_equal(np.flatnonzero(r["ci_unavailable_mask"]), [13, 14, 15, 17, 18, 19])
        np.testing.assert_array_equal(np.flatnonzero(r["ce_unavailable_mask"]), [7, 10, 13, 14, 15, 17, 18, 19])
        self.assertFalse(np.any(r["ci_available_mask"] & r["ci_unavailable_mask"]))
        self.assertTrue(np.all(r["dY_dt"][13:] == 0))  # Excluded Li source, explicitly masked above.

    def test_zero_density_and_population_limits_and_bad_parent(self):
        for Y, nb in ((self.Y, 0.), (np.zeros(21), .25)):
            r = self.budget.evaluate(Y, 1e4, nb)
            self.assertTrue(np.all(r["dY_dt"] == 0))
            self.assertEqual(r["particle_source"], 0)
            self.assertEqual(r["ce_cooling_W_m3"], 0)
            self.assertEqual(r["ci_binding_W_m3"], 0)
            self.assertTrue(r["all_included_fits_in_domain"])
        bad = copy.copy(self.atomic)
        bad.isotope_groups = dict(self.atomic.isotope_groups, D=(4, 3))
        with self.assertRaises(ValueError):
            CollisionalBudget(bad)
        bad = copy.copy(self.atomic)
        bad.ionization_energy_J = self.atomic.ionization_energy_J.copy()
        bad.ionization_energy_J[2] = bad.ionization_energy_J[1]
        with self.assertRaises(ValueError):
            CollisionalBudget(bad)


if __name__ == "__main__":
    unittest.main(verbosity=2)
