from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[2]
NAME = "Full_Bianchi_HyRec_PR05C2C0_theory_closure_v0_65"
EXPANDED = ROOT / "archive" / "expanded" / NAME
BUNDLE = ROOT / "archive" / "bundles" / f"{NAME}.zip"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def test_pr05c2c0_theory_artifact_is_self_verifying() -> None:
    result = subprocess.run(
        [sys.executable, str(EXPANDED / "verify_PR05C2C0.py")],
        cwd=EXPANDED,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    assert result.returncode == 0, result.stdout
    assert "PASS_PR05C2C0_SCALAR_THEORY_CONTRACT_COMPLETE" in result.stdout


def test_pr05c2c0_bundle_and_theorem_registry_are_consistent() -> None:
    assert BUNDLE.is_file()
    with zipfile.ZipFile(BUNDLE) as archive:
        assert archive.testzip() is None
        metrics = json.loads(archive.read("NUMERICAL_METRICS.json"))
        gates = json.loads(archive.read("HARD_GATE_LEDGER.json"))
        theorems = json.loads(archive.read("THEOREM_REGISTRY.json"))
    assert metrics["theory_contract_complete"] is True
    assert metrics["direct_thermodynamic_compiler_implemented"] is False
    assert metrics["multi_macro_trajectory_completed"] is False
    assert gates["PR05C2C0"] == "COMPLETE_SCALAR_THEORY_CONTRACT"
    assert gates["PR05C2C1"] == "OPEN_IMPLEMENTATION_AND_NUMERICAL_EVIDENCE"
    assert len(theorems["theorems"]) >= 10
    index = json.loads((ROOT / "state/BUNDLE_INDEX.json").read_text())
    row = next(item for item in index if item["bundle"] == BUNDLE.name)
    assert _sha256(BUNDLE) == row["sha256"]
    assert BUNDLE.stat().st_size == row["size_bytes"]
