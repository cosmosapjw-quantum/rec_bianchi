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


__all__ = [
    "FarBoundaryCell",
    "FarBoundaryAdapter",
    "BoundaryTransferAccumulator",
]
