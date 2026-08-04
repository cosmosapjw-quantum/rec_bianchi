import numpy as np

from full_bianchi_hyrec.background.characteristics import (
    aberrate_direction,
    hydrogen_frame_characteristic,
    normal_frame_characteristic,
)
from full_bianchi_hyrec.background.snapshot import BackgroundSnapshot


def _snapshot():
    return BackgroundSnapshot(
        tau=0.0,
        cosmic_time_s=0.0,
        H_s_inv=0.8,
        q=0.7,
        sigma_s_inv=np.array(
            [[-1.2, 0.1, -0.05], [0.1, 0.7, 0.2], [-0.05, 0.2, 0.5]]
        ),
        N_s_inv=np.array(
            [[0.0, 0.0, 0.0], [0.0, 0.4, -0.2], [0.0, -0.2, 0.1]]
        ),
        A_s_inv=np.array([0.16, 0.0, 0.0]),
        frame_rotation_s_inv=np.array([0.07, -0.03, 0.04]),
        beta_H=np.array([0.24, -0.11, 0.08]),
        D0_beta_H_s_inv=np.array([0.03, 0.02, -0.01]),
        chart_id="synthetic",
        bianchi_type="VII_h",
    )


def _five_point_derivative(function, step=2e-5):
    return (
        function(-2 * step)
        - 8.0 * function(-step)
        + 8.0 * function(step)
        - function(2 * step)
    ) / (12.0 * step)


def test_normal_characteristic_preserves_direction_norm_and_frequency_sign():
    snapshot = _snapshot()
    n = np.array([0.3, -0.4, 0.8])
    n /= np.linalg.norm(n)

    characteristic = normal_frame_characteristic(snapshot, n)

    expected_R = -(
        snapshot.H_s_inv + n @ snapshot.sigma_s_inv @ n
    )
    assert abs(characteristic.R_normal_s_inv - expected_R) < 1e-14
    assert abs(n @ characteristic.D0_direction_normal_s_inv) < 2e-15


def test_hydrogen_frame_frequency_and_direction_derivatives_match_direct_boost():
    snapshot = _snapshot()
    n = np.array([0.3, -0.4, 0.8])
    n /= np.linalg.norm(n)
    normal = normal_frame_characteristic(snapshot, n)
    hydrogen = hydrogen_frame_characteristic(snapshot, normal)

    beta0 = snapshot.beta_H
    dbeta = snapshot.D0_beta_H_s_inv
    dn = normal.D0_direction_normal_s_inv
    Rn = normal.R_normal_s_inv

    direct_n = _five_point_derivative(
        lambda dt: aberrate_direction(
            beta0 + dt * dbeta,
            (n + dt * dn) / np.linalg.norm(n + dt * dn),
        )
    )
    direct_log_nu = _five_point_derivative(
        lambda dt: (
            Rn * dt
            + np.log(
                hydrogen_frame_characteristic.doppler_factor(
                    beta0 + dt * dbeta,
                    (n + dt * dn) / np.linalg.norm(n + dt * dn),
                )
            )
        )
    )

    assert np.linalg.norm(
        direct_n - hydrogen.D0_direction_hydrogen_s_inv
    ) < 2e-9
    assert abs(direct_log_nu - hydrogen.R_hydrogen_s_inv) < 2e-9
    assert abs(
        hydrogen.direction_hydrogen
        @ hydrogen.D0_direction_hydrogen_s_inv
    ) < 2e-14


def test_zero_tilt_limit_is_identity():
    snapshot = _snapshot().replace(
        beta_H=np.zeros(3), D0_beta_H_s_inv=np.zeros(3)
    )
    n = np.array([1.0, 2.0, -0.5])
    n /= np.linalg.norm(n)
    normal = normal_frame_characteristic(snapshot, n)
    hydrogen = hydrogen_frame_characteristic(snapshot, normal)

    assert np.allclose(hydrogen.direction_hydrogen, n)
    assert np.allclose(
        hydrogen.D0_direction_hydrogen_s_inv,
        normal.D0_direction_normal_s_inv,
    )
    assert hydrogen.R_hydrogen_s_inv == normal.R_normal_s_inv
