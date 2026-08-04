import numpy as np
import pytest

from full_bianchi_hyrec.background.snapshot import BackgroundSnapshot
from full_bianchi_hyrec.background.adapters import (
    class_a_snapshot,
    exceptional_snapshot,
    tilted_class_b_snapshot,
)

SQRT3 = np.sqrt(3.0)


def test_snapshot_rejects_non_tracefree_shear_and_superluminal_tilt():
    with pytest.raises(ValueError, match="trace-free"):
        BackgroundSnapshot(
            tau=0.0,
            cosmic_time_s=0.0,
            H_s_inv=1.0,
            q=0.5,
            sigma_s_inv=np.eye(3),
            N_s_inv=np.zeros((3, 3)),
            A_s_inv=np.zeros(3),
            frame_rotation_s_inv=np.zeros(3),
            beta_H=np.zeros(3),
            D0_beta_H_s_inv=np.zeros(3),
            chart_id="test",
            bianchi_type="I",
        )

    with pytest.raises(ValueError, match=r"\|beta_H\|"):
        BackgroundSnapshot(
            tau=0.0,
            cosmic_time_s=0.0,
            H_s_inv=1.0,
            q=0.5,
            sigma_s_inv=np.zeros((3, 3)),
            N_s_inv=np.zeros((3, 3)),
            A_s_inv=np.zeros(3),
            frame_rotation_s_inv=np.zeros(3),
            beta_H=np.array([1.0, 0.0, 0.0]),
            D0_beta_H_s_inv=np.zeros(3),
            chart_id="test",
            bianchi_type="I",
        )


def test_class_a_adapter_matches_we_matrix_dictionary():
    H = 2.0
    state = np.array([0.2, -0.1, 1.0, 0.0, 0.0])
    snapshot = class_a_snapshot(
        state,
        q=0.7,
        H_s_inv=H,
        tau=0.3,
        cosmic_time_s=4.0,
        bianchi_type="II",
    )

    expected_sigma_norm = np.diag(
        [-0.4, 0.2 - 0.1 * SQRT3, 0.2 + 0.1 * SQRT3]
    )
    assert np.allclose(snapshot.sigma_s_inv, H * expected_sigma_norm)
    assert np.allclose(snapshot.N_s_inv, H * np.diag([1.0, 0.0, 0.0]))
    assert np.allclose(snapshot.A_s_inv, 0.0)
    assert np.allclose(snapshot.frame_rotation_s_inv, 0.0)
    assert snapshot.bianchi_type == "II"


def test_tilted_class_b_adapter_preserves_hervik_gauge_and_tilt_derivative():
    H = 3.0
    state = np.array(
        [0.08, 0.05, 0.11, -0.07, 0.04, 0.35, 0.25, 0.28,
         0.12, 0.06, -0.09]
    )
    rhs = np.linspace(-0.05, 0.05, 11)
    snapshot = tilted_class_b_snapshot(
        state,
        rhs,
        q=0.91,
        H_s_inv=H,
        tau=0.2,
        cosmic_time_s=5.0,
        bianchi_type="VII_h",
        constraint_residuals={"C2": 1e-15},
    )

    Sp, Sm, S12, S13, S23, N, lam, A = state[:8]
    expected_sigma = np.array(
        [
            [-2 * Sp, SQRT3 * S12, SQRT3 * S13],
            [SQRT3 * S12, Sp + SQRT3 * Sm, SQRT3 * S23],
            [SQRT3 * S13, SQRT3 * S23, Sp - SQRT3 * Sm],
        ]
    )
    expected_N = np.array(
        [
            [0.0, 0.0, 0.0],
            [0.0, SQRT3 * lam * N, SQRT3 * N],
            [0.0, SQRT3 * N, SQRT3 * lam * N],
        ]
    )
    expected_R = np.array(
        [SQRT3 * Sm * lam, -SQRT3 * S13, SQRT3 * S12]
    )

    assert np.allclose(snapshot.sigma_s_inv, H * expected_sigma)
    assert np.allclose(snapshot.N_s_inv, H * expected_N)
    assert np.allclose(snapshot.A_s_inv, H * np.array([A, 0.0, 0.0]))
    assert np.allclose(snapshot.frame_rotation_s_inv, H * expected_R)
    assert np.allclose(snapshot.beta_H, state[8:11])
    assert np.allclose(snapshot.D0_beta_H_s_inv, H * rhs[8:11])
    assert snapshot.constraint_residuals["C2"] == 1e-15


def test_exceptional_adapter_matches_hhw_lift_and_gauge_rotation():
    H = 4.0
    state = np.array([0.12, -0.04, 0.07, 0.03, 0.31, 0.09])
    snapshot = exceptional_snapshot(
        state,
        q=0.8,
        H_s_inv=H,
        tau=0.4,
        cosmic_time_s=6.0,
    )

    Sp, Sm, S2, Sx, Nm, A = state
    expected_sigma = np.array(
        [
            [-2 * Sp, 0.0, SQRT3 * S2],
            [0.0, Sp + SQRT3 * Sm, SQRT3 * Sx],
            [SQRT3 * S2, SQRT3 * Sx, Sp - SQRT3 * Sm],
        ]
    )
    expected_N = np.array(
        [
            [0.0, 0.0, 0.0],
            [0.0, 2.0 * SQRT3 * Nm, 3.0 * A],
            [0.0, 3.0 * A, 0.0],
        ]
    )
    expected_R = np.array([-SQRT3 * Sx, -SQRT3 * S2, 0.0])

    assert np.allclose(snapshot.sigma_s_inv, H * expected_sigma)
    assert np.allclose(snapshot.N_s_inv, H * expected_N)
    assert np.allclose(snapshot.A_s_inv, H * np.array([A, 0.0, 0.0]))
    assert np.allclose(snapshot.frame_rotation_s_inv, H * expected_R)
    assert snapshot.bianchi_type == "VI_-1/9"
