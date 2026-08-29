from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from full_bianchi_hyrec.recoil.original_hyrec_physical_flux import (
    parse_original_hyrec_snapshot_csv,
)
from full_bianchi_hyrec.trajectory.causal_history import (
    AcceptedRadiationHistory,
    CharacteristicHistoryGrid,
    FutureHistoryEndpointError,
    HistoryAppendCandidate,
    build_original_hyrec_queries,
    construct_original_hyrec_incoming,
)
from full_bianchi_hyrec.trajectory.causal_history_step import (
    CausalHistoryAcceptedStepProblem,
)
from full_bianchi_hyrec.trajectory.primitive_rates import OriginalHyRecPrimitiveRateTable
from full_bianchi_hyrec.trajectory.primitive_trajectory import PrimitiveTrajectoryProblem, atomic_state_from_source_snapshot
from full_bianchi_hyrec.trajectory.time_dependent_native import SourceIdentifiableOriginalHyRecDAE
from full_bianchi_hyrec.background.snapshot import BackgroundSnapshot
from full_bianchi_hyrec.recoil.nonlinear_bose_runtime import CollisionNetwork, LineBoundaryConfig, positive_harmonic_grid


ROOT = Path(__file__).resolve().parents[2]
ARCHIVE = ROOT / "archive/inputs/original_hyrec_oct2012/HyRec_Oct2012.zip"
SNAPSHOT_DIR = ROOT / "archive/expanded/Full_Bianchi_HyRec_PR04C0C1A_split_domain_boundary_v0_55"
NETWORK = ROOT / "data/full_scalar_com_khw_v050.npz"
HISTORY = ROOT / "data/pr05b2_source_history_v060.npz"


def _synthetic_history(n: int = 12) -> AcceptedRadiationHistory:
    energy = np.linspace(5.0, 12.7, 311)
    eta0 = -8.0
    dlna = 1.0e-3
    eta = eta0 + dlna * np.arange(n)
    virtual = np.empty((311, n))
    average = np.empty((311, n))
    for b in range(311):
        virtual[b] = 1.0e-12 * (1.0 + 0.001 * b) * (1.0 + 0.01 * np.arange(n))
        average[b] = -0.25 * virtual[b]
    lyman = np.vstack([
        2.0e-13 * (1.0 + 0.02 * np.arange(n)),
        3.0e-14 * (1.0 + 0.03 * np.arange(n)),
        4.0e-15 * (1.0 + 0.04 * np.arange(n)),
    ])
    grid = CharacteristicHistoryGrid(
        eta=eta,
        source_indices=np.arange(n),
        z_start=np.exp(-eta0) - 1.0,
        dlna=dlna,
        energy_eV=energy,
        source_hashes={"synthetic": "0" * 64},
    )
    return AcceptedRadiationHistory(
        grid=grid,
        outgoing_virtual=virtual,
        outgoing_lyman=lyman,
        average_virtual=average,
        completeness="SYNTHETIC_FULL",
    )


def _dae(target: int = 1100) -> tuple[SourceIdentifiableOriginalHyRecDAE, object]:
    source = parse_original_hyrec_snapshot_csv(SNAPSHOT_DIR / f"pr04c_z{target}.csv")
    table = OriginalHyRecPrimitiveRateTable.from_archive(ARCHIVE)
    rates = table.evaluate(
        radiation_temperature_eV_rescaled=source.TR_eV_rescaled,
        matter_to_radiation_temperature_ratio=source.TM_over_TR,
        fsR=source.fsR,
        meR=source.meR,
    )
    network = CollisionNetwork.from_npz(NETWORK)
    grid = positive_harmonic_grid(12)
    activity = network.equilibrium_weight / network.mode_measure
    scalar = activity / (1.0 - activity)
    state = atomic_state_from_source_snapshot(
        source,
        com_occupation=scalar[:, None] * np.ones((1, grid.n_angle)),
        beta_H=np.zeros(3),
    )
    background = BackgroundSnapshot(
        tau=-np.log1p(source.z),
        cosmic_time_s=1.0,
        H_s_inv=source.H_s_inv,
        q=0.5,
        sigma_s_inv=np.zeros((3, 3)),
        N_s_inv=np.zeros((3, 3)),
        A_s_inv=np.zeros(3),
        frame_rotation_s_inv=np.zeros(3),
        beta_H=np.zeros(3),
        D0_beta_H_s_inv=np.zeros(3),
        chart_id="pr05b2-test",
        bianchi_type="I",
    )
    primitive = PrimitiveTrajectoryProblem(
        background=background,
        source_snapshot=source,
        rates=rates,
        network=network,
        grid=grid,
        line=LineBoundaryConfig.lyman_alpha(
            temperature_K=state.T_m_K, x_red=-21.25, x_blue=21.25
        ),
        interface_enabled=False,
    )
    return SourceIdentifiableOriginalHyRecDAE.from_primitive_problem(primitive), source


def test_history_schema_is_immutable_monotone_and_binary_restart_exact() -> None:
    history = _synthetic_history()
    assert history.accepted_count == 12
    assert np.all(np.diff(history.grid.eta) > 0.0)
    assert history.outgoing_virtual.flags.writeable is False
    payload = history.to_bytes()
    decoded = AcceptedRadiationHistory.from_bytes(payload)
    assert decoded.to_bytes() == payload
    assert decoded.sha256 == history.sha256
    assert np.array_equal(decoded.outgoing_virtual, history.outgoing_virtual)


def test_source_query_registry_has_exact_channel_counts_and_no_missing_output() -> None:
    source = parse_original_hyrec_snapshot_csv(SNAPSHOT_DIR / "pr04c_z1100.csv")
    queries = build_original_hyrec_queries(source.energy_eV, z=source.z)
    assert len(queries) == 313
    assert sum(query.channel == "virtual_to_virtual" for query in queries) == 308
    assert sum(query.source_kind == "lyman" and query.target_kind == "virtual" for query in queries) == 3
    assert sum(query.source_kind == "virtual" and query.target_kind == "lyman" for query in queries) == 2
    virtual_outputs = sorted(query.target_index for query in queries if query.target_kind == "virtual")
    line_outputs = sorted(query.target_index for query in queries if query.target_kind == "lyman")
    assert virtual_outputs == list(range(311))
    assert line_outputs == [0, 1]


def test_interpolator_rejects_future_endpoint_and_keeps_primal_stencil_for_jvp() -> None:
    history = _synthetic_history()
    eta_query = history.grid.eta[-2] + 0.25 * history.grid.dlna
    stencil = history.grid.locate(eta_query, accepted_count=history.accepted_count)
    value = stencil.evaluate(history.outgoing_virtual[10])
    assert value > 0.0
    derivative = stencil.jvp(
        history.outgoing_virtual[10],
        np.zeros(history.accepted_count),
        delta_eta=0.8 * history.grid.dlna,
    )
    expected = (
        history.outgoing_virtual[10, stencil.right_index]
        - history.outgoing_virtual[10, stencil.left_index]
    ) * 0.8
    assert derivative == pytest.approx(expected)
    with pytest.raises(FutureHistoryEndpointError):
        history.grid.locate(history.grid.eta[-1], accepted_count=history.accepted_count)


def test_one_slice_history_rejects_endpoint_and_future_before_thermal_shortcut() -> None:
    history = _synthetic_history(n=1)
    past = history.grid.locate(history.grid.eta_start - history.grid.dlna)
    assert past.thermal_zero
    with pytest.raises(FutureHistoryEndpointError):
        history.grid.locate(history.grid.eta_start)
    with pytest.raises(FutureHistoryEndpointError):
        history.grid.locate(history.grid.eta_start + 10.0 * history.grid.dlna)


def test_fixed_primal_stencil_jvp_is_homogeneous_in_direction() -> None:
    history = _synthetic_history()
    query = history.grid.eta[5] + 0.75 * history.grid.dlna
    stencil = history.grid.locate(query)
    values = history.outgoing_virtual[10]
    direction = np.linspace(-2.0, 3.0, history.accepted_count)
    delta_eta = 0.2 * history.grid.dlna
    first = stencil.jvp(values, direction, delta_eta=delta_eta)
    second = stencil.jvp(values, 2.0 * direction, delta_eta=2.0 * delta_eta)
    assert second == pytest.approx(2.0 * first, rel=2.0e-15, abs=0.0)


def test_append_reject_rollback_and_restart_are_byte_exact() -> None:
    history = _synthetic_history()
    before = history.to_bytes()
    candidate = HistoryAppendCandidate(
        accepted_index=history.accepted_count,
        eta=history.grid.eta[-1] + history.grid.dlna,
        outgoing_virtual=np.linspace(-1e-13, 2e-13, 311),
        outgoing_lyman=np.asarray([2e-14, 3e-15, 4e-16]),
        average_virtual=np.linspace(-2e-13, 1e-13, 311),
        parent_sha256=history.sha256,
    )
    assert history.reject(candidate) is history
    assert history.to_bytes() == before
    accepted = history.accept(candidate)
    assert accepted.accepted_count == history.accepted_count + 1
    rolled_back = accepted.rollback(history.accepted_count)
    assert rolled_back.to_bytes() == before
    assert AcceptedRadiationHistory.from_bytes(accepted.to_bytes()).to_bytes() == accepted.to_bytes()


@pytest.mark.slow
def test_source_history_reconstructs_all_three_c_outputs_and_coupled_step() -> None:
    data = np.load(HISTORY, allow_pickle=False)
    history = AcceptedRadiationHistory.from_npz_mapping(data)
    for target in (1300, 1100, 900):
        dae, source = _dae(target)
        prefix = history.prefix(source.iz_local)
        incoming = construct_original_hyrec_incoming(prefix, z=source.z)
        assert np.max(np.abs(incoming.virtual - source.Dfplus)) < 3.0e-25
        assert np.max(np.abs(incoming.lyman - np.asarray([source.Dfplus_Lya, source.Dfplus_Lyb]))) < 3.0e-25
        step = CausalHistoryAcceptedStepProblem(dae=dae, history=prefix).evaluate()
        assert step.native_residual_relative < 3.0e-13
        assert step.electron_rate_relative < 4.0e-13
        assert step.outgoing_virtual_relative < 5.0e-12
        assert step.outgoing_lyman_relative < 3.0e-12
        assert step.average_virtual_relative < 3.0e-12
        assert step.characteristic_number_relative < 3.0e-13
        assert step.characteristic_energy_relative < 3.0e-13
        assert step.interface_atom_source_W_per_H == 0.0
        accepted = prefix.accept(step.append_candidate)
        assert accepted.rollback(prefix.accepted_count).to_bytes() == prefix.to_bytes()


@pytest.mark.slow
def test_full_history_jvp_couples_through_algebraic_solve_and_outgoing_append() -> None:
    data = np.load(HISTORY, allow_pickle=False)
    history = AcceptedRadiationHistory.from_npz_mapping(data)
    dae, source = _dae(1100)
    prefix = history.prefix(source.iz_local)
    problem = CausalHistoryAcceptedStepProblem(dae=dae, history=prefix)
    rng = np.random.default_rng(60)
    dvirtual = rng.normal(size=prefix.outgoing_virtual.shape) * 1.0e-16
    dlyman = rng.normal(size=prefix.outgoing_lyman.shape) * 1.0e-16
    error = problem.central_difference_history_jvp_error(
        outgoing_virtual_direction=dvirtual,
        outgoing_lyman_direction=dlyman,
        step=5.0e-1,
    )
    assert error < 1.0e-10
