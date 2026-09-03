from __future__ import annotations

import importlib.util
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CAS_ROOT = ROOT / "formal" / "rec_next03" / "external_cas_oji"
WORKFLOW = ROOT / ".github" / "workflows" / "rec-next03-octave-jas-julia-cas.yml"
COLLECTOR = CAS_ROOT / "scripts" / "collect_engine_receipt.py"

EVENT_IDENTITIES = {"I07H", "I07R", "I07B", "I07D", "I07J"}
EVENT_MUTATIONS = {"M05H", "M05R", "M05B", "M05D", "M05J"}


def _contract() -> dict:
    return json.loads((CAS_ROOT / "CONTRACT.json").read_text(encoding="utf-8"))


def _source(relative: str) -> str:
    return (CAS_ROOT / relative).read_text(encoding="utf-8")


def test_r3_contract_requires_event_transversality_on_every_engine() -> None:
    contract = _contract()
    assert contract["stage_id"] == "REC_NEXT03_EXTERNAL_CAS_OCTAVE_JAS_JULIA_R3"
    assert EVENT_IDENTITIES.issubset(contract["identity_catalog"])
    assert EVENT_MUTATIONS.issubset(contract["mutation_catalog"])
    assert "I07" not in contract["identity_catalog"]
    assert "M05" not in contract["mutation_catalog"]

    for engine in contract["required_engines"]:
        engine_contract = contract["engine_contracts"][engine]
        assert EVENT_IDENTITIES.issubset(engine_contract["required_identities"])
        assert EVENT_MUTATIONS.issubset(engine_contract["required_mutations"])

    critical = set(
        contract["aggregate_acceptance"]
        ["critical_identities_covered_by_both_independent_cores"]
    )
    assert {"I03", *EVENT_IDENTITIES}.issubset(critical)


def test_collector_receipts_support_suffixed_event_ids() -> None:
    spec = importlib.util.spec_from_file_location("oji_receipt_collector", COLLECTOR)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    identity_log = "\n".join(f"IDENTITY {item} PASS" for item in sorted(EVENT_IDENTITIES))
    mutation_log = "\n".join(
        f"MUTATION {item} DETECTED" for item in sorted(EVENT_MUTATIONS)
    )
    assert set(module.IDENTITY_RE.findall(identity_log)) == EVENT_IDENTITIES
    assert set(module.MUTATION_RE.findall(mutation_log)) == EVENT_MUTATIONS


def test_jas_and_julia_are_independent_i03_cores() -> None:
    contract = _contract()
    engines = contract["engine_contracts"]
    assert "I03" in engines["jas"]["required_identities"]
    assert "I03" in engines["julia_symbolics_nemo"]["required_identities"]

    jas = _source("jas/src/main/java/RecNext03JasOracle.java")
    julia = _source("julia/verify_rec_next03_symbolics.jl")
    assert 'identity("I03"' in jas
    assert 'identity("I03"' in julia


def test_event_jacobian_rank_theorem_is_materialized_on_all_axes() -> None:
    sources = {
        "octave": _source("octave/verify_rec_next03_symbolic.m"),
        "jas": _source("jas/src/main/java/RecNext03JasOracle.java"),
        "julia": _source("julia/verify_rec_next03_symbolics.jl"),
    }
    for engine, source in sources.items():
        assert "I07J" in source, f"{engine} missing event-Jacobian identity"
        assert "M05J" in source, f"{engine} missing rank-collapse mutation"
        assert re.search(r"[Dd]elta\s*\^\s*2|delta\^2", source), (
            f"{engine} must retain the exact det(J)=Delta^2 theorem"
        )


def test_event_mutations_are_tied_to_reconstructed_event_functions() -> None:
    octave = _source("octave/verify_rec_next03_symbolic.m")
    jas = _source("jas/src/main/java/RecNext03JasOracle.java")
    julia = _source("julia/verify_rec_next03_symbolics.jl")

    for mutation in EVENT_MUTATIONS:
        assert mutation in octave
        assert mutation in jas
        assert mutation in julia

    # A hostile control must not be a renamed assertion that a numeric constant
    # is nonzero. It must use a reconstructed event function or Jacobian.
    assert 'require_nonzero("M05B", sym(1))' not in octave
    assert 'require_nonzero("M05R", sym(-1))' not in octave
    assert not re.search(r'mutation\("M05[A-Z]",\s*"[-+]?\d+"\)', jas)
    assert 'mutation("M05B", onep != 0)' not in julia
    assert 'mutation("M05R", onep != 0)' not in julia

    for token in (
        "hubble_zero_witness",
        "red_zero_witness",
        "blue_zero_witness",
        "event_jacobian",
        "mutated_event_jacobian",
    ):
        assert token in julia, f"Julia oracle missing reconstructed object {token}"


def test_r3_preserves_c1_manifest_and_dual_event_provenance() -> None:
    contract = _contract()
    lock = contract["julia_environment_lock"]
    assert lock["julia_version"] == "1.12.7"
    assert lock["project_sha256"] == (
        "596a97233fc57b0251aa3517b080c583d971e0bd0c79ae13eafc128ed1a1cce2"
    )
    assert lock["manifest_sha256"] == (
        "e5eaab5c224dddd81c02e5fc798f1d631e6f71be1adf3c1c974bafa07d88e5bf"
    )

    provenance = contract["provenance_contract"]
    assert provenance["legacy_source_sha_field_forbidden"] is True
    workflow = WORKFLOW.read_text(encoding="utf-8")
    assert "REC_SOURCE_HEAD_SHA" in workflow
    assert "REC_WORKFLOW_SHA" in workflow
    assert "REC_WORKFLOW_TRIGGER" in workflow
    assert "--source-sha" not in workflow
    assert "Pkg.instantiate()" in workflow
    assert "git diff --exit-code --" in workflow
