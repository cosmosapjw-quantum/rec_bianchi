#!/usr/bin/env python3
"""Execute and classify the REC-DONOR-01 implementation-absent RED.

This runner is standard-library only.  Its successful process exit means that
exactly the declared future behaviours failed as assertions, the three controls
passed, no error/skip occurred, no production source changed, and the worktree
remained clean.  It does not turn the absent implementation into a physics PASS.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import sys
import unittest


BASE_COMMIT = "926e0c79a3fe7c3f5b24d5c5bb81304332def232"
BASE_TREE = "ce0654041d097768fae4f6a52b23c2137558f7be"
CLASSIFICATION = "PASS_EXPECTED_REC_DONOR01_TYPED_PHYSICAL_SOURCE_RED"
FUTURE_PRODUCTION_PATH = "src/full_bianchi_hyrec/physical_source_authority.py"
TEST_PATH = "tests/trajectory/test_rec_donor01_typed_physical_source_red.py"

REQUIRED_CHANGED_PATHS = {
    ".github/workflows/rec-donor01-typed-physical-source-red.yml",
    "docs/research/rec_donor01_typed_physical_source_red/CONTRACT.md",
    "docs/research/rec_donor01_typed_physical_source_red/DAG_STATE.json",
    "docs/research/rec_donor01_typed_physical_source_red/OPERATOR_READBACK_AND_ENVIRONMENT_DIAGNOSIS.md",
    "docs/research/rec_donor01_typed_physical_source_red/PHYS_MATH_AUDIT.md",
    "docs/research/rec_donor01_typed_physical_source_red/PHYS_MATH_CODE_AUDIT.md",
    "docs/research/rec_donor01_typed_physical_source_red/README.md",
    "docs/research/rec_donor01_typed_physical_source_red/SCISPACE_METHODOLOGY_LOCK.md",
    "docs/research/rec_donor01_typed_physical_source_red/STAGE_MANIFEST.json",
    "docs/research/rec_donor01_typed_physical_source_red/WOLFRAM_STATUS.json",
    "docs/superpowers/plans/2026-09-05-rec-donor01-typed-physical-source-red.md",
    "scripts/run_rec_donor01_typed_physical_source_red.py",
    TEST_PATH,
}

EXPECTED_FAILURE_METHODS = {
    "test_future_module_exposes_minimal_typed_authority_surface",
    "test_local_source_binds_physical_metadata_and_provenance",
    "test_source_identity_is_representation_neutral_and_mutation_sensitive",
    "test_positive_primary_rates_and_signed_net_affine_rate",
    "test_stimulated_emission_action_and_source_off_control",
    "test_equilibrium_detailed_balance_and_amplifying_branch_boundary",
    "test_energy_threshold_support_and_units_are_explicit",
    "test_local_analytic_jvp_is_exact_without_finite_difference_fallback",
    "test_two_photon_and_raman_kernels_are_nonlocal_not_local_pairs",
    "test_packet_rate_requires_once_only_deposition_authority",
    "test_trajectory_event_and_restart_identity_fail_closed",
    "test_integrated_state_requires_explicit_moment_map_binding",
    "test_no_universal_26_direction_authority_and_no_local_observer_boost",
}


def _run_git(root: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", "-C", str(root), *args],
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return completed.stdout.strip()


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _method_name(test: unittest.case.TestCase) -> str:
    return test.id().rsplit(".", 1)[-1]


def _load_suite(root: Path) -> unittest.TestSuite:
    test_file = root / TEST_PATH
    spec = importlib.util.spec_from_file_location("rec_donor01_red_tests", test_file)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load test module from {test_file}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return unittest.defaultTestLoader.loadTestsFromModule(module)


def _validate_source_state(root: Path) -> tuple[str, str, list[str]]:
    head = _run_git(root, "rev-parse", "HEAD")
    tree = _run_git(root, "rev-parse", "HEAD^{tree}")
    observed_base_tree = _run_git(root, "rev-parse", f"{BASE_COMMIT}^{{tree}}")
    if observed_base_tree != BASE_TREE:
        raise RuntimeError(
            f"base tree mismatch: expected {BASE_TREE}, observed {observed_base_tree}"
        )
    subprocess.run(
        ["git", "-C", str(root), "merge-base", "--is-ancestor", BASE_COMMIT, head],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
        text=True,
    )
    changed = sorted(
        line
        for line in _run_git(root, "diff", "--name-only", f"{BASE_COMMIT}..{head}").splitlines()
        if line
    )
    if set(changed) != REQUIRED_CHANGED_PATHS:
        missing = sorted(REQUIRED_CHANGED_PATHS - set(changed))
        extra = sorted(set(changed) - REQUIRED_CHANGED_PATHS)
        raise RuntimeError(f"changed-path contract mismatch: missing={missing}, extra={extra}")
    if (root / FUTURE_PRODUCTION_PATH).exists():
        raise RuntimeError(
            "future production module is present; this is not the implementation-absent RED"
        )
    if any(path.startswith("src/") for path in changed):
        raise RuntimeError("production source changed on a test-first RED branch")
    subprocess.run(
        ["git", "-C", str(root), "diff", "--check", f"{BASE_COMMIT}..{head}"],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    dirty = _run_git(root, "status", "--porcelain=v1", "--untracked-files=all")
    if dirty:
        raise RuntimeError(f"worktree is not clean before execution:\n{dirty}")
    return head, tree, changed


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
    )
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    root = args.repo_root.resolve()
    output_dir = args.output_dir.resolve()
    try:
        output_dir.relative_to(root)
    except ValueError:
        pass
    else:
        raise RuntimeError("output directory must be outside the Git worktree")

    head, tree, changed = _validate_source_state(root)
    sys.dont_write_bytecode = True
    stream = io.StringIO()
    result = unittest.TextTestRunner(stream=stream, verbosity=2).run(_load_suite(root))
    log_text = stream.getvalue()

    failure_methods = sorted(_method_name(test) for test, _ in result.failures)
    error_methods = sorted(_method_name(test) for test, _ in result.errors)
    skipped_methods = sorted(_method_name(test) for test, _ in result.skipped)
    unexpected_success_methods = sorted(
        _method_name(test) for test in result.unexpectedSuccesses
    )

    if result.testsRun != 16:
        raise RuntimeError(f"expected 16 tests, observed {result.testsRun}")
    if set(failure_methods) != EXPECTED_FAILURE_METHODS:
        raise RuntimeError(
            "expected failure set mismatch: "
            f"expected={sorted(EXPECTED_FAILURE_METHODS)}, observed={failure_methods}"
        )
    if error_methods or skipped_methods or unexpected_success_methods:
        raise RuntimeError(
            "non-admissible unittest result: "
            f"errors={error_methods}, skipped={skipped_methods}, "
            f"unexpected_successes={unexpected_success_methods}"
        )

    dirty_after = _run_git(root, "status", "--porcelain=v1", "--untracked-files=all")
    if dirty_after:
        raise RuntimeError(f"worktree became dirty during execution:\n{dirty_after}")

    output_dir.mkdir(parents=True, exist_ok=False)
    log_path = output_dir / "unittest.log"
    receipt_path = output_dir / "REC_DONOR01_EXPECTED_RED_RECEIPT.json"
    summary_path = output_dir / "summary.txt"
    manifest_path = output_dir / "SHA256SUMS"
    log_path.write_text(log_text, encoding="utf-8")

    receipt = {
        "schema": "rec-donor01-typed-physical-source-expected-red/v1",
        "classification": CLASSIFICATION,
        "repository": "cosmosapjw-quantum/rec_bianchi",
        "base_commit": BASE_COMMIT,
        "base_tree": BASE_TREE,
        "head_commit": head,
        "head_tree": tree,
        "changed_paths": changed,
        "future_production_path": FUTURE_PRODUCTION_PATH,
        "future_production_path_absent": True,
        "tests_run": result.testsRun,
        "assertion_failures": len(failure_methods),
        "failure_methods": failure_methods,
        "passing_controls": 3,
        "errors": 0,
        "skips": 0,
        "unexpected_successes": 0,
        "raw_unittest_would_exit": 1,
        "wrapper_exit": 0,
        "production_source_changed": False,
        "worktree_clean": True,
        "claim_effect": "TEST_CONTRACT_ONLY_NO_PHYSICAL_SOURCE_AUTHORITY",
    }
    receipt_path.write_text(
        json.dumps(receipt, sort_keys=True, indent=2) + "\n", encoding="utf-8"
    )
    summary_path.write_text(
        "\n".join(
            [
                CLASSIFICATION,
                f"head={head}",
                f"tree={tree}",
                "tests=16",
                "assertion_failures=13",
                "passing_controls=3",
                "errors=0",
                "skips=0",
                "production_source_changed=false",
                "physical_source_authority=false",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    manifest_path.write_text(
        "\n".join(
            f"{_sha256(path)}  {path.name}"
            for path in (receipt_path, summary_path, log_path)
        )
        + "\n",
        encoding="utf-8",
    )
    print(CLASSIFICATION)
    print(receipt_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
