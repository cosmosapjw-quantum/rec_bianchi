from __future__ import annotations

import json

import numpy as np
import pytest
from scipy.constants import h

from full_bianchi_hyrec.recoil.split_domain_exchange import (
    ExchangeDirection,
    ExchangePacket,
    InterfaceSide,
    OperatorOwner,
    OwnershipRegistry,
    ProcessOwnership,
    SplitDomainExchangeOperator,
    default_ownership_registry,
)


def _packet(*, side: InterfaceSide = InterfaceSide.BLUE) -> ExchangePacket:
    number = 2.5e-17
    frequency = 2.466_067_55e15
    reference = 1.7e-17
    distortion = number - reference
    direction = (
        ExchangeDirection.NATIVE_TO_COM
        if side is InterfaceSide.BLUE
        else ExchangeDirection.COM_TO_NATIVE
    )
    return ExchangePacket(
        side=side,
        direction=direction,
        interface_x=21.25 if side is InterfaceSide.BLUE else -21.25,
        interface_frequency_Hz=frequency,
        total_number_flux_per_H_s=number,
        reference_number_flux_per_H_s=reference,
        distortion_number_flux_per_H_s=distortion,
        photon_energy_flux_W_per_H=h * frequency * number,
        reference_photon_energy_flux_W_per_H=h * frequency * reference,
        distortion_photon_energy_flux_W_per_H=h * frequency * distortion,
        atom_energy_flux_W_per_H=-h * frequency * number,
        source_snapshot_z=1100.0,
    )


def test_default_ownership_registry_has_exactly_one_owner_per_process() -> None:
    registry = default_ownership_registry()
    registry.validate()
    assert registry.owner_of("cross_interface_red") is OperatorOwner.INTERFACE
    assert registry.owner_of("cross_interface_blue") is OperatorOwner.INTERFACE
    assert registry.owner_of("local_com_khw_collision") is OperatorOwner.COM_COLLISION
    assert registry.owner_of("native_free_streaming") is OperatorOwner.NATIVE_TRANSPORT
    assert len(registry.processes) == len({item.process for item in registry.processes})


def test_registry_rejects_duplicate_and_unowned_processes() -> None:
    duplicate = OwnershipRegistry(
        processes=(
            ProcessOwnership("p", OperatorOwner.INTERFACE, "boundary"),
            ProcessOwnership("p", OperatorOwner.NATIVE_TRANSPORT, "native"),
        ),
        required_processes=("p",),
    )
    with pytest.raises(ValueError, match="duplicate"):
        duplicate.validate()

    missing = OwnershipRegistry(
        processes=(ProcessOwnership("p", OperatorOwner.INTERFACE, "boundary"),),
        required_processes=("p", "q"),
    )
    with pytest.raises(ValueError, match="unowned"):
        missing.validate()


def test_replacement_switch_off_is_exact_identity() -> None:
    native = np.asarray([0.1, 0.2, 0.3])
    com = np.asarray([0.4, 0.5])
    operator = SplitDomainExchangeOperator(enabled=False)
    result = operator.apply(_packet(), native_state=native, com_state=com, dt_s=3.0)
    assert np.array_equal(result.native_state, native)
    assert np.array_equal(result.com_state, com)
    assert result.ledger.evaluation_count == 0
    assert result.ledger.native_application_count == 0
    assert result.ledger.com_application_count == 0
    assert result.ledger.number_residual_per_H_s == 0.0
    assert result.ledger.energy_residual_W_per_H == 0.0


def test_cross_interface_packet_is_evaluated_once_and_applied_with_opposite_signs() -> None:
    operator = SplitDomainExchangeOperator(enabled=True)
    result = operator.apply(
        _packet(),
        native_state=np.asarray([1.0]),
        com_state=np.asarray([2.0]),
        dt_s=1.0,
    )
    assert result.ledger.evaluation_count == 1
    assert result.ledger.native_application_count == 1
    assert result.ledger.com_application_count == 1
    assert result.ledger.number_residual_per_H_s == 0.0
    assert result.ledger.photon_energy_residual_W_per_H == 0.0
    assert result.ledger.total_energy_residual_W_per_H == 0.0


def test_packet_round_trip_and_frequency_centroid() -> None:
    packet = _packet()
    encoded = json.dumps(packet.to_dict(), sort_keys=True, separators=(",", ":"))
    restored = ExchangePacket.from_dict(json.loads(encoded))
    assert restored == packet
    assert restored.frequency_centroid_Hz == pytest.approx(packet.interface_frequency_Hz)
    assert len(restored.sha256) == 64


def test_packet_rejects_invalid_signs_and_interface_side() -> None:
    valid = _packet().to_dict()

    negative = dict(valid)
    negative["total_number_flux_per_H_s"] = -1.0
    with pytest.raises(ValueError, match="positive"):
        ExchangePacket.from_dict(negative)

    wrong_atom = dict(valid)
    wrong_atom["atom_energy_flux_W_per_H"] *= -1.0
    with pytest.raises(ValueError, match="atom"):
        ExchangePacket.from_dict(wrong_atom)

    wrong_side = dict(valid)
    wrong_side["interface_x"] = -21.25
    with pytest.raises(ValueError, match="side"):
        ExchangePacket.from_dict(wrong_side)


def test_packet_accepts_signed_distortion_when_total_is_positive() -> None:
    packet_dict = _packet().to_dict()
    total = packet_dict["total_number_flux_per_H_s"]
    packet_dict["reference_number_flux_per_H_s"] = 1.2 * total
    packet_dict["distortion_number_flux_per_H_s"] = -0.2 * total
    frequency = packet_dict["interface_frequency_Hz"]
    packet_dict["reference_photon_energy_flux_W_per_H"] = h * frequency * 1.2 * total
    packet_dict["distortion_photon_energy_flux_W_per_H"] = -h * frequency * 0.2 * total
    packet = ExchangePacket.from_dict(packet_dict)
    assert packet.distortion_number_flux_per_H_s < 0.0
    assert packet.total_number_flux_per_H_s > 0.0


def test_local_microphysics_firewall_ignores_bianchi_label() -> None:
    packet = _packet()
    operator = SplitDomainExchangeOperator(enabled=True)
    a = operator.evaluate_packet(packet, bianchi_type="II")
    b = operator.evaluate_packet(packet, bianchi_type="VI_-1/9")
    assert a == b == packet
