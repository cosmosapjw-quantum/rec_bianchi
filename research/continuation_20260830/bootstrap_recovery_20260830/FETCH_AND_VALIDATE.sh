#!/usr/bin/env bash
set -euo pipefail

usage() {
  echo "usage: FETCH_AND_VALIDATE.sh --repo ABSOLUTE_REPOSITORY_PATH" >&2
  exit 64
}

repo=""
while (($#)); do
  case "$1" in
    --repo)
      (($# >= 2)) || usage
      repo="$2"
      shift 2
      ;;
    *) usage ;;
  esac
done

[[ -n "$repo" && "$repo" = /* ]] || usage
repo="$(git -C "$repo" rev-parse --show-toplevel)"
package="$repo/research/continuation_20260830/bootstrap_recovery_20260830"

python3 "$repo/research/continuation_20260830/verify_payload.py" \
  --root "$repo" --repo "$repo"

python3 "$package/validate_package.py" --root "$repo" --repo "$repo"
