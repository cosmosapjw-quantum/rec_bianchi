"""Entropy-metric graph preconditioner candidate for scalar Bose collisions.

The candidate is deliberately kept separate from the production solver because
v0.66 measured it to be slower than the diagonal/AP baseline.  It remains a
reproducible audit implementation of the v0.65 theorem contract: the scalar
conductance graph is reciprocal and nonnegative, its Laplacian has the exact
constant-activity null mode, and the positive entropy metric regularizes that
mode in a shifted implicit solve.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class EntropyGraphPreconditioner:
    graph_laplacian: np.ndarray
    entropy_weight: np.ndarray
    shifted_matrix: np.ndarray

    @classmethod
    def from_scalar_graph(
        cls,
        *,
        conductance: np.ndarray,
        occupation: np.ndarray,
        mode_measure: np.ndarray,
        shift: float,
        stiffness: float,
        symmetry_tolerance: float = 1.0e-13,
    ) -> "EntropyGraphPreconditioner":
        graph = np.asarray(conductance, dtype=float)
        f = np.asarray(occupation, dtype=float)
        mode = np.asarray(mode_measure, dtype=float)
        if graph.ndim != 2 or graph.shape[0] != graph.shape[1]:
            raise ValueError("conductance must be square")
        size = graph.shape[0]
        if f.shape != (size,) or mode.shape != (size,):
            raise ValueError("occupation and mode_measure must match the graph")
        if not np.all(np.isfinite(graph)) or not np.all(np.isfinite(f + mode)):
            raise ValueError("preconditioner inputs must be finite")
        if np.min(graph) < 0.0 or np.min(f) < 0.0 or np.min(mode) <= 0.0:
            raise ValueError("conductance/occupation must be nonnegative and mode positive")
        scale = max(float(np.max(np.abs(graph))), 1.0)
        if np.max(np.abs(graph - graph.T)) > symmetry_tolerance * scale:
            raise ValueError("conductance graph must be reciprocal")
        if shift <= 0.0 or stiffness < 0.0:
            raise ValueError("shift must be positive and stiffness nonnegative")

        symmetric = 0.5 * (graph + graph.T)
        symmetric = symmetric.copy()
        np.fill_diagonal(symmetric, 0.0)
        laplacian = np.diag(np.sum(symmetric, axis=1)) - symmetric
        entropy_weight = mode * f * (1.0 + f)
        if np.min(entropy_weight) <= 0.0:
            raise ValueError("strictly positive occupation is required for the entropy metric")
        shifted = float(shift) * np.diag(entropy_weight) + float(stiffness) * laplacian
        laplacian.setflags(write=False)
        entropy_weight.setflags(write=False)
        shifted.setflags(write=False)
        return cls(laplacian, entropy_weight, shifted)

    def solve(self, right_hand_side: np.ndarray) -> np.ndarray:
        rhs = np.asarray(right_hand_side, dtype=float)
        if rhs.shape != self.entropy_weight.shape or not np.all(np.isfinite(rhs)):
            raise ValueError("right_hand_side has the wrong shape or nonfinite values")
        solution = np.linalg.solve(self.shifted_matrix, rhs)
        # The candidate is intentionally tested in very stiff regimes where the
        # activity mode and relaxing modes differ by many orders of magnitude.
        # A small fixed iterative-refinement pass makes the audit solve reflect
        # the original residual rather than the factorization's scaled error.
        for _ in range(2):
            residual = rhs - self.shifted_matrix @ solution
            if np.linalg.norm(residual, ord=np.inf) <= 8.0 * np.finfo(float).eps * max(
                np.linalg.norm(rhs, ord=np.inf), 1.0
            ):
                break
            solution = solution + np.linalg.solve(self.shifted_matrix, residual)
        return solution


__all__ = ["EntropyGraphPreconditioner"]
