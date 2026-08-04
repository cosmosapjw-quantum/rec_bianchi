"""Adapters from the supplied primitive Bianchi chart dictionaries.

Input arrays are Hubble-normalized chart states.  A positive physical H
converts Sigma, N, A and frame rotation to s^-1.  For a chart time
variable satisfying d/dt = H d/dtau, a tilted chart derivative v' gives
D0 beta_H = H v'.
"""
from __future__ import annotations

from typing import Mapping

import numpy as np

from .snapshot import BackgroundSnapshot

_SQRT3 = np.sqrt(3.0)


def _base_kwargs(
    *,
    q,
    H_s_inv,
    tau,
    cosmic_time_s,
    chart_id,
    bianchi_type,
    beta_H,
    D0_beta_H_s_inv,
    branch_flags,
    constraint_residuals,
):
    return dict(
        tau=float(tau),
        cosmic_time_s=float(cosmic_time_s),
        H_s_inv=float(H_s_inv),
        q=float(q),
        chart_id=str(chart_id),
        bianchi_type=str(bianchi_type),
        beta_H=np.asarray(beta_H, dtype=float),
        D0_beta_H_s_inv=np.asarray(D0_beta_H_s_inv, dtype=float),
        branch_flags={} if branch_flags is None else branch_flags,
        constraint_residuals=(
            {} if constraint_residuals is None else constraint_residuals
        ),
    )


def class_a_snapshot(
    state,
    *,
    q,
    H_s_inv,
    tau,
    cosmic_time_s,
    bianchi_type,
    beta_H=np.zeros(3),
    D0_beta_H_s_inv=np.zeros(3),
    branch_flags: Mapping[str, bool] | None = None,
    constraint_residuals: Mapping[str, float] | None = None,
):
    values = np.asarray(state, dtype=float)
    if values.shape != (5,):
        raise ValueError("class-A state must have shape (5,)")
    Sp, Sm, N1, N2, N3 = values
    sigma_norm = np.diag(
        [-2.0 * Sp, Sp + _SQRT3 * Sm, Sp - _SQRT3 * Sm]
    )
    N_norm = np.diag([N1, N2, N3])
    H = float(H_s_inv)
    return BackgroundSnapshot(
        sigma_s_inv=H * sigma_norm,
        N_s_inv=H * N_norm,
        A_s_inv=np.zeros(3),
        frame_rotation_s_inv=np.zeros(3),
        **_base_kwargs(
            q=q,
            H_s_inv=H,
            tau=tau,
            cosmic_time_s=cosmic_time_s,
            chart_id="class_a",
            bianchi_type=bianchi_type,
            beta_H=beta_H,
            D0_beta_H_s_inv=D0_beta_H_s_inv,
            branch_flags=branch_flags,
            constraint_residuals=constraint_residuals,
        ),
    )


def tilted_class_b_snapshot(
    state,
    state_rhs_tau,
    *,
    q,
    H_s_inv,
    tau,
    cosmic_time_s,
    bianchi_type,
    branch_flags: Mapping[str, bool] | None = None,
    constraint_residuals: Mapping[str, float] | None = None,
):
    values = np.asarray(state, dtype=float)
    derivatives = np.asarray(state_rhs_tau, dtype=float)
    if values.shape != (11,) or derivatives.shape != (11,):
        raise ValueError("tilted class-B state and derivative must have shape (11,)")

    Sp, Sm, S12, S13, S23, N, lam, A = values[:8]
    sigma_norm = np.array(
        [
            [-2.0 * Sp, _SQRT3 * S12, _SQRT3 * S13],
            [_SQRT3 * S12, Sp + _SQRT3 * Sm, _SQRT3 * S23],
            [_SQRT3 * S13, _SQRT3 * S23, Sp - _SQRT3 * Sm],
        ]
    )
    N_norm = np.array(
        [
            [0.0, 0.0, 0.0],
            [0.0, _SQRT3 * lam * N, _SQRT3 * N],
            [0.0, _SQRT3 * N, _SQRT3 * lam * N],
        ]
    )
    A_norm = np.array([A, 0.0, 0.0])
    # COMMUTATOR convention in the supplied primitive chart.
    R_norm = np.array(
        [_SQRT3 * Sm * lam, -_SQRT3 * S13, _SQRT3 * S12]
    )
    H = float(H_s_inv)
    return BackgroundSnapshot(
        sigma_s_inv=H * sigma_norm,
        N_s_inv=H * N_norm,
        A_s_inv=H * A_norm,
        frame_rotation_s_inv=H * R_norm,
        **_base_kwargs(
            q=q,
            H_s_inv=H,
            tau=tau,
            cosmic_time_s=cosmic_time_s,
            chart_id="class_b_tilted",
            bianchi_type=bianchi_type,
            beta_H=values[8:11],
            D0_beta_H_s_inv=H * derivatives[8:11],
            branch_flags=branch_flags,
            constraint_residuals=constraint_residuals,
        ),
    )


def exceptional_snapshot(
    state,
    *,
    q,
    H_s_inv,
    tau,
    cosmic_time_s,
    beta_H=np.zeros(3),
    D0_beta_H_s_inv=np.zeros(3),
    branch_flags: Mapping[str, bool] | None = None,
    constraint_residuals: Mapping[str, float] | None = None,
):
    values = np.asarray(state, dtype=float)
    if values.shape != (6,):
        raise ValueError("exceptional state must have shape (6,)")
    Sp, Sm, S2, Sx, Nm, A = values
    # HHW gauge recovered by closing the primitive exceptional RHS on the
    # general orthonormal-frame chart:
    # Sigma_13=Sigma_2, Sigma_23=Sigma_x, Sigma_12=0;
    # n22=2 sqrt(3) N_-, n23=3 A, n33=0.
    sigma_norm = np.array(
        [
            [-2.0 * Sp, 0.0, _SQRT3 * S2],
            [0.0, Sp + _SQRT3 * Sm, _SQRT3 * Sx],
            [_SQRT3 * S2, _SQRT3 * Sx, Sp - _SQRT3 * Sm],
        ]
    )
    N_norm = np.array(
        [
            [0.0, 0.0, 0.0],
            [0.0, 2.0 * _SQRT3 * Nm, 3.0 * A],
            [0.0, 3.0 * A, 0.0],
        ]
    )
    A_norm = np.array([A, 0.0, 0.0])
    R_norm = np.array([-_SQRT3 * Sx, -_SQRT3 * S2, 0.0])
    H = float(H_s_inv)
    return BackgroundSnapshot(
        sigma_s_inv=H * sigma_norm,
        N_s_inv=H * N_norm,
        A_s_inv=H * A_norm,
        frame_rotation_s_inv=H * R_norm,
        **_base_kwargs(
            q=q,
            H_s_inv=H,
            tau=tau,
            cosmic_time_s=cosmic_time_s,
            chart_id="exceptional_VI",
            bianchi_type="VI_-1/9",
            beta_H=beta_H,
            D0_beta_H_s_inv=D0_beta_H_s_inv,
            branch_flags=branch_flags,
            constraint_residuals=constraint_residuals,
        ),
    )
