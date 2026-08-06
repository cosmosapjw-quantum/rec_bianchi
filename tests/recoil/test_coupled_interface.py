from __future__ import annotations

import csv
import json
from pathlib import Path

import numpy as np
import pytest
from scipy.constants import c, h

from full_bianchi_hyrec.recoil.nonlinear_bose_runtime import CollisionNetwork
from full_bianchi_hyrec.recoil.split_domain_exchange import (
    ExchangeDirection,
    ExchangePacket,
    InterfaceSide,
)


ROOT = Path(__file__).resolve().parents[2]
NETWORK_PATH = ROOT / "data/full_scalar_com_khw_v050.npz"


def _packet(side: InterfaceSide, *, flux: float = 2.5e-14) -> ExchangePacket:
    frequency = 2.465e15 if side is InterfaceSide.RED else 2.467e15
    direction = (
        ExchangeDirection.COM_TO_NATIVE
        if side is InterfaceSide.RED
        else ExchangeDirection.NATIVE_TO_COM
    )
    reference = 0.1 * flux
    distortion = flux - reference
    return ExchangePacket(
        side=side,
        direction=direction,
        interface_x=-21.25 if side is InterfaceSide.RED else 21.25,
        interface_frequency_Hz=frequency,
        total_number_flux_per_H_s=flux,
        reference_number_flux_per_H_s=reference,
        distortion_number_flux_per_H_s=distortion,
        photon_energy_flux_W_per_H=h * frequency * flux,
        reference_photon_energy_flux_W_per_H=h * frequency * reference,
        distortion_photon_energy_flux_W_per_H=h * frequency * distortion,
        atom_energy_flux_W_per_H=0.0,
        source_snapshot_z=1100.0,
    )


def test_far_boundary_adapter_pins_exact_outer_state_registry():
    from full_bianchi_hyrec.recoil.coupled_interface import FarBoundaryAdapter

    network = CollisionNetwork.from_npz(NETWORK_PATH)
    adapter = FarBoundaryAdapter.from_network(network)
    red = adapter.for_side(InterfaceSide.RED)
    blue = adapter.for_side(InterfaceSide.BLUE)

    assert (red.label, red.index, red.interval, red.face_x) == (
        "FR00",
        29,
        (-21.25, -16.25),
        -21.25,
    )
    assert (blue.label, blue.index, blue.interval, blue.face_x) == (
        "FB02",
        34,
        (16.25, 21.25),
        21.25,
    )
    assert red.mode_measure_m3 == network.mode_measure[29]
    assert blue.mode_measure_m3 == network.mode_measure[34]
    assert red.centroid_frequency_Hz == network.momentum_scale[29] * c / h
    assert blue.centroid_frequency_Hz == network.momentum_scale[34] * c / h


def test_accumulator_is_positive_component_exact_and_restart_stable():
    from full_bianchi_hyrec.recoil.coupled_interface import (
        BoundaryTransferAccumulator,
    )

    packet = _packet(InterfaceSide.BLUE)
    accumulator = BoundaryTransferAccumulator.from_packet(packet, dt_s=1.25e5)
    assert accumulator.number_per_H == packet.total_number_flux_per_H_s * 1.25e5
    assert accumulator.energy_J_per_H == packet.photon_energy_flux_W_per_H * 1.25e5
    assert accumulator.energy_J_per_H == h * accumulator.interface_frequency_Hz * accumulator.number_per_H

    encoded = json.dumps(accumulator.to_dict(), sort_keys=True, separators=(",", ":"))
    decoded = BoundaryTransferAccumulator.from_dict(json.loads(encoded))
    assert decoded == accumulator
    assert decoded.sha256 == accumulator.sha256


def test_accumulator_rejects_bad_side_direction_and_nonpositive_duration():
    from full_bianchi_hyrec.recoil.coupled_interface import (
        BoundaryTransferAccumulator,
    )

    packet = _packet(InterfaceSide.RED)
    with pytest.raises(ValueError, match="dt_s"):
        BoundaryTransferAccumulator.from_packet(packet, dt_s=0.0)

    values = BoundaryTransferAccumulator.from_packet(packet, dt_s=1.0).to_dict()
    values["direction"] = ExchangeDirection.NATIVE_TO_COM.value
    with pytest.raises(ValueError, match="direction"):
        BoundaryTransferAccumulator.from_dict(values)


def test_boundary_number_deposition_matches_integrated_packet_exactly():
    from full_bianchi_hyrec.recoil.coupled_interface import (
        BoundaryTransferAccumulator,
        FarBoundaryAdapter,
    )

    network = CollisionNetwork.from_npz(NETWORK_PATH)
    adapter = FarBoundaryAdapter.from_network(network)
    weights = np.asarray([0.05, 0.15, 0.3, 0.5])
    n_H_m3 = 2.5018675437302318e8

    for side, sign in ((InterfaceSide.RED, -1.0), (InterfaceSide.BLUE, 1.0)):
        accumulator = BoundaryTransferAccumulator.from_packet(
            _packet(side), dt_s=1.0e5
        )
        increment = adapter.occupation_increment(
            accumulator,
            n_H_m3=n_H_m3,
            angular_weights=weights,
        )
        assert increment.shape == (network.n_state, len(weights))
        number_change = float(
            np.sum(network.mode_measure[:, None] * increment * weights[None, :])
        )
        assert number_change == pytest.approx(
            sign * n_H_m3 * accumulator.number_per_H,
            rel=3e-15,
            abs=0.0,
        )
        nonzero = np.flatnonzero(np.any(increment != 0.0, axis=1))
        expected = 29 if side is InterfaceSide.RED else 34
        assert np.array_equal(nonzero, np.asarray([expected]))


def test_interface_transfer_ledger_closes_number_energy_and_atom_sources_exactly():
    from full_bianchi_hyrec.recoil.coupled_interface import (
        BoundaryTransferAccumulator,
        FarBoundaryAdapter,
        InterfaceTransferLedger,
    )

    network = CollisionNetwork.from_npz(NETWORK_PATH)
    adapter = FarBoundaryAdapter.from_network(network)
    accumulators = tuple(
        BoundaryTransferAccumulator.from_packet(_packet(side), dt_s=1.0e5)
        for side in (InterfaceSide.RED, InterfaceSide.BLUE)
    )
    ledger = InterfaceTransferLedger.from_accumulators(
        adapter,
        accumulators,
        n_H_m3=2.5018675437302318e8,
    )

    assert ledger.native_number_change_per_H + ledger.com_number_change_per_H == 0.0
    assert ledger.native_energy_change_J_per_H + ledger.com_energy_change_J_per_H == 0.0
    assert ledger.number_residual_per_H == 0.0
    assert ledger.transported_energy_residual_J_per_H == 0.0
    assert ledger.atom_energy_change_J_per_H == 0.0
    ledger.validate()


def test_face_energy_is_not_replaced_by_finite_cell_centroid():
    from full_bianchi_hyrec.recoil.coupled_interface import (
        BoundaryTransferAccumulator,
        FarBoundaryAdapter,
        InterfaceTransferLedger,
    )

    network = CollisionNetwork.from_npz(NETWORK_PATH)
    adapter = FarBoundaryAdapter.from_network(network)
    accumulator = BoundaryTransferAccumulator.from_packet(
        _packet(InterfaceSide.RED), dt_s=1.0e5
    )
    ledger = InterfaceTransferLedger.from_accumulators(
        adapter,
        (accumulator,),
        n_H_m3=2.5018675437302318e8,
    )
    side = ledger.sides[0]

    assert side.cell_centroid_energy_proxy_J_per_H != side.com_energy_change_J_per_H
    assert side.unresolved_energy_correction_J_per_H != 0.0
    assert side.cell_centroid_energy_proxy_J_per_H + side.unresolved_energy_correction_J_per_H == pytest.approx(
        side.com_energy_change_J_per_H,
        rel=3e-15,
        abs=0.0,
    )


def _octahedral_grid():
    from full_bianchi_hyrec.recoil.nonlinear_bose_release import HarmonicGrid

    directions = np.asarray(
        [
            [1.0, 0.0, 0.0],
            [-1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0],
            [0.0, -1.0, 0.0],
            [0.0, 0.0, 1.0],
            [0.0, 0.0, -1.0],
        ]
    )
    return HarmonicGrid.from_directions(
        directions, np.full(6, 1.0 / 6.0), ell_max=1
    )


def _two_boundary_network() -> CollisionNetwork:
    pair = np.zeros((2, 2, 2))
    pair[0, 0, 1] = pair[0, 1, 0] = 0.8
    pair[1, 0, 1] = pair[1, 1, 0] = 0.12
    return CollisionNetwork(
        state_intervals=np.asarray([[-21.25, -16.25], [16.25, 21.25]]),
        state_labels=np.asarray(["FR00", "FB02"]),
        pair_moments=pair,
        same_cell_rates=np.zeros((2, 2)),
        mode_measure=np.asarray([2.0, 3.0]),
        equilibrium_weight=np.asarray([0.4, 0.9]),
        momentum_scale=np.asarray([h * 2.4655e15 / c, h * 2.4665e15 / c]),
        inherited_release_policy={"synthetic": 1},
    )


def test_coupled_residual_analytic_jvp_matches_central_difference():
    from full_bianchi_hyrec.recoil.coupled_interface import CoupledInterfaceProblem

    network = _two_boundary_network()
    grid = _octahedral_grid()
    packets = (
        _packet(InterfaceSide.RED, flux=3.0e-3),
        _packet(InterfaceSide.BLUE, flux=2.0e-3),
    )
    problem = CoupledInterfaceProblem(
        network=network,
        grid=grid,
        packets=packets,
        n_H_m3=0.8,
        dt_s=0.2,
    )
    old = np.asarray(
        [
            [0.32, 0.08, 0.24, 0.11, 0.28, 0.09],
            [0.015, 0.09, 0.025, 0.08, 0.03, 0.07],
        ]
    )
    field = 1.03 * old
    vector = problem.pack(np.log(field), np.log(np.asarray([0.9, 1.1])))
    direction = np.linspace(-0.03, 0.04, vector.size)
    exact = problem.jvp(vector, direction, old, scaled=True)

    errors = []
    for epsilon in (2.0e-5, 1.0e-5, 5.0e-6):
        numeric = (
            problem.scaled_residual(vector + epsilon * direction, old)
            - problem.scaled_residual(vector - epsilon * direction, old)
        ) / (2.0 * epsilon)
        errors.append(
            np.linalg.norm(exact - numeric) / max(np.linalg.norm(numeric), 1e-300)
        )
    assert min(errors) < 1.0e-8


def test_unscaled_residual_preserves_exact_interface_number_identity():
    from full_bianchi_hyrec.recoil.coupled_interface import CoupledInterfaceProblem
    from full_bianchi_hyrec.recoil.nonlinear_bose_release import (
        apply_nonlinear_bose_operator,
    )

    network = _two_boundary_network()
    grid = _octahedral_grid()
    problem = CoupledInterfaceProblem(
        network=network,
        grid=grid,
        packets=(
            _packet(InterfaceSide.RED, flux=3.0e-3),
            _packet(InterfaceSide.BLUE, flux=2.0e-3),
        ),
        n_H_m3=0.8,
        dt_s=0.2,
    )
    old = np.full((2, 6), 0.2)
    field = np.asarray(
        [
            [0.21, 0.19, 0.22, 0.18, 0.205, 0.195],
            [0.17, 0.16, 0.18, 0.15, 0.175, 0.165],
        ]
    )
    rho = np.asarray([0.85, 1.15])
    vector = problem.pack(np.log(field), np.log(rho))
    residual = problem.unscaled_residual(vector, old)
    residual_f, _ = problem.unpack_residual(residual)

    action = apply_nonlinear_bose_operator(
        field,
        mode_measure=network.mode_measure,
        equilibrium_weight=network.equilibrium_weight,
        pair_moments=network.pair_moments,
        same_cell_rates=network.same_cell_rates,
        grid=grid,
    )
    assert abs(action.number_residual) < 1.0e-13
    weighted_residual = float(
        np.sum(
            network.mode_measure[:, None]
            * residual_f
            * grid.weights[None, :]
        )
    )
    expected = (
        float(
            np.sum(
                network.mode_measure[:, None]
                * (field - old)
                * grid.weights[None, :]
            )
        )
        - problem.interface_number_change_m3(np.log(rho))
    )
    assert weighted_residual == pytest.approx(expected, rel=3e-14, abs=3e-16)


def test_coupled_implicit_step_recovers_positivity_after_negative_explicit_trial():
    from full_bianchi_hyrec.recoil.coupled_interface import (
        CoupledInterfaceProblem,
        solve_coupled_interface,
    )

    network = _two_boundary_network()
    grid = _octahedral_grid()
    old = np.asarray(
        [
            [0.32, 0.08, 0.24, 0.11, 0.28, 0.09],
            [0.015, 0.09, 0.025, 0.08, 0.03, 0.07],
        ]
    )
    from full_bianchi_hyrec.recoil.nonlinear_bose_release import (
        apply_nonlinear_bose_operator,
    )
    action = apply_nonlinear_bose_operator(
        old,
        mode_measure=network.mode_measure,
        equilibrium_weight=network.equilibrium_weight,
        pair_moments=network.pair_moments,
        same_cell_rates=network.same_cell_rates,
        grid=grid,
    ).occupation_action
    negative = action < 0.0
    critical = float(np.min(-old[negative] / action[negative]))
    problem = CoupledInterfaceProblem(
        network=network,
        grid=grid,
        packets=(_packet(InterfaceSide.BLUE, flux=1.0e-6),),
        n_H_m3=1.0,
        dt_s=1.05 * critical,
    )
    result = solve_coupled_interface(
        old,
        problem,
        nonlinear_rtol=5.0e-12,
        gmres_rtol=1.0e-11,
    )

    assert result.converged
    assert result.explicit_trial_minimum < 0.0
    assert result.minimum_occupation > 0.0
    assert result.residual_relative < 1.0e-11
    assert result.number_relative_residual < 1.0e-11
    assert result.collision_entropy_production <= 1.0e-11
    assert len(result.accumulators) == 1
    result.ledger.validate()


def test_interface_guard_off_is_exact_collision_solver_parity():
    from full_bianchi_hyrec.recoil.coupled_interface import (
        CoupledInterfaceProblem,
        solve_coupled_interface,
    )
    from full_bianchi_hyrec.recoil.nonlinear_bose_runtime import implicit_bose_step

    network = _two_boundary_network()
    grid = _octahedral_grid()
    old = np.asarray(
        [
            [0.32, 0.08, 0.24, 0.11, 0.28, 0.09],
            [0.015, 0.09, 0.025, 0.08, 0.03, 0.07],
        ]
    )
    baseline = implicit_bose_step(
        old,
        dt_s=0.2,
        network=network,
        grid=grid,
        nonlinear_rtol=2.0e-11,
        gmres_rtol=2.0e-8,
    )
    problem = CoupledInterfaceProblem(
        network=network,
        grid=grid,
        packets=(),
        n_H_m3=1.0,
        dt_s=0.2,
        enabled=False,
    )
    result = solve_coupled_interface(
        old,
        problem,
        nonlinear_rtol=2.0e-11,
        gmres_rtol=2.0e-8,
    )

    assert np.array_equal(result.occupation, baseline.occupation)
    assert result.accumulators == ()
    assert result.ledger.sides == ()
    assert result.number_relative_residual == baseline.number_relative_change
    assert result.residual_relative == baseline.residual_relative


def test_boundary_speed_audit_localizes_internal_zeros_and_rejects_endpoint_heuristic():
    from full_bianchi_hyrec.recoil.coupled_interface import (
        audit_boundary_speed_history,
    )

    audit = audit_boundary_speed_history(
        np.asarray([0.0, 1.0, 2.0]),
        np.asarray([1.0, -1.0, 1.0]),
        np.asarray([-1.0, 1.0, -1.0]),
    )
    assert np.allclose(audit.red_roots, [0.5, 1.5])
    assert np.allclose(audit.blue_roots, [0.5, 1.5])
    assert audit.red_positive_integral > 0.0
    assert audit.red_negative_integral > 0.0
    assert audit.blue_positive_integral > 0.0
    assert audit.blue_negative_integral > 0.0
    assert audit.red_endpoint_heuristic_error != 0.0
    assert audit.blue_endpoint_heuristic_error != 0.0


@pytest.mark.parametrize(
    ("model", "angle"),
    [
        ("Bianchi_II_large_shear", 0),
        ("Bianchi_VI_h_tilted_large_shear", 20),
        ("Bianchi_VI_minus_1_over_9_exceptional", 6),
    ],
)
def test_stored_bianchi_histories_require_branch_zero_localization(model, angle):
    from full_bianchi_hyrec.recoil.coupled_interface import (
        audit_boundary_speed_history,
    )

    with np.load(ROOT / "data/pr01c_background_snapshots_v048.npz") as data:
        audit = audit_boundary_speed_history(
            data[f"{model}_cosmic_time_s"],
            data[f"{model}_red_speed_s_inv"][:, angle],
            data[f"{model}_blue_speed_s_inv"][:, angle],
        )
    assert len(audit.red_roots) >= 1
    assert len(audit.blue_roots) >= 1
    assert audit.red_total_absolute_integral > 0.0
    assert audit.blue_total_absolute_integral > 0.0
    assert abs(audit.red_endpoint_heuristic_error) > 0.0
    assert abs(audit.blue_endpoint_heuristic_error) > 0.0


def test_coupled_restart_payload_round_trips_exactly():
    from full_bianchi_hyrec.recoil.coupled_interface import (
        CoupledInterfaceProblem,
        CoupledInterfaceRestartState,
        solve_coupled_interface,
    )

    network = _two_boundary_network()
    grid = _octahedral_grid()
    old = np.asarray(
        [
            [0.32, 0.08, 0.24, 0.11, 0.28, 0.09],
            [0.015, 0.09, 0.025, 0.08, 0.03, 0.07],
        ]
    )
    problem = CoupledInterfaceProblem(
        network=network,
        grid=grid,
        packets=(
            _packet(InterfaceSide.RED, flux=3.0e-5),
            _packet(InterfaceSide.BLUE, flux=2.0e-5),
        ),
        n_H_m3=0.8,
        dt_s=0.2,
    )
    result = solve_coupled_interface(old, problem)
    encoded = json.dumps(result.restart_payload(), sort_keys=True, separators=(",", ":"))
    restored = CoupledInterfaceRestartState.from_payload(json.loads(encoded))

    assert np.array_equal(restored.occupation, result.occupation)
    assert restored.accumulators == result.accumulators
    assert restored.dt_s == result.dt_s
    assert restored.interface_enabled is result.interface_enabled
    assert restored.to_payload() == result.restart_payload()


def test_full_network_packet_solve_accepts_verified_gross_backward_error():
    from full_bianchi_hyrec.recoil.coupled_interface import (
        CoupledInterfaceProblem,
        solve_coupled_interface,
    )
    from full_bianchi_hyrec.recoil.nonlinear_bose_release import HarmonicGrid

    network = CollisionNetwork.from_npz(NETWORK_PATH)
    background_path = ROOT / "data/pr01c_background_snapshots_v048.npz"
    with np.load(background_path, allow_pickle=False) as background:
        grid = HarmonicGrid.from_directions(
            background["directions"], background["angular_weights"], ell_max=0
        )
    packet_path = (
        ROOT
        / "archive/expanded/Full_Bianchi_HyRec_PR04C0C1A_split_domain_boundary_v0_55"
        / "THREE_SNAPSHOT_INTERFACE_PACKETS.csv"
    )
    with packet_path.open(newline="", encoding="utf-8") as handle:
        rows = [row for row in csv.DictReader(handle) if float(row["target_z"]) == 1300.0]
    packets = tuple(
        ExchangePacket(
            side=InterfaceSide(row["side"]),
            direction=ExchangeDirection(row["direction"]),
            interface_x=float(row["interface_x"]),
            interface_frequency_Hz=float(row["interface_frequency_Hz"]),
            total_number_flux_per_H_s=float(row["total_number_flux_per_H_s"]),
            reference_number_flux_per_H_s=float(row["reference_number_flux_per_H_s"]),
            distortion_number_flux_per_H_s=float(row["distortion_number_flux_per_H_s"]),
            photon_energy_flux_W_per_H=float(row["total_photon_energy_flux_W_per_H"]),
            reference_photon_energy_flux_W_per_H=float(row["reference_photon_energy_flux_W_per_H"]),
            distortion_photon_energy_flux_W_per_H=float(row["distortion_photon_energy_flux_W_per_H"]),
            atom_energy_flux_W_per_H=float(row["atom_source_W_per_H"]),
            source_snapshot_z=float(row["snapshot_z"]),
        )
        for row in rows
    )
    activity = network.equilibrium_weight / network.mode_measure
    old = (activity / (1.0 - activity))[:, None] * np.ones((1, grid.n_angle))
    problem = CoupledInterfaceProblem(
        network=network,
        grid=grid,
        packets=packets,
        n_H_m3=float(rows[0]["nH_cm3"]) * 1.0e6,
        dt_s=1.0e5,
    )

    result = solve_coupled_interface(
        old,
        problem,
        nonlinear_rtol=1.0e-11,
        gmres_rtol=1.0e-10,
        max_newton=20,
        gmres_maxiter=300,
    )

    assert result.converged
    assert result.backward_error_relative < 1.0e-11
    assert result.number_relative_residual < 1.0e-11
    assert result.convergence_basis in {"scaled_residual", "gross_backward_error"}
