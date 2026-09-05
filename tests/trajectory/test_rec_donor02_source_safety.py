"""Bounded REC-DONOR-02 checks. Manufactured inputs are never admitted data."""
from __future__ import annotations

from dataclasses import FrozenInstanceError, replace
from fractions import Fraction as Q
import importlib.util
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location(
    "rec_donor01_fixture", ROOT / "tests/trajectory/test_rec_donor01_typed_physical_source_red.py"
)
legacy = importlib.util.module_from_spec(spec)
spec.loader.exec_module(legacy)


class TestRecDonor02SourceSafety(unittest.TestCase):
    def setUp(self):
        self.case = legacy.TestRecDonor01TypedPhysicalSourceRed()

    def module(self):
        return self.case._module()

    def test_control_threshold_fixture_is_equilibrium_null(self):
        eta, kappa, f = Q(1, 4), Q(3, 4), Q(1, 2)
        self.assertEqual(eta * (1 + f) - kappa * f, 0)
        self.assertEqual(eta * (1 + 2) - kappa * 2, Q(-3, 4))
        self.assertEqual((1 + f) * Q(1, 2) - f * Q(-1, 4)
                         - (kappa - eta) * Q(1, 8), Q(13, 16))

    def test_control_deposition_requires_operator_values(self):
        # Two number-preserving maps acting on the same two packet channels.
        rates = (Q(1), Q(4))
        B1 = ((Q(1), Q(0)), (Q(0), Q(1)))
        B2 = ((Q(0), Q(1)), (Q(1), Q(0)))
        def apply(B):
            return tuple(sum(b * r for b, r in zip(row, rates)) for row in B)
        self.assertNotEqual(apply(B1), apply(B2))
        self.assertEqual(sum(apply(B1)), sum(apply(B2)))

    def test_factory_and_no_physical_admission(self):
        m = self.module()
        source = self.case._source(m)
        with self.assertRaises(m.SourceContractError):
            type(source)()
        self.assertFalse(source.physical_authority_admitted)
        self.assertFalse(source.provider_export_authorized)
        self.assertEqual(source.provenance.verification_status, "DECLARED_NOT_AUTHENTICATED")

    def test_input_types_units_and_support_fail_closed(self):
        m = self.module()
        for bad in (True, "0.25", -1.0, float("nan"), float("inf")):
            with self.subTest(bad=repr(bad)), self.assertRaises(m.SourceContractError):
                self.case._source(m, emission=bad)
        for changes in ({"coordinate": "eV"}, {"lower_j": -1.0},
                        {"upper_j": 1.0e-18}, {"lower_inclusive": 1}):
            with self.subTest(changes=changes), self.assertRaises(m.SourceContractError):
                replace(self.case._support(m), **changes)
        for bad in (True, -1.0, float("nan")):
            with self.assertRaises(m.SourceContractError):
                self.case._source(m).action(energy_j=bad, occupation=0.0)

    def test_nested_metadata_is_immutable(self):
        m = self.module()
        p = self.case._provenance(m)
        with self.assertRaises(TypeError):
            p.dependency_sha256["Alpha_inf.dat"] = "0" * 64
        source = self.case._source(m)
        with self.assertRaises((FrozenInstanceError, AttributeError)):
            source.emission_s_inv = 2.0
        with self.assertRaises(m.SourceContractError):
            replace(p, source_path="../hydrogen.c")
        with self.assertRaises(m.SourceContractError):
            replace(p, source_blob_sha="Z" * 40)

    def test_identity_binds_rates_support_event_and_jvp(self):
        m = self.module()
        source = self.case._source(m)
        self.assertNotEqual(source.semantic_sha256, self.case._source(m, emission=0.5).semantic_sha256)
        self.assertNotEqual(source.semantic_sha256, self.case._source(
            m, trajectory=replace(self.case._trajectory(m), event_surface_id="RED_FACE_V_X_ZERO")
        ).semantic_sha256)
        a = self.case._source(m, emission=0.0)
        b = self.case._source(m, emission=-0.0)
        self.assertEqual(a.semantic_sha256, b.semantic_sha256)
        self.assertEqual(source.semantic_sha256, self.case._source(m).semantic_sha256)

    def test_overflow_is_not_silently_admitted(self):
        m = self.module()
        source = self.case._source(m, emission=1.0e308, absorption=0.0)
        with self.assertRaises(m.SourceArithmeticError):
            source.action(energy_j=2.25e-18, occupation=1.0e308)
        self.assertEqual(self.case._source(m, 0.0, 0.0).action(
            energy_j=2.25e-18, occupation=1.0e308), 0.0)
        with self.assertRaises(m.SourceContractError):
            self.case._source(m).jvp(energy_j=2.25e-18, occupation=0.5,
                d_occupation=float("nan"), d_emission_s_inv=0.0, d_absorption_s_inv=0.0)

    def test_equilibrium_degenerate_branches_are_distinguished(self):
        m = self.module()
        with self.assertRaises(m.NoFiniteEquilibriumError):
            self.case._source(m, 0.5, 0.5).equilibrium_occupation()
        with self.assertRaises(m.NonUniqueEquilibriumError):
            self.case._source(m, 0.0, 0.0).equilibrium_occupation()
        self.assertEqual(self.case._source(m, 0.0, 0.5).equilibrium_occupation(), 0.0)

    def test_moment_map_binding_cannot_be_reused_for_another_source(self):
        m = self.module()
        source = self.case._source(m)
        binding = m.MomentMapBinding(target=m.G_ANGULAR_ENERGY,
            source_semantic_sha256="0" * 64, radial_weight_sha256="8" * 64,
            angular_measure_sha256="9" * 64, closure_status=m.EXPLICIT_PROJECTION_ONLY)
        with self.assertRaises(m.MomentMapBindingRequiredError):
            source.bind_integrated_target(target=m.G_ANGULAR_ENERGY, moment_map=binding)
        bound = source.bind_integrated_target(target=m.G_ANGULAR_ENERGY,
            moment_map=replace(binding, source_semantic_sha256=source.semantic_sha256))
        self.assertFalse(bound.numerically_executed)

    def test_nonlocal_linear_probe_has_no_hyrec_physics_claim(self):
        m = self.module()
        kernel = self.case._kernel(m)
        self.assertEqual(kernel.evaluation_scope, "MANUFACTURED_LINEAR_PACKET_PROBE")
        self.assertFalse(kernel.physical_authority_admitted)
        self.assertEqual(kernel.evaluate_packet_rate(companion_occupation=(0.5, 1.0)), 4.0)
        for occupations in ((0.5,), (-1.0, 0.0), (float("nan"), 1.0)):
            with self.assertRaises(m.SourceContractError):
                kernel.evaluate_packet_rate(companion_occupation=occupations)

    def test_deposition_hash_declaration_is_not_execution(self):
        m = self.module()
        binding = m.PacketDepositionBinding(n_H_m3=1.0e8, phase_space_measure_si=2.0,
            deposition_matrix_sha256="5" * 64, normalization_sha256="6" * 64,
            application_count=1)
        with self.assertRaisesRegex(m.DepositionAuthorityError, "UNRESOLVED_DEPOSITION_OPERATOR"):
            m.deposit_packet_rate(kernel=self.case._kernel(m), deposition=binding,
                                  companion_occupation=(0.5, 1.0))
        for count in (0, 2, True, 1.0):
            with self.assertRaises(m.DepositionAuthorityError):
                replace(binding, application_count=count)


if __name__ == "__main__":
    unittest.main(verbosity=2)
