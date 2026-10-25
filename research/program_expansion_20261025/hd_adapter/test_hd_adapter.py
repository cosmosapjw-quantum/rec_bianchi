"""Targeted tests of the new pinned source adapter, not the old compiler suite."""
from dataclasses import FrozenInstanceError
from decimal import Decimal, localcontext
from fractions import Fraction
import hashlib
import math
import os
from pathlib import Path
import sys
import unittest

import lamda_hd as hd


class PinnedHDTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = Path(os.environ["REC_HD_SOURCE"]).read_bytes()
        cls.data = hd.parse_hd(cls.raw)

    def test_source_bytes(self):
        self.assertEqual(len(self.raw), 2289)
        self.assertEqual(hashlib.sha256(self.raw).hexdigest(), hd.SOURCE_SHA256)
        self.assertEqual(self.data.source_roundtrip(), self.raw)

    def test_shape(self):
        self.assertEqual((len(self.data.levels), len(self.data.radiative_lines)), (9, 8))
        self.assertEqual(tuple(c.id for c in self.data.colliders), (2, 3))
        self.assertEqual(sum(len(c.downward_pairs) for c in self.data.colliders), 18)
        self.assertEqual(sum(len(p.downward_cm3_per_s) for c in self.data.colliders for p in c.downward_pairs), 54)

    def test_immutable(self):
        with self.assertRaises(FrozenInstanceError):
            self.data.levels[0].J = 9
        self.assertIsInstance(self.data.colliders, tuple)
        self.assertIsInstance(self.data.colliders[0].downward_pairs, tuple)

    def test_all_literal_tokens(self):
        original_lines = self.raw.decode("ascii").splitlines()
        records = list(self.data.levels) + list(self.data.radiative_lines)
        records += [p for c in self.data.colliders for p in c.downward_pairs]
        for record in records:
            with self.subTest(line=record.source_line):
                self.assertEqual(record.source_tokens, tuple(original_lines[record.source_line - 1].split()))
        self.assertEqual(self.data.radiative_lines[0].A_per_s.literal, "5.442E-08")
        self.assertEqual(self.data.colliders[0].downward_pairs[0].downward_cm3_per_s[0].literal, "2.2e-11")

    def test_exact_SI_units_against_rationals(self):
        for level in self.data.levels:
            with self.subTest(level=level.id):
                independent = Fraction(level.energy_cm_inverse.literal) * Fraction("6.62607015e-34") * 299792458 * 100
                self.assertEqual(Fraction(level.energy_J), independent)
        for line in self.data.radiative_lines:
            self.assertEqual(Fraction(line.frequency_Hz), Fraction(line.frequency_GHz.literal) * 10**9)
        for collider in self.data.colliders:
            for pair in collider.downward_pairs:
                for index, temperature in enumerate((50, 100, 200)):
                    self.assertEqual(Fraction(self.data.downward_rate(collider.id, pair.upper, pair.lower, temperature)),
                                     Fraction(pair.downward_cm3_per_s[index].literal) / 10**6)

    def test_frequency_precision_against_rationals(self):
        for line in self.data.radiative_lines:
            delta = Fraction(self.data.level(line.upper).energy_cm_inverse.literal) - Fraction(self.data.level(line.lower).energy_cm_inverse.literal)
            independent = abs(299792458 * 100 * delta - 10**9 * Fraction(line.frequency_GHz.literal))
            self.assertEqual(Fraction(hd.line_frequency_gap_Hz(self.data, line.id)), independent)
            self.assertLessEqual(independent, 35)

    def test_level_energy_reference(self):
        with localcontext() as context:
            context.prec = 70
            actual = self.data.level(2).energy_J / hd.KB
        self.assertAlmostEqual(float(actual), 128.37908482940912, places=12)
        self.assertEqual(self.data.line(1).A_per_s.value, Decimal("5.442e-8"))

    def test_upward_reference(self):
        self.assertEqual(self.data.downward_rate(2, 2, 1, 100), Decimal("2.7e-17"))
        actual = self.data.upward_rate(2, 1, 2, 100)
        self.assertLessEqual(abs(actual - 2.243580917662442e-17) / abs(actual), hd.ROUNDING_TOLERANCE)

    def test_detailed_balance_decimal_independent(self):
        # High-precision Decimal evaluates the complete relation separately.
        with localcontext() as context:
            context.prec = 70
            for collider in self.data.colliders:
                for pair in collider.downward_pairs:
                    u, l = self.data.level(pair.upper), self.data.level(pair.lower)
                    for T in hd.TEMPERATURES_K:
                        expected = (self.data.downward_rate(collider.id, pair.upper, pair.lower, T)
                                    * u.degeneracy.value / l.degeneracy.value
                                    * (-(u.energy_J - l.energy_J) / (hd.KB * T)).exp())
                        actual = self.data.upward_rate(collider.id, pair.lower, pair.upper, T)
                        self.assertLessEqual(abs(actual - float(expected)) / (abs(actual) + abs(float(expected))), hd.ROUNDING_TOLERANCE)

    def test_p_o_are_distinct(self):
        self.assertNotEqual(self.data.downward_rate(2, 3, 1, 100), self.data.downward_rate(3, 3, 1, 100))
        self.assertEqual(self.data.collider(2).name, "para-H2")
        self.assertEqual(self.data.collider(3).name, "ortho-H2")
        self.assertNotEqual(self.data.collider(2).source_reference, self.data.collider(3).source_reference)

    def test_missing_pair_not_zero(self):
        with self.assertRaises(hd.UnsupportedDomain):
            self.data.downward_rate(2, 4, 1, 100)
        with self.assertRaises(hd.UnsupportedDomain):
            self.data.upward_rate(2, 1, 4, 100)

    def test_temperature_domain(self):
        for T in (0, 49, 75, 150, 201, -1, "100.00000000000001", "NaN", "Infinity", True):
            with self.subTest(temperature=T), self.assertRaises(hd.AdapterError):
                self.data.downward_rate(2, 2, 1, T)
        self.assertEqual(self.data.downward_rate(2, 2, 1, "100.0"), Decimal("2.7e-17"))

    def test_no_collider_mix(self):
        for collider in (1, 4, "2", "H2", "mixture", (2, 3), {2: 0.25, 3: 0.75}, True):
            with self.subTest(collider=str(collider)), self.assertRaises(hd.UnsupportedDomain):
                self.data.downward_rate(collider, 2, 1, 100)

    def test_bad_source_rejected(self):
        for changed in (self.raw[:-1], self.raw + b"\n", self.raw.replace(b"5.442E-08", b"5.443E-08", 1)):
            with self.assertRaises(hd.SourceIdentityError):
                hd.parse_hd(changed)
        with self.assertRaises(hd.SourceIdentityError):
            hd.parse_hd(self.raw.decode("ascii"))

    def test_grammar_corruption_rejected(self):
        changes = [
            self.raw.replace(b"           9\n", b"           8\n", 1),
            self.raw.replace(b"0.000000000   1.0", b"NaN           1.0", 1),
            self.raw.replace(b"89.227931611   3.0", b"89.227931611   4.0", 1),
            self.raw.replace(b"HD-pH2", b"HD-oH2", 1),
            self.raw.replace(b"   50.0   100.0  200.0", b"   50.0   100.0  201.0", 1),
            self.raw.replace(b"1\t2\t1\t2.2e-11", b"1\t20\t1\t2.2e-11", 1),
            self.raw.replace(b"2.2e-11", b"-2.2e-11", 1),
            self.raw + b"unparsed\n",
        ]
        for changed in changes:
            with self.subTest(changed_sha=hashlib.sha256(changed).hexdigest()), self.assertRaises(hd.AdapterError):
                hd._parse_unqualified(changed)

    def test_premature_EOF(self):
        with self.assertRaises(hd.SourceFormatError):
            hd._parse_unqualified(self.raw[:1800])

    def test_Einstein_relations(self):
        for line in self.data.radiative_lines:
            B_ul, B_lu = hd.einstein_B(self.data, line.id)
            nu = float(line.frequency_Hz)
            gu = float(self.data.level(line.upper).degeneracy.value)
            gl = float(self.data.level(line.lower).degeneracy.value)
            self.assertLessEqual(abs(gl * B_lu - gu * B_ul) / (abs(gl * B_lu) + abs(gu * B_ul)), hd.ROUNDING_TOLERANCE)
            expected = 2 * float(hd.H) * nu ** 3 / float(hd.C) ** 2
            self.assertLessEqual(abs(float(line.A_per_s.value) / B_ul / expected - 1), hd.ROUNDING_TOLERANCE)

    def test_Kirchhoff(self):
        for line in self.data.radiative_lines:
            for T in (50, 100, 200):
                result = hd.thermal_line(self.data, line.id, T)
                self.assertGreater(result["alpha_nu_per_m"], 0)
                self.assertFalse(result["underflow"])
                self.assertLessEqual(result["normalized_Kirchhoff_residual"], hd.ROUNDING_TOLERANCE)
                # General population helper agrees with thermal stable helper.
                direct = hd.line_coefficients(self.data, line.id, 1, result["n_upper_per_m3"], 1)
                self.assertLessEqual(abs(direct["alpha_nu_per_m"] - result["alpha_nu_per_m"]) / (abs(direct["alpha_nu_per_m"]) + abs(result["alpha_nu_per_m"])), hd.ROUNDING_TOLERANCE)

    def test_inversion_sign_preserved(self):
        result = hd.line_coefficients(self.data, 1, 1, 4, 1)
        self.assertLess(result["alpha_nu_per_m"], 0)
        self.assertTrue(result["population_inversion"])
        self.assertGreater(result["j_nu_J_s_m3_sr_Hz"], 0)

    def test_analytic_zero(self):
        result = hd.thermal_line(self.data, 1, 100, 0, 1)
        self.assertEqual(result["classification"], "ANALYTIC_ZERO")
        self.assertIsNone(result["normalized_Kirchhoff_residual"])
        self.assertFalse(result["underflow"])

    def test_bad_radiative_inputs(self):
        for value in ("NaN", "Infinity", -1, True, "1e-1000", "1e1000"):
            for call in (lambda: hd.thermal_line(self.data, 1, 100, value),
                         lambda: hd.thermal_line(self.data, 1, 100, 1, value),
                         lambda: hd.line_coefficients(self.data, 1, value, 1, 1),
                         lambda: hd.line_coefficients(self.data, 1, 1, value, 1),
                         lambda: hd.line_coefficients(self.data, 1, 1, 1, value)):
                with self.subTest(value=value), self.assertRaises(hd.AdapterError):
                    call()
        for T in ("1e-1000", "1e1000", "NaN", 0, -1):
            with self.assertRaises(hd.AdapterError):
                hd.thermal_line(self.data, 1, T)

    def test_underflow_is_not_analytic_zero(self):
        with self.assertRaises(hd.NumericalDomainError):
            hd.thermal_line(self.data, 1, 100, "1e-1000", 1)
        with self.assertRaises(hd.NumericalDomainError):
            hd.thermal_line(self.data, 1, 100, 1, "1e-1000")
        with self.assertRaises(hd.NumericalDomainError):
            hd.line_coefficients(self.data, 1, 1, "1e-310", 1)

        with self.assertRaises(hd.NumericalDomainError):
            hd.line_coefficients(self.data, 1, "1e-320", 0, 1)
        with self.assertRaises(hd.NumericalDomainError):
            hd.thermal_line(self.data, 1, "1e-310")

    def test_WU_canonical_schema_reuse(self):
        species = hd.bind_wu_species(self.data, os.environ["REC_HD_WU_MODULE"])
        self.assertEqual(len(species), 9)
        self.assertEqual(len({row.key() for row in species}), 9)
        for row in species:
            self.assertEqual(row.composition, (((1, 1, "ground"), 1), ((1, 2, "ground"), 1)))
            self.assertEqual(row.charge, 0)
            self.assertEqual(row.pool, "material")
            self.assertEqual(row.baryon_count(), 3)
            self.assertIn("v=UNSPECIFIED", row.state)

    def test_caller_decimal_context_does_not_change_rates(self):
        reference_up = self.data.upward_rate(2, 3, 4, 100)
        reference_B = hd.einstein_B(self.data, 3)
        reference_lte = hd.thermal_line(self.data, 3, 100)
        with localcontext() as context:
            context.prec = 4
            self.assertEqual(self.data.upward_rate(2, 3, 4, 100), reference_up)
            self.assertEqual(hd.einstein_B(self.data, 3), reference_B)
            self.assertEqual(hd.thermal_line(self.data, 3, 100), reference_lte)

    def test_failed_source_rows_remain_unqualified(self):
        self.assertEqual(hd.require_energy_frequency_bridge(self.data, 1).id, 1)
        for line_id in range(2, 9):
            self.assertEqual(hd.transition_qualification(self.data, line_id)["status"], "SOURCE_DISCREPANCY_UNQUALIFIED")
            with self.assertRaises(hd.UnsupportedDomain):
                hd.require_energy_frequency_bridge(self.data, line_id)

    def test_unknown_state_and_reference(self):
        for value in (0, 10, "1", True):
            with self.assertRaises(hd.UnsupportedDomain):
                self.data.level(value)
        for value in (0, 9, "1", True):
            with self.assertRaises(hd.UnsupportedDomain):
                self.data.line(value)


if __name__ == "__main__":
    unittest.main(verbosity=2)
