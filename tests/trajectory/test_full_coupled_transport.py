from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from full_bianchi_hyrec.background import BackgroundSnapshotSequence
from full_bianchi_hyrec.recoil.frequency_liouville import (
    ConservativeFrequencyLiouville,
    angular_scalarization_no_go_witness,
)
from full_bianchi_hyrec.recoil.nonlinear_bose_release import HarmonicGrid
from full_bianchi_hyrec.recoil.nonlinear_bose_runtime import (
    CollisionNetwork,
    LineBoundaryConfig,
)
from full_bianchi_hyrec.trajectory.full_coupled_adaptive import (
    CoupledCollisionTransportProblem,
)


ROOT = Path(__file__).resolve().parents[2]
BACKGROUND = ROOT / "data/pr01c_background_snapshots_v048.npz"
NETWORK = ROOT / "data/full_scalar_com_khw_v050.npz"


def octahedral_grid() -> HarmonicGrid:
    directions = np.asarray(
        [
            [1.0, 0.0, 0.0],
            [-1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0],
            [0.0, -1.0, 0.0],
            [0.0, 0.0, 1.0],
            [0.0, 0.0, -1.0],
        ]
    )
    return HarmonicGrid.from_directions(directions, np.full(6, 1.0 / 6.0), ell_max=1)


def three_cell_network() -> CollisionNetwork:
    pair = np.zeros((2, 3, 3))
    pair[0, 0, 1] = pair[0, 1, 0] = 2.0e-3
    pair[0, 1, 2] = pair[0, 2, 1] = 1.5e-3
    pair[1, 0, 1] = pair[1, 1, 0] = 2.0e-4
    pair[1, 1, 2] = pair[1, 2, 1] = -1.0e-4
    line = LineBoundaryConfig.lyman_alpha(temperature_K=3000.0, x_red=-1.5, x_blue=1.5)
    intervals = np.asarray([[-1.5, -0.5], [-0.5, 0.5], [0.5, 1.5]])
    from scipy.constants import c, h

    lo = line.nu_abs_Hz + intervals[:, 0] * line.Doppler_width_Hz
    hi = line.nu_abs_Hz + intervals[:, 1] * line.Doppler_width_Hz
    mode = 8.0 * np.pi * (hi**3 - lo**3) / (3.0 * c**3)
    centroid = 0.75 * (hi**4 - lo**4) / (hi**3 - lo**3)
    momentum = h * centroid / c
    return CollisionNetwork(
        state_intervals=intervals,
        state_labels=np.asarray(["FR00", "I00", "FB02"]),
        pair_moments=pair,
        same_cell_rates=np.zeros((2, 3)),
        mode_measure=mode,
        equilibrium_weight=0.2 * mode,
        momentum_scale=momentum,
        inherited_release_policy={"test": 1},
    )


def test_background_sequence_interpolates_actual_snapshots_and_localizes_source_root() -> None:
    sequence = BackgroundSnapshotSequence.from_npz(
        BACKGROUND, "Bianchi_II_large_shear"
    )
    midpoint = 0.5 * (sequence.tau[58] + sequence.tau[59])
    snapshot = sequence.snapshot_at_tau(midpoint)
    assert snapshot.chart_id == "class_a"
    assert snapshot.bianchi_type == "II"
    assert snapshot.tau == pytest.approx(midpoint)
    assert np.max(np.abs(snapshot.sigma_s_inv - snapshot.sigma_s_inv.T)) == 0.0
    assert abs(np.trace(snapshot.sigma_s_inv)) < 1.0e-25

    line = LineBoundaryConfig.lyman_alpha(temperature_K=3000.0, x_red=-21.25, x_blue=21.25)
    direction = np.asarray([[1.0, 0.0, 0.0]])
    roots = sequence.boundary_speed_roots(
        tau_start=0.5,
        tau_end=0.72,
        directions_normal=direction,
        line=line,
    )
    assert roots.red.shape == (1,)
    assert roots.red[0] == pytest.approx(0.6072662349590596, abs=3.0e-4)
    assert roots.source_derived


def test_frequency_liouville_is_number_conservative_and_energy_exact() -> None:
    network = three_cell_network()
    grid = octahedral_grid()
    operator = ConservativeFrequencyLiouville.from_network(
        network,
        reference_line=LineBoundaryConfig.lyman_alpha(
            temperature_K=3000.0, x_red=-1.5, x_blue=1.5
        ),
    )
    occupation = np.asarray(
        [
            [0.20, 0.18, 0.22, 0.19, 0.25, 0.17],
            [0.16, 0.17, 0.15, 0.18, 0.14, 0.19],
            [0.11, 0.13, 0.10, 0.14, 0.09, 0.15],
        ]
    )
    face_speeds = np.asarray(
        [
            [-0.3, -0.2, 0.1, 0.2, -0.4, 0.4],
            [-0.25, -0.15, 0.15, 0.25, -0.35, 0.35],
            [-0.2, -0.1, 0.2, 0.3, -0.3, 0.3],
            [-0.1, 0.05, 0.25, 0.35, -0.2, 0.2],
        ]
    )
    result = operator.evaluate(
        occupation,
        face_speeds_x_s_inv=face_speeds,
        native_red_occupation=0.24,
        native_blue_occupation=0.08,
        grid=grid,
    )
    assert abs(result.global_number_residual_m3_s) < 2.0e-12
    assert result.energy_identity_relative_residual < 2.0e-15
    assert result.interface_atom_source_W_m3 == 0.0
    assert np.linalg.norm(result.interface_four_momentum_residual) < 2.0e-25


def test_frequency_liouville_jvp_matches_central_difference() -> None:
    network = three_cell_network()
    grid = octahedral_grid()
    operator = ConservativeFrequencyLiouville.from_network(
        network,
        reference_line=LineBoundaryConfig.lyman_alpha(
            temperature_K=3000.0, x_red=-1.5, x_blue=1.5
        ),
    )
    rng = np.random.default_rng(42)
    occupation = 0.05 + 0.2 * rng.random((3, grid.n_angle))
    direction = rng.normal(size=occupation.shape)
    speeds = rng.normal(scale=0.2, size=(4, grid.n_angle))
    analytic = operator.jvp(
        occupation,
        direction,
        face_speeds_x_s_inv=speeds,
        grid=grid,
    ).occupation_action_jvp
    epsilon = 2.0e-7
    plus = operator.evaluate(
        occupation + epsilon * direction,
        face_speeds_x_s_inv=speeds,
        native_red_occupation=0.1,
        native_blue_occupation=0.1,
        grid=grid,
    ).occupation_action
    minus = operator.evaluate(
        occupation - epsilon * direction,
        face_speeds_x_s_inv=speeds,
        native_red_occupation=0.1,
        native_blue_occupation=0.1,
        grid=grid,
    ).occupation_action
    finite = (plus - minus) / (2.0 * epsilon)
    relative = np.max(np.abs(analytic - finite)) / max(np.max(np.abs(finite)), 1.0e-300)
    assert relative < 2.0e-9


def test_scalar_native_feedback_cannot_preserve_directional_momentum() -> None:
    grid = octahedral_grid()
    witness = angular_scalarization_no_go_witness(grid)
    assert witness.monopole_residual == 0.0
    assert witness.scalarized_value_a == witness.scalarized_value_b
    assert np.linalg.norm(witness.momentum_a + witness.momentum_b) < 1.0e-15
    assert np.linalg.norm(witness.momentum_a - witness.momentum_b) > 0.5
    assert witness.no_unique_scalar_momentum_preserving_map


def test_coupled_collision_transport_step_preserves_positivity_and_global_ledgers() -> None:
    network = three_cell_network()
    grid = octahedral_grid()
    transport = ConservativeFrequencyLiouville.from_network(
        network,
        reference_line=LineBoundaryConfig.lyman_alpha(
            temperature_K=3000.0, x_red=-1.5, x_blue=1.5
        ),
    )
    speeds = np.asarray(
        [
            [-2.0e-5, -1.0e-5, 1.0e-5, 2.0e-5, -1.5e-5, 1.5e-5],
            [-1.5e-5, -0.5e-5, 1.2e-5, 2.2e-5, -1.0e-5, 1.0e-5],
            [-1.0e-5, 0.2e-5, 1.4e-5, 2.4e-5, -0.5e-5, 0.5e-5],
            [-0.5e-5, 0.5e-5, 1.6e-5, 2.6e-5, 0.1e-5, 0.3e-5],
        ]
    )
    old = np.asarray(
        [
            [0.20, 0.18, 0.22, 0.19, 0.25, 0.17],
            [0.16, 0.17, 0.15, 0.18, 0.14, 0.19],
            [0.11, 0.13, 0.10, 0.14, 0.09, 0.15],
        ]
    )
    problem = CoupledCollisionTransportProblem(
        network=network,
        grid=grid,
        transport=transport,
        face_speeds_x_s_inv=speeds,
        native_red_occupation=np.full(grid.n_angle, 0.24),
        native_blue_occupation=np.full(grid.n_angle, 0.08),
        dt_s=200.0,
    )
    result = problem.implicit_step(old, nonlinear_rtol=2.0e-10)
    assert result.converged
    assert result.minimum_occupation > 0.0
    assert result.residual_relative < 2.0e-10
    assert result.global_number_relative_residual < 2.0e-12
    assert result.energy_identity_relative_residual < 2.0e-12
    assert result.interface_atom_source_J_m3 == 0.0
    assert result.collision_four_force_residual < 2.0e-18
    assert result.collision_entropy_production <= 1.0e-18


def test_locked_35_state_operator_uses_actual_background_characteristics() -> None:
    network = CollisionNetwork.from_npz(NETWORK)
    with np.load(BACKGROUND, allow_pickle=False) as data:
        # This 26-direction fixture has rank 22 at ell_max=4, so its 25-mode
        # analysis/synthesis map is not an admissible harmonic grid.  The face
        # speed assertion below uses directions only; ell_max=3 is the largest
        # full-rank basis supported by these same physical ordinates.
        with pytest.raises(ValueError, match="rank deficient|ill-conditioned"):
            HarmonicGrid.from_directions(
                data["directions"], data["angular_weights"], ell_max=4
            )
        grid = HarmonicGrid.from_directions(
            data["directions"], data["angular_weights"], ell_max=3
        )
    sequence = BackgroundSnapshotSequence.from_npz(
        BACKGROUND, "Bianchi_II_large_shear"
    )
    snapshot = sequence.snapshot_at_tau(0.0)
    line = LineBoundaryConfig.lyman_alpha(temperature_K=3000.0, x_red=-21.25, x_blue=21.25)
    transport = ConservativeFrequencyLiouville.from_network(network)
    speeds = transport.face_speeds_from_snapshot(snapshot, grid=grid, line=line)
    assert speeds.shape == (36, grid.n_angle)
    assert np.any(speeds < 0.0)
    assert np.any(speeds > 0.0)
    assert transport.network_mode_measure_residual < 2.0e-8




def test_frequency_liouville_rejects_reference_grid_inconsistent_with_locked_modes() -> None:
    network = CollisionNetwork.from_npz(NETWORK)
    mismatched = LineBoundaryConfig.lyman_alpha(
        temperature_K=3550.0, x_red=-21.25, x_blue=21.25
    )
    with pytest.raises(ValueError, match="locked network mode measure"):
        ConservativeFrequencyLiouville.from_network(
            network, reference_line=mismatched
        )


def test_frequency_liouville_rejects_a_mismatched_moving_doppler_grid() -> None:
    network = CollisionNetwork.from_npz(NETWORK)
    with np.load(BACKGROUND, allow_pickle=False) as data:
        grid = HarmonicGrid.from_directions(
            data["directions"], data["angular_weights"], ell_max=3
        )
    sequence = BackgroundSnapshotSequence.from_npz(
        BACKGROUND, "Bianchi_II_large_shear"
    )
    snapshot = sequence.snapshot_at_tau(0.4)
    transport = ConservativeFrequencyLiouville.from_network(network)
    mismatched = LineBoundaryConfig.lyman_alpha(
        temperature_K=3550.0, x_red=-21.25, x_blue=21.25
    )
    with pytest.raises(ValueError, match="fixed COM frequency grid"):
        transport.face_speeds_from_snapshot(
            snapshot, grid=grid, line=mismatched
        )


def test_source_h_rescaling_preserves_hubble_normalized_geometry() -> None:
    sequence = BackgroundSnapshotSequence.from_npz(
        BACKGROUND, "Bianchi_VI_h_tilted_large_shear"
    )
    base = sequence.snapshot_at_tau(0.2)
    target_H = 6.25e-14
    scaled = sequence.snapshot_at_tau(0.2, H_s_inv_override=target_H)
    factor = target_H / base.H_s_inv
    assert scaled.H_s_inv == target_H
    assert np.allclose(scaled.sigma_s_inv, factor * base.sigma_s_inv)
    assert np.allclose(scaled.N_s_inv, factor * base.N_s_inv)
    assert np.allclose(scaled.A_s_inv, factor * base.A_s_inv)
    assert np.allclose(
        scaled.frame_rotation_s_inv, factor * base.frame_rotation_s_inv
    )
    assert np.allclose(scaled.D0_beta_H_s_inv, factor * base.D0_beta_H_s_inv)
    assert np.array_equal(scaled.beta_H, base.beta_H)
    assert scaled.branch_flags["local_hubble_rescaled"]


def test_full_coupling_identifiability_audit_blocks_source_derived_claim() -> None:
    from full_bianchi_hyrec.trajectory.full_coupled_adaptive import (
        audit_full_coupling_identifiability,
    )

    audit = audit_full_coupling_identifiability(octahedral_grid())
    assert audit.native_history_angular_rank == 1
    assert audit.minimum_number_momentum_rank == 4
    assert audit.exact_face_trace_rank == 6
    assert audit.required_angular_rank == 6
    assert audit.com_face_trace_source_defined is False
    assert audit.p0_face_trace_is_new_closure
    assert audit.fully_source_derived_coupling_identified is False
    assert audit.bounded_no_go


def test_locked_collision_stiffness_audit_requires_block_preconditioner() -> None:
    from full_bianchi_hyrec.trajectory.full_coupled_adaptive import (
        audit_collision_stiffness,
    )

    network = CollisionNetwork.from_npz(NETWORK)
    audit = audit_collision_stiffness(
        network,
        H_s_inv=4.969651222923834e-14,
        canonical_dlna=8.49e-5,
    )
    assert audit.spectral_radius_s_inv > 1.0e-3
    assert audit.macro_dt_s > 1.0e9
    assert audit.stiffness_number > 1.0e6
    assert audit.requires_block_preconditioner
    assert audit.unpreconditioned_full_macro_production_claim is False


@pytest.mark.slow
def test_real_35_state_directional_pilot_closes_bounded_step() -> None:
    from full_bianchi_hyrec.recoil.original_hyrec_physical_flux import (
        parse_original_hyrec_boundary_snapshot_csv,
    )

    network = CollisionNetwork.from_npz(NETWORK)
    with np.load(BACKGROUND, allow_pickle=False) as data:
        grid = HarmonicGrid.from_directions(
            data["directions"], data["angular_weights"], ell_max=3
        )
    source = parse_original_hyrec_boundary_snapshot_csv(
        ROOT
        / "archive/expanded/Full_Bianchi_HyRec_PR04C0C1A_split_domain_boundary_v0_55"
        / "pr04c_z1100.csv"
    )
    red, blue = source.boundaries
    sequence = BackgroundSnapshotSequence.from_npz(
        BACKGROUND, "Bianchi_II_large_shear"
    )
    snapshot = sequence.snapshot_at_tau(
        0.6072662349590596,
        H_s_inv_override=source.trajectory.H_s_inv,
    )
    transport = ConservativeFrequencyLiouville.from_network(network)
    speeds = transport.face_speeds_from_snapshot(snapshot, grid=grid)
    activity = network.equilibrium_weight / network.mode_measure
    scalar = activity / (1.0 - activity)
    old = scalar[:, None] * (1.0 + 1.0e-5 * grid.directions[:, 0][None, :])
    problem = CoupledCollisionTransportProblem(
        network=network,
        grid=grid,
        transport=transport,
        face_speeds_x_s_inv=speeds,
        native_red_occupation=red.total_occupation,
        native_blue_occupation=blue.total_occupation,
        dt_s=1.0,
    )
    result = problem.implicit_step(
        old,
        nonlinear_rtol=2.0e-10,
        gmres_rtol=1.0e-7,
        gmres_maxiter=40,
    )
    assert result.converged
    assert result.minimum_occupation > 0.0
    assert result.residual_relative < 2.0e-10
    assert result.global_number_relative_residual < 2.0e-12
    assert result.energy_identity_relative_residual < 2.0e-12
    assert result.interface_atom_source_J_m3 == 0.0
    assert result.collision_four_force_residual < 1.0e-18


@pytest.mark.parametrize(
    ("model", "expected_red", "expected_blue"),
    [
        ("Bianchi_II_large_shear", 1, 1),
        ("Bianchi_VI_h_tilted_large_shear", 5, 5),
        ("Bianchi_VI_minus_1_over_9_exceptional", 3, 3),
    ],
)
def test_all_locked_background_sequences_have_source_derived_boundary_roots(
    model: str, expected_red: int, expected_blue: int
) -> None:
    with np.load(BACKGROUND, allow_pickle=False) as data:
        directions = data["directions"]
    sequence = BackgroundSnapshotSequence.from_npz(BACKGROUND, model)
    roots = sequence.boundary_speed_roots(
        tau_start=sequence.tau_range[0],
        tau_end=sequence.tau_range[1],
        directions_normal=directions,
        line=LineBoundaryConfig.lyman_alpha(
            temperature_K=3000.0, x_red=-21.25, x_blue=21.25
        ),
    )
    assert roots.source_derived
    assert roots.red.size == expected_red
    assert roots.blue.size == expected_blue
    assert np.array_equal(roots.red, roots.blue)


def test_real_35_state_coupled_jvp_passes_scale_appropriate_difference() -> None:
    from full_bianchi_hyrec.recoil.original_hyrec_physical_flux import (
        parse_original_hyrec_boundary_snapshot_csv,
    )

    network = CollisionNetwork.from_npz(NETWORK)
    with np.load(BACKGROUND, allow_pickle=False) as data:
        grid = HarmonicGrid.from_directions(
            data["directions"], data["angular_weights"], ell_max=3
        )
    source = parse_original_hyrec_boundary_snapshot_csv(
        ROOT
        / "archive/expanded/Full_Bianchi_HyRec_PR04C0C1A_split_domain_boundary_v0_55"
        / "pr04c_z1100.csv"
    )
    red, blue = source.boundaries
    sequence = BackgroundSnapshotSequence.from_npz(
        BACKGROUND, "Bianchi_VI_h_tilted_large_shear"
    )
    snapshot = sequence.snapshot_at_tau(
        0.195, H_s_inv_override=source.trajectory.H_s_inv
    )
    transport = ConservativeFrequencyLiouville.from_network(network)
    speeds = transport.face_speeds_from_snapshot(snapshot, grid=grid)
    activity = network.equilibrium_weight / network.mode_measure
    scalar = activity / (1.0 - activity)
    old = scalar[:, None] * (1.0 + 1.0e-5 * grid.directions[:, 0][None, :])
    problem = CoupledCollisionTransportProblem(
        network=network,
        grid=grid,
        transport=transport,
        face_speeds_x_s_inv=speeds,
        native_red_occupation=red.total_occupation,
        native_blue_occupation=blue.total_occupation,
        dt_s=1.0,
    )
    rng = np.random.default_rng(104729)
    direction = rng.normal(size=old.shape)
    direction /= np.max(np.abs(direction))
    log_old = np.log(old)
    analytic = problem.residual_jvp(log_old, direction)
    epsilon = 3.0e-5
    finite = (
        problem.residual(log_old + epsilon * direction, old)
        - problem.residual(log_old - epsilon * direction, old)
    ) / (2.0 * epsilon)
    scale = max(
        float(np.max(np.abs(analytic))),
        float(np.max(np.abs(finite))),
        1.0e-300,
    )
    assert float(np.max(np.abs(analytic - finite))) / scale < 1.0e-8

def test_source_temperature_requires_a_dynamic_com_frequency_measure_adapter() -> None:
    from full_bianchi_hyrec.trajectory.full_coupled_adaptive import (
        audit_thermodynamic_grid_consistency,
    )
    from full_bianchi_hyrec.recoil.original_hyrec_physical_flux import (
        parse_original_hyrec_boundary_snapshot_csv,
    )

    network = CollisionNetwork.from_npz(NETWORK)
    source = parse_original_hyrec_boundary_snapshot_csv(
        ROOT
        / "archive/expanded/Full_Bianchi_HyRec_PR04C0C1A_split_domain_boundary_v0_55"
        / "pr04c_z1300.csv"
    )
    line = LineBoundaryConfig.lyman_alpha(
        temperature_K=source.trajectory.TM_eV_rescaled * 11604.518121550082,
        x_red=-21.25,
        x_blue=21.25,
    )
    audit = audit_thermodynamic_grid_consistency(network, source_line=line)
    assert audit.mode_measure_relative_residual > 0.05
    assert audit.outer_face_frequency_relative_mismatch > 1.0e-5
    assert audit.source_conditioned_dynamic_measure_identified is False
    assert audit.requires_network_recompilation
    assert audit.requires_explicit_frequency_remap
    assert audit.bounded_no_go
