from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
import importlib.util

import numpy as np
import pytest
from scipy.optimize import root_scalar

MODULE = Path(__file__).resolve().parents[1] / "physical_inputs.py"


def load_module():
    assert MODULE.is_file(), "physical_inputs.py is missing"
    spec = importlib.util.spec_from_file_location("rec_physical_inputs", MODULE)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


@dataclass(frozen=True)
class Snapshot:
    temperature_K: float
    doppler_width_Hz: float
    state: np.ndarray


@dataclass(frozen=True)
class Solution:
    weights: np.ndarray
    dual: np.ndarray


def declared_inputs(width=2.5e10):
    return {
        "snapshot": Snapshot(temperature_K=3000.0, doppler_width_Hz=width,
                             state=np.array([0.2, 0.8], dtype=np.float64)),
        "frequency_measure": {"id": "com-p0-v1", "faces_Hz": [1.0, 2.0, 3.0]},
        "atomic_constants": {"lyman_alpha_eV": 10.2, "ratio": Fraction(3, 2)},
        "source_provenance": "hyrec-oct2012:locked",
        "frame": "hydrogen-orthonormal-v1",
        "time_variable": "proper_seconds_future",
        "event_topology": {"cross_edges": [[135, 136], [143, 144]]},
    }


def test_input_identity_binds_doppler_width_and_required_conventions():
    mod = load_module()
    first = mod.input_identity(declared_inputs(2.5e10))
    second = mod.input_identity(declared_inputs(2.6e10))
    assert first != second
    missing = declared_inputs()
    del missing["frame"]
    with pytest.raises(ValueError, match="incomplete"):
        mod.input_identity(missing)


def test_checkpoint_rejects_payload_or_physical_input_change():
    mod = load_module()
    payload = b"checkpoint-v2"
    inputs = declared_inputs()
    envelope = mod.seal_checkpoint(payload, inputs)
    assert mod.validate_checkpoint(payload, inputs, envelope) == payload
    with pytest.raises(ValueError, match="mismatch"):
        mod.validate_checkpoint(payload + b"x", inputs, envelope)
    with pytest.raises(ValueError, match="mismatch"):
        mod.validate_checkpoint(payload, declared_inputs(2.7e10), envelope)


def test_moving_deposition_jvp_matches_independent_finite_difference():
    mod = load_module()
    matrix = np.array([[1.0, 2.0]])
    d_matrix = np.array([[0.1, -0.2]])
    prior = np.array([1.0, 1.0])
    d_log_prior = np.array([0.03, -0.04])
    dual = np.array([0.0])
    weights = prior * np.exp(matrix.T @ dual)
    target = matrix @ weights
    d_target = np.array([0.07])
    solution = Solution(weights=weights, dual=dual)

    tangent = mod.moving_deposition_jvp(
        matrix, solution, d_matrix, d_target, d_log_prior
    )

    def solved_weights(epsilon):
        moved_matrix = matrix + epsilon * d_matrix
        moved_prior = prior * np.exp(epsilon * d_log_prior)
        moved_target = target + epsilon * d_target

        def residual(lam):
            q = moved_prior * np.exp(moved_matrix[0] * lam)
            return float((moved_matrix @ q - moved_target).item())

        root = root_scalar(residual, x0=0.0, x1=1.0e-6).root
        return moved_prior * np.exp(moved_matrix[0] * root)

    epsilon = 1.0e-6
    finite_difference = (solved_weights(epsilon) - solved_weights(-epsilon)) / (2 * epsilon)
    np.testing.assert_allclose(tangent, finite_difference, rtol=2e-8, atol=2e-10)
    np.testing.assert_allclose(matrix @ tangent + d_matrix @ weights, d_target,
                               rtol=2e-12, atol=2e-12)


def test_moving_deposition_jvp_fails_closed_on_rank_loss():
    mod = load_module()
    matrix = np.array([[1.0, 1.0], [2.0, 2.0]])
    solution = Solution(weights=np.ones(2), dual=np.zeros(2))
    with pytest.raises(ArithmeticError, match="ill-conditioned"):
        mod.moving_deposition_jvp(
            matrix, solution, np.zeros_like(matrix), np.zeros(2), np.zeros(2)
        )
