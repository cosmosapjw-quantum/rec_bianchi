from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "check_hyrec_binary_hash_policy.py"


def _load_scanner():
    assert SCRIPT.is_file(), "binary-hash policy scanner is missing"
    spec = importlib.util.spec_from_file_location("hyrec_hash_policy", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_scanner_rejects_unguarded_assertion_and_accepts_guarded_one(tmp_path):
    scanner = _load_scanner()
    guarded = tmp_path / "test_guarded.py"
    guarded.write_text(
        "if binary_hash_is_meaningful:\n"
        "    assert digest == ORIGINAL_HYREC_PORTABLE_BINARY_SHA256\n"
    )
    unguarded = tmp_path / "test_unguarded.py"
    unguarded.write_text(
        "assert digest == ORIGINAL_HYREC_PORTABLE_BINARY_SHA256\n"
    )

    assert scanner.audit_binary_hash_assertions(tmp_path) == [
        "test_unguarded.py:1: unguarded ORIGINAL_HYREC_PORTABLE_BINARY_SHA256 assertion"
    ]


def test_repository_contains_no_unguarded_binary_hash_assertions():
    scanner = _load_scanner()
    assert scanner.audit_binary_hash_assertions(ROOT / "tests") == []
