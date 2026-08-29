from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from full_bianchi_hyrec.recoil.original_hyrec_native import NVIRT
from full_bianchi_hyrec.recoil.original_hyrec_physical_flux import (
    parse_original_hyrec_boundary_snapshot_csv,
)
from full_bianchi_hyrec.trajectory.dynamic_macro_ownership import (
    audit_dynamic_atomic_macro_ownership,
    implemented_split_domain_ownership_config,
    resolved_split_domain_contract_witness,
)


try:
    from full_bianchi_hyrec.trajectory.split_domain_replacement import (
        SplitDomainContext,
        SplitDomainReplacement,
    )
except ImportError:
    SplitDomainContext = None
    SplitDomainReplacement = None


ROOT = Path(__file__).resolve().parents[2]
SOURCE = (
    ROOT
    / "archive/expanded/Full_Bianchi_HyRec_PR04C0C1A_split_domain_boundary_v0_55"
    / "pr04c_z1100.csv"
)
INTERIOR_NATIVE_INDICES = tuple(range(136, 144))
CROSS_EDGES = ((135, 136), (143, 144))
DIRECTIONAL_DERIVATIVE_SCHEDULE = (
    ("central", 1.0e-4),
    ("central", 3.0e-5),
    ("central", 1.0e-5),
    ("complex", 1.0e-30),
)


def _parsed():
    return parse_original_hyrec_boundary_snapshot_csv(SOURCE)


def _independent_dense_primitive(snapshot) -> tuple[np.ndarray, np.ndarray]:
    """Test-only dense primitive assembly independent of production helpers."""

    matrix = np.zeros((2 + NVIRT, 2 + NVIRT), dtype=float)
    matrix[:2, :2] = snapshot.Trr
    matrix[:2, 2:] = snapshot.Trv
    matrix[2:, :2] = snapshot.Tvr.T
    matrix[2:, 2:] = np.diag(snapshot.Tvv[0])
    rows = np.arange(NVIRT - 1)
    matrix[2 + rows, 3 + rows] = snapshot.Tvv[2, :-1]
    matrix[3 + rows, 2 + rows] = snapshot.Tvv[1, 1:]
    right_hand_side = np.concatenate((snapshot.sr, snapshot.sv))
    return matrix, right_hand_side


def _independent_exterior_schur(snapshot):
    matrix, right_hand_side = _independent_dense_primitive(snapshot)
    interior = np.asarray([2 + index for index in INTERIOR_NATIVE_INDICES])
    exterior = np.asarray(
        [index for index in range(2 + NVIRT) if index not in set(interior)]
    )
    a_ee = matrix[np.ix_(exterior, exterior)]
    a_ei = matrix[np.ix_(exterior, interior)]
    a_ie = matrix[np.ix_(interior, exterior)]
    a_ii = matrix[np.ix_(interior, interior)]
    inverse_a_ie = np.linalg.solve(a_ii, a_ie)
    inverse_b_i = np.linalg.solve(a_ii, right_hand_side[interior])
    schur = a_ee - a_ei @ inverse_a_ie
    reduced_rhs = right_hand_side[exterior] - a_ei @ inverse_b_i
    exterior_state = np.linalg.solve(schur, reduced_rhs)
    interior_state = inverse_b_i - inverse_a_ie @ exterior_state
    full_state = np.empty(2 + NVIRT)
    full_state[exterior] = exterior_state
    full_state[interior] = interior_state
    return schur, reduced_rhs, exterior, interior, exterior_state, full_state


def _replacement_or_none(parsed):
    if SplitDomainReplacement is None:
        return None
    return SplitDomainReplacement.from_snapshot(
        parsed.trajectory,
        doppler_width_eV=parsed.boundaries[0].doppler_width_eV,
        interface_abs_x=21.25,
    )


def test_exact_owner_swap_is_implementation_evidence_not_a_witness() -> None:
    parsed = _parsed()
    replacement = _replacement_or_none(parsed)
    if replacement is None:
        audit = audit_dynamic_atomic_macro_ownership(
            parsed.trajectory,
            doppler_width_eV=parsed.boundaries[0].doppler_width_eV,
            config=resolved_split_domain_contract_witness(),
        )
        interior_indices = audit.com_interior_native_indices
        cross_edges = audit.diffusion_cross_edges
        overlap_count = audit.overlap_count
        unowned_process_count = audit.unowned_process_count
        implementation_evidence = not audit.contract_witness_only
    else:
        audit = replacement.registry.audit()
        interior_indices = replacement.registry.interior_indices
        cross_edges = replacement.registry.cross_edges
        overlap_count = audit.overlap_count
        unowned_process_count = audit.unowned_process_count
        implementation_evidence = audit.implementation_evidence

    assert interior_indices == INTERIOR_NATIVE_INDICES
    assert cross_edges == CROSS_EDGES
    assert overlap_count == 0
    assert unowned_process_count == 0
    assert implementation_evidence

    production_audit = audit_dynamic_atomic_macro_ownership(
        parsed.trajectory,
        doppler_width_eV=parsed.boundaries[0].doppler_width_eV,
        config=implemented_split_domain_ownership_config(),
    )
    assert production_audit.com_interior_native_indices == INTERIOR_NATIVE_INDICES
    assert production_audit.diffusion_cross_edges == CROSS_EDGES
    assert production_audit.overlap_count == 0
    assert production_audit.unowned_process_count == 0
    assert production_audit.dynamic_atomic_macro_ready
    assert not production_audit.contract_witness_only


def test_exterior_schur_state_and_observables_match_independent_dense_primitive() -> None:
    parsed = _parsed()
    snapshot = parsed.trajectory
    _, _, _, _, _, direct_full = _independent_exterior_schur(snapshot)
    replacement = _replacement_or_none(parsed)
    if replacement is None:
        candidate_full = np.zeros_like(direct_full)
    else:
        candidate_full = replacement.solve(SplitDomainContext()).full_state

    selected = np.asarray((0, 1, 2 + 135, 2 + 136, 2 + 143, 2 + 144))
    state_relative = np.linalg.norm(candidate_full - direct_full, ord=np.inf) / max(
        np.linalg.norm(direct_full, ord=np.inf), 1.0e-300
    )
    observable_relative = np.linalg.norm(
        candidate_full[selected] - direct_full[selected], ord=np.inf
    ) / max(np.linalg.norm(direct_full[selected], ord=np.inf), 1.0e-300)
    assert state_relative < 3.0e-12
    assert observable_relative < 3.0e-12


def test_interface_ledger_closes_number_energy_four_force_and_atom_source() -> None:
    parsed = _parsed()
    replacement = _replacement_or_none(parsed)
    if replacement is None:
        number_residual = 1.0
        energy_residual = 1.0
        four_force_residual = np.ones(4)
        atom_source = 1.0
    else:
        solution = replacement.solve(SplitDomainContext())
        ledger = replacement.ledger(solution.exterior_state, SplitDomainContext())
        number_residual = ledger.number_residual_per_H_s
        energy_residual = ledger.photon_energy_residual_W_per_H
        four_force_residual = ledger.four_force_residual_W_per_H
        atom_source = ledger.atom_source_W_per_H

    assert number_residual == 0.0
    assert energy_residual == 0.0
    assert np.array_equal(four_force_residual, np.zeros(4))
    assert atom_source == 0.0


def test_analytic_jvp_matches_preregistered_independent_directional_schedule() -> None:
    parsed = _parsed()
    snapshot = parsed.trajectory
    schur, reduced_rhs, _, _, state, _ = _independent_exterior_schur(snapshot)
    direction = np.sin(np.arange(state.size, dtype=float) + 0.5)
    direction /= np.linalg.norm(direction, ord=np.inf)
    replacement = _replacement_or_none(parsed)
    analytic = (
        np.zeros_like(direction)
        if replacement is None
        else replacement.jvp(state, direction, SplitDomainContext())
    )

    def independent_residual(value):
        return schur @ value - reduced_rhs

    for method, epsilon in DIRECTIONAL_DERIVATIVE_SCHEDULE:
        if method == "central":
            finite = (
                independent_residual(state + epsilon * direction)
                - independent_residual(state - epsilon * direction)
            ) / (2.0 * epsilon)
        else:
            finite = np.imag(
                independent_residual(state.astype(complex) + 1j * epsilon * direction)
            ) / epsilon
        relative = np.linalg.norm(analytic - finite, ord=np.inf) / max(
            np.linalg.norm(finite, ord=np.inf), 1.0e-300
        )
        assert relative < 2.0e-10, (method, epsilon, relative)


def test_restart_and_history_round_trip_preserves_state_and_residual() -> None:
    parsed = _parsed()
    _, _, _, _, exterior_state, _ = _independent_exterior_schur(parsed.trajectory)
    replacement = _replacement_or_none(parsed)
    if replacement is None:
        restored_state = np.zeros_like(exterior_state)
        restored_history = np.zeros_like(parsed.trajectory.Dfplus)
        restored_residual = np.ones_like(exterior_state)
    else:
        encoded = json.loads(json.dumps(replacement.restart_record()))
        restored = replacement.state_from_restart_record(encoded)
        restored_state = restored.exterior_state
        restored_history = restored.history_Dfplus
        restored_residual = replacement.residual(
            restored_state, SplitDomainContext()
        )

    assert np.array_equal(restored_state, exterior_state)
    assert np.array_equal(restored_history, parsed.trajectory.Dfplus)
    assert np.linalg.norm(restored_residual, ord=np.inf) < 2.0e-24
