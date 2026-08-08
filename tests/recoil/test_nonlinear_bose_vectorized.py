from __future__ import annotations

import numpy as np

from full_bianchi_hyrec.recoil.nonlinear_bose_release import (
    HarmonicGrid,
    apply_nonlinear_bose_action,
    apply_nonlinear_bose_jvp,
    apply_nonlinear_bose_jvp_batched,
    apply_nonlinear_bose_jvp_pair_loop,
    apply_nonlinear_bose_operator,
    apply_nonlinear_bose_operator_pair_loop,
)


def _grid() -> HarmonicGrid:
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
    return HarmonicGrid.from_directions(
        directions, np.full(6, 1.0 / 6.0), ell_max=1
    )


def _inputs():
    rng = np.random.default_rng(6401)
    n_state = 5
    grid = _grid()
    mode = 1.0 + rng.random(n_state)
    activity = 1.0e-3 * (1.0 + 0.1 * rng.random(n_state))
    equilibrium = mode * activity
    pair = np.zeros((2, n_state, n_state))
    scalar = rng.random((n_state, n_state))
    scalar = 0.5 * (scalar + scalar.T)
    np.fill_diagonal(scalar, 0.0)
    pair[0] = 2.0e-3 * scalar
    anis = rng.normal(scale=0.1, size=(n_state, n_state))
    anis = 0.5 * (anis + anis.T)
    np.fill_diagonal(anis, 0.0)
    pair[1] = pair[0] * anis
    same = np.zeros((2, n_state))
    same[1] = -1.0e-3 * rng.random(n_state)
    occupation = 0.01 + 0.1 * rng.random((n_state, grid.n_angle))
    return grid, mode, equilibrium, pair, same, occupation


def _kwargs(grid, mode, equilibrium, pair, same):
    return {
        "mode_measure": mode,
        "equilibrium_weight": equilibrium,
        "pair_moments": pair,
        "same_cell_rates": same,
        "grid": grid,
    }


def test_vectorized_operator_matches_pair_loop_oracle() -> None:
    grid, mode, equilibrium, pair, same, occupation = _inputs()
    kwargs = _kwargs(grid, mode, equilibrium, pair, same)
    expected = apply_nonlinear_bose_operator_pair_loop(occupation, **kwargs)
    actual = apply_nonlinear_bose_operator(occupation, **kwargs)
    assert np.allclose(actual.occupation_action, expected.occupation_action, rtol=2e-13, atol=2e-15)
    assert np.allclose(actual.number_action, expected.number_action, rtol=2e-13, atol=2e-15)
    assert np.allclose(actual.action_coefficients, expected.action_coefficients, rtol=2e-13, atol=2e-15)
    assert abs(actual.number_residual - expected.number_residual) < 2e-14
    assert abs(actual.entropy_production - expected.entropy_production) < 2e-14
    assert np.allclose(actual.Q_gamma, expected.Q_gamma, rtol=2e-13, atol=2e-15)
    assert np.allclose(actual.Q_atom, expected.Q_atom, rtol=2e-13, atol=2e-15)
    assert abs(actual.gross_action_scale - expected.gross_action_scale) < 2e-13 * max(abs(expected.gross_action_scale), 1.0)


def test_action_only_path_matches_full_operator() -> None:
    grid, mode, equilibrium, pair, same, occupation = _inputs()
    kwargs = _kwargs(grid, mode, equilibrium, pair, same)
    expected = apply_nonlinear_bose_operator(occupation, **kwargs).occupation_action
    actual = apply_nonlinear_bose_action(occupation, **kwargs)
    assert np.allclose(actual, expected, rtol=2e-13, atol=2e-15)


def test_vectorized_jvp_matches_pair_loop_oracle() -> None:
    grid, mode, equilibrium, pair, same, occupation = _inputs()
    rng = np.random.default_rng(6402)
    direction = rng.normal(size=occupation.shape)
    kwargs = _kwargs(grid, mode, equilibrium, pair, same)
    expected = apply_nonlinear_bose_jvp_pair_loop(occupation, direction, **kwargs)
    actual = apply_nonlinear_bose_jvp(occupation, direction, **kwargs)
    assert np.allclose(actual.occupation_action_jvp, expected.occupation_action_jvp, rtol=3e-13, atol=3e-15)
    assert np.allclose(actual.number_action_jvp, expected.number_action_jvp, rtol=3e-13, atol=3e-15)
    assert abs(actual.number_residual_jvp - expected.number_residual_jvp) < 3e-14


def test_batched_jvp_matches_individual_vectorized_jvps() -> None:
    grid, mode, equilibrium, pair, same, occupation = _inputs()
    rng = np.random.default_rng(6403)
    directions = rng.normal(size=(7,) + occupation.shape)
    kwargs = _kwargs(grid, mode, equilibrium, pair, same)
    batched = apply_nonlinear_bose_jvp_batched(occupation, directions, **kwargs)
    expected = np.stack(
        [apply_nonlinear_bose_jvp(occupation, item, **kwargs).occupation_action_jvp for item in directions]
    )
    assert np.allclose(batched.occupation_action_jvp, expected, rtol=3e-13, atol=3e-15)
    assert np.allclose(
        batched.number_action_jvp,
        np.stack([apply_nonlinear_bose_jvp(occupation, item, **kwargs).number_action_jvp for item in directions]),
        rtol=3e-13,
        atol=3e-15,
    )
