from pathlib import Path

import numpy as np
import pytest

from full_bianchi_hyrec.background.sequence import BackgroundSnapshotSequence
from full_bianchi_hyrec.trajectory.characteristic_angular import (
    BianchiCharacteristicFaceSolver,
    constant_coefficient_transfer,
    constant_coefficient_transfer_jvp,
)

ROOT = Path(__file__).resolve().parents[2]
BACKGROUND = ROOT / "data/pr01c_background_snapshots_v048.npz"
MODELS = (
    "Bianchi_II_large_shear",
    "Bianchi_VI_h_tilted_large_shear",
    "Bianchi_VI_minus_1_over_9_exceptional",
)
DIRECTION = np.array([0.3, 0.4, np.sqrt(0.75)])
NU0 = 2.466e15


def _snapshot(model: str):
    sequence = BackgroundSnapshotSequence.from_npz(BACKGROUND, model)
    tau = 0.5 * (sequence.tau[0] + sequence.tau[-1])
    return sequence.snapshot_at_tau(tau)


@pytest.mark.parametrize("model", MODELS)
def test_actual_bianchi_free_characteristic_reaches_face_and_preserves_occupation(model):
    solver = BianchiCharacteristicFaceSolver(_snapshot(model))
    initial = solver.local_characteristic(DIRECTION)
    target = NU0 * np.exp(np.sign(initial.R_hydrogen_s_inv) * 2.0e-4)
    result = solver.trace_to_frequency_face(
        direction_normal=DIRECTION,
        frequency_initial_Hz=NU0,
        frequency_target_Hz=target,
        f_initial=0.27,
        emissivity_s_inv=0.0,
        opacity_s_inv=0.0,
        n_steps=48,
    )
    assert result.frequency_relative_residual < 3.0e-13
    assert result.f_face == 0.27
    assert np.isclose(np.linalg.norm(result.direction_normal), 1.0, rtol=0.0, atol=2e-14)
    assert np.isclose(np.linalg.norm(result.direction_hydrogen), 1.0, rtol=0.0, atol=2e-14)
    assert result.minimum_doppler_factor > 0.0


def test_constant_positive_source_matches_formal_solution():
    f_out = constant_coefficient_transfer(
        f_initial=0.2,
        emissivity_s_inv=3.0e-12,
        opacity_s_inv=5.0e-12,
        travel_time_s=2.0e10,
    )
    transmission = np.exp(-0.1)
    expected = transmission * 0.2 + (3.0 / 5.0) * (1.0 - transmission)
    assert np.isclose(f_out, expected, rtol=2e-15, atol=0.0)
    assert f_out > 0.0


def test_constant_transfer_jvp_matches_central_difference():
    kwargs = dict(
        f_initial=0.31,
        emissivity_s_inv=2.0e-12,
        opacity_s_inv=7.0e-12,
        travel_time_s=1.5e10,
    )
    direction = dict(
        d_f_initial=-0.19,
        d_emissivity_s_inv=0.8e-12,
        d_opacity_s_inv=-0.6e-12,
        d_travel_time_s=2.0e8,
    )
    analytic = constant_coefficient_transfer_jvp(**kwargs, **direction)
    eps = 2.0e-6
    plus = constant_coefficient_transfer(
        **{key: kwargs[key] + eps * direction[f"d_{key}"] for key in kwargs}
    )
    minus = constant_coefficient_transfer(
        **{key: kwargs[key] - eps * direction[f"d_{key}"] for key in kwargs}
    )
    finite_difference = (plus - minus) / (2.0 * eps)
    assert np.isclose(analytic, finite_difference, rtol=4e-8, atol=2e-10)


def test_characteristic_direction_has_fourth_order_refinement_witness():
    solver = BianchiCharacteristicFaceSolver(_snapshot("Bianchi_VI_h_tilted_large_shear"))
    initial = solver.local_characteristic(DIRECTION)
    target = NU0 * np.exp(np.sign(initial.R_hydrogen_s_inv) * 1.0e-2)
    coarse = solver.trace_to_frequency_face(
        direction_normal=DIRECTION,
        frequency_initial_Hz=NU0,
        frequency_target_Hz=target,
        f_initial=0.1,
        n_steps=8,
    )
    medium = solver.trace_to_frequency_face(
        direction_normal=DIRECTION,
        frequency_initial_Hz=NU0,
        frequency_target_Hz=target,
        f_initial=0.1,
        n_steps=16,
    )
    fine = solver.trace_to_frequency_face(
        direction_normal=DIRECTION,
        frequency_initial_Hz=NU0,
        frequency_target_Hz=target,
        f_initial=0.1,
        n_steps=64,
    )
    err_coarse = np.linalg.norm(coarse.direction_normal - fine.direction_normal)
    err_medium = np.linalg.norm(medium.direction_normal - fine.direction_normal)
    assert err_coarse / err_medium > 8.0


def test_unreachable_frequency_face_fails_closed():
    solver = BianchiCharacteristicFaceSolver(_snapshot("Bianchi_II_large_shear"))
    initial = solver.local_characteristic(DIRECTION)
    wrong_target = NU0 * np.exp(-np.sign(initial.R_hydrogen_s_inv) * 1.0e-4)
    with pytest.raises(ValueError, match="not forward-reachable"):
        solver.trace_to_frequency_face(
            direction_normal=DIRECTION,
            frequency_initial_Hz=NU0,
            frequency_target_Hz=wrong_target,
            f_initial=0.2,
        )
