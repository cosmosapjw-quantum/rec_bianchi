from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
ADMISSION_ROOT = (
    ROOT
    / "artifacts"
    / "trajectory"
    / "pr05c2c1b2b1e1c_recovery"
    / "rec_local01_admission"
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_concrete_local01_admission_has_closed_copied_evidence_schema() -> None:
    admission = json.loads(
        (ADMISSION_ROOT / "REC_LOCAL_01_ADMISSION.json").read_text(
            encoding="utf-8"
        )
    )
    assert admission["schema"] == "rec-local01-canonical-context-admission/v1"
    assert admission["status"] == (
        "PASS_REC_LOCAL01_EVIDENCE_ADMITTED_NOT_PHYSICAL_SPLIT"
    )
    assert admission["claim"] == "NO_PASS_REC_PHYSICAL_SPLIT"
    evidence = admission["evidence"]
    copied = evidence["copied_paths"]
    hashes = evidence["copied_path_sha256"]
    assert len(copied) == len(set(copied)) == 6
    assert set(hashes) == set(copied)
    for name in copied:
        path = ADMISSION_ROOT / "evidence" / name
        assert path.is_file() and not path.is_symlink()
        assert sha256(path) == hashes[name]
    assert hashes["REC_LOCAL_01_CANONICAL_CONTEXT_INTEGRATION.json"] == (
        admission["source_receipt"]["sha256"]
    )
    assert admission["bootstrap_recovery"] == {
        "original_status": "STOP_INVALID",
        "classification": "HISTORICAL_R2_PACKAGING_REPRODUCIBILITY_FAILURE",
        "r2_sidecar_rebind": "PASS",
        "followthrough_rebind": "PASS",
    }
