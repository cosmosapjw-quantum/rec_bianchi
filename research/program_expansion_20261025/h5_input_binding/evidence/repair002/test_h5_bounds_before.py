"""Analytic controls plus actual 313-query binding/refusal checks.

Manufactured input proofs in temporary directories test the consumer and its
scope guards; they never qualify the actual source's physical uncertainty.
"""
from __future__ import annotations
import copy
from decimal import Decimal, localcontext
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

UNIT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(UNIT / "code"))
from h5_bounds import (BoundInputError, evaluate_candidate, evaluate_files,
                       decimal_bound_token, exp_upper, frozen_box_upper, gronwall_upper,
                       interpolation_upper, rational, validate_context)


def toy_context():
    return {"schema": "REC_H5_FIXED_QUERY_CONTEXT_V1",
            "source_identity": {"query_count": 1, "active_endpoint_slots": 2,
                                "prefix": 2, "history_sha256": "MANUFACTURED_ONLY"},
            "native_reference": "MANUFACTURED_G=x+eta^2",
            "queries": [{"incoming_index": 0, "source_index": 1, "cell": 0,
                         "eta_left_hex": (0.0).hex(), "eta_right_hex": (1.0).hex(),
                         "query_hex": (0.5).hex(), "sample_left_hex": (0.0).hex(),
                         "sample_right_hex": (1.0).hex(),
                         "nominal_incoming_hex": (0.5).hex(),
                         "geometric_alpha_exact": "1/2",
                         "anchor_representation_radius_exact": "0"}]}


def scalar(x):
    return {"upper": str(x), "proof_refs": ["manufactured"]}


def toy_packet(context, proof):
    return {"schema": "REC_H5_BOUND_INPUT_PACKET_V1",
            "source_identity": copy.deepcopy(context["source_identity"]),
            "clock": "eta=ln(a)", "native_reference": context["native_reference"],
            "query_policy": "fixed_represented_binary64_queries",
            "enclosure_kind": "continuous_source_ode_tube",
            "proof_artifacts": [{"id": "manufactured", "path": proof.name,
                                 "sha256": hashlib.sha256(proof.read_bytes()).hexdigest()}],
            "state_enclosure": {
                "norm": {"kind": "fixed_weighted_infinity", "coordinates": [
                    {"name": "x", "unit": "1", "scale": "1"}]},
                "reconstruction": "continuous_piecewise_absolutely_continuous",
                "bound_support": "whole_eta_domain_ess_sup",
                "tube_definition": "uniform_open_scaled_radius_about_reconstruction",
                "state_proof_refs": ["manufactured"],
                "orientation": 1, "eta_origin": "0", "eta_domain": ["0", "1"],
                "initial_error": scalar(0), "defect": scalar(0),
                "stability_L": scalar(0), "tube_radius": scalar(1),
                "model_discrepancy": scalar(0)},
            "query_bounds": [{"incoming_index": 0, "source_index": 1, "cell": 0,
                              "curvature_support": "ess_sup_whole_cell", "regularity": "C2",
                              "K_left": scalar(1), "K_right": scalar(1),
                              "reference_left": scalar(0), "reference_right": scalar(0),
                              "endpoint_representation_left": scalar(0),
                              "endpoint_representation_right": scalar(0),
                              "curvature_M2": scalar(2)}]}


class ExactArithmeticControls(unittest.TestCase):
    def test_quadratic_midpoint_attains_interpolation_bound(self):
        # y=eta^2, [0,1], q=1/2: linear interpolant is 1/2, y(q)=1/4.
        result = interpolation_upper(0, F(1, 2), 1, 0, 0, 2)
        self.assertEqual(result, F(1, 4))

    def test_zero_curvature_and_endpoints(self):
        self.assertEqual(interpolation_upper(0, F(1, 3), 1, 0, 0, 0), 0)
        self.assertEqual(interpolation_upper(0, 0, 1, 2, 3, 5), 2)
        self.assertEqual(interpolation_upper(0, 1, 1, 2, 3, 5), 3)

    def test_nonuniform_cell_weight_and_anchor(self):
        self.assertEqual(interpolation_upper(2, 3, 6, 1, 3, 2, F(1, 7)), F(65, 14))

    def test_zero_stability_limit(self):
        self.assertEqual(gronwall_upper(F(1, 5), F(2, 7), 0, 3), F(37, 35))

    def test_exponential_bound_against_independent_decimal(self):
        with localcontext() as ctx:
            ctx.prec = 100
            for x in (F(0), F(1, 2), F(1), F(5), F(16), F(64)):
                upper = exp_upper(x)
                reference = (Decimal(x.numerator) / Decimal(x.denominator)).exp()
                ref_rational = F(reference)
                self.assertGreaterEqual(upper, ref_rational)
                self.assertLess((upper - ref_rational) / ref_rational, F("1e-50"))

    def test_positive_stability_constant_defect(self):
        upper = gronwall_upper(F(1, 2), F(3, 4), 2, F(1, 3))
        with localcontext() as ctx:
            ctx.prec = 100
            reference = Decimal("0.875") * (Decimal(2) / 3).exp() - Decimal("0.375")
        self.assertGreaterEqual(upper, F(reference))

    def test_negative_duration_rejected(self):
        with self.assertRaisesRegex(BoundInputError, "NEGATIVE_BOUND:path_length"):
            gronwall_upper(0, 1, 0, -1)

    def test_large_exponent_is_unsupported(self):
        with self.assertRaisesRegex(BoundInputError, "EXPONENT_RANGE_UNSUPPORTED"):
            exp_upper(F(65))

    def test_invalid_or_implicit_float_bounds_rejected(self):
        for value in (float("nan"), 0.1, "NaN", "Infinity", "1/0", True):
            with self.subTest(value=value):
                with self.assertRaises(BoundInputError):
                    rational(value)

    def test_subnormal_scale_is_not_clamped(self):
        tiny = F("1e-1000")
        self.assertEqual(gronwall_upper(tiny, 0, 0, 1), tiny)

    def test_entrywise_interval_propagation_exact(self):
        result = frozen_box_upper([["-2", "1"], ["0", "-1/2"]],
                                  [["-1", "3"], ["0", "1/2"]], ["1/4", "1/3"])
        self.assertEqual(result, [F(3, 2), F(1, 6)])

    def test_interval_shape_and_order_rejected(self):
        for lo, hi in (([[1]], [[0]]), ([[0, 1]], [[1]])):
            with self.assertRaises(BoundInputError):
                frozen_box_upper(lo, hi, [1])


class ConditionalConsumerControls(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        proof = self.root / "manufactured.txt"
        proof.write_text("Manufactured scalar x'=0, x=0, G=x+eta^2, e0=d=L=0, K=1, M2=2.\n")
        self.context = toy_context()
        self.packet = toy_packet(self.context, proof)

    def tearDown(self):
        self.temp.cleanup()

    def evaluate(self):
        return evaluate_candidate(self.context, self.packet, proof_root=self.root)

    def test_quadratic_candidate_keeps_physical_admission_null(self):
        result = self.evaluate()
        self.assertEqual([F(x) for x in result["conditional_epsilon"]], [F(1, 4)])
        self.assertIsNone(result["physical_epsilon"])
        self.assertIsNone(result["physical_outgoing_bound"])
        self.assertEqual(result["status"], "CONDITIONAL_BOUND_CANDIDATE_REVIEW_REQUIRED")

    def test_backward_orientation(self):
        self.packet["state_enclosure"].update(orientation=-1, eta_origin="1")
        self.assertEqual([F(x) for x in self.evaluate()["conditional_epsilon"]], [F(1, 4)])

    def test_forward_negative_path_rejected(self):
        self.packet["state_enclosure"]["eta_origin"] = "1"
        with self.assertRaisesRegex(BoundInputError, "ENDPOINT_BEFORE_ORIENTED_ORIGIN"):
            self.evaluate()

    def test_tube_bootstrap_violation(self):
        self.packet["state_enclosure"]["initial_error"] = scalar(1)
        with self.assertRaisesRegex(BoundInputError, "TUBE_BOOTSTRAP_FAILED"):
            self.evaluate()

    def test_tube_end_growth_is_checked(self):
        self.packet["state_enclosure"]["defect"] = scalar(1)
        self.packet["state_enclosure"]["tube_radius"] = scalar("0.9")
        with self.assertRaisesRegex(BoundInputError, "TUBE_BOOTSTRAP_FAILED"):
            self.evaluate()

    def test_sampled_defect_cannot_be_used(self):
        self.packet["state_enclosure"]["bound_support"] = "sampled_residual_nodes"
        with self.assertRaisesRegex(BoundInputError, "SAMPLED_BOUND_NOT_CONTINUOUS"):
            self.evaluate()

    def test_sampled_curvature_cannot_be_used(self):
        self.packet["query_bounds"][0]["curvature_support"] = "second_finite_difference"
        with self.assertRaisesRegex(BoundInputError, "CURVATURE_NOT_WHOLE_CELL"):
            self.evaluate()

    def test_inverse_certificate_rho_is_not_a_tube(self):
        self.packet["enclosure_kind"] = "represented_matrix_inverse_certificate"
        with self.assertRaisesRegex(BoundInputError, "WRONG_DEFECT_OR_TUBE_SEMANTICS"):
            self.evaluate()

    def test_source_reference_clock_and_query_policy(self):
        for key, value, error in (("clock", "proper_time_seconds", "CLOCK_MISMATCH"),
                                  ("native_reference", "changed_reference", "NATIVE_REFERENCE_MISMATCH"),
                                  ("query_policy", "retimed_queries", "QUERY_RETEMING")):
            with self.subTest(key=key):
                original = self.packet[key]
                self.packet[key] = value
                with self.assertRaisesRegex(BoundInputError, error):
                    self.evaluate()
                self.packet[key] = original

    def test_wrong_source_identity(self):
        self.packet["source_identity"]["history_sha256"] = "another_cosmology"
        with self.assertRaisesRegex(BoundInputError, "SOURCE_IDENTITY_MISMATCH"):
            self.evaluate()

    def test_missing_domain_proof(self):
        self.packet["state_enclosure"]["state_proof_refs"] = []
        with self.assertRaisesRegex(BoundInputError, "STATE_DOMAIN_PROOF_REQUIRED"):
            self.evaluate()

    def test_changed_proof_bytes(self):
        (self.root / "manufactured.txt").write_text("Changed hypothesis\n")
        with self.assertRaisesRegex(BoundInputError, "PROOF_ARTIFACT_BYTE_MISMATCH"):
            self.evaluate()

    def test_missing_proof_field(self):
        self.packet["query_bounds"][0]["curvature_M2"]["proof_refs"] = []
        with self.assertRaisesRegex(BoundInputError, "BOUND_PROOF_REFERENCE_MISSING"):
            self.evaluate()

    def test_continuity_required(self):
        self.packet["state_enclosure"]["reconstruction"] = "piecewise_with_unbudgeted_jumps"
        with self.assertRaisesRegex(BoundInputError, "RECONSTRUCTION_CONTINUITY"):
            self.evaluate()

    def test_norm_and_cell_coverage(self):
        self.packet["state_enclosure"]["norm"]["coordinates"][0]["scale"] = "0"
        with self.assertRaisesRegex(BoundInputError, "POSITIVE_DIMENSIONAL_SCALE"):
            self.evaluate()
        self.packet["state_enclosure"]["norm"]["coordinates"][0]["scale"] = "1"
        self.packet["state_enclosure"]["eta_domain"] = ["0", "3/4"]
        with self.assertRaisesRegex(BoundInputError, "CELL_OUTSIDE_ENCLOSURE_DOMAIN"):
            self.evaluate()

    def test_wrong_query_identity(self):
        self.packet["query_bounds"][0]["source_index"] = 2
        with self.assertRaisesRegex(BoundInputError, "BOUND_QUERY_IDENTITY"):
            self.evaluate()

    def test_exact_anchor_is_added_once(self):
        self.context["queries"][0]["nominal_incoming_hex"] = (0.625).hex()
        self.context["queries"][0]["anchor_representation_radius_exact"] = "1/8"
        self.assertEqual([F(x) for x in self.evaluate()["conditional_epsilon"]], [F(3, 8)])

    def test_fraction_serialization_63_5_regression(self):
        self.packet["state_enclosure"]["initial_error"] = scalar(1)
        self.packet["state_enclosure"]["stability_L"] = scalar("63.5")
        self.packet["state_enclosure"]["tube_radius"] = scalar("1e30")
        result = self.evaluate()
        internal_upper = exp_upper(F(127, 2))
        self.assertGreaterEqual(F(result["state_error_upper_max"]), internal_upper)
        self.assertLess(len(result["state_error_upper_max"]), 90)
        self.assertLessEqual(F(result["tube_margin_lower"]), F("1e30") - internal_upper)
        self.assertIsNone(result["physical_epsilon"])

    def test_outward_decimal_serialization_extreme_scales(self):
        for x in (F(0), F(1, 3), F("1e-10000"), F("1e10000"), exp_upper(F(127, 2))):
            with self.subTest(binary_order=x.numerator.bit_length()-x.denominator.bit_length()):
                upper = decimal_bound_token(x, upper=True)
                lower = decimal_bound_token(x, upper=False)
                self.assertLess(len(upper), 90)
                self.assertGreaterEqual(F(upper), x)
                self.assertLessEqual(F(lower), x)

    def test_missing_input_key_matches_evaluator(self):
        self.packet["state_enclosure"] = None
        result = self.evaluate()
        self.assertIn("state_enclosure.reconstruction", result["missing_inputs"])
        self.assertNotIn("state_enclosure.continuous_reconstruction", result["missing_inputs"])

    def test_negative_curvature_rejected(self):
        self.packet["query_bounds"][0]["curvature_M2"] = scalar(-1)
        with self.assertRaisesRegex(BoundInputError, "NEGATIVE_BOUND:curvature_M2"):
            self.evaluate()


class ActualBindingControls(unittest.TestCase):
    def test_actual_313_queries_626_endpoints(self):
        context = json.loads((UNIT / "inputs" / "SOURCE_CONTEXT.json").read_text())
        validate_context(context)
        self.assertEqual(len(context["queries"]), 313)
        self.assertEqual(context["source_identity"]["active_endpoint_slots"], 626)
        self.assertEqual(context["operator"]["shape"], [314, 313])

    def test_actual_missing_inputs_fail_closed(self):
        result = evaluate_files(UNIT / "inputs" / "SOURCE_CONTEXT.json",
                                UNIT / "inputs" / "ACTUAL_BOUND_INPUTS.json")
        self.assertEqual(result["status"], "BLOCKED_ACTUAL_BOUND_INPUTS")
        self.assertEqual(result["bound_input_query_coverage"], 0)
        self.assertIsNone(result["physical_epsilon"])
        self.assertIsNone(result["conditional_epsilon"])
        self.assertIn("state_enclosure.defect", result["missing_inputs"])
        self.assertIn("query_bounds.whole_cell_curvature", result["missing_inputs"])

    def test_actual_anchor_and_context_tamper_detected(self):
        context = json.loads((UNIT / "inputs" / "SOURCE_CONTEXT.json").read_text())
        context["queries"][0]["anchor_representation_radius_exact"] = "0"
        with self.assertRaisesRegex(BoundInputError, "SOURCE_ANCHOR_MISMATCH"):
            validate_context(context)


if __name__ == "__main__":
    unittest.main(verbosity=2)
