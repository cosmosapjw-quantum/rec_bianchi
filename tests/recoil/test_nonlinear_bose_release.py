import numpy as np
import pytest

from full_bianchi_hyrec.recoil.nonlinear_bose_release import (
    HarmonicGrid,
    apply_nonlinear_bose_jvp,
    apply_nonlinear_bose_operator,
    bose_free_energy,
    bose_photon_number,
)


def synthetic_grid() -> HarmonicGrid:
    directions = np.asarray(
        [
            [1, 0, 0],
            [-1, 0, 0],
            [0, 1, 0],
            [0, -1, 0],
            [0, 0, 1],
            [0, 0, -1],
        ],
        dtype=float,
    )
    return HarmonicGrid.from_directions(
        directions,
        np.full(6, 1 / 6),
        ell_max=1,
    )


def synthetic_pair_moments() -> np.ndarray:
    moments = np.zeros((2, 2, 2))
    moments[0, 0, 1] = moments[0, 1, 0] = 0.7
    moments[1, 0, 1] = moments[1, 1, 0] = 0.1
    return moments


def test_discrete_be_family_is_exact_null():
    grid = synthetic_grid()
    mode = np.asarray([2.0, 3.0])
    equilibrium = np.asarray([0.4, 0.9])
    activity = equilibrium / mode
    chemical_activity = 0.8
    isotropic = chemical_activity * activity / (1 - chemical_activity * activity)
    occupation = np.repeat(isotropic[:, None], grid.n_angle, axis=1)

    result = apply_nonlinear_bose_operator(
        occupation,
        mode_measure=mode,
        equilibrium_weight=equilibrium,
        pair_moments=synthetic_pair_moments(),
        same_cell_rates=np.zeros((2, 2)),
        grid=grid,
    )

    assert np.max(np.abs(result.occupation_action)) < 1e-14
    assert abs(result.number_residual) < 1e-14


def test_nonlinear_pair_conserves_number_and_dissipates_free_energy():
    grid = synthetic_grid()
    mode = np.asarray([2.0, 3.0])
    equilibrium = np.asarray([0.4, 0.9])
    occupation = np.asarray(
        [
            [0.25, 0.10, 0.18, 0.12, 0.22, 0.11],
            [0.02, 0.08, 0.03, 0.07, 0.04, 0.06],
        ]
    )

    result = apply_nonlinear_bose_operator(
        occupation,
        mode_measure=mode,
        equilibrium_weight=equilibrium,
        pair_moments=synthetic_pair_moments(),
        same_cell_rates=np.zeros((2, 2)),
        grid=grid,
    )

    assert abs(result.number_residual) < 1e-13
    assert result.entropy_production <= 1e-13
    assert np.linalg.norm(result.Q_gamma + result.Q_atom) == 0

    epsilon = 1e-6
    plus = bose_free_energy(
        occupation + epsilon * result.occupation_action,
        mode_measure=mode,
        equilibrium_weight=equilibrium,
        grid=grid,
    )
    minus = bose_free_energy(
        occupation - epsilon * result.occupation_action,
        mode_measure=mode,
        equilibrium_weight=equilibrium,
        grid=grid,
    )
    finite_difference = (plus - minus) / (2 * epsilon)
    assert np.isclose(
        finite_difference,
        result.entropy_production,
        rtol=2e-9,
        atol=2e-11,
    )


def test_exact_jvp_matches_central_finite_difference_and_number_left_null():
    grid = synthetic_grid()
    mode = np.asarray([2.0, 3.0])
    equilibrium = np.asarray([0.4, 0.9])
    occupation = np.asarray(
        [
            [0.25, 0.10, 0.18, 0.12, 0.22, 0.11],
            [0.02, 0.08, 0.03, 0.07, 0.04, 0.06],
        ]
    )
    perturbation = np.asarray(
        [
            [0.03, -0.01, 0.02, -0.015, 0.01, -0.02],
            [-0.004, 0.008, -0.002, 0.006, -0.007, 0.003],
        ]
    )
    kwargs = {
        "mode_measure": mode,
        "equilibrium_weight": equilibrium,
        "pair_moments": synthetic_pair_moments(),
        "same_cell_rates": np.zeros((2, 2)),
        "grid": grid,
    }

    exact = apply_nonlinear_bose_jvp(occupation, perturbation, **kwargs)
    epsilon = 1e-5
    plus = apply_nonlinear_bose_operator(
        occupation + epsilon * perturbation,
        **kwargs,
    ).occupation_action
    minus = apply_nonlinear_bose_operator(
        occupation - epsilon * perturbation,
        **kwargs,
    ).occupation_action
    finite_difference = (plus - minus) / (2 * epsilon)
    relative = np.linalg.norm(exact.occupation_action_jvp - finite_difference) / (
        np.linalg.norm(finite_difference) + 1e-300
    )

    assert relative < 2e-10
    assert abs(exact.number_residual_jvp) < 2e-13


def test_same_frequency_bose_factors_cancel_to_linear_angular_damping():
    grid = synthetic_grid()
    mode = np.asarray([2.0])
    equilibrium = np.asarray([0.4])
    occupation = np.asarray([[0.3, 0.1, 0.2, 0.12, 0.25, 0.15]])
    same = np.asarray([[0.0], [-0.5]])
    moments = np.zeros((2, 1, 1))

    first = apply_nonlinear_bose_operator(
        occupation,
        mode_measure=mode,
        equilibrium_weight=equilibrium,
        pair_moments=moments,
        same_cell_rates=same,
        grid=grid,
    )
    second = apply_nonlinear_bose_operator(
        4 * occupation,
        mode_measure=mode,
        equilibrium_weight=equilibrium,
        pair_moments=moments,
        same_cell_rates=same,
        grid=grid,
    )

    assert np.linalg.norm(
        second.occupation_action - 4 * first.occupation_action
    ) < 1e-13
    assert abs(first.number_residual) < 1e-14


def test_number_function_uses_frequency_and_angular_measures():
    grid = synthetic_grid()
    occupation = np.ones((2, grid.n_angle))
    assert bose_photon_number(
        occupation,
        mode_measure=np.asarray([2.0, 3.0]),
        grid=grid,
    ) == 5.0


def test_harmonic_grid_copies_primitives_without_mutating_caller_flags():
    """Catch caller aliasing that can stale the grid's derived harmonic matrices."""

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
    weights = np.full(6, 1.0 / 6.0)
    original_directions = directions.copy()
    original_weights = weights.copy()

    grid = HarmonicGrid.from_directions(directions, weights, ell_max=1)
    normalized_weights = grid.weights.copy()

    assert directions.flags.writeable
    assert weights.flags.writeable
    directions[0] = [0.0, 1.0, 0.0]
    weights[0] = 0.25
    assert np.array_equal(grid.directions, original_directions)
    assert np.allclose(normalized_weights, original_weights, rtol=0.0, atol=1.0e-16)
    assert np.array_equal(grid.weights, normalized_weights)
    with pytest.raises(ValueError):
        grid.directions.setflags(write=True)


@pytest.mark.parametrize("field", ["directions", "weights"])
def test_harmonic_grid_rejects_nonfinite_primitives(field):
    """Catch NaN primitives passing comparison-only validation."""

    directions = np.asarray(
        [[1.0, 0.0, 0.0], [-1.0, 0.0, 0.0], [0.0, 1.0, 0.0]]
    )
    weights = np.full(3, 1.0 / 3.0)
    if field == "directions":
        directions[0, 0] = np.nan
    else:
        weights[0] = np.nan

    with pytest.raises(ValueError, match="finite"):
        HarmonicGrid.from_directions(directions, weights, ell_max=0)


def test_harmonic_grid_raw_constructor_rejects_stale_derived_matrices():
    """Catch the public dataclass constructor pairing new primitives with stale matrices."""

    grid = synthetic_grid()
    permuted_directions = np.roll(grid.directions, 1, axis=0)

    with pytest.raises(ValueError, match="derived"):
        HarmonicGrid(
            permuted_directions,
            grid.weights,
            grid.ell_max,
            grid.lm,
            grid.synthesis,
            grid.analysis,
            grid.ell_of_mode,
            grid.gram_residual,
        )


def test_harmonic_grid_rejects_numerically_incoherent_near_rank_grid():
    epsilon = 1.0e-8
    directions = np.asarray(
        [
            [1.0, 0.0, 0.0],
            [-1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0],
            [0.0, -1.0, epsilon],
        ]
    )
    directions /= np.linalg.norm(directions, axis=1)[:, None]

    with pytest.raises(ValueError, match="rank deficient|ill-conditioned|coherence"):
        HarmonicGrid.from_directions(
            directions,
            np.ones(4),
            ell_max=1,
        )
