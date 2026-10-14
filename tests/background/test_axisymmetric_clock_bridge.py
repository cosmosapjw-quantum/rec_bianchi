"""Regression tests for the actual REC/native AXBI clock bridge CLI."""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
import subprocess
import sys

import pytest

from full_bianchi_hyrec.background import AxisymmetricBianchiIBackground


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts/validate_axisymmetric_clock_bridge.py"


def _fixtures(tmp_path):
    rows = []
    sources = []
    for label, q in (("ZERO", 0.0), ("SHEAR_PLUS", 0.01), ("SHEAR_MINUS", -0.01)):
        model = AxisymmetricBianchiIBackground(q_ref=q)
        a1, a2 = model.a_ref, 0.04761905047098814
        interval = model.interval(a1, a2)
        rows.append({
            "case": label, "index": 3, "a1": a1, "a2": a2,
            "signed_q": q, "saved_dt_s": interval.delta_t_s,
            "reference_dt_s": interval.delta_t_s,
        })
        sources.append({
            "case": label, "history_sha256": hashlib.sha256(label.encode()).hexdigest(),
            "rows": 4, "selected": 1,
        })
    p = tmp_path / "native.csv"
    with p.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    s = tmp_path / "native_summary.json"
    s.write_text(json.dumps({
        "run_id": "REC_BG_R8_20261014",
        "source_cases": sources, "sample_count": 3,
    }))
    return p, s


def test_bridge_cli_produces_r8_bounded_json(tmp_path):
    inp, summary = _fixtures(tmp_path)
    output = tmp_path / "new.json"
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--input", str(inp),
         "--summary", str(summary), "--out", str(output)],
        cwd=ROOT,
        env={"PYTHONPATH": str(ROOT / "src")},
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    parsed = json.loads(output.read_text())
    assert parsed["component_pass"] is True
    assert parsed["sample_count"] == 3
    assert len(parsed["rows"]) == 3
    assert parsed["scientific_status"] == "SCOPED_COMPONENT_DIAGNOSTIC_ONLY"
    assert "full-history convergence" in parsed["not_claimed"]


def test_bridge_refuses_overwrite(tmp_path):
    inp, summary = _fixtures(tmp_path)
    output = tmp_path / "old.json"
    output.write_text("PRESERVED")
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--input", str(inp),
         "--summary", str(summary), "--out", str(output)],
        cwd=ROOT, env={"PYTHONPATH": str(ROOT / "src")},
        capture_output=True, text=True,
    )
    assert result.returncode != 0
    assert output.read_text() == "PRESERVED"


def test_bridge_rejects_wrong_signed_case(tmp_path):
    inp, summary = _fixtures(tmp_path)
    text = inp.read_text().replace("SHEAR_PLUS", "SHEAR_MINUS", 1)
    inp.write_text(text)
    out = tmp_path / "bad.json"
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--input", str(inp),
         "--summary", str(summary), "--out", str(out)],
        cwd=ROOT, env={"PYTHONPATH": str(ROOT / "src")},
        capture_output=True, text=True,
    )
    assert result.returncode != 0
    assert not out.exists()
