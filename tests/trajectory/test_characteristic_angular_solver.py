from __future__ import annotations

from pathlib import Path

import numpy as np

from full_bianchi_hyrec.background.sequence import BackgroundSnapshotSequence
from full_bianchi_hyrec.trajectory.characteristic_angular import (
    CharacteristicAngularSolver,
    IsotropicTransferCoefficients,
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
