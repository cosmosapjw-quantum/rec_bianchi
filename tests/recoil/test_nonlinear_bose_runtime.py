from pathlib import Path

import numpy as np
import pytest

from full_bianchi_hyrec.background.snapshot import BackgroundSnapshot
from full_bianchi_hyrec.recoil.nonlinear_bose_release import HarmonicGrid
from full_bianchi_hyrec.recoil.nonlinear_bose_runtime import (
    ADAPTIVE_GRID_ORDER,
    BoseCollisionRuntime,
    CollisionNetwork,
    LineBoundaryConfig,
    boost_four_hydrogen_to_normal,
    boost_four_normal_to_hydrogen,
    implicit_bose_step,
    implicit_residual_jvp,
    positive_harmonic_grid,
    prepare_runtime_state,
)


ROOT = Path(__file__).resolve().parents[2]
SNAPSHOT_DATA = ROOT / "data" / "pr01c_background_snapshots_v048.npz"
COLLISION_DATA = ROOT / "data" / "full_scalar_com_khw_v050.npz"
MODEL_META = {
    "Bianchi_II_large_shear": ("class_a", "II"),
    "Bianchi_VI_h_tilted_large_shear": ("class_b_tilted", "VI_h"),
    "Bianchi_VI_minus_1_over_9_exceptional": (
        "exceptional_VI",
        "VI_-1/9",
    ),
}


def snapshot_record(model: str, index: int) -> BackgroundSnapshot:
    chart, bianchi_type = MODEL_META[model]
    with np.load(SNAPSHOT_DATA, allow_pickle=False) as data:
        return BackgroundSnapshot(
            tau=data[f"{model}_tau"][index],
            cosmic_time_s=data[f"{model}_cosmic_time_s"][index],
            H_s_inv=data[f"{model}_H_s_inv"][index],
            q=data[f"{model}_q"][index],
            sigma_s_inv=data[f"{model}_sigma_s_inv"][index],
            N_s_inv=data[f"{model}_N_s_inv"][index],
            A_s_inv=data[f"{model}_A_s_inv"][index],
            frame_rotation_s_inv=data[
                f"{model}_frame_rotation_s_inv"
            ][index],
            beta_H=data[f"{model}_beta_H"][index],
            D0_beta_H_s_inv=data[f"{model}_D0_beta_H_s_inv"][index],
            chart_id=chart,
            bianchi_type=bianchi_type,
        )


def octahedral_grid() -> HarmonicGrid:
    directions = np.asarray(
        [
            [1, 0, 0],
            [-1, 0, 0],
            [0, 1, 0],
            [0, -1, 0],
            [0, 0, 1],
            [0, 0, -1],
        ],
        dtype=float,
    )
    return HarmonicGrid.from_directions(
        directions,
        np.full(6, 1 / 6),
        ell_max=1,
    )


def two_state_network() -> CollisionNetwork:
    return CollisionNetwork(**two_state_network_inputs())


def two_state_network_inputs() -> dict[str, object]:
    pair = np.zeros((2, 2, 2))
    pair[0, 0, 1] = pair[0, 1, 0] = 0.8
    pair[1, 0, 1] = pair[1, 1, 0] = 0.12
    return {
        "state_intervals": np.asarray([[-1.0, 0.0], [0.0, 1.0]]),
        "state_labels": np.asarray(["I0", "NR0"]),
        "pair_moments": pair,
        "same_cell_rates": np.zeros((2, 2)),
        "mode_measure": np.asarray([2.0, 3.0]),
        "equilibrium_weight": np.asarray([0.4, 0.9]),
        "momentum_scale": np.asarray([1.0, 1.1]),
        "inherited_release_policy": {"finite_tilt": 12},
    }


@pytest.mark.parametrize(
    ("ell_max", "point_count"),
    [(12, 302), (20, 590), (24, 974)],
)
def test_positive_harmonic_grid_lock(ell_max, point_count):
    grid = positive_harmonic_grid(ell_max)
    assert ADAPTIVE_GRID_ORDER[ell_max] in (29, 41, 53)
    assert grid.n_angle == point_count
    assert np.min(grid.weights) > 0
    assert abs(np.sum(grid.weights) - 1.0) < 2e-15
    assert grid.gram_residual < 5e-13
    assert not grid.weights.flags.writeable
    assert positive_harmonic_grid(ell_max) is grid


@pytest.mark.parametrize(
    ("model", "index", "policy", "ell_max"),
    [
        (
            "Bianchi_VI_h_tilted_large_shear",
            100,
            "finite_or_mixed_tilt",
            12,
        ),
        ("Bianchi_II_large_shear", 70, "nonlinear_even_shear", 20),
        ("Bianchi_II_large_shear", 0, "directional_crossing", 24),
    ],
)
def test_background_snapshot_selects_locked_adaptive_lane(
    model,
    index,
    policy,
    ell_max,
):
    state = prepare_runtime_state(
        snapshot_record(model, index),
        boundary=LineBoundaryConfig.lyman_alpha(),
    )
    assert state.policy.policy == policy
    assert state.policy.ell_max == ell_max
    assert state.frame_roundtrip_residual < 2e-14
    assert np.min(state.doppler_factor) > 0
    assert np.max(
        np.abs(np.linalg.norm(state.direction_hydrogen, axis=1) - 1.0)
    ) < 2e-14


def test_four_vector_boost_roundtrip_and_same_event_closure():
    beta = np.asarray([0.31, -0.12, 0.08])
    normal = np.asarray([1.7, 0.2, -0.4, 0.1])
    hydrogen = boost_four_normal_to_hydrogen(normal, beta)
    recovered = boost_four_hydrogen_to_normal(hydrogen, beta)
    assert np.allclose(recovered, normal, rtol=2e-15, atol=2e-15)

    photon = np.asarray([0.3, 0.02, -0.04, 0.01])
    atom = -photon
    assert np.linalg.norm(
        boost_four_hydrogen_to_normal(photon, beta)
        + boost_four_hydrogen_to_normal(atom, beta)
    ) < 2e-16


def test_background_geometry_does_not_modify_local_collision_microphysics():
    network = CollisionNetwork.from_npz(COLLISION_DATA)
    runtime = BoseCollisionRuntime(network)
    first = runtime.prepare(
        snapshot_record("Bianchi_II_large_shear", 70),
        force_ell_max=12,
    )
    second = runtime.prepare(
        snapshot_record("Bianchi_VI_h_tilted_large_shear", 100),
        force_ell_max=12,
    )
    base = 0.16 + 0.02 * np.cos(network.centers / 4.0)
    angular = 1.0 + 0.08 * first.grid.directions[:, 2]
    occupation = base[:, None] * angular[None, :]

    first_result = runtime.evaluate(first, occupation)
    second_result = runtime.evaluate(second, occupation)

    assert np.array_equal(
        first_result.full_action.occupation_action,
        second_result.full_action.occupation_action,
    )
    assert first_result.four_force_hydrogen_residual == 0.0
    assert second_result.four_force_hydrogen_residual == 0.0
    assert first_result.four_force_normal_residual < 2e-25
    assert second_result.four_force_normal_residual < 2e-25


def test_log_implicit_update_preserves_positivity_number_and_free_energy():
    grid = octahedral_grid()
    network = two_state_network()
    occupation = np.asarray(
        [
            [0.32, 0.08, 0.24, 0.11, 0.28, 0.09],
            [0.015, 0.09, 0.025, 0.08, 0.03, 0.07],
        ]
    )
    from full_bianchi_hyrec.recoil.nonlinear_bose_release import (
        apply_nonlinear_bose_operator,
    )

    operator = apply_nonlinear_bose_operator(
        occupation,
        mode_measure=network.mode_measure,
        equilibrium_weight=network.equilibrium_weight,
        pair_moments=network.pair_moments,
        same_cell_rates=network.same_cell_rates,
        grid=grid,
    ).occupation_action
    negative = operator < 0
    critical = float(np.min(-occupation[negative] / operator[negative]))
    result = implicit_bose_step(
        occupation,
        dt_s=1.05 * critical,
        network=network,
        grid=grid,
        nonlinear_rtol=2e-11,
    )

    assert result.converged
    assert result.explicit_trial_minimum < 0
    assert result.minimum_occupation > 0
    assert result.residual_relative < 2e-11
    assert result.number_relative_change < 2e-12
    assert result.free_energy_change < 0


def test_implicit_log_residual_jvp_matches_finite_difference():
    grid = octahedral_grid()
    network = two_state_network()
    occupation = np.asarray(
        [
            [0.32, 0.08, 0.24, 0.11, 0.28, 0.09],
            [0.015, 0.09, 0.025, 0.08, 0.03, 0.07],
        ]
    )
    direction = np.asarray(
        [
            [0.03, -0.02, 0.01, -0.015, 0.02, -0.01],
            [-0.01, 0.015, -0.02, 0.01, -0.005, 0.02],
        ]
    )
    dt_s = 0.2
    exact = implicit_residual_jvp(
        occupation,
        direction,
        dt_s=dt_s,
        network=network,
        grid=grid,
    )

    from full_bianchi_hyrec.recoil.nonlinear_bose_release import (
        apply_nonlinear_bose_operator,
    )

    old = 0.9 * occupation

    def residual(log_occupation):
        field = np.exp(log_occupation)
        action = apply_nonlinear_bose_operator(
            field,
            mode_measure=network.mode_measure,
            equilibrium_weight=network.equilibrium_weight,
            pair_moments=network.pair_moments,
            same_cell_rates=network.same_cell_rates,
            grid=grid,
        ).occupation_action
        return field - old - dt_s * action

    epsilon = 1e-5
    log_f = np.log(occupation)
    finite_difference = (
        residual(log_f + epsilon * direction)
        - residual(log_f - epsilon * direction)
    ) / (2 * epsilon)
    relative = np.linalg.norm(exact - finite_difference) / (
        np.linalg.norm(finite_difference) + 1e-300
    )
    assert relative < 5e-10


@pytest.mark.parametrize(
    "field",
    [
        "state_intervals",
        "pair_moments",
        "same_cell_rates",
        "mode_measure",
        "equilibrium_weight",
        "momentum_scale",
    ],
)
def test_collision_network_rejects_nonfinite_numeric_fields(field):
    """Catch NaN network data passing sign and symmetry comparisons."""

    arguments = two_state_network_inputs()
    damaged = np.asarray(arguments[field]).copy()
    damaged.flat[0] = np.nan
    arguments[field] = damaged

    with pytest.raises(ValueError, match="finite"):
        CollisionNetwork(**arguments)


@pytest.mark.parametrize("policy_value", [True, 1.5, -1])
def test_collision_network_rejects_invalid_release_policy(policy_value):
    """Catch lossy int coercion and negative inherited harmonic orders."""

    arguments = two_state_network_inputs()
    arguments["inherited_release_policy"] = {"synthetic": policy_value}

    with pytest.raises(ValueError, match="release policy"):
        CollisionNetwork(**arguments)


@pytest.mark.parametrize(
    "field",
    [
        "nu_abs_Hz",
        "Doppler_width_Hz",
        "x_red",
        "x_blue",
        "D0_nu_abs_Hz_s",
        "D0_log_Doppler_width_s_inv",
        "D0_x_red_s_inv",
        "D0_x_blue_s_inv",
    ],
)
def test_line_boundary_config_rejects_nonfinite_fields(field):
    """Catch NaN line-boundary values bypassing order/positivity comparisons."""

    arguments = {
        "nu_abs_Hz": 2.466e15,
        "Doppler_width_Hz": 5.0e10,
    }
    arguments[field] = float("nan")

    with pytest.raises(ValueError, match="finite"):
        LineBoundaryConfig(**arguments)


def test_lyman_alpha_rejects_nonfinite_temperature():
    """Catch NaN temperature propagating into a NaN Doppler width."""

    with pytest.raises(ValueError, match="temperature_K"):
        LineBoundaryConfig.lyman_alpha(temperature_K=float("nan"))
