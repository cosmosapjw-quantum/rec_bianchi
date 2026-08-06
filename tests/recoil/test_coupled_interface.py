from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest
from scipy.constants import c, h

from full_bianchi_hyrec.recoil.nonlinear_bose_runtime import CollisionNetwork
from full_bianchi_hyrec.recoil.split_domain_exchange import (
    ExchangeDirection,
    ExchangePacket,
    InterfaceSide,
)


ROOT = Path(__file__).resolve().parents[2]
NETWORK_PATH = ROOT / "data/full_scalar_com_khw_v050.npz"


def _packet(side: InterfaceSide, *, flux: float = 2.5e-14) -> ExchangePacket:
    frequency = 2.465e15 if side is InterfaceSide.RED else 2.467e15
    direction = (
        ExchangeDirection.COM_TO_NATIVE
        if side is InterfaceSide.RED
        else ExchangeDirection.NATIVE_TO_COM
    )
    reference = 0.1 * flux
    distortion = flux - reference
    return ExchangePacket(
        side=side,
        direction=direction,
        interface_x=-21.25 if side is InterfaceSide.RED else 21.25,
        interface_frequency_Hz=frequency,
        total_number_flux_per_H_s=flux,
        reference_number_flux_per_H_s=reference,
        distortion_number_flux_per_H_s=distortion,
        photon_energy_flux_W_per_H=h * frequency * flux,
        reference_photon_energy_flux_W_per_H=h * frequency * reference,
        distortion_photon_energy_flux_W_per_H=h * frequency * distortion,
        atom_energy_flux_W_per_H=0.0,
        source_snapshot_z=1100.0,
    )


def test_far_boundary_adapter_pins_exact_outer_state_registry():
    from full_bianchi_hyrec.recoil.coupled_interface import FarBoundaryAdapter

    network = CollisionNetwork.from_npz(NETWORK_PATH)
    adapter = FarBoundaryAdapter.from_network(network)
    red = adapter.for_side(InterfaceSide.RED)
    blue = adapter.for_side(InterfaceSide.BLUE)

    assert (red.label, red.index, red.interval, red.face_x) == (
        "FR00",
        29,
        (-21.25, -16.25),
        -21.25,
    )
    assert (blue.label, blue.index, blue.interval, blue.face_x) == (
        "FB02",
        34,
        (16.25, 21.25),
        21.25,
    )
    assert red.mode_measure_m3 == network.mode_measure[29]
    assert blue.mode_measure_m3 == network.mode_measure[34]
    assert red.centroid_frequency_Hz == network.momentum_scale[29] * c / h
    assert blue.centroid_frequency_Hz == network.momentum_scale[34] * c / h


def test_accumulator_is_positive_component_exact_and_restart_stable():
    from full_bianchi_hyrec.recoil.coupled_interface import (
        BoundaryTransferAccumulator,
    )

    packet = _packet(InterfaceSide.BLUE)
    accumulator = BoundaryTransferAccumulator.from_packet(packet, dt_s=1.25e5)
    assert accumulator.number_per_H == packet.total_number_flux_per_H_s * 1.25e5
    assert accumulator.energy_J_per_H == packet.photon_energy_flux_W_per_H * 1.25e5
    assert accumulator.energy_J_per_H == h * accumulator.interface_frequency_Hz * accumulator.number_per_H

    encoded = json.dumps(accumulator.to_dict(), sort_keys=True, separators=(",", ":"))
    decoded = BoundaryTransferAccumulator.from_dict(json.loads(encoded))
    assert decoded == accumulator
    assert decoded.sha256 == accumulator.sha256


def test_accumulator_rejects_bad_side_direction_and_nonpositive_duration():
    from full_bianchi_hyrec.recoil.coupled_interface import (
        BoundaryTransferAccumulator,
    )

    packet = _packet(InterfaceSide.RED)
    with pytest.raises(ValueError, match="dt_s"):
        BoundaryTransferAccumulator.from_packet(packet, dt_s=0.0)

    values = BoundaryTransferAccumulator.from_packet(packet, dt_s=1.0).to_dict()
    values["direction"] = ExchangeDirection.NATIVE_TO_COM.value
    with pytest.raises(ValueError, match="direction"):
        BoundaryTransferAccumulator.from_dict(values)


def test_boundary_number_deposition_matches_integrated_packet_exactly():
    from full_bianchi_hyrec.recoil.coupled_interface import (
        BoundaryTransferAccumulator,
        FarBoundaryAdapter,
    )

    network = CollisionNetwork.from_npz(NETWORK_PATH)
    adapter = FarBoundaryAdapter.from_network(network)
    weights = np.asarray([0.05, 0.15, 0.3, 0.5])
    n_H_m3 = 2.5018675437302318e8

    for side, sign in ((InterfaceSide.RED, -1.0), (InterfaceSide.BLUE, 1.0)):
        accumulator = BoundaryTransferAccumulator.from_packet(
            _packet(side), dt_s=1.0e5
        )
        increment = adapter.occupation_increment(
            accumulator,
            n_H_m3=n_H_m3,
            angular_weights=weights,
        )
        assert increment.shape == (network.n_state, len(weights))
        number_change = float(
            np.sum(network.mode_measure[:, None] * increment * weights[None, :])
        )
        assert number_change == pytest.approx(
            sign * n_H_m3 * accumulator.number_per_H,
            rel=3e-15,
            abs=0.0,
        )
        nonzero = np.flatnonzero(np.any(increment != 0.0, axis=1))
        expected = 29 if side is InterfaceSide.RED else 34
        assert np.array_equal(nonzero, np.asarray([expected]))
