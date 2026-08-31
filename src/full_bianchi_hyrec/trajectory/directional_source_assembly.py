"""Typed four-channel directional source assembly research contract.

This module evaluates source laws on the ordered 26-node hydrogen-frame grid.
It deliberately does not construct red/blue boundary values, admit a physical
face, or verify external source authority.  The original-HyRec virtual spike is
kept as an affine jump on signed spectral distortion ``Delta_f``.  One-photon
coefficients act directly on total occupation, while two-photon/Raman values
remain photon-packet production rates per H per second until an authorized
``n_H B_is / mu_i`` deposition exists.  These three variable/unit domains are
never summed here.

``df/dt = emission*(1+f) - absorption*f``.

The net affine opacity may be negative and is therefore never used as an owner
or admission criterion here.
"""
from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
import hashlib
import json
from types import MappingProxyType
from typing import Any

import numpy as np

from full_bianchi_hyrec.trajectory.directional_face_admission import (
    PACKET_RATE_PER_H_S,
    REQUIRED_SOURCE_CHANNELS,
    SOURCE_IDENTICAL_SCALAR_PRIMITIVE,
    THEORY_CONTRACT_DERIVED_26_ORDINATE_FACE_V1,
)


_SHA256_HEX = frozenset("0123456789abcdef")
_NODE_COUNT = 26
SIGNED_SPECTRAL_DISTORTION_DELTA_F = "SIGNED_SPECTRAL_DISTORTION_DELTA_F"
_OWNER_LABELS_BELOW_CEILING = frozenset(
    {
        SOURCE_IDENTICAL_SCALAR_PRIMITIVE,
        THEORY_CONTRACT_DERIVED_26_ORDINATE_FACE_V1,
    }
)


def _is_sha256(value: str) -> bool:
    return len(value) == 64 and all(character in _SHA256_HEX for character in value)


def _sha256(value: object, *, name: str) -> str:
    digest = str(value).lower()
    if not _is_sha256(digest):
        raise ValueError(f"{name} must be a SHA-256 digest")
    return digest


def _owner_below_ceiling(value: object) -> str:
    owner = str(value)
    if owner not in _OWNER_LABELS_BELOW_CEILING:
        raise ValueError(
            "directional source owner ceiling is "
            f"{THEORY_CONTRACT_DERIVED_26_ORDINATE_FACE_V1}"
        )
    return owner


def _immutable_f8_vector(value: object, *, name: str) -> np.ndarray:
    array = np.asarray(value, dtype="<f8")
    if array.shape != (_NODE_COUNT,) or not np.all(np.isfinite(array)):
        raise ValueError(f"{name} must be a finite ordered 26-node vector")
    copied = np.array(array, dtype="<f8", copy=True, order="C")
    return np.frombuffer(copied.tobytes(order="C"), dtype="<f8")


@dataclass(frozen=True)
class SignedDeltaF26:
    """Ordered signed spectral distortion ``Delta_f`` on 26 nodes."""

    values: np.ndarray

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "values",
            _immutable_f8_vector(self.values, name="SignedDeltaF26.values"),
        )

    @property
    def meaning(self) -> str:
        return SIGNED_SPECTRAL_DISTORTION_DELTA_F

    @property
    def units(self) -> str:
        return "1"


@dataclass(frozen=True)
class TotalOccupation26:
    """Ordered nonnegative total photon occupation on 26 nodes."""

    values: np.ndarray

    def __post_init__(self) -> None:
        values = _immutable_f8_vector(
            self.values,
            name="TotalOccupation26.values",
        )
        if np.any(values < 0.0):
            raise ValueError("TotalOccupation26.values must be nonnegative")
        object.__setattr__(self, "values", values)

    @property
    def meaning(self) -> str:
        return "TOTAL_OCCUPATION_F"

    @property
    def units(self) -> str:
        return "1"


@dataclass(frozen=True)
class OccupationRate26:
    """Ordered signed time derivative of total occupation."""

    values: np.ndarray

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "values",
            _immutable_f8_vector(self.values, name="OccupationRate26.values"),
        )

    @property
    def meaning(self) -> str:
        return "TOTAL_OCCUPATION_TIME_DERIVATIVE_DF_DT"

    @property
    def units(self) -> str:
        return "s^-1"


@dataclass(frozen=True)
class PacketRatePerH26:
    """Ordered signed photon-packet production per hydrogen atom and second."""

    values: np.ndarray

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "values",
            _immutable_f8_vector(self.values, name="PacketRatePerH26.values"),
        )

    @property
    def meaning(self) -> str:
        return "TRACKED_PHOTON_PACKET_PRODUCTION_PER_HYDROGEN"

    @property
    def units(self) -> str:
        return PACKET_RATE_PER_H_S


def _dependencies(value: Mapping[str, str]) -> Mapping[str, str]:
    if not isinstance(value, Mapping) or not value:
        raise ValueError("dependency_sha256 must bind at least one dependency")
    normalized: dict[str, str] = {}
    for raw_name, raw_digest in value.items():
        name = str(raw_name)
        if not name or name.strip() != name:
            raise ValueError("dependency names must be nonempty canonical strings")
        normalized[name] = _sha256(
            raw_digest,
            name=f"dependency_sha256[{name!r}]",
        )
    return MappingProxyType(dict(sorted(normalized.items())))


def _canonical_json(value: Mapping[str, Any]) -> bytes:
    return json.dumps(
        dict(value),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode("utf-8")


def _semantic_sha256(
    *,
    metadata: Mapping[str, Any],
    arrays: Sequence[np.ndarray],
) -> str:
    payload = bytearray(_canonical_json(metadata))
    for array in arrays:
        raw = np.asarray(array, dtype="<f8").tobytes(order="C")
        payload.extend(len(raw).to_bytes(8, byteorder="little", signed=False))
        payload.extend(raw)
    return hashlib.sha256(payload).hexdigest()


def _channel_metadata(
    *,
    schema: str,
    name: str,
    owner_label: str,
    source_sha256: str,
    dependency_sha256: Mapping[str, str],
    coefficient_units: str,
    array_names: Sequence[str],
) -> dict[str, Any]:
    return {
        "schema": schema,
        "name": name,
        "owner_label": owner_label,
        "owner_ceiling": THEORY_CONTRACT_DERIVED_26_ORDINATE_FACE_V1,
        "source_sha256": source_sha256,
        "dependency_sha256": dict(dependency_sha256),
        "coefficient_units": coefficient_units,
        "array_dtype": "<f8",
        "array_shape": [_NODE_COUNT],
        "array_order": "C",
        "array_names": list(array_names),
    }


@dataclass(frozen=True)
class DirectionalVirtualSpikeJump:
    """Exact ordered virtual-spike jump, separate from continuous sources."""

    name: str
    owner_label: str
    source_sha256: str
    dependency_sha256: Mapping[str, str]
    optical_depth: np.ndarray
    equilibrium_departure: np.ndarray

    @classmethod
    def from_original_hyrec(
        cls,
        *,
        source: object,
        minus_dlognu_dt_s_inv: object,
        source_sha256: str,
        dependency_sha256: Mapping[str, str],
        owner_label: str = SOURCE_IDENTICAL_SCALAR_PRIMITIVE,
    ) -> DirectionalVirtualSpikeJump:
        """Evaluate the exact virtual-spike jump on all 26 ordered nodes."""

        from full_bianchi_hyrec.trajectory.hyrec_source_adapter import (
            OriginalHyRecVirtualSpikeSource,
        )

        if not isinstance(source, OriginalHyRecVirtualSpikeSource):
            raise TypeError("source must be OriginalHyRecVirtualSpikeSource")
        if source.tau_flrw.shape != (_NODE_COUNT,):
            raise ValueError("virtual-spike source must contain exactly 26 ordered nodes")
        speed = _immutable_f8_vector(
            minus_dlognu_dt_s_inv,
            name="minus_dlognu_dt_s_inv",
        )
        return cls(
            name=REQUIRED_SOURCE_CHANNELS[0],
            owner_label=owner_label,
            source_sha256=source_sha256,
            dependency_sha256=dependency_sha256,
            optical_depth=source.directional_optical_depth(
                minus_dlognu_dt_s_inv=speed
            ),
            equilibrium_departure=source.equilibrium_departure,
        )

    def __post_init__(self) -> None:
        if self.name != REQUIRED_SOURCE_CHANNELS[0]:
            raise ValueError("virtual jump name must be 'virtual_spike'")
        object.__setattr__(self, "owner_label", _owner_below_ceiling(self.owner_label))
        object.__setattr__(
            self,
            "source_sha256",
            _sha256(self.source_sha256, name="source_sha256"),
        )
        object.__setattr__(
            self,
            "dependency_sha256",
            _dependencies(self.dependency_sha256),
        )
        optical_depth = _immutable_f8_vector(
            self.optical_depth,
            name="optical_depth",
        )
        if np.any(optical_depth < 0.0):
            raise ValueError("optical_depth must be nonnegative")
        object.__setattr__(self, "optical_depth", optical_depth)
        object.__setattr__(
            self,
            "equilibrium_departure",
            _immutable_f8_vector(
                self.equilibrium_departure,
                name="equilibrium_departure",
            ),
        )

    @property
    def coefficient_units(self) -> str:
        """Units of the source law that produced this dimensionless jump."""

        return "s^-1"

    @property
    def stored_variable(self) -> str:
        return SIGNED_SPECTRAL_DISTORTION_DELTA_F

    @property
    def semantic_sha256(self) -> str:
        metadata = _channel_metadata(
            schema="DIRECTIONAL_VIRTUAL_SPIKE_JUMP_V1",
            name=self.name,
            owner_label=self.owner_label,
            source_sha256=self.source_sha256,
            dependency_sha256=self.dependency_sha256,
            coefficient_units=self.coefficient_units,
            array_names=("optical_depth", "equilibrium_departure"),
        )
        metadata["payload_units"] = ("1", "1")
        metadata["stored_variable"] = self.stored_variable
        return _semantic_sha256(
            metadata=metadata,
            arrays=(self.optical_depth, self.equilibrium_departure),
        )

    def apply_distortion(self, incoming_distortion: SignedDeltaF26) -> SignedDeltaF26:
        """Apply the source-identical jump to signed ``Delta_f`` only."""

        if not isinstance(incoming_distortion, SignedDeltaF26):
            raise TypeError("incoming_distortion must be SignedDeltaF26")
        values = incoming_distortion.values
        absorbed = -np.expm1(-self.optical_depth)
        result = values + (self.equilibrium_departure - values) * absorbed
        return SignedDeltaF26(result)


@dataclass(frozen=True)
class DirectionalOccupationSourceChannel:
    """Direct total-occupation one-photon coefficients in ``s^-1``."""

    name: str
    owner_label: str
    source_sha256: str
    dependency_sha256: Mapping[str, str]
    emission_s_inv: np.ndarray
    absorption_s_inv: np.ndarray

    @classmethod
    def from_einstein_line(
        cls,
        *,
        source: object,
        source_sha256: str,
        dependency_sha256: Mapping[str, str],
        owner_label: str = THEORY_CONTRACT_DERIVED_26_ORDINATE_FACE_V1,
    ) -> DirectionalOccupationSourceChannel:
        """Broadcast one isotropic hydrogen-frame line pair to 26 nodes."""

        from full_bianchi_hyrec.trajectory.hyrec_source_adapter import (
            IsotropicEinsteinLineSource,
        )

        if not isinstance(source, IsotropicEinsteinLineSource):
            raise TypeError("source must be IsotropicEinsteinLineSource")
        emission, absorption = source.paired_coefficients()
        return cls(
            name="one_photon",
            owner_label=owner_label,
            source_sha256=source_sha256,
            dependency_sha256=dependency_sha256,
            emission_s_inv=np.full(_NODE_COUNT, emission, dtype="<f8"),
            absorption_s_inv=np.full(_NODE_COUNT, absorption, dtype="<f8"),
        )

    def __post_init__(self) -> None:
        if self.name != "one_photon":
            raise ValueError("occupation source name must be one_photon")
        object.__setattr__(self, "owner_label", _owner_below_ceiling(self.owner_label))
        object.__setattr__(
            self,
            "source_sha256",
            _sha256(self.source_sha256, name="source_sha256"),
        )
        object.__setattr__(
            self,
            "dependency_sha256",
            _dependencies(self.dependency_sha256),
        )
        emission = _immutable_f8_vector(self.emission_s_inv, name="emission_s_inv")
        absorption = _immutable_f8_vector(
            self.absorption_s_inv,
            name="absorption_s_inv",
        )
        if np.any(emission < 0.0) or np.any(absorption < 0.0):
            raise ValueError("paired emission/absorption coefficients must be nonnegative")
        object.__setattr__(self, "emission_s_inv", emission)
        object.__setattr__(self, "absorption_s_inv", absorption)

    @property
    def coefficient_units(self) -> str:
        return "s^-1"

    @property
    def semantic_sha256(self) -> str:
        return _semantic_sha256(
            metadata=_channel_metadata(
                schema="DIRECTIONAL_OCCUPATION_SOURCE_CHANNEL_V1",
                name=self.name,
                owner_label=self.owner_label,
                source_sha256=self.source_sha256,
                dependency_sha256=self.dependency_sha256,
                coefficient_units=self.coefficient_units,
                array_names=("emission_s_inv", "absorption_s_inv"),
            ),
            arrays=(self.emission_s_inv, self.absorption_s_inv),
        )

    def action(self, occupation: TotalOccupation26) -> OccupationRate26:
        if not isinstance(occupation, TotalOccupation26):
            raise TypeError("occupation must be TotalOccupation26")
        values = occupation.values
        result = self.emission_s_inv * (1.0 + values) - self.absorption_s_inv * values
        return OccupationRate26(result)


@dataclass(frozen=True)
class DirectionalPacketSourceChannel:
    """Two-photon/Raman packet production per H per second.

    This is not an occupation-rate channel.  It requires a separately approved
    ``n_H B_is / mu_i`` deposition before it can contribute to ``df/dt``.
    """

    name: str
    owner_label: str
    source_sha256: str
    dependency_sha256: Mapping[str, str]
    emission_per_H_s: np.ndarray
    absorption_per_H_s: np.ndarray

    @classmethod
    def from_two_photon_raman(
        cls,
        *,
        source: object,
        companion_occupation: TotalOccupation26,
        source_sha256: str,
        dependency_sha256: Mapping[str, str],
        owner_label: str = THEORY_CONTRACT_DERIVED_26_ORDINATE_FACE_V1,
    ) -> DirectionalPacketSourceChannel:
        """Evaluate one packet source on all 26 companion occupations."""

        from full_bianchi_hyrec.trajectory.hyrec_two_photon_raman import (
            PhysicalTwoPhotonRamanBin,
        )

        if not isinstance(source, PhysicalTwoPhotonRamanBin):
            raise TypeError("source must be PhysicalTwoPhotonRamanBin")
        if not isinstance(companion_occupation, TotalOccupation26):
            raise TypeError("companion_occupation must be TotalOccupation26")
        coefficients = tuple(
            source.paired_packet_coefficients_per_H_s(
                companion_occupation=float(value)
            )
            for value in companion_occupation.values
        )
        emission, absorption = np.asarray(coefficients, dtype="<f8").T
        return cls(
            name=source.process,
            owner_label=owner_label,
            source_sha256=source_sha256,
            dependency_sha256=dependency_sha256,
            emission_per_H_s=emission,
            absorption_per_H_s=absorption,
        )

    def __post_init__(self) -> None:
        if self.name not in {"two_photon", "raman"}:
            raise ValueError("packet source name must be two_photon or raman")
        object.__setattr__(self, "owner_label", _owner_below_ceiling(self.owner_label))
        object.__setattr__(
            self,
            "source_sha256",
            _sha256(self.source_sha256, name="source_sha256"),
        )
        object.__setattr__(
            self,
            "dependency_sha256",
            _dependencies(self.dependency_sha256),
        )
        emission = _immutable_f8_vector(
            self.emission_per_H_s,
            name="emission_per_H_s",
        )
        absorption = _immutable_f8_vector(
            self.absorption_per_H_s,
            name="absorption_per_H_s",
        )
        if np.any(emission < 0.0) or np.any(absorption < 0.0):
            raise ValueError("paired packet coefficients must be nonnegative")
        object.__setattr__(self, "emission_per_H_s", emission)
        object.__setattr__(self, "absorption_per_H_s", absorption)

    @property
    def coefficient_units(self) -> str:
        return PACKET_RATE_PER_H_S

    @property
    def semantic_sha256(self) -> str:
        return _semantic_sha256(
            metadata=_channel_metadata(
                schema="DIRECTIONAL_PACKET_SOURCE_CHANNEL_V1",
                name=self.name,
                owner_label=self.owner_label,
                source_sha256=self.source_sha256,
                dependency_sha256=self.dependency_sha256,
                coefficient_units=self.coefficient_units,
                array_names=("emission_per_H_s", "absorption_per_H_s"),
            ),
            arrays=(self.emission_per_H_s, self.absorption_per_H_s),
        )

    def packet_action_per_H_s(
        self,
        tracked_occupation: TotalOccupation26,
    ) -> PacketRatePerH26:
        if not isinstance(tracked_occupation, TotalOccupation26):
            raise TypeError("tracked_occupation must be TotalOccupation26")
        values = tracked_occupation.values
        result = self.emission_per_H_s * (1.0 + values) - (
            self.absorption_per_H_s * values
        )
        return PacketRatePerH26(result)


DirectionalSourceChannelPayload = (
    DirectionalVirtualSpikeJump
    | DirectionalOccupationSourceChannel
    | DirectionalPacketSourceChannel
)


@dataclass(frozen=True)
class DirectionalSourceAssembly:
    """Typed domain-separated assembly below physical directional authority."""

    quadrature_sha256: str
    channels: Sequence[DirectionalSourceChannelPayload]

    def __post_init__(self) -> None:
        quadrature_hash = _sha256(
            self.quadrature_sha256,
            name="quadrature_sha256",
        )
        channels = tuple(self.channels)
        names = tuple(getattr(channel, "name", None) for channel in channels)
        if len(channels) != len(REQUIRED_SOURCE_CHANNELS) or len(set(names)) != len(
            REQUIRED_SOURCE_CHANNELS
        ):
            raise ValueError("all four directional source channels are required exactly once")
        if names != REQUIRED_SOURCE_CHANNELS:
            raise ValueError(
                "directional source channel order must be "
                f"{REQUIRED_SOURCE_CHANNELS!r}"
            )
        if (
            not isinstance(channels[0], DirectionalVirtualSpikeJump)
            or not isinstance(channels[1], DirectionalOccupationSourceChannel)
            or any(
                not isinstance(channel, DirectionalPacketSourceChannel)
                for channel in channels[2:]
            )
        ):
            raise TypeError(
                "channel payload types must be distortion jump, occupation source, "
                "then two packet sources"
            )
        object.__setattr__(self, "quadrature_sha256", quadrature_hash)
        object.__setattr__(self, "channels", channels)

    @property
    def channel_names(self) -> tuple[str, ...]:
        return tuple(channel.name for channel in self.channels)

    @property
    def owner_label(self) -> str:
        return THEORY_CONTRACT_DERIVED_26_ORDINATE_FACE_V1

    @property
    def physical_face_materialized(self) -> bool:
        return False

    @property
    def reference_field_adapter_present(self) -> bool:
        return False

    @property
    def deposition_authority_present(self) -> bool:
        return False

    @property
    def occupation_action_available(self) -> bool:
        return False

    @property
    def semantic_sha256(self) -> str:
        return hashlib.sha256(
            _canonical_json(
                {
                    "schema": "DIRECTIONAL_SOURCE_ASSEMBLY_V1",
                    "quadrature_sha256": self.quadrature_sha256,
                    "channel_order": list(self.channel_names),
                    "channel_semantic_sha256": [
                        channel.semantic_sha256 for channel in self.channels
                    ],
                    "owner_label": self.owner_label,
                    "owner_ceiling": THEORY_CONTRACT_DERIVED_26_ORDINATE_FACE_V1,
                    "reference_field_adapter_present": False,
                    "deposition_authority_present": False,
                    "occupation_action_available": False,
                    "physical_face_materialized": False,
                }
            )
        ).hexdigest()

    def source_declarations(self) -> tuple[object, ...]:
        """Return shape-compatible declarations without claiming verification."""

        # Delayed import keeps admission independent at module-import time.
        from full_bianchi_hyrec.trajectory.directional_face_admission import (
            DirectionalSourceChannel,
        )

        return tuple(
            DirectionalSourceChannel(
                name=channel.name,
                owner_label=channel.owner_label,
                coefficient_units=channel.coefficient_units,
                source_sha256=channel.source_sha256,
            )
            for channel in self.channels
        )

    def apply_virtual_spike_distortion(
        self,
        incoming_distortion: SignedDeltaF26,
    ) -> SignedDeltaF26:
        channel = self.channels[0]
        assert isinstance(channel, DirectionalVirtualSpikeJump)
        return channel.apply_distortion(incoming_distortion)


__all__ = [
    "SignedDeltaF26",
    "TotalOccupation26",
    "OccupationRate26",
    "PacketRatePerH26",
    "DirectionalVirtualSpikeJump",
    "DirectionalOccupationSourceChannel",
    "DirectionalPacketSourceChannel",
    "DirectionalSourceAssembly",
    "SIGNED_SPECTRAL_DISTORTION_DELTA_F",
]
