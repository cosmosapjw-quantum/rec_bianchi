from __future__ import annotations

import numpy as np

from full_bianchi_hyrec.trajectory.entropy_preconditioner import (
    EntropyGraphPreconditioner,
)


def test_entropy_graph_preconditioner_preserves_activity_nullspace() -> None:
    conductance = np.array(
        [[0.0, 2.0, 1.0], [2.0, 0.0, 3.0], [1.0, 3.0, 0.0]],
        dtype=float,
    )
    occupation = np.array([0.2, 0.3, 0.4])
    mode = np.array([1.0, 2.0, 1.5])
    pre = EntropyGraphPreconditioner.from_scalar_graph(
        conductance=conductance,
        occupation=occupation,
        mode_measure=mode,
        shift=1.0,
        stiffness=1.0e8,
    )
    assert np.linalg.norm(pre.graph_laplacian @ np.ones(3), ord=np.inf) < 1.0e-14
    assert np.all(pre.entropy_weight > 0.0)
    assert np.all(np.linalg.eigvalsh(pre.shifted_matrix) > 0.0)


def test_entropy_graph_preconditioner_solve_has_small_normwise_backward_error() -> None:
    conductance = np.array([[0.0, 1.0], [1.0, 0.0]])
    pre = EntropyGraphPreconditioner.from_scalar_graph(
        conductance=conductance,
        occupation=np.array([0.1, 0.2]),
        mode_measure=np.ones(2),
        shift=0.7,
        stiffness=1.0e6,
    )
    rhs = np.array([1.2, -0.4])
    solution = pre.solve(rhs)
    residual = pre.shifted_matrix @ solution - rhs
    scale = (
        np.linalg.norm(pre.shifted_matrix, ord=np.inf)
        * np.linalg.norm(solution, ord=np.inf)
        + np.linalg.norm(rhs, ord=np.inf)
    )
    assert np.linalg.norm(residual, ord=np.inf) / scale < 2.0e-15
