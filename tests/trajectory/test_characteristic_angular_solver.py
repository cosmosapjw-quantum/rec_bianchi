from __future__ import annotations

from pathlib import Path

import mpmath as mp
import numpy as np
import pytest

from full_bianchi_hyrec.background.sequence import BackgroundSnapshotSequence
from full_bianchi_hyrec.trajectory.characteristic_angular import (
    BianchiCharacteristicFaceSolver,
    CharacteristicAngularSolver,
    IsotropicTransferCoefficients,
    constant_coefficient_transfer,
    constant_coefficient_transfer_jvp,
)

ROOT = Path(__file__).resolve().parents[2]
BACKGROUND = ROOT / "data" / "pr01c_background_snapshots_v048.npz"


def _sequence(model: str) -> BackgroundSnapshotSequence:
    return BackgroundSnapshotSequence.from_npz(BACKGROUND, model)


def test_source_free_characteristic_preserves_positive_occupation() -> None:
    sequence = _sequence("Bianchi_II_large_shear")
    solver = CharacteristicAngularSolver(sequence)
    tau0, tau1 = sequence.tau_range
    result = solver.trace_to_face(
        tau_start=tau0,
        tau_end=tau1,
        direction_hydrogen=np.array([0.2, -0.3, 0.9]),
        face_frequency_Hz=2.466e15,
        initial_occupation=1.0e-12,
        coefficients=IsotropicTransferCoefficients.zero(),
        n_step=256,
    )
    assert result.occupation_face > 0.0
    assert result.minimum_doppler_factor > 0.0
    assert abs(result.occupation_face - 1.0e-12) < 2.0e-25
    assert abs(np.linalg.norm(result.initial_direction_hydrogen) - 1.0) < 2.0e-12


def test_manufactured_source_refines_at_second_order_or_better() -> None:
    sequence = _sequence("Bianchi_VI_h_tilted_large_shear")
    solver = CharacteristicAngularSolver(sequence)
    tau0, tau1 = sequence.tau_range

    coeff = IsotropicTransferCoefficients(
        emissivity_s_inv=lambda tau, nu: 2.0e-13 * (1.0 + 0.1 * tau),
        opacity_s_inv=lambda tau, nu: 3.0e-13 * (1.0 + 0.05 * tau),
    )
    reference = solver.trace_to_face(
        tau_start=tau0,
        tau_end=tau1,
        direction_hydrogen=np.array([0.5, 0.4, 0.75]),
        face_frequency_Hz=2.466e15,
        initial_occupation=2.0e-12,
        coefficients=coeff,
        n_step=2048,
    )
    coarse = solver.trace_to_face(
        tau_start=tau0,
        tau_end=tau1,
        direction_hydrogen=np.array([0.5, 0.4, 0.75]),
        face_frequency_Hz=2.466e15,
        initial_occupation=2.0e-12,
        coefficients=coeff,
        n_step=64,
    )
    fine = solver.trace_to_face(
        tau_start=tau0,
        tau_end=tau1,
        direction_hydrogen=np.array([0.5, 0.4, 0.75]),
        face_frequency_Hz=2.466e15,
        initial_occupation=2.0e-12,
        coefficients=coeff,
        n_step=128,
    )
    e0 = abs(coarse.occupation_face - reference.occupation_face)
    e1 = abs(fine.occupation_face - reference.occupation_face)
    assert e1 > 0.0
    assert e0 / e1 > 3.0
    assert fine.occupation_face > 0.0


@pytest.mark.parametrize("opacity", [1.0e-6, 1.0e-8, 1.0e-10, 1.0e-20])
def test_constant_transfer_small_optical_depth_matches_mpmath_value_and_jvp(
    opacity: float,
) -> None:
    """Catch cancellation in the opacity derivative near zero optical depth."""

    f_initial = 0.7
    emissivity = 1.3
    travel_time = 2.0
    with mp.workdps(100):
        chi_mp = mp.mpf(str(opacity))
        time_mp = mp.mpf(str(travel_time))
        f_mp = mp.mpf(str(f_initial))
        emissivity_mp = mp.mpf(str(emissivity))
        attenuation = mp.exp(-chi_mp * time_mp)
        absorbed = -mp.expm1(-chi_mp * time_mp)
        value_reference = attenuation * f_mp + emissivity_mp * absorbed / chi_mp
        jvp_reference = (
            -time_mp * attenuation * f_mp
            + emissivity_mp
            * (time_mp * attenuation * chi_mp - absorbed)
            / chi_mp**2
        )

    value = constant_coefficient_transfer(
        f_initial=f_initial,
        emissivity_s_inv=emissivity,
        opacity_s_inv=opacity,
        travel_time_s=travel_time,
    )
    jvp = constant_coefficient_transfer_jvp(
        f_initial=f_initial,
        emissivity_s_inv=emissivity,
        opacity_s_inv=opacity,
        travel_time_s=travel_time,
        d_opacity_s_inv=1.0,
    )

    assert np.isclose(value, float(value_reference), rtol=2.0e-15, atol=0.0)
    assert np.isclose(jvp, float(jvp_reference), rtol=2.0e-14, atol=2.0e-15)


@pytest.mark.parametrize(
    "invalid_update",
    [
        {"f_initial": -1.0},
        {"emissivity_s_inv": -1.0},
        {"opacity_s_inv": -1.0},
        {"n_steps": 64.5},
        {"n_steps": True},
        {"time_safety_factor": float("nan")},
        {"time_safety_factor": 0.0},
    ],
)
def test_zero_distance_characteristic_validates_all_transfer_and_policy_inputs(
    invalid_update: dict[str, float],
) -> None:
    """Catch the equal-frequency shortcut bypassing scalar and policy validation."""

    sequence = _sequence("Bianchi_II_large_shear")
    solver = BianchiCharacteristicFaceSolver(
        sequence.snapshot_at_tau(float(np.mean(sequence.tau_range)))
    )
    arguments = {
        "direction_normal": np.array([1.0, 0.0, 0.0]),
        "frequency_initial_Hz": 2.466e15,
        "frequency_target_Hz": 2.466e15,
        "f_initial": 0.2,
        "emissivity_s_inv": 0.0,
        "opacity_s_inv": 0.0,
        "n_steps": 64,
        "time_safety_factor": 4.0,
    }
    arguments.update(invalid_update)

    with pytest.raises(ValueError):
        solver.trace_to_frequency_face(**arguments)


def test_constant_transfer_jvp_rejects_nonfinite_tangent() -> None:
    """Catch NaN derivative seeds escaping an otherwise validated primal call."""

    with pytest.raises(ValueError, match="tangent"):
        constant_coefficient_transfer_jvp(
            f_initial=0.2,
            emissivity_s_inv=0.3,
            opacity_s_inv=0.4,
            travel_time_s=0.5,
            d_opacity_s_inv=float("nan"),
        )
