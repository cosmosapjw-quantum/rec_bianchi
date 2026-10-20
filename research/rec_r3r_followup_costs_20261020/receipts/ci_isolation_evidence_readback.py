#!/usr/bin/env python3
"""Independent saved-CI and fixed-source readback; never runs scientific code."""
from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path
import subprocess
import tarfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SOURCE = "70a53396e910869ea069e184a44f1fb21cb47a0a"
BASE = "7d1a05033ad7b82527c66ae45a1feb09ff0d4ccc"
SCIENCE = "1313b1f1b2c081d57bcce9c60e757ef79110df91"
TREE = "565550bec51506b2a85c48442b9ab0d69be18be7"
TEST = "tests/test_r3r_stream_audit.py"
TEST_SHA = "6b29e4018f56ba20e455f7cac375a45d0eb712659827def308258c4bd0cd74d3"
CASES = {"test_actual_all_lane_binary64_bytes_separate_from_maxima",
         "test_valid_arbitrary_per_tag_interleaving_and_ordered_lane_trace"}
PROTECTED = ("scripts/build_r3o_rust.py", "scripts/benchmark_r3r_stream_audit.py",
             "scripts/r3r_stream_audit.py", "scripts/verify_r3q_h4_continuation.py",
             "scripts/run_r3r_h4_supervised.py")
MANIFEST = "research/rec_r3q_h4_continuation_20261020/SOURCE_CLOSURE.json"


def check(condition, message):
    if not condition:
        raise ValueError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def git(*args):
    result = subprocess.run(["git", *args], cwd=ROOT, capture_output=True,
                            timeout=15, check=False)
    check(result.returncode == 0 and not result.stderr, "read-only Git command failed")
    return result.stdout


def content(commit, name):
    return git("show", commit + ":" + name)


def tree_functions(raw):
    return {node.name: node for node in ast.parse(raw).body
            if isinstance(node, ast.FunctionDef) and node.name.startswith("test_")}


def main():
    changed = git("diff", "--name-only", BASE, SOURCE).decode().splitlines()
    check(changed == [TEST], "unexpected changed committed paths")
    check(git("rev-parse", SOURCE + "^{tree}").decode().strip() == TREE, "source tree mismatch")
    old, new = content(BASE, TEST), content(SOURCE, TEST)
    check(sha(new) == TEST_SHA, "reviewed test bytes differ")
    old_functions, new_functions = tree_functions(old), tree_functions(new)
    check(list(old_functions) == list(new_functions) and len(new_functions) == 18,
          "test function inventory differs")
    for name in old_functions:
        first, last = old_functions[name], new_functions[name]
        check([ast.dump(v) for v in first.decorator_list] == [ast.dump(v) for v in last.decorator_list],
              "test parameterization differs:" + name)
        if name not in CASES:
            check(ast.dump(first) == ast.dump(last), "unrelated test function changed:" + name)
    protected = {}
    for name in PROTECTED:
        raw = content(SOURCE, name)
        previous, science = content(BASE, name), content(SCIENCE, name)
        check(raw == previous, "runtime bytes changed since base:" + name)
        check(ast.dump(ast.parse(raw), include_attributes=True)
              == ast.dump(ast.parse(science), include_attributes=True),
              "runtime AST or locations changed since scientific execution:" + name)
        protected[name] = {"sha256": sha(raw), "base_bytes_equal": True,
                           "scientific_source_bytes_equal": raw == science,
                           "scientific_source_AST_and_locations_equal": True}
    frozen = json.loads(content(SOURCE, MANIFEST))["files"]
    names = set(frozen) | set(PROTECTED) | {
        MANIFEST, TEST, "tests/conftest.py", "pyproject.toml",
        "tests/fixtures/r3r_actual32/MANIFEST.json",
        "tests/fixtures/r3r_actual32/native_stream.csv.gz",
        "tests/fixtures/r3r_actual32/python_continuation.npz"}
    check(len(frozen) == 100 and len(names) == 111, "closure inventory differs")
    source_files = {}
    for name in sorted(names):
        raw = content(SOURCE, name)
        if name in frozen:
            check(sha(raw) == frozen[name], "frozen source hash changed:" + name)
        source_files[name] = {"bytes": len(raw), "sha256": sha(raw),
                              "git_blob": hashlib.sha1(b"blob " + str(len(raw)).encode()
                                                       + b"\0" + raw).hexdigest()}
    old_audits = {}
    for name in ("C9_CODE_AUDIT.json", "C9_CODE_AUDIT.md", "C9_EVIDENCE_READBACK.json"):
        path = HERE / name
        raw = path.read_bytes()
        check(raw == content(BASE, str(path.relative_to(ROOT))), "historical C9 changed:" + name)
        old_audits[name] = sha(raw)

    metadata_path = HERE / "ci/CI_ISOLATION_CI.json"
    metadata = json.loads(metadata_path.read_bytes())
    archive_path = metadata_path.parent / metadata["archive"]
    check(sha(archive_path.read_bytes()) == metadata["archive_sha256"], "CI archive hash differs")
    logs = {}
    with tarfile.open(archive_path, "r:gz") as archive:
        for entry in metadata["logs"]:
            raw = archive.extractfile(entry["file"]).read()
            check(len(raw) == entry["bytes"] and sha(raw) == entry["sha256"], "raw CI member differs")
            text = raw.decode("utf-8")
            check(entry["actual_checkout_sha"] in text and entry["actual_pytest_summary"] in text,
                  "CI identity or summary missing from actual raw")
            logs[entry["kind"]] = text
        provider_raw = archive.extractfile("PROVIDER_RETURNS.json").read()
    check(sha(provider_raw) == metadata["provider_returns_member_sha256"], "provider receipt differs")
    provider = json.loads(provider_raw)
    def provider_value(name):
        return json.loads(provider[name]["result"]["structuredContent"]["content"])
    source, merge = provider_value("source_commit"), provider_value("merge_commit")
    check(source["sha"] == SOURCE and source["tree"]["sha"] == merge["tree"]["sha"] == TREE,
          "source and actual PR merge tree differ")
    check(merge["sha"] == metadata["actual_PR_checkout"]
          and [v["sha"] for v in merge["parents"]]
          == ["5b44bb21ce0599e55e0848e5e3ff320c9e8ca172", SOURCE], "merge parents differ")
    for name in ("general_run", "dedicated_run"):
        run = provider_value(name)
        check(run["head_sha"] == SOURCE and run["status"] == "completed"
              and run["conclusion"] == "success", "current actual CI did not succeed")
    for text in ("cpu_s=92.440560:wall_s=80.063518", "cpu_s=92.626558:wall_s=80.249547",
                 "2 failed, 1036 passed, 103 skipped, 72 subtests passed in 131.63s"):
        check(text in logs["historical_general"], "historical failed evidence missing")
    check("1038 passed, 103 skipped, 72 subtests passed in 138.69s" in logs["current_general"],
          "new actual general result missing")
    check("60 passed, 1 skipped in 9.47s" in logs["current_dedicated"],
          "new actual dedicated result missing")
    result = {"schema": "rec.r3r.ci-isolation-independent-readback.v2", "status": "PASS_SCOPED",
              "scope": "SAVED_CI_LOGS_PROVIDER_RETURNS_AND_FIXED_GIT_BYTES; NO_TEST_SOLVER_OR_BENCHMARK_RUN",
              "source_commit": SOURCE, "source_tree": TREE,
              "actual_PR_checkout": merge["sha"], "exact_merge_tree_equal": True,
              "scientific_execution_source_complete_reused": SCIENCE,
              "changed_committed_paths": changed, "test_sha256": TEST_SHA,
              "existing_test_functions": len(new_functions), "parameterizations_unchanged": True,
              "unique_test_case_universe": 61, "new_unique_test_cases": 0,
              "protected_runtime": protected, "source_files": source_files,
              "frozen_source_files_verified": len(frozen), "total_source_files_verified": len(names),
              "historical_C9_sha256_unchanged": old_audits, "raw_CI_members_verified": 4,
              "CI_metadata_sha256": sha(metadata_path.read_bytes()),
              "CI_archive_sha256": metadata["archive_sha256"],
              "formal_validation_003": "NOT_RUN_SUPERSEDED_BY_ACTUAL_SOURCE70A_CI_RETURN",
              "new_local_test_executions": 0, "new_solver_integrations": 0,
              "new_timed_benchmark_trials": 0, "remaining_reviewed_P1": 0,
              "remaining_reviewed_P2": 0}
    text = json.dumps(result, sort_keys=True, indent=2, allow_nan=False) + "\n"
    with (HERE / "CI_ISOLATION_EVIDENCE_READBACK.json").open("x") as stream:
        stream.write(text)
    print(json.dumps({k: v for k, v in result.items() if k != "source_files"}, sort_keys=True))


if __name__ == "__main__":
    main()
