from __future__ import annotations

import hashlib

import numpy as np
import pytest

from full_bianchi_hyrec.trajectory.directional_face_admission import (
    PACKET_RATE_PER_H_S,
    SOURCE_IDENTICAL_DIRECTIONAL_FACE,
    SOURCE_IDENTICAL_SCALAR_PRIMITIVE,
    THEORY_CONTRACT_DERIVED_26_ORDINATE_FACE_V1,
)
from full_bianchi_hyrec.trajectory.directional_source_assembly import (
    DirectionalOccupationSourceChannel,
    DirectionalPacketSourceChannel,
    DirectionalSourceAssembly,
    DirectionalVirtualSpikeJump,
    OccupationRate26,
    PacketRatePerH26,
    SIGNED_SPECTRAL_DISTORTION_DELTA_F,
    SignedDeltaF26,
    TotalOccupation26,
)
from full_bianchi_hyrec.trajectory.hyrec_source_adapter import (
    IsotropicEinsteinLineSource,
    OriginalHyRecVirtualSpikeSource,
)
from full_bianchi_hyrec.trajectory.hyrec_two_photon_raman import (
    PhysicalTwoPhotonRamanBin,
)


def _sha(label: str) -> str:
    return hashlib.sha256(label.encode("ascii")).hexdigest()


def _dependencies(name: str, *, reverse: bool = False) -> dict[str, str]:
    rows = [("network", _sha(f"{name}:network")), ("state", _sha(f"{name}:state"))]
    if reverse:
        rows.reverse()
    return dict(rows)


def _virtual(*, equilibrium_shift: float = 0.0) -> DirectionalVirtualSpikeJump:
    return DirectionalVirtualSpikeJump(
        name="virtual_spike",
        owner_label=SOURCE_IDENTICAL_SCALAR_PRIMITIVE,
        source_sha256=_sha("virtual-law"),
        dependency_sha256=_dependencies("virtual"),
        optical_depth=np.linspace(0.0, 0.25, 26),
        equilibrium_departure=np.linspace(-0.02, 0.03, 26) + equilibrium_shift,
    )


def _paired(
    name: str, scale: float = 1.0
) -> DirectionalOccupationSourceChannel | DirectionalPacketSourceChannel:
    common = {
        "name": name,
        "owner_label": THEORY_CONTRACT_DERIVED_26_ORDINATE_FACE_V1,
        "source_sha256": _sha(f"{name}-law"),
        "dependency_sha256": _dependencies(name),
    }
    if name == "one_photon":
        return DirectionalOccupationSourceChannel(
            **common,
            emission_s_inv=scale * np.linspace(0.01, 0.02, 26),
            absorption_s_inv=scale * np.linspace(0.03, 0.05, 26),
        )
    return DirectionalPacketSourceChannel(
        **common,
        emission_per_H_s=scale * np.linspace(0.01, 0.02, 26),
        absorption_per_H_s=scale * np.linspace(0.03, 0.05, 26),
    )


def _assembly() -> DirectionalSourceAssembly:
    virtual_source = OriginalHyRecVirtualSpikeSource(
        tau_flrw=np.linspace(0.0, 0.25, 26),
        equilibrium_departure=np.linspace(-0.02, 0.03, 26),
        H_s_inv=2.0,
    )
    one_photon_source = IsotropicEinsteinLineSource(
        A_ul_s_inv=6.265e8,
        profile_Hz_inv=2.0e-12,
        frequency_Hz=2.4660677e15,
        nH_m3=2.5e8,
        upper_population=0.001,
        lower_population=0.8,
        upper_degeneracy=3.0,
        lower_degeneracy=1.0,
    )
    two_photon_source = PhysicalTwoPhotonRamanBin(
        process="two_photon",
        integrated_rate_s_inv=0.013,
        transition_frequency_Hz=2.6e15,
        companion_frequency_Hz=0.7e15,
        tracked_frequency_Hz=1.9e15,
        upper_population=0.012,
        ground_population=0.76,
        upper_to_ground_degeneracy_ratio=3.0,
    )
    raman_source = PhysicalTwoPhotonRamanBin(
        process="raman",
        integrated_rate_s_inv=0.027,
        transition_frequency_Hz=2.4e15,
        companion_frequency_Hz=0.35e15,
        tracked_frequency_Hz=2.75e15,
        upper_population=0.012,
        ground_population=0.81,
        upper_to_ground_degeneracy_ratio=3.0,
    )
    companion = TotalOccupation26(np.linspace(0.01, 0.04, 26))
    return DirectionalSourceAssembly(
        quadrature_sha256=_sha("quadrature"),
        channels=(
            DirectionalVirtualSpikeJump.from_original_hyrec(
                source=virtual_source,
                minus_dlognu_dt_s_inv=np.full(26, 2.0),
                source_sha256=_sha("virtual-law"),
                dependency_sha256=_dependencies("virtual"),
            ),
            DirectionalOccupationSourceChannel.from_einstein_line(
                source=one_photon_source,
                source_sha256=_sha("one-photon-law"),
                dependency_sha256=_dependencies("one_photon"),
            ),
            DirectionalPacketSourceChannel.from_two_photon_raman(
                source=two_photon_source,
                companion_occupation=companion,
                source_sha256=_sha("two-photon-law"),
                dependency_sha256=_dependencies("two_photon"),
            ),
            DirectionalPacketSourceChannel.from_two_photon_raman(
                source=raman_source,
                companion_occupation=companion,
                source_sha256=_sha("raman-law"),
                dependency_sha256=_dependencies("raman"),
            ),
        ),
    )


def test_four_channel_assembly_keeps_distortion_occupation_and_packet_domains_apart() -> None:
    assembly = _assembly()
    incoming_distortion = SignedDeltaF26(np.linspace(-0.03, 0.04, 26))
    after_jump = assembly.apply_virtual_spike_distortion(incoming_distortion)
    jump = assembly.channels[0]
    expected_jump = incoming_distortion.values + (
        jump.equilibrium_departure - incoming_distortion.values
    ) * (-np.expm1(-jump.optical_depth))
    assert isinstance(after_jump, SignedDeltaF26)
    assert np.array_equal(after_jump.values, expected_jump)
    assert after_jump.meaning == SIGNED_SPECTRAL_DISTORTION_DELTA_F
    assert after_jump.units == "1"
    assert jump.stored_variable == SIGNED_SPECTRAL_DISTORTION_DELTA_F

    occupation = TotalOccupation26(np.linspace(0.01, 0.04, 26))
    assert occupation.meaning == "TOTAL_OCCUPATION_F"
    assert occupation.units == "1"
    one_photon = assembly.channels[1]
    occupation_rate = one_photon.action(occupation)
    assert isinstance(occupation_rate, OccupationRate26)
    assert occupation_rate.meaning == "TOTAL_OCCUPATION_TIME_DERIVATIVE_DF_DT"
    assert occupation_rate.units == "s^-1"
    assert np.array_equal(
        occupation_rate.values,
        one_photon.emission_s_inv * (1.0 + occupation.values)
        - one_photon.absorption_s_inv * occupation.values,
    )
    for packet in assembly.channels[2:]:
        assert packet.coefficient_units == PACKET_RATE_PER_H_S
        packet_rate = packet.packet_action_per_H_s(occupation)
        assert isinstance(packet_rate, PacketRatePerH26)
        assert (
            packet_rate.meaning
            == "TRACKED_PHOTON_PACKET_PRODUCTION_PER_HYDROGEN"
        )
        assert packet_rate.units == PACKET_RATE_PER_H_S
        assert np.array_equal(
            packet_rate.values,
            packet.emission_per_H_s * (1.0 + occupation.values)
            - packet.absorption_per_H_s * occupation.values,
        )
    assert assembly.channel_names == (
        "virtual_spike",
        "one_photon",
        "two_photon",
        "raman",
    )
    assert assembly.owner_label == THEORY_CONTRACT_DERIVED_26_ORDINATE_FACE_V1
    assert not assembly.reference_field_adapter_present
    assert not assembly.deposition_authority_present
    assert not assembly.occupation_action_available
    assert not assembly.physical_face_materialized


def test_arrays_are_bytes_backed_and_digest_binds_payload_and_dependencies() -> None:
    mutable_tau = np.linspace(0.0, 0.25, 26)
    mutable_dependencies = _dependencies("virtual")
    virtual = DirectionalVirtualSpikeJump(
        name="virtual_spike",
        owner_label=SOURCE_IDENTICAL_SCALAR_PRIMITIVE,
        source_sha256=_sha("virtual-law"),
        dependency_sha256=mutable_dependencies,
        optical_depth=mutable_tau,
        equilibrium_departure=np.zeros(26),
    )
    digest = virtual.semantic_sha256
    mutable_tau[:] = 99.0
    mutable_dependencies["state"] = _sha("mutated-after-construction")
    assert virtual.semantic_sha256 == digest
    assert not np.any(virtual.optical_depth == 99.0)
    with pytest.raises(ValueError):
        virtual.optical_depth.setflags(write=True)
    with pytest.raises(TypeError):
        virtual.dependency_sha256["state"] = _sha("mutation-attempt")

    reordered_dependencies = DirectionalVirtualSpikeJump(
        name="virtual_spike",
        owner_label=SOURCE_IDENTICAL_SCALAR_PRIMITIVE,
        source_sha256=_sha("virtual-law"),
        dependency_sha256=_dependencies("virtual", reverse=True),
        optical_depth=np.linspace(0.0, 0.25, 26),
        equilibrium_departure=np.zeros(26),
    )
    assert reordered_dependencies.semantic_sha256 == virtual.semantic_sha256
    changed_dependency = DirectionalVirtualSpikeJump(
        name="virtual_spike",
        owner_label=SOURCE_IDENTICAL_SCALAR_PRIMITIVE,
        source_sha256=_sha("virtual-law"),
        dependency_sha256={**_dependencies("virtual"), "state": _sha("changed")},
        optical_depth=np.linspace(0.0, 0.25, 26),
        equilibrium_departure=np.zeros(26),
    )
    assert changed_dependency.semantic_sha256 != virtual.semantic_sha256
    changed_payload = _virtual(equilibrium_shift=1.0e-12)
    assert changed_payload.semantic_sha256 != _virtual().semantic_sha256
    assert changed_payload.semantic_sha256 != digest

    assembly = _assembly()
    with pytest.raises(ValueError):
        assembly.channels[1].emission_s_inv.setflags(write=True)
    with pytest.raises(ValueError):
        assembly.channels[2].emission_per_H_s.setflags(write=True)
    assert len(assembly.semantic_sha256) == 64


def test_tagged_vectors_are_immutable_and_enforce_domain_seams() -> None:
    mutable = np.linspace(-0.02, 0.03, 26)
    distortion = SignedDeltaF26(mutable)
    mutable[:] = 17.0
    assert not np.any(distortion.values == 17.0)

    occupation = TotalOccupation26(np.linspace(0.01, 0.04, 26))
    occupation_rate = OccupationRate26(np.linspace(-0.04, 0.03, 26))
    packet_rate = PacketRatePerH26(np.linspace(-0.02, 0.05, 26))
    for tagged in (distortion, occupation, occupation_rate, packet_rate):
        assert tagged.values.shape == (26,)
        assert tagged.values.dtype.str == "<f8"
        assert isinstance(tagged.values.base, bytes)
        assert not tagged.values.flags.writeable
        with pytest.raises(ValueError):
            tagged.values.setflags(write=True)
    with pytest.raises(ValueError, match="nonnegative"):
        TotalOccupation26(-np.ones(26))
    for vector_type in (
        SignedDeltaF26,
        TotalOccupation26,
        OccupationRate26,
        PacketRatePerH26,
    ):
        with pytest.raises(ValueError, match="26-node"):
            vector_type(np.zeros(25))
        with pytest.raises(ValueError, match="finite"):
            vector_type(np.full(26, np.nan))

    assembly = _assembly()
    jump = assembly.channels[0]
    one_photon = assembly.channels[1]
    packet = assembly.channels[2]
    for wrong in (np.zeros(26), occupation, OccupationRate26(np.zeros(26))):
        with pytest.raises(TypeError, match="SignedDeltaF26"):
            jump.apply_distortion(wrong)
        with pytest.raises(TypeError, match="SignedDeltaF26"):
            assembly.apply_virtual_spike_distortion(wrong)
    for wrong in (np.zeros(26), distortion, OccupationRate26(np.zeros(26))):
        with pytest.raises(TypeError, match="TotalOccupation26"):
            one_photon.action(wrong)
    for wrong in (np.zeros(26), distortion, PacketRatePerH26(np.zeros(26))):
        with pytest.raises(TypeError, match="TotalOccupation26"):
            packet.packet_action_per_H_s(wrong)


def test_packet_factory_rejects_raw_or_wrong_tagged_companion_domain() -> None:
    source = PhysicalTwoPhotonRamanBin(
        process="two_photon",
        integrated_rate_s_inv=0.013,
        transition_frequency_Hz=2.6e15,
        companion_frequency_Hz=0.7e15,
        tracked_frequency_Hz=1.9e15,
        upper_population=0.012,
        ground_population=0.76,
        upper_to_ground_degeneracy_ratio=3.0,
    )
    common = {
        "source": source,
        "source_sha256": _sha("two-photon-law"),
        "dependency_sha256": _dependencies("two_photon"),
    }
    for wrong in (
        np.zeros(26),
        SignedDeltaF26(np.zeros(26)),
        PacketRatePerH26(np.zeros(26)),
    ):
        with pytest.raises(TypeError, match="TotalOccupation26"):
            DirectionalPacketSourceChannel.from_two_photon_raman(
                companion_occupation=wrong,
                **common,
            )


@pytest.mark.parametrize(
    "channels,match",
    [
        ((_virtual(), _paired("one_photon"), _paired("two_photon")), "exactly"),
        (
            (
                _virtual(),
                _paired("two_photon"),
                _paired("one_photon"),
                _paired("raman"),
            ),
            "order",
        ),
        (
            (
                _virtual(),
                _paired("one_photon"),
                _paired("two_photon"),
                _paired("two_photon"),
            ),
            "exactly|order",
        ),
    ],
)
def test_assembly_requires_all_four_channels_exactly_once_and_in_order(
    channels: tuple[object, ...], match: str
) -> None:
    with pytest.raises(ValueError, match=match):
        DirectionalSourceAssembly(
            quadrature_sha256=_sha("quadrature"),
            channels=channels,
        )


def test_owner_ceiling_rejects_directional_source_identity_claim() -> None:
    with pytest.raises(ValueError, match="owner ceiling"):
        DirectionalOccupationSourceChannel(
            name="one_photon",
            owner_label=SOURCE_IDENTICAL_DIRECTIONAL_FACE,
            source_sha256=_sha("law"),
            dependency_sha256=_dependencies("one"),
            emission_s_inv=np.ones(26),
            absorption_s_inv=np.ones(26),
        )


def test_packet_channels_cannot_be_summed_into_an_occupation_action() -> None:
    assembly = _assembly()
    assert not assembly.occupation_action_available
    assert not assembly.deposition_authority_present
    assert not hasattr(assembly, "continuous_action")
    assert not hasattr(assembly, "paired_coefficients")


def test_existing_scalar_sources_expose_consistent_paired_coefficients() -> None:
    line = IsotropicEinsteinLineSource(
        A_ul_s_inv=6.265e8,
        profile_Hz_inv=2.0e-12,
        frequency_Hz=2.4660677e15,
        nH_m3=2.5e8,
        upper_population=0.001,
        lower_population=0.8,
        upper_degeneracy=3.0,
        lower_degeneracy=1.0,
    )
    emission, absorption = line.paired_coefficients()
    occupation = 0.013
    assert line.occupation_action(occupation) == pytest.approx(
        emission * (1.0 + occupation) - absorption * occupation
    )

    two_photon = PhysicalTwoPhotonRamanBin(
        process="two_photon",
        integrated_rate_s_inv=0.013,
        transition_frequency_Hz=2.6e15,
        companion_frequency_Hz=0.7e15,
        tracked_frequency_Hz=1.9e15,
        upper_population=0.012,
        ground_population=0.76,
        upper_to_ground_degeneracy_ratio=3.0,
    )
    companion = 0.031
    tracked = 0.006
    emission, absorption = two_photon.paired_packet_coefficients_per_H_s(
        companion_occupation=companion
    )
    assert two_photon.net_action(companion, tracked) == pytest.approx(
        emission * (1.0 + tracked) - absorption * tracked
    )

    raman = PhysicalTwoPhotonRamanBin(
        process="raman",
        integrated_rate_s_inv=0.027,
        transition_frequency_Hz=2.4e15,
        companion_frequency_Hz=0.35e15,
        tracked_frequency_Hz=2.75e15,
        upper_population=0.012,
        ground_population=0.81,
        upper_to_ground_degeneracy_ratio=3.0,
    )
    emission, absorption = raman.paired_packet_coefficients_per_H_s(
        companion_occupation=companion
    )
    assert raman.net_action(companion, tracked) == pytest.approx(
        emission * (1.0 + tracked) - absorption * tracked
    )
