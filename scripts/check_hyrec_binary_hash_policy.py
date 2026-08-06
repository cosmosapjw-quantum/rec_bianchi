#!/usr/bin/env python3
"""Fail fast on compiler-dependent HyRec binary-hash assertions.

The canonical numerical output hash is a portable scientific regression.  The
compiled executable hash is meaningful only on the exact compiler toolchain
that produced the pinned value.  Every assertion involving
``ORIGINAL_HYREC_PORTABLE_BINARY_SHA256`` must therefore be inside the positive
branch of ``if binary_hash_is_meaningful:``.
"""
from __future__ import annotations

import ast
from pathlib import Path
import sys


PINNED_NAME = "ORIGINAL_HYREC_PORTABLE_BINARY_SHA256"
GUARD_NAME = "binary_hash_is_meaningful"


def _contains_name(node: ast.AST, name: str) -> bool:
    return any(isinstance(item, ast.Name) and item.id == name for item in ast.walk(node))


def _positive_guard(test: ast.AST) -> bool:
    """Return whether ``test`` positively requires the shared guard.

    The intentionally narrow policy accepts ``if binary_hash_is_meaningful``
    and conjunctions containing that positive name.  Negated guards and else
    branches are not accepted.
    """

    if isinstance(test, ast.Name):
        return test.id == GUARD_NAME
    if isinstance(test, ast.BoolOp) and isinstance(test.op, ast.And):
        return any(_positive_guard(value) for value in test.values)
    return False


class _AssertionVisitor(ast.NodeVisitor):
    def __init__(self, relative_path: str) -> None:
        self.relative_path = relative_path
        self.guard_depth = 0
        self.violations: list[str] = []

    def visit_If(self, node: ast.If) -> None:  # noqa: N802 - ast API
        guarded = _positive_guard(node.test)
        if guarded:
            self.guard_depth += 1
        for statement in node.body:
            self.visit(statement)
        if guarded:
            self.guard_depth -= 1
        for statement in node.orelse:
            self.visit(statement)

    def visit_Assert(self, node: ast.Assert) -> None:  # noqa: N802 - ast API
        if _contains_name(node.test, PINNED_NAME) and self.guard_depth == 0:
            self.violations.append(
                f"{self.relative_path}:{node.lineno}: unguarded "
                f"{PINNED_NAME} assertion"
            )
        self.generic_visit(node)


def audit_binary_hash_assertions(root: Path) -> list[str]:
    """Return sorted policy violations below ``root``."""

    root = Path(root)
    violations: list[str] = []
    for path in sorted(root.rglob("*.py")):
        try:
            tree = ast.parse(path.read_text(), filename=str(path))
        except (OSError, SyntaxError) as exc:
            violations.append(f"{path}: cannot audit Python source: {exc}")
            continue
        relative = path.relative_to(root).as_posix()
        visitor = _AssertionVisitor(relative)
        visitor.visit(tree)
        violations.extend(visitor.violations)
    return sorted(violations)


def main(argv: list[str] | None = None) -> int:
    arguments = sys.argv[1:] if argv is None else argv
    root = Path(arguments[0]) if arguments else Path(__file__).resolve().parents[1] / "tests"
    violations = audit_binary_hash_assertions(root)
    if violations:
        print("HyRec binary-hash policy violations:", file=sys.stderr)
        for violation in violations:
            print(f"- {violation}", file=sys.stderr)
        return 1
    print(f"HyRec binary-hash policy PASS ({root})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
