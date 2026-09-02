from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CAS_ROOT = ROOT / "formal" / "rec_next03" / "external_cas_oji"
WORKFLOW = ROOT / ".github" / "workflows" / "rec-next03-octave-jas-julia-cas.yml"

REQUIRED_FILES = (
    "CONTRACT.json",
    "octave/verify_rec_next03_symbolic.m",
    "jas/pom.xml",
    "jas/src/main/java/RecNext03JasOracle.java",
    "julia/Project.toml",
    "julia/ENVIRONMENT_LOCK.json",
    "julia/verify_rec_next03_symbolics.jl",
    "scripts/collect_engine_receipt.py",
    "scripts/verify_julia_environment_lock.py",
    "scripts/verify_external_cas_matrix.py",
    "scripts/render_external_cas_coverage.py",
)

EXPECTED_IDENTITIES = {
    "I01",
    "I02",
    "I03",
    "I04",
    "I05",
    "I06",
    "I07R",
    "I07B",
    "I07D",
    "I08",
    "I09",
    "I10",
}
EXPECTED_MUTATIONS = {
    "M01",
    "M02",
    "M03",
    "M04",
    "M05R",
    "M05B",
    "M06",
    "M07",
    "M08",
}
EXPECTED_CRITICAL_TWO_CORE = {
    "I01",
    "I03",
    "I04",
    "I06",
    "I07R",
    "I07B",
    "I07D",
    "I08",
    "I09",
}


def _contract() -> dict:
    return json.loads((CAS_ROOT / "CONTRACT.json").read_text(encoding="utf-8"))


def test_external_cas_axis_materialized() -> None:
    missing = [path for path in REQUIRED_FILES if not (CAS_ROOT / path).is_file()]
    assert not missing, f"missing external-CAS contract files: {missing}"


def test_external_cas_r2_contract_is_fail_closed() -> None:
    contract = _contract()
    assert contract["stage_id"] == "REC_NEXT03_EXTERNAL_CAS_OCTAVE_JAS_JULIA_R2"
    assert contract["authority_effect"] == "NONE"
    assert contract["required_engines"] == [
        "octave_symbolic",
        "jas",
        "julia_symbolics_nemo",
    ]
    assert set(contract["identity_catalog"]) == EXPECTED_IDENTITIES
    assert set(contract["mutation_catalog"]) == EXPECTED_MUTATIONS

    engines = contract["engine_contracts"]
    assert engines["octave_symbolic"]["counts_as_independent_algebra_core"] is False
    assert engines["jas"]["counts_as_independent_algebra_core"] is True
    assert engines["julia_symbolics_nemo"]["counts_as_independent_algebra_core"] is True
    assert engines["octave_symbolic"]["independence_class"] == (
        "SYMPY_BACKED_CROSS_LANGUAGE_WRAPPER"
    )
    assert "I03" in engines["jas"]["required_identities"]
    assert "I03" in engines["julia_symbolics_nemo"]["required_identities"]
    for engine in engines.values():
        assert {"I07R", "I07B", "I07D"}.issubset(engine["required_identities"])
        assert {"M05R", "M05B"}.issubset(engine["required_mutations"])

    acceptance = contract["aggregate_acceptance"]
    assert acceptance["minimum_independent_algebra_cores"] == 2
    assert set(acceptance["critical_identities_covered_by_both_independent_cores"]) == (
        EXPECTED_CRITICAL_TWO_CORE
    )
    assert acceptance["minimum_execution_axes_per_mutation"] == 2
    assert acceptance["exact_source_head_binding_required"] is True
    assert acceptance["julia_environment_lock_required"] is True

    static = contract["static_physics_contract"]
    assert static["small_beta_branch"] == (
        "BOUNDED_NUMERICAL_REGULARIZATION_NOT_EXACT_PARITY"
    )
    assert static["ray_parameter"] == "s=c*t; ell is reserved for angular rank"
    assert contract["claim_boundary"] == (
        "EXTERNAL_FORMULA_ORACLE_ONLY_NO_PHYSICAL_FACE_PROVIDER_OR_SCIENCE_PROMOTION"
    )


def test_suffixed_event_and_mutation_ids_are_receiptable() -> None:
    module_path = CAS_ROOT / "scripts" / "collect_engine_receipt.py"
    spec = importlib.util.spec_from_file_location("oji_receipt_collector", module_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    assert module.IDENTITY_RE.findall("IDENTITY I07R PASS\nIDENTITY I07D PASS\n") == [
        "I07R",
        "I07D",
    ]
    assert module.MUTATION_RE.findall(
        "MUTATION M05R DETECTED\nMUTATION M05B DETECTED\n"
    ) == ["M05R", "M05B"]


def test_julia_environment_lock_is_exact_and_source_bound() -> None:
    lock = json.loads(
        (CAS_ROOT / "julia" / "ENVIRONMENT_LOCK.json").read_text(encoding="utf-8")
    )
    assert lock["julia_version"] == "1.12.7"
    assert lock["packages"] == {
        "Nemo": "0.56.1",
        "SymbolicLimits": "1.2.1",
        "Symbolics": "7.39.0",
    }
    assert len(lock["project_sha256"]) == 64
    assert len(lock["manifest_sha256"]) == 64
    assert lock["source_failure_run"] == 33678531383
    assert lock["source_failure_artifact"] == 9865537045
    assert lock["authority_effect"] == "NONE"


def test_workflow_binds_receipts_to_pr_head_and_checks_julia_lock() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")
    assert "OJI_SOURCE_HEAD_SHA" in text
    assert text.count('--source-sha "$OJI_SOURCE_HEAD_SHA"') == 3
    assert '--expected-source-sha "$OJI_SOURCE_HEAD_SHA"' in text
    assert "verify_julia_environment_lock.py" in text
