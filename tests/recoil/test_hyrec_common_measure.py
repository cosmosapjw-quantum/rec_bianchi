from pathlib import Path

import numpy as np
import pytest

from full_bianchi_hyrec.recoil.hyrec_common_measure import (
    CommonMeasureMoments,
    apply_scalar_bose_jvp,
    apply_scalar_bose_operator,
    HYREC2_DIFFUSION_START,
    HYREC2_DIFFUSION_STOP,
    build_oriented_tensor,
    conservative_conditional_moment_projection,
    integrate_disjoint_frequency_moments_x,
    integrate_same_interval_jump_moments_x,
    interval_equilibrium_weight_m3,
    interval_mode_measure_m3,
    implicit_scalar_bose_step,
    native_diffusion_centres_from_csv,
    native_voronoi_intervals,
    raw_native_adjacent_jump_moments,
    scalar_bose_equilibrium_family,
    scalar_bose_free_energy_m3,
    scalar_bose_photon_number_m3,
)

ROOT = Path(__file__).resolve().parents[2]
NATIVE_CSV = (
    ROOT
    / "archive"
    / "expanded"
    / "Full_Bianchi_HyRec_C3B1_native_sparse_block_v0_27"
    / "diffusion_detailed_balance.csv"
)


def test_interval_measures_reproduce_v050_registry():
    with np.load(ROOT / "data" / "full_scalar_com_khw_v050.npz") as data:
        intervals = data["state_intervals"]
        mode = data["mode_measure_m3"]
        equilibrium = data["equilibrium_weight_m3"]
    for index in (0, 8, 17, 29, 34):
        assert abs(interval_mode_measure_m3(intervals[index]) / mode[index] - 1.0) < 2e-15
        assert (
            abs(
                interval_equilibrium_weight_m3(intervals[index])
                / equilibrium[index]
                - 1.0
            )
            < 2e-15
        )


def test_conservative_projection_preserves_durable_mass_and_ratios():
    raw = np.asarray([2.0, -0.8, 0.7, -0.5, 0.4])
    output = conservative_conditional_moment_projection(raw, 7.0)
    assert output[0] == 7.0
    assert np.max(np.abs(output[1:] / output[0] - raw[1:] / raw[0])) == 0.0


def test_oriented_tensor_has_exact_exchange_parity():
    pair = {(0, 1): np.asarray([2.0, 3.0, 5.0, 7.0, 11.0])}
    same = {0: np.asarray([13.0, 0.0, 17.0, 0.0, 19.0])}
    tensor = build_oriented_tensor(pair, same, 2)
    assert np.array_equal(tensor[:, 0, 1], pair[(0, 1)])
    assert np.array_equal(
        tensor[:, 1, 0], pair[(0, 1)] * np.asarray([1, -1, 1, -1, 1])
    )
    assert tensor[1, 0, 0] == 0.0
    assert tensor[3, 0, 0] == 0.0


def test_source_conditioned_moment_jvp_is_exact():
    tensor_x = build_oriented_tensor(
        {(0, 1): np.asarray([2.0, 0.4, 0.3, 0.1, 0.08])},
        {
            0: np.asarray([1.0, 0.0, 0.2, 0.0, 0.06]),
            1: np.asarray([1.5, 0.0, 0.25, 0.0, 0.07]),
        },
        2,
    )
    width = 3.0
    moments = CommonMeasureMoments(
        intervals_x=np.asarray([[-1.0, 0.0], [0.0, 1.0]]),
        labels=np.asarray(["a", "b"]),
        mode_measure_m3=np.asarray([10.0, 11.0]),
        equilibrium_weight_m3=np.asarray([2.0, 3.0]),
        frequency_moments_x=tensor_x,
        frequency_moments_hz=tensor_x * width ** np.arange(5)[:, None, None],
        same_cell_jump_moments_x=np.stack(
            [tensor_x[:, 0, 0], tensor_x[:, 1, 1]], axis=1
        ),
        Doppler_width_Hz=width,
        nu_abs_Hz=100.0,
        temperature_K=3000.0,
        source="unit-test",
    )
    occupation = np.asarray([0.2, 0.4])
    direction = np.asarray([-0.3, 0.5])
    epsilon = 1e-7
    finite = (
        moments.source_conditioned_moments(occupation + epsilon * direction)
        - moments.source_conditioned_moments(occupation - epsilon * direction)
    ) / (2 * epsilon)
    exact = moments.source_conditioned_jvp(direction)
    assert np.max(np.abs(finite - exact)) / np.max(np.abs(exact)) < 4e-9
    assert np.all(moments.source_conditioned_moments()[2] >= 0.0)
    assert np.all(moments.source_conditioned_moments()[4] >= 0.0)


def test_native_diffusion_registry_and_voronoi_adapter_are_locked():
    native = native_diffusion_centres_from_csv(NATIVE_CSV)
    assert np.array_equal(
        native["virtual_index"],
        np.arange(HYREC2_DIFFUSION_START, HYREC2_DIFFUSION_STOP),
    )
    assert np.max(
        np.abs(
            native["detailed_balance_target"]
            - native["detailed_balance_reconstructed"]
        )
    ) < 5e-20
    intervals = native_voronoi_intervals(
        native["x"], window=(-4.25, 4.25), split_line_centre=True
    )
    assert intervals.shape == (3, 2)
    assert intervals[0, 0] == -4.25
    assert intervals[-1, 1] == 4.25
    assert np.any(intervals[:, 0] == 0.0)
    assert np.any(intervals[:, 1] == 0.0)
    raw = raw_native_adjacent_jump_moments(native)
    assert raw.shape == (5, 80)
    assert np.all(raw[0] >= 0.0)
    assert np.all(raw[2] >= 0.0)
    assert np.all(raw[4] >= 0.0)


@pytest.mark.slow
def test_direct_event_moment_quadrature_has_positive_even_moments_and_refines():
    target = (-0.25, 0.25)
    source = (0.25, 0.75)
    production = integrate_disjoint_frequency_moments_x(
        target, source, lane="production"
    )
    reference = integrate_disjoint_frequency_moments_x(
        target, source, lane="reference"
    )
    production_ratio = production[1:] / production[0]
    reference_ratio = reference[1:] / reference[0]
    assert production[0] > 0.0
    assert production[2] > 0.0
    assert production[4] > 0.0
    assert np.max(
        np.abs(production_ratio - reference_ratio)
        / np.maximum(np.abs(reference_ratio), 1e-300)
    ) < 3e-6

    same = integrate_same_interval_jump_moments_x(
        target, lane="production"
    )
    assert same[0] > 0.0
    assert same[1] == 0.0
    assert same[2] > 0.0
    assert same[3] == 0.0
    assert same[4] > 0.0



def _unit_common_measure() -> CommonMeasureMoments:
    tensor_x = build_oriented_tensor(
        {
            (0, 1): np.asarray([2.0, -0.4, 0.3, -0.1, 0.08]),
            (0, 2): np.asarray([0.9, -0.8, 0.75, -0.7, 0.68]),
            (1, 2): np.asarray([1.4, -0.35, 0.22, -0.16, 0.12]),
        },
        {
            0: np.asarray([1.0, 0.0, 0.2, 0.0, 0.06]),
            1: np.asarray([1.5, 0.0, 0.25, 0.0, 0.07]),
            2: np.asarray([0.8, 0.0, 0.18, 0.0, 0.05]),
        },
        3,
    )
    width = 3.0
    return CommonMeasureMoments(
        intervals_x=np.asarray([[-1.5, -0.5], [-0.5, 0.5], [0.5, 1.5]]),
        labels=np.asarray(["a", "b", "c"]),
        mode_measure_m3=np.asarray([10.0, 11.0, 12.0]),
        equilibrium_weight_m3=np.asarray([2.0, 3.0, 4.0]),
        frequency_moments_x=tensor_x,
        frequency_moments_hz=tensor_x * width ** np.arange(5)[:, None, None],
        same_cell_jump_moments_x=np.stack(
            [tensor_x[:, i, i] for i in range(3)], axis=1
        ),
        Doppler_width_Hz=width,
        nu_abs_Hz=100.0,
        temperature_K=3000.0,
        source="unit-test",
    )


def test_scalar_bose_operator_closes_equilibrium_number_entropy_and_energy():
    moments = _unit_common_measure()
    equilibrium = scalar_bose_equilibrium_family(moments, activity=0.7)
    null = apply_scalar_bose_operator(moments, equilibrium)
    assert np.max(np.abs(null.number_action_m3_s)) < 2e-15
    assert abs(null.number_residual_m3_s) < 2e-15
    assert abs(null.energy_ledger_residual_W_m3) == 0.0

    occupation = np.asarray([0.14, 0.38, 0.22])
    result = apply_scalar_bose_operator(moments, occupation)
    assert abs(result.number_residual_m3_s) < 2e-15
    assert result.entropy_production_m3_s < 0.0
    assert result.atom_power_W_m3 == -result.photon_power_W_m3
    assert result.energy_ledger_residual_W_m3 == 0.0


def test_scalar_bose_operator_jvp_matches_central_difference():
    moments = _unit_common_measure()
    occupation = np.asarray([0.14, 0.38, 0.22])
    direction = np.asarray([0.03, -0.08, 0.05])
    epsilon = 2e-7
    finite = (
        apply_scalar_bose_operator(
            moments, occupation + epsilon * direction
        ).occupation_action_s_inv
        - apply_scalar_bose_operator(
            moments, occupation - epsilon * direction
        ).occupation_action_s_inv
    ) / (2 * epsilon)
    exact = apply_scalar_bose_jvp(
        moments, occupation, direction
    ).occupation_action_jvp_s_inv
    assert np.linalg.norm(finite - exact) / np.linalg.norm(exact) < 2e-8
    assert abs(
        apply_scalar_bose_jvp(
            moments, occupation, direction
        ).number_residual_jvp_m3_s
    ) < 2e-15


def test_log_implicit_scalar_step_is_positive_conservative_and_dissipative():
    moments = _unit_common_measure()
    occupation = np.asarray([0.04, 0.9, 0.12])
    action = apply_scalar_bose_operator(moments, occupation).occupation_action_s_inv
    negative = action < 0.0
    critical = np.min(-occupation[negative] / action[negative])
    result = implicit_scalar_bose_step(
        moments, occupation, dt_s=1.03 * critical
    )
    assert result.explicit_trial_minimum < 0.0
    assert result.converged
    assert result.minimum_occupation > 0.0
    assert result.residual_relative < 2e-12
    assert result.number_relative_change < 2e-12
    assert result.free_energy_change_m3 < 0.0
    assert scalar_bose_photon_number_m3(moments, result.occupation) == pytest.approx(
        scalar_bose_photon_number_m3(moments, occupation), rel=2e-12
    )
    assert scalar_bose_free_energy_m3(moments, result.occupation) < scalar_bose_free_energy_m3(
        moments, occupation
    )


def test_v051_durable_common_measure_reproduces_v050_offdiagonal_mass_exactly():
    path = ROOT / "data" / "hyrec_common_measure_v051.npz"
    with np.load(path, allow_pickle=False) as current, np.load(
        ROOT / "data" / "full_scalar_com_khw_v050.npz", allow_pickle=False
    ) as parent:
        tensor = current["frequency_moments_x_m3_sInv"]
        durable = parent["pair_moments_m3_sInv"][0, :17, :17]
        offdiag = ~np.eye(17, dtype=bool)
        assert np.array_equal(tensor[0][offdiag], durable[offdiag])
        assert np.all(np.diag(tensor[0]) > 0.0)
        assert np.all(np.diag(tensor[1]) == 0.0)
        assert np.all(np.diag(tensor[3]) == 0.0)
        assert str(current["hyrec2_source_commit"].item()) == (
            "09e8243d0e08edd3603a94dfbc445ae06cafe139"
        )
        assert str(current["original_hyrec_archive_sha256"].item()) == (
            "OPEN_NOT_ACQUIRED"
        )


def test_v051_durable_operator_and_native_firewall_gates_are_closed():
    import json

    artifact = (
        ROOT
        / "archive"
        / "expanded"
        / "Full_Bianchi_HyRec_PR04A_HYREC_common_measure_v0_51"
    )
    ledger = json.loads((artifact / "PR04A_ledger.json").read_text())
    assert ledger["status"] == (
        "PASS_PR04A_COMMON_MEASURE_CORE_PR04B_ORIGINAL_HYREC_ARCHIVE_OPEN"
    )
    assert all(ledger["hard_gate_status"].values())
    assert ledger["decision"]["PR04"] == "IN_PROGRESS"
    assert ledger["decision"]["native_raw_rate_substitution"] == "FORBIDDEN"
    assert ledger["decision"]["original_HyRec_archive_parity"] == (
        "OPEN_FAIL_CLOSED"
    )

    moments = CommonMeasureMoments.from_npz(
        ROOT / "data" / "hyrec_common_measure_v051.npz"
    )
    equilibrium = scalar_bose_equilibrium_family(moments, activity=0.71)
    null = apply_scalar_bose_operator(moments, equilibrium)
    assert null.number_residual_m3_s == 0.0
    assert null.energy_ledger_residual_W_m3 == 0.0
    source = moments.source_conditioned_moments()
    assert np.all(source[0] > 0.0)
    assert np.all(source[2] > 0.0)
    assert np.all(source[4] > 0.0)
