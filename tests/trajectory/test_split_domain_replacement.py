from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pytest
from scipy.constants import electron_volt

from full_bianchi_hyrec.recoil.original_hyrec_native import NVIRT
from full_bianchi_hyrec.recoil.original_hyrec_physical_flux import (
    outgoing_distortion,
    parse_original_hyrec_boundary_snapshot_csv,
    reconstruct_equilibrium_distortion,
    spectral_source_moments_Hz,
    transport_edge_flux_per_H_s,
)
from full_bianchi_hyrec.trajectory.dynamic_macro_ownership import (
    audit_dynamic_atomic_macro_ownership,
    implemented_split_domain_ownership_config,
    resolved_split_domain_contract_witness,
)
from full_bianchi_hyrec.trajectory.primitive_rates import LYMAN_ALPHA_ENERGY_EV


try:
    from full_bianchi_hyrec.trajectory.split_domain_replacement import (
        SplitDomainContext,
        SplitDomainInterfaceEntry,
        SplitDomainLedger,
        SplitDomainRegistry,
        SplitDomainReplacement,
    )
except ImportError:
    SplitDomainContext = None
    SplitDomainInterfaceEntry = None
    SplitDomainLedger = None
    SplitDomainRegistry = None
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
INHERITED_DENSE_SOLVE_RELATIVE_LIMIT = 5.0e-13


def _parsed():
    return parse_original_hyrec_boundary_snapshot_csv(SOURCE)


def _history_sha256_for_test(dfplus, dfminus) -> str:
    digest = hashlib.sha256()
    for value in (dfplus, dfminus):
        digest.update(np.asarray(value, dtype="<f8").tobytes(order="C"))
    return digest.hexdigest()


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
    direct_full_state = np.linalg.solve(matrix, right_hand_side)
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
    return (
        schur,
        reduced_rhs,
        exterior,
        interior,
        direct_full_state[exterior],
        direct_full_state,
    )


def _independent_matrix_without_interface(snapshot):
    matrix, right_hand_side = _independent_dense_primitive(snapshot)
    for left, right in CROSS_EDGES:
        left_full = 2 + left
        right_full = 2 + right
        matrix[left_full, left_full] -= snapshot.Aup_s_inv[left]
        matrix[right_full, right_full] -= snapshot.Adn_s_inv[right]
        matrix[right_full, left_full] = 0.0
        matrix[left_full, right_full] = 0.0
    return matrix, right_hand_side


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

    state_relative = np.linalg.norm(candidate_full - direct_full, ord=np.inf) / max(
        np.linalg.norm(direct_full, ord=np.inf), 1.0e-300
    )
    direct_equilibrium = reconstruct_equilibrium_distortion(snapshot, direct_full)
    candidate_equilibrium = reconstruct_equilibrium_distortion(snapshot, candidate_full)
    direct_flux = transport_edge_flux_per_H_s(
        snapshot,
        outgoing=outgoing_distortion(
            snapshot.Dfplus,
            direct_equilibrium,
            snapshot.Dtau,
            source_branch=True,
        ),
    )
    candidate_flux = transport_edge_flux_per_H_s(
        snapshot,
        outgoing=outgoing_distortion(
            snapshot.Dfplus,
            candidate_equilibrium,
            snapshot.Dtau,
            source_branch=True,
        ),
    )
    direct_observables = spectral_source_moments_Hz(
        direct_flux, snapshot.frequency_Hz
    )
    candidate_observables = spectral_source_moments_Hz(
        candidate_flux, snapshot.frequency_Hz
    )
    observable_relative = np.linalg.norm(
        candidate_observables - direct_observables, ord=np.inf
    ) / max(np.linalg.norm(direct_observables, ord=np.inf), 1.0e-300)
    assert state_relative < 3.0e-12
    assert observable_relative < 3.0e-12


def test_conditioning_and_operator_residual_are_reported_separately() -> None:
    parsed = _parsed()
    schur, reduced_rhs, _, _, _, _ = _independent_exterior_schur(
        parsed.trajectory
    )
    replacement = _replacement_or_none(parsed)
    assert replacement is not None
    context = SplitDomainContext()
    solution = replacement.solve(context)
    condition_number = replacement.operator_condition_number(context)
    normalized_residual = replacement.operator_residual(
        solution.exterior_state, context
    )
    independent_condition_number = float(np.linalg.cond(schur))
    independent_residual = np.linalg.norm(
        schur @ solution.exterior_state - reduced_rhs, ord=np.inf
    ) / max(
        np.linalg.norm(schur, ord=np.inf)
        * np.linalg.norm(solution.exterior_state, ord=np.inf)
        + np.linalg.norm(reduced_rhs, ord=np.inf),
        1.0e-300,
    )
    assert np.isfinite(condition_number)
    assert condition_number >= 1.0
    assert abs(condition_number - independent_condition_number) / (
        independent_condition_number
    ) < 2.0e-14
    assert normalized_residual < INHERITED_DENSE_SOLVE_RELATIVE_LIMIT
    assert independent_residual < INHERITED_DENSE_SOLVE_RELATIVE_LIMIT


def test_interior_atomic_deposition_is_source_exact_and_nonnegative_as_rates() -> None:
    parsed = _parsed()
    replacement = _replacement_or_none(parsed)
    assert replacement is not None
    indices = np.asarray(INTERIOR_NATIVE_INDICES)
    real_to_com = replacement.interior_atomic_real_to_com
    com_to_real = replacement.interior_atomic_com_to_real
    assert np.array_equal(real_to_com, parsed.trajectory.Tvr[:, indices].T)
    assert np.array_equal(com_to_real, parsed.trajectory.Trv[:, indices])
    assert np.all(-real_to_com >= 0.0)
    assert np.all(-com_to_real >= 0.0)


def test_interface_off_and_flrw_limit_match_independent_expected_actions() -> None:
    parsed = _parsed()
    replacement = _replacement_or_none(parsed)
    assert replacement is not None
    matrix_off, right_hand_side = _independent_matrix_without_interface(
        parsed.trajectory
    )
    direct_off = np.linalg.solve(matrix_off, right_hand_side)
    off_context = SplitDomainContext(interface_enabled=False)
    candidate_off = replacement.solve(off_context)
    state_relative = np.linalg.norm(
        candidate_off.full_state - direct_off, ord=np.inf
    ) / max(np.linalg.norm(direct_off, ord=np.inf), 1.0e-300)
    assert state_relative < 3.0e-12
    off_ledger = replacement.ledger(candidate_off.exterior_state, off_context)
    assert off_ledger.entries == ()
    assert off_ledger.number_residual_per_H_s == 0.0
    assert off_ledger.photon_energy_residual_W_per_H == 0.0

    ordinary = replacement.solve(SplitDomainContext())
    flrw = replacement.solve(SplitDomainContext(flrw_limit=True))
    assert np.array_equal(flrw.exterior_state, ordinary.exterior_state)
    assert np.array_equal(flrw.interior_com_state, ordinary.interior_com_state)
    assert np.array_equal(flrw.full_state, ordinary.full_state)


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
        assert tuple(entry.edge for entry in ledger.entries) == CROSS_EDGES
        for entry, (left, right) in zip(ledger.entries, CROSS_EDGES, strict=True):
            pair_flux = (
                parsed.trajectory.Aup_s_inv[left] * solution.full_state[2 + left]
                - parsed.trajectory.Adn_s_inv[right] * solution.full_state[2 + right]
            )
            expected_native_number = (
                pair_flux if left in INTERIOR_NATIVE_INDICES else -pair_flux
            )
            sign_x = 1.0 if left in INTERIOR_NATIVE_INDICES else -1.0
            expected_energy = (
                (LYMAN_ALPHA_ENERGY_EV + sign_x * 21.25 * parsed.boundaries[0].doppler_width_eV)
                * parsed.trajectory.fsR**2
                * parsed.trajectory.meR
                * electron_volt
            )
            assert entry.native_number_flux_per_H_s == expected_native_number
            assert entry.com_number_flux_per_H_s == -expected_native_number
            assert entry.interface_energy_J == expected_energy
            assert entry.native_photon_energy_flux_W_per_H == (
                expected_native_number * expected_energy
            )
            assert entry.com_photon_energy_flux_W_per_H == (
                -expected_native_number * expected_energy
            )
            assert np.array_equal(
                entry.native_four_force_W_per_H,
                np.asarray(
                    (entry.native_photon_energy_flux_W_per_H, 0.0, 0.0, 0.0)
                ),
            )
            assert np.array_equal(
                entry.com_four_force_W_per_H, -entry.native_four_force_W_per_H
            )
            assert entry.atom_source_W_per_H == 0.0
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
    replacement = _replacement_or_none(parsed)
    if replacement is None:
        _, _, _, _, exterior_state, _ = _independent_exterior_schur(
            parsed.trajectory
        )
        restored_state = np.zeros_like(exterior_state)
        restored_history = np.zeros_like(parsed.trajectory.Dfplus)
        restored_residual = np.ones_like(exterior_state)
    else:
        exterior_state = replacement.solve(SplitDomainContext()).exterior_state
        encoded = json.loads(json.dumps(replacement.restart_record()))
        restored = replacement.state_from_restart_record(encoded)
        assert set(encoded) == {
            "schema",
            "source_z",
            "source_index",
            "context",
            "registry",
            "registry_sha256",
            "exterior_state",
            "interior_com_state",
            "full_state",
            "history_Dfplus",
            "history_Dfminus",
            "history_sha256",
        }
        assert encoded["context"] == {
            "interface_enabled": True,
            "flrw_limit": False,
        }
        restored_state = restored.exterior_state
        restored_history = restored.history_Dfplus
        assert np.array_equal(
            restored.history_Dfminus, parsed.trajectory.Dfminus
        )
        restored_residual = replacement.residual(
            restored_state, SplitDomainContext()
        )

    assert np.array_equal(restored_state, exterior_state)
    assert np.array_equal(restored_history, parsed.trajectory.Dfplus)
    assert np.linalg.norm(restored_residual, ord=np.inf) < 2.0e-24


def test_preregistered_owner_interface_and_ledger_mutants_are_rejected() -> None:
    parsed = _parsed()
    replacement = _replacement_or_none(parsed)
    assert replacement is not None
    assert SplitDomainRegistry is not None
    assert SplitDomainInterfaceEntry is not None
    assert SplitDomainLedger is not None

    double_owner = SplitDomainRegistry(
        interior_indices=INTERIOR_NATIVE_INDICES,
        cross_edges=CROSS_EDGES,
        process_owners=replacement.registry.process_owners
        + (("cross_edge_135_136", "exterior_native"),),
        implementation_evidence=True,
    ).audit()
    assert double_owner.overlap_count == 1
    assert not double_owner.implementation_evidence

    unowned_edge = SplitDomainRegistry(
        interior_indices=INTERIOR_NATIVE_INDICES,
        cross_edges=CROSS_EDGES,
        process_owners=tuple(
            item
            for item in replacement.registry.process_owners
            if item[0] != "cross_edge_143_144"
        ),
        implementation_evidence=True,
    ).audit()
    assert unowned_edge.unowned_process_count == 1
    assert unowned_edge.cross_edge_count == 1
    assert not unowned_edge.implementation_evidence

    solution = replacement.solve(SplitDomainContext())
    ledger = replacement.ledger(solution.exterior_state, SplitDomainContext())
    entry = ledger.entries[0]
    with pytest.raises(ValueError, match="wrong number-flux sign"):
        SplitDomainInterfaceEntry(
            edge=entry.edge,
            side=entry.side,
            interface_energy_J=entry.interface_energy_J,
            native_number_flux_per_H_s=entry.native_number_flux_per_H_s,
            com_number_flux_per_H_s=entry.com_number_flux_per_H_s,
            native_photon_energy_flux_W_per_H=-entry.native_photon_energy_flux_W_per_H,
            com_photon_energy_flux_W_per_H=-entry.com_photon_energy_flux_W_per_H,
            native_four_force_W_per_H=-entry.native_four_force_W_per_H,
            com_four_force_W_per_H=-entry.com_four_force_W_per_H,
            atom_source_W_per_H=0.0,
        )

    with pytest.raises(ValueError, match="zero or two"):
        SplitDomainLedger(
            entries=(entry,),
            native_number_flux_per_H_s=entry.native_number_flux_per_H_s,
            com_number_flux_per_H_s=entry.com_number_flux_per_H_s,
            native_photon_energy_flux_W_per_H=entry.native_photon_energy_flux_W_per_H,
            com_photon_energy_flux_W_per_H=entry.com_photon_energy_flux_W_per_H,
            native_four_force_W_per_H=entry.native_four_force_W_per_H,
            com_four_force_W_per_H=entry.com_four_force_W_per_H,
            atom_source_W_per_H=0.0,
        )


def test_restart_rejects_context_and_history_mutants() -> None:
    parsed = _parsed()
    replacement = _replacement_or_none(parsed)
    assert replacement is not None
    record = replacement.restart_record()

    context_mutant = json.loads(json.dumps(record))
    context_mutant["context"]["interface_enabled"] = False
    with pytest.raises(ValueError, match="context"):
        replacement.state_from_restart_record(context_mutant)

    history_mutant = json.loads(json.dumps(record))
    history_mutant["history_Dfplus"][136] += 1.0e-18
    history_mutant["history_sha256"] = _history_sha256_for_test(
        history_mutant["history_Dfplus"], history_mutant["history_Dfminus"]
    )
    with pytest.raises(ValueError, match="Dfplus history"):
        replacement.state_from_restart_record(history_mutant)
