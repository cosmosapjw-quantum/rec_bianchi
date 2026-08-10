from __future__ import annotations

import hashlib
import math
from pathlib import Path
import tarfile

import numpy as np
import pytest

from full_bianchi_hyrec.background import (
    BackgroundChartEventRequired,
    BackgroundSnapshotSequence,
    BianchiIINormalizedState,
    BianchiReviewBianchiIIProvider,
    OrthogonalGammaLawMatter,
    TiltedPerfectFluidRequest,
    UnsupportedBackgroundBranchError,
)
from full_bianchi_hyrec.background.evolution_provider import (
    BIANCHI_REVIEW_ARCHIVE_SHA256,
    BIANCHI_REVIEW_CLASS_A_SOURCE_SHA256,
    BIANCHI_REVIEW_TYPE_IX_D_SOURCE_SHA256,
)


ROOT = Path(__file__).resolve().parents[2]
TAU0 = 0.6072662349590596
DELTA_ETA = 8.49e-5


def _locked_sequence() -> BackgroundSnapshotSequence:
    return BackgroundSnapshotSequence.from_npz(
        ROOT / "data/pr01c_background_snapshots_v048.npz",
        "Bianchi_II_large_shear",
    )


def _provider_sequence():
    locked = _locked_sequence()
    start = locked.snapshot_at_tau(TAU0)
    provider = BianchiReviewBianchiIIProvider()
    sequence = provider.snapshots(
        family="II",
        eta_grid=np.asarray([TAU0, TAU0 + DELTA_ETA]),
        initial_state=BianchiIINormalizedState.from_snapshot(start),
        matter_parameters=OrthogonalGammaLawMatter(gamma=4.0 / 3.0),
        H_anchor_s_inv=start.H_s_inv,
        eta_anchor=TAU0,
        cosmic_time_anchor_s=start.cosmic_time_s,
    )
    return locked, provider, sequence


def _normalized_state(snapshot):
    H = snapshot.H_s_inv
    sigma = snapshot.sigma_s_inv / H
    curvature = snapshot.N_s_inv / H
    return np.asarray(
        [
            -0.5 * sigma[0, 0],
            (sigma[1, 1] - sigma[2, 2]) / (2.0 * math.sqrt(3.0)),
            curvature[0, 0],
        ]
    )


def test_bianchi_ii_provider_matches_locked_v048_over_one_macro() -> None:
    locked, provider, sequence = _provider_sequence()
    reference = locked.snapshot_at_tau(TAU0 + DELTA_ETA)
    predicted = sequence.snapshot_at_tau(TAU0 + DELTA_ETA)

    error = np.abs(_normalized_state(predicted) - _normalized_state(reference))
    assert np.max(error) < 1.0e-5
    assert error[0] < 3.0e-7
    assert error[1] < 4.0e-8
    assert error[2] < 3.0e-7
    assert predicted.branch_flags["provider_validated_bianchi_ii"]
    assert predicted.provenance["archive_sha256"].startswith("6bb094d3")
    assert sequence.source_sha256 == provider.source_sha256
    assert max(abs(value) for value in predicted.constraint_residuals.values()) < 1.0e-11


def test_provider_reconstructs_physical_units_and_time_chart() -> None:
    _locked, _provider, sequence = _provider_sequence()
    first = sequence.snapshot_at_tau(TAU0)
    last = sequence.snapshot_at_tau(TAU0 + DELTA_ETA)
    state = _normalized_state(first)
    expected_sigma = first.H_s_inv * np.diag(
        [
            -2.0 * state[0],
            state[0] + math.sqrt(3.0) * state[1],
            state[0] - math.sqrt(3.0) * state[1],
        ]
    )
    expected_N = first.H_s_inv * np.diag([state[2], 0.0, 0.0])

    assert np.array_equal(first.sigma_s_inv, expected_sigma)
    assert np.array_equal(first.N_s_inv, expected_N)
    assert np.array_equal(first.A_s_inv, np.zeros(3))
    assert np.array_equal(first.beta_H, np.zeros(3))
    midpoint_H = 0.5 * (first.H_s_inv + last.H_s_inv)
    trapezoid_dt = DELTA_ETA / midpoint_H
    actual_dt = last.cosmic_time_s - first.cosmic_time_s
    assert abs(actual_dt / trapezoid_dt - 1.0) < 2.0e-8
    assert first.provenance["time_coordinate"] == "eta=tau=ln(ell/ell0)"


def test_bianchi_ix_h_zero_requires_d_normalized_event() -> None:
    provider = BianchiReviewBianchiIIProvider()
    with pytest.raises(BackgroundChartEventRequired) as captured:
        provider.snapshots(
            family="IX",
            eta_grid=[0.0, 1.0e-4],
            initial_state=object(),
            matter_parameters=OrthogonalGammaLawMatter(gamma=4.0 / 3.0),
            H_anchor_s_inv=1.0,
            eta_anchor=0.0,
        )
    event = captured.value.event
    assert event.event_type == "H_ZERO_RECOLLAPSE"
    assert event.required_chart == "type_ix_D_normalized"


def test_exceptional_tilted_provider_request_is_explicitly_unsupported() -> None:
    provider = BianchiReviewBianchiIIProvider()
    with pytest.raises(UnsupportedBackgroundBranchError, match="no fallback"):
        provider.snapshots(
            family="VI*_-1/9",
            eta_grid=[0.0, 1.0e-4],
            initial_state=object(),
            matter_parameters=TiltedPerfectFluidRequest(
                gamma=4.0 / 3.0,
                beta=np.asarray([0.1, 0.0, 0.0]),
            ),
            H_anchor_s_inv=1.0,
            eta_anchor=0.0,
        )


def test_provider_source_archive_and_equation_bytes_are_locked() -> None:
    archive = (
        ROOT
        / "archive/inputs/bianchi_background_solver_v87/bianchireview87.tar.gz"
    )
    assert hashlib.sha256(archive.read_bytes()).hexdigest() == BIANCHI_REVIEW_ARCHIVE_SHA256
    with tarfile.open(archive, "r:gz") as handle:
        class_a = handle.extractfile("./bianchi/charts/class_a.py")
        type_ix = handle.extractfile("./bianchi/charts/type_ix_d.py")
        assert class_a is not None and type_ix is not None
        assert hashlib.sha256(class_a.read()).hexdigest() == BIANCHI_REVIEW_CLASS_A_SOURCE_SHA256
        assert hashlib.sha256(type_ix.read()).hexdigest() == BIANCHI_REVIEW_TYPE_IX_D_SOURCE_SHA256
