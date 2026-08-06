from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[2]
ARTIFACT = (
    ROOT
    / "archive/expanded/Full_Bianchi_HyRec_PR05B3_scalar_history_owner_swap_v0_61"
)
BUNDLE = (
    ROOT
    / "archive/bundles/Full_Bianchi_HyRec_PR05B3_scalar_history_owner_swap_v0_61.zip"
)
DATA = ROOT / "data/pr05b3_scalar_history_owner_swap_v061.npz"


def test_pr05b3_artifact_closes_owner_swap_and_hands_off_pr05c() -> None:
    hard = json.loads((ARTIFACT / "HARD_GATE_LEDGER.json").read_text())
    assert hard["status"] == "PASS_PR05B3_SCALAR_HISTORY_OWNER_SWAP_PR05C_NEXT"
    assert hard["PR05B3"] == "COMPLETE"
    assert hard["PR05"] == "IN_PROGRESS"
    assert all(item["passed"] for item in hard["gates"])
    assert hard["claim_boundary"]["typed_history_is_sole_python_owner"] is True
    assert hard["claim_boundary"]["adaptive_short_trajectory"] is False
    assert BUNDLE.is_file()
    assert DATA.is_file()
    subprocess.run(
        [sys.executable, str(ARTIFACT / "verify_PR05B3.py")],
        cwd=ARTIFACT,
        check=True,
    )
