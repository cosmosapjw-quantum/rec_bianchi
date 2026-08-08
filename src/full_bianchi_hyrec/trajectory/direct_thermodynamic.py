"""Direct source-temperature COM--KHW network nodes and safe interpolation.

This module consumes immutable node files produced by the expensive direct
compiler.  It intentionally exposes only exact-node full networks and
fixed-topology log interpolation of the scalar reciprocal event graph.  Signed
harmonic coefficients are never interpolated as though they were positive
conductances.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import math
from pathlib import Path
from typing import Iterable

import numpy as np

from full_bianchi_hyrec.recoil.nonlinear_bose_runtime import CollisionNetwork
from full_bianchi_hyrec.theory.pr05c2c0_closure import geometric_conductance_interpolate

_RELEASE_POLICY = {
    "finite_tilt_beta0p3": 12,
    "nonlinear_even_shear": 20,
    "mixed_tilt_shear": 12,
    "red_blue_crossing": 24,
    "high_occupation_stress": 12,
}


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


@dataclass(frozen=True)
class DirectThermodynamicNode:
    network: CollisionNetwork
    temperature_K: float
    nH_m3: float
    context_fingerprint: str
    node_sha256: str
    file_sha256: str
    reference_anchor_exact: bool
    source_path: str

    def number_left_null_relative_residual(self) -> float:
        scalar = self.network.pair_moments[0]
        scale = max(float(np.max(np.abs(scalar))), 1.0e-300)
        return float(np.max(np.abs(scalar - scalar.T)) / scale)

    def be_action_relative_residual(self, *, activity: float = 0.5) -> float:
        z = self.network.activity_weight
        if np.any(activity * z >= 1.0):
            raise ValueError("activity is outside the Bose--Einstein domain")
        occupation = activity * z / (1.0 - activity * z)
        phi = occupation / (z * (1.0 + occupation))
        scalar = self.network.pair_moments[0]
        flux = scalar * (1.0 + occupation[:, None]) * (1.0 + occupation[None, :]) * (
            phi[None, :] - phi[:, None]
        )
        scale = max(float(np.max(np.abs(scalar))), 1.0e-300)
        return float(np.max(np.abs(flux)) / scale)


def load_direct_network_node(path: str | Path) -> DirectThermodynamicNode:
    source = Path(path)
    if not source.is_file():
        raise FileNotFoundError(source)
    with np.load(source, allow_pickle=False) as data:
        required = {
            "temperature_K",
            "nH_m3",
            "context_fingerprint",
            "state_intervals",
            "state_labels",
            "pair_moments_m3_sInv",
            "same_cell_rates_sInv",
            "mode_measure_m3",
            "equilibrium_weight_m3",
            "momentum_scale",
            "node_sha256",
            "reference_anchor_exact",
        }
        missing = required.difference(data.files)
        if missing:
            raise ValueError(f"direct node is missing keys: {sorted(missing)}")
        network = CollisionNetwork(
            state_intervals=data["state_intervals"],
            state_labels=data["state_labels"],
            pair_moments=data["pair_moments_m3_sInv"],
            same_cell_rates=data["same_cell_rates_sInv"],
            mode_measure=data["mode_measure_m3"],
            equilibrium_weight=data["equilibrium_weight_m3"],
            momentum_scale=data["momentum_scale"],
            inherited_release_policy=_RELEASE_POLICY,
        )
        temperature = float(data["temperature_K"])
        density = float(data["nH_m3"])
        context = str(data["context_fingerprint"])
        node_sha = str(data["node_sha256"])
        anchor = bool(data["reference_anchor_exact"])
    if temperature <= 0.0 or density <= 0.0:
        raise ValueError("thermodynamic node must have positive T and nH")
    return DirectThermodynamicNode(
        network=network,
        temperature_K=temperature,
        nH_m3=density,
        context_fingerprint=context,
        node_sha256=node_sha,
        file_sha256=_sha256(source),
        reference_anchor_exact=anchor,
        source_path=str(source.resolve()),
    )


class DirectThermodynamicNetworkFamily:
    """Ordered immutable direct nodes with fixed-topology scalar interpolation."""

    def __init__(self, nodes: Iterable[DirectThermodynamicNode]) -> None:
        ordered = tuple(sorted(nodes, key=lambda item: item.temperature_K))
        if len(ordered) < 2:
            raise ValueError("at least two direct nodes are required")
        temperatures = np.asarray([item.temperature_K for item in ordered])
        if np.any(np.diff(temperatures) <= 0.0):
            raise ValueError("direct node temperatures must be unique")
        labels = ordered[0].network.state_labels
        intervals = ordered[0].network.state_intervals
        for node in ordered[1:]:
            if not np.array_equal(node.network.state_labels, labels):
                raise ValueError("direct node labels differ")
            if not np.array_equal(node.network.state_intervals, intervals):
                raise ValueError("direct node intervals differ")
        self.nodes = ordered
        self.temperatures_K = temperatures

    def exact_node(self, temperature_K: float, *, atol: float = 1.0e-12) -> DirectThermodynamicNode:
        value = float(temperature_K)
        index = int(np.argmin(np.abs(self.temperatures_K - value)))
        node = self.nodes[index]
        if not math.isclose(node.temperature_K, value, rel_tol=0.0, abs_tol=atol):
            raise KeyError(f"no exact direct node at T={value}")
        return node

    def _bracket(self, temperature_K: float) -> tuple[DirectThermodynamicNode, DirectThermodynamicNode, float]:
        value = float(temperature_K)
        if not math.isfinite(value) or value < self.temperatures_K[0] or value > self.temperatures_K[-1]:
            raise ValueError("temperature lies outside the direct node family")
        right = int(np.searchsorted(self.temperatures_K, value, side="right"))
        if right == 0:
            return self.nodes[0], self.nodes[0], 0.0
        if right >= len(self.nodes):
            return self.nodes[-1], self.nodes[-1], 0.0
        left = right - 1
        if value == self.temperatures_K[left]:
            return self.nodes[left], self.nodes[left], 0.0
        fraction = (value - self.temperatures_K[left]) / (
            self.temperatures_K[right] - self.temperatures_K[left]
        )
        return self.nodes[left], self.nodes[right], float(fraction)

    def interpolate_scalar_graph(self, *, temperature_K: float) -> tuple[np.ndarray, np.ndarray]:
        left, right, fraction = self._bracket(temperature_K)
        if left is right:
            return left.network.pair_moments[0].copy(), np.zeros_like(left.network.pair_moments[0])
        return geometric_conductance_interpolate(
            left.network.pair_moments[0],
            right.network.pair_moments[0],
            fraction=fraction,
            coordinate_span=right.temperature_K - left.temperature_K,
        )


__all__ = [
    "DirectThermodynamicNetworkFamily",
    "DirectThermodynamicNode",
    "load_direct_network_node",
]
