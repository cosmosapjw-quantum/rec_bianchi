from pathlib import Path

import numpy as np
import pytest

from full_bianchi_hyrec.trajectory.direct_thermodynamic import (
    DirectThermodynamicNetworkFamily,
    DirectThermodynamicNode,
)

ROOT = Path(__file__).resolve().parents[2]
NODE_PATHS = [
    ROOT / "data/pr05c2c1a_z900_direct_network_node_v066.npz",
    ROOT / "data/pr05c2c1a_z1100_direct_network_node_v066.npz",
    ROOT / "data/pr05c2c1a_z1300_direct_network_node_v066.npz",
]
REFERENCE = ROOT / "data/full_scalar_com_khw_v050.npz"


def test_direct_nodes_recover_complete_positive_reciprocal_graphs():
    nodes = [
        DirectThermodynamicNode.from_npz(path, reference_path=REFERENCE)
        for path in NODE_PATHS
    ]
    assert [node.network.n_state for node in nodes] == [35, 35, 35]
    assert [node.network.pair_moments.shape[0] for node in nodes] == [25, 25, 25]
    assert [node.block_count for node in nodes] == [459, 459, 459]
    for node in nodes:
        pair = node.network.pair_moments
        assert np.array_equal(pair, np.swapaxes(pair, 1, 2))
        scalar = pair[0]
        off_diagonal = scalar[~np.eye(35, dtype=bool)]
        assert np.min(off_diagonal[off_diagonal > 0.0]) > 0.0
        assert node.network.same_cell_rates.shape == (25, 35)
        assert len(node.node_sha256) == 64


def test_direct_family_inverse_temperature_log_interpolation_and_density_split():
    family = DirectThermodynamicNetworkFamily.from_paths(
        NODE_PATHS,
        reference_path=REFERENCE,
    )
    left, right = family.nodes[0], family.nodes[1]
    beta_mid = 0.5 * (1.0 / left.temperature_K + 1.0 / right.temperature_K)
    temperature = 1.0 / beta_mid
    density = 0.5 * (left.nH_m3 + right.nH_m3)
    scalar, derivative = family.interpolate_scalar_graph(
        temperature_K=temperature,
        nH_m3=density,
    )
    expected = density * np.sqrt(
        (left.network.pair_moments[0] / left.nH_m3)
        * (right.network.pair_moments[0] / right.nH_m3)
    )
    assert np.allclose(scalar, expected, rtol=2e-14, atol=0.0)
    assert np.array_equal(scalar, scalar.T)
    assert np.array_equal(derivative, derivative.T)
    assert np.all(np.diag(scalar) == 0.0)


def test_direct_family_exact_3000K_anchor_is_byte_identical():
    family = DirectThermodynamicNetworkFamily.from_paths(
        NODE_PATHS,
        reference_path=REFERENCE,
    )
    anchor = family.network_at(temperature_K=3000.0, nH_m3=2.5e8)
    reference = family.reference
    assert anchor.reference_anchor_exact is True
    assert np.array_equal(anchor.network.pair_moments, reference.pair_moments)
    assert np.array_equal(anchor.network.same_cell_rates, reference.same_cell_rates)
    assert np.array_equal(anchor.network.mode_measure, reference.mode_measure)
    assert np.array_equal(anchor.network.equilibrium_weight, reference.equilibrium_weight)


def test_direct_family_fails_closed_across_topology_change(tmp_path):
    original = DirectThermodynamicNode.from_npz(
        NODE_PATHS[0], reference_path=REFERENCE
    )
    with np.load(NODE_PATHS[1], allow_pickle=False) as data:
        payload = {key: data[key] for key in data.files}
    pair = np.array(payload["pair_moments_m3_sInv"], copy=True)
    pair[:, 0, 1] = 0.0
    pair[:, 1, 0] = 0.0
    payload["pair_moments_m3_sInv"] = pair
    changed = tmp_path / "changed.npz"
    np.savez(changed, **payload)
    other = DirectThermodynamicNode.from_npz(changed, reference_path=REFERENCE)
    family = DirectThermodynamicNetworkFamily((original, other), reference=original.network)
    with pytest.raises(ValueError, match="topology"):
        family.interpolate_scalar_graph(
            temperature_K=0.5 * (original.temperature_K + other.temperature_K),
            nH_m3=0.5 * (original.nH_m3 + other.nH_m3),
        )


def test_full_withheld_node_audit_covers_all_pair_and_same_cell_blocks():
    nodes = [
        DirectThermodynamicNode.from_npz(path, reference_path=REFERENCE)
        for path in NODE_PATHS
    ]
    family = DirectThermodynamicNetworkFamily(
        (nodes[0], nodes[2]),
        reference=DirectThermodynamicNetworkFamily.from_paths(
            NODE_PATHS, reference_path=REFERENCE
        ).reference,
    )
    audit = family.audit_withheld_node(nodes[1])
    assert audit.pair_block_count == 442
    assert audit.same_cell_block_count == 17
    assert audit.topology_stable is True
    assert audit.scalar_event_mass_weighted_relative < 1.0e-4
    assert audit.scalar_edge_maximum_relative < 9.0e-3
    assert audit.maximum_pair_moment_l2_relative < 2.5e-4
    assert audit.worst_pair_moment_order == 23
    assert audit.same_cell_l2_relative < 9.0e-3
    assert audit.same_cell_maximum_relative < 1.7e-2
