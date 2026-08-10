"""Fail-closed provenance contract for production radiation macro parents.

Operator-verification and manufactured states are useful audit fixtures, but they
must never enter the production macro continuation path.  This module makes the
distinction explicit and binds every source-derived accepted parent to the
canonical history, atomic state, background, network, interface and branch that
produced it.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
import hashlib
import json
import math
import struct
from types import MappingProxyType
from typing import Mapping, Sequence

import numpy as np


class ParentEvidenceClass(str, Enum):
    SOURCE_DERIVED_ACCEPTED = "SOURCE_DERIVED_ACCEPTED"
    OPERATOR_VERIFICATION = "OPERATOR_VERIFICATION"
    MANUFACTURED = "MANUFACTURED"


def _is_sha256(value: str) -> bool:
    text = str(value).lower()
    return len(text) == 64 and all(character in "0123456789abcdef" for character in text)


def _canonical_json(value: object) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode("ascii")


def _immutable_positive_array(value: Sequence[float] | np.ndarray) -> np.ndarray:
    array = np.asarray(value, dtype=float)
    if array.ndim != 2 or array.size == 0:
        raise ValueError("occupation must be a nonempty two-dimensional array")
    if not np.all(np.isfinite(array)) or np.any(array <= 0.0):
        raise ValueError("occupation must be finite and strictly positive")
    result = np.array(array, dtype="<f8", copy=True, order="C")
    result.setflags(write=False)
    return result


@dataclass(frozen=True)
class ProductionParentRequirements:
    """Expected provenance of the previous accepted canonical radiation slice."""

    accepted_history_index: int
    accepted_history_sha256: str
    atomic_state_sha256: str
    background_sequence_sha256: str
    network_sha256: str
    interface_sha256: str
    branch_id: str

    def __post_init__(self) -> None:
        index = int(self.accepted_history_index)
        if index < 0:
            raise ValueError("accepted_history_index must be nonnegative")
        object.__setattr__(self, "accepted_history_index", index)
        for name in (
            "accepted_history_sha256",
            "atomic_state_sha256",
            "background_sequence_sha256",
            "network_sha256",
            "interface_sha256",
        ):
            value = str(getattr(self, name)).lower()
            if not _is_sha256(value):
                raise ValueError(f"{name} must be a SHA-256 digest")
            object.__setattr__(self, name, value)
        branch = str(self.branch_id)
        if not branch:
            raise ValueError("branch_id must be nonempty")
        object.__setattr__(self, "branch_id", branch)


@dataclass(frozen=True)
class AcceptedRadiationParent:
    """Content-addressed parent state for one canonical radiation macro.

    Only ``SOURCE_DERIVED_ACCEPTED`` objects that match an explicit
    :class:`ProductionParentRequirements` instance may enter the production
    continuation factory.  Audit fixtures remain serializable and hashable, but
    fail closed at that boundary.
    """

    occupation: np.ndarray
    evidence_class: ParentEvidenceClass | str
    accepted_history_index: int
    accepted_history_sha256: str
    atomic_state_sha256: str
    background_sequence_sha256: str
    network_sha256: str
    interface_sha256: str
    branch_id: str
    metadata: Mapping[str, str | int | float | bool] = field(default_factory=dict)

    SCHEMA = "PR05C_ACCEPTED_RADIATION_PARENT_V1"

    def __post_init__(self) -> None:
        object.__setattr__(self, "occupation", _immutable_positive_array(self.occupation))
        try:
            evidence = (
                self.evidence_class
                if isinstance(self.evidence_class, ParentEvidenceClass)
                else ParentEvidenceClass(str(self.evidence_class))
            )
        except ValueError as exc:
            raise ValueError("unknown parent evidence_class") from exc
        object.__setattr__(self, "evidence_class", evidence)
        index = int(self.accepted_history_index)
        if index < 0:
            raise ValueError("accepted_history_index must be nonnegative")
        object.__setattr__(self, "accepted_history_index", index)
        for name in (
            "accepted_history_sha256",
            "atomic_state_sha256",
            "background_sequence_sha256",
            "network_sha256",
            "interface_sha256",
        ):
            value = str(getattr(self, name)).lower()
            if not _is_sha256(value):
                raise ValueError(f"{name} must be a SHA-256 digest")
            object.__setattr__(self, name, value)
        branch = str(self.branch_id)
        if not branch:
            raise ValueError("branch_id must be nonempty")
        object.__setattr__(self, "branch_id", branch)
        normalized_metadata: dict[str, str | int | float | bool] = {}
        for key, value in self.metadata.items():
            name = str(key)
            if not name:
                raise ValueError("metadata keys must be nonempty")
            if isinstance(value, bool):
                normalized_metadata[name] = value
            elif isinstance(value, int):
                normalized_metadata[name] = int(value)
            elif isinstance(value, float):
                number = float(value)
                if not math.isfinite(number):
                    raise ValueError("metadata floats must be finite")
                normalized_metadata[name] = number
            elif isinstance(value, str):
                normalized_metadata[name] = value
            else:
                raise TypeError("metadata values must be scalar JSON primitives")
        object.__setattr__(self, "metadata", MappingProxyType(normalized_metadata))

    def to_bytes(self) -> bytes:
        header = {
            "schema": self.SCHEMA,
            "shape": list(self.occupation.shape),
            "dtype": "<f8",
            "evidence_class": self.evidence_class.value,
            "accepted_history_index": self.accepted_history_index,
            "accepted_history_sha256": self.accepted_history_sha256,
            "atomic_state_sha256": self.atomic_state_sha256,
            "background_sequence_sha256": self.background_sequence_sha256,
            "network_sha256": self.network_sha256,
            "interface_sha256": self.interface_sha256,
            "branch_id": self.branch_id,
            "metadata": dict(self.metadata),
        }
        header_bytes = _canonical_json(header)
        return struct.pack("<Q", len(header_bytes)) + header_bytes + self.occupation.tobytes(order="C")

    @classmethod
    def from_bytes(cls, payload: bytes) -> "AcceptedRadiationParent":
        if len(payload) < 8:
            raise ValueError("parent payload is truncated")
        (header_size,) = struct.unpack("<Q", payload[:8])
        if header_size <= 0 or 8 + header_size > len(payload):
            raise ValueError("parent header length is invalid")
        header = json.loads(payload[8 : 8 + header_size].decode("ascii"))
        if header.get("schema") != cls.SCHEMA or header.get("dtype") != "<f8":
            raise ValueError("parent payload schema/dtype mismatch")
        shape = tuple(int(item) for item in header["shape"])
        if len(shape) != 2 or min(shape) <= 0:
            raise ValueError("parent payload shape is invalid")
        data = payload[8 + header_size :]
        expected = int(np.prod(shape)) * np.dtype("<f8").itemsize
        if len(data) != expected:
            raise ValueError("parent payload data length mismatch")
        occupation = np.frombuffer(data, dtype="<f8").reshape(shape).copy()
        return cls(
            occupation=occupation,
            evidence_class=header["evidence_class"],
            accepted_history_index=header["accepted_history_index"],
            accepted_history_sha256=header["accepted_history_sha256"],
            atomic_state_sha256=header["atomic_state_sha256"],
            background_sequence_sha256=header["background_sequence_sha256"],
            network_sha256=header["network_sha256"],
            interface_sha256=header["interface_sha256"],
            branch_id=header["branch_id"],
            metadata=header.get("metadata", {}),
        )

    @property
    def sha256(self) -> str:
        return hashlib.sha256(self.to_bytes()).hexdigest()

    def validate_for_production(self, requirements: ProductionParentRequirements) -> None:
        if self.evidence_class is not ParentEvidenceClass.SOURCE_DERIVED_ACCEPTED:
            raise PermissionError(
                "production macro requires SOURCE_DERIVED_ACCEPTED parent; "
                f"received {self.evidence_class.value}"
            )
        mismatches: list[str] = []
        for name in (
            "accepted_history_index",
            "accepted_history_sha256",
            "atomic_state_sha256",
            "background_sequence_sha256",
            "network_sha256",
            "interface_sha256",
            "branch_id",
        ):
            if getattr(self, name) != getattr(requirements, name):
                mismatches.append(name)
        if mismatches:
            raise ValueError("production parent provenance mismatch: " + ", ".join(mismatches))


__all__ = [
    "AcceptedRadiationParent",
    "ParentEvidenceClass",
    "ProductionParentRequirements",
]
