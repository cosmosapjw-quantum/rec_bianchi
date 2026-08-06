from __future__ import annotations

import json

import numpy as np
import pytest
from scipy.constants import h

from full_bianchi_hyrec.recoil.original_hyrec_physical_flux import OriginalHyRecBoundarySample

from full_bianchi_hyrec.recoil.split_domain_exchange import (
    ExchangeDirection,
    ExchangePacket,
    InterfaceSide,
    OperatorOwner,
    OwnershipRegistry,
    ProcessOwnership,
    SplitDomainExchangeOperator,
    default_ownership_registry,
    packet_from_original_hyrec_boundary_sample,
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
        atom_energy_flux_W_per_H=0.0,
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
    wrong_atom["atom_energy_flux_W_per_H"] = -wrong_atom["photon_energy_flux_W_per_H"]
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


def test_pure_representation_interface_has_no_atomic_source_term() -> None:
    packet = _packet()
    assert packet.atom_energy_flux_W_per_H == 0.0
    result = SplitDomainExchangeOperator(enabled=True).apply(
        packet, native_state=[1.0], com_state=[2.0], dt_s=1.0
    )
    assert result.ledger.photon_energy_residual_W_per_H == 0.0
    assert result.ledger.total_energy_residual_W_per_H == 0.0


def _boundary_sample(side: str) -> OriginalHyRecBoundarySample:
    interface_x = -21.25 if side == "red" else 21.25
    energy_eV = 10.2 + interface_x * 1.0e-4
    frequency = energy_eV / 4.135667696e-15
    reference = 1.0e-16
    distortion = -2.0e-17 if side == "red" else 3.0e-17
    total = reference + distortion
    mode = 3.0e13
    H_s_inv = 5.0e-14
    phi_reference = H_s_inv * mode * reference
    phi_distortion = H_s_inv * mode * distortion
    phi_total = H_s_inv * mode * total
    return OriginalHyRecBoundarySample(
        side=side,
        interface_x=interface_x,
        doppler_width_eV=1.0e-4,
        interface_energy_eV=energy_eV,
        interface_frequency_Hz=frequency,
        source_index=2,
        source_energy_eV=energy_eV + 2.0e-4,
        lna_query=-7.0,
        history_index_left=10,
        history_index_right=11,
        interpolation_fraction=0.5,
        history_value_left=distortion,
        history_value_right=distortion,
        distortion_occupation=distortion,
        blackbody_occupation=reference,
        total_occupation=total,
        mode_factor_per_H=mode,
        distortion_number_flux_per_H_s=phi_distortion,
        reference_number_flux_per_H_s=phi_reference,
        total_number_flux_per_H_s=phi_total,
        distortion_photon_energy_flux_W_per_H=h * frequency * phi_distortion,
        reference_photon_energy_flux_W_per_H=h * frequency * phi_reference,
        total_photon_energy_flux_W_per_H=h * frequency * phi_total,
    )


def test_boundary_sample_constructs_directional_positive_packet() -> None:
    red = packet_from_original_hyrec_boundary_sample(
        _boundary_sample("red"), source_snapshot_z=1100.0
    )
    blue = packet_from_original_hyrec_boundary_sample(
        _boundary_sample("blue"), source_snapshot_z=1100.0
    )
    assert red.direction is ExchangeDirection.COM_TO_NATIVE
    assert blue.direction is ExchangeDirection.NATIVE_TO_COM
    assert red.total_number_flux_per_H_s > 0.0
    assert blue.total_number_flux_per_H_s > 0.0
    assert red.atom_energy_flux_W_per_H == 0.0
    assert blue.atom_energy_flux_W_per_H == 0.0
    assert red.distortion_number_flux_per_H_s < 0.0
    assert blue.distortion_number_flux_per_H_s > 0.0
