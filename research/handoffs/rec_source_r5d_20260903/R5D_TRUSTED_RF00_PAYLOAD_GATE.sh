#!/usr/bin/env bash
# REC-owned trusted-native gate for the current BASS R6 GREEN source.
# The caller checkout is never switched or edited. The script always exits 0
# after writing a machine-readable classification.

set +e
set +u
set +o pipefail 2>/dev/null || true
unset BASS_ALLOW_UNVERIFIED_NATIVE_DEV

SOURCE_BRANCH='research/bass-rec-source-r6-hardening-green-20260904-r1'
SOURCE_COMMIT='92d67dc79cf645947beb93ac01a9505ee277dabd'
SOURCE_TREE='65cb63e6d08e80e9a8f38f83e3a536cb0a00a693'
SOURCE_BLOB='869677390004f68aef9f547e6556f5f1c15bd012'
R5_TEST_BLOB='db336d64633d8a9552bc3613c588a00f33404a4d'
R6_TEST_BLOB='49be9546c4655bc5ca330bc31ae2daf07578b74f'

TRUSTED_BRANCH='agent/architecture/rf04-scalar-raw-20260829-fhxMnS'
TRUSTED_COMMIT='50b6e9f7a6741b7fd25b0421d2a674b9eb92cdda'
TRUSTED_WHEEL_PATH='artifacts/rust_first_runtime/rf04/scalar_raw/native_delta/rf02c-wheel/bianchi_rustcore-0.1.0-cp312-cp312-manylinux_2_34_x86_64.whl'
TRUSTED_RESTORE_PATH='artifacts/rust_first_runtime/rf04/scalar_raw/native_delta/RF02C_NATIVE_RESTORE.json'
TRUSTED_WHEEL_SHA='99bd0596642dd31ca82080fb24306cd9bf3f6dd1ad3f68a1380f77378e266302'
TRUSTED_SO_SHA='5d5b8197518d8637b14e0c78b871802ed64f6506c7a95128f31bd52044a98633'

SOURCE_HASH='7f0db7e1cf7423ff6751a21ab4002ef8f13d89f788a8a746b26992abecf791e8'
BINDING_HASH='54762aa915b3fa0da847676a3d4491b8f7f2f358e48dd275fffee84ba6496093'

STAMP="$(date -u +%Y%m%dT%H%M%SZ 2>/dev/null)"
[ -n "$STAMP" ] || STAMP='UNKNOWN_TIME'
ROOT="${RECEIPT_ROOT:-$HOME/Dropbox/bianchi/_runtime_receipts}"
OUT="$ROOT/BASS_REC_SOURCE_R5D_V2_$STAMP"
mkdir -p "$OUT" 2>/dev/null

stop_gate() {
  printf 'classification=%s\ndetail=%s\nreceipt_dir=%s\n' \
    "$1" "$2" "$OUT" | tee "$OUT/summary.txt"
  exit 0
}

[ -d "$OUT" ] || {
  printf 'classification=STOP_RECEIPT_DIRECTORY_UNAVAILABLE\n'
  exit 0
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
[ -n "$BASS" ] || stop_gate STOP_BASS_REPOSITORY_NOT_FOUND \
  'Set BASS_REPO=/absolute/path/to/bass and rerun.'
BASS_ORIGIN="$(git -C "$BASS" config --get remote.origin.url 2>/dev/null)"

PYBOOT="${PYTHON_BOOTSTRAP:-$(command -v python3.12 2>/dev/null)}"
[ -x "$PYBOOT" ] || PYBOOT="$(command -v python 2>/dev/null)"
[ -x "$PYBOOT" ] || stop_gate STOP_PYTHON_NOT_FOUND 'Python 3.12 is required.'
PYVER="$($PYBOOT -c 'import sys; print(".".join(map(str,sys.version_info[:3])))' 2>/dev/null)"
case "$PYVER" in 3.12.*) ;; *) stop_gate STOP_PYTHON_3_12_REQUIRED "$PYVER" ;; esac

git -C "$BASS" fetch --no-tags origin \
  "$SOURCE_BRANCH:refs/remotes/origin/$SOURCE_BRANCH" \
  "$TRUSTED_BRANCH:refs/remotes/origin/$TRUSTED_BRANCH" \
  >"$OUT/fetch.log" 2>&1
RC_FETCH=$?
SOURCE_HEAD="$(git -C "$BASS" rev-parse "refs/remotes/origin/$SOURCE_BRANCH" 2>/dev/null)"
TRUSTED_HEAD="$(git -C "$BASS" rev-parse "refs/remotes/origin/$TRUSTED_BRANCH" 2>/dev/null)"
if [ "$RC_FETCH" -ne 0 ] || [ -z "$SOURCE_HEAD" ] || \
   [ "$TRUSTED_HEAD" != "$TRUSTED_COMMIT" ]; then
  stop_gate STOP_REMOTE_IDENTITY_MISMATCH \
    "fetch=$RC_FETCH source=${SOURCE_HEAD:-MISSING} trusted=${TRUSTED_HEAD:-MISSING}"
fi

git -C "$BASS" merge-base --is-ancestor "$SOURCE_COMMIT" "$SOURCE_HEAD" \
  >/dev/null 2>&1
[ "$?" -eq 0 ] || stop_gate STOP_SOURCE_NOT_PUBLICATION_ANCESTOR "$SOURCE_HEAD"

TMP="$(mktemp -d /tmp/bass-r5d-v2.XXXXXX 2>/dev/null)"
[ -d "$TMP" ] || stop_gate STOP_TEMP_DIRECTORY_FAILURE "$TMP"
WT="$TMP/worktree"
STAGE="$TMP/stage"
VENV="$TMP/venv"

cleanup() {
  git -C "$BASS" worktree remove --force "$WT" >/dev/null 2>&1 || true
  case "$TMP" in /tmp/bass-r5d-v2.*) rm -rf -- "$TMP" >/dev/null 2>&1 || true ;; esac
}
trap cleanup EXIT HUP INT TERM

git -C "$BASS" worktree add --detach "$WT" "$SOURCE_COMMIT" \
  >"$OUT/worktree.log" 2>&1
RC_WT=$?
[ "$RC_WT" -eq 0 ] || stop_gate STOP_WORKTREE_FAILURE "$RC_WT"

ACTUAL_COMMIT="$(git -C "$WT" rev-parse HEAD 2>/dev/null)"
ACTUAL_TREE="$(git -C "$WT" rev-parse HEAD^{tree} 2>/dev/null)"
ACTUAL_SOURCE_BLOB="$(git -C "$WT" hash-object bianchi/source_authority.py 2>/dev/null)"
ACTUAL_R5_BLOB="$(git -C "$WT" hash-object tests/research/test_bass_rec_source_protocol_red.py 2>/dev/null)"
ACTUAL_R6_BLOB="$(git -C "$WT" hash-object tests/research/test_bass_rec_source_protocol_r6_red.py 2>/dev/null)"
if [ "$ACTUAL_COMMIT" != "$SOURCE_COMMIT" ] || \
   [ "$ACTUAL_TREE" != "$SOURCE_TREE" ] || \
   [ "$ACTUAL_SOURCE_BLOB" != "$SOURCE_BLOB" ] || \
   [ "$ACTUAL_R5_BLOB" != "$R5_TEST_BLOB" ] || \
   [ "$ACTUAL_R6_BLOB" != "$R6_TEST_BLOB" ]; then
  stop_gate STOP_SOURCE_IDENTITY_MISMATCH \
    "$ACTUAL_COMMIT $ACTUAL_TREE $ACTUAL_SOURCE_BLOB $ACTUAL_R5_BLOB $ACTUAL_R6_BLOB"
fi

mkdir -p "$STAGE"
git -C "$BASS" archive --format=tar --output="$TMP/source.tar" \
  "$SOURCE_COMMIT" >"$OUT/archive.log" 2>&1
RC_ARCHIVE=$?
tar -xf "$TMP/source.tar" -C "$STAGE" >"$OUT/extract.log" 2>&1
RC_EXTRACT=$?
if [ "$RC_ARCHIVE" -ne 0 ] || [ "$RC_EXTRACT" -ne 0 ]; then
  stop_gate STOP_SOURCE_STAGING_FAILURE \
    "archive=$RC_ARCHIVE extract=$RC_EXTRACT"
fi
STAGED_SOURCE_BLOB="$(git -C "$BASS" hash-object "$STAGE/bianchi/source_authority.py" 2>/dev/null)"
[ "$STAGED_SOURCE_BLOB" = "$SOURCE_BLOB" ] || \
  stop_gate STOP_STAGED_SOURCE_IDENTITY_MISMATCH "$STAGED_SOURCE_BLOB"

"$PYBOOT" -m venv "$VENV" >"$OUT/venv.log" 2>&1
RC_VENV=$?
[ "$RC_VENV" -eq 0 ] || stop_gate STOP_VENV_FAILURE "$RC_VENV"
PY="$VENV/bin/python"

"$PY" -m pip install --disable-pip-version-check -r "$WT/requirements.lock" \
  >"$OUT/pip-lock.log" 2>&1
RC_LOCK=$?
[ "$RC_LOCK" -eq 0 ] || stop_gate STOP_REQUIREMENTS_INSTALL_FAILED "$RC_LOCK"

WHEEL="$OUT/bianchi_rustcore-0.1.0-cp312-cp312-manylinux_2_34_x86_64.whl"
git -C "$BASS" show "$TRUSTED_COMMIT:$TRUSTED_WHEEL_PATH" \
  >"$WHEEL" 2>"$OUT/extract-wheel.log"
RC_WHEEL_EXTRACT=$?
git -C "$BASS" show "$TRUSTED_COMMIT:$TRUSTED_RESTORE_PATH" \
  >"$OUT/RF02C_NATIVE_RESTORE.json" 2>"$OUT/extract-restore.log"
RC_RESTORE_EXTRACT=$?
WHEEL_SHA="$(sha256sum "$WHEEL" 2>/dev/null | awk '{print $1}')"
if [ "$RC_WHEEL_EXTRACT" -ne 0 ] || [ "$RC_RESTORE_EXTRACT" -ne 0 ] || \
   [ "$WHEEL_SHA" != "$TRUSTED_WHEEL_SHA" ]; then
  stop_gate STOP_TRUSTED_WHEEL_RECOVERY_FAILURE \
    "wheel=$RC_WHEEL_EXTRACT restore=$RC_RESTORE_EXTRACT sha=${WHEEL_SHA:-MISSING}"
fi

"$PY" -m pip install --disable-pip-version-check --no-index --no-deps \
  --force-reinstall "$WHEEL" >"$OUT/pip-wheel.log" 2>&1
RC_WHEEL_INSTALL=$?
"$PY" -m pip install --disable-pip-version-check \
  'setuptools==68.1.2' 'wheel==0.42.0' >"$OUT/pip-build-system.log" 2>&1
RC_BUILD_SYSTEM=$?
(
  cd "$STAGE" || exit 97
  env -u BASS_ALLOW_UNVERIFIED_NATIVE_DEV \
    "$PY" -m pip install --disable-pip-version-check \
      --no-deps --no-build-isolation .
) >"$OUT/pip-project-from-stage.log" 2>&1
RC_PROJECT=$?
if [ "$RC_WHEEL_INSTALL" -ne 0 ] || [ "$RC_BUILD_SYSTEM" -ne 0 ] || \
   [ "$RC_PROJECT" -ne 0 ]; then
  stop_gate STOP_PROJECT_INSTALL_FAILURE \
    "wheel=$RC_WHEEL_INSTALL build_system=$RC_BUILD_SYSTEM project=$RC_PROJECT"
fi

(
  cd "$WT" || exit 97
  env -u BASS_ALLOW_UNVERIFIED_NATIVE_DEV PYTHONPATH="$WT" "$PY" - <<'PY'
from __future__ import annotations
import hashlib
from importlib import metadata
import json
from pathlib import Path
import bianchi
from bianchi import backend_policy
import bianchi_rustcore
import jax
root = Path(bianchi_rustcore.__file__).resolve().parent
extensions = sorted(root.glob("*.so"))
if len(extensions) != 1:
    raise SystemExit(f"expected exactly one native extension, found {extensions}")
load = backend_policy.load_native()
if not load.available or load.module is None:
    raise SystemExit(f"native load unavailable: {load!r}")
so = extensions[0]
print(json.dumps({
    "bianchi_source": str(Path(bianchi.__file__).resolve()),
    "native_distribution_version": metadata.version("bianchi-rustcore"),
    "root_distribution_version": metadata.version("bianchi-solver"),
    "jax_version": jax.__version__,
    "shared_object": str(so),
    "shared_object_sha256": hashlib.sha256(so.read_bytes()).hexdigest(),
    "native_load_available": load.available,
    "development_override_present": False,
}, indent=2, sort_keys=True))
PY
) >"$OUT/native-identity.json" 2>"$OUT/native-identity.err"
RC_NATIVE_ID=$?
SO_SHA="$(sed -n 's/.*"shared_object_sha256": "\([0-9a-f]*\)".*/\1/p' "$OUT/native-identity.json" | head -n 1)"

(
  cd "$WT" || exit 97
  env -u BASS_ALLOW_UNVERIFIED_NATIVE_DEV PYTHONPATH="$WT" "$PY" \
    -m unittest -q \
      tests/research/test_bass_rec_source_protocol_red.py \
      tests/research/test_bass_rec_source_protocol_r6_red.py
) >"$OUT/focused.log" 2>&1
RC_FOCUSED=$?

: >"$OUT/source-hashes.txt"
: >"$OUT/binding-hashes.txt"
for run_index in 1 2; do
  (
    cd "$WT" || exit 97
    env -u BASS_ALLOW_UNVERIFIED_NATIVE_DEV PYTHONPATH="$WT" "$PY" - <<'PY'
from bianchi.source_authority import SourceAuthorityBundle, SourceFrequencyKind
b = SourceAuthorityBundle.constant_pair(
    eta_s_inv=3.0, kappa_s_inv=2.0,
    frame="hydrogen_orthonormal", channel="total_occupation",
    source_sha256="0" * 64,
    frequency_kind=SourceFrequencyKind.POINTWISE_SPECTRAL,
)
print(b.payload_sha256)
PY
  ) >>"$OUT/source-hashes.txt" 2>>"$OUT/hash-errors.log"
  (
    cd "$WT" || exit 97
    env -u BASS_ALLOW_UNVERIFIED_NATIVE_DEV PYTHONPATH="$WT" "$PY" - <<'PY'
from bianchi.source_authority import IntegratedMomentMapBinding, SourceStateKind
b = IntegratedMomentMapBinding.create(
    target_state_kind=SourceStateKind.RADIAL_INTEGRATED_ANGULAR_GRID,
    moment_map_sha256="1" * 64,
    radial_weight_family_sha256="2" * 64,
    source_sha256="3" * 64,
)
print(b.binding_sha256)
PY
  ) >>"$OUT/binding-hashes.txt" 2>>"$OUT/hash-errors.log"
done
S1="$(sed -n '1p' "$OUT/source-hashes.txt")"
S2="$(sed -n '2p' "$OUT/source-hashes.txt")"
B1="$(sed -n '1p' "$OUT/binding-hashes.txt")"
B2="$(sed -n '2p' "$OUT/binding-hashes.txt")"
HASHES_PASS=false
if [ "$S1" = "$SOURCE_HASH" ] && [ "$S2" = "$SOURCE_HASH" ] && \
   [ "$B1" = "$BINDING_HASH" ] && [ "$B2" = "$BINDING_HASH" ]; then
  HASHES_PASS=true
fi

(
  cd "$WT" || exit 97
  env -u BASS_ALLOW_UNVERIFIED_NATIVE_DEV PYTHONPATH="$WT" "$PY" \
    -m pytest -q \
      tests/test_backend_policy.py \
      tests/test_backend_integration.py \
      tests/test_backend_packaging.py
) >"$OUT/backend.log" 2>&1
RC_BACKEND=$?

grep -nE 'UnverifiedNativePayloadError|UNVERIFIED_DEVELOPMENT_NATIVE_PAYLOAD|UnverifiedNativeDevelopmentWarning' \
  "$OUT/backend.log" >"$OUT/forbidden-provenance-diagnostics.txt" 2>/dev/null || true
FORBIDDEN="$(wc -l <"$OUT/forbidden-provenance-diagnostics.txt" 2>/dev/null | tr -d ' ')"
[ -n "$FORBIDDEN" ] || FORBIDDEN=0

git -C "$WT" status --porcelain=v1 --untracked-files=all \
  >"$OUT/source-worktree-status.txt"
CLEAN=false
[ ! -s "$OUT/source-worktree-status.txt" ] && CLEAN=true
find "$STAGE" -maxdepth 3 \
  \( -type d -name build -o -type d -name '*.egg-info' \) \
  -print 2>/dev/null | sort >"$OUT/staging-artifact-inventory.txt"

CLASS='FAIL_R5D_TRUSTED_RF00_PAYLOAD_GATE'
if [ "$RC_NATIVE_ID" -eq 0 ] && [ "$SO_SHA" = "$TRUSTED_SO_SHA" ] && \
   [ "$RC_FOCUSED" -eq 0 ] && [ "$HASHES_PASS" = true ] && \
   [ "$RC_BACKEND" -eq 0 ] && [ "$FORBIDDEN" -eq 0 ] && \
   [ "$CLEAN" = true ]; then
  CLASS='PASS_R5D_TRUSTED_RF00_PAYLOAD_PROVENANCE_AND_BACKEND_GATE'
fi

cat >"$OUT/summary.txt" <<EOF
classification=$CLASS
source_publication_head=$SOURCE_HEAD
source_commit=$ACTUAL_COMMIT
source_tree=$ACTUAL_TREE
source_blob=$ACTUAL_SOURCE_BLOB
r5_test_blob=$ACTUAL_R5_BLOB
r6_test_blob=$ACTUAL_R6_BLOB
trusted_commit=$TRUSTED_COMMIT
trusted_wheel_sha256=$WHEEL_SHA
trusted_shared_object_sha256=${SO_SHA:-MISSING}
python=$PYVER
native_identity_rc=$RC_NATIVE_ID
focused_rc=$RC_FOCUSED
backend_rc=$RC_BACKEND
forbidden_provenance_lines=$FORBIDDEN
deterministic_golden_hashes=$HASHES_PASS
source_hash_1=$S1
source_hash_2=$S2
binding_hash_1=$B1
binding_hash_2=$B2
clean_source_worktree=$CLEAN
root_package_build_location=NON_GIT_STAGING_DIRECTORY
development_override=unset
opens_R7_only_with_R6C=$([ "$CLASS" = 'PASS_R5D_TRUSTED_RF00_PAYLOAD_PROVENANCE_AND_BACKEND_GATE' ] && echo true || echo false)
receipt_dir=$OUT
EOF
cat "$OUT/summary.txt"

cat >"$OUT/R5D_TRUSTED_PAYLOAD_RECEIPT.json" <<EOF
{
  "schema_version": "2.0.0",
  "stage": "BASS_REC_SOURCE_R5D_TRUSTED_RF00_PAYLOAD_PROVENANCE_GATE",
  "classification": "$CLASS",
  "source_commit": "$ACTUAL_COMMIT",
  "source_tree": "$ACTUAL_TREE",
  "trusted_wheel_sha256": "$WHEEL_SHA",
  "trusted_shared_object_sha256": "${SO_SHA:-MISSING}",
  "native_identity_rc": $RC_NATIVE_ID,
  "focused_rc": $RC_FOCUSED,
  "backend_rc": $RC_BACKEND,
  "forbidden_provenance_lines": $FORBIDDEN,
  "deterministic_golden_hashes": $HASHES_PASS,
  "clean_source_worktree": $CLEAN,
  "development_override": "unset",
  "r7_gate_logic": "R6C_PASS_AND_R5D_PASS",
  "claim_boundary": {
    "physical_REC_source_integration": false,
    "grid_PSTF_adapter": false,
    "grid_PSTF_parity": false,
    "physical_face": false,
    "provider_export": false,
    "pass_REC_physical_split": false,
    "pass_RF04": false
  }
}
EOF

sha256sum "$OUT"/* >"$OUT/SHA256SUMS" 2>/dev/null || true
printf '\nCaller checkout was not switched or modified.\n'
exit 0
