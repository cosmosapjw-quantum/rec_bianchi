#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
OFFLINE=0
if [[ "${1:-}" == "--offline" ]]; then OFFLINE=1; fi
PYTHON_BIN="${PYTHON_BIN:-python3}"
if [[ ! -d .venv ]]; then
  "$PYTHON_BIN" -m venv .venv || {
    if [[ "$OFFLINE" -eq 1 ]]; then
      echo "venv creation unavailable; using base interpreter" >&2
    else
      exit 1
    fi
  }
fi
if [[ -x .venv/bin/python ]]; then PY=.venv/bin/python; else PY="$PYTHON_BIN"; fi
if [[ "$OFFLINE" -eq 0 ]]; then
  "$PY" -m pip install --upgrade pip
  "$PY" -m pip install -e '.[test,research]'
else
  "$PY" - <<'PY'
import importlib
for name in ('numpy','scipy','pytest'):
    importlib.import_module(name)
print('offline dependency check: PASS')
PY
fi
export REC_BIANCHI_ROOT="$ROOT"
export BIANCHI_PRIMITIVE_SOURCE="$ROOT/archive/inputs/bianchibianchic2"
export JAX_ENABLE_X64=True
"$PY" scripts/verify_repo.py --quick
printf '
Sandbox ready. Read HANDOFF_PROMPT.md and state/PROJECT_STATE.json.
'
