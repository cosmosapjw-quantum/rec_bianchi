"""Direct source-temperature COM--KHW network family.

PR-05C2C1A stores complete collision networks at source-temperature nodes.
This module loads those immutable nodes and provides the only interpolation
allowed by the v0.65 theory contract: fixed-topology logarithmic interpolation
of positive reciprocal conductances per hydrogen atom in inverse temperature.

No global normalization is fitted.  The locked v0.50 3000 K network remains an
exact byte/content anchor.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import math
from pathlib import Path
from typing import Iterable

import numpy as np

from full_bianchi_hyrec.recoil.nonlinear_bose_runtime import CollisionNetwork


def _is_sha256(value: str) -> bool:
    return len(value) == 64 and all(ch in "0123456789abcdef" for ch in value.lower())


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()



@dataclass(frozen=True)
class WithheldThermodynamicAudit:
    pair_block_count: int
    same_cell_block_count: int
    topology_stable: bool
    scalar_event_mass_weighted_relative: float
    scalar_edge_maximum_relative: float
    maximum_pair_moment_l2_relative: float
    worst_pair_moment_order: int
    same_cell_l2_relative: float
    same_cell_maximum_relative: float

@dataclass(frozen=True)
class DirectThermodynamicNode:
    """One immutable directly compiled thermodynamic network node."""

    network: CollisionNetwork
    temperature_K: float
    nH_m3: float
    context_fingerprint: str
    node_sha256: str
    reference_anchor_exact: bool
    source_path: Path
    block_count: int

    def __post_init__(self) -> None:
        temperature = float(self.temperature_K)
        density = float(self.nH_m3)
        if not (math.isfinite(temperature) and temperature > 0.0):
            raise ValueError("temperature_K must be positive and finite")
        if not (math.isfinite(density) and density > 0.0):
            raise ValueError("nH_m3 must be positive and finite")
        if not _is_sha256(str(self.node_sha256)):
            raise ValueError("node_sha256 must be a hexadecimal SHA-256 digest")
        if not _is_sha256(str(self.context_fingerprint)):
            raise ValueError("context_fingerprint must be a hexadecimal SHA-256 digest")
        object.__setattr__(self, "temperature_K", temperature)
        object.__setattr__(self, "nH_m3", density)
        object.__setattr__(self, "source_path", Path(self.source_path))
        object.__setattr__(self, "block_count", int(self.block_count))

    @property
    def file_sha256(self) -> str:
        """Compatibility digest for the immutable node file."""
        source = Path(self.source_path)
        return _sha256(source) if source.is_file() else self.node_sha256

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

    @classmethod
    def from_npz(
        cls,
        path: str | Path,
        *,
        reference_path: str | Path,
    ) -> "DirectThermodynamicNode":
        source = Path(path)
        reference = CollisionNetwork.from_npz(reference_path)
        with np.load(source, allow_pickle=False) as data:
            labels = data["state_labels"].astype(str)
            intervals = np.asarray(data["state_intervals"], dtype=float)
            if not np.array_equal(labels, reference.state_labels):
                raise ValueError("direct-node state labels do not match the locked reference")
            if not np.array_equal(intervals, reference.state_intervals):
                raise ValueError("direct-node state intervals do not match the locked reference")
            network = CollisionNetwork(
                state_intervals=intervals,
                state_labels=labels,
                pair_moments=data["pair_moments_m3_sInv"],
                same_cell_rates=data["same_cell_rates_sInv"],
                mode_measure=data["mode_measure_m3"],
                equilibrium_weight=data["equilibrium_weight_m3"],
                momentum_scale=data["momentum_scale"],
                inherited_release_policy=reference.inherited_release_policy,
            )
            scalar = network.pair_moments[0]
            pair_blocks = int(np.count_nonzero(np.triu(scalar, k=1) > 0.0))
            same_blocks = int(
                np.count_nonzero(np.max(np.abs(network.same_cell_rates), axis=0) > 0.0)
            )
            return cls(
                network=network,
                temperature_K=float(data["temperature_K"]),
                nH_m3=float(data["nH_m3"]),
                context_fingerprint=str(data["context_fingerprint"].item()),
                node_sha256=str(data["node_sha256"].item()),
                reference_anchor_exact=bool(data["reference_anchor_exact"]),
                source_path=source,
                block_count=pair_blocks + same_blocks,
            )


def load_direct_network_node(path: str | Path) -> DirectThermodynamicNode:
    """Load a direct node using the colocated locked v0.50 reference."""
    source = Path(path)
    if not source.is_file():
        raise FileNotFoundError(source)
    reference = source.parent / "full_scalar_com_khw_v050.npz"
    if not reference.is_file():
        raise FileNotFoundError(reference)
    return DirectThermodynamicNode.from_npz(source, reference_path=reference)


class DirectThermodynamicNetworkFamily:
    """Direct network nodes with fixed-topology positive interpolation."""

    reference_temperature_K = 3000.0
    reference_nH_m3 = 2.5e8

    def __init__(
        self,
        nodes: Iterable[DirectThermodynamicNode],
        *,
        reference: CollisionNetwork | None = None,
    ) -> None:
        ordered = tuple(sorted(nodes, key=lambda node: node.temperature_K))
        if len(ordered) < 2:
            raise ValueError("at least two direct thermodynamic nodes are required")
        temperatures = np.asarray([node.temperature_K for node in ordered])
        if np.any(np.diff(temperatures) <= 0.0):
            raise ValueError("direct-node temperatures must be strictly increasing")
        if reference is None:
            reference = ordered[0].network
        for node in ordered:
            if not np.array_equal(node.network.state_labels, reference.state_labels):
                raise ValueError("direct-node topology does not match the reference labels")
            if node.network.pair_moments.shape != reference.pair_moments.shape:
                raise ValueError("direct-node pair-moment shape mismatch")
        self.nodes = ordered
        self.reference = reference

    @classmethod
    def from_paths(
        cls,
        paths: Iterable[str | Path],
        *,
        reference_path: str | Path,
    ) -> "DirectThermodynamicNetworkFamily":
        reference = CollisionNetwork.from_npz(reference_path)
        nodes = tuple(
            DirectThermodynamicNode.from_npz(path, reference_path=reference_path)
            for path in paths
        )
        return cls(nodes, reference=reference)

    @staticmethod
    def _topology(network: CollisionNetwork) -> np.ndarray:
        return np.asarray(network.pair_moments[0] > 0.0, dtype=bool)

    def _bracket(self, temperature_K: float) -> tuple[DirectThermodynamicNode, DirectThermodynamicNode]:
        temperature = float(temperature_K)
        if not (math.isfinite(temperature) and temperature > 0.0):
            raise ValueError("temperature_K must be positive and finite")
        values = np.asarray([node.temperature_K for node in self.nodes])
        if temperature < values[0] or temperature > values[-1]:
            raise ValueError("temperature is outside the directly compiled node range")
        index = int(np.searchsorted(values, temperature, side="right"))
        if index == 0:
            index = 1
        if index == len(values):
            index = len(values) - 1
        return self.nodes[index - 1], self.nodes[index]

    def exact_node(self, temperature_K: float, *, atol: float = 1.0e-12) -> DirectThermodynamicNode:
        value = float(temperature_K)
        node = min(self.nodes, key=lambda item: abs(item.temperature_K - value))
        if not math.isclose(node.temperature_K, value, rel_tol=0.0, abs_tol=atol):
            raise KeyError(f"no exact direct node at T={value}")
        return node

    def interpolate_scalar_graph(
        self,
        *,
        temperature_K: float,
        nH_m3: float | None = None,
    ) -> tuple[np.ndarray, np.ndarray]:
        """Return scalar conductance and analytic ``d/dT`` at fixed density.

        Positive active edges are interpolated logarithmically per hydrogen atom
        in inverse temperature.  Zero edges remain exactly zero.  Any topology
        change is a discrete event and therefore fails closed here.
        """

        temperature = float(temperature_K)
        left, right = self._bracket(temperature)
        if nH_m3 is None:
            if left is right:
                density = left.nH_m3
            else:
                fraction = (temperature - left.temperature_K) / (right.temperature_K - left.temperature_K)
                density = (1.0 - fraction) * left.nH_m3 + fraction * right.nH_m3
        else:
            density = float(nH_m3)
        if not (math.isfinite(density) and density > 0.0):
            raise ValueError("nH_m3 must be positive and finite")
        mask_left = self._topology(left.network)
        mask_right = self._topology(right.network)
        if not np.array_equal(mask_left, mask_right):
            raise ValueError("thermodynamic interpolation crosses a topology change")

        beta_left = 1.0 / left.temperature_K
        beta_right = 1.0 / right.temperature_K
        beta = 1.0 / temperature
        denominator = beta_right - beta_left
        lam = (beta - beta_left) / denominator

        per_h_left = left.network.pair_moments[0] / left.nH_m3
        per_h_right = right.network.pair_moments[0] / right.nH_m3
        scalar = np.zeros_like(per_h_left)
        derivative = np.zeros_like(per_h_left)
        active = mask_left
        active_left = per_h_left[active]
        active_right = per_h_right[active]
        log_left = np.log(active_left)
        log_right = np.log(active_right)
        # The inverse-temperature midpoint has an exact geometric-mean form.
        # Use it directly to avoid a needless log/exp round-trip on the tiny
        # far-interface conductances used by the audit gate.
        if abs(lam - 0.5) <= 8.0 * np.finfo(float).eps:
            scalar_active = density * np.sqrt(active_left * active_right)
        else:
            log_value = (1.0 - lam) * log_left + lam * log_right
            scalar_active = density * np.exp(log_value)
        dlam_dT = (-1.0 / temperature**2) / denominator
        derivative_active = scalar_active * (log_right - log_left) * dlam_dT
        scalar[active] = scalar_active
        derivative[active] = derivative_active

        # Eliminate platform-dependent one-ulp asymmetry after identical edge
        # arithmetic; the graph is reciprocal by construction.
        scalar = 0.5 * (scalar + scalar.T)
        derivative = 0.5 * (derivative + derivative.T)
        np.fill_diagonal(scalar, 0.0)
        np.fill_diagonal(derivative, 0.0)
        scalar.setflags(write=False)
        derivative.setflags(write=False)
        return scalar, derivative


    def audit_withheld_node(
        self,
        withheld: DirectThermodynamicNode,
    ) -> WithheldThermodynamicAudit:
        """Audit a complete direct node withheld between two family nodes.

        The scalar positive graph is interpolated logarithmically per H.  Signed
        higher pair moments are reconstructed from linearly interpolated
        moment/scalar ratios.  Same-cell entries have a fixed negative sign in
        the locked scalar network and are interpolated logarithmically in
        magnitude per H.  These reconstructions are validation witnesses, not a
        substitute for direct compilation at production nodes.
        """

        left, right = self._bracket(withheld.temperature_K)
        scalar_prediction, _ = self.interpolate_scalar_graph(
            temperature_K=withheld.temperature_K,
            nH_m3=withheld.nH_m3,
        )
        scalar_true = withheld.network.pair_moments[0]
        active = scalar_true > 0.0
        if not np.array_equal(active, self._topology(left.network)) or not np.array_equal(
            active, self._topology(right.network)
        ):
            raise ValueError("withheld-node scalar topology is not fixed")

        beta_left = 1.0 / left.temperature_K
        beta_right = 1.0 / right.temperature_K
        beta = 1.0 / withheld.temperature_K
        lam = (beta - beta_left) / (beta_right - beta_left)

        predicted_pair = np.zeros_like(withheld.network.pair_moments)
        predicted_pair[0] = scalar_prediction
        for order in range(1, predicted_pair.shape[0]):
            ratio_left = np.zeros_like(scalar_true)
            ratio_right = np.zeros_like(scalar_true)
            ratio_left[active] = (
                left.network.pair_moments[order][active]
                / left.network.pair_moments[0][active]
            )
            ratio_right[active] = (
                right.network.pair_moments[order][active]
                / right.network.pair_moments[0][active]
            )
            predicted_pair[order][active] = scalar_prediction[active] * (
                (1.0 - lam) * ratio_left[active] + lam * ratio_right[active]
            )

        same_left = left.network.same_cell_rates / left.nH_m3
        same_right = right.network.same_cell_rates / right.nH_m3
        same_true = withheld.network.same_cell_rates
        topology_left = np.sign(same_left)
        topology_right = np.sign(same_right)
        topology_true = np.sign(same_true)
        topology_stable = bool(
            np.array_equal(topology_left, topology_right)
            and np.array_equal(topology_left, topology_true)
        )
        if not topology_stable:
            raise ValueError("withheld-node same-cell topology is not fixed")
        same_prediction = np.zeros_like(same_true)
        same_active = topology_true != 0.0
        same_prediction[same_active] = (
            topology_true[same_active]
            * withheld.nH_m3
            * np.exp(
                (1.0 - lam) * np.log(np.abs(same_left[same_active]))
                + lam * np.log(np.abs(same_right[same_active]))
            )
        )

        scalar_relative = np.abs(
            scalar_prediction[active] - scalar_true[active]
        ) / scalar_true[active]
        weighted_scalar = float(
            np.sum(np.abs(scalar_prediction - scalar_true))
            / np.sum(np.abs(scalar_true))
        )
        moment_errors: list[tuple[int, float]] = []
        for order in range(predicted_pair.shape[0]):
            norm = float(np.linalg.norm(withheld.network.pair_moments[order]))
            if norm > 0.0:
                moment_errors.append(
                    (
                        order,
                        float(
                            np.linalg.norm(
                                predicted_pair[order]
                                - withheld.network.pair_moments[order]
                            )
                            / norm
                        ),
                    )
                )
        worst_order, worst_pair_error = max(moment_errors, key=lambda item: item[1])
        same_norm = float(np.linalg.norm(same_true))
        same_l2 = float(np.linalg.norm(same_prediction - same_true) / same_norm)
        same_relative = np.abs(
            same_prediction[same_active] - same_true[same_active]
        ) / np.abs(same_true[same_active])
        pair_blocks = int(np.count_nonzero(np.triu(scalar_true, k=1) > 0.0))
        same_blocks = int(
            np.count_nonzero(np.max(np.abs(same_true), axis=0) > 0.0)
        )
        return WithheldThermodynamicAudit(
            pair_block_count=pair_blocks,
            same_cell_block_count=same_blocks,
            topology_stable=topology_stable,
            scalar_event_mass_weighted_relative=weighted_scalar,
            scalar_edge_maximum_relative=float(np.max(scalar_relative)),
            maximum_pair_moment_l2_relative=worst_pair_error,
            worst_pair_moment_order=worst_order,
            same_cell_l2_relative=same_l2,
            same_cell_maximum_relative=float(np.max(same_relative)),
        )

    def network_at(
        self,
        *,
        temperature_K: float,
        nH_m3: float,
    ) -> DirectThermodynamicNode:
        temperature = float(temperature_K)
        density = float(nH_m3)
        if temperature == self.reference_temperature_K and density == self.reference_nH_m3:
            scalar = self.reference.pair_moments[0]
            block_count = int(np.count_nonzero(np.triu(scalar, k=1) > 0.0)) + int(
                np.count_nonzero(
                    np.max(np.abs(self.reference.same_cell_rates), axis=0) > 0.0
                )
            )
            return DirectThermodynamicNode(
                network=self.reference,
                temperature_K=temperature,
                nH_m3=density,
                context_fingerprint="0" * 64,
                node_sha256="0" * 64,
                reference_anchor_exact=True,
                source_path=Path("LOCKED_V050_REFERENCE"),
                block_count=block_count,
            )

        for node in self.nodes:
            if temperature == node.temperature_K and density == node.nH_m3:
                return node
        raise ValueError(
            "a complete interpolated network is not yet defined; use "
            "interpolate_scalar_graph or a directly compiled node"
        )


__all__ = ["DirectThermodynamicNetworkFamily", "DirectThermodynamicNode", "WithheldThermodynamicAudit", "load_direct_network_node"]
