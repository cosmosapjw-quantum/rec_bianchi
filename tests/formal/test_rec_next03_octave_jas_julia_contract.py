from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
CAS_ROOT = ROOT / "formal" / "rec_next03" / "external_cas_oji"
JULIA_ROOT = CAS_ROOT / "julia"
COLLECTOR = CAS_ROOT / "scripts" / "collect_engine_receipt.py"
AGGREGATOR = CAS_ROOT / "scripts" / "verify_external_cas_matrix.py"
JULIA_LOCK_VERIFIER = CAS_ROOT / "scripts" / "verify_julia_environment_lock.py"
WORKFLOW = ROOT / ".github" / "workflows" / "rec-next03-octave-jas-julia-cas.yml"

REQUIRED_FILES = (
    "CONTRACT.json",
    "octave/verify_rec_next03_symbolic.m",
    "jas/pom.xml",
    "jas/src/main/java/RecNext03JasOracle.java",
    "julia/Project.toml",
    "julia/Manifest.toml",
    "julia/verify_rec_next03_symbolics.jl",
    "scripts/collect_engine_receipt.py",
    "scripts/verify_external_cas_matrix.py",
    "scripts/verify_julia_environment_lock.py",
    "scripts/render_external_cas_coverage.py",
)

SOURCE_HEAD_SHA = "1" * 40
WORKFLOW_SHA = "2" * 40


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write_minimal_contract(path: Path) -> Path:
    engines = ["engine_a", "engine_b", "engine_c"]
    contract = {
        "stage_id": "TEST_PROVENANCE",
        "claim_boundary": "TEST_ONLY",
        "required_engines": engines,
        "engine_contracts": {
            engine: {
                "independence_class": f"INDEPENDENT_TEST_CORE_{index}",
                "counts_as_independent_algebra_core": True,
                "required_identities": ["I01"],
                "required_mutations": ["M01"],
            }
            for index, engine in enumerate(engines)
        },
        "identity_catalog": {"I01": "test identity"},
        "mutation_catalog": {"M01": "test mutation"},
        "aggregate_acceptance": {
            "minimum_independent_algebra_cores": 2,
            "critical_identities_covered_by_both_independent_cores": ["I01"],
            "minimum_execution_axes_per_mutation": 2,
        },
    }
    path.write_text(json.dumps(contract), encoding="utf-8")
    return path


def _write_engine_receipt(
    root: Path,
    *,
    engine: str,
    index: int,
    source_head_sha: str = SOURCE_HEAD_SHA,
    workflow_sha: str = WORKFLOW_SHA,
    trigger: str = "pull_request",
) -> None:
    destination = root / engine
    destination.mkdir(parents=True, exist_ok=True)
    receipt = {
        "engine": engine,
        "status": "PASS",
        "authority_effect": "NONE",
        "independence_class": f"INDEPENDENT_TEST_CORE_{index}",
        "counts_as_independent_algebra_core": True,
        "version": "test-version",
        "package_hashes": [{"sha256": "3" * 64, "artifact": "test-package"}],
        "identities": ["I01"],
        "mutations": ["M01"],
        "source_head_sha": source_head_sha,
        "workflow_sha": workflow_sha,
        "trigger": trigger,
    }
    (destination / "receipt.json").write_text(
        json.dumps(receipt), encoding="utf-8"
    )


def _run_aggregate(
    *,
    contract: Path,
    receipts_root: Path,
    output: Path,
    expected_source_head_sha: str = SOURCE_HEAD_SHA,
    expected_workflow_sha: str = WORKFLOW_SHA,
    expected_trigger: str = "pull_request",
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            str(AGGREGATOR),
            "--contract",
            str(contract),
            "--receipts-root",
            str(receipts_root),
            "--output",
            str(output),
            "--expected-source-head-sha",
            expected_source_head_sha,
            "--expected-workflow-sha",
            expected_workflow_sha,
            "--expected-trigger",
            expected_trigger,
        ],
        check=False,
        capture_output=True,
        text=True,
    )


def _run_julia_lock_verifier(
    *,
    contract: Path,
    project: Path,
    manifest: Path,
    output: Path,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            str(JULIA_LOCK_VERIFIER),
            "--contract",
            str(contract),
            "--project",
            str(project),
            "--manifest",
            str(manifest),
            "--output",
            str(output),
        ],
        check=False,
        capture_output=True,
        text=True,
    )


def _replace_manifest_package_field(
    text: str,
    *,
    package: str,
    field: str,
    replacement: str,
) -> str:
    pattern = re.compile(
        rf'(\[\[deps\.{re.escape(package)}\]\].*?^{re.escape(field)} = ")[^"]+("$)',
        flags=re.MULTILINE | re.DOTALL,
    )
    mutated, count = pattern.subn(rf"\g<1>{replacement}\g<2>", text, count=1)
    assert count == 1, f"unable to mutate {package}.{field}"
    return mutated


def test_external_cas_axis_materialized() -> None:
    missing = [path for path in REQUIRED_FILES if not (CAS_ROOT / path).is_file()]
    assert not missing, f"missing external-CAS contract files: {missing}"


def test_external_cas_contract_is_fail_closed() -> None:
    contract_path = CAS_ROOT / "CONTRACT.json"
    assert contract_path.is_file(), "CONTRACT.json must exist before validation"
    contract = json.loads(contract_path.read_text(encoding="utf-8"))
    assert contract["stage_id"] == "REC_NEXT03_EXTERNAL_CAS_OCTAVE_JAS_JULIA_R3"
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

    provenance = contract["provenance_contract"]
    assert provenance["source_head_sha"] == (
        "EXACT_TESTED_PR_HEAD_OR_DIRECT_PUSH_COMMIT"
    )
    assert provenance["workflow_sha"] == (
        "EXACT_GITHUB_WORKFLOW_REVISION_INCLUDING_SYNTHETIC_PR_MERGE"
    )
    assert provenance["trigger"] == "pull_request_OR_push"
    assert provenance["aggregate_requires_uniform_source_head_sha"] is True
    assert provenance["aggregate_requires_uniform_workflow_sha"] is True
    assert provenance["legacy_source_sha_field_forbidden"] is True


def test_julia_i03_uses_exact_nemo_series_not_heuristic_limit() -> None:
    source_path = JULIA_ROOT / "verify_rec_next03_symbolics.jl"
    source = source_path.read_text(encoding="utf-8")

    assert "Symbolics.limit" not in source
    assert "iszero(reduced)" not in source

    for token in (
        "power_series_ring(",
        "divexact(",
        "coeff(Fseries, 0)",
        "coeff(Fseries, 1)",
        'identity("I03"',
        'mutation("M03"',
    ):
        assert token in source, f"missing exact I03 oracle token: {token}"


def test_receipt_collector_separates_source_head_from_workflow_revision(
    tmp_path: Path,
) -> None:
    contract = _write_minimal_contract(tmp_path / "contract.json")
    log = tmp_path / "engine.log"
    version = tmp_path / "version.txt"
    hashes = tmp_path / "package.sha256"
    output = tmp_path / "receipt.json"
    log.write_text(
        "IDENTITY I01 PASS\nMUTATION M01 DETECTED\nSTATUS PASS\n",
        encoding="utf-8",
    )
    version.write_text("test-version\n", encoding="utf-8")
    hashes.write_text(f"{'3' * 64}  test-package\n", encoding="utf-8")

    completed = subprocess.run(
        [
            sys.executable,
            str(COLLECTOR),
            "--contract",
            str(contract),
            "--engine",
            "engine_a",
            "--log",
            str(log),
            "--version",
            str(version),
            "--hashes",
            str(hashes),
            "--engine-exit-code",
            "0",
            "--source-head-sha",
            SOURCE_HEAD_SHA,
            "--workflow-sha",
            WORKFLOW_SHA,
            "--trigger",
            "pull_request",
            "--output",
            str(output),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0, completed.stderr or completed.stdout
    receipt = json.loads(output.read_text(encoding="utf-8"))
    assert receipt["source_head_sha"] == SOURCE_HEAD_SHA
    assert receipt["workflow_sha"] == WORKFLOW_SHA
    assert receipt["trigger"] == "pull_request"
    assert "source_sha" not in receipt


def test_aggregate_accepts_uniform_provenance_and_rejects_mismatched_head(
    tmp_path: Path,
) -> None:
    contract = _write_minimal_contract(tmp_path / "contract.json")
    receipts = tmp_path / "receipts"
    for index, engine in enumerate(("engine_a", "engine_b", "engine_c")):
        _write_engine_receipt(receipts, engine=engine, index=index)

    accepted_output = tmp_path / "accepted.json"
    accepted = _run_aggregate(
        contract=contract,
        receipts_root=receipts,
        output=accepted_output,
    )
    assert accepted.returncode == 0, accepted.stderr or accepted.stdout
    accepted_receipt = json.loads(accepted_output.read_text(encoding="utf-8"))
    assert accepted_receipt["provenance"]["source_head_sha"] == SOURCE_HEAD_SHA
    assert accepted_receipt["provenance"]["workflow_sha"] == WORKFLOW_SHA
    assert accepted_receipt["provenance"]["trigger"] == "pull_request"

    _write_engine_receipt(
        receipts,
        engine="engine_c",
        index=2,
        source_head_sha="4" * 40,
    )
    rejected_output = tmp_path / "rejected.json"
    rejected = _run_aggregate(
        contract=contract,
        receipts_root=receipts,
        output=rejected_output,
    )
    assert rejected.returncode != 0
    rejected_receipt = json.loads(rejected_output.read_text(encoding="utf-8"))
    assert rejected_receipt["status"] == "FAIL"
    assert any(
        "source_head_sha mismatch" in error
        for error in rejected_receipt["errors"]
    )


def test_workflow_passes_exact_head_and_workflow_revision_separately() -> None:
    source = WORKFLOW.read_text(encoding="utf-8")
    for token in (
        "REC_SOURCE_HEAD_SHA: ${{ github.event.pull_request.head.sha || github.sha }}",
        "REC_WORKFLOW_SHA: ${{ github.sha }}",
        "REC_WORKFLOW_TRIGGER: ${{ github.event_name }}",
        '--source-head-sha "$REC_SOURCE_HEAD_SHA"',
        '--workflow-sha "$REC_WORKFLOW_SHA"',
        '--trigger "$REC_WORKFLOW_TRIGGER"',
        '--expected-source-head-sha "$REC_SOURCE_HEAD_SHA"',
        '--expected-workflow-sha "$REC_WORKFLOW_SHA"',
        '--expected-trigger "$REC_WORKFLOW_TRIGGER"',
    ):
        assert token in source, f"workflow missing provenance token: {token}"
    assert "--source-sha" not in source


def test_julia_environment_is_source_locked_and_contract_bound(tmp_path: Path) -> None:
    contract_path = CAS_ROOT / "CONTRACT.json"
    project_path = JULIA_ROOT / "Project.toml"
    manifest_path = JULIA_ROOT / "Manifest.toml"
    output = tmp_path / "julia-lock-receipt.json"

    assert JULIA_LOCK_VERIFIER.is_file(), "Julia lock verifier must be source-controlled"
    assert manifest_path.is_file(), "Manifest.toml must be source-controlled"

    completed = _run_julia_lock_verifier(
        contract=contract_path,
        project=project_path,
        manifest=manifest_path,
        output=output,
    )
    assert completed.returncode == 0, completed.stderr or completed.stdout

    receipt = json.loads(output.read_text(encoding="utf-8"))
    assert receipt["status"] == "PASS"
    contract = json.loads(contract_path.read_text(encoding="utf-8"))
    lock = contract["julia_environment_lock"]
    assert lock["julia_version"] == "1.12.7"
    assert lock["manifest_format"] == "2.0"
    assert lock["project_sha256"] == _sha256(project_path)
    assert lock["manifest_sha256"] == _sha256(manifest_path)
    assert re.fullmatch(r"[0-9a-f]{40}", lock["project_hash"])
    assert set(lock["required_packages"]) == {"Nemo", "Symbolics"}
    for package in ("Nemo", "Symbolics"):
        pin = lock["required_packages"][package]
        assert re.fullmatch(r"[0-9a-f-]{36}", pin["uuid"])
        assert re.fullmatch(r"\d+\.\d+\.\d+", pin["version"])
        assert re.fullmatch(r"[0-9a-f]{40}", pin["git_tree_sha1"])


@pytest.mark.parametrize(
    ("mutation", "expected_error"),
    (
        ("nemo_version", "Nemo version mismatch"),
        ("nemo_tree", "Nemo git-tree-sha1 mismatch"),
        ("symbolics_version", "Symbolics version mismatch"),
        ("manifest_project_hash", "project_hash mismatch"),
    ),
)
def test_julia_environment_lock_rejects_semantic_manifest_mutations_even_if_rehashed(
    tmp_path: Path,
    mutation: str,
    expected_error: str,
) -> None:
    contract = json.loads((CAS_ROOT / "CONTRACT.json").read_text(encoding="utf-8"))
    lock = contract["julia_environment_lock"]
    project_path = tmp_path / "Project.toml"
    manifest_path = tmp_path / "Manifest.toml"
    contract_path = tmp_path / "CONTRACT.json"
    output = tmp_path / "receipt.json"

    project_path.write_bytes((JULIA_ROOT / "Project.toml").read_bytes())
    manifest_text = (JULIA_ROOT / "Manifest.toml").read_text(encoding="utf-8")

    if mutation == "nemo_version":
        manifest_text = _replace_manifest_package_field(
            manifest_text,
            package="Nemo",
            field="version",
            replacement="0.0.0",
        )
    elif mutation == "nemo_tree":
        manifest_text = _replace_manifest_package_field(
            manifest_text,
            package="Nemo",
            field="git-tree-sha1",
            replacement="0" * 40,
        )
    elif mutation == "symbolics_version":
        manifest_text = _replace_manifest_package_field(
            manifest_text,
            package="Symbolics",
            field="version",
            replacement="0.0.0",
        )
    elif mutation == "manifest_project_hash":
        manifest_text, count = re.subn(
            r'(?m)^project_hash = "[0-9a-f]{40}"$',
            f'project_hash = "{"0" * 40}"',
            manifest_text,
            count=1,
        )
        assert count == 1
    else:  # pragma: no cover - parametrization is exhaustive
        raise AssertionError(mutation)

    manifest_path.write_text(manifest_text, encoding="utf-8")
    lock["manifest_sha256"] = _sha256(manifest_path)
    contract_path.write_text(json.dumps(contract), encoding="utf-8")

    completed = _run_julia_lock_verifier(
        contract=contract_path,
        project=project_path,
        manifest=manifest_path,
        output=output,
    )
    assert completed.returncode != 0
    receipt = json.loads(output.read_text(encoding="utf-8"))
    assert receipt["status"] == "FAIL"
    assert any(expected_error in error for error in receipt["errors"])


def test_julia_environment_lock_rejects_project_byte_drift(tmp_path: Path) -> None:
    contract_path = CAS_ROOT / "CONTRACT.json"
    project_path = tmp_path / "Project.toml"
    manifest_path = tmp_path / "Manifest.toml"
    output = tmp_path / "receipt.json"

    project_path.write_bytes((JULIA_ROOT / "Project.toml").read_bytes() + b"\n")
    manifest_path.write_bytes((JULIA_ROOT / "Manifest.toml").read_bytes())

    completed = _run_julia_lock_verifier(
        contract=contract_path,
        project=project_path,
        manifest=manifest_path,
        output=output,
    )
    assert completed.returncode != 0
    receipt = json.loads(output.read_text(encoding="utf-8"))
    assert any("Project.toml SHA-256 mismatch" in error for error in receipt["errors"])


def test_workflow_enforces_committed_manifest_immutability() -> None:
    source = WORKFLOW.read_text(encoding="utf-8")
    for token in (
        "Verify committed Julia environment lock",
        "verify_julia_environment_lock.py",
        "Pkg.instantiate()",
        "git diff --exit-code -- formal/rec_next03/external_cas_oji/julia/Project.toml formal/rec_next03/external_cas_oji/julia/Manifest.toml",
        "formal/rec_next03/external_cas_oji/julia/julia_environment_lock_receipt.json",
    ):
        assert token in source, f"workflow missing immutable-environment token: {token}"
    assert "Pkg.resolve()" not in source
    assert "Pkg.update()" not in source
