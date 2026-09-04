from __future__ import annotations

import importlib
import json
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
DOC = ROOT / "docs" / "research" / "rec_donor01_typed_physical_source_red"
FUTURE_MODULE = "full_bianchi_hyrec.physical_source_authority"
FUTURE_PATH = SRC / "full_bianchi_hyrec" / "physical_source_authority.py"


class TestRecDonor01TypedPhysicalSourceRed(unittest.TestCase):
    """Inherited RED behaviours; only presence and a proved null fixture migrate."""

    def _module(self):
        if not FUTURE_PATH.is_file():
            self.fail(
                "INTENDED_RED: future physical-source authority is absent at "
                f"{FUTURE_PATH.relative_to(ROOT)}"
            )
        source_path = str(SRC)
        if source_path not in sys.path:
            sys.path.insert(0, source_path)
        try:
            return importlib.import_module(FUTURE_MODULE)
        except ModuleNotFoundError as exc:
            if exc.name == FUTURE_MODULE:
                self.fail(f"INTENDED_RED: future module import is absent: {exc}")
            raise

    def _support(self, m):
        return m.SpectralSupport(
            coordinate=m.PHOTON_ENERGY_J,
            lower_j=2.0e-18,
            upper_j=2.5e-18,
            lower_inclusive=True,
            upper_inclusive=False,
            outside_policy=m.ZERO_OUTSIDE_SUPPORT,
        )

    def _provenance(self, m, payload_sha256="c" * 64):
        return m.SourceProvenance(
            repository="cosmosapjw-quantum/rec_bianchi",
            source_commit_sha="a" * 40,
            source_path="HyRec/hydrogen.c",
            source_blob_sha="b" * 40,
            payload_sha256=payload_sha256,
            dependency_sha256={
                "Alpha_inf.dat": "d" * 64,
                "R_inf.dat": "e" * 64,
                "two_photon_tables.dat": "f" * 64,
            },
            algorithm_id="original-hyrec-2012-source-law/v1",
        )

    def _trajectory(self, m, restart_sha256="1" * 64):
        return m.TrajectoryBinding(
            background_snapshot_sha256="2" * 64,
            trajectory_id="rec-donor01-manufactured-interior-trajectory",
            event_surface_id="NO_EVENT_INTERIOR",
            restart_certificate_sha256=restart_sha256,
            time_basis=m.PHYSICAL_SECONDS,
        )

    def _source(
        self,
        m,
        emission=0.25,
        absorption=0.75,
        provenance=None,
        trajectory=None,
    ):
        return m.build_local_bosonic_affine_source(
            emission_s_inv=emission,
            absorption_s_inv=absorption,
            species=m.PHOTON,
            statistics=m.BOSON,
            frame=m.HYDROGEN_REST_FRAME,
            time_basis=m.PHYSICAL_SECONDS,
            support=self._support(m),
            provenance=provenance or self._provenance(m),
            trajectory=trajectory or self._trajectory(m),
            jvp_status=m.ANALYTIC_JVP,
        )

    def _kernel(self, m, process=None):
        return m.build_nonlocal_packet_kernel(
            process=process or m.TWO_PHOTON,
            companion_energy_nodes_j=(2.05e-18, 2.35e-18),
            kernel_per_H_s=(2.0, 3.0),
            support=self._support(m),
            provenance=self._provenance(m),
            trajectory=self._trajectory(m),
            jvp_status=m.NO_JVP_FAIL_CLOSED,
        )

    # Three controls. The immutable RED metadata remains unchanged.

    def test_control_parent_identity_and_future_module_present(self):
        manifest = json.loads((DOC / "STAGE_MANIFEST.json").read_text())
        self.assertEqual(
            manifest["base_commit"],
            "926e0c79a3fe7c3f5b24d5c5bb81304332def232",
        )
        self.assertEqual(
            manifest["base_tree"],
            "ce0654041d097768fae4f6a52b23c2137558f7be",
        )
        self.assertTrue(FUTURE_PATH.is_file())

    def test_control_existing_affine_primitive_remains_nonauthoritative(self):
        text = (
            ROOT
            / "src/full_bianchi_hyrec/trajectory/paired_source_transfer.py"
        ).read_text()
        self.assertIn('CLASSIFICATION = "NONAUTHORITATIVE_FORMULA_PRIMITIVE"', text)
        self.assertIn("eta * (1 + f) - kappa * f", text)
        self.assertIn("not directional-source authority", text)

    def test_control_progress_policy_retains_physical_face_firewalls(self):
        text = (ROOT / "docs/quality/PROGRESS_FIRST_IDENTITY_POLICY.md").read_text()
        self.assertIn("## 4. Physical-face firewall", text)
        self.assertIn("Formula closure is not source authority", text)
        self.assertIn("two-photon and Raman primitives produce photon-packet rates", text)

    # Thirteen inherited behaviours; unresolved deposition is NOT suppressed.

    def test_future_module_exposes_minimal_typed_authority_surface(self):
        m = self._module()
        required = {
            "SpectralSupport", "SourceProvenance", "TrajectoryBinding",
            "AngularRepresentation", "MomentMapBinding",
            "PacketDepositionBinding", "build_local_bosonic_affine_source",
            "build_nonlocal_packet_kernel", "bind_angular_representation",
            "deposit_packet_rate", "apply_local_observer_boost", "PHOTON",
            "BOSON", "HYDROGEN_REST_FRAME", "PHYSICAL_SECONDS",
            "PHOTON_ENERGY_J", "ANALYTIC_JVP",
        }
        self.assertFalse(required - set(dir(m)))

    def test_local_source_binds_physical_metadata_and_provenance(self):
        m = self._module()
        source = self._source(m)
        self.assertEqual(
            (source.species, source.statistics, source.frame, source.time_basis),
            (m.PHOTON, m.BOSON, m.HYDROGEN_REST_FRAME, m.PHYSICAL_SECONDS),
        )
        self.assertEqual(source.spectral_coordinate, m.PHOTON_ENERGY_J)
        self.assertEqual(source.rate_units, "s^-1")
        self.assertEqual(source.provenance.repository, "cosmosapjw-quantum/rec_bianchi")
        self.assertRegex(source.semantic_sha256, r"^[0-9a-f]{64}$")
        self.assertEqual(source.construction_status, "VALIDATED_FACTORY_ONLY")

    def test_source_identity_is_representation_neutral_and_mutation_sensitive(self):
        m = self._module()
        source = self._source(m)
        changed = self._source(m, provenance=self._provenance(m, "9" * 64))
        self.assertNotEqual(source.semantic_sha256, changed.semantic_sha256)
        grid = m.AngularRepresentation(
            kind=m.FULL_SPECTRAL_ANGULAR_GRID,
            identity_sha256="3" * 64,
            rank_limit=None,
            node_count=None,
            rank_claim=m.DECLARED_SUBSPACE_ONLY,
        )
        pstf = m.AngularRepresentation(
            kind=m.SPECTRAL_PSTF_COEFFICIENTS,
            identity_sha256="4" * 64,
            rank_limit=8,
            node_count=None,
            rank_claim=m.DECLARED_SUBSPACE_ONLY,
        )
        a = m.bind_angular_representation(source, grid)
        b = m.bind_angular_representation(source, pstf)
        self.assertEqual(a.source_semantic_sha256, source.semantic_sha256)
        self.assertEqual(b.source_semantic_sha256, source.semantic_sha256)
        self.assertNotEqual(a.representation_sha256, b.representation_sha256)

    def test_positive_primary_rates_and_signed_net_affine_rate(self):
        m = self._module()
        self.assertEqual(self._source(m, 0.25, 0.75).chi_affine_s_inv, 0.5)
        self.assertEqual(self._source(m, 0.75, 0.25).chi_affine_s_inv, -0.5)
        for emission, absorption in (
            (-1.0, 0.75), (0.25, -1.0),
            (float("nan"), 0.75), (0.25, float("inf")),
        ):
            with self.assertRaises(m.SourceContractError):
                self._source(m, emission, absorption)

    def test_stimulated_emission_action_and_source_off_control(self):
        m = self._module()
        source = self._source(m)
        energy = 2.25e-18
        self.assertEqual(source.action(energy_j=energy, occupation=2.0), -0.75)
        off = self._source(m, 0.0, 0.0)
        self.assertEqual(off.action(energy_j=energy, occupation=123.0), 0.0)
        with self.assertRaises(m.SourceContractError):
            source.action(energy_j=energy, occupation=-1.0)

    def test_equilibrium_detailed_balance_and_amplifying_branch_boundary(self):
        m = self._module()
        source = self._source(m)
        equilibrium = source.equilibrium_occupation()
        self.assertEqual(equilibrium, 0.5)
        self.assertEqual(source.action(energy_j=2.25e-18, occupation=equilibrium), 0.0)
        with self.assertRaises(m.NoFiniteEquilibriumError):
            self._source(m, 0.75, 0.25).equilibrium_occupation()

    def test_energy_threshold_support_and_units_are_explicit(self):
        m = self._module()
        source = self._source(m)
        # At f=0.5 the affine law is exactly zero everywhere, so it cannot
        # detect endpoint inclusion. The independent Fraction control proves
        # C(2)=-3/4; the support and physical coefficients are unchanged.
        self.assertEqual(source.action(energy_j=1.99e-18, occupation=2.0), 0.0)
        self.assertEqual(source.action(energy_j=2.0e-18, occupation=2.0), -0.75)
        self.assertEqual(source.action(energy_j=2.5e-18, occupation=2.0), 0.0)
        self.assertEqual(source.support.coordinate, m.PHOTON_ENERGY_J)
        self.assertEqual(source.support.outside_policy, m.ZERO_OUTSIDE_SUPPORT)
        self.assertEqual(source.rate_units, "s^-1")

    def test_local_analytic_jvp_is_exact_without_finite_difference_fallback(self):
        m = self._module()
        source = self._source(m)
        actual = source.jvp(
            energy_j=2.25e-18,
            occupation=0.5,
            d_occupation=0.125,
            d_emission_s_inv=0.5,
            d_absorption_s_inv=-0.25,
        )
        self.assertEqual(actual, 0.8125)
        self.assertEqual(source.jvp_method, m.ANALYTIC_JVP)
        self.assertFalse(source.uses_finite_difference_jvp)

    def test_two_photon_and_raman_kernels_are_nonlocal_not_local_pairs(self):
        m = self._module()
        two = self._kernel(m, m.TWO_PHOTON)
        raman = self._kernel(m, m.RAMAN)
        self.assertEqual(two.packet_rate_units, "photon_packet H^-1 s^-1")
        self.assertNotEqual(two.semantic_sha256, raman.semantic_sha256)
        self.assertNotEqual(
            two.evaluate_packet_rate(companion_occupation=(0.5, 0.0)),
            two.evaluate_packet_rate(companion_occupation=(0.5, 1.0)),
        )
        with self.assertRaises(m.NonlocalKernelIsNotLocalPairError):
            two.as_local_affine_pair()
        with self.assertRaises(m.SourceJVPUnavailableError):
            two.jvp(companion_occupation=(0.5, 1.0), tangent=(0.0, 1.0))

    def test_packet_rate_requires_once_only_deposition_authority(self):
        m = self._module()
        kernel = self._kernel(m)
        with self.assertRaises(m.DepositionAuthorityError):
            m.deposit_packet_rate(
                kernel=kernel,
                deposition=None,
                companion_occupation=(0.5, 1.0),
            )
        binding = m.PacketDepositionBinding(
            n_H_m3=1.0e8,
            phase_space_measure_si=2.0,
            deposition_matrix_sha256="5" * 64,
            normalization_sha256="6" * 64,
            application_count=1,
        )
        receipt = m.deposit_packet_rate(
            kernel=kernel,
            deposition=binding,
            companion_occupation=(0.5, 1.0),
        )
        self.assertEqual(receipt.application_count, 1)
        self.assertEqual(receipt.output_units, "s^-1")
        self.assertEqual(receipt.source_semantic_sha256, kernel.semantic_sha256)
        with self.assertRaises(m.DepositionAuthorityError):
            m.PacketDepositionBinding(
                n_H_m3=1.0e8,
                phase_space_measure_si=2.0,
                deposition_matrix_sha256="5" * 64,
                normalization_sha256="6" * 64,
                application_count=2,
            )

    def test_trajectory_event_and_restart_identity_fail_closed(self):
        m = self._module()
        source = self._source(m)
        self.assertIsNone(source.require_trajectory(self._trajectory(m)))
        with self.assertRaises(m.TrajectoryBindingError):
            source.require_trajectory(self._trajectory(m, "7" * 64))
        self.assertIn(source.trajectory.event_surface_id, source.semantic_payload)
        self.assertIn(source.trajectory.restart_certificate_sha256, source.semantic_payload)

    def test_integrated_state_requires_explicit_moment_map_binding(self):
        m = self._module()
        source = self._source(m)
        with self.assertRaises(m.MomentMapBindingRequiredError):
            source.bind_integrated_target(target=m.G_ANGULAR_ENERGY, moment_map=None)
        binding = m.MomentMapBinding(
            target=m.G_ANGULAR_ENERGY,
            source_semantic_sha256=source.semantic_sha256,
            radial_weight_sha256="8" * 64,
            angular_measure_sha256="9" * 64,
            closure_status=m.EXPLICIT_PROJECTION_ONLY,
        )
        bound = source.bind_integrated_target(
            target=m.G_ANGULAR_ENERGY,
            moment_map=binding,
        )
        self.assertEqual(bound.source_semantic_sha256, source.semantic_sha256)
        self.assertEqual(bound.target, m.G_ANGULAR_ENERGY)

    def test_no_universal_26_direction_authority_and_no_local_observer_boost(self):
        m = self._module()
        source = self._source(m)
        with self.assertRaises(m.FixedAngularFaceAuthorityError):
            m.AngularRepresentation(
                kind=m.FIXED_DIRECTIONAL_FACE,
                identity_sha256="a" * 64,
                rank_limit=None,
                node_count=26,
                rank_claim=m.ARBITRARY_HIGH_RANK,
            )
        with self.assertRaises(m.LocalObserverBoostForbiddenError):
            m.apply_local_observer_boost(source=source, beta=(1.0e-3, 0.0, 0.0))


if __name__ == "__main__":
    unittest.main(verbosity=2)
