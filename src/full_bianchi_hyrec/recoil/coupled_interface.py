"""Conservative far-boundary coupling for PR-04C1B/C2.

The original-HyRec radiation representation and the 35-state COM--KHW
collision representation remain distinct.  A source-derived interface packet
changes only the exact outer COM state (`FR00` or `FB02`) through a finite-volume
number flux.  Exact face-frequency energy is retained independently from the
finite-cell energy centroid so a representation boundary cannot manufacture an
atomic recoil source.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import math
from typing import Mapping

import numpy as np
from scipy.constants import c, h

from .nonlinear_bose_release import (
    HarmonicGrid,
    apply_nonlinear_bose_jvp,
    apply_nonlinear_bose_operator,
)
from .nonlinear_bose_runtime import CollisionNetwork
from .split_domain_exchange import (
    ExchangeDirection,
    ExchangePacket,
    InterfaceSide,
)


_REL_TOL = 3.0e-14
_ABS_TOL = 1.0e-300


def _close(first: float, second: float) -> bool:
    return math.isclose(float(first), float(second), rel_tol=_REL_TOL, abs_tol=_ABS_TOL)


@dataclass(frozen=True)
class FarBoundaryCell:
    """Exact COM--KHW cell adjacent to one physical interface face."""

    side: InterfaceSide
    label: str
    index: int
    interval: tuple[float, float]
    face_x: float
    mode_measure_m3: float
    equilibrium_weight_m3: float
    centroid_frequency_Hz: float

    def __post_init__(self) -> None:
        left, right = self.interval
        if not (math.isfinite(left) and math.isfinite(right) and right > left):
            raise ValueError("boundary interval must be finite and ordered")
        if self.index < 0 or not self.label:
            raise ValueError("boundary state identity is invalid")
        if self.mode_measure_m3 <= 0.0 or self.equilibrium_weight_m3 <= 0.0:
            raise ValueError("boundary measures must be positive")
        if self.centroid_frequency_Hz <= 0.0:
            raise ValueError("boundary centroid frequency must be positive")
        expected_label = "FR00" if self.side is InterfaceSide.RED else "FB02"
        expected_face = -21.25 if self.side is InterfaceSide.RED else 21.25
        expected_interval_face = left if self.side is InterfaceSide.RED else right
        if self.label != expected_label:
            raise ValueError("boundary label is inconsistent with interface side")
        if not _close(self.face_x, expected_face) or not _close(
            expected_interval_face, expected_face
        ):
            raise ValueError("boundary interval does not meet the declared face")


@dataclass(frozen=True)
class FarBoundaryAdapter:
    """Byte-derived ownership adapter for `FR00` and `FB02`."""

    network: CollisionNetwork
    red: FarBoundaryCell
    blue: FarBoundaryCell

    @classmethod
    def from_network(cls, network: CollisionNetwork) -> "FarBoundaryAdapter":
        if not isinstance(network, CollisionNetwork):
            raise TypeError("network must be a CollisionNetwork")
        labels = network.state_labels.astype(str).tolist()

        def build(side: InterfaceSide, label: str) -> FarBoundaryCell:
            matches = [index for index, value in enumerate(labels) if value == label]
            if len(matches) != 1:
                raise ValueError(f"expected exactly one {label} boundary state")
            index = matches[0]
            interval = tuple(float(value) for value in network.state_intervals[index])
            face_x = -21.25 if side is InterfaceSide.RED else 21.25
            centroid = float(network.momentum_scale[index] * c / h)
            return FarBoundaryCell(
                side=side,
                label=label,
                index=index,
                interval=interval,
                face_x=face_x,
                mode_measure_m3=float(network.mode_measure[index]),
                equilibrium_weight_m3=float(network.equilibrium_weight[index]),
                centroid_frequency_Hz=centroid,
            )

        return cls(
            network=network,
            red=build(InterfaceSide.RED, "FR00"),
            blue=build(InterfaceSide.BLUE, "FB02"),
        )

    def for_side(self, side: InterfaceSide) -> FarBoundaryCell:
        side = InterfaceSide(side)
        return self.red if side is InterfaceSide.RED else self.blue

    def occupation_increment(
        self,
        accumulator: "BoundaryTransferAccumulator",
        *,
        n_H_m3: float,
        angular_weights: np.ndarray,
    ) -> np.ndarray:
        """Return the integrated uniform-angular COM occupation increment.

        The unique scalar conversion is

        ``Delta f = sigma n_H q / g_cell``

        where ``q`` is the integrated packet number per H and the normalized
        angular weights sum to one.
        """

        if not isinstance(accumulator, BoundaryTransferAccumulator):
            raise TypeError("accumulator must be a BoundaryTransferAccumulator")
        if not math.isfinite(n_H_m3) or n_H_m3 <= 0.0:
            raise ValueError("n_H_m3 must be positive and finite")
        weights = np.asarray(angular_weights, dtype=float)
        if weights.ndim != 1 or len(weights) == 0:
            raise ValueError("angular_weights must be one-dimensional")
        if np.any(weights <= 0.0) or not np.all(np.isfinite(weights)):
            raise ValueError("angular_weights must be finite and positive")
        if not math.isclose(float(np.sum(weights)), 1.0, rel_tol=3e-14, abs_tol=3e-15):
            raise ValueError("angular_weights must sum to one")

        cell = self.for_side(accumulator.side)
        expected_direction = (
            ExchangeDirection.COM_TO_NATIVE
            if accumulator.side is InterfaceSide.RED
            else ExchangeDirection.NATIVE_TO_COM
        )
        if accumulator.direction is not expected_direction:
            raise ValueError("accumulator direction is inconsistent with side")
        sign_com = -1.0 if accumulator.side is InterfaceSide.RED else 1.0
        increment = np.zeros((self.network.n_state, len(weights)), dtype=float)
        increment[cell.index, :] = (
            sign_com * float(n_H_m3) * accumulator.number_per_H / cell.mode_measure_m3
        )
        return increment


@dataclass(frozen=True)
class BoundaryTransferAccumulator:
    """Positive integrated transfer magnitude for one source-derived packet."""

    side: InterfaceSide
    direction: ExchangeDirection
    interface_x: float
    interface_frequency_Hz: float
    number_per_H: float
    reference_number_per_H: float
    distortion_number_per_H: float
    energy_J_per_H: float
    reference_energy_J_per_H: float
    distortion_energy_J_per_H: float
    atom_energy_J_per_H: float
    source_snapshot_z: float
    dt_s: float

    def __post_init__(self) -> None:
        values = (
            self.interface_x,
            self.interface_frequency_Hz,
            self.number_per_H,
            self.reference_number_per_H,
            self.distortion_number_per_H,
            self.energy_J_per_H,
            self.reference_energy_J_per_H,
            self.distortion_energy_J_per_H,
            self.atom_energy_J_per_H,
            self.source_snapshot_z,
            self.dt_s,
        )
        if not all(math.isfinite(float(value)) for value in values):
            raise ValueError("accumulator fields must be finite")
        if self.dt_s <= 0.0:
            raise ValueError("dt_s must be positive")
        if self.number_per_H <= 0.0 or self.energy_J_per_H <= 0.0:
            raise ValueError("integrated number and energy must be positive")
        if self.reference_number_per_H < 0.0 or self.reference_energy_J_per_H < 0.0:
            raise ValueError("reference components must be nonnegative")
        if not _close(
            self.number_per_H,
            self.reference_number_per_H + self.distortion_number_per_H,
        ):
            raise ValueError("number components do not add to total")
        if not _close(
            self.energy_J_per_H,
            self.reference_energy_J_per_H + self.distortion_energy_J_per_H,
        ):
            raise ValueError("energy components do not add to total")
        if not _close(self.atom_energy_J_per_H, 0.0):
            raise ValueError("pure interface transfer must have zero atom energy")
        if not _close(
            self.energy_J_per_H,
            h * self.interface_frequency_Hz * self.number_per_H,
        ):
            raise ValueError("integrated energy is inconsistent with face frequency")
        expected_x = -21.25 if self.side is InterfaceSide.RED else 21.25
        expected_direction = (
            ExchangeDirection.COM_TO_NATIVE
            if self.side is InterfaceSide.RED
            else ExchangeDirection.NATIVE_TO_COM
        )
        if not _close(self.interface_x, expected_x):
            raise ValueError("interface x is inconsistent with side")
        if self.direction is not expected_direction:
            raise ValueError("direction is inconsistent with interface side")

    @classmethod
    def from_packet(
        cls,
        packet: ExchangePacket,
        *,
        dt_s: float,
    ) -> "BoundaryTransferAccumulator":
        if not isinstance(packet, ExchangePacket):
            raise TypeError("packet must be an ExchangePacket")
        if not math.isfinite(dt_s) or dt_s <= 0.0:
            raise ValueError("dt_s must be positive and finite")
        return cls(
            side=packet.side,
            direction=packet.direction,
            interface_x=packet.interface_x,
            interface_frequency_Hz=packet.interface_frequency_Hz,
            number_per_H=packet.total_number_flux_per_H_s * dt_s,
            reference_number_per_H=packet.reference_number_flux_per_H_s * dt_s,
            distortion_number_per_H=packet.distortion_number_flux_per_H_s * dt_s,
            energy_J_per_H=packet.photon_energy_flux_W_per_H * dt_s,
            reference_energy_J_per_H=packet.reference_photon_energy_flux_W_per_H * dt_s,
            distortion_energy_J_per_H=packet.distortion_photon_energy_flux_W_per_H * dt_s,
            atom_energy_J_per_H=packet.atom_energy_flux_W_per_H * dt_s,
            source_snapshot_z=packet.source_snapshot_z,
            dt_s=float(dt_s),
        )

    def to_dict(self) -> dict[str, float | str]:
        return {
            "side": self.side.value,
            "direction": self.direction.value,
            "interface_x": self.interface_x,
            "interface_frequency_Hz": self.interface_frequency_Hz,
            "number_per_H": self.number_per_H,
            "reference_number_per_H": self.reference_number_per_H,
            "distortion_number_per_H": self.distortion_number_per_H,
            "energy_J_per_H": self.energy_J_per_H,
            "reference_energy_J_per_H": self.reference_energy_J_per_H,
            "distortion_energy_J_per_H": self.distortion_energy_J_per_H,
            "atom_energy_J_per_H": self.atom_energy_J_per_H,
            "source_snapshot_z": self.source_snapshot_z,
            "dt_s": self.dt_s,
        }

    @classmethod
    def from_dict(
        cls, values: Mapping[str, float | str]
    ) -> "BoundaryTransferAccumulator":
        payload = dict(values)
        payload["side"] = InterfaceSide(str(payload["side"]))
        payload["direction"] = ExchangeDirection(str(payload["direction"]))
        return cls(**payload)  # type: ignore[arg-type]

    @property
    def sha256(self) -> str:
        payload = json.dumps(
            self.to_dict(), sort_keys=True, separators=(",", ":"), allow_nan=False
        ).encode("utf-8")
        return hashlib.sha256(payload).hexdigest()


@dataclass(frozen=True)
class CoupledInterfaceProblem:
    """Source-conditioned monolithic collision/interface residual.

    Resolved occupations use ``f=exp(u)``.  Each positive integrated packet is
    multiplied by ``rho=exp(v)`` and constrained by ``rho-1=0`` in the same
    residual, which keeps the transfer block nonsingular while retaining the
    packet as an explicit nonlinear unknown.
    """

    network: CollisionNetwork
    grid: HarmonicGrid
    packets: tuple[ExchangePacket, ...]
    n_H_m3: float
    dt_s: float
    enabled: bool = True

    def __post_init__(self) -> None:
        if not isinstance(self.network, CollisionNetwork):
            raise TypeError("network must be a CollisionNetwork")
        if not isinstance(self.grid, HarmonicGrid):
            raise TypeError("grid must be a HarmonicGrid")
        if not math.isfinite(self.n_H_m3) or self.n_H_m3 <= 0.0:
            raise ValueError("n_H_m3 must be positive and finite")
        if not math.isfinite(self.dt_s) or self.dt_s <= 0.0:
            raise ValueError("dt_s must be positive and finite")
        if not self.enabled and self.packets:
            # Guard-off is represented by an empty transfer block.  This avoids
            # a logarithm of an exact zero accumulator.
            object.__setattr__(self, "packets", tuple())
        if self.enabled and not self.packets:
            raise ValueError("enabled interface requires at least one packet")
        if len({packet.side for packet in self.packets}) != len(self.packets):
            raise ValueError("at most one packet per interface side is allowed")
        ordered = tuple(
            sorted(
                self.packets,
                key=lambda packet: 0 if packet.side is InterfaceSide.RED else 1,
            )
        )
        if ordered and len({packet.source_snapshot_z for packet in ordered}) != 1:
            raise ValueError("coupled packets must come from one source snapshot")
        object.__setattr__(self, "packets", ordered)
        object.__setattr__(self, "adapter", FarBoundaryAdapter.from_network(self.network))
        object.__setattr__(
            self,
            "base_accumulators",
            tuple(
                BoundaryTransferAccumulator.from_packet(packet, dt_s=self.dt_s)
                for packet in ordered
            ),
        )

    @property
    def n_transfer(self) -> int:
        return len(self.base_accumulators)  # type: ignore[attr-defined]

    @property
    def occupation_shape(self) -> tuple[int, int]:
        return (self.network.n_state, self.grid.n_angle)

    @property
    def vector_size(self) -> int:
        return self.network.n_state * self.grid.n_angle + self.n_transfer

    def pack(self, log_occupation: np.ndarray, log_rho: np.ndarray) -> np.ndarray:
        log_f = np.asarray(log_occupation, dtype=float)
        log_rho = np.asarray(log_rho, dtype=float)
        if log_f.shape != self.occupation_shape:
            raise ValueError("log occupation shape mismatch")
        if log_rho.shape != (self.n_transfer,):
            raise ValueError("log transfer multiplier shape mismatch")
        if not np.all(np.isfinite(log_f)) or not np.all(np.isfinite(log_rho)):
            raise ValueError("log variables must be finite")
        return np.concatenate((log_f.ravel(), log_rho))

    def unpack(self, vector: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        values = np.asarray(vector, dtype=float)
        if values.shape != (self.vector_size,):
            raise ValueError("coupled vector size mismatch")
        split = self.network.n_state * self.grid.n_angle
        return values[:split].reshape(self.occupation_shape), values[split:]

    def unpack_residual(self, vector: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        return self.unpack(vector)

    def _base_increments(self) -> tuple[np.ndarray, ...]:
        adapter: FarBoundaryAdapter = self.adapter  # type: ignore[attr-defined]
        return tuple(
            adapter.occupation_increment(
                accumulator,
                n_H_m3=self.n_H_m3,
                angular_weights=self.grid.weights,
            )
            for accumulator in self.base_accumulators  # type: ignore[attr-defined]
        )

    def interface_increment(self, log_rho: np.ndarray) -> np.ndarray:
        log_rho = np.asarray(log_rho, dtype=float)
        if log_rho.shape != (self.n_transfer,):
            raise ValueError("log transfer multiplier shape mismatch")
        rho = np.exp(log_rho)
        increment = np.zeros(self.occupation_shape, dtype=float)
        for scale, base in zip(rho, self._base_increments()):
            increment += float(scale) * base
        return increment

    def interface_number_change_m3(self, log_rho: np.ndarray) -> float:
        log_rho = np.asarray(log_rho, dtype=float)
        if log_rho.shape != (self.n_transfer,):
            raise ValueError("log transfer multiplier shape mismatch")
        rho = np.exp(log_rho)
        total = 0.0
        for scale, accumulator in zip(
            rho, self.base_accumulators  # type: ignore[attr-defined]
        ):
            sign_com = -1.0 if accumulator.side is InterfaceSide.RED else 1.0
            total += (
                sign_com
                * self.n_H_m3
                * accumulator.number_per_H
                * float(scale)
            )
        return float(total)

    def _validated_old(self, old_occupation: np.ndarray) -> np.ndarray:
        old = np.asarray(old_occupation, dtype=float)
        if old.shape != self.occupation_shape:
            raise ValueError("old occupation shape mismatch")
        if np.any(old <= 0.0) or not np.all(np.isfinite(old)):
            raise ValueError("old occupation must be finite and strictly positive")
        return old

    def _occupation_scale(self, old_occupation: np.ndarray) -> np.ndarray:
        old = self._validated_old(old_occupation)
        interface_scale = np.zeros_like(old)
        for base in self._base_increments():
            interface_scale += np.abs(base)
        return np.maximum(np.maximum(np.abs(old), interface_scale), 1.0e-300)

    def unscaled_residual(
        self, vector: np.ndarray, old_occupation: np.ndarray
    ) -> np.ndarray:
        old = self._validated_old(old_occupation)
        log_f, log_rho = self.unpack(vector)
        if np.max(log_f) > 700.0 or np.min(log_f) < -745.0:
            raise FloatingPointError("log occupation is outside finite exponential range")
        if np.max(log_rho, initial=0.0) > 700.0 or np.min(log_rho, initial=0.0) < -745.0:
            raise FloatingPointError("log transfer multiplier is outside range")
        occupation = np.exp(log_f)
        rho = np.exp(log_rho)
        action = apply_nonlinear_bose_operator(
            occupation,
            mode_measure=self.network.mode_measure,
            equilibrium_weight=self.network.equilibrium_weight,
            pair_moments=self.network.pair_moments,
            same_cell_rates=self.network.same_cell_rates,
            grid=self.grid,
            photon_momentum_scale=self.network.momentum_scale,
        ).occupation_action
        residual_f = (
            occupation
            - old
            - self.dt_s * action
            - self.interface_increment(log_rho)
        )
        residual_rho = rho - 1.0
        return self.pack(residual_f, residual_rho)

    def scaled_residual(
        self, vector: np.ndarray, old_occupation: np.ndarray
    ) -> np.ndarray:
        raw_f, raw_rho = self.unpack_residual(
            self.unscaled_residual(vector, old_occupation)
        )
        return self.pack(raw_f / self._occupation_scale(old_occupation), raw_rho)

    def jvp(
        self,
        vector: np.ndarray,
        direction: np.ndarray,
        old_occupation: np.ndarray,
        *,
        scaled: bool = True,
    ) -> np.ndarray:
        self._validated_old(old_occupation)
        log_f, log_rho = self.unpack(vector)
        du, dv = self.unpack(direction)
        occupation = np.exp(log_f)
        rho = np.exp(log_rho)
        d_occupation = occupation * du
        action_jvp = apply_nonlinear_bose_jvp(
            occupation,
            d_occupation,
            mode_measure=self.network.mode_measure,
            equilibrium_weight=self.network.equilibrium_weight,
            pair_moments=self.network.pair_moments,
            same_cell_rates=self.network.same_cell_rates,
            grid=self.grid,
        ).occupation_action_jvp
        d_interface = np.zeros_like(occupation)
        for scale, scalar_direction, base in zip(
            rho, dv, self._base_increments()
        ):
            d_interface += float(scale * scalar_direction) * base
        result_f = d_occupation - self.dt_s * action_jvp - d_interface
        result_rho = rho * dv
        if scaled:
            result_f = result_f / self._occupation_scale(old_occupation)
        return self.pack(result_f, result_rho)


@dataclass(frozen=True)
class SideTransferLedger:
    """One side of the exact number/transported-energy exchange ledger."""

    side: InterfaceSide
    direction: ExchangeDirection
    native_number_change_per_H: float
    com_number_change_per_H: float
    native_energy_change_J_per_H: float
    com_energy_change_J_per_H: float
    atom_energy_change_J_per_H: float
    cell_centroid_energy_proxy_J_per_H: float
    unresolved_energy_correction_J_per_H: float

    @property
    def number_residual_per_H(self) -> float:
        return self.native_number_change_per_H + self.com_number_change_per_H

    @property
    def transported_energy_residual_J_per_H(self) -> float:
        return self.native_energy_change_J_per_H + self.com_energy_change_J_per_H

    def validate(self) -> None:
        if self.number_residual_per_H != 0.0:
            raise ValueError("side number ledger does not cancel exactly")
        if self.transported_energy_residual_J_per_H != 0.0:
            raise ValueError("side transported-energy ledger does not cancel exactly")
        if self.atom_energy_change_J_per_H != 0.0:
            raise ValueError("pure representation crossing has nonzero atom source")
        reconstructed = (
            self.cell_centroid_energy_proxy_J_per_H
            + self.unresolved_energy_correction_J_per_H
        )
        if not _close(reconstructed, self.com_energy_change_J_per_H):
            raise ValueError("cell proxy plus unresolved correction is inconsistent")


@dataclass(frozen=True)
class InterfaceTransferLedger:
    """Global exact exchange ledger for one coupled interface step."""

    n_H_m3: float
    sides: tuple[SideTransferLedger, ...]
    native_number_change_per_H: float
    com_number_change_per_H: float
    native_energy_change_J_per_H: float
    com_energy_change_J_per_H: float
    atom_energy_change_J_per_H: float

    @classmethod
    def from_accumulators(
        cls,
        adapter: FarBoundaryAdapter,
        accumulators: tuple[BoundaryTransferAccumulator, ...],
        *,
        n_H_m3: float,
    ) -> "InterfaceTransferLedger":
        if not isinstance(adapter, FarBoundaryAdapter):
            raise TypeError("adapter must be a FarBoundaryAdapter")
        if not math.isfinite(n_H_m3) or n_H_m3 <= 0.0:
            raise ValueError("n_H_m3 must be positive and finite")
        if len({accumulator.side for accumulator in accumulators}) != len(accumulators):
            raise ValueError("at most one accumulator per interface side is allowed")

        side_ledgers: list[SideTransferLedger] = []
        for accumulator in accumulators:
            if not isinstance(accumulator, BoundaryTransferAccumulator):
                raise TypeError("all accumulators must be BoundaryTransferAccumulator")
            cell = adapter.for_side(accumulator.side)
            sign_com = -1.0 if accumulator.side is InterfaceSide.RED else 1.0
            com_number = sign_com * accumulator.number_per_H
            native_number = -com_number
            com_energy = sign_com * accumulator.energy_J_per_H
            native_energy = -com_energy
            cell_proxy = (
                sign_com
                * h
                * cell.centroid_frequency_Hz
                * accumulator.number_per_H
            )
            correction = com_energy - cell_proxy
            row = SideTransferLedger(
                side=accumulator.side,
                direction=accumulator.direction,
                native_number_change_per_H=native_number,
                com_number_change_per_H=com_number,
                native_energy_change_J_per_H=native_energy,
                com_energy_change_J_per_H=com_energy,
                atom_energy_change_J_per_H=accumulator.atom_energy_J_per_H,
                cell_centroid_energy_proxy_J_per_H=cell_proxy,
                unresolved_energy_correction_J_per_H=correction,
            )
            row.validate()
            side_ledgers.append(row)

        result = cls(
            n_H_m3=float(n_H_m3),
            sides=tuple(side_ledgers),
            native_number_change_per_H=float(
                sum(row.native_number_change_per_H for row in side_ledgers)
            ),
            com_number_change_per_H=float(
                sum(row.com_number_change_per_H for row in side_ledgers)
            ),
            native_energy_change_J_per_H=float(
                sum(row.native_energy_change_J_per_H for row in side_ledgers)
            ),
            com_energy_change_J_per_H=float(
                sum(row.com_energy_change_J_per_H for row in side_ledgers)
            ),
            atom_energy_change_J_per_H=float(
                sum(row.atom_energy_change_J_per_H for row in side_ledgers)
            ),
        )
        result.validate()
        return result

    @property
    def number_residual_per_H(self) -> float:
        return self.native_number_change_per_H + self.com_number_change_per_H

    @property
    def transported_energy_residual_J_per_H(self) -> float:
        return self.native_energy_change_J_per_H + self.com_energy_change_J_per_H

    @property
    def number_residual_m3(self) -> float:
        return self.n_H_m3 * self.number_residual_per_H

    @property
    def transported_energy_residual_J_m3(self) -> float:
        return self.n_H_m3 * self.transported_energy_residual_J_per_H

    def validate(self) -> None:
        for row in self.sides:
            row.validate()
        if self.number_residual_per_H != 0.0:
            raise ValueError("global interface number ledger does not cancel exactly")
        if self.transported_energy_residual_J_per_H != 0.0:
            raise ValueError("global transported-energy ledger does not cancel exactly")
        if self.atom_energy_change_J_per_H != 0.0:
            raise ValueError("global interface atom source must be zero")


__all__ = [
    "FarBoundaryCell",
    "FarBoundaryAdapter",
    "BoundaryTransferAccumulator",
    "CoupledInterfaceProblem",
    "SideTransferLedger",
    "InterfaceTransferLedger",
]
