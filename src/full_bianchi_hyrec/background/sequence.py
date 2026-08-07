"""Source-locked interpolation of durable Bianchi ``BackgroundSnapshot`` data.

The v0.48 release stores chart-independent physical snapshot arrays on a
strictly increasing Hubble-time coordinate ``tau`` satisfying ``d tau/dt=H``.
For homogeneous backgrounds ``eta=ln(a)`` obeys the same differential relation,
so a short trajectory may identify ``eta`` and ``tau`` up to one explicitly
recorded additive anchor.  This module never exposes primitive chart state to
local microphysics.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import math
from pathlib import Path
from typing import Sequence

import numpy as np

from .branch_events import piecewise_linear_roots
from .characteristics import (
    doppler_coordinate_speed,
    hydrogen_frame_characteristic,
    normal_frame_characteristic,
)
from .snapshot import BackgroundSnapshot


_MODEL_META = {
    "Bianchi_II_large_shear": ("class_a", "II"),
    "Bianchi_VI_h_tilted_large_shear": ("class_b_tilted", "VI_h"),
    "Bianchi_VI_minus_1_over_9_exceptional": (
        "exceptional_VI",
        "VI_-1/9",
    ),
}


def _readonly(value: np.ndarray) -> np.ndarray:
    result = np.array(value, copy=True)
    result.setflags(write=False)
    return result


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


@dataclass(frozen=True)
class SourceDerivedBoundaryRoots:
    red: np.ndarray
    blue: np.ndarray
    red_by_direction: tuple[np.ndarray, ...]
    blue_by_direction: tuple[np.ndarray, ...]
    source_derived: bool
    source_sha256: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "red", _readonly(np.asarray(self.red, dtype=float)))
        object.__setattr__(self, "blue", _readonly(np.asarray(self.blue, dtype=float)))
        object.__setattr__(
            self,
            "red_by_direction",
            tuple(_readonly(np.asarray(item, dtype=float)) for item in self.red_by_direction),
        )
        object.__setattr__(
            self,
            "blue_by_direction",
            tuple(_readonly(np.asarray(item, dtype=float)) for item in self.blue_by_direction),
        )


@dataclass(frozen=True)
class BackgroundSnapshotSequence:
    model_name: str
    chart_id: str
    bianchi_type: str
    tau: np.ndarray
    cosmic_time_s: np.ndarray
    H_s_inv: np.ndarray
    q: np.ndarray
    sigma_s_inv: np.ndarray
    N_s_inv: np.ndarray
    A_s_inv: np.ndarray
    frame_rotation_s_inv: np.ndarray
    beta_H: np.ndarray
    D0_beta_H_s_inv: np.ndarray
    source_path: str
    source_sha256: str

    def __post_init__(self) -> None:
        tau = np.asarray(self.tau, dtype=float)
        if tau.ndim != 1 or tau.size < 2 or np.any(np.diff(tau) <= 0.0):
            raise ValueError("tau must be a strictly increasing one-dimensional grid")
        n = tau.size
        shapes = {
            "cosmic_time_s": (n,),
            "H_s_inv": (n,),
            "q": (n,),
            "sigma_s_inv": (n, 3, 3),
            "N_s_inv": (n, 3, 3),
            "A_s_inv": (n, 3),
            "frame_rotation_s_inv": (n, 3),
            "beta_H": (n, 3),
            "D0_beta_H_s_inv": (n, 3),
        }
        object.__setattr__(self, "tau", _readonly(tau))
        for name, shape in shapes.items():
            array = np.asarray(getattr(self, name), dtype=float)
            if array.shape != shape or not np.all(np.isfinite(array)):
                raise ValueError(f"{name} must have shape {shape} and finite values")
            object.__setattr__(self, name, _readonly(array))
        if np.any(self.H_s_inv <= 0.0):
            raise ValueError("all H values must be positive")
        if self.model_name not in _MODEL_META:
            raise ValueError("unsupported locked background model")

    @classmethod
    def from_npz(cls, path: str | Path, model_name: str) -> "BackgroundSnapshotSequence":
        source = Path(path)
        if not source.is_file():
            raise FileNotFoundError(source)
        try:
            chart_id, bianchi_type = _MODEL_META[str(model_name)]
        except KeyError as exc:
            raise ValueError("unknown locked background model") from exc
        prefix = str(model_name)
        with np.load(source, allow_pickle=False) as data:
            required = {
                name: data[f"{prefix}_{name}"]
                for name in (
                    "tau",
                    "cosmic_time_s",
                    "H_s_inv",
                    "q",
                    "sigma_s_inv",
                    "N_s_inv",
                    "A_s_inv",
                    "frame_rotation_s_inv",
                    "beta_H",
                    "D0_beta_H_s_inv",
                )
            }
        return cls(
            model_name=prefix,
            chart_id=chart_id,
            bianchi_type=bianchi_type,
            source_path=str(source.resolve()),
            source_sha256=_sha256(source),
            **required,
        )

    @property
    def tau_range(self) -> tuple[float, float]:
        return float(self.tau[0]), float(self.tau[-1])

    def _bracket(self, tau: float) -> tuple[int, int, float]:
        value = float(tau)
        if not math.isfinite(value) or value < self.tau[0] or value > self.tau[-1]:
            raise ValueError("tau lies outside the locked background sequence")
        right = int(np.searchsorted(self.tau, value, side="right"))
        if right == 0:
            return 0, 0, 0.0
        if right >= self.tau.size:
            last = self.tau.size - 1
            return last, last, 0.0
        left = right - 1
        if value == self.tau[left]:
            return left, left, 0.0
        fraction = (value - self.tau[left]) / (self.tau[right] - self.tau[left])
        return left, right, float(fraction)

    def _interpolate(self, name: str, left: int, right: int, fraction: float):
        array = np.asarray(getattr(self, name), dtype=float)
        if left == right:
            return np.array(array[left], copy=True)
        return (1.0 - fraction) * array[left] + fraction * array[right]

    def snapshot_at_tau(
        self, tau: float, *, H_s_inv_override: float | None = None
    ) -> BackgroundSnapshot:
        left, right, fraction = self._bracket(tau)
        source_H = float(self._interpolate("H_s_inv", left, right, fraction))
        target_H = source_H if H_s_inv_override is None else float(H_s_inv_override)
        if not math.isfinite(target_H) or target_H <= 0.0:
            raise ValueError("H_s_inv_override must be positive and finite")
        scale = target_H / source_H
        flags = {"interpolated": left != right}
        if H_s_inv_override is not None:
            flags["local_hubble_rescaled"] = True
        snapshot = BackgroundSnapshot(
            tau=float(tau),
            cosmic_time_s=float(self._interpolate("cosmic_time_s", left, right, fraction)) / scale,
            H_s_inv=target_H,
            q=float(self._interpolate("q", left, right, fraction)),
            sigma_s_inv=scale * self._interpolate("sigma_s_inv", left, right, fraction),
            N_s_inv=scale * self._interpolate("N_s_inv", left, right, fraction),
            A_s_inv=scale * self._interpolate("A_s_inv", left, right, fraction),
            frame_rotation_s_inv=scale * self._interpolate(
                "frame_rotation_s_inv", left, right, fraction
            ),
            beta_H=self._interpolate("beta_H", left, right, fraction),
            D0_beta_H_s_inv=scale * self._interpolate(
                "D0_beta_H_s_inv", left, right, fraction
            ),
            chart_id=self.chart_id,
            bianchi_type=self.bianchi_type,
            branch_flags=flags,
            constraint_residuals={"source_fraction": fraction},
        )
        return snapshot

    def snapshot_at_eta(
        self,
        eta: float,
        *,
        eta_anchor: float,
        tau_anchor: float,
    ) -> BackgroundSnapshot:
        return self.snapshot_at_tau(float(tau_anchor) + float(eta) - float(eta_anchor))

    def _sample_grid(self, start: float, end: float) -> np.ndarray:
        if not math.isfinite(start) or not math.isfinite(end) or end <= start:
            raise ValueError("boundary interval must satisfy finite start < end")
        if start < self.tau[0] or end > self.tau[-1]:
            raise ValueError("boundary interval lies outside source sequence")
        interior = self.tau[(self.tau > start) & (self.tau < end)]
        result = np.concatenate(([float(start)], interior, [float(end)]))
        return np.unique(result)

    def boundary_speed_roots(
        self,
        *,
        tau_start: float,
        tau_end: float,
        directions_normal: Sequence[Sequence[float]],
        line,
    ) -> SourceDerivedBoundaryRoots:
        directions = np.asarray(directions_normal, dtype=float)
        if directions.ndim != 2 or directions.shape[1] != 3:
            raise ValueError("directions_normal must have shape (n,3)")
        norms = np.linalg.norm(directions, axis=1)
        if np.any(norms == 0.0) or not np.all(np.isfinite(directions)):
            raise ValueError("directions_normal must be finite and nonzero")
        directions = directions / norms[:, None]
        times = self._sample_grid(float(tau_start), float(tau_end))
        red = np.empty((times.size, directions.shape[0]), dtype=float)
        blue = np.empty_like(red)
        for time_index, tau in enumerate(times):
            snapshot = self.snapshot_at_tau(float(tau))
            for angle_index, direction in enumerate(directions):
                normal = normal_frame_characteristic(snapshot, direction)
                hydrogen = hydrogen_frame_characteristic(snapshot, normal)
                red[time_index, angle_index] = float(
                    doppler_coordinate_speed(
                        hydrogen.R_hydrogen_s_inv,
                        line.x_red,
                        nu_abs_Hz=line.nu_abs_Hz,
                        Doppler_width_Hz=line.Doppler_width_Hz,
                    )
                )
                blue[time_index, angle_index] = float(
                    doppler_coordinate_speed(
                        hydrogen.R_hydrogen_s_inv,
                        line.x_blue,
                        nu_abs_Hz=line.nu_abs_Hz,
                        Doppler_width_Hz=line.Doppler_width_Hz,
                    )
                )
        red_by = tuple(piecewise_linear_roots(times, red[:, index]) for index in range(red.shape[1]))
        blue_by = tuple(piecewise_linear_roots(times, blue[:, index]) for index in range(blue.shape[1]))
        red_all = np.unique(np.concatenate(red_by)) if red_by and any(item.size for item in red_by) else np.empty(0)
        blue_all = np.unique(np.concatenate(blue_by)) if blue_by and any(item.size for item in blue_by) else np.empty(0)
        return SourceDerivedBoundaryRoots(
            red=red_all,
            blue=blue_all,
            red_by_direction=red_by,
            blue_by_direction=blue_by,
            source_derived=True,
            source_sha256=self.source_sha256,
        )


__all__ = ["BackgroundSnapshotSequence", "SourceDerivedBoundaryRoots"]
