from __future__ import annotations

from pathlib import Path

import numpy as np

from full_bianchi_hyrec.trajectory.direct_thermodynamic import (
    DirectThermodynamicNetworkFamily,
    load_direct_network_node,
)

ROOT = Path(__file__).resolve().parents[2]


def _node(name: str):
    return load_direct_network_node(ROOT / "data" / name)


def test_direct_nodes_are_positive_reciprocal_and_have_be_null() -> None:
    for name in (
        "z900_direct_network_node.npz",
        "z1100_direct_network_node.npz",
        "z1300_direct_network_node.npz",
    ):
        node = _node(name)
        network = node.network
        assert network.pair_moments.shape == (25, 35, 35)
        assert np.min(network.pair_moments[0]) >= 0.0
        assert np.array_equal(network.pair_moments, np.swapaxes(network.pair_moments, 1, 2))
        assert node.number_left_null_relative_residual() < 1.0e-12
        assert node.be_action_relative_residual() < 1.0e-12


def test_direct_family_interpolates_positive_fixed_topology_scalar_graph() -> None:
    family = DirectThermodynamicNetworkFamily(
        [_node("z900_direct_network_node.npz"), _node("z1100_direct_network_node.npz"), _node("z1300_direct_network_node.npz")]
    )
    value, derivative = family.interpolate_scalar_graph(temperature_K=2730.0)
    assert value.shape == (35, 35)
    assert derivative.shape == value.shape
    assert np.all(np.isfinite(value))
    assert np.all(np.isfinite(derivative))
    assert np.min(value) >= 0.0
    assert np.array_equal(value, value.T)
    assert np.array_equal(derivative, derivative.T)


def test_direct_family_exact_node_is_identity() -> None:
    middle = _node("z1100_direct_network_node.npz")
    family = DirectThermodynamicNetworkFamily([_node("z900_direct_network_node.npz"), middle, _node("z1300_direct_network_node.npz")])
    exact = family.exact_node(middle.temperature_K)
    assert exact.node_sha256 == middle.node_sha256
    assert np.array_equal(exact.network.pair_moments, middle.network.pair_moments)
