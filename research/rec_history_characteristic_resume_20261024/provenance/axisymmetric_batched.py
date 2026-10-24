"""Vectorized exact-Killing-ray formal transfer for a prescribed LRS Bianchi I.

This is an explicitly opt-in independent reference/fast CPU path. It reuses
the C8 finite positive logarithmic clock on one common time grid and advances
many normal-comoving photon rays by the *exact* conserved k_i map. It does
NOT solve the coupled Einstein--HyRec system, change any historical solver
checkpoint, or silently replace the generic tilted-Bianchi characteristic.
"""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
import math
from types import MappingProxyType
from typing import Callable

import numpy as np

from full_bianchi_hyrec.background.axisymmetric_bianchi_i import (
    AxisymmetricBianchiIBackground,
)
from full_bianchi_hyrec.background.sequence import BackgroundSnapshotSequence
from .characteristic_angular import CharacteristicAngularSolver

_BI_EXACT_BATCH = "rec_lrs_bi_exact_Ki_batch_source_log_clock_v1"


@dataclass(frozen=True)
class BatchIsotropicCoefficients:
    """Pure callable source j(tau, nu[]) and opacity chi(tau, nu[]) in s^-1.

    Callbacks accept a vector of ordinary frequencies (Hz) and return a
    nonnegative scalar or shape-(nrays,) NumPy-compatible array. Parallel
    execution is permitted *only* if thread_safe=True is explicitly asserted.
    That assertion is a caller contract, not automatically certified.
    """

    emissivity_s_inv: Callable[[float, np.ndarray], object]
    opacity_s_inv: Callable[[float, np.ndarray], object]
    thread_safe: bool = False

    @classmethod
    def zero(cls) -> "BatchIsotropicCoefficients":
        return cls(lambda _tau, _nu: 0., lambda _tau, _nu: 0.)


@dataclass(frozen=True)
class AxisymmetricBatchFaceResult:
    """Numerical result for one independent batch of normal-frame rays."""

    occupation_face: np.ndarray
    initial_frequency_Hz: np.ndarray
    initial_direction_normal: np.ndarray
    face_direction_normal: np.ndarray
    face_frequency_Hz: np.ndarray
    n_step: int
    n_rays: int
    method_identity: str = _BI_EXACT_BATCH

    def __post_init__(self):
        for name in (
            "occupation_face", "initial_frequency_Hz",
            "initial_direction_normal", "face_direction_normal",
            "face_frequency_Hz",
        ):
            array = np.array(getattr(self, name), dtype=float, copy=True)
            if not np.all(np.isfinite(array)):
                raise ValueError("nonfinite batched ray output")
            array.setflags(write=False)
            object.__setattr__(self, name, array)


def _broadcast_positive(value, size: int, label: str, *, allow_zero: bool):
    array = np.asarray(value, dtype=float)
    if array.ndim == 0:
        array = np.full(size, float(array), dtype=float)
    elif array.shape == (size,):
        array = np.array(array, dtype=float, copy=True)
    else:
        raise ValueError(f"{label} must be scalar or array of shape ({size},)")
    if not np.all(np.isfinite(array)):
        raise ValueError(f"{label} contains nonfinite values")
    if np.any(array < 0 if allow_zero else array <= 0):
        raise ValueError(f"{label} must be {'nonnegative' if allow_zero else 'positive'}")
    return array


class AxisymmetricBianchiIBatchSolver:
    """Exact Bianchi-I null map + positive step-exponential scalar transfer.

    Construct once for a frozen, source-matched BackgroundSnapshotSequence.
    The constructor reuses the C7 numerical payload audit via the existing
    CharacteristicAngularSolver; only ray propagation is specialized.
    """

    def __init__(
        self, sequence: BackgroundSnapshotSequence,
        source: AxisymmetricBianchiIBackground,
    ):
        if not isinstance(source, AxisymmetricBianchiIBackground):
            raise TypeError("source must be an AxisymmetricBianchiIBackground")
        # Reuse strict source/method identity and every-node physical check.
        CharacteristicAngularSolver(sequence, interval_source=source)
        self.sequence = sequence
        self.source = source
        # Up to four O(n_step)-sized numerical grids, never one array per ray.
        # Cache only the frozen geometry; coefficient callbacks remain mutable
        # inputs and are always evaluated on each fresh transfer call.
        self._geometry_cache = {}

    @property
    def cached_geometry_count(self) -> int:
        return len(self._geometry_cache)

    def _prepare_geometry(self, start: float, end: float, n_step: int):
        """One geometry clock calculation shared by all rays and chunks."""
        if not all(math.isfinite(t) for t in (start, end)) or not start < end:
            raise ValueError("require finite strictly increasing log-time endpoints")
        if start < float(self.sequence.tau[0]) or end > float(self.sequence.tau[-1]):
            raise ValueError("time interval outside source-identified snapshots")
        if isinstance(n_step, bool) or not isinstance(n_step, int) or n_step < 2:
            raise ValueError("n_step must be integer >= 2")
        key = (start, end, n_step)
        cached = self._geometry_cache.get(key)
        if cached is not None:
            return cached

        nodes = np.linspace(start, end, n_step + 1)
        if np.any(np.diff(nodes) <= 0):
            raise ValueError("requested represented time grid contains collapsed substeps")
        anchor = float(self.sequence.tau[0])
        local = nodes - anchor
        if np.any(np.diff(local) <= 0):
            raise ValueError("source log-time conversion collapsed an interval")
        widths = []
        b_steps = []
        mid_face_b = []
        # Reverse running physical shear from the face, making the exact
        # Killing momentum redshift at each source midpoint accessible without
        # subtracting large cumulative shear values.
        for i in range(n_step):
            full = self.source.interval_log(float(local[i]), float(local[i+1]))
            widths.append(full.delta_t_s)
            b_steps.append(full.delta_b)
        suffix_b = np.empty(n_step + 1, dtype=float)
        suffix_b[-1] = 0.
        for i in range(n_step-1, -1, -1):
            suffix_b[i] = suffix_b[i+1]+b_steps[i]
        middles = 0.5*(nodes[:-1]+nodes[1:])
        midlocal = middles-anchor
        if np.any(midlocal <= local[:-1]) or np.any(midlocal >= local[1:]):
            raise ValueError("representable middle source event collapsed")
        for i in range(n_step):
            trailing = self.source.interval_log(
                float(midlocal[i]), float(local[i+1])
            )
            mid_face_b.append(-(suffix_b[i+1]+trailing.delta_b))
        geo = {
            "dt": np.asarray(widths, dtype=float),
            "middle_tau": middles,
            "middle_log": midlocal,
            "middle_b_face": np.asarray(mid_face_b, dtype=float),
            "start_b_face": -float(math.fsum(b_steps)),
            "start_log_face": float(local[0]-local[-1]),
            "middle_log_face": midlocal-float(local[-1]),
        }
        # Cached data are immutable: worker threads and subsequent callbacks
        # can never change another ray's physical clock source.
        for array in geo.values():
            if isinstance(array, np.ndarray):
                array.setflags(write=False)
        if len(self._geometry_cache) >= 4:
            del self._geometry_cache[next(iter(self._geometry_cache))]
        # Freeze the dictionary as well: numerical object identities never
        # depend on callback mutation or a later method call.
        result = MappingProxyType(geo)
        self._geometry_cache[key] = result
        return result

    @staticmethod
    def _chunk(
        face_normal: np.ndarray,
        face_nu: np.ndarray,
        f0: np.ndarray,
        coeff: BatchIsotropicCoefficients,
        geometry: dict,
    ):
        """All rays in one chunk, with O(nrays) scratch and no history matrix."""
        zmu = face_normal[:, 2]
        perpendicular2 = np.sum(face_normal[:, :2]**2, axis=1)
        axial2 = zmu*zmu
        occupation = np.array(f0, dtype=float, copy=True)
        n = len(occupation)

        for i, tau_mid in enumerate(geometry["middle_tau"]):
            db = float(geometry["middle_b_face"][i])
            fac_perp = math.exp(db)
            fac_ax = math.exp(-2.*db)
            R = np.sqrt(fac_perp*fac_perp*perpendicular2 + fac_ax*fac_ax*axial2)
            frequency = face_nu * math.exp(
                -float(geometry["middle_log_face"][i])
            ) * R
            if not np.all(np.isfinite(frequency)) or np.any(frequency <= 0):
                raise ValueError("nonfinite normal-frame midpoint photon frequency")
            emission = _broadcast_positive(
                coeff.emissivity_s_inv(float(tau_mid), frequency),
                n, "emissivity_s_inv", allow_zero=True,
            )
            opacity = _broadcast_positive(
                coeff.opacity_s_inv(float(tau_mid), frequency),
                n, "opacity_s_inv", allow_zero=True,
            )
            dt = float(geometry["dt"][i])
            # This is the exact positive frozen-coefficient solution.
            # np.expm1 prevents cancellation at small optical depth; at
            # chi==0 the source factor is exactly dt, not 0/0.
            optical = opacity*dt
            atten = np.exp(-optical)
            absorbed = -np.expm1(-optical)
            factor = np.full(n, dt, dtype=float)
            np.divide(absorbed, opacity, out=factor, where=opacity > 0.)
            occupation = atten*occupation + emission*factor
            if not np.all(np.isfinite(occupation)) or np.any(occupation < 0.):
                raise FloatingPointError("nonfinite or negative source-evolved occupation")

        db_total = float(geometry["start_b_face"])
        per = math.exp(db_total)
        ax = math.exp(-2.*db_total)
        R0 = np.sqrt(per*per*perpendicular2+ax*ax*axial2)
        initial_freq = face_nu*math.exp(
            -float(geometry["start_log_face"])
        )*R0
        initial_n = np.array(face_normal, copy=True)
        initial_n[:, :2] *= per/R0[:,None]
        initial_n[:, 2] *= ax/R0
        return occupation, initial_freq, initial_n

    def trace_many_to_face(
        self,
        *,
        tau_start: float,
        tau_end: float,
        face_directions,
        face_frequency_Hz,
        initial_occupation,
        coefficients: BatchIsotropicCoefficients,
        n_step: int = 128,
        chunk_size: int = 1024,
        workers: int = 1,
    ) -> AxisymmetricBatchFaceResult:
        if not isinstance(coefficients, BatchIsotropicCoefficients):
            raise TypeError("coefficients require BatchIsotropicCoefficients")
        if isinstance(workers, bool) or not isinstance(workers, int) or workers < 1 or workers > 32:
            raise ValueError("workers must be an integer in [1,32]")
        if isinstance(chunk_size, bool) or not isinstance(chunk_size, int) or chunk_size < 1:
            raise ValueError("chunk_size must be positive integer")
        if workers > 1 and not coefficients.thread_safe:
            raise ValueError("parallel workers require explicitly pure thread_safe callbacks")

        face = np.asarray(face_directions, dtype=float)
        if face.ndim != 2 or face.shape[1] != 3 or face.shape[0] < 1:
            raise ValueError("face_directions requires a nonempty (nrays,3) matrix")
        if not np.all(np.isfinite(face)):
            raise ValueError("nonfinite normal ray directions")
        norm = np.linalg.norm(face, axis=1)
        if np.any(~np.isfinite(norm)) or np.any(norm <= 0):
            raise ValueError("zero or unnormalizable normal ray")
        unit = face/norm[:,None]
        count = len(unit)
        nu = _broadcast_positive(face_frequency_Hz, count, "face_frequency_Hz", allow_zero=False)
        f0 = _broadcast_positive(initial_occupation, count, "initial_occupation", allow_zero=True)
        geo = self._prepare_geometry(float(tau_start), float(tau_end), n_step)
        sections = [
            slice(i, min(i + chunk_size, count))
            for i in range(0,count,chunk_size)
        ]

        def evaluate(slc):
            return self._chunk(unit[slc], nu[slc], f0[slc], coefficients, geo)

        if workers == 1 or len(sections) == 1:
            partial = [evaluate(slc) for slc in sections]
        else:
            # Read-only NumPy arrays, deterministic ordered collection. Useful
            # only for sufficiently large ray chunks and thread-safe callbacks.
            with ThreadPoolExecutor(max_workers=workers) as pool:
                partial = list(pool.map(evaluate, sections))
        return AxisymmetricBatchFaceResult(
            occupation_face=np.concatenate([p[0] for p in partial]),
            initial_frequency_Hz=np.concatenate([p[1] for p in partial]),
            initial_direction_normal=np.vstack([p[2] for p in partial]),
            face_direction_normal=unit,
            face_frequency_Hz=nu,
            n_step=n_step,
            n_rays=count,
        )


__all__=[
    "AxisymmetricBianchiIBatchSolver",
    "AxisymmetricBatchFaceResult",
    "BatchIsotropicCoefficients",
]
