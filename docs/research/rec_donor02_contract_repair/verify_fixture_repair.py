"""Read-only, stdlib-only check of two test contracts; no donor is executed.

Usage: python verify_fixture_repair.py --repo-root /path/to/child
An offline --parent-file may supply the exact, Git-blob-verified parent test.
This is not the frozen RED runner, a production test runner, or a deposition
operator. It compiles/collects the test and checks its literals and AST only.
"""
from __future__ import annotations

import argparse
import ast
from fractions import Fraction as F
import hashlib
import importlib.util
import json
from pathlib import Path
import platform
import subprocess
import sys
import unittest

BASE = "2dfd464efe91b319993e6c6759d380d53d0f3fde"
BASE_TREE = "0fdb8bf0904df05ef5b495f3f0b19e5c4444a886"
PARENT_BLOB = "59b58011629b83fefe99670e870fa99ffa18e7f5"
TEST = "tests/trajectory/test_rec_donor01_typed_physical_source_red.py"
A = "test_energy_threshold_support_and_units_are_explicit"
B = "test_packet_rate_requires_once_only_deposition_authority"
J = "test_local_analytic_jvp_is_exact_without_finite_difference_fallback"


def blob_sha(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def method(tree: ast.AST, name: str) -> ast.FunctionDef:
    return next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == name)


def without_changed_methods(text: str) -> str:
    lines = text.splitlines(keepends=True)
    ranges = sorted((method(ast.parse(text), name).lineno - 1,
                     method(ast.parse(text), name).end_lineno) for name in (A, B))
    for start, end in reversed(ranges):
        lines[start:end] = ["    # BOUNDED_METHOD_REPLACEMENT\n"]
    return "".join(lines)


def number(node: ast.AST) -> F:
    return F(str(ast.literal_eval(node)))


def action_assertions(tree: ast.AST) -> list[dict]:
    result = []
    for node in ast.walk(method(tree, A)):
        if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                and node.func.attr in ("assertEqual", "assertNotEqual") and len(node.args) == 2):
            continue
        action = node.args[0]
        if not (isinstance(action, ast.Call) and isinstance(action.func, ast.Attribute)
                and action.func.attr == "action"):
            continue
        kw = {k.arg: number(k.value) for k in action.keywords}
        energy, occupation = kw["energy_j"], kw["occupation"]
        # Independent exact arithmetic on the declared, unchanged fixture.
        active = F("2.0e-18") <= energy < F("2.5e-18")
        value = F(1, 4) * (1 + occupation) - F(3, 4) * occupation if active else F(0)
        expected = number(node.args[1])
        agrees = value == expected if node.func.attr == "assertEqual" else value != expected
        result.append({"energy_j": str(energy), "occupation": str(occupation),
                       "assertion": node.func.attr, "expected": str(expected),
                       "exact_action_s_inv": str(value), "consistent": agrees})
    return result


def guarded_deposition(tree: ast.AST) -> tuple[int, int]:
    scope = method(tree, B)
    parents = {child: parent for parent in ast.walk(scope) for child in ast.iter_child_nodes(parent)}
    calls = [n for n in ast.walk(scope) if isinstance(n, ast.Call)
             and isinstance(n.func, ast.Attribute) and n.func.attr == "deposit_packet_rate"]
    unguarded = 0
    for call in calls:
        cur, guarded = call, False
        while cur in parents:
            cur = parents[cur]
            if isinstance(cur, ast.With):
                for item in cur.items:
                    ctx = item.context_expr
                    guarded |= (isinstance(ctx, ast.Call) and isinstance(ctx.func, ast.Attribute)
                                and ctx.func.attr == "assertRaises" and len(ctx.args) == 1
                                and ast.unparse(ctx.args[0]) == "m.DepositionAuthorityError")
        unguarded += not guarded
    return len(calls), unguarded


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[3])
    parser.add_argument("--parent-file", type=Path)
    args = parser.parse_args()
    root = args.repo_root.resolve()
    before = (args.parent_file.read_bytes() if args.parent_file else subprocess.check_output(
        ["git", "-C", str(root), "show", f"{BASE}:{TEST}"]))
    if blob_sha(before) != PARENT_BLOB:
        raise ValueError("parent test does not match the pinned Git blob")
    path = root / TEST
    after = path.read_bytes()
    old, new = before.decode("utf-8"), after.decode("utf-8")
    old_ast, new_ast = ast.parse(old), ast.parse(new)
    compile(new, str(path), "exec", dont_inherit=True)
    sys.dont_write_bytecode = True
    spec = importlib.util.spec_from_file_location("rec_contract_repair_collection", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot collect amended test")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    suite = unittest.defaultTestLoader.loadTestsFromModule(module)
    new_cases, old_cases = action_assertions(new_ast), action_assertions(old_ast)
    jvp = next(n for n in ast.walk(method(new_ast, J)) if isinstance(n, ast.Call)
               and isinstance(n.func, ast.Attribute) and n.func.attr == "jvp")
    kv = {k.arg: number(k.value) for k in jvp.keywords}
    dC = ((1 + kv["occupation"]) * kv["d_emission_s_inv"]
          - kv["occupation"] * kv["d_absorption_s_inv"] - F(1, 2) * kv["d_occupation"])
    expected_cases = [(F(e), F(f), F(c)) for e, f, c in (
        ("1.99e-18", "2", "0"), ("2e-18", "2", "-0.75"),
        ("2.25e-18", "2", "-0.75"), ("2.5e-18", "2", "0"),
        ("2e-18", "0.5", "0"))]
    observed = [(F(c["energy_j"]), F(c["occupation"]), F(c["expected"])) for c in new_cases]
    checks = {
        "syntax_compiles": True,
        "collected_16_without_executing_tests": suite.countTestCases() == 16,
        "only_two_method_bodies_changed": without_changed_methods(old) == without_changed_methods(new),
        "parent_threshold_contradiction_reproduced": sum(not c["consistent"] for c in old_cases) == 1,
        "five_authorized_exact_support_cases": observed == expected_cases,
        "all_five_support_assertions_are_equalities": all(c["assertion"] == "assertEqual" for c in new_cases),
        "all_five_support_cases_consistent": len(new_cases) == 5 and all(c["consistent"] for c in new_cases),
        "jvp_is_13_over_16_unchanged": dC == F(13, 16) and ast.dump(method(old_ast, J)) == ast.dump(method(new_ast, J)),
        "parent_hash_only_success_path_detected": guarded_deposition(old_ast) == (2, 1),
        "both_missing_and_unresolved_deposition_calls_guarded": guarded_deposition(new_ast) == (2, 0),
        "future_module_not_materialized": not (root / "src/full_bianchi_hyrec/physical_source_authority.py").exists(),
    }
    result = {
        "schema": "rec-donor02-bounded-contract-repair-check/v1",
        "classification": "PASS_CONTRACT_REPAIR_CHECKS_ONLY" if all(checks.values()) else "FAIL_CONTRACT_REPAIR_CHECKS",
        "parent_commit": BASE, "parent_tree": BASE_TREE,
        "parent_test_blob": PARENT_BLOB, "amended_test_blob": blob_sha(after),
        "python": platform.python_version(), "checks": checks,
        "exact_threshold_cases": new_cases, "exact_jvp": str(dC),
        "tests_collected": suite.countTestCases(), "production_tests_executed": 0,
        "deposition_operator_executed": False, "old_red_runner_executed": False,
        "broad_suite_executed": False, "new_physical_authority": False,
    }
    print(json.dumps(result, sort_keys=True, indent=2))
    return 0 if all(checks.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
