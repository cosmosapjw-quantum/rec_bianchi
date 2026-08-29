"""Locked z~1100 exterior-native/interior-COM replacement.

The original-HyRec virtual registry contains zero-width point spikes.  This
module therefore partitions only the source-defined points: indices 136..143
are COM-owned, the remaining points are native-owned, and diffusion edges
(135,136) and (143,144) are each owned once by the interface.  No native cell
width or fitted normalization is introduced.

The production action is the exterior Schur complement.  A separately
assembled dense primitive operator belongs in tests as the independent oracle;
this module never reports its own residual as proof of correctness.

Conventions
-----------
* metric signature ``(-,+,+,+)``;
* local hydrogen orthonormal tetrad;
* ordinary frequency in Hz;
* matrix coefficients and residuals have the original-HyRec algebraic units;
* interface number transfer is per H per second and interface energy transfer
  is W per H;
* a pure representation crossing has identically zero atomic source.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import math
from typing import Mapping, Sequence

import numpy as np
from scipy.constants import electron_volt

from full_bianchi_hyrec.recoil.original_hyrec_native import NVIRT
from full_bianchi_hyrec.recoil.original_hyrec_physical_flux import (
    OriginalHyRecTrajectorySnapshot,
    dense_original_hyrec_matrix,
)
from full_bianchi_hyrec.trajectory.primitive_rates import LYMAN_ALPHA_ENERGY_EV


LOCKED_INTERIOR_NATIVE_INDICES = tuple(range(136, 144))
LOCKED_CROSS_EDGES = ((135, 136), (143, 144))
LOCKED_INTERFACE_ABS_X = 21.25

_ALLOWED_OWNERS = {
    "exterior_native",
    "interior_com",
    "split_domain_interface",
    "typed_characteristic_history",
}
_REQUIRED_PROCESS_OWNERS = (
    ("native_diffusion_exterior", "exterior_native"),
    ("com_diffusion_interior", "interior_com"),
    ("native_atomic_source_exterior", "exterior_native"),
    ("com_atomic_source_interior", "interior_com"),
    ("completed_tvv_exterior_schur", "exterior_native"),
    ("cross_edge_135_136", "split_domain_interface"),
    ("cross_edge_143_144", "split_domain_interface"),
    ("scalar_characteristic_history", "typed_characteristic_history"),
)


def _readonly(
    value: Sequence[float] | np.ndarray,
    shape: tuple[int, ...],
    name: str,
    *,
    allow_complex: bool = False,
) -> np.ndarray:
    array = np.asarray(value)
    if array.shape != shape:
        raise ValueError(f"{name} must have shape {shape}, got {array.shape}")
    if array.dtype.kind not in ("f", "c"):
        array = np.asarray(array, dtype=float)
    if array.dtype.kind == "c" and not allow_complex:
        if np.any(array.imag != 0.0):
            raise ValueError(f"{name} must be real")
        array = array.real
    if not np.all(np.isfinite(array)):
        raise ValueError(f"{name} contains nonfinite values")
    result = np.array(array, copy=True)
    result.setflags(write=False)
    return result


def _history_sha256(dfplus: np.ndarray, dfminus: np.ndarray) -> str:
    digest = hashlib.sha256()
    for value in (dfplus, dfminus):
        array = np.asarray(value, dtype="<f8")
        digest.update(array.tobytes(order="C"))
    return digest.hexdigest()


def _readonly_indices(
    value: Sequence[int] | np.ndarray,
    shape: tuple[int, ...],
    name: str,
) -> np.ndarray:
    array = np.asarray(value, dtype=int)
    if array.shape != shape:
        raise ValueError(f"{name} must have shape {shape}, got {array.shape}")
    result = np.array(array, dtype=int, copy=True)
    result.setflags(write=False)
    return result


@dataclass(frozen=True)
class SplitDomainContext:
    """Local scalar context for one frozen-snapshot replacement action."""

    interface_enabled: bool = True
    flrw_limit: bool = False

    def __post_init__(self) -> None:
        if type(self.interface_enabled) is not bool:
            raise TypeError("interface_enabled must be bool")
        if type(self.flrw_limit) is not bool:
            raise TypeError("flrw_limit must be bool")


@dataclass(frozen=True)
class SplitDomainOwnershipAudit:
    process_count: int
    overlap_count: int
    unowned_process_count: int
    cross_edge_count: int
    implementation_evidence: bool


@dataclass(frozen=True)
class SplitDomainRegistry:
    """Exact point-support and one-owner process registry."""

    interior_indices: tuple[int, ...]
    cross_edges: tuple[tuple[int, int], ...]
    process_owners: tuple[tuple[str, str], ...] = ()
    implementation_evidence: bool = False

    def __post_init__(self) -> None:
        interior = tuple(int(value) for value in self.interior_indices)
        edges = tuple((int(left), int(right)) for left, right in self.cross_edges)
        if interior != LOCKED_INTERIOR_NATIVE_INDICES:
            raise ValueError("interior support must be exactly native indices 136..143")
        if edges != LOCKED_CROSS_EDGES:
            raise ValueError(
                "cross edges must be exactly (135,136) and (143,144)"
            )
        owners = tuple((str(process), str(owner)) for process, owner in self.process_owners)
        object.__setattr__(self, "interior_indices", interior)
        object.__setattr__(self, "cross_edges", edges)
        object.__setattr__(self, "process_owners", owners)

    def audit(self) -> SplitDomainOwnershipAudit:
        names = [process for process, _ in self.process_owners]
        duplicate_names = {name for name in names if names.count(name) > 1}
        present = set(names)
        required = dict(_REQUIRED_PROCESS_OWNERS)
        missing = set(required) - present
        extra = present - set(required)
        actual = dict(self.process_owners)
        wrong_owner = {
            process
            for process in set(required) & present
            if actual[process] != required[process]
        }
        invalid_owner = {
            process
            for process, owner in self.process_owners
            if owner not in _ALLOWED_OWNERS
        }
        unowned = len(missing | extra | wrong_owner | invalid_owner)
        cross_owned = sum(
            process in {"cross_edge_135_136", "cross_edge_143_144"}
            and owner == "split_domain_interface"
            for process, owner in self.process_owners
        )
        implemented = bool(
            self.implementation_evidence
            and not duplicate_names
            and unowned == 0
            and cross_owned == 2
        )
        return SplitDomainOwnershipAudit(
            process_count=len(self.process_owners),
            overlap_count=len(duplicate_names),
            unowned_process_count=unowned,
            cross_edge_count=cross_owned,
            implementation_evidence=implemented,
        )


@dataclass(frozen=True)
class SplitDomainSolution:
    exterior_state: np.ndarray
    interior_com_state: np.ndarray
    full_state: np.ndarray

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "exterior_state",
            _readonly(self.exterior_state, (2 + NVIRT - 8,), "exterior_state"),
        )
        object.__setattr__(
            self,
            "interior_com_state",
            _readonly(self.interior_com_state, (8,), "interior_com_state"),
        )
        object.__setattr__(
            self,
            "full_state",
            _readonly(self.full_state, (2 + NVIRT,), "full_state"),
        )


@dataclass(frozen=True)
class SplitDomainRestartState:
    exterior_state: np.ndarray
    interior_com_state: np.ndarray
    full_state: np.ndarray
    history_Dfplus: np.ndarray
    history_Dfminus: np.ndarray

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "exterior_state",
            _readonly(self.exterior_state, (2 + NVIRT - 8,), "exterior_state"),
        )
        object.__setattr__(
            self,
            "interior_com_state",
            _readonly(self.interior_com_state, (8,), "interior_com_state"),
        )
        object.__setattr__(
            self,
            "full_state",
            _readonly(self.full_state, (2 + NVIRT,), "full_state"),
        )
        object.__setattr__(
            self,
            "history_Dfplus",
            _readonly(self.history_Dfplus, (NVIRT,), "history_Dfplus"),
        )
        object.__setattr__(
            self,
            "history_Dfminus",
            _readonly(self.history_Dfminus, (NVIRT,), "history_Dfminus"),
        )


@dataclass(frozen=True)
class SplitDomainInterfaceEntry:
    edge: tuple[int, int]
    side: str
    interface_energy_J: float
    native_number_flux_per_H_s: float
    com_number_flux_per_H_s: float
    native_photon_energy_flux_W_per_H: float
    com_photon_energy_flux_W_per_H: float
    native_four_force_W_per_H: np.ndarray
    com_four_force_W_per_H: np.ndarray
    atom_source_W_per_H: float = 0.0

    def __post_init__(self) -> None:
        if self.edge not in LOCKED_CROSS_EDGES:
            raise ValueError("entry edge is not a locked crossing edge")
        if self.side not in {"red", "blue"}:
            raise ValueError("entry side must be red or blue")
        for name in (
            "interface_energy_J",
            "native_number_flux_per_H_s",
            "com_number_flux_per_H_s",
            "native_photon_energy_flux_W_per_H",
            "com_photon_energy_flux_W_per_H",
            "atom_source_W_per_H",
        ):
            value = float(getattr(self, name))
            if not math.isfinite(value):
                raise ValueError(f"{name} must be finite")
            object.__setattr__(self, name, value)
        if self.interface_energy_J <= 0.0:
            raise ValueError("interface energy must be positive")
        object.__setattr__(
            self,
            "native_four_force_W_per_H",
            _readonly(
                self.native_four_force_W_per_H,
                (4,),
                "native_four_force_W_per_H",
            ),
        )
        object.__setattr__(
            self,
            "com_four_force_W_per_H",
            _readonly(
                self.com_four_force_W_per_H,
                (4,),
                "com_four_force_W_per_H",
            ),
        )
        if self.native_number_flux_per_H_s + self.com_number_flux_per_H_s != 0.0:
            raise ValueError("interface number entries must be equal and opposite")
        if (
            self.native_photon_energy_flux_W_per_H
            != self.native_number_flux_per_H_s * self.interface_energy_J
            or self.com_photon_energy_flux_W_per_H
            != self.com_number_flux_per_H_s * self.interface_energy_J
        ):
            raise ValueError("interface photon energy has the wrong number-flux sign")
        if (
            self.native_photon_energy_flux_W_per_H
            + self.com_photon_energy_flux_W_per_H
            != 0.0
        ):
            raise ValueError("interface energy entries must be equal and opposite")
        expected_native_four_force = np.asarray(
            (self.native_photon_energy_flux_W_per_H, 0.0, 0.0, 0.0)
        )
        expected_com_four_force = np.asarray(
            (self.com_photon_energy_flux_W_per_H, 0.0, 0.0, 0.0)
        )
        if not np.array_equal(
            self.native_four_force_W_per_H, expected_native_four_force
        ) or not np.array_equal(
            self.com_four_force_W_per_H, expected_com_four_force
        ):
            raise ValueError("interface four-force is inconsistent with photon energy")
        if not np.array_equal(
            self.native_four_force_W_per_H + self.com_four_force_W_per_H,
            np.zeros(4),
        ):
            raise ValueError("interface four-force entries must be equal and opposite")
        if self.atom_source_W_per_H != 0.0:
            raise ValueError("pure representation crossing has nonzero atom source")


@dataclass(frozen=True)
class SplitDomainLedger:
    entries: tuple[SplitDomainInterfaceEntry, ...]
    native_number_flux_per_H_s: float
    com_number_flux_per_H_s: float
    native_photon_energy_flux_W_per_H: float
    com_photon_energy_flux_W_per_H: float
    native_four_force_W_per_H: np.ndarray
    com_four_force_W_per_H: np.ndarray
    atom_source_W_per_H: float

    def __post_init__(self) -> None:
        for entry in self.entries:
            if not isinstance(entry, SplitDomainInterfaceEntry):
                raise TypeError("ledger entries must be SplitDomainInterfaceEntry")
        for name in (
            "native_number_flux_per_H_s",
            "com_number_flux_per_H_s",
            "native_photon_energy_flux_W_per_H",
            "com_photon_energy_flux_W_per_H",
            "atom_source_W_per_H",
        ):
            value = float(getattr(self, name))
            if not math.isfinite(value):
                raise ValueError(f"{name} must be finite")
            object.__setattr__(self, name, value)
        object.__setattr__(
            self,
            "native_four_force_W_per_H",
            _readonly(
                self.native_four_force_W_per_H,
                (4,),
                "native_four_force_W_per_H",
            ),
        )
        object.__setattr__(
            self,
            "com_four_force_W_per_H",
            _readonly(
                self.com_four_force_W_per_H,
                (4,),
                "com_four_force_W_per_H",
            ),
        )
        self.validate()

    @property
    def number_residual_per_H_s(self) -> float:
        return self.native_number_flux_per_H_s + self.com_number_flux_per_H_s

    @property
    def photon_energy_residual_W_per_H(self) -> float:
        return (
            self.native_photon_energy_flux_W_per_H
            + self.com_photon_energy_flux_W_per_H
        )

    @property
    def four_force_residual_W_per_H(self) -> np.ndarray:
        return self.native_four_force_W_per_H + self.com_four_force_W_per_H

    def validate(self) -> None:
        if len(self.entries) not in {0, 2}:
            raise ValueError("ledger must contain zero or two locked interface entries")
        if len({entry.edge for entry in self.entries}) != len(self.entries):
            raise ValueError("an interface edge was evaluated more than once")
        if self.number_residual_per_H_s != 0.0:
            raise ValueError("interface number ledger does not cancel exactly")
        if self.photon_energy_residual_W_per_H != 0.0:
            raise ValueError("interface photon-energy ledger does not cancel exactly")
        if not np.array_equal(self.four_force_residual_W_per_H, np.zeros(4)):
            raise ValueError("interface four-force ledger does not cancel exactly")
        if self.atom_source_W_per_H != 0.0:
            raise ValueError("pure representation crossing has nonzero atom source")


@dataclass(frozen=True)
class SplitDomainReplacement:
    """Exterior Schur action with COM-owned interior and one interface owner."""

    snapshot: OriginalHyRecTrajectorySnapshot
    doppler_width_eV: float
    interface_abs_x: float
    registry: SplitDomainRegistry
    _full_matrix: np.ndarray
    _matrix_without_interface: np.ndarray
    _right_hand_side: np.ndarray
    _exterior_full_indices: np.ndarray
    _interior_full_indices: np.ndarray

    def __post_init__(self) -> None:
        if not isinstance(self.snapshot, OriginalHyRecTrajectorySnapshot):
            raise TypeError("snapshot must be OriginalHyRecTrajectorySnapshot")
        width = float(self.doppler_width_eV)
        boundary = float(self.interface_abs_x)
        if not math.isfinite(width) or width <= 0.0:
            raise ValueError("doppler_width_eV must be positive and finite")
        if boundary != LOCKED_INTERFACE_ABS_X:
            raise ValueError("interface_abs_x must be exactly 21.25")
        object.__setattr__(self, "doppler_width_eV", width)
        object.__setattr__(self, "interface_abs_x", boundary)
        n_full = 2 + NVIRT
        object.__setattr__(
            self,
            "_full_matrix",
            _readonly(self._full_matrix, (n_full, n_full), "_full_matrix"),
        )
        object.__setattr__(
            self,
            "_matrix_without_interface",
            _readonly(
                self._matrix_without_interface,
                (n_full, n_full),
                "_matrix_without_interface",
            ),
        )
        object.__setattr__(
            self,
            "_right_hand_side",
            _readonly(self._right_hand_side, (n_full,), "_right_hand_side"),
        )
        object.__setattr__(
            self,
            "_exterior_full_indices",
            _readonly_indices(
                self._exterior_full_indices,
                (n_full - 8,),
                "_exterior_full_indices",
            ),
        )
        object.__setattr__(
            self,
            "_interior_full_indices",
            _readonly_indices(
                self._interior_full_indices,
                (8,),
                "_interior_full_indices",
            ),
        )

    @classmethod
    def from_snapshot(
        cls,
        snapshot: OriginalHyRecTrajectorySnapshot,
        doppler_width_eV: float,
        interface_abs_x: float = LOCKED_INTERFACE_ABS_X,
    ) -> "SplitDomainReplacement":
        if not isinstance(snapshot, OriginalHyRecTrajectorySnapshot):
            raise TypeError("snapshot must be OriginalHyRecTrajectorySnapshot")
        width = float(doppler_width_eV)
        boundary = float(interface_abs_x)
        if not math.isfinite(width) or width <= 0.0:
            raise ValueError("doppler_width_eV must be positive and finite")
        if boundary != LOCKED_INTERFACE_ABS_X:
            raise ValueError("interface_abs_x must be exactly 21.25")

        x = (snapshot.energy_eV - LYMAN_ALPHA_ENERGY_EV) / width
        observed_interior = tuple(
            int(index) for index in np.flatnonzero(np.abs(x) <= boundary)
        )
        observed_cross_edges: list[tuple[int, int]] = []
        for index in range(NVIRT - 1):
            rate = max(abs(float(snapshot.Tvv[2, index])), abs(float(snapshot.Tvv[1, index + 1])))
            if rate == 0.0:
                continue
            if (index in observed_interior) != (index + 1 in observed_interior):
                observed_cross_edges.append((index, index + 1))
        if observed_interior != LOCKED_INTERIOR_NATIVE_INDICES:
            raise ValueError("snapshot does not have the locked 136..143 interior support")
        if tuple(observed_cross_edges) != LOCKED_CROSS_EDGES:
            raise ValueError("snapshot does not have the two locked crossing edges")

        # The constants, not a reconstructed cell geometry, are the operative
        # ownership registry.  The calculation above only rejects a source
        # snapshot that does not realize the already locked point support.
        interior_indices = LOCKED_INTERIOR_NATIVE_INDICES
        cross_edges = LOCKED_CROSS_EDGES

        process_owners = (
            ("native_diffusion_exterior", "exterior_native"),
            ("com_diffusion_interior", "interior_com"),
            ("native_atomic_source_exterior", "exterior_native"),
            ("com_atomic_source_interior", "interior_com"),
            ("completed_tvv_exterior_schur", "exterior_native"),
            ("cross_edge_135_136", "split_domain_interface"),
            ("cross_edge_143_144", "split_domain_interface"),
            ("scalar_characteristic_history", "typed_characteristic_history"),
        )
        registry = SplitDomainRegistry(
            interior_indices=interior_indices,
            cross_edges=cross_edges,
            process_owners=process_owners,
            implementation_evidence=True,
        )
        if not registry.audit().implementation_evidence:
            raise ValueError("replacement registry is not one-owner complete")

        full = dense_original_hyrec_matrix(snapshot)
        without_interface = np.array(full, copy=True)
        for left, right in LOCKED_CROSS_EDGES:
            left_full = 2 + left
            right_full = 2 + right
            left_to_right = float(snapshot.Aup_s_inv[left])
            right_to_left = float(snapshot.Adn_s_inv[right])
            if full[right_full, left_full] != -left_to_right:
                raise ValueError("left-to-right interface coefficient is not source exact")
            if full[left_full, right_full] != -right_to_left:
                raise ValueError("right-to-left interface coefficient is not source exact")
            without_interface[left_full, left_full] -= left_to_right
            without_interface[right_full, right_full] -= right_to_left
            without_interface[right_full, left_full] = 0.0
            without_interface[left_full, right_full] = 0.0

        interior_full = np.asarray([2 + index for index in interior_indices], dtype=int)
        interior_set = set(int(value) for value in interior_full)
        exterior_full = np.asarray(
            [index for index in range(2 + NVIRT) if index not in interior_set],
            dtype=int,
        )
        right_hand_side = np.concatenate((snapshot.sr, snapshot.sv))
        return cls(
            snapshot=snapshot,
            doppler_width_eV=width,
            interface_abs_x=boundary,
            registry=registry,
            _full_matrix=full,
            _matrix_without_interface=without_interface,
            _right_hand_side=right_hand_side,
            _exterior_full_indices=exterior_full,
            _interior_full_indices=interior_full,
        )

    @property
    def exterior_state_size(self) -> int:
        return int(self._exterior_full_indices.size)

    @property
    def interior_atomic_real_to_com(self) -> np.ndarray:
        result = self._full_matrix[np.ix_(self._interior_full_indices, np.asarray([0, 1]))]
        result.setflags(write=False)
        return result

    @property
    def interior_atomic_com_to_real(self) -> np.ndarray:
        result = self._full_matrix[np.ix_(np.asarray([0, 1]), self._interior_full_indices)]
        result.setflags(write=False)
        return result

    def _context_matrix(self, context: SplitDomainContext) -> np.ndarray:
        if not isinstance(context, SplitDomainContext):
            raise TypeError("context must be SplitDomainContext")
        # At fixed local scalar state the FLRW label does not alter the
        # hydrogen-frame microphysics.  It is retained as an explicit parity
        # context rather than silently changing conventions.
        return self._full_matrix if context.interface_enabled else self._matrix_without_interface

    def _partition(self, context: SplitDomainContext):
        matrix = self._context_matrix(context)
        exterior = self._exterior_full_indices
        interior = self._interior_full_indices
        a_ee = matrix[np.ix_(exterior, exterior)]
        a_ei = matrix[np.ix_(exterior, interior)]
        a_ie = matrix[np.ix_(interior, exterior)]
        a_ii = matrix[np.ix_(interior, interior)]
        b_e = self._right_hand_side[exterior]
        b_i = self._right_hand_side[interior]
        inverse_a_ie = np.linalg.solve(a_ii, a_ie)
        inverse_b_i = np.linalg.solve(a_ii, b_i)
        schur = a_ee - a_ei @ inverse_a_ie
        reduced_rhs = b_e - a_ei @ inverse_b_i
        return schur, reduced_rhs, inverse_a_ie, inverse_b_i

    def solve(self, context: SplitDomainContext) -> SplitDomainSolution:
        schur, reduced_rhs, inverse_a_ie, inverse_b_i = self._partition(context)
        exterior_state = np.linalg.solve(schur, reduced_rhs)
        interior_state = inverse_b_i - inverse_a_ie @ exterior_state
        full_state = np.empty(2 + NVIRT)
        full_state[self._exterior_full_indices] = exterior_state
        full_state[self._interior_full_indices] = interior_state
        return SplitDomainSolution(exterior_state, interior_state, full_state)

    def residual(
        self,
        state: Sequence[float] | np.ndarray,
        context: SplitDomainContext,
    ) -> np.ndarray:
        value = _readonly(
            state,
            (self.exterior_state_size,),
            "state",
            allow_complex=True,
        )
        schur, reduced_rhs, _, _ = self._partition(context)
        return schur @ value - reduced_rhs

    def jvp(
        self,
        state: Sequence[float] | np.ndarray,
        direction: Sequence[float] | np.ndarray,
        context: SplitDomainContext,
    ) -> np.ndarray:
        _readonly(state, (self.exterior_state_size,), "state", allow_complex=True)
        tangent = _readonly(
            direction,
            (self.exterior_state_size,),
            "direction",
            allow_complex=True,
        )
        schur, _, _, _ = self._partition(context)
        return schur @ tangent

    def operator_condition_number(self, context: SplitDomainContext) -> float:
        schur, _, _, _ = self._partition(context)
        return float(np.linalg.cond(schur))

    def operator_residual(
        self,
        state: Sequence[float] | np.ndarray,
        context: SplitDomainContext,
    ) -> float:
        value = _readonly(state, (self.exterior_state_size,), "state")
        schur, reduced_rhs, _, _ = self._partition(context)
        residual = schur @ value - reduced_rhs
        denominator = (
            np.linalg.norm(schur, ord=np.inf) * np.linalg.norm(value, ord=np.inf)
            + np.linalg.norm(reduced_rhs, ord=np.inf)
        )
        return float(np.linalg.norm(residual, ord=np.inf) / max(denominator, 1.0e-300))

    def _full_state_from_exterior(
        self,
        state: Sequence[float] | np.ndarray,
        context: SplitDomainContext,
    ) -> np.ndarray:
        value = _readonly(state, (self.exterior_state_size,), "state")
        _, _, inverse_a_ie, inverse_b_i = self._partition(context)
        interior_state = inverse_b_i - inverse_a_ie @ value
        full_state = np.empty(2 + NVIRT)
        full_state[self._exterior_full_indices] = value
        full_state[self._interior_full_indices] = interior_state
        return full_state

    def ledger(
        self,
        state: Sequence[float] | np.ndarray,
        context: SplitDomainContext,
    ) -> SplitDomainLedger:
        full_state = self._full_state_from_exterior(state, context)
        if not context.interface_enabled:
            return SplitDomainLedger(
                entries=(),
                native_number_flux_per_H_s=0.0,
                com_number_flux_per_H_s=0.0,
                native_photon_energy_flux_W_per_H=0.0,
                com_photon_energy_flux_W_per_H=0.0,
                native_four_force_W_per_H=np.zeros(4),
                com_four_force_W_per_H=np.zeros(4),
                atom_source_W_per_H=0.0,
            )

        entries: list[SplitDomainInterfaceEntry] = []
        for left, right in LOCKED_CROSS_EDGES:
            left_to_right = float(self.snapshot.Aup_s_inv[left])
            right_to_left = float(self.snapshot.Adn_s_inv[right])
            pair_flux = (
                left_to_right * full_state[2 + left]
                - right_to_left * full_state[2 + right]
            )
            if left in self.registry.interior_indices:
                native_number = pair_flux
                side = "blue"
                sign_x = 1.0
            else:
                native_number = -pair_flux
                side = "red"
                sign_x = -1.0
            com_number = -native_number
            interface_energy_eV = (
                LYMAN_ALPHA_ENERGY_EV
                + sign_x * self.interface_abs_x * self.doppler_width_eV
            )
            interface_energy_J = (
                interface_energy_eV
                * self.snapshot.fsR**2
                * self.snapshot.meR
                * electron_volt
            )
            native_energy = native_number * interface_energy_J
            com_energy = -native_energy
            native_four_force = np.asarray((native_energy, 0.0, 0.0, 0.0))
            com_four_force = -native_four_force
            entries.append(
                SplitDomainInterfaceEntry(
                    edge=(left, right),
                    side=side,
                    interface_energy_J=interface_energy_J,
                    native_number_flux_per_H_s=native_number,
                    com_number_flux_per_H_s=com_number,
                    native_photon_energy_flux_W_per_H=native_energy,
                    com_photon_energy_flux_W_per_H=com_energy,
                    native_four_force_W_per_H=native_four_force,
                    com_four_force_W_per_H=com_four_force,
                    atom_source_W_per_H=0.0,
                )
            )

        native_number = float(sum(entry.native_number_flux_per_H_s for entry in entries))
        native_energy = float(
            sum(entry.native_photon_energy_flux_W_per_H for entry in entries)
        )
        native_four_force = np.sum(
            [entry.native_four_force_W_per_H for entry in entries], axis=0
        )
        return SplitDomainLedger(
            entries=tuple(entries),
            native_number_flux_per_H_s=native_number,
            com_number_flux_per_H_s=-native_number,
            native_photon_energy_flux_W_per_H=native_energy,
            com_photon_energy_flux_W_per_H=-native_energy,
            native_four_force_W_per_H=native_four_force,
            com_four_force_W_per_H=-native_four_force,
            atom_source_W_per_H=0.0,
        )

    def restart_record(self) -> dict[str, object]:
        context = SplitDomainContext()
        solution = self.solve(context)
        registry_payload = {
            "interior_indices": list(self.registry.interior_indices),
            "cross_edges": [list(edge) for edge in self.registry.cross_edges],
            "process_owners": [list(item) for item in self.registry.process_owners],
        }
        registry_sha256 = hashlib.sha256(
            json.dumps(
                registry_payload,
                sort_keys=True,
                separators=(",", ":"),
                allow_nan=False,
            ).encode("utf-8")
        ).hexdigest()
        return {
            "schema": "rec-split-domain-restart/v1",
            "source_z": self.snapshot.z,
            "source_index": self.snapshot.iz_local,
            "context": {
                "interface_enabled": context.interface_enabled,
                "flrw_limit": context.flrw_limit,
            },
            "registry": registry_payload,
            "registry_sha256": registry_sha256,
            "exterior_state": solution.exterior_state.tolist(),
            "interior_com_state": solution.interior_com_state.tolist(),
            "full_state": solution.full_state.tolist(),
            "history_Dfplus": self.snapshot.Dfplus.tolist(),
            "history_Dfminus": self.snapshot.Dfminus.tolist(),
            "history_sha256": _history_sha256(
                self.snapshot.Dfplus, self.snapshot.Dfminus
            ),
        }

    def state_from_restart_record(
        self,
        record: Mapping[str, object],
    ) -> SplitDomainRestartState:
        if not isinstance(record, Mapping):
            raise TypeError("restart record must be a mapping")
        if record.get("schema") != "rec-split-domain-restart/v1":
            raise ValueError("unsupported split-domain restart schema")
        if float(record.get("source_z", math.nan)) != self.snapshot.z:
            raise ValueError("restart source redshift mismatch")
        if int(record.get("source_index", -1)) != self.snapshot.iz_local:
            raise ValueError("restart source index mismatch")
        context_payload = record.get("context")
        expected_context = {
            "interface_enabled": True,
            "flrw_limit": False,
        }
        if not isinstance(context_payload, Mapping) or dict(context_payload) != expected_context:
            raise ValueError("restart context differs from the locked replacement")
        registry_payload = record.get("registry")
        if not isinstance(registry_payload, Mapping):
            raise ValueError("restart registry is missing")
        canonical_registry = {
            "interior_indices": list(self.registry.interior_indices),
            "cross_edges": [list(edge) for edge in self.registry.cross_edges],
            "process_owners": [list(item) for item in self.registry.process_owners],
        }
        if dict(registry_payload) != canonical_registry:
            raise ValueError("restart registry differs from locked replacement")
        registry_sha256 = hashlib.sha256(
            json.dumps(
                canonical_registry,
                sort_keys=True,
                separators=(",", ":"),
                allow_nan=False,
            ).encode("utf-8")
        ).hexdigest()
        if record.get("registry_sha256") != registry_sha256:
            raise ValueError("restart registry digest mismatch")

        restored = SplitDomainRestartState(
            exterior_state=np.asarray(record.get("exterior_state"), dtype=float),
            interior_com_state=np.asarray(
                record.get("interior_com_state"), dtype=float
            ),
            full_state=np.asarray(record.get("full_state"), dtype=float),
            history_Dfplus=np.asarray(record.get("history_Dfplus"), dtype=float),
            history_Dfminus=np.asarray(record.get("history_Dfminus"), dtype=float),
        )
        if record.get("history_sha256") != _history_sha256(
            restored.history_Dfplus, restored.history_Dfminus
        ):
            raise ValueError("restart history digest mismatch")
        if not np.array_equal(restored.history_Dfplus, self.snapshot.Dfplus):
            raise ValueError("restart Dfplus history differs from the source snapshot")
        if not np.array_equal(restored.history_Dfminus, self.snapshot.Dfminus):
            raise ValueError("restart Dfminus history differs from the source snapshot")
        expected = self.solve(SplitDomainContext())
        if not np.array_equal(restored.exterior_state, expected.exterior_state):
            raise ValueError("restart exterior state mismatch")
        if not np.array_equal(restored.interior_com_state, expected.interior_com_state):
            raise ValueError("restart interior COM state mismatch")
        if not np.array_equal(restored.full_state, expected.full_state):
            raise ValueError("restart full state mismatch")
        return restored


__all__ = [
    "LOCKED_INTERIOR_NATIVE_INDICES",
    "LOCKED_CROSS_EDGES",
    "LOCKED_INTERFACE_ABS_X",
    "SplitDomainContext",
    "SplitDomainOwnershipAudit",
    "SplitDomainRegistry",
    "SplitDomainSolution",
    "SplitDomainRestartState",
    "SplitDomainInterfaceEntry",
    "SplitDomainLedger",
    "SplitDomainReplacement",
]
