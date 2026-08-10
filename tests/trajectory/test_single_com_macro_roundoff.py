from __future__ import annotations

import hashlib
from pathlib import Path

import numpy as np

from full_bianchi_hyrec.background import (
    BackgroundSnapshotSequence,
    BianchiIINormalizedState,
    BianchiReviewBianchiIIProvider,
    OrthogonalGammaLawMatter,
)
from full_bianchi_hyrec.recoil.frequency_liouville import ConservativeFrequencyLiouville
from full_bianchi_hyrec.recoil.nonlinear_bose_release import HarmonicGrid
from full_bianchi_hyrec.recoil.nonlinear_bose_runtime import LineBoundaryConfig
from full_bianchi_hyrec.recoil.original_hyrec_physical_flux import (
    parse_original_hyrec_boundary_snapshot_csv,
)
from full_bianchi_hyrec.trajectory.causal_history import AcceptedRadiationHistory
from full_bianchi_hyrec.trajectory.direct_thermodynamic import load_direct_network_node
from full_bianchi_hyrec.trajectory.full_coupled_adaptive import (
    CoupledCollisionTransportProblem,
)
from full_bianchi_hyrec.trajectory.single_com_macro import (
    assess_roundoff_aware_macro,
    restore_activity_number_ledger,
    solve_roundoff_aware_single_macro,
)
from full_bianchi_hyrec.trajectory.source_derived_parent import (
    build_source_derived_bootstrap_parent,
)


ROOT = Path(__file__).resolve().parents[2]
HISTORY = ROOT / "data/pr05b2_source_history_v060.npz"
NODE = ROOT / "data/z1100_direct_network_node.npz"
BACKGROUND = ROOT / "data/pr01c_background_snapshots_v048.npz"
SOURCE = (
    ROOT
    / "archive/expanded/Full_Bianchi_HyRec_PR04C0C1A_split_domain_boundary_v0_55"
    / "pr04c_z1100.csv"
)
TAU0 = 0.6072662349590596


def _problem_and_parent() -> tuple[CoupledCollisionTransportProblem, np.ndarray]:
    source = parse_original_hyrec_boundary_snapshot_csv(SOURCE)
    with np.load(HISTORY, allow_pickle=False) as data:
        full_history = AcceptedRadiationHistory.from_npz_mapping(data)
    history = full_history.prefix(source.trajectory.iz_local + 1)
    node = load_direct_network_node(NODE)
    with np.load(BACKGROUND, allow_pickle=False) as data:
        grid = HarmonicGrid.from_directions(
            data["directions"], data["angular_weights"], ell_max=3
        )
    locked = BackgroundSnapshotSequence.from_npz(
        BACKGROUND, "Bianchi_II_large_shear"
    )
    start = locked.snapshot_at_tau(TAU0)
    provider = BianchiReviewBianchiIIProvider()
    sequence = provider.snapshots(
        family="II",
        eta_grid=np.asarray([TAU0, TAU0 + history.grid.dlna]),
        initial_state=BianchiIINormalizedState.from_snapshot(start),
        matter_parameters=OrthogonalGammaLawMatter(gamma=4.0 / 3.0),
        H_anchor_s_inv=start.H_s_inv,
        eta_anchor=TAU0,
        cosmic_time_anchor_s=start.cosmic_time_s,
    )
    parent = build_source_derived_bootstrap_parent(
        history=history,
        source_snapshot=source.trajectory,
        source_snapshot_sha256=hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        network_node=node,
        angular_grid=grid,
        background_sequence=sequence,
        background_tau=TAU0,
        branch_id="Bianchi_II:expanding:orthogonal",
    )
    line = LineBoundaryConfig.lyman_alpha(
        temperature_K=node.temperature_K, x_red=-21.25, x_blue=21.25
    )
    # Backward Euler evaluates the geometry at the macro endpoint.  Preserve
    # the exact v0.73 provider provenance and rescale its Hubble rate to the
    # original-HyRec local H anchor.
    endpoint_tau = TAU0 + history.grid.dlna
    endpoint_raw = sequence.snapshot_at_tau(endpoint_tau)
    H_endpoint = source.trajectory.H_s_inv * (
        endpoint_raw.H_s_inv / start.H_s_inv
    )
    endpoint = sequence.snapshot_at_tau(
        endpoint_tau, H_s_inv_override=H_endpoint
    )
    provider_dt = endpoint_raw.cosmic_time_s - start.cosmic_time_s
    dt_s = provider_dt * start.H_s_inv / source.trajectory.H_s_inv
    transport = ConservativeFrequencyLiouville.from_network(
        node.network, reference_line=line
    )
    speeds = transport.face_speeds_from_snapshot(endpoint, grid=grid, line=line)
    problem = CoupledCollisionTransportProblem(
        network=node.network,
        grid=grid,
        transport=transport,
        face_speeds_x_s_inv=speeds,
        native_red_occupation=parent.interface_samples[0].total_occupation,
        native_blue_occupation=parent.interface_samples[1].total_occupation,
        dt_s=dt_s,
    )
    parent.parent.validate_for_production(parent.requirements)
    return problem, np.array(parent.parent.occupation, copy=True)


def test_roundoff_aware_single_com_macro_rejects_parent_and_accepts_root() -> None:
    problem, parent = _problem_and_parent()
    initial = assess_roundoff_aware_macro(
        problem, old_occupation=parent, occupation=parent
    )
    assert initial.gross_backward_error > 1.0e-6
    assert initial.number_relative_residual > 1.0e-3
    assert not initial.passed()

    result = solve_roundoff_aware_single_macro(problem, parent)
    assert result.converged
    assert result.convergence_basis == "roundoff_limited_gross_backward_error_and_ledgers"
    assert len(result.iterations) >= 3
    assert result.assessment.minimum_occupation > 0.0
    assert result.assessment.gross_backward_error < 1.0e-11
    assert result.assessment.number_relative_residual < 1.0e-11
    assert result.assessment.energy_gross_backward_error < 1.0e-11
    assert result.assessment.residual_roundoff_limited
    assert result.assessment.energy_roundoff_limited
    # Keep the cancellation-amplified diagnostics visible rather than
    # laundering them into the hard-gate metric.
    assert result.assessment.net_scaled_residual > 1.0e-11
    assert result.assessment.energy_net_relative_residual > 1.0e-11
    assert result.activity_shift_max_relative < 1.0e-8
    assert result.assessment.pair_loop_action_relative_residual < 1.0e-8
    assert result.assessment.pair_loop_four_force_gross_relative_residual < 1.0e-12
    assert result.assessment.collision_entropy_production <= 0.0


def test_activity_number_restoration_is_tiny_positive_and_exact() -> None:
    problem, parent = _problem_and_parent()
    preliminary = problem.implicit_step(
        parent,
        nonlinear_rtol=1.0e-5,
        gmres_rtol=1.0e-10,
        gmres_restart=80,
        gmres_maxiter=300,
    ).occupation
    restored = restore_activity_number_ledger(
        problem,
        old_occupation=parent,
        occupation=preliminary,
        tolerance=1.0e-11,
    )
    assert restored.number_relative_residual < 1.0e-11
    assert restored.maximum_relative_correction < 1.0e-8
    assert np.min(restored.occupation) > 0.0
