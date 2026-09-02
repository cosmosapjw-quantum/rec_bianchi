from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CAS_ROOT = ROOT / "formal" / "rec_next03" / "external_cas_oji"

REQUIRED_FILES = (
    "CONTRACT.json",
    "octave/verify_rec_next03_symbolic.m",
    "jas/pom.xml",
    "jas/src/main/java/RecNext03JasOracle.java",
    "julia/Project.toml",
    "julia/verify_rec_next03_symbolics.jl",
    "scripts/collect_engine_receipt.py",
    "scripts/verify_external_cas_matrix.py",
    "scripts/render_external_cas_coverage.py",
)


def test_external_cas_axis_materialized() -> None:
    missing = [path for path in REQUIRED_FILES if not (CAS_ROOT / path).is_file()]
    assert not missing, f"missing external-CAS contract files: {missing}"


def test_external_cas_contract_is_fail_closed() -> None:
    contract_path = CAS_ROOT / "CONTRACT.json"
    assert contract_path.is_file(), "CONTRACT.json must exist before validation"
    contract = json.loads(contract_path.read_text(encoding="utf-8"))
    assert contract["stage_id"] == "REC_NEXT03_EXTERNAL_CAS_OCTAVE_JAS_JULIA_R1"
    assert contract["authority_effect"] == "NONE"
    assert contract["required_engines"] == [
        "octave_symbolic",
        "jas",
        "julia_symbolics_nemo",
    ]
    engines = contract["engine_contracts"]
    assert engines["octave_symbolic"]["counts_as_independent_algebra_core"] is False
    assert engines["jas"]["counts_as_independent_algebra_core"] is True
    assert engines["julia_symbolics_nemo"]["counts_as_independent_algebra_core"] is True
    assert engines["octave_symbolic"]["independence_class"] == (
        "SYMPY_BACKED_CROSS_LANGUAGE_WRAPPER"
    )
    assert contract["aggregate_acceptance"]["minimum_independent_algebra_cores"] == 2
    assert contract["static_physics_contract"]["small_beta_branch"] == (
        "BOUNDED_NUMERICAL_REGULARIZATION_NOT_EXACT_PARITY"
    )
    assert contract["claim_boundary"] == (
        "EXTERNAL_FORMULA_ORACLE_ONLY_NO_PHYSICAL_FACE_PROVIDER_OR_SCIENCE_PROMOTION"
    )
