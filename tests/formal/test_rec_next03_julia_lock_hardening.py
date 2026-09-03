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
VERIFIER = CAS_ROOT / "scripts" / "verify_julia_environment_lock.py"
WORKFLOW = ROOT / ".github" / "workflows" / "rec-next03-octave-jas-julia-cas.yml"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _run_verifier(
    *, contract: Path, project: Path, manifest: Path, output: Path
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            str(VERIFIER),
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


def _replace_package_field(
    text: str, *, package: str, field: str, replacement: str
) -> str:
    pattern = re.compile(
        rf'(\[\[deps\.{re.escape(package)}\]\].*?^{re.escape(field)} = ")[^"]+("$)',
        flags=re.MULTILINE | re.DOTALL,
    )
    mutated, count = pattern.subn(rf"\g<1>{replacement}\g<2>", text, count=1)
    assert count == 1
    return mutated


@pytest.mark.parametrize(
    ("mutation", "expected_error"),
    (
        ("julia_version", "Julia version mismatch"),
        ("manifest_format", "manifest_format mismatch"),
        ("symbolics_tree", "Symbolics git-tree-sha1 mismatch"),
        ("missing_nemo", "exactly one [[deps.Nemo]] table"),
    ),
)
def test_additional_manifest_mutations_fail_even_after_contract_rehash(
    tmp_path: Path,
    mutation: str,
    expected_error: str,
) -> None:
    contract = json.loads((CAS_ROOT / "CONTRACT.json").read_text(encoding="utf-8"))
    project = tmp_path / "Project.toml"
    manifest = tmp_path / "Manifest.toml"
    contract_path = tmp_path / "CONTRACT.json"
    output = tmp_path / "receipt.json"

    project.write_bytes((JULIA_ROOT / "Project.toml").read_bytes())
    text = (JULIA_ROOT / "Manifest.toml").read_text(encoding="utf-8")

    if mutation == "julia_version":
        text, count = re.subn(
            r'(?m)^julia_version = "[^"]+"$',
            'julia_version = "1.12.6"',
            text,
            count=1,
        )
        assert count == 1
    elif mutation == "manifest_format":
        text, count = re.subn(
            r'(?m)^manifest_format = "[^"]+"$',
            'manifest_format = "1.0"',
            text,
            count=1,
        )
        assert count == 1
    elif mutation == "symbolics_tree":
        text = _replace_package_field(
            text,
            package="Symbolics",
            field="git-tree-sha1",
            replacement="0" * 40,
        )
    elif mutation == "missing_nemo":
        text, count = re.subn(
            r'\n\[\[deps\.Nemo\]\]\n.*?(?=\n\[\[deps\.|\Z)',
            "\n",
            text,
            count=1,
            flags=re.DOTALL,
        )
        assert count == 1
    else:  # pragma: no cover
        raise AssertionError(mutation)

    manifest.write_text(text, encoding="utf-8")
    contract["julia_environment_lock"]["manifest_sha256"] = _sha256(manifest)
    contract_path.write_text(json.dumps(contract), encoding="utf-8")

    completed = _run_verifier(
        contract=contract_path,
        project=project,
        manifest=manifest,
        output=output,
    )
    assert completed.returncode != 0
    receipt = json.loads(output.read_text(encoding="utf-8"))
    assert receipt["status"] == "FAIL"
    assert any(expected_error in error for error in receipt["errors"])


def test_workflow_hard_gates_actual_julia_runtime_version() -> None:
    source = WORKFLOW.read_text(encoding="utf-8")
    assert 'VERSION == v"1.12.7"' in source
    assert "unexpected Julia runtime version" in source
