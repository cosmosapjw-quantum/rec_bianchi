"""Bounded, causal q=0 HyRec2012 FULL hydrogen accepted-history experiment.

This is an *independent Python* source-physics trajectory. Each accepted
photon column is produced from already accepted earlier columns and the
original 2-real + 311-algebraic-virtual Schur collision operator. There is
no injected native HyRec x_e(z), photon output, or manufactured future sample.

Scope: hydrogen with neutral He, FLRW q=0, specified starting HII/Tm and
prehistory delta-f=0 at z_start, a first-order positive-control integrator.
The artificial spectral prehistory means this is NOT an accepted primordial
recombination x_e(z) solution or a substitute for native C FULL history.
"""
from __future__ import annotations

from dataclasses import dataclass
import math

import numpy as np

from full_bianchi_hyrec.trajectory.causal_virtual_redshift import (
    SOURCE_DLNA, causal_incoming_from_accepted_histories,
)
from full_bianchi_hyrec.trajectory.full_2012_atomic_source import (
    NVIRT, complete_original_full_atomic, populate_original_full_atomic,
    _canonical_twophoton_table,
)
from full_bianchi_hyrec.trajectory.hmla_flrw import (
    COMPTON_GAMMA_PER_T4_S_INV_K4, HMLAFlrwSource,
)


@dataclass(frozen=True)
class AcceptedFullHShortHistory:
    z: np.ndarray
    x_HII: np.ndarray
    Tm_K: np.ndarray
    dx_HII_dln_a: np.ndarray
    virtual_out: np.ndarray
    lyman_out: np.ndarray
    matrix_residual: np.ndarray
    initial_boundary: str = "ZERO_PREHISTORY_H_ONLY_FLRW_MANUFACTURED"
    source_mode: str = "CAUSAL_HYREC2012_FULL_FIRST_ORDER_SHORT_TRAJECTORY"

    def __post_init__(self):
        n = len(self.z)
        for name, shape in (
            ("z", (n,)), ("x_HII", (n,)), ("Tm_K", (n,)),
            ("dx_HII_dln_a", (n,)), ("virtual_out", (NVIRT, n)),
            ("lyman_out", (3, n)), ("matrix_residual", (n,)),
        ):
            arr = np.asarray(getattr(self, name), dtype=np.float64)
            if arr.shape != shape or not np.all(np.isfinite(arr)):
                raise ValueError(f"invalid accepted history {name}")
            readonly = np.array(arr, copy=True)
            readonly.setflags(write=False)
            object.__setattr__(self, name, readonly)
        if (np.any(np.diff(self.z) >= 0) or np.any(self.x_HII <= 0)
                or np.any(self.x_HII >= 1) or np.any(self.Tm_K <= 0)):
            raise ValueError("nonphysical accepted H-only history")


def _implicit_thermal_step(source: HMLAFlrwSource, z: float,
                           x_HII: float, Tm_K: float, deta: float) -> float:
    """Backward Euler for a linear Compton plus adiabatic cooling operator.

    At a fixed endpoint state: dTm/deta = -(2+G/H) Tm + (G/H) Tr.
    Implicit treatment is positivity preserving for any positive step.
    """
    H, _ = source.cosmology(z)
    Tr = source.tcmb0_K * (1. + z)
    rate = (COMPTON_GAMMA_PER_T4_S_INV_K4 * Tr**4 * x_HII
            / (1. + x_HII + source.f_he) / H)
    result = (Tm_K + deta * rate * Tr) / (1. + deta * (2. + rate))
    if not (math.isfinite(result) and 0 < result <= Tr * (1. + 1.e-10)):
        raise FloatingPointError("gas temperature outside H-only branch")
    return result


def integrate_full_h_short_history(
    source: HMLAFlrwSource, *, z_start: float, x_HII_start: float,
    Tm_start_K: float, steps: int, dlna: float = SOURCE_DLNA,
) -> AcceptedFullHShortHistory:
    """Advance a short predeclared q=0 experiment using causal accepted bins.

    Exactly n=steps source snapshots and n accepted photon columns, never
    an ODE evolving 311 virtual levels. Original q=0 HyRec Fplus is used
    after two columns. For samples 0 and 1 the strict source-grid delay
    lies before the zero-distortion prehistory boundary.
    """
    if not (isinstance(steps, int) and 3 <= steps <= 2048):
        raise ValueError("bounded source-grid experiment requires 3..2048 steps")
    if not (math.isfinite(dlna) and 0 < dlna <= SOURCE_DLNA):
        raise ValueError("invalid source physical step")
    if not (math.isfinite(z_start) and 500 <= z_start <= 1600):
        raise ValueError("outside specified H-only source experiment epoch")
    if not (math.isfinite(x_HII_start) and 0 < x_HII_start < 1
            and math.isfinite(Tm_start_K) and 0 < Tm_start_K
            <= source.tcmb0_K * (1. + z_start)):
        raise ValueError("invalid declared starting thermodynamic slice")
    eta0 = -math.log1p(z_start)
    eta = eta0 + dlna * np.arange(steps)
    zz = np.expm1(-eta)
    zz[0] = z_start  # Preserve the exact independently supplied first source row.
    if zz[-1] < 500:
        raise ValueError("experiment extends beyond the declared H-only interval")
    table = _canonical_twophoton_table(source.table.archive_path)
    # Fortran columns are contiguous and immutable only when returned.
    virtual = np.empty((NVIRT, steps), dtype=np.float64, order="F")
    lyman = np.empty((3, steps), dtype=np.float64, order="F")
    x = np.empty(steps, dtype=np.float64)
    temperature = np.empty(steps, dtype=np.float64)
    rhs = np.empty(steps, dtype=np.float64)
    residual = np.empty(steps, dtype=np.float64)
    x[0] = x_HII_start
    temperature[0] = Tm_start_K
    for i in range(steps):
        if i < 2:
            incoming_virtual = np.zeros(NVIRT, dtype=np.float64)
            incoming_lyman = np.zeros(2, dtype=np.float64)
        else:
            # Direct accepted-history views; never concat or copy all history.
            incoming = causal_incoming_from_accepted_histories(
                energies_eV=table.energy_eV,
                virtual_history=virtual[:, :i],
                lyman_history=lyman[:, :i],
                z_start=z_start, iz=i, z_face=float(zz[i]),
                dlna=dlna, shear_q=0.,
            )
            incoming_virtual = incoming.virtual_distortion[0]
            incoming_lyman = incoming.lya_lyb_incoming_distortion[0]
        snapshot = populate_original_full_atomic(
            source, z=float(zz[i]), xHII=float(x[i]), xe=float(x[i]),
            Tm_K=float(temperature[i]),
            incoming_virtual=incoming_virtual,
            incoming_lyman=incoming_lyman,
        )
        result = complete_original_full_atomic(snapshot)
        virtual[:, i] = result.outgoing_virtual
        lyman[:, i] = result.outgoing_lyman
        rhs[i] = result.dxHII_dln_a
        residual[i] = result.normalized_matrix_residual
        if residual[i] > 2.e-10:
            raise FloatingPointError(f"atomic Schur residual at step {i}")
        if i < steps-1:
            next_x = x[i] + dlna * rhs[i]
            if not (math.isfinite(next_x) and 0 < next_x < 1):
                raise FloatingPointError(
                    f"explicit H chemistry violates admissibility at step {i}"
                )
            x[i+1] = next_x
            temperature[i+1] = _implicit_thermal_step(
                source, float(zz[i+1]), float(next_x),
                float(temperature[i]), dlna,
            )
    return AcceptedFullHShortHistory(
        z=zz, x_HII=x, Tm_K=temperature, dx_HII_dln_a=rhs,
        virtual_out=virtual, lyman_out=lyman, matrix_residual=residual,
    )
