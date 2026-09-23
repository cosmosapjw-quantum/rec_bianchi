#!/usr/bin/env python3
from __future__ import annotations
import json, math, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "rust" / "rec_microphysics" / "Cargo.toml"
FIXTURE = ROOT / "tests" / "fixtures" / "rust_forward" / "fixed_source_oracle.json"

def fail(msg: str) -> None:
    print(f"FAIL: {msg}", file=sys.stderr)
    raise SystemExit(1)

def close(a: float, b: float, tol: float) -> bool:
    return abs(a-b) <= tol * (1.0 + abs(a) + abs(b))

def main() -> int:
    cfg = json.loads(FIXTURE.read_text())
    tol = float(cfg["implementation_tolerance"])
    proc = subprocess.run(
        ["cargo", "run", "--manifest-path", str(MANIFEST), "--locked", "--example", "eval_fixture", "--quiet"],
        cwd=ROOT, text=True, capture_output=True
    )
    if proc.returncode != 0:
        print(proc.stdout, end="")
        print(proc.stderr, end="", file=sys.stderr)
        fail(f"Rust fixture exited {proc.returncode}")
    try:
        got = json.loads(proc.stdout.strip())
    except Exception as exc:
        fail(f"fixture JSON parse: {exc}; stdout={proc.stdout!r}")
    for key, expected in cfg["expected"].items():
        actual = got.get(key)
        if actual is None or not close(float(actual), float(expected), tol):
            fail(f"{key}: got {actual}, expected {expected}, tol={tol}")
    for key in cfg["zero_or_scaled_residual_keys"]:
        value = float(got.get(key, math.inf))
        # Absolute zero-ledger entries are also safely bounded by this same tiny gate.
        if not math.isfinite(value) or abs(value) > tol:
            fail(f"{key}: residual {value} exceeds {tol}")
    if not close(float(got["bb_jvp_num"]), float(got["bb_jvp_ana"]), tol):
        fail(f"BB JVP: numeric {got['bb_jvp_num']} analytic {got['bb_jvp_ana']}")
    print(json.dumps({"status":"PASS","tolerance":tol,"values":got}, sort_keys=True))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
