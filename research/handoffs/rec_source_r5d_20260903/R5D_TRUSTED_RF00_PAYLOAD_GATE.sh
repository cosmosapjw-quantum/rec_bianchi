#!/usr/bin/env bash
# REC-side handoff for the BASS R5D trusted native-payload gate.
#
# Safe properties:
# - may be launched from rec_bianchi or any other directory;
# - identifies BASS by remote.origin.url;
# - never switches or edits the caller checkout;
# - uses a detached BASS worktree and isolated Python 3.12 venv;
# - extracts the immutable trusted wheel from BASS Git history;
# - runs with BASS_ALLOW_UNVERIFIED_NATIVE_DEV unset;
# - always exits shell status zero after writing its own classification.

set +e
set +u
set +o pipefail 2>/dev/null || true

CANDIDATE_BRANCH='research/bass-rec-source-r5-protocol-green-20260903-r1'
CANDIDATE_COMMIT='fc4d21b92a1abd1e9b35178f7d666831fc5c827d'
CANDIDATE_TREE='c0caf9b8017d4c3850a1a99629246164fd4b27ff'
TRUSTED_BRANCH='agent/architecture/rf04-scalar-raw-20260829-fhxMnS'
TRUSTED_COMMIT='50b6e9f7a6741b7fd25b0421d2a674b9eb92cdda'
TRUSTED_WHEEL_PATH='artifacts/rust_first_runtime/rf04/scalar_raw/native_delta/rf02c-wheel/bianchi_rustcore-0.1.0-cp312-cp312-manylinux_2_34_x86_64.whl'
TRUSTED_RESTORE_PATH='artifacts/rust_first_runtime/rf04/scalar_raw/native_delta/RF02C_NATIVE_RESTORE.json'
TRUSTED_WHEEL_SHA='99bd0596642dd31ca82080fb24306cd9bf3f6dd1ad3f68a1380f77378e266302'
TRUSTED_SO_SHA='5d5b8197518d8637b14e0c78b871802ed64f6506c7a95128f31bd52044a98633'
GOLDEN_SOURCE_HASH='ca3807fa4ef49b5292bd65fd80b6fe9947c1cef7f835979122bff572900eb906'

STAMP="$(date -u +%Y%m%dT%H%M%SZ 2>/dev/null)"
[ -n "$STAMP" ] || STAMP='UNKNOWN_TIME'
RECEIPT_ROOT="${RECEIPT_ROOT:-$HOME/Dropbox/bianchi/_runtime_receipts}"
OUT="$RECEIPT_ROOT/BASS_REC_SOURCE_R5D_$STAMP"
mkdir -p "$OUT" 2>/dev/null || {
  printf 'classification=STOP_RECEIPT_DIRECTORY_UNAVAILABLE\n'
  exit 0
}

summary() {
  printf '%s=%s\n' "$1" "$2" | tee -a "$OUT/summary.txt"
}

find_bass() {
  for candidate in \
    "${BASS_REPO:-}" \
    "$HOME/Dropbox/bianchi/bass" \
    "$HOME/Dropbox/bass" \
    "$HOME/bass"
  do
    [ -n "$candidate" ] || continue
    top="$(git -C "$candidate" rev-parse --show-toplevel 2>/dev/null)"
    [ -n "$top" ] || continue
    origin="$(git -C "$top" config --get remote.origin.url 2>/dev/null)"
    case "$origin" in
      *cosmosapjw-quantum/bass|*cosmosapjw-quantum/bass.git)
        printf '%s\n' "$top"
        return 0
        ;;
    esac
  done
  return 1
}

BASS="$(find_bass)"
if [ -z "$BASS" ]; then
  summary classification STOP_BASS_REPOSITORY_NOT_FOUND
  summary receipt_dir "$OUT"
  exit 0
fi
summary bass_repo "$BASS"
summary bass_origin "$(git -C "$BASS" config --get remote.origin.url 2>/dev/null)"

PY_BOOT="${PYTHON_BOOTSTRAP:-$(command -v python3.12 2>/dev/null)}"
[ -x "$PY_BOOT" ] || PY_BOOT="$(command -v python 2>/dev/null)"
PYVER="$("$PY_BOOT" -c 'import sys; print(".".join(map(str,sys.version_info[:3])))' 2>/dev/null)"
case "$PYVER" in
  3.12.*) ;;
  *)
    summary classification STOP_PYTHON_3_12_REQUIRED
    summary python_version "${PYVER:-UNAVAILABLE}"
    summary receipt_dir "$OUT"
    exit 0
    ;;
esac
summary python_bootstrap "$PY_BOOT"
summary python_version "$PYVER"

# Fetch named refs rather than relying on raw-SHA fetch support.
git -C "$BASS" fetch --no-tags origin \
  "$CANDIDATE_BRANCH:refs/remotes/origin/$CANDIDATE_BRANCH" \
  "$TRUSTED_BRANCH:refs/remotes/origin/$TRUSTED_BRANCH" \
  >"$OUT/fetch.log" 2>&1
RC_FETCH=$?
CANDIDATE_REMOTE="$(git -C "$BASS" rev-parse "refs/remotes/origin/$CANDIDATE_BRANCH" 2>/dev/null)"
TRUSTED_REMOTE="$(git -C "$BASS" rev-parse "refs/remotes/origin/$TRUSTED_BRANCH" 2>/dev/null)"
summary fetch_rc "$RC_FETCH"
summary candidate_remote "$CANDIDATE_REMOTE"
summary trusted_remote "$TRUSTED_REMOTE"
if [ "$CANDIDATE_REMOTE" != "$CANDIDATE_COMMIT" ] || \
   [ "$TRUSTED_REMOTE" != "$TRUSTED_COMMIT" ]; then
  summary classification STOP_REMOTE_IDENTITY_MISMATCH
  summary receipt_dir "$OUT"
  exit 0
fi

TMP="$(mktemp -d /tmp/bass-r5d.XXXXXX 2>/dev/null)"
WT="$TMP/worktree"
VENV="$TMP/venv"
cleanup() {
  git -C "$BASS" worktree remove --force "$WT" >/dev/null 2>&1 || true
  case "$TMP" in
    /tmp/bass-r5d.*) rm -rf -- "$TMP" >/dev/null 2>&1 || true ;;
  esac
}
trap cleanup EXIT HUP INT TERM

if [ -z "$TMP" ] || [ ! -d "$TMP" ]; then
  summary classification STOP_TEMP_DIRECTORY_FAILURE
  summary receipt_dir "$OUT"
  exit 0
fi

git -C "$BASS" worktree add --detach "$WT" "$CANDIDATE_COMMIT" \
  >"$OUT/worktree.log" 2>&1
RC_WORKTREE=$?
"$PY_BOOT" -m venv "$VENV" >"$OUT/venv.log" 2>&1
RC_VENV=$?
summary worktree_rc "$RC_WORKTREE"
summary venv_rc "$RC_VENV"
if [ "$RC_WORKTREE" -ne 0 ] || [ "$RC_VENV" -ne 0 ]; then
  summary classification STOP_ISOLATION_CREATION_FAILURE
  summary receipt_dir "$OUT"
  exit 0
fi
PY="$VENV/bin/python"

HEAD="$(git -C "$WT" rev-parse HEAD 2>/dev/null)"
TREE="$(git -C "$WT" rev-parse HEAD^{tree} 2>/dev/null)"
summary candidate_head "$HEAD"
summary candidate_tree "$TREE"
if [ "$HEAD" != "$CANDIDATE_COMMIT" ] || [ "$TREE" != "$CANDIDATE_TREE" ]; then
  summary classification STOP_CANDIDATE_IDENTITY_MISMATCH
  summary receipt_dir "$OUT"
  exit 0
fi

# Provision the exact Python-oracle lock.
"$PY" -m pip install --disable-pip-version-check \
  -r "$WT/requirements.lock" >"$OUT/pip-lock.log" 2>&1
RC_LOCK=$?
summary lock_rc "$RC_LOCK"
if [ "$RC_LOCK" -ne 0 ]; then
  summary classification STOP_REQUIREMENTS_INSTALL_FAILED
  summary receipt_dir "$OUT"
  exit 0
fi

# Recover the exact immutable RF04 scalar-raw/RF02C wheel from Git bytes.
WHEEL="$OUT/bianchi_rustcore-0.1.0-cp312-cp312-manylinux_2_34_x86_64.whl"
git -C "$BASS" show "$TRUSTED_COMMIT:$TRUSTED_WHEEL_PATH" \
  >"$WHEEL" 2>"$OUT/extract-wheel.log"
RC_EXTRACT=$?
git -C "$BASS" show "$TRUSTED_COMMIT:$TRUSTED_RESTORE_PATH" \
  >"$OUT/RF02C_NATIVE_RESTORE.json" 2>"$OUT/extract-restore.log"
RC_RESTORE=$?
WHEEL_SHA="$(sha256sum "$WHEEL" 2>/dev/null | awk '{print $1}')"
summary extract_wheel_rc "$RC_EXTRACT"
summary extract_restore_rc "$RC_RESTORE"
summary trusted_wheel_sha256 "$WHEEL_SHA"
summary expected_wheel_sha256 "$TRUSTED_WHEEL_SHA"
if [ "$RC_EXTRACT" -ne 0 ] || [ "$RC_RESTORE" -ne 0 ] || \
   [ "$WHEEL_SHA" != "$TRUSTED_WHEEL_SHA" ]; then
  summary classification STOP_TRUSTED_WHEEL_RECOVERY_FAILURE
  summary receipt_dir "$OUT"
  exit 0
fi

# Install the trusted native payload, then the candidate Python tree.
"$PY" -m pip install --disable-pip-version-check --no-index --no-deps \
  --force-reinstall "$WHEEL" >"$OUT/pip-wheel.log" 2>&1
RC_WHEEL=$?
"$PY" -m pip install --disable-pip-version-check \
  'setuptools==68.1.2' 'wheel==0.42.0' >"$OUT/pip-build-system.log" 2>&1
RC_BUILD_SYSTEM=$?
(
  cd "$WT" || exit 97
  "$PY" -m pip install --disable-pip-version-check \
    --no-deps --no-build-isolation .
) >"$OUT/pip-project.log" 2>&1
RC_PROJECT=$?
summary wheel_install_rc "$RC_WHEEL"
summary build_system_rc "$RC_BUILD_SYSTEM"
summary project_install_rc "$RC_PROJECT"

# Verify the installed shared-object byte identity with the override unset.
(
  cd "$WT" || exit 97
  env -u BASS_ALLOW_UNVERIFIED_NATIVE_DEV PYTHONPATH="$WT" "$PY" - <<'PY'
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import bianchi_rustcore

root = Path(bianchi_rustcore.__file__).resolve().parent
extensions = sorted(root.glob("*.so"))
if len(extensions) != 1:
    raise SystemExit(f"expected exactly one native extension, found {extensions}")
so = extensions[0]
print(json.dumps({
    "module_file": str(Path(bianchi_rustcore.__file__).resolve()),
    "shared_object": str(so),
    "shared_object_sha256": hashlib.sha256(so.read_bytes()).hexdigest(),
}, indent=2, sort_keys=True))
PY
) >"$OUT/native-identity.json" 2>"$OUT/native-identity.err"
RC_NATIVE_ID=$?
SO_SHA="$(sed -n 's/.*"shared_object_sha256": "\([0-9a-f]*\)".*/\1/p' "$OUT/native-identity.json" | head -n1)"
summary native_identity_rc "$RC_NATIVE_ID"
summary shared_object_sha256 "${SO_SHA:-MISSING}"
summary expected_shared_object_sha256 "$TRUSTED_SO_SHA"

# Re-run the narrow protocol and canonical payload identity.
(
  cd "$WT" || exit 97
  env -u BASS_ALLOW_UNVERIFIED_NATIVE_DEV PYTHONPATH="$WT" "$PY" -m unittest -v \
    tests/research/test_bass_rec_source_protocol_red.py
) >"$OUT/focused.log" 2>&1
RC_FOCUSED=$?
summary focused_rc "$RC_FOCUSED"

HASHES="$OUT/hashes.txt"
: >"$HASHES"
for run in 1 2; do
  (
    cd "$WT" || exit 97
    env -u BASS_ALLOW_UNVERIFIED_NATIVE_DEV PYTHONPATH="$WT" "$PY" - <<'PY'
from bianchi.source_authority import SourceAuthorityBundle, SourceFrequencyKind
bundle = SourceAuthorityBundle.constant_pair(
    eta_s_inv=3.0,
    kappa_s_inv=2.0,
    frame="hydrogen_orthonormal",
    channel="total_occupation",
    source_sha256="0" * 64,
    frequency_kind=SourceFrequencyKind.POINTWISE_SPECTRAL,
)
print(bundle.payload_sha256)
PY
  ) >>"$HASHES" 2>>"$OUT/hash-errors.log"
done
HASH1="$(sed -n '1p' "$HASHES")"
HASH2="$(sed -n '2p' "$HASHES")"
summary hash1 "$HASH1"
summary hash2 "$HASH2"
summary golden "$GOLDEN_SOURCE_HASH"

# Critical production-provenance backend cone: no development override.
(
  cd "$WT" || exit 97
  env -u BASS_ALLOW_UNVERIFIED_NATIVE_DEV PYTHONPATH="$WT" "$PY" -m pytest -q \
    tests/test_backend_policy.py \
    tests/test_backend_integration.py \
    tests/test_backend_packaging.py
) >"$OUT/backend.log" 2>&1
RC_BACKEND=$?
summary backend_rc "$RC_BACKEND"

grep -n 'UnverifiedNativePayloadError\|UNVERIFIED_DEVELOPMENT_NATIVE_PAYLOAD' \
  "$OUT/backend.log" >"$OUT/forbidden-provenance-diagnostics.txt" 2>/dev/null
FORBIDDEN_LINES="$(wc -l <"$OUT/forbidden-provenance-diagnostics.txt" 2>/dev/null | tr -d ' ')"
summary forbidden_provenance_lines "${FORBIDDEN_LINES:-0}"
summary development_override unset

CLASSIFICATION='FAIL_R5D_TRUSTED_RF00_PAYLOAD_GATE'
if [ "$RC_WHEEL" -eq 0 ] && [ "$RC_BUILD_SYSTEM" -eq 0 ] && \
   [ "$RC_PROJECT" -eq 0 ] && [ "$RC_NATIVE_ID" -eq 0 ] && \
   [ "$SO_SHA" = "$TRUSTED_SO_SHA" ] && [ "$RC_FOCUSED" -eq 0 ] && \
   [ "$HASH1" = "$GOLDEN_SOURCE_HASH" ] && \
   [ "$HASH2" = "$GOLDEN_SOURCE_HASH" ] && \
   [ "$RC_BACKEND" -eq 0 ] && [ "${FORBIDDEN_LINES:-0}" -eq 0 ]; then
  CLASSIFICATION='PASS_R5D_TRUSTED_RF00_PAYLOAD_PROVENANCE_AND_BACKEND_GATE'
fi
summary classification "$CLASSIFICATION"
summary opens_R6 "$([ "$CLASSIFICATION" = 'PASS_R5D_TRUSTED_RF00_PAYLOAD_PROVENANCE_AND_BACKEND_GATE' ] && printf true || printf false)"
summary receipt_dir "$OUT"

sha256sum "$OUT"/* 2>/dev/null >"$OUT/SHA256SUMS" || true
printf '\nCaller checkout was not switched or modified.\n'
exit 0
