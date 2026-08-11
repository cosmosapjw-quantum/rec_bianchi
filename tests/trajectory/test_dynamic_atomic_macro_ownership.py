from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from full_bianchi_hyrec.recoil.original_hyrec_physical_flux import (
    parse_original_hyrec_boundary_snapshot_csv,
)
from full_bianchi_hyrec.trajectory.dynamic_macro_ownership import (
    DynamicMacroOwnershipError,
    DynamicMacroOwnershipConfig,
    audit_dynamic_atomic_macro_ownership,
    current_v074_ownership_config,
    naive_dynamic_atomic_ownership_config,
    require_dynamic_atomic_macro_ready,
    resolved_split_domain_contract_witness,
)


ROOT = Path(__file__).resolve().parents[2]
SOURCE = (
    ROOT
    / "archive/expanded/Full_Bianchi_HyRec_PR04C0C1A_split_domain_boundary_v0_55"
    / "pr04c_z1100.csv"
)


def _audit(config: DynamicMacroOwnershipConfig):
    parsed = parse_original_hyrec_boundary_snapshot_csv(SOURCE)
    return audit_dynamic_atomic_macro_ownership(
        parsed.trajectory,
        doppler_width_eV=parsed.boundaries[0].doppler_width_eV,
        config=config,
    )


def test_z1100_native_support_overlaps_the_com_domain() -> None:
    audit = _audit(current_v074_ownership_config())
    assert audit.native_virtual_count == 311
    assert audit.com_interior_native_count == 8
    assert audit.com_interior_native_indices == tuple(range(136, 144))
    assert audit.diffusion_inside_edge_count == 6
    assert audit.diffusion_cross_edge_count == 2
    assert audit.diffusion_cross_edges == ((135, 136), (143, 144))
    assert audit.diffusion_outside_edge_count == 70
    assert audit.minimum_interior_x > -21.25
    assert audit.maximum_interior_x < 21.25
    assert audit.left_exterior_x < -21.25
    assert audit.right_exterior_x > 21.25


def test_canonical_real_virtual_rates_are_dominated_by_the_com_interior() -> None:
    audit = _audit(current_v074_ownership_config())
    assert audit.canonical_up_rate_interior_fraction > 0.97
    assert audit.canonical_down_rate_interior_fraction > 0.97
    assert audit.real_to_virtual_abs_interior_fraction > 0.90
    assert audit.virtual_to_real_abs_interior_fraction > 0.90
    assert np.isfinite(audit.diffusion_cross_rate_s_inv)
    assert audit.diffusion_cross_rate_s_inv > 0.0


def test_v074_configuration_is_not_admissible_for_dynamic_atomic_coupling() -> None:
    audit = _audit(current_v074_ownership_config())
    assert not audit.dynamic_atomic_macro_ready
    assert "native_A1s_diffusion_inside" in audit.unresolved_processes
    assert "completed_Tvv_inside" in audit.unresolved_processes
    with pytest.raises(DynamicMacroOwnershipError, match="not admissible"):
        require_dynamic_atomic_macro_ready(audit)


def test_naive_atomic_source_coupling_adds_a_second_overlap() -> None:
    audit = _audit(naive_dynamic_atomic_ownership_config())
    assert not audit.dynamic_atomic_macro_ready
    assert "atomic_real_virtual_source_inside" in audit.unresolved_processes
    assert audit.overlap_count >= 3


def test_contract_witness_cannot_authorize_production_dynamic_macro() -> None:
    audit = _audit(resolved_split_domain_contract_witness())
    assert audit.dynamic_atomic_macro_ready
    assert audit.overlap_count == 0
    assert audit.unowned_process_count == 0
    assert audit.unresolved_processes == ()
    assert audit.cross_edge_owner == "split_domain_interface"
    assert audit.scalar_history_owner == "typed_characteristic_history"
    assert audit.contract_witness_only
    with pytest.raises(DynamicMacroOwnershipError, match="contract witness"):
        require_dynamic_atomic_macro_ready(audit)


def test_unknown_or_multi_owner_configuration_fails_closed() -> None:
    base = resolved_split_domain_contract_witness()
    with pytest.raises(ValueError, match="owner"):
        DynamicMacroOwnershipConfig(
            native_diffusion_support=base.native_diffusion_support,
            com_collision_support=base.com_collision_support,
            native_atomic_source_support=base.native_atomic_source_support,
            com_atomic_source_support=base.com_atomic_source_support,
            completed_tvv_support=base.completed_tvv_support,
            cross_edge_owner="native+interface",
            scalar_history_owner=base.scalar_history_owner,
            replacement_complete=True,
            contract_witness_only=True,
        )
