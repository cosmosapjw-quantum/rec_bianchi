from __future__ import annotations

import math
from pathlib import Path

import numpy as np
import pytest

from full_bianchi_hyrec.background import (
    BackgroundSnapshotSequence,
    BianchiIINormalizedState,
    BianchiReviewBianchiIIProvider,
    OrthogonalGammaLawMatter,
)
from full_bianchi_hyrec.recoil.nonlinear_bose_release import HarmonicGrid
from full_bianchi_hyrec.recoil.original_hyrec_physical_flux import (
    parse_original_hyrec_boundary_snapshot_csv,
)
from full_bianchi_hyrec.trajectory.accepted_parent import ParentEvidenceClass
from full_bianchi_hyrec.trajectory.causal_history import (
    AcceptedRadiationHistory,
    FutureHistoryEndpointError,
)
from full_bianchi_hyrec.trajectory.direct_thermodynamic import load_direct_network_node
from full_bianchi_hyrec.trajectory.source_derived_parent import (
    OriginalHyRecPointCharacteristicEvaluator,
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


def _inputs():
    source = parse_original_hyrec_boundary_snapshot_csv(SOURCE)
    with np.load(HISTORY, allow_pickle=False) as data:
        full_history = AcceptedRadiationHistory.from_npz_mapping(data)
    # The source snapshot at iz_local has already been solved and is therefore
    # the last accepted scalar slice for the next canonical interval.
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
    return source, history, node, grid, sequence


def test_point_characteristic_reproduces_locked_red_blue_interfaces() -> None:
    source, history, _node, _grid, _sequence = _inputs()
    evaluator = OriginalHyRecPointCharacteristicEvaluator(
        history=history,
        fsR=source.trajectory.fsR,
        meR=source.trajectory.meR,
    )
    eta_target = -math.log1p(source.trajectory.z)
    for expected in source.boundaries:
        sample = evaluator.evaluate(
            eta_target=eta_target,
            target_frequency_Hz=expected.interface_frequency_Hz,
            radiation_temperature_eV_rescaled=source.trajectory.TR_eV_rescaled,
        )
        assert sample.source_index == expected.source_index
        assert sample.left_index == expected.history_index_left
        assert sample.right_index == expected.history_index_right
        assert abs(sample.fraction - expected.interpolation_fraction) < 2.0e-12
        assert abs(sample.total_occupation / expected.total_occupation - 1.0) < 5.0e-13


def test_point_characteristic_rejects_future_history_endpoint() -> None:
    source, history, _node, _grid, _sequence = _inputs()
    stale = history.prefix(history.accepted_count - 1)
    evaluator = OriginalHyRecPointCharacteristicEvaluator(
        history=stale,
        fsR=source.trajectory.fsR,
        meR=source.trajectory.meR,
    )
    with pytest.raises(FutureHistoryEndpointError):
        evaluator.evaluate(
            eta_target=-math.log1p(source.trajectory.z),
            target_frequency_Hz=source.boundaries[0].interface_frequency_Hz,
            radiation_temperature_eV_rescaled=source.trajectory.TR_eV_rescaled,
        )


def test_source_derived_bootstrap_parent_is_deterministic_positive_and_provenance_locked() -> None:
    source, history, node, grid, sequence = _inputs()
    first = build_source_derived_bootstrap_parent(
        history=history,
        source_snapshot=source.trajectory,
        source_snapshot_sha256=__import__("hashlib").sha256(SOURCE.read_bytes()).hexdigest(),
        network_node=node,
        angular_grid=grid,
        background_sequence=sequence,
        background_tau=TAU0,
        branch_id="Bianchi_II:expanding:orthogonal",
    )
    second = build_source_derived_bootstrap_parent(
        history=history,
        source_snapshot=source.trajectory,
        source_snapshot_sha256=__import__("hashlib").sha256(SOURCE.read_bytes()).hexdigest(),
        network_node=node,
        angular_grid=grid,
        background_sequence=sequence,
        background_tau=TAU0,
        branch_id="Bianchi_II:expanding:orthogonal",
    )

    parent = first.parent
    assert parent.evidence_class is ParentEvidenceClass.SOURCE_DERIVED_ACCEPTED
    assert parent.accepted_history_index == source.trajectory.iz_local
    assert parent.accepted_history_sha256 == history.sha256
    assert parent.occupation.shape == (node.network.n_state, grid.n_angle)
    assert np.min(parent.occupation) > 0.0
    assert np.max(np.ptp(parent.occupation, axis=1)) == 0.0
    assert parent.metadata["claim_boundary"] == "BOOTSTRAP_PARENT_NOT_COUPLED_MACRO_ENDPOINT"
    assert parent.metadata["reconstruction"] == "POINT_CHARACTERISTIC_SCALAR_HISTORY_V1"
    assert parent.metadata["initial_angular_condition"] == "ISOTROPIC_HYDROGEN_FRAME_V1"
    parent.validate_for_production(first.requirements)

    assert first.parent.to_bytes() == second.parent.to_bytes()
    assert first.parent.sha256 == second.parent.sha256
    assert first.requirements == second.requirements
    assert first.atomic_state_sha256 == second.atomic_state_sha256
    assert first.background_sequence_sha256 == second.background_sequence_sha256
    assert first.interface_sha256 == second.interface_sha256


def test_bootstrap_parent_removes_the_q1_provenance_mismatch_without_claiming_macro_acceptance() -> None:
    source, history, node, grid, sequence = _inputs()
    result = build_source_derived_bootstrap_parent(
        history=history,
        source_snapshot=source.trajectory,
        source_snapshot_sha256=__import__("hashlib").sha256(SOURCE.read_bytes()).hexdigest(),
        network_node=node,
        angular_grid=grid,
        background_sequence=sequence,
        background_tau=TAU0,
        branch_id="Bianchi_II:expanding:orthogonal",
    )
    q1 = node.network.activity_weight / (1.0 - node.network.activity_weight)
    scalar = result.parent.occupation[:, 0]
    assert np.median(scalar / q1) > 100.0
    assert 900.0 < np.median(result.activity) < 1100.0
    assert not result.coupled_macro_endpoint
