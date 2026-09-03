from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RESEARCH = ROOT / "research" / "rec_physical_donor_angular"
REQUIRED = (
    RESEARCH / "CONTRACT.json",
    RESEARCH / "analyze_angular_donor.py",
    RESEARCH / "verify_research_packet.py",
)


def test_research_contract_materialized_before_claims() -> None:
    missing = [str(path.relative_to(ROOT)) for path in REQUIRED if not path.is_file()]
    assert not missing, f"missing physical-donor research files: {missing}"


def test_research_contract_is_discretization_agnostic_and_fail_closed() -> None:
    contract = json.loads((RESEARCH / "CONTRACT.json").read_text(encoding="utf-8"))
    assert contract["stage_id"] == "REC_PHYSICAL_DONOR_ANGULAR_BASIS_AUDIT_R1"
    assert contract["authority_effect"] == "NONE_RESEARCH_ONLY"
    assert contract["physical_face_admitted"] is False
    assert contract["provider_export_authorized"] is False
    assert contract["angular_state_authority"] == "CONTINUOUS_OR_RECONSTRUCTIBLE_FUNCTION_ON_S2"
    assert contract["fixed_26_direction_authority"] is False
    assert set(contract["candidate_families"]) == {
        "CURRENT_26_POINT_RULE",
        "LEBEDEV_SEQUENCE",
        "SPHERICAL_HARMONIC_PN",
        "FILTERED_OR_REALIZABLE_MOMENTS",
        "ADAPTIVE_SPHERICAL_MESH",
        "HYBRID_LOW_MOMENT_PLUS_ADAPTIVE_RESIDUAL",
    }
    assert set(contract["required_benchmarks"]) == {
        "SMOOTH_QUADRUPOLE",
        "FINITE_BOOST_PATTERN",
        "NARROW_POSITIVE_BEAM",
        "HALF_RANGE_INFLOW_MASK",
        "SIGNED_DISTORTION",
        "REPOSITORY_BIANCHI_FACE_MASK",
    }
    assert contract["claim_boundary"] == (
        "RESEARCH_DONOR_ARCHITECTURE_ONLY_NO_SOURCE_IDENTICAL_FACE_PROVIDER_OR_SCIENCE_PROMOTION"
    )


def test_signed_lebedev_rules_are_inventory_only_not_positive_runtime_candidates() -> None:
    source = (RESEARCH / "analyze_angular_donor.py").read_text(encoding="utf-8")
    assert "require_positive: bool=True" in source
    assert "if self.require_positive:" in source
    assert 'return Grid(f"LEBEDEV_{o}_{len(w)}",p,w,"LEBEDEV",o,False)' in source
    assert "positive_orders=[o for o,g in lg.items() if np.all(g.w>0)]" in source
    assert "excluded_signed_candidate_orders" in source
    assert "lebedev_weight_sign_inventory" in source
    assert "no positive-weight Lebedev reference rule available" in source
