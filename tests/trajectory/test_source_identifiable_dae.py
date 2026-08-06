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
    PrimitiveTrajectoryProblem,
    atomic_state_from_source_snapshot,
)
from full_bianchi_hyrec.trajectory.time_dependent_native import (
    CausalRadiationHistoryState,
    OriginalHyRecStateRole,
    SourceIdentifiableOriginalHyRecDAE,
    audit_canonical_native_radiation_time_measure,
    default_pr05b1_replacement_registry,
    source_identifiable_original_hyrec_layout,
)


ROOT = Path(__file__).resolve().parents[2]
ARCHIVE = ROOT / "archive/inputs/original_hyrec_oct2012/HyRec_Oct2012.zip"
SNAPSHOT_DIR = ROOT / "archive/expanded/Full_Bianchi_HyRec_PR04C0C1A_split_domain_boundary_v0_55"
NETWORK = ROOT / "data/full_scalar_com_khw_v050.npz"


def _background(snapshot, *, bianchi_type="I", sigma=None, A=None):
    return BackgroundSnapshot(
        tau=-np.log1p(snapshot.z),
        cosmic_time_s=1.0,
        H_s_inv=snapshot.H_s_inv,
        q=0.5,
        sigma_s_inv=np.zeros((3, 3)) if sigma is None else np.asarray(sigma, float),
        N_s_inv=np.zeros((3, 3)),
        A_s_inv=np.zeros(3) if A is None else np.asarray(A, float),
        frame_rotation_s_inv=np.zeros(3),
        beta_H=np.zeros(3),
        D0_beta_H_s_inv=np.zeros(3),
        chart_id="pr05b1-test",
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
    state = atomic_state_from_source_snapshot(
        source,
        com_occupation=scalar[:, None] * np.ones((1, grid.n_angle)),
        beta_H=np.zeros(3),
    )
    primitive = PrimitiveTrajectoryProblem(
        background=_background(source, bianchi_type=bianchi_type, sigma=sigma, A=A),
        source_snapshot=source,
        rates=rates,
        network=network,
        grid=grid,
        line=LineBoundaryConfig.lyman_alpha(
            temperature_K=state.T_m_K, x_red=-21.25, x_blue=21.25
        ),
        interface_enabled=False,
    )
    return SourceIdentifiableOriginalHyRecDAE.from_primitive_problem(primitive), state, source


def test_source_identifiable_row_roles_are_fixed_and_history_is_not_a_local_mass_row():
    layout = source_identifiable_original_hyrec_layout()
    assert layout.local_size == 314
    assert layout.differential_size == 1
    assert layout.algebraic_size == 313
    assert layout.history_size == 625
    assert layout.blocks[0].name == "free_electron_fraction"
    assert layout.blocks[0].role is OriginalHyRecStateRole.DIFFERENTIAL
    assert layout.blocks[1].role is OriginalHyRecStateRole.ALGEBRAIC
    assert layout.blocks[2].role is OriginalHyRecStateRole.ALGEBRAIC
    assert all(
        block.role is OriginalHyRecStateRole.ACCEPTED_STEP_MEMORY
        for block in layout.blocks[3:6]
    )
    assert np.array_equal(layout.mass_diagonal, np.r_[1.0, np.zeros(313)])


def test_canonical_source_residual_and_electron_rate_match_three_snapshots():
    for target in (1300, 1100, 900):
        problem, state, source = _problem(target)
        vector = problem.source_state_vector(state)
        derivative = problem.source_derivative_vector()
        residual = problem.residual(vector, derivative)
        assert problem.electron_rate_per_lna(source.xe, source.xr) == pytest.approx(
            source.dxHIIdlna, rel=4.0e-13, abs=0.0
        )
        assert problem.scaled_residual(residual, vector, derivative) < 3.0e-13


def test_shifted_ijacobian_matches_petsc_style_centered_difference():
    problem, state, _ = _problem()
    rng = np.random.default_rng(59)
    vector = problem.source_state_vector(state)
    derivative = problem.source_derivative_vector()
    direction = rng.normal(size=vector.size)
    shift = 3.7
    error = problem.central_difference_shifted_ijacobian_error(
        vector,
        derivative,
        direction=direction,
        shift=shift,
        step=2.0e-7,
    )
    assert error < 1.0e-8


def test_frozen_coefficient_backward_euler_reference_is_positive_and_reduces_to_source_constraint():
    problem, state, source = _problem()
    old = problem.source_state_vector(state).copy()
    old[0] *= 1.001
    result = problem.frozen_coefficient_backward_euler_step(old, delta_lna=1.0e-5)
    assert result.converged
    assert result.backward_error < 1.0e-11
    assert 0.0 < result.state_vector[0] < 1.0
    assert result.minimum_physical_population > 0.0
    assert result.algebraic_residual_relative < 3.0e-13
    assert np.linalg.norm(result.state_vector[1:] - problem.steady_native_solution, ord=np.inf) < 1.0e-12
    assert abs(result.state_vector[0] - source.xe) < 1.0e-2


def test_native_radiation_local_time_measure_is_constructively_nonidentifiable():
    _, _, source = _problem()
    audit = audit_canonical_native_radiation_time_measure(
        source.energy_eV,
        x_1s=source.x1s,
    )
    assert audit.identifiable is False
    assert audit.canonical_virtual_role is OriginalHyRecStateRole.ALGEBRAIC
    assert audit.finite_support_widths_present is False
    assert audit.cell_edges_present is False
    assert np.all(audit.candidate_mass_a > 0.0)
    assert np.all(audit.candidate_mass_b > 0.0)
    assert np.max(np.abs(audit.candidate_mass_b / audit.candidate_mass_a - 2.0)) < 2.0e-14
    assert audit.maximum_relative_candidate_difference > 0.4


def test_compressed_terms_remain_owned_and_pr05b_is_not_falsely_closed():
    registry = default_pr05b1_replacement_registry()
    audit = registry.audit()
    assert audit.duplicate_owner_count == 0
    assert audit.unowned_term_count == 0
    assert audit.removed_without_complete_replacement_count == 0
    assert audit.completed_replacement_count == 0
    assert audit.requested_replacement_count == 4
    assert audit.pr05b_complete is False
    assert all(not term.removed for term in registry.terms)
    assert all(term.blocker for term in registry.terms)


def test_causal_history_state_rejects_future_endpoint_and_round_trips_exactly():
    state = CausalRadiationHistoryState(
        accepted_index=12,
        outgoing_virtual=np.linspace(-1e-12, 2e-12, 311),
        outgoing_lyman=np.asarray([1e-13, -2e-14, 3e-15]),
        average_virtual=np.linspace(-2e-12, 1e-12, 311),
    )
    state.assert_endpoint_is_available(12)
    with pytest.raises(ValueError, match="future"):
        state.assert_endpoint_is_available(13)
    decoded = CausalRadiationHistoryState.from_json(state.to_json())
    assert decoded.accepted_index == state.accepted_index
    assert np.array_equal(decoded.outgoing_virtual, state.outgoing_virtual)
    assert np.array_equal(decoded.outgoing_lyman, state.outgoing_lyman)
    assert np.array_equal(decoded.average_virtual, state.average_virtual)


def test_fixed_local_state_dae_is_bianchi_type_independent():
    shear = np.diag([2e-14, -1e-14, -1e-14])
    first, state, _ = _problem(1100, bianchi_type="II", sigma=shear)
    second, state2, _ = _problem(1100, bianchi_type="VI_h", A=np.asarray([2e-14, 0.0, 0.0]))
    third, state3, _ = _problem(1100, bianchi_type="VI_-1/9", sigma=-shear)
    pairs = ((first, state), (second, state2), (third, state3))
    residuals = [
        problem.residual(problem.source_state_vector(st), problem.source_derivative_vector())
        for problem, st in pairs
    ]
    assert np.array_equal(residuals[0], residuals[1])
    assert np.array_equal(residuals[0], residuals[2])
    assert first.electron_rate_per_lna(first.source_snapshot.xe, first.source_snapshot.xr) == second.electron_rate_per_lna(second.source_snapshot.xe, second.source_snapshot.xr)
