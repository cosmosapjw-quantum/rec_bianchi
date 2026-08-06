from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from full_bianchi_hyrec.background.snapshot import BackgroundSnapshot
from full_bianchi_hyrec.recoil.nonlinear_bose_runtime import (
    CollisionNetwork,
    LineBoundaryConfig,
    positive_harmonic_grid,
)
from full_bianchi_hyrec.recoil.original_hyrec_physical_flux import (
    parse_original_hyrec_snapshot_csv,
)
from full_bianchi_hyrec.trajectory.primitive_rates import OriginalHyRecPrimitiveRateTable
from full_bianchi_hyrec.trajectory.primitive_trajectory import (
    AtomicRadiationState,
    PrimitiveTrajectoryProblem,
    StateClassification,
    atomic_state_from_source_snapshot,
    audit_native_m_matrix,
    default_pr05a_ownership_registry,
)


ROOT = Path(__file__).resolve().parents[2]
ARCHIVE = ROOT / "archive/inputs/original_hyrec_oct2012/HyRec_Oct2012.zip"
SNAPSHOT_DIR = ROOT / "archive/expanded/Full_Bianchi_HyRec_PR04C0C1A_split_domain_boundary_v0_55"
NETWORK = ROOT / "data/full_scalar_com_khw_v050.npz"


def _background(snapshot, *, bianchi_type="I", sigma=None, A=None):
    sigma = np.zeros((3, 3)) if sigma is None else np.asarray(sigma, float)
    A = np.zeros(3) if A is None else np.asarray(A, float)
    return BackgroundSnapshot(
        tau=-np.log1p(snapshot.z),
        cosmic_time_s=1.0,
        H_s_inv=snapshot.H_s_inv,
        q=0.5,
        sigma_s_inv=sigma,
        N_s_inv=np.zeros((3, 3)),
        A_s_inv=A,
        frame_rotation_s_inv=np.zeros(3),
        beta_H=np.zeros(3),
        D0_beta_H_s_inv=np.zeros(3),
        chart_id="pr05a-test",
        bianchi_type=bianchi_type,
    )


def _problem(target=1100, *, bianchi_type="I", sigma=None, A=None):
    source = parse_original_hyrec_snapshot_csv(SNAPSHOT_DIR / f"pr04c_z{target}.csv")
    rates = OriginalHyRecPrimitiveRateTable.from_archive(ARCHIVE).evaluate(
        radiation_temperature_eV_rescaled=source.TR_eV_rescaled,
        matter_to_radiation_temperature_ratio=source.TM_over_TR,
        fsR=source.fsR,
        meR=source.meR,
    )
    network = CollisionNetwork.from_npz(NETWORK)
    grid = positive_harmonic_grid(12)
    activity = network.equilibrium_weight / network.mode_measure
    scalar = activity / (1.0 - activity)
    occupation = scalar[:, None] * np.ones((1, grid.n_angle))
    state = atomic_state_from_source_snapshot(
        source,
        com_occupation=occupation,
        beta_H=np.zeros(3),
    )
    problem = PrimitiveTrajectoryProblem(
        background=_background(source, bianchi_type=bianchi_type, sigma=sigma, A=A),
        source_snapshot=source,
        rates=rates,
        network=network,
        grid=grid,
        line=LineBoundaryConfig.lyman_alpha(temperature_K=state.T_m_K, x_red=-21.25, x_blue=21.25),
        interface_enabled=False,
    )
    return problem, state


def test_typed_state_is_immutable_positive_where_physical_and_signed_where_departure():
    _, state = _problem()
    assert isinstance(state, AtomicRadiationState)
    assert state.classification is StateClassification.SOURCE_DERIVED
    assert np.all(state.com_occupation > 0.0)
    assert state.x_1s > 0.0 and state.x_2s > 0.0 and state.x_2p > 0.0
    assert state.native_departure.shape == (311,)
    assert not state.native_departure.flags.writeable
    with pytest.raises(ValueError, match="strictly positive"):
        AtomicRadiationState(
            real_departure=state.real_departure,
            native_departure=state.native_departure,
            com_occupation=np.zeros_like(state.com_occupation),
            x_1s=state.x_1s,
            x_2s=state.x_2s,
            x_2p=state.x_2p,
            x_e=state.x_e,
            x_HII=state.x_HII,
            T_m_K=state.T_m_K,
            beta_H=state.beta_H,
            interface_accumulators=state.interface_accumulators,
            classification=state.classification,
        )


def test_source_solution_closes_native_residual_and_m_matrix_gate_at_three_snapshots():
    for target in (1300, 1100, 900):
        problem, state = _problem(target)
        result = problem.evaluate(state)
        assert result.native_residual_relative < 2.0e-13
        assert result.com_collision_relative < 2.0e-13
        assert result.ledger.number_residual < 3.0e-13
        assert result.ledger.photon_atom_energy_residual_W_m3 == 0.0
        assert result.ledger.minimum_physical_state > 0.0
        audit = audit_native_m_matrix(problem.native_matrix_s_inv)
        assert audit.off_diagonal_max <= 0.0
        assert audit.diagonal_min > 0.0
        assert audit.column_dominance_margin_min > 0.0
        assert audit.nonsingular_m_matrix


def test_full_analytic_jvp_matches_centered_difference():
    problem, state = _problem()
    rng = np.random.default_rng(58)
    native_direction = rng.normal(size=313)
    log_com_direction = rng.normal(size=state.com_occupation.shape)
    residual = problem.central_difference_jvp_residual(
        state,
        native_direction=native_direction,
        log_com_direction=log_com_direction,
        step=1.0e-6,
    )
    assert residual < 1.0e-8


def test_feedback_has_correct_units_structure_and_scalar_equilibrium_limit():
    problem, state = _problem()
    feedback = problem.evaluate(state).feedback
    assert feedback.rho_gamma_J_m3 > 0.0
    assert feedback.p_gamma_Pa == pytest.approx(feedback.rho_gamma_J_m3 / 3.0, rel=3e-13)
    assert np.max(np.abs(feedback.q_gamma_a_W_m2)) < 1.0e-8 * feedback.rho_gamma_J_m3 * 299792458.0
    assert np.max(np.abs(feedback.pi_gamma_ab_Pa)) < 1.0e-8 * feedback.rho_gamma_J_m3
    assert np.max(np.abs(feedback.Q_atom_mu_W_m3)) < 1.0e-4 * feedback.rho_gamma_J_m3 * problem.background.H_s_inv
    assert feedback.boundary_red_number_flux_per_H_s == 0.0
    assert feedback.boundary_blue_number_flux_per_H_s == 0.0


def test_ownership_registry_is_fail_closed_and_keeps_compressed_terms_until_replaced():
    registry = default_pr05a_ownership_registry()
    audit = registry.audit()
    assert audit.duplicate_owner_count == 0
    assert audit.unowned_term_count == 0
    assert audit.removed_without_replacement_count == 0
    assert audit.interface_evaluation_count == 1
    assert audit.interface_application_count == 2
    assert audit.pure_interface_atom_source_W_m3 == 0.0
    assert all(
        not term.removed
        for term in registry.terms
        if term.name in {
            "sobolev_lya_escape",
            "native_A1s_diffusion",
            "completed_Tvv_schur",
            "scalar_Dfplus_history_feedback",
        }
    )


def test_fixed_hydrogen_frame_microphysics_is_bianchi_type_independent():
    zero = np.zeros((3, 3))
    shear = np.diag([2e-14, -1e-14, -1e-14])
    first, state = _problem(1100, bianchi_type="II", sigma=shear)
    second, state2 = _problem(1100, bianchi_type="VI_h", sigma=zero, A=np.array([2e-14, 0.0, 0.0]))
    third, state3 = _problem(1100, bianchi_type="VI_-1/9", sigma=-shear)
    values = [problem.evaluate(st) for problem, st in ((first, state), (second, state2), (third, state3))]
    assert all(np.array_equal(values[0].native_residual, item.native_residual) for item in values[1:])
    assert all(np.array_equal(values[0].com_collision_action, item.com_collision_action) for item in values[1:])
    assert all(item.feedback.rho_gamma_J_m3 == values[0].feedback.rho_gamma_J_m3 for item in values[1:])


def test_restart_round_trip_is_exact():
    problem, state = _problem()
    encoded = problem.restart_payload(state)
    decoded = problem.state_from_restart_payload(encoded)
    assert np.array_equal(decoded.real_departure, state.real_departure)
    assert np.array_equal(decoded.native_departure, state.native_departure)
    assert np.array_equal(decoded.com_occupation, state.com_occupation)
    assert decoded.interface_accumulators == state.interface_accumulators


def test_interface_off_implicit_projection_is_positive_conservative_and_stable():
    problem, state = _problem()
    perturbed = state.replace(
        real_departure=state.real_departure * np.asarray([1.03, 0.97]),
        native_departure=state.native_departure * (1.0 + 0.02 * np.sin(np.arange(311))),
        # PR-05A proves the native DAE projection while retaining the exact
        # v0.57 COM equilibrium lane. A dynamically perturbed COM trajectory
        # belongs to PR-05B/C and would duplicate the already stress-tested
        # v0.56 nonlinear solve.
        com_occupation=state.com_occupation,
        classification=StateClassification.OPERATOR_VERIFICATION,
    )
    result = problem.implicit_step(perturbed, dt_s=1.0e5)
    assert result.converged
    assert result.backward_error < 1.0e-11
    assert result.native_residual_relative < 2.0e-13
    assert result.com_residual_relative < 1.0e-11
    assert result.number_relative_change < 1.0e-11
    assert result.minimum_physical_state > 0.0
    assert result.free_energy_change == 0.0
    assert result.state.classification is StateClassification.OPERATOR_VERIFICATION
