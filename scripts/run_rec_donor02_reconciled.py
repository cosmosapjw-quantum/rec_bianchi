"""Exact-head reconciliation check: PR59 contract plus unchanged PR58 source.

No old RED runner or repository-wide suite is executed. All outputs go outside
this detached worktree. Exit zero means bounded protocol PASS, not physical
source authentication, executed deposition, or provider admission.
"""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import traceback
import unittest

ROOT = Path(__file__).resolve().parents[1]
BASE = "8436c135d62ebc33e329b5541ebea53d9a067ffd"
BASE_TREE = "b1b71f7571b5d58b25164e37149d645e4bef0b46"
DONOR = "a83204c887785ee3453be2c2361b7fda012e16ba"
SOURCE = "src/full_bianchi_hyrec/physical_source_authority.py"
TEST = "tests/trajectory/test_rec_donor01_typed_physical_source_red.py"
SAFETY = "tests/trajectory/test_rec_donor02_source_safety.py"
PROBE = "scripts/probe_rec_donor02.py"
DOC = "docs/research/rec_donor02_reconciled/"
BORROWED = {SOURCE: "6d4f39d48993c4715f5002ba068e8dcf98336be3",
            SAFETY: "e432652b4f626bd9cf98d96f9770ba44e36cea44",
            PROBE: "c2fbd594d1ca05b3165890ba156056257f9cfdfa"}
MIGRATIONS = (
    ('"""Implementation-absent RED for a representation-neutral REC source owner."""',
     '"""REC-DONOR-01 assertions under the amended REC-DONOR-02 contract."""'),
    ('# Three controls.  These pass while the future implementation is absent.',
     '# Three controls. The historical manifest stays fixed; presence migrates.'),
    ('def test_control_parent_identity_and_future_module_absent(self):',
     'def test_control_parent_identity_and_future_module_present(self):'),
    ('self.assertFalse(FUTURE_PATH.exists())', 'self.assertTrue(FUTURE_PATH.is_file())'),
    ('# Thirteen future behaviours.  Each currently fails only at _module().',
     '# Thirteen behaviours retained from the amended source contract.'),
)
GOLDEN = {
    "source": "c200d4698f8ed8590d05ef5561aed80749b1e85d13ca9bd2f8f16c11f363fb3b",
    "payload_mutant": "ec9490abc21a7910a88332bb6ae3ac8a120a6eaabd89b652d9dc76628a4418c4",
    "restart_mutant": "38d984499e2565b5afc540f0cbda848bc41ed498aa3c857cd6a223f6ea300c03",
}


def git(*args: str) -> str:
    return subprocess.check_output(["git", "-C", str(ROOT), *args], text=True).strip()


def require(ok: bool, message: str) -> None:
    if not ok:
        raise RuntimeError(message)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--expected-head", required=True)
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()
    out = Path(args.output_dir).resolve()
    require(out != ROOT and ROOT not in out.parents, "OUTPUT_MUST_BE_OUTSIDE_WORKTREE")
    out.mkdir(parents=True, exist_ok=False)
    sys.dont_write_bytecode = True
    os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
    receipt = {"schema": "rec-donor02-amended-reconciliation/v1", "status": "STOP_INVALID",
               "parent": BASE, "parent_tree": BASE_TREE, "source_donor": DONOR,
               "python": sys.version, "platform": platform.platform(),
               "workflow_sha": os.getenv("GITHUB_SHA"),
               "workflow_run_id": os.getenv("GITHUB_RUN_ID"),
               "physical_deposition_executed": False, "provider_admitted": False,
               "physical_source_authenticated": False, "rendered_plot_audit": "NOT_PERFORMED",
               "claim": "NO_PASS_REC_PHYSICAL_SPLIT"}
    try:
        head, tree = git("rev-parse", "HEAD"), git("rev-parse", "HEAD^{tree}")
        receipt.update(executed_head=head, executed_tree=tree)
        require(head == args.expected_head, "EXACT_HEAD_MISMATCH")
        detached = subprocess.run(["git", "-C", str(ROOT), "symbolic-ref", "-q", "HEAD"],
                                  capture_output=True, text=True)
        require(detached.returncode == 1, "DETACHED_CHECKOUT_REQUIRED")
        require(git("rev-parse", BASE + "^{tree}") == BASE_TREE, "BASE_TREE_MISMATCH")
        subprocess.run(["git", "-C", str(ROOT), "merge-base", "--is-ancestor", BASE, head], check=True)
        require(not git("status", "--porcelain=v1", "--untracked-files=all"), "INITIAL_DIRTY_WORKTREE")
        changed = git("diff", "--name-only", BASE, head).splitlines()
        allowed = {SOURCE, TEST, SAFETY, PROBE, "scripts/run_rec_donor02_reconciled.py",
                   ".github/workflows/rec-donor02-reconciled.yml"}
        require(all(p in allowed or p.startswith(DOC) for p in changed), "OUT_OF_SCOPE_DELTA")
        require(git("diff", "--name-status", BASE, head, "--", "src") == "A\t" + SOURCE,
                "PRODUCTION_DELTA_NOT_SINGLE_ADDITION")
        for path, blob in BORROWED.items():
            require(git("rev-parse", "HEAD:" + path) == blob, "BORROWED_BLOB_DRIFT:" + path)
            require(git("hash-object", str(ROOT / path)) == blob, "WORKING_BYTES_DRIFT:" + path)
        require(git("rev-parse", BASE + ":" + TEST) == "3ac3ed17b5b236cac7a9407bc5a2d405d2c18f97",
                "AMENDED_BASE_TEST_DRIFT")
        expected = subprocess.check_output(["git", "-C", str(ROOT), "show", BASE + ":" + TEST])
        for old, new in MIGRATIONS:
            require(expected.count(old.encode()) == 1, "MIGRATION_NOT_UNIQUE")
            expected = expected.replace(old.encode(), new.encode(), 1)
        require((ROOT / TEST).read_bytes() == expected, "UNAUTHORIZED_TEST_MIGRATION")
        subprocess.run(["git", "-C", str(ROOT), "diff", "--check", BASE, head], check=True)
        manifest = {p: {"git_blob": git("rev-parse", "HEAD:" + p),
                        "sha256": hashlib.sha256((ROOT / p).read_bytes()).hexdigest()}
                    for p in changed}
        (out / "source_manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
        for path in (SOURCE, TEST, SAFETY, PROBE, "scripts/run_rec_donor02_reconciled.py"):
            compile((ROOT / path).read_bytes(), str(ROOT / path), "exec")
        receipt.update(changed_paths=changed, source_blob=BORROWED[SOURCE],
                       borrowed_blobs_exact=True, authorized_presence_migration_only=True, compile_rc=0)
        suite = unittest.TestSuite()
        for i, path in enumerate((TEST, SAFETY)):
            spec = importlib.util.spec_from_file_location(f"reconciled_test_{i}", ROOT / path)
            mod = importlib.util.module_from_spec(spec)
            sys.modules[spec.name] = mod
            spec.loader.exec_module(mod)
            suite.addTests(unittest.defaultTestLoader.loadTestsFromModule(mod))
        require(suite.countTestCases() == 27, "UNEXPECTED_COLLECTION_COUNT")
        stream = io.StringIO()
        result = unittest.TextTestRunner(stream=stream, verbosity=2).run(suite)
        (out / "tests.log").write_text(stream.getvalue(), encoding="utf-8")
        print(stream.getvalue(), flush=True)
        receipt.update(tests=result.testsRun,
                       failures=[{"id": t.id(), "traceback": s} for t, s in result.failures],
                       errors=[{"id": t.id(), "traceback": s} for t, s in result.errors],
                       skips=[{"id": t.id(), "reason": s} for t, s in result.skipped],
                       expected_failures=[t.id() for t, _ in result.expectedFailures],
                       unexpected_successes=[t.id() for t in result.unexpectedSuccesses])
        receipt["tests_pass"] = (result.testsRun == 27 and result.wasSuccessful()
                                 and not result.skipped and not result.expectedFailures)
        probe = subprocess.run([sys.executable, "-B", str(ROOT / PROBE), str(out)],
                               capture_output=True, text=True, timeout=90)
        (out / "probe.log").write_text(probe.stdout + probe.stderr, encoding="utf-8")
        print(probe.stdout, flush=True)
        receipt["probe_rc"] = probe.returncode
        require(probe.returncode == 0, "NUMERICAL_PROBE_FAILED")
        numeric = json.loads((out / "NUMERICAL_PROBE.json").read_text())
        require(numeric["fresh_process_hashes"] == GOLDEN, "FROZEN_SEMANTIC_HASH_DRIFT")
        require(numeric["action_cases"] == 36 and numeric["jvp_cases"] == 108
                and numeric["max_action_residual"] == 0 and numeric["max_jvp_residual"] == 0
                and numeric["hashes_identical_in_two_fresh_processes"] is True,
                "BOUNDED_ORACLE_MISMATCH")
        receipt["numerical_probe"] = numeric
        receipt["clean_worktree"] = not git("status", "--porcelain=v1", "--untracked-files=all")
        require(receipt["clean_worktree"], "POSTRUN_DIRTY_WORKTREE")
        receipt["status"] = ("PASS_REC_DONOR02_AMENDED_SOURCE_PROTOCOL" if receipt["tests_pass"]
                             else "FAIL_REC_DONOR02_AMENDED_SOURCE_PROTOCOL")
    except Exception:
        receipt["exception"] = traceback.format_exc()
        print(receipt["exception"], file=sys.stderr)
    finally:
        (out / "REC_DONOR02_RECONCILED_RECEIPT.json").write_text(
            json.dumps(receipt, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")
        (out / "SHA256SUMS").write_text("".join(
            hashlib.sha256(p.read_bytes()).hexdigest() + "  " + p.name + "\n"
            for p in sorted(out.iterdir()) if p.is_file() and p.name != "SHA256SUMS"), encoding="utf-8")
        print(json.dumps(receipt, sort_keys=True, allow_nan=False), flush=True)
    return 0 if receipt["status"] == "PASS_REC_DONOR02_AMENDED_SOURCE_PROTOCOL" else 1


if __name__ == "__main__":
    raise SystemExit(main())
