#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

OFFLINE=0
if [[ "${1:-}" == "--offline" ]]; then
  OFFLINE=1
fi

PYTHON_BIN="${PYTHON_BIN:-python3}"

has_runtime_deps() {
  "$1" - <<'PY' >/dev/null 2>&1
import importlib
for name in ("numpy", "scipy", "pytest"):
    importlib.import_module(name)
PY
}

if [[ "$OFFLINE" -eq 1 ]]; then
  # An ordinary venv is intentionally isolated from preinstalled scientific
  # packages.  In an offline recovery runtime that can create an unusable empty
  # environment, so prefer an existing usable venv and otherwise use the base
  # interpreter that already carries the locked dependencies.
  if [[ -x .venv/bin/python ]] && has_runtime_deps .venv/bin/python; then
    PY=.venv/bin/python
  elif has_runtime_deps "$PYTHON_BIN"; then
    PY="$PYTHON_BIN"
    echo "offline recovery: using dependency-complete base interpreter $PY" >&2
  else
    echo "offline dependency check failed for .venv and $PYTHON_BIN" >&2
    echo "Set PYTHON_BIN to an interpreter containing numpy, scipy, and pytest." >&2
    exit 2
  fi
else
  if [[ ! -d .venv ]]; then
    "$PYTHON_BIN" -m venv .venv
  fi
  PY=.venv/bin/python
  "$PY" -m pip install --upgrade pip
  "$PY" -m pip install -e '.[test,research]'
fi

"$PY" - <<'PY'
import numpy
import scipy
import pytest
print(
    "dependency check: PASS "
    f"(numpy={numpy.__version__}, scipy={scipy.__version__}, pytest={pytest.__version__})"
)
PY

export REC_BIANCHI_ROOT="$ROOT"
export BIANCHI_PRIMITIVE_SOURCE="$ROOT/archive/inputs/bianchibianchic2"
export JAX_ENABLE_X64=True
"$PY" scripts/verify_repo.py --quick
printf '\nSandbox ready. Read HANDOFF_PROMPT.md and state/PROJECT_STATE.json.\n'
