"""Source-identical causal characteristic history for original HyRec.

The October-2012 hydrogen solver keeps the virtual radiation block algebraic
and obtains incoming distortions by free-streaming previously accepted outgoing
values along logarithmic-frequency characteristics.  This module reproduces
``interp_Dfnu`` and ``fplus_from_fminus`` without inventing a finite local
virtual-cell mass.

Conventions
-----------
* ``eta = ln(a)`` increases toward the future;
* ordinary frequency is measured in Hz, not angular frequency;
* energy tables use eV exactly as the canonical source does;
* signed distortion variables are never clipped;
* a history candidate is immutable until explicitly accepted.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import math
import struct
from types import MappingProxyType
from typing import Mapping, Sequence

import numpy as np

from full_bianchi_hyrec.recoil.original_hyrec_native import (
    E21_EV,
    H_PLANCK_EV_S,
    NSUBLYA,
    NVIRT,
)


NSUBLYB = 271
E31_EV = 12.087365397278509
E41_EV = 12.748393192442178
CANONICAL_DLNA = 8.49e-5
_HISTORY_MAGIC = b"PR05B2_ACCEPTED_HISTORY_V1\n"


class FutureHistoryEndpointError(ValueError):
    """Raised when a characteristic query would read an unaccepted endpoint."""


class CharacteristicStencilSwitch(RuntimeError):
    """Raised when a derivative perturbation changes the discrete source stencil."""


def _readonly_float_array(value: Sequence[float] | np.ndarray, shape: tuple[int, ...], name: str) -> np.ndarray:
    array = np.asarray(value, dtype=float)
    if array.shape != shape or not np.all(np.isfinite(array)):
        raise ValueError(f"{name} must have shape {shape} and finite values")
    result = np.array(array, dtype=float, copy=True, order="C")
    result.setflags(write=False)
    return result



def _hash_mapping(mapping: Mapping[str, str]) -> Mapping[str, str]:
    normalized: dict[str, str] = {}
    for key, value in mapping.items():
        key_s = str(key)
        value_s = str(value)
        if not key_s or len(value_s) != 64 or any(ch not in "0123456789abcdef" for ch in value_s.lower()):
            raise ValueError("source hashes must be nonempty SHA-256 hex strings")
        normalized[key_s] = value_s.lower()
    if not normalized:
        raise ValueError("at least one source hash is required")
    return MappingProxyType(dict(sorted(normalized.items())))


@dataclass(frozen=True)
class CharacteristicInterpolationStencil:
    """Two-neighbour source-order interpolation stencil."""

    eta_query: float
    eta_start: float
    dlna: float
    accepted_count: int
    left_index: int | None
    right_index: int | None
    fraction: float
    thermal_zero: bool = False

    def __post_init__(self) -> None:
        for name in ("eta_query", "eta_start", "dlna", "fraction"):
            value = float(getattr(self, name))
            if not math.isfinite(value):
                raise ValueError(f"{name} must be finite")
            object.__setattr__(self, name, value)
        if self.dlna <= 0.0:
            raise ValueError("dlna must be positive")
        if int(self.accepted_count) != self.accepted_count or self.accepted_count < 0:
            raise ValueError("accepted_count must be a nonnegative integer")
        object.__setattr__(self, "accepted_count", int(self.accepted_count))
        if self.thermal_zero:
            if self.left_index is not None or self.right_index is not None:
                raise ValueError("thermal-zero stencil cannot own endpoints")
            if self.fraction != 0.0:
                raise ValueError("thermal-zero fraction must be zero")
            return
        if self.left_index is None or self.right_index is None:
            raise ValueError("nonthermal stencil requires two endpoints")
        if self.right_index != self.left_index + 1:
            raise ValueError("source stencil endpoints must be adjacent")
        if self.left_index < 0 or self.right_index >= self.accepted_count:
            raise FutureHistoryEndpointError("stencil endpoint lies outside accepted history")
        if not 0.0 <= self.fraction < 1.0:
            raise ValueError("interpolation fraction must lie in [0,1)")

    def evaluate(self, values: Sequence[float] | np.ndarray) -> float:
        array = np.asarray(values, dtype=float)
        if array.ndim != 1 or array.size < self.accepted_count or not np.all(np.isfinite(array[: self.accepted_count])):
            raise ValueError("history values must be a finite one-dimensional accepted array")
        if self.thermal_zero:
            return 0.0
        assert self.left_index is not None and self.right_index is not None
        return float(
            (1.0 - self.fraction) * array[self.left_index]
            + self.fraction * array[self.right_index]
        )

    def jvp(
        self,
        values: Sequence[float] | np.ndarray,
        endpoint_direction: Sequence[float] | np.ndarray,
        *,
        delta_eta: float = 0.0,
    ) -> float:
        """Exact fixed-primal-stencil JVP.

        ``delta_eta`` is a tangent direction, not a finite perturbation.  The
        primal evaluation owns the active stencil; deciding whether a finite
        step crosses a stencil boundary belongs to the caller's active-set
        radius check, outside this linear map.
        """

        array = np.asarray(values, dtype=float)
        direction = np.asarray(endpoint_direction, dtype=float)
        if array.ndim != 1 or direction.shape != array.shape:
            raise ValueError("values and endpoint_direction must be matching vectors")
        if array.size < self.accepted_count or not np.all(np.isfinite(array[: self.accepted_count])) or not np.all(np.isfinite(direction[: self.accepted_count])):
            raise ValueError("JVP arrays contain unavailable or nonfinite entries")
        deta = float(delta_eta)
        if not math.isfinite(deta):
            raise ValueError("delta_eta must be finite")
        if self.thermal_zero:
            return 0.0
        assert self.left_index is not None and self.right_index is not None
        return float(
            (1.0 - self.fraction) * direction[self.left_index]
            + self.fraction * direction[self.right_index]
            + (array[self.right_index] - array[self.left_index]) * deta / self.dlna
        )


@dataclass(frozen=True)
class CharacteristicHistoryGrid:
    eta: np.ndarray
    source_indices: np.ndarray
    z_start: float
    dlna: float
    energy_eV: np.ndarray
    source_hashes: Mapping[str, str]

    def __post_init__(self) -> None:
        eta = np.asarray(self.eta, dtype=float)
        if eta.ndim != 1 or eta.size < 1 or not np.all(np.isfinite(eta)):
            raise ValueError("eta must be a nonempty finite vector")
        indices = np.asarray(self.source_indices, dtype=np.int64)
        if indices.shape != eta.shape:
            raise ValueError("source_indices must match eta")
        if np.any(np.diff(eta) <= 0.0) or np.any(np.diff(indices) <= 0):
            raise ValueError("accepted eta and source indices must be strictly increasing")
        if indices[0] != 0 or not np.array_equal(indices, np.arange(eta.size, dtype=np.int64)):
            raise ValueError("canonical source indices must be contiguous from zero")
        z_start = float(self.z_start)
        dlna = float(self.dlna)
        if not math.isfinite(z_start) or z_start <= 0.0 or not math.isfinite(dlna) or dlna <= 0.0:
            raise ValueError("z_start and dlna must be positive and finite")
        eta_start = -math.log1p(z_start)
        expected = eta_start + dlna * indices
        scale = max(abs(eta_start), dlna, 1.0)
        if float(np.max(np.abs(eta - expected))) > 64.0 * np.finfo(float).eps * scale:
            raise ValueError("eta grid is not the canonical uniform source grid")
        energy = np.asarray(self.energy_eV, dtype=float)
        if energy.shape != (NVIRT,) or np.any(energy <= 0.0) or not np.all(np.isfinite(energy)) or np.any(np.diff(energy) <= 0.0):
            raise ValueError("energy_eV must be NVIRT positive increasing centres")
        eta = np.array(eta, copy=True); eta.setflags(write=False)
        indices = np.array(indices, copy=True); indices.setflags(write=False)
        energy = np.array(energy, copy=True); energy.setflags(write=False)
        object.__setattr__(self, "eta", eta)
        object.__setattr__(self, "source_indices", indices)
        object.__setattr__(self, "energy_eV", energy)
        object.__setattr__(self, "z_start", z_start)
        object.__setattr__(self, "dlna", dlna)
        object.__setattr__(self, "source_hashes", _hash_mapping(self.source_hashes))

    @property
    def accepted_count(self) -> int:
        return int(self.eta.size)

    @property
    def eta_start(self) -> float:
        return -math.log1p(self.z_start)

    @property
    def frequency_Hz(self) -> np.ndarray:
        result = self.energy_eV / H_PLANCK_EV_S
        result.setflags(write=False)
        return result

    def prefix(self, count: int) -> "CharacteristicHistoryGrid":
        n = int(count)
        if n < 1 or n > self.accepted_count:
            raise ValueError("prefix count lies outside available history")
        return CharacteristicHistoryGrid(
            eta=self.eta[:n],
            source_indices=self.source_indices[:n],
            z_start=self.z_start,
            dlna=self.dlna,
            energy_eV=self.energy_eV,
            source_hashes=self.source_hashes,
        )

    def locate(self, eta_query: float, *, accepted_count: int | None = None) -> CharacteristicInterpolationStencil:
        count = self.accepted_count if accepted_count is None else int(accepted_count)
        if count < 0 or count > self.accepted_count:
            raise ValueError("accepted_count lies outside grid")
        query = float(eta_query)
        if not math.isfinite(query):
            raise ValueError("eta_query must be finite")
        if query < self.eta_start:
            return CharacteristicInterpolationStencil(
                eta_query=query,
                eta_start=self.eta_start,
                dlna=self.dlna,
                accepted_count=count,
                left_index=None,
                right_index=None,
                fraction=0.0,
                thermal_zero=True,
            )
        # Exact source condition: lna >= lna_start + dlna*(iz-1) is out of range,
        # where iz is the number of already accepted entries.
        future_boundary = self.eta_start + self.dlna * (count - 1)
        if count <= 1 or query >= future_boundary:
            raise FutureHistoryEndpointError(
                f"eta query {query:.17g} reaches unaccepted endpoint at {future_boundary:.17g}"
            )
        coordinate = (query - self.eta_start) / self.dlna
        left = int(math.floor(coordinate))
        fraction = coordinate - left
        return CharacteristicInterpolationStencil(
            eta_query=query,
            eta_start=self.eta_start,
            dlna=self.dlna,
            accepted_count=count,
            left_index=left,
            right_index=left + 1,
            fraction=fraction,
            thermal_zero=False,
        )


@dataclass(frozen=True)
class HistoryAppendCandidate:
    accepted_index: int
    eta: float
    outgoing_virtual: np.ndarray
    outgoing_lyman: np.ndarray
    average_virtual: np.ndarray
    parent_sha256: str

    def __post_init__(self) -> None:
        if int(self.accepted_index) != self.accepted_index or self.accepted_index < 0:
            raise ValueError("accepted_index must be a nonnegative integer")
        object.__setattr__(self, "accepted_index", int(self.accepted_index))
        eta = float(self.eta)
        if not math.isfinite(eta):
            raise ValueError("candidate eta must be finite")
        object.__setattr__(self, "eta", eta)
        object.__setattr__(self, "outgoing_virtual", _readonly_float_array(self.outgoing_virtual, (NVIRT,), "outgoing_virtual"))
        object.__setattr__(self, "outgoing_lyman", _readonly_float_array(self.outgoing_lyman, (3,), "outgoing_lyman"))
        object.__setattr__(self, "average_virtual", _readonly_float_array(self.average_virtual, (NVIRT,), "average_virtual"))
        parent = str(self.parent_sha256).lower()
        if len(parent) != 64 or any(ch not in "0123456789abcdef" for ch in parent):
            raise ValueError("parent_sha256 must be a SHA-256 hex string")
        object.__setattr__(self, "parent_sha256", parent)


@dataclass(frozen=True)
class AcceptedRadiationHistory:
    grid: CharacteristicHistoryGrid
    outgoing_virtual: np.ndarray
    outgoing_lyman: np.ndarray
    average_virtual: np.ndarray
    completeness: str = "SOURCE_COMPLETE"

    def __post_init__(self) -> None:
        n = self.grid.accepted_count
        object.__setattr__(self, "outgoing_virtual", _readonly_float_array(self.outgoing_virtual, (NVIRT, n), "outgoing_virtual"))
        object.__setattr__(self, "outgoing_lyman", _readonly_float_array(self.outgoing_lyman, (3, n), "outgoing_lyman"))
        object.__setattr__(self, "average_virtual", _readonly_float_array(self.average_virtual, (NVIRT, n), "average_virtual"))
        completeness = str(self.completeness)
        if not completeness:
            raise ValueError("history completeness classification is required")
        object.__setattr__(self, "completeness", completeness)

    @property
    def accepted_count(self) -> int:
        return self.grid.accepted_count

    @property
    def sha256(self) -> str:
        return hashlib.sha256(self.to_bytes()).hexdigest()

    def prefix(self, count: int) -> "AcceptedRadiationHistory":
        n = int(count)
        if n < 1 or n > self.accepted_count:
            raise ValueError("prefix count lies outside accepted history")
        return AcceptedRadiationHistory(
            grid=self.grid.prefix(n),
            outgoing_virtual=self.outgoing_virtual[:, :n],
            outgoing_lyman=self.outgoing_lyman[:, :n],
            average_virtual=self.average_virtual[:, :n],
            completeness=self.completeness,
        )

    def perturb(
        self,
        *,
        outgoing_virtual_direction: np.ndarray,
        outgoing_lyman_direction: np.ndarray,
        average_virtual_direction: np.ndarray | None = None,
        scale: float,
    ) -> "AcceptedRadiationHistory":
        value = float(scale)
        if not math.isfinite(value):
            raise ValueError("perturbation scale must be finite")
        dv = np.asarray(outgoing_virtual_direction, dtype=float)
        dl = np.asarray(outgoing_lyman_direction, dtype=float)
        da = np.zeros_like(self.average_virtual) if average_virtual_direction is None else np.asarray(average_virtual_direction, dtype=float)
        if dv.shape != self.outgoing_virtual.shape or dl.shape != self.outgoing_lyman.shape or da.shape != self.average_virtual.shape:
            raise ValueError("history perturbation shapes do not match")
        return AcceptedRadiationHistory(
            grid=self.grid,
            outgoing_virtual=self.outgoing_virtual + value * dv,
            outgoing_lyman=self.outgoing_lyman + value * dl,
            average_virtual=self.average_virtual + value * da,
            completeness=self.completeness,
        )

    def reject(self, candidate: HistoryAppendCandidate) -> "AcceptedRadiationHistory":
        self._validate_candidate(candidate)
        return self

    def _validate_candidate(self, candidate: HistoryAppendCandidate) -> None:
        if candidate.parent_sha256 != self.sha256:
            raise ValueError("append candidate parent hash does not match history")
        if candidate.accepted_index != self.accepted_count:
            raise ValueError("append candidate index is not the next accepted index")
        expected_eta = self.grid.eta_start + self.grid.dlna * candidate.accepted_index
        if not math.isclose(candidate.eta, expected_eta, rel_tol=0.0, abs_tol=64.0 * np.finfo(float).eps * max(abs(expected_eta), 1.0)):
            raise ValueError("append candidate eta is not on the canonical source grid")

    def accept(self, candidate: HistoryAppendCandidate) -> "AcceptedRadiationHistory":
        self._validate_candidate(candidate)
        eta = np.r_[self.grid.eta, candidate.eta]
        indices = np.r_[self.grid.source_indices, candidate.accepted_index]
        grid = CharacteristicHistoryGrid(
            eta=eta,
            source_indices=indices,
            z_start=self.grid.z_start,
            dlna=self.grid.dlna,
            energy_eV=self.grid.energy_eV,
            source_hashes=self.grid.source_hashes,
        )
        return AcceptedRadiationHistory(
            grid=grid,
            outgoing_virtual=np.column_stack((self.outgoing_virtual, candidate.outgoing_virtual)),
            outgoing_lyman=np.column_stack((self.outgoing_lyman, candidate.outgoing_lyman)),
            average_virtual=np.column_stack((self.average_virtual, candidate.average_virtual)),
            completeness=self.completeness,
        )

    def rollback(self, accepted_count: int) -> "AcceptedRadiationHistory":
        return self.prefix(accepted_count)

    def to_npz_dict(self) -> dict[str, np.ndarray]:
        keys = np.asarray(list(self.grid.source_hashes), dtype="U128")
        values = np.asarray([self.grid.source_hashes[key] for key in keys], dtype="U64")
        return {
            "schema": np.asarray("PR05B2_ACCEPTED_HISTORY_V1"),
            "eta": self.grid.eta,
            "source_indices": self.grid.source_indices,
            "z_start": np.asarray(self.grid.z_start),
            "dlna": np.asarray(self.grid.dlna),
            "energy_eV": self.grid.energy_eV,
            "frequency_Hz": self.grid.frequency_Hz,
            "source_hash_keys": keys,
            "source_hash_values": values,
            "outgoing_virtual": self.outgoing_virtual,
            "outgoing_lyman": self.outgoing_lyman,
            "average_virtual": self.average_virtual,
            "completeness": np.asarray(self.completeness),
        }

    @classmethod
    def from_npz_mapping(cls, mapping: Mapping[str, np.ndarray]) -> "AcceptedRadiationHistory":
        schema = str(np.asarray(mapping["schema"]).item())
        if schema != "PR05B2_ACCEPTED_HISTORY_V1":
            raise ValueError("unknown PR05B2 NPZ history schema")
        keys = [str(item) for item in np.asarray(mapping["source_hash_keys"]).tolist()]
        values = [str(item) for item in np.asarray(mapping["source_hash_values"]).tolist()]
        hashes = dict(zip(keys, values, strict=True))
        grid = CharacteristicHistoryGrid(
            eta=mapping["eta"],
            source_indices=mapping["source_indices"],
            z_start=float(np.asarray(mapping["z_start"]).item()),
            dlna=float(np.asarray(mapping["dlna"]).item()),
            energy_eV=mapping["energy_eV"],
            source_hashes=hashes,
        )
        expected_frequency = grid.frequency_Hz
        observed_frequency = np.asarray(mapping["frequency_Hz"], dtype=float)
        if observed_frequency.shape != (NVIRT,) or not np.array_equal(observed_frequency, expected_frequency):
            raise ValueError("NPZ ordinary-frequency registry is inconsistent")
        return cls(
            grid=grid,
            outgoing_virtual=mapping["outgoing_virtual"],
            outgoing_lyman=mapping["outgoing_lyman"],
            average_virtual=mapping["average_virtual"],
            completeness=str(np.asarray(mapping["completeness"]).item()),
        )

    def to_bytes(self) -> bytes:
        arrays = (
            ("eta", np.asarray(self.grid.eta, dtype="<f8")),
            ("source_indices", np.asarray(self.grid.source_indices, dtype="<i8")),
            ("energy_eV", np.asarray(self.grid.energy_eV, dtype="<f8")),
            ("frequency_Hz", np.asarray(self.grid.frequency_Hz, dtype="<f8")),
            ("outgoing_virtual", np.asarray(self.outgoing_virtual, dtype="<f8")),
            ("outgoing_lyman", np.asarray(self.outgoing_lyman, dtype="<f8")),
            ("average_virtual", np.asarray(self.average_virtual, dtype="<f8")),
        )
        header = {
            "schema": "PR05B2_ACCEPTED_HISTORY_V1",
            "z_start": self.grid.z_start,
            "dlna": self.grid.dlna,
            "source_hashes": dict(self.grid.source_hashes),
            "completeness": self.completeness,
            "arrays": [
                {"name": name, "dtype": str(array.dtype), "shape": list(array.shape), "nbytes": int(array.nbytes)}
                for name, array in arrays
            ],
        }
        encoded = json.dumps(header, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")
        payload = bytearray(_HISTORY_MAGIC)
        payload.extend(struct.pack(">Q", len(encoded)))
        payload.extend(encoded)
        for _, array in arrays:
            payload.extend(array.tobytes(order="C"))
        return bytes(payload)

    @classmethod
    def from_bytes(cls, payload: bytes) -> "AcceptedRadiationHistory":
        if not payload.startswith(_HISTORY_MAGIC):
            raise ValueError("unknown accepted-history binary magic")
        offset = len(_HISTORY_MAGIC)
        if len(payload) < offset + 8:
            raise ValueError("truncated accepted-history header")
        header_size = struct.unpack(">Q", payload[offset : offset + 8])[0]
        offset += 8
        header = json.loads(payload[offset : offset + header_size].decode("utf-8"))
        offset += header_size
        if header.get("schema") != "PR05B2_ACCEPTED_HISTORY_V1":
            raise ValueError("unknown accepted-history binary schema")
        arrays: dict[str, np.ndarray] = {}
        for specification in header["arrays"]:
            dtype = np.dtype(specification["dtype"])
            shape = tuple(int(value) for value in specification["shape"])
            nbytes = int(specification["nbytes"])
            block = payload[offset : offset + nbytes]
            if len(block) != nbytes:
                raise ValueError("truncated accepted-history array")
            arrays[specification["name"]] = np.frombuffer(block, dtype=dtype).reshape(shape).copy()
            offset += nbytes
        if offset != len(payload):
            raise ValueError("trailing bytes in accepted-history payload")
        grid = CharacteristicHistoryGrid(
            eta=arrays["eta"],
            source_indices=arrays["source_indices"],
            z_start=header["z_start"],
            dlna=header["dlna"],
            energy_eV=arrays["energy_eV"],
            source_hashes=header["source_hashes"],
        )
        if not np.array_equal(arrays["frequency_Hz"], grid.frequency_Hz):
            raise ValueError("binary ordinary-frequency registry is inconsistent")
        return cls(
            grid=grid,
            outgoing_virtual=arrays["outgoing_virtual"],
            outgoing_lyman=arrays["outgoing_lyman"],
            average_virtual=arrays["average_virtual"],
            completeness=header["completeness"],
        )


@dataclass(frozen=True)
class HistoryStepLedger:
    """Immutable accepted-step transaction and source-parity ledger."""

    target_z: float
    actual_z: float
    accepted_count_before: int
    candidate_index: int
    history_before_sha256: str
    candidate_parent_sha256: str
    incoming_virtual_relative: float
    incoming_lyman_relative: float
    native_residual_relative: float
    electron_rate_relative: float
    outgoing_virtual_relative: float
    outgoing_lyman_relative: float
    average_virtual_relative: float
    characteristic_number_relative: float
    characteristic_energy_relative: float
    interface_atom_source_W_per_H: float
    future_endpoint_count: int = 0
    stencil_switch_count: int = 0

    def __post_init__(self) -> None:
        for name in ("target_z", "actual_z"):
            value = float(getattr(self, name))
            if not math.isfinite(value) or value <= 0.0:
                raise ValueError(f"{name} must be positive and finite")
            object.__setattr__(self, name, value)
        for name in ("accepted_count_before", "candidate_index", "future_endpoint_count", "stencil_switch_count"):
            value = int(getattr(self, name))
            if value < 0:
                raise ValueError(f"{name} must be nonnegative")
            object.__setattr__(self, name, value)
        if self.candidate_index != self.accepted_count_before:
            raise ValueError("candidate index must be the next accepted history index")
        for name in ("history_before_sha256", "candidate_parent_sha256"):
            value = str(getattr(self, name)).lower()
            if len(value) != 64 or any(ch not in "0123456789abcdef" for ch in value):
                raise ValueError(f"{name} must be a SHA-256 hex string")
            object.__setattr__(self, name, value)
        if self.history_before_sha256 != self.candidate_parent_sha256:
            raise ValueError("candidate parent must equal the pre-step history hash")
        for name in (
            "incoming_virtual_relative",
            "incoming_lyman_relative",
            "native_residual_relative",
            "electron_rate_relative",
            "outgoing_virtual_relative",
            "outgoing_lyman_relative",
            "average_virtual_relative",
            "characteristic_number_relative",
            "characteristic_energy_relative",
            "interface_atom_source_W_per_H",
        ):
            value = float(getattr(self, name))
            if not math.isfinite(value):
                raise ValueError(f"{name} must be finite")
            if name != "interface_atom_source_W_per_H" and value < 0.0:
                raise ValueError(f"{name} must be nonnegative")
            object.__setattr__(self, name, value)


@dataclass(frozen=True)
class CharacteristicQuery:
    channel: str
    source_kind: str
    source_index: int
    target_kind: str
    target_index: int
    source_energy_eV: float
    target_energy_eV: float
    eta_query: float

    def __post_init__(self) -> None:
        allowed_kind = {"virtual", "lyman"}
        if self.source_kind not in allowed_kind or self.target_kind not in allowed_kind:
            raise ValueError("query kinds must be virtual or lyman")
        if not self.channel:
            raise ValueError("query channel is required")
        for name in ("source_energy_eV", "target_energy_eV"):
            value = float(getattr(self, name))
            if not math.isfinite(value) or value <= 0.0:
                raise ValueError(f"{name} must be positive")
            object.__setattr__(self, name, value)
        eta = float(self.eta_query)
        if not math.isfinite(eta):
            raise ValueError("eta_query must be finite")
        object.__setattr__(self, "eta_query", eta)


@dataclass(frozen=True)
class OriginalHyRecIncoming:
    virtual: np.ndarray
    lyman: np.ndarray
    queries: tuple[CharacteristicQuery, ...]
    stencils: tuple[CharacteristicInterpolationStencil, ...]

    def __post_init__(self) -> None:
        object.__setattr__(self, "virtual", _readonly_float_array(self.virtual, (NVIRT,), "virtual"))
        object.__setattr__(self, "lyman", _readonly_float_array(self.lyman, (2,), "lyman"))
        if len(self.queries) != 313 or len(self.stencils) != 313:
            raise ValueError("original-HyRec incoming registry must contain 313 queries")


def _query_eta(z: float, source_energy_eV: float, target_energy_eV: float) -> float:
    zp1 = 1.0 + float(z)
    if not math.isfinite(zp1) or zp1 <= 0.0:
        raise ValueError("z must exceed -1")
    return -math.log(zp1 * source_energy_eV / target_energy_eV)


def build_original_hyrec_queries(energy_eV: Sequence[float], *, z: float) -> tuple[CharacteristicQuery, ...]:
    energy = np.asarray(energy_eV, dtype=float)
    if energy.shape != (NVIRT,) or np.any(energy <= 0.0) or np.any(np.diff(energy) <= 0.0):
        raise ValueError("energy_eV must contain the increasing canonical virtual centres")
    queries: list[CharacteristicQuery] = []

    def add(channel: str, source_kind: str, source_index: int, target_kind: str, target_index: int, source_energy: float, target_energy: float) -> None:
        queries.append(
            CharacteristicQuery(
                channel=channel,
                source_kind=source_kind,
                source_index=source_index,
                target_kind=target_kind,
                target_index=target_index,
                source_energy_eV=source_energy,
                target_energy_eV=target_energy,
                eta_query=_query_eta(z, source_energy, target_energy),
            )
        )

    for b in range(0, NSUBLYA - 1):
        add("virtual_to_virtual", "virtual", b + 1, "virtual", b, energy[b + 1], energy[b])
    b = NSUBLYA - 1
    add("lya_to_virtual", "lyman", 0, "virtual", b, E21_EV, energy[b])
    b = NSUBLYA
    add("virtual_to_lya", "virtual", b, "lyman", 0, energy[b], E21_EV)
    for b in range(NSUBLYA, NSUBLYB - 1):
        add("virtual_to_virtual", "virtual", b + 1, "virtual", b, energy[b + 1], energy[b])
    b = NSUBLYB - 1
    add("lyb_to_virtual", "lyman", 1, "virtual", b, E31_EV, energy[b])
    b = NSUBLYB
    add("virtual_to_lyb", "virtual", b, "lyman", 1, energy[b], E31_EV)
    for b in range(NSUBLYB, NVIRT - 1):
        add("virtual_to_virtual", "virtual", b + 1, "virtual", b, energy[b + 1], energy[b])
    b = NVIRT - 1
    add("lyg_to_virtual", "lyman", 2, "virtual", b, E41_EV, energy[b])
    return tuple(queries)


def construct_original_hyrec_incoming(history: AcceptedRadiationHistory, *, z: float) -> OriginalHyRecIncoming:
    queries = build_original_hyrec_queries(history.grid.energy_eV, z=z)
    virtual = np.empty(NVIRT, dtype=float)
    lyman = np.empty(2, dtype=float)
    stencils: list[CharacteristicInterpolationStencil] = []
    for query in queries:
        stencil = history.grid.locate(query.eta_query, accepted_count=history.accepted_count)
        if query.source_kind == "virtual":
            source_values = history.outgoing_virtual[query.source_index]
        else:
            source_values = history.outgoing_lyman[query.source_index]
        value = stencil.evaluate(source_values)
        if query.target_kind == "virtual":
            virtual[query.target_index] = value
        else:
            lyman[query.target_index] = value
        stencils.append(stencil)
    return OriginalHyRecIncoming(
        virtual=virtual,
        lyman=lyman,
        queries=queries,
        stencils=tuple(stencils),
    )


def original_hyrec_incoming_jvp(
    history: AcceptedRadiationHistory,
    incoming: OriginalHyRecIncoming,
    *,
    outgoing_virtual_direction: np.ndarray,
    outgoing_lyman_direction: np.ndarray,
    eta_query_directions: Sequence[float] | None = None,
) -> tuple[np.ndarray, np.ndarray]:
    dv = np.asarray(outgoing_virtual_direction, dtype=float)
    dl = np.asarray(outgoing_lyman_direction, dtype=float)
    if dv.shape != history.outgoing_virtual.shape or dl.shape != history.outgoing_lyman.shape:
        raise ValueError("history JVP directions have invalid shapes")
    deta = np.zeros(len(incoming.queries), dtype=float) if eta_query_directions is None else np.asarray(eta_query_directions, dtype=float)
    if deta.shape != (len(incoming.queries),) or not np.all(np.isfinite(deta)):
        raise ValueError("eta_query_directions has invalid shape or values")
    virtual = np.empty(NVIRT, dtype=float)
    lyman = np.empty(2, dtype=float)
    for index, (query, stencil) in enumerate(zip(incoming.queries, incoming.stencils, strict=True)):
        if query.source_kind == "virtual":
            values = history.outgoing_virtual[query.source_index]
            direction = dv[query.source_index]
        else:
            values = history.outgoing_lyman[query.source_index]
            direction = dl[query.source_index]
        value = stencil.jvp(values, direction, delta_eta=float(deta[index]))
        if query.target_kind == "virtual":
            virtual[query.target_index] = value
        else:
            lyman[query.target_index] = value
    return virtual, lyman


__all__ = [
    "AcceptedRadiationHistory",
    "CANONICAL_DLNA",
    "CharacteristicHistoryGrid",
    "CharacteristicInterpolationStencil",
    "CharacteristicQuery",
    "CharacteristicStencilSwitch",
    "E31_EV",
    "E41_EV",
    "FutureHistoryEndpointError",
    "HistoryAppendCandidate",
    "HistoryStepLedger",
    "NSUBLYB",
    "OriginalHyRecIncoming",
    "build_original_hyrec_queries",
    "construct_original_hyrec_incoming",
    "original_hyrec_incoming_jvp",
]
