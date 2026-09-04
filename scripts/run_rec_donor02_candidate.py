"""Execute exact-head source contracts and preserve all failures, including known ones."""
from __future__ import annotations
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
RED = "2dfd464efe91b319993e6c6759d380d53d0f3fde"
RED_TREE = "0fdb8bf0904df05ef5b495f3f0b19e5c4444a886"
SOURCE = "src/full_bianchi_hyrec/physical_source_authority.py"
TESTS = ("tests/trajectory/test_rec_donor01_typed_physical_source_red.py",
         "tests/trajectory/test_rec_donor02_source_safety.py")

def git(*args):
    return subprocess.check_output(["git", "-C", str(ROOT), *args], text=True).strip()

def main():
    out = Path(sys.argv[1]).resolve()
    if out == ROOT or ROOT in out.parents:
        raise RuntimeError("OUTPUT_MUST_BE_OUTSIDE_WORKTREE")
    out.mkdir(parents=True, exist_ok=False)
    receipt = {"schema": "rec-donor02-candidate/v1", "status": "STOP_INVALID",
               "scientific_claim": "NO_PASS_REC_PHYSICAL_SPLIT",
               "physical_deposition_executed": False, "provider_admitted": False}
    rc = 2
    try:
        head = git("rev-parse", "HEAD")
        receipt.update(head=head, tree=git("rev-parse", "HEAD^{tree}"),
                       python=sys.version, platform=platform.platform(),
                       workflow_sha=os.environ.get("GITHUB_WORKFLOW_SHA"),
                       trigger=os.environ.get("GITHUB_EVENT_NAME"))
        expected = os.environ.get("REC_EXPECTED_HEAD")
        if expected and head != expected:
            raise RuntimeError("EXACT_SOURCE_HEAD_MISMATCH")
        if git("rev-parse", RED + "^{tree}") != RED_TREE:
            raise RuntimeError("RED_TREE_MISMATCH")
        subprocess.run(["git", "-C", str(ROOT), "merge-base", "--is-ancestor", RED, head], check=True)
        if git("status", "--porcelain"):
            raise RuntimeError("DIRTY_WORKTREE_BEFORE")
        production = git("diff", "--name-only", RED, head, "--", "src").splitlines()
        present = (ROOT / SOURCE).is_file()
        if production != ([SOURCE] if present else []):
            raise RuntimeError("UNEXPECTED_PRODUCTION_PATH")
        subprocess.run(["git", "-C", str(ROOT), "diff", "--check", RED, head], check=True)
        suite = unittest.TestSuite()
        for i, path in enumerate(TESTS):
            spec = importlib.util.spec_from_file_location("donor02_test_" + str(i), ROOT / path)
            module = importlib.util.module_from_spec(spec)
            sys.modules[spec.name] = module
            spec.loader.exec_module(module)
            suite.addTests(unittest.defaultTestLoader.loadTestsFromModule(module))
        stream = io.StringIO()
        result = unittest.TextTestRunner(stream=stream, verbosity=2).run(suite)
        log = stream.getvalue()
        (out / "tests.log").write_text(log, encoding="utf-8")
        print(log)
        receipt.update(tests=result.testsRun,
                       passes=result.testsRun-len(result.failures)-len(result.errors)-len(result.skipped),
                       failures=[{"id": t.id(), "traceback": s} for t, s in result.failures],
                       errors=[{"id": t.id(), "traceback": s} for t, s in result.errors],
                       skips=[t.id() for t, _ in result.skipped],
                       unexpected_successes=[t.id() for t in result.unexpectedSuccesses],
                       production_paths=production, source_present=present)
        (out / "source_manifest.json").write_text(json.dumps({
            path: {"git_blob": git("rev-parse", "HEAD:" + path),
                   "sha256": hashlib.sha256((ROOT / path).read_bytes()).hexdigest()}
            for path in (*TESTS, "scripts/run_rec_donor02_candidate.py", *production)
        }, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        if git("status", "--porcelain"):
            raise RuntimeError("DIRTY_WORKTREE_AFTER")
        receipt["clean_worktree"] = True
        receipt["status"] = ("PASS_TESTS_NOT_PHYSICAL_ADMISSION" if result.wasSuccessful()
                             else "SOURCE_CANDIDATE_NOT_GREEN" if present
                             else "IMPLEMENTATION_ABSENT_RED_OBSERVED")
        rc = 0 if result.wasSuccessful() else 1
    except Exception as exc:
        receipt["exception"] = type(exc).__name__ + ": " + str(exc)
        raise
    finally:
        target = out / "REC_DONOR02_RECEIPT.json"
        tmp = out / ".receipt.tmp"
        tmp.write_text(json.dumps(receipt, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")
        os.replace(tmp, target)
        paths = sorted(p for p in out.iterdir() if p.is_file())
        (out / "SHA256SUMS").write_text("".join(
            hashlib.sha256(p.read_bytes()).hexdigest() + "  " + p.name + "\n" for p in paths), encoding="utf-8")
        print(json.dumps(receipt, sort_keys=True, allow_nan=False))
    return rc

if __name__ == "__main__":
    raise SystemExit(main())
