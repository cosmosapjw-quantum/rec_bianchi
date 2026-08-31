#!/usr/bin/env python3
"""Read-only contract checks and isolated REC-NEXT-03 formal executions.

The formal sources describe conditional, nonauthoritative mathematics.  This
runner deliberately cannot turn a successful CAS/proof-assistant execution
into source, implementation, physical-face, or production authority.

The default ``--check-contract`` mode only reads the repository.  ``--run-all``
copies the formal input tree to a caller-selected directory outside every Git
worktree and confines subprocess homes, caches, temporary files, build products,
raw logs, versions, and reports to that directory.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import signal
import shutil
import subprocess
import sys
import tarfile
import time
import tomllib
from typing import Any, Iterable, Mapping, Sequence


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
FORMAL_ROOT = REPOSITORY_ROOT / "formal" / "rec_next03"

AUTHORITY = "NONAUTHORITATIVE_CONDITIONAL_FORMAL_CHECK"
PHYSICAL_AUTHORITY_STATUS = "NOT_ESTABLISHED"
SOURCE_AUTHORITY_STATUS = "NOT_ESTABLISHED"
XACT_ARCHIVE_SHA256 = "7a6c5f600868a3922668b020a15c0692f76574ff2a559808c62d460cef1b07be"
MATHLIB_TAG = "v4.33.0"
MATHLIB_COMMIT = "db584cd6d46c92f209a44c0f1c829460d327499d"
MATHLIB_GIT_URL = "https://github.com/leanprover-community/mathlib4.git"
SCIENTIFIC_TERMINAL = (
    "BLOCKED_REC_PHYSICAL_INTERFACE_DEFECT / "
    "SOURCE_DEFINED_26_DIRECTION_FACE_RECONSTRUCTION_ABSENT"
)
SCIENTIFIC_CLAIM = "NO_PASS_REC_PHYSICAL_SPLIT"

EXPECTED_FILES = (
    "CONTRACT.md",
    "OBLIGATIONS.json",
    "README.md",
    "SOURCE_MAP.json",
    "TOOLCHAINS.lock.json",
    "lean/RecNext03.lean",
    "lean/RecNext03/All.lean",
    "lean/RecNext03/Contracts.lean",
    "lean/lakefile.toml",
    "lean/lean-toolchain",
    "prompts/lean.json",
    "prompts/rocq.json",
    "prompts/sage.json",
    "prompts/wolfram.json",
    "rocq/All.v",
    "rocq/RecNext03Contracts.v",
    "rocq/_CoqProject",
    "rocq/rocq-toolchain",
    "sage/verify_remap_event.sage",
    "wolfram/verify_frame_face_event.wls",
)

EXPECTED_JSON_SCHEMAS = {
    "OBLIGATIONS.json": "rec-next03-formal-obligations/v1",
    "SOURCE_MAP.json": "rec-next03-source-map/v1",
    "TOOLCHAINS.lock.json": "rec-next03-toolchains-lock/v1",
    "prompts/lean.json": "rec-next03-local-formal-prompt/v1",
    "prompts/rocq.json": "rec-next03-local-formal-prompt/v1",
    "prompts/sage.json": "rec-next03-local-formal-prompt/v1",
    "prompts/wolfram.json": "rec-next03-local-formal-prompt/v1",
}

GENERATED_COMPONENTS = {
    ".lake",
    "__pycache__",
}
GENERATED_SUFFIXES = {
    ".aux",
    ".glob",
    ".olean",
    ".pyc",
    ".vos",
    ".vok",
    ".vo",
}

LEAN_BANS = (
    ("lean_sorry", re.compile(r"\bsorry\b", re.IGNORECASE)),
    ("lean_admit", re.compile(r"\badmit\b", re.IGNORECASE)),
    (
        "lean_axiom_declaration",
        re.compile(
            r"(?m)^[ \t]*(?:(?:private|protected|local|scoped|noncomputable|unsafe)\s+)*"
            r"(?:axiom|axioms)\b",
            re.IGNORECASE,
        ),
    ),
    (
        "lean_constant_declaration",
        re.compile(
            r"(?m)^[ \t]*(?:(?:private|protected|local|scoped|noncomputable|unsafe)\s+)*"
            r"(?:constant|constants)\b",
            re.IGNORECASE,
        ),
    ),
)
ROCQ_BANS = (
    ("rocq_admitted", re.compile(r"\bAdmitted\s*\.", re.IGNORECASE)),
    ("rocq_admit", re.compile(r"\badmit\b", re.IGNORECASE)),
    (
        "rocq_parameter",
        re.compile(
            r"(?m)^[ \t]*(?:#\[[^\]\n]+\][ \t]*)*"
            r"(?:(?:Local|Global)\s+)?(?:Parameter|Parameters)\b",
            re.IGNORECASE,
        ),
    ),
    (
        "rocq_axiom",
        re.compile(
            r"(?m)^[ \t]*(?:#\[[^\]\n]+\][ \t]*)*"
            r"(?:(?:Local|Global)\s+)?(?:Axiom|Axioms)\b",
            re.IGNORECASE,
        ),
    ),
    (
        "rocq_conjecture",
        re.compile(
            r"(?m)^[ \t]*(?:#\[[^\]\n]+\][ \t]*)*"
            r"(?:(?:Local|Global)\s+)?(?:Conjecture|Conjectures)\b",
            re.IGNORECASE,
        ),
    ),
)
WOLFRAM_BANS = (
    ("wolfram_network", re.compile(r"\b(?:URLRead|URLExecute|URLDownload)\b")),
    ("wolfram_process", re.compile(r"\b(?:RunProcess|StartProcess)\b")),
)
SAGE_BANS = (
    ("sage_network", re.compile(r"\b(?:requests|urllib|socket)\b")),
    ("sage_process", re.compile(r"\b(?:subprocess|os\.system|os\.popen)\b")),
)

SAFE_AUTHORITY_MARKERS = (
    "NONAUTHORITATIVE",
    "NOT_AUTHORITATIVE",
    "NOT_ESTABLISHED",
    "NOT_APPROVED",
    "PROPOSED",
    "SPECIFIED",
    "UNAPPROVED",
    "UNRESOLVED",
    "EXTERNAL_AUTHORITY_REQUIRED",
    "FORMAL_ONLY",
)
POSITIVE_CLAIM_VALUES = {
    "ADMITTED",
    "APPROVED",
    "AUTHORITATIVE",
    "ESTABLISHED",
    "PASS",
    "PASSED",
    "PHYSICAL_AUTHORITY",
    "PRODUCTION_AUTHORITY",
    "READY",
    "RESOLVED",
    "SOURCE_IDENTICAL",
    "TRUE",
    "VALIDATED",
}
ENVIRONMENT_GAP_EXIT_CODES = {69, 127}
ENVIRONMENT_GAP_PATTERNS = (
    "command not found",
    "could not find",
    "library not found",
    "missing dependency",
    "no such file or directory",
    "unknown module 'mathlib'",
    'unknown package "mathlib"',
    "unknown package 'mathlib'",
    "xact unavailable",
)
WOLFRAM_LICENSE_SLOT_BUSY_PATTERNS = (
    "all available licenses are in use",
    "all licenses are in use",
    "license limit reached",
    "license quota reached",
    "maximum number of concurrent",
    "maximum number of kernels",
    "maximum number of processes",
    "license server is busy",
    "license temporarily unavailable",
    "could not obtain a license",
    "cannot obtain a license",
)
WOLFRAM_LICENSE_AVAILABILITY_MARKERS = ("license", "activation", "activated")
WOLFRAM_LICENSE_WAIT_DEFAULT_SECONDS = 3600
WOLFRAM_LICENSE_POLL_DEFAULT_SECONDS = 30

CLEARED_SEARCH_OVERRIDES = (
    "COQBIN",
    "COQLIB",
    "COQPATH",
    "LAKE_HOME",
    "LEAN_PATH",
    "LEAN_SRC_PATH",
    "MATHEMATICA_USERBASE",
    "MATHLIB",
    "OCAMLPATH",
    "PYTHONHOME",
    "PYTHONPATH",
    "ROCQLIB",
    "ROCQPATH",
    "SAGE_PATH",
    "SINGULARPATH",
    "WOLFRAM_USERBASE",
)

CLEARED_LEAN_CACHE_OVERRIDES = (
    "LAKE_ARTIFACT_CACHE",
    "LAKE_CACHE_DIR",
    "LAKE_CACHE_URL",
    "LAKE_RESTORE_ARTIFACTS",
    "MATHLIB_CACHE_DIR",
)

NETWORK_PREFIX_ENV = "_REC_NEXT03_NETWORK_NAMESPACE_PREFIX_JSON"
NETWORK_GAP_REASON = "ENVIRONMENT_GAP_NETWORK_ISOLATION_UNAVAILABLE_NOT_PASS"
NETWORK_PREFIX_ARGUMENTS = (
    "--user",
    "--map-root-user",
    "--net",
    "--fork",
    "--",
)

LEAN_RUNTIME_ARTIFACT_SUFFIXES = (".ilean", ".olean")

LEAN_EXPECTED_THEOREMS = (
    "RecNext03.h_eq_two_pi_hbar",
    "RecNext03.energy_per_unit_from_ordinary_frequency",
    "RecNext03.photon_null_of_orthonormal_tetrad_direction",
    "RecNext03.vFace_static",
    "RecNext03.vFace_static_pos_iff",
    "RecNext03.vFace_static_neg_iff",
    "RecNext03.vFace_static_zero_iff",
    "RecNext03.upwindFlux_positive",
    "RecNext03.upwindFlux_negative",
    "RecNext03.upwindFlux_zero",
    "RecNext03.classifyRed_positive",
    "RecNext03.classifyBlue_negative",
    "RecNext03.classifyRed_zero",
    "RecNext03.classifyBlue_zero",
    "RecNext03.upwind_right_zero_secant",
    "RecNext03.upwind_left_zero_secant",
    "RecNext03.zero_secants_agree_iff",
    "RecNext03.depositPacketRate_value",
    "RecNext03.remap_number_identity",
    "RecNext03.remap_gcl_left",
    "RecNext03.remap_gcl_right",
    "RecNext03.remap_jvp_left",
    "RecNext03.remap_jvp_right",
    "RecNext03.event_tags_pairwise_distinct",
    "RecNext03.restart_preserves_accepted_parent",
)
ROCQ_EXPECTED_THEOREMS = tuple(name.removeprefix("RecNext03.") for name in LEAN_EXPECTED_THEOREMS)
LEAN_ALLOWED_AXIOMS = ("propext", "Classical.choice", "Quot.sound")
ROCQ_ALLOWED_FOUNDATIONS = (
    {
        "name_prefix": "Rdefinitions.RbaseSymbolsImpl.",
        "required_origin": "Stdlib.Reals.Rdefinitions",
    },
    {"name_prefix": "Raxioms.", "required_origin": "Stdlib.Reals.Raxioms"},
    {
        "exact_name": "Classical_Prop.classic",
        "required_origin": "Stdlib.Logic.Classical_Prop",
    },
)


class ContractError(ValueError):
    """Raised for deterministic formal contract violations."""


def _canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        allow_nan=False,
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    ) + "\n"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _duplicate_rejecting_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ContractError(f"duplicate JSON key: {key!r}")
        result[key] = value
    return result


def _reject_json_constant(value: str) -> None:
    raise ContractError(f"non-finite JSON constant: {value}")


def _load_json_text(text: str, *, source: str) -> Any:
    try:
        return json.loads(
            text,
            object_pairs_hook=_duplicate_rejecting_object,
            parse_constant=_reject_json_constant,
        )
    except (json.JSONDecodeError, ContractError) as exc:
        raise ContractError(f"{source}: invalid strict JSON: {exc}") from exc


def _is_within(path: Path, ancestor: Path) -> bool:
    return path == ancestor or ancestor in path.parents


def _nearest_existing(path: Path) -> Path:
    candidate = path
    while not candidate.exists():
        if candidate.parent == candidate:
            break
        candidate = candidate.parent
    return candidate


def _git_container(path: Path) -> Path | None:
    candidate = _nearest_existing(path)
    if candidate.is_file():
        candidate = candidate.parent
    while True:
        if (candidate / ".git").exists():
            return candidate
        if candidate.parent == candidate:
            return None
        candidate = candidate.parent


def _normalise_key(key: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", key.lower()).strip("_")


def _is_positive_claim(value: Any) -> bool:
    if value is True:
        return True
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return value != 0
    if not isinstance(value, str):
        return False
    upper = re.sub(r"[^A-Z0-9]+", "_", value.upper()).strip("_")
    if any(marker in upper for marker in SAFE_AUTHORITY_MARKERS):
        return False
    return upper in POSITIVE_CLAIM_VALUES or any(
        upper.startswith(prefix)
        for prefix in (
            "ADMITTED_",
            "APPROVED_",
            "PHYSICAL_AUTHORITY_",
            "PRODUCTION_AUTHORITY_",
            "SOURCE_IDENTICAL_",
        )
    )


def _dangerous_admission_key(key: str) -> bool:
    normalised = _normalise_key(key)
    direct = {
        "admission_allowed",
        "admission_ready",
        "physical_admission",
        "physical_admission_status",
        "physical_authority",
        "physical_authority_status",
        "physical_face_admitted",
        "physical_face_materialized",
        "production_admission",
        "production_ready",
        "source_authority_resolved",
        "source_identical",
        "source_identical_admission",
    }
    if normalised in direct:
        return True
    return bool(
        re.search(
            r"(?:physical|production|source_identical|source_authority).*"
            r"(?:admission|admitted|approved|authority|materialized|pass|ready|resolved)",
            normalised,
        )
        or re.search(
            r"(?:clear|resolve|remove).*"
            r"(?:authority|blocker|physical|production|source)",
            normalised,
        )
    )


def _validate_authority_value(value: Any, *, location: str, errors: list[str]) -> None:
    if not isinstance(value, str):
        return
    upper = value.upper()
    if any(marker in upper for marker in SAFE_AUTHORITY_MARKERS):
        return
    if any(
        marker in upper
        for marker in (
            "AUTHORITATIVE",
            "PHYSICAL_AUTHORITY",
            "PRODUCTION_AUTHORITY",
            "SOURCE_IDENTICAL",
        )
    ):
        errors.append(f"{location}: unqualified authority value {value!r}")


def _audit_json_claims(value: Any, *, location: str, errors: list[str]) -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            child_location = f"{location}.{key}"
            if _dangerous_admission_key(key) and _is_positive_claim(child):
                errors.append(
                    f"{child_location}: formal data cannot grant admission/authority: {child!r}"
                )
            if "authority" in _normalise_key(key):
                _validate_authority_value(child, location=child_location, errors=errors)
            _audit_json_claims(child, location=child_location, errors=errors)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _audit_json_claims(child, location=f"{location}[{index}]", errors=errors)


def _strip_comments_and_strings(text: str, *, lean: bool) -> str:
    """Return code-shaped text while preserving offsets and line numbers.

    Lean and Rocq both have nested block comments.  Only Lean has ``--`` line
    comments.  String contents are also blanked so a quoted audit description
    cannot trigger (or conceal) a declaration-command detector.
    """

    result = list(text)
    index = 0
    block_depth = 0
    in_string = False
    escaped = False
    while index < len(text):
        if block_depth:
            if text.startswith("/-" if lean else "(*", index):
                block_depth += 1
                result[index : index + 2] = "  "
                index += 2
                continue
            if text.startswith("-/" if lean else "*)", index):
                block_depth -= 1
                result[index : index + 2] = "  "
                index += 2
                continue
            if text[index] != "\n":
                result[index] = " "
            index += 1
            continue
        if in_string:
            character = text[index]
            if character != "\n":
                result[index] = " "
            if escaped:
                escaped = False
            elif character == "\\":
                escaped = True
            elif character == '"':
                in_string = False
            index += 1
            continue
        if text.startswith("/-" if lean else "(*", index):
            block_depth = 1
            result[index : index + 2] = "  "
            index += 2
            continue
        if lean and text.startswith("--", index):
            end = text.find("\n", index)
            if end == -1:
                end = len(text)
            result[index:end] = " " * (end - index)
            index = end
            continue
        if text[index] == '"':
            in_string = True
            result[index] = " "
            index += 1
            continue
        index += 1
    return "".join(result)


def _source_ban_errors(relative: str, text: str) -> list[str]:
    errors: list[str] = []
    if relative.endswith(".lean"):
        bans = LEAN_BANS
        scanned_text = _strip_comments_and_strings(text, lean=True)
    elif relative.endswith(".v"):
        bans = ROCQ_BANS
        scanned_text = _strip_comments_and_strings(text, lean=False)
    elif relative.endswith(".wls"):
        bans = WOLFRAM_BANS
        scanned_text = text
    elif relative.endswith(".sage"):
        bans = SAGE_BANS
        scanned_text = text
    else:
        bans = ()
        scanned_text = text
    for ban_id, pattern in bans:
        match = pattern.search(scanned_text)
        if match is not None:
            line = text.count("\n", 0, match.start()) + 1
            errors.append(f"{relative}:{line}: static ban {ban_id}")
    positive_admission = re.compile(
        r"(?:physical|production|source[_ -]?identical)"
        r"[^\n]{0,80}(?:admission|admitted|authority|ready)"
        r"\s*(?:->|:=|=|:)\s*(?:true|pass|approved|admitted|ready)",
        re.IGNORECASE,
    )
    match = positive_admission.search(scanned_text)
    if match is not None:
        line = text.count("\n", 0, match.start()) + 1
        errors.append(f"{relative}:{line}: unapproved positive admission assignment")
    return errors


def _iter_formal_files(root: Path) -> Iterable[Path]:
    if not root.is_dir():
        return ()
    return (path for path in sorted(root.rglob("*")) if path.is_file() or path.is_symlink())


def _collect_tree_hashes(root: Path) -> dict[str, str]:
    hashes: dict[str, str] = {}
    for path in _iter_formal_files(root):
        relative = path.relative_to(root).as_posix()
        if path.is_symlink():
            hashes[relative] = f"SYMLINK:{os.readlink(path)}"
        elif path.is_file():
            hashes[relative] = _sha256(path)
    return hashes


def _as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _lakefile_mathlib_requirement(text: str) -> tuple[dict[str, Any] | None, str | None]:
    try:
        payload = tomllib.loads(text)
    except tomllib.TOMLDecodeError as exc:
        return None, f"invalid lakefile TOML: {exc}"
    requirements = payload.get("require", []) if isinstance(payload, dict) else []
    if isinstance(requirements, dict):
        requirements = [requirements]
    if not isinstance(requirements, list):
        return None, "lakefile [[require]] must decode as an array"
    matches = [
        item for item in requirements if isinstance(item, dict) and item.get("name") == "mathlib"
    ]
    if len(matches) != 1:
        return None, f"lakefile must contain exactly one mathlib requirement, found {len(matches)}"
    entry = matches[0]
    if entry.get("git") != MATHLIB_GIT_URL or entry.get("rev") != MATHLIB_TAG:
        return None, "lakefile mathlib git/tag does not match the locked identity"
    return dict(entry), None


def _manifest_mathlib_entry(payload: Any) -> tuple[dict[str, Any] | None, str | None]:
    if not isinstance(payload, dict):
        return None, "lake manifest root must be an object"
    packages = payload.get("packages")
    if not isinstance(packages, list):
        return None, "lake manifest packages must be an array"
    matches = [
        item for item in packages if isinstance(item, dict) and item.get("name") == "mathlib"
    ]
    if len(matches) != 1:
        return None, f"lake manifest must contain exactly one mathlib package, found {len(matches)}"
    entry = matches[0]
    if entry.get("inputRev") != MATHLIB_TAG:
        return None, "lake manifest mathlib inputRev mismatch"
    if entry.get("rev") != MATHLIB_COMMIT:
        return None, "lake manifest mathlib resolved commit mismatch"
    if entry.get("url") != MATHLIB_GIT_URL:
        return None, "lake manifest mathlib canonical git URL mismatch"
    return dict(entry), None


def _lean_audit_directives(text: str) -> list[str]:
    code = _strip_comments_and_strings(text, lean=True)
    return re.findall(r"(?m)^[ \t]*#print[ \t]+axioms[ \t]+([A-Za-z0-9_.']+)[ \t]*$", code)


def _rocq_audit_directives(text: str) -> list[str]:
    code = _strip_comments_and_strings(text, lean=False)
    return re.findall(
        r"(?m)^[ \t]*Print[ \t]+Assumptions[ \t]+([A-Za-z0-9_.']+)[ \t]*\.[ \t]*$",
        code,
    )


def _audit_policy(prompt: Any) -> dict[str, Any]:
    return _as_dict(_as_dict(prompt).get("execution")).get("assumption_audit", {})


def _audit_contract_errors(
    *, tool: str, source_text: str, prompt: Any
) -> list[str]:
    policy = _audit_policy(prompt)
    if not isinstance(policy, dict):
        return [f"{tool}: missing structured assumption_audit policy"]
    expected = policy.get("expected_theorems")
    expected_count = policy.get("expected_theorem_count")
    if not isinstance(expected, list) or not all(isinstance(item, str) for item in expected):
        return [f"{tool}: expected_theorems must be a string array"]
    directives = (
        _lean_audit_directives(source_text)
        if tool == "lean"
        else _rocq_audit_directives(source_text)
    )
    errors: list[str] = []
    if expected_count != 25 or len(expected) != 25:
        errors.append(f"{tool}: assumption audit count must be exactly 25")
    locked_expected = LEAN_EXPECTED_THEOREMS if tool == "lean" else ROCQ_EXPECTED_THEOREMS
    if tuple(expected) != locked_expected:
        errors.append(f"{tool}: assumption audit theorem set/order differs from runner lock")
    if len(set(expected)) != len(expected):
        errors.append(f"{tool}: expected theorem audit set contains duplicates")
    if directives != expected:
        errors.append(f"{tool}: aggregate audit directives do not exactly match expected theorem order")
    allowed = policy.get("allowed_foundation_axioms")
    if not isinstance(allowed, list) or not allowed:
        errors.append(f"{tool}: narrow allowed foundation list is missing")
    locked_allowed: Any = (
        list(LEAN_ALLOWED_AXIOMS)
        if tool == "lean"
        else [dict(rule) for rule in ROCQ_ALLOWED_FOUNDATIONS]
    )
    if allowed != locked_allowed:
        errors.append(f"{tool}: allowed foundation list differs from runner lock")
    return errors


def _runner_selftest_errors() -> list[str]:
    errors: list[str] = []
    lean_safe = 'def constantName := "axiom sorry admit"\n-- axiom hidden : Prop\n'
    lean_unsafe = {
        "constant": "constant bad : Prop\n",
        "axiom": "private axiom bad : Prop\n",
        "sorry": "theorem bad : True := by sorry\n",
        "admit": "theorem bad : True := by admit\n",
    }
    if _source_ban_errors("test.lean", lean_safe):
        errors.append("Lean lexical self-test rejected comments/strings/identifier substrings")
    for token, source in lean_unsafe.items():
        if not _source_ban_errors("test.lean", source):
            errors.append(f"Lean lexical self-test failed to reject {token}")
    for token, source in {
        "Parameter": "Parameter bad : Prop.\n",
        "Axiom": "Local Axiom bad : Prop.\n",
        "Conjecture": "Conjecture bad : Prop.\n",
        "Admitted": "Theorem bad : True. Admitted.\n",
        "admit": "Theorem bad : True. Proof. admit. Qed.\n",
    }.items():
        if not _source_ban_errors("test.v", source):
            errors.append(f"Rocq lexical self-test failed to reject {token}")

    valid_manifest = {
        "packages": [
            {
                "name": "mathlib",
                "inputRev": MATHLIB_TAG,
                "rev": MATHLIB_COMMIT,
                "url": MATHLIB_GIT_URL,
            }
        ]
    }
    if _manifest_mathlib_entry(valid_manifest)[1] is not None:
        errors.append("structured mathlib manifest self-test rejected exact identity")
    duplicate_manifest = {"packages": [*valid_manifest["packages"], *valid_manifest["packages"]]}
    if _manifest_mathlib_entry(duplicate_manifest)[1] is None:
        errors.append("structured mathlib manifest self-test accepted duplicate entry")
    wrong_manifest = json.loads(json.dumps(valid_manifest))
    wrong_manifest["packages"][0]["rev"] = "0" * 40
    if _manifest_mathlib_entry(wrong_manifest)[1] is None:
        errors.append("structured mathlib manifest self-test accepted wrong commit")

    poisoned = {variable: "ATTACK" for variable in CLEARED_SEARCH_OVERRIDES}
    poisoned.update({variable: "ATTACK" for variable in CLEARED_LEAN_CACHE_OVERRIDES})
    poisoned[NETWORK_PREFIX_ENV] = "[]"
    cleaned = _clear_search_overrides(poisoned)
    if any(variable in cleaned for variable in (*poisoned,)):
        errors.append("environment override self-test failed to clear inherited controls")

    lean_audit = _parse_lean_assumption_audit(
        "'Alpha' depends on axioms: [propext]\n'Beta' does not depend on any axioms\n",
        expected=("Alpha", "Beta"),
        allowed_axioms=("propext",),
    )
    lean_bad = _parse_lean_assumption_audit(
        "'Alpha' depends on axioms: [Local.bad]\n",
        expected=("Alpha",),
        allowed_axioms=("propext",),
    )
    if lean_audit["status"] != "PASS" or lean_bad["status"] != "FAIL":
        errors.append("Lean assumption-output parser mutation self-test failed")

    rocq_policy = (
        {"exact_name": "Classical_Prop.classic", "required_origin": "Stdlib.Logic.Classical_Prop"},
    )
    rocq_good_output = (
        "REC_NEXT03_AUDIT_BEGIN__Alpha\nAxioms:\n"
        "Classical_Prop.classic : forall P : Prop, P \\/ ~ P\n"
        "REC_NEXT03_AUDIT_END__Alpha\n"
    )
    rocq_bad_output = (
        "REC_NEXT03_AUDIT_BEGIN__Alpha\nAxioms:\nLocal.bad : Prop\n"
        "REC_NEXT03_AUDIT_END__Alpha\n"
    )
    rocq_audit = _parse_rocq_assumption_audit(
        rocq_good_output, expected=("Alpha",), allowed_foundations=rocq_policy
    )
    rocq_bad = _parse_rocq_assumption_audit(
        rocq_bad_output, expected=("Alpha",), allowed_foundations=rocq_policy
    )
    if rocq_audit["status"] != "PASS" or rocq_bad["status"] != "FAIL":
        errors.append("Rocq assumption-output parser mutation self-test failed")

    parent_namespace = "net:[100]"
    isolated_observation = {
        "interfaces": ["lo"],
        "net_namespace": "net:[101]",
        "non_loopback_routes": [],
        "sysfs_interfaces": ["docker0", "lo"],
    }
    if not _network_namespace_isolated(
        isolated_observation, parent_namespace=parent_namespace
    ):
        errors.append("network namespace self-test rejected isolated syscall observation")
    for mutated in (
        {**isolated_observation, "net_namespace": parent_namespace},
        {**isolated_observation, "interfaces": ["docker0", "lo"]},
        {**isolated_observation, "non_loopback_routes": ["eth0"]},
    ):
        if _network_namespace_isolated(mutated, parent_namespace=parent_namespace):
            errors.append("network namespace self-test accepted an unisolated observation")
            break
    if _wolfram_license_availability_state("License limit reached: all available licenses are in use") != "SLOT_BUSY":
        errors.append("Wolfram license self-test failed to classify slot contention")
    if _wolfram_license_availability_state("Wolfram Engine is not activated") != "LICENSE_OR_ACTIVATION_UNAVAILABLE":
        errors.append("Wolfram license self-test failed to classify an unavailable runtime")
    if _wolfram_license_availability_state("formal check failed: expected identity did not hold") is not None:
        errors.append("Wolfram license self-test misclassified a formal failure")
    return errors


def check_contract(root: Path = FORMAL_ROOT) -> dict[str, Any]:
    errors: list[str] = []
    admission_errors: list[str] = []
    checks: list[dict[str, Any]] = []
    parsed_json: dict[str, Any] = {}

    checks.append({"id": "formal_root_exists", "passed": root.is_dir()})
    if not root.is_dir():
        errors.append(f"missing formal root: {root.relative_to(REPOSITORY_ROOT)}")
        return _contract_report(checks=checks, errors=errors, files={})

    for relative in EXPECTED_FILES:
        path = root / relative
        passed = path.is_file() and not path.is_symlink()
        checks.append({"id": f"required_file:{relative}", "passed": passed})
        if not passed:
            errors.append(f"missing required regular file: {relative}")

    files: dict[str, str] = {}
    for path in _iter_formal_files(root):
        relative = path.relative_to(root).as_posix()
        if path.is_symlink():
            errors.append(f"symlink forbidden in formal tree: {relative}")
            continue
        if any(component in GENERATED_COMPONENTS for component in path.parts) or (
            path.suffix in GENERATED_SUFFIXES
        ):
            errors.append(f"generated artifact forbidden in formal tree: {relative}")
            continue
        files[relative] = _sha256(path)
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            errors.append(f"non-UTF-8 formal source forbidden: {relative}")
            continue
        source_errors = _source_ban_errors(relative, text)
        errors.extend(source_errors)
        admission_errors.extend(
            error for error in source_errors if "unapproved positive admission" in error
        )
        if relative.endswith(".json"):
            try:
                payload = _load_json_text(text, source=relative)
            except ContractError as exc:
                errors.append(str(exc))
                continue
            if not isinstance(payload, dict):
                errors.append(f"{relative}: JSON root must be an object")
                continue
            parsed_json[relative] = payload
            json_claim_errors: list[str] = []
            _audit_json_claims(payload, location=relative, errors=json_claim_errors)
            errors.extend(json_claim_errors)
            admission_errors.extend(json_claim_errors)

    for relative, schema in EXPECTED_JSON_SCHEMAS.items():
        payload = parsed_json.get(relative)
        passed = isinstance(payload, dict) and payload.get("schema") == schema
        checks.append({"id": f"json_schema:{relative}", "passed": passed})
        if payload is not None and not passed:
            errors.append(
                f"{relative}: schema must be {schema!r}, got {payload.get('schema')!r}"
            )

    obligations = parsed_json.get("OBLIGATIONS.json")
    obligations_ok = (
        isinstance(obligations, dict)
        and "NONAUTHORITATIVE" in str(obligations.get("authority", "")).upper()
        and isinstance(obligations.get("obligations"), list)
        and bool(obligations.get("obligations"))
    )
    checks.append({"id": "obligations_are_nonauthoritative_and_nonempty", "passed": obligations_ok})
    if obligations is not None and not obligations_ok:
        errors.append(
            "OBLIGATIONS.json: authority must be NONAUTHORITATIVE and obligations nonempty"
        )

    toolchains = parsed_json.get("TOOLCHAINS.lock.json")
    toolchains_ok = (
        isinstance(toolchains, dict)
        and toolchains.get("status") == "PARTIAL_LOCK_SPEC_NOT_EXECUTION_RECEIPT"
        and isinstance(toolchains.get("tools"), (dict, list))
    )
    checks.append({"id": "toolchain_lock_is_spec_not_receipt", "passed": toolchains_ok})
    if toolchains is not None and not toolchains_ok:
        errors.append(
            "TOOLCHAINS.lock.json: lock must remain PARTIAL_LOCK_SPEC_NOT_EXECUTION_RECEIPT"
        )
    locked_tools = _as_dict(toolchains.get("tools")) if isinstance(toolchains, dict) else {}
    lean_lock = _as_dict(locked_tools.get("lean"))
    mathlib_lock = _as_dict(lean_lock.get("mathlib"))
    manifest_lock = _as_dict(mathlib_lock.get("manifest_contract"))
    checkout_lock = _as_dict(mathlib_lock.get("checkout_contract"))
    rocq_lock = _as_dict(locked_tools.get("rocq"))
    wolfram_lock = _as_dict(locked_tools.get("wolfram"))
    xact_lock = _as_dict(wolfram_lock.get("xact"))
    sagemath_lock = _as_dict(locked_tools.get("sagemath"))
    singular_lock = _as_dict(locked_tools.get("singular"))
    toolchain_json_pins_ok = (
        lean_lock.get("version") == MATHLIB_TAG
        and mathlib_lock.get("tag") == MATHLIB_TAG
        and mathlib_lock.get("commit") == MATHLIB_COMMIT
        and mathlib_lock.get("canonical_git_url") == MATHLIB_GIT_URL
        and manifest_lock.get("unique_package_name") == "mathlib"
        and manifest_lock.get("inputRev") == MATHLIB_TAG
        and manifest_lock.get("rev") == MATHLIB_COMMIT
        and manifest_lock.get("matching_entries_required") == 1
        and checkout_lock.get("git_head") == MATHLIB_COMMIT
        and checkout_lock.get("git_status_porcelain") == "EMPTY"
        and checkout_lock.get("record_head_tree") is True
        and rocq_lock.get("version") == "9.2.0"
        and xact_lock.get("archive_sha256") == XACT_ARCHIVE_SHA256
        and sagemath_lock.get("version_lock")
        == "UNPINNED_RECORD_EXACT_VERSION_AT_RUNTIME"
        and singular_lock.get("version_lock")
        == "UNPINNED_RECORD_EXACT_VERSION_AT_RUNTIME"
    )
    checks.append({"id": "toolchain_json_exact_pins", "passed": toolchain_json_pins_ok})
    if toolchains is not None and not toolchain_json_pins_ok:
        errors.append("TOOLCHAINS.lock.json: exact backend pin policy mismatch")

    pin_requirements: Mapping[str, Sequence[str]] = {
        "lean/lean-toolchain": ("leanprover/lean4:v4.33.0",),
        "rocq/rocq-toolchain": ("rocq-prover", "9.2.0"),
    }
    for relative, markers in pin_requirements.items():
        path = root / relative
        text = path.read_text(encoding="utf-8") if path.is_file() else ""
        passed = all(marker in text for marker in markers)
        checks.append({"id": f"source_toolchain_pin:{relative}", "passed": passed})
        if path.is_file() and not passed:
            errors.append(f"{relative}: missing exact toolchain pin markers {list(markers)!r}")

    lakefile_path = root / "lean" / "lakefile.toml"
    lakefile_requirement, lakefile_error = (
        _lakefile_mathlib_requirement(lakefile_path.read_text(encoding="utf-8"))
        if lakefile_path.is_file()
        else (None, "missing lakefile")
    )
    lakefile_ok = lakefile_error is None and lakefile_requirement is not None
    checks.append({"id": "lakefile_structured_mathlib_pin", "passed": lakefile_ok})
    if lakefile_path.is_file() and not lakefile_ok:
        errors.append(f"lean/lakefile.toml: {lakefile_error}")

    tool_name_markers = {
        "lean": "lean",
        "rocq": "rocq",
        "sage": "sage",
        "wolfram": "wolfram",
    }
    for tool, tool_marker in tool_name_markers.items():
        relative = f"prompts/{tool}.json"
        payload = parsed_json.get(relative)
        mutation_policy = payload.get("mutation_policy") if isinstance(payload, dict) else None
        required_final_state = (
            payload.get("required_final_state") if isinstance(payload, dict) else None
        )
        prompt_ok = (
            isinstance(payload, dict)
            and tool_marker in str(payload.get("tool", "")).lower()
            and "NONAUTHORITATIVE" in str(payload.get("authority", "")).upper()
            and isinstance(payload.get("fail_closed"), list)
            and bool(payload.get("fail_closed"))
            and isinstance(mutation_policy, dict)
            and mutation_policy.get("repository_mutations") == []
            and isinstance(required_final_state, dict)
            and required_final_state.get("physical_face_admission") is False
        )
        checks.append({"id": f"local_prompt_fail_closed:{tool}", "passed": prompt_ok})
        if payload is not None and not prompt_ok:
            errors.append(
                f"{relative}: tool/authority/fail_closed contract is incomplete"
            )

    for tool, relative in (
        ("lean", "lean/RecNext03/All.lean"),
        ("rocq", "rocq/All.v"),
    ):
        source_path = root / relative
        prompt = parsed_json.get(f"prompts/{tool}.json")
        audit_errors = _audit_contract_errors(
            tool=tool,
            source_text=source_path.read_text(encoding="utf-8") if source_path.is_file() else "",
            prompt=prompt,
        )
        checks.append({"id": f"exact_25_theorem_audit:{tool}", "passed": not audit_errors})
        errors.extend(audit_errors)

    build_policy = _as_dict(_as_dict(toolchains).get("build_policy"))
    inherited_policy = _as_dict(build_policy.get("inherited_search_path_policy"))
    cleared_contract = inherited_policy.get("clear_before_every_tool_subprocess")
    overrides_ok = (
        isinstance(cleared_contract, list)
        and set(cleared_contract) == set(CLEARED_SEARCH_OVERRIDES)
        and len(cleared_contract) == len(CLEARED_SEARCH_OVERRIDES)
        and inherited_policy.get("runner_controlled_paths_only") is True
    )
    checks.append({"id": "inherited_search_override_contract", "passed": overrides_ok})
    if toolchains is not None and not overrides_ok:
        errors.append("TOOLCHAINS.lock.json: inherited search override policy mismatch")

    network_policy = _as_dict(build_policy.get("network_isolation"))
    network_preflight = _as_dict(network_policy.get("preflight"))
    network_prefix_ok = network_policy.get("command_prefix") == [
        "unshare",
        *NETWORK_PREFIX_ARGUMENTS,
    ] and (
        network_policy.get("unavailable_denied_or_unverified_result") == NETWORK_GAP_REASON
    ) and (
        network_preflight.get("child_namespace_must_differ_from_parent") is True
    ) and network_preflight.get("non_loopback_routes_must_be_empty") is True and (
        network_preflight.get("inherited_sysfs_interfaces_are_diagnostic_only") is True
    )
    checks.append({"id": "exact_fail_closed_network_prefix_contract", "passed": network_prefix_ok})
    if toolchains is not None and not network_prefix_ok:
        errors.append("TOOLCHAINS.lock.json: network namespace prefix/result contract mismatch")

    wolfram_license_policy = _as_dict(build_policy.get("wolfram_license_slot_wait"))
    wolfram_prompt_execution = _as_dict(
        _as_dict(parsed_json.get("prompts/wolfram.json")).get("execution")
    )
    wolfram_prompt_license_policy = _as_dict(
        wolfram_prompt_execution.get("license_slot_wait")
    )
    wolfram_license_wait_ok = (
        wolfram_license_policy.get(
            "external_license_contention_is_not_a_formal_counterexample"
        )
        is True
        and wolfram_license_policy.get("wait_seconds_default")
        == WOLFRAM_LICENSE_WAIT_DEFAULT_SECONDS
        and wolfram_license_policy.get("poll_seconds_default")
        == WOLFRAM_LICENSE_POLL_DEFAULT_SECONDS
        and wolfram_license_policy.get("retry_scope")
        == "ONLY_WOLFRAM_OUTPUTS_CLASSIFIED_AS_LICENSE_OR_ACTIVATION_AVAILABILITY"
        and wolfram_license_policy.get("activation_or_relicensing_attempted") is False
        and wolfram_license_policy.get("deadline_result") == "ENVIRONMENT_GAP"
        and wolfram_prompt_license_policy == {
            "external_license_contention_is_not_a_formal_counterexample": True,
            "wait_seconds_default": WOLFRAM_LICENSE_WAIT_DEFAULT_SECONDS,
            "poll_seconds_default": WOLFRAM_LICENSE_POLL_DEFAULT_SECONDS,
            "retry_scope": "ONLY_WOLFRAM_OUTPUTS_CLASSIFIED_AS_LICENSE_OR_ACTIVATION_AVAILABILITY",
            "activation_or_relicensing_attempted": False,
            "deadline_result": "ENVIRONMENT_GAP",
        }
    )
    checks.append({"id": "wolfram_license_slot_wait_contract", "passed": wolfram_license_wait_ok})
    if toolchains is not None and not wolfram_license_wait_ok:
        errors.append("Wolfram license-slot wait contract mismatch")

    provisioning_policy = _as_dict(build_policy.get("toolchain_provisioning"))
    provisioning_ok = (
        provisioning_policy.get("authorized_executor") == "LOCAL_CODEX"
        and provisioning_policy.get("entrypoint")
        == "scripts/provision_rec_next03_formal_toolchains.py"
        and provisioning_policy.get("phase")
        == "SETUP_AFTER_DELIVERY_IDENTITY_BEFORE_EVIDENCE"
        and provisioning_policy.get("network_enabled_setup_only") is True
        and provisioning_policy.get("repository_mutations") == []
        and provisioning_policy.get("external_root_required") is True
        and provisioning_policy.get("xact_archive_sha256_required") == XACT_ARCHIVE_SHA256
        and _as_dict(provisioning_policy.get("lean")).get("toolchain")
        == "leanprover/lean4:v4.33.0"
        and _as_dict(provisioning_policy.get("lean")).get("required_mathlib_commit")
        == MATHLIB_COMMIT
        and (
            REPOSITORY_ROOT / "scripts" / "provision_rec_next03_formal_toolchains.py"
        ).is_file()
    )
    checks.append({"id": "local_codex_provisioning_contract", "passed": provisioning_ok})
    if toolchains is not None and not provisioning_ok:
        errors.append("TOOLCHAINS.lock.json: local Codex provisioning contract mismatch")

    cache_policy = _as_dict(build_policy.get("lean_artifact_cache_policy"))
    cleared_cache_contract = cache_policy.get(
        "clear_inherited_before_every_tool_subprocess"
    )
    cache_contract_ok = (
        isinstance(cleared_cache_contract, list)
        and set(cleared_cache_contract) == set(CLEARED_LEAN_CACHE_OVERRIDES)
        and len(cleared_cache_contract) == len(CLEARED_LEAN_CACHE_OVERRIDES)
        and cache_policy.get("required_effective_values")
        == {
            "LAKE_ARTIFACT_CACHE": "false",
            "LAKE_NO_CACHE": "1",
            "LAKE_RESTORE_ARTIFACTS": "0",
        }
    )
    checks.append({"id": "lean_artifact_cache_contract", "passed": cache_contract_ok})
    if toolchains is not None and not cache_contract_ok:
        errors.append("TOOLCHAINS.lock.json: Lean artifact-cache contract mismatch")

    selftest_errors = _runner_selftest_errors()
    checks.append({"id": "runner_mutation_selftests", "passed": not selftest_errors})
    errors.extend(selftest_errors)

    wolfram_prompt = parsed_json.get("prompts/wolfram.json")
    wolfram_source_path = root / "wolfram" / "verify_frame_face_event.wls"
    wolfram_source = (
        wolfram_source_path.read_text(encoding="utf-8")
        if wolfram_source_path.is_file()
        else ""
    )
    wolfram_check_ids = re.findall(r'AddCheck\["([^"]+)"', wolfram_source)
    wolfram_expected_count = (
        wolfram_prompt.get("required_checks", {}).get("expected_check_count")
        if isinstance(wolfram_prompt, dict)
        else None
    )
    wolfram_ids_ok = (
        isinstance(wolfram_expected_count, int)
        and len(wolfram_check_ids) == wolfram_expected_count
        and len(set(wolfram_check_ids)) == len(wolfram_check_ids)
    )
    checks.append({"id": "wolfram_exact_literal_check_ids", "passed": wolfram_ids_ok})
    if wolfram_source_path.is_file() and not wolfram_ids_ok:
        errors.append(
            "wolfram verifier quoted AddCheck IDs must be unique and match prompt expected_check_count"
        )

    marker_requirements: Mapping[str, Sequence[str]] = {
        "CONTRACT.md": (
            "NONAUTHORITATIVE",
            SCIENTIFIC_TERMINAL,
            SCIENTIFIC_CLAIM,
        ),
        "wolfram/verify_frame_face_event.wls": (
            "NONAUTHORITATIVE",
            "CHARACTERISTIC_R_H_ZERO",
            "RED_FACE_V_X_ZERO",
            "BLUE_FACE_V_X_ZERO",
        ),
        "sage/verify_remap_event.sage": (
            "NONAUTHORITATIVE",
            "NOT_ESTABLISHED",
        ),
    }
    for relative, markers in marker_requirements.items():
        path = root / relative
        text = path.read_text(encoding="utf-8") if path.is_file() else ""
        for marker in markers:
            passed = marker.upper() in text.upper()
            checks.append({"id": f"required_marker:{relative}:{marker}", "passed": passed})
            if path.is_file() and not passed:
                errors.append(f"{relative}: missing required marker {marker!r}")

    checks.append({"id": "no_unapproved_admission", "passed": not admission_errors})
    return _contract_report(checks=checks, errors=errors, files=files)


def _contract_report(
    *,
    checks: list[dict[str, Any]],
    errors: list[str],
    files: dict[str, str],
) -> dict[str, Any]:
    unique_errors = sorted(set(errors))
    return {
        "admission_allowed": False,
        "authority": AUTHORITY,
        "blockers_resolved": [],
        "checks": checks,
        "errors": unique_errors,
        "formal_tree_sha256": files,
        "mode": "CHECK_CONTRACT",
        "physical_authority_status": PHYSICAL_AUTHORITY_STATUS,
        "schema": "rec-next03-formal-runner/v1",
        "scientific_claim": SCIENTIFIC_CLAIM,
        "scientific_terminal": SCIENTIFIC_TERMINAL,
        "source_authority_status": SOURCE_AUTHORITY_STATUS,
        "status": "PASS" if not unique_errors and all(c["passed"] for c in checks) else "FAIL",
    }


def _write_bytes(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as handle:
        handle.write(data)


def _write_json(path: Path, value: Any) -> None:
    _write_bytes(path, _canonical_json(value).encode("ascii"))


def _network_namespace_isolated(
    observation: Mapping[str, Any], *, parent_namespace: str | None
) -> bool:
    return (
        isinstance(parent_namespace, str)
        and isinstance(observation.get("net_namespace"), str)
        and observation.get("net_namespace") != parent_namespace
        and observation.get("interfaces") == ["lo"]
        and observation.get("non_loopback_routes") == []
    )


def _clear_search_overrides(env: Mapping[str, str]) -> dict[str, str]:
    cleaned = dict(env)
    for variable in (*CLEARED_SEARCH_OVERRIDES, *CLEARED_LEAN_CACHE_OVERRIDES):
        cleaned.pop(variable, None)
    cleaned.pop(NETWORK_PREFIX_ENV, None)
    return cleaned


def _isolated_environment(output_dir: Path) -> dict[str, str]:
    inherited = os.environ.copy()
    original_home = Path(inherited["HOME"]).expanduser() if inherited.get("HOME") else None
    env = _clear_search_overrides(inherited)
    home = output_dir / "runtime" / "home"
    cache = output_dir / "runtime" / "cache"
    temporary = output_dir / "runtime" / "tmp"
    sage_home = output_dir / "runtime" / "sage"
    for path in (home, cache, temporary, sage_home):
        path.mkdir(parents=True, exist_ok=True)
    env.update(
        {
            "ALL_PROXY": "http://127.0.0.1:9",
            "ELAN_DIST_SERVER": "http://127.0.0.1:9/elan-dist-network-disabled",
            "ELAN_UPDATE_ROOT": "http://127.0.0.1:9/elan-update-network-disabled",
            "GIT_TERMINAL_PROMPT": "0",
            "GIT_CONFIG_COUNT": "2",
            "GIT_CONFIG_KEY_0": "url.file:///__rec_next03_network_forbidden__/.insteadOf",
            "GIT_CONFIG_KEY_1": "url.file:///__rec_next03_network_forbidden__/.insteadOf",
            "GIT_CONFIG_VALUE_0": "https://",
            "GIT_CONFIG_VALUE_1": "http://",
            "GIT_OPTIONAL_LOCKS": "0",
            "HOME": str(home),
            "HTTPS_PROXY": "http://127.0.0.1:9",
            "HTTP_PROXY": "http://127.0.0.1:9",
            "NO_PROXY": "127.0.0.1,localhost",
            "LAKE_NO_CACHE": "1",
            "LAKE_ARTIFACT_CACHE": "false",
            "LAKE_RESTORE_ARTIFACTS": "0",
            "PYTHONDONTWRITEBYTECODE": "1",
            "SAGE_DOT_SAGE": str(sage_home),
            "TMPDIR": str(temporary),
            "XDG_CACHE_HOME": str(cache),
            "XDG_CONFIG_HOME": str(output_dir / "runtime" / "config"),
            "XDG_DATA_HOME": str(output_dir / "runtime" / "data"),
            "all_proxy": "http://127.0.0.1:9",
            "http_proxy": "http://127.0.0.1:9",
            "https_proxy": "http://127.0.0.1:9",
            "no_proxy": "127.0.0.1,localhost",
        }
    )
    # Elan shims commonly live on PATH while ELAN_HOME is implicit in HOME.
    # Preserve an already-installed toolchain lookup, but make every attempted
    # download fail locally.  No update/install command is ever invoked here.
    if "ELAN_HOME" not in env and original_home is not None:
        inferred_elan = original_home / ".elan"
        if inferred_elan.is_dir():
            env["ELAN_HOME"] = str(inferred_elan)
    return env


def _copy_xact_into_isolated_home(output_dir: Path) -> dict[str, Any]:
    """Copy an existing xAct install into the isolated Wolfram user base.

    ``HOME`` isolation prevents CAS caches from landing outside ``output_dir``
    but would also hide a user xAct install.  An explicit source wins; otherwise
    only conventional per-user application directories are inspected.  The
    source is read-only and every copy target remains under ``output_dir``.
    """

    candidates: list[Path] = []
    archive_raw = os.environ.get("REC_NEXT03_XACT_ARCHIVE")
    archive_sha256: str | None = None
    archive_verified = False
    if archive_raw:
        archive = Path(archive_raw).expanduser().resolve()
        if not archive.is_file():
            return {
                "copied": False,
                "reason": "REC_NEXT03_XACT_ARCHIVE is not a regular file",
                "toolchain_status": "TOOLCHAIN_MISMATCH",
            }
        archive_sha256 = _sha256(archive)
        if archive_sha256 != XACT_ARCHIVE_SHA256:
            return {
                "archive_sha256": archive_sha256,
                "copied": False,
                "reason": "xAct archive SHA-256 does not match TOOLCHAINS.lock.json",
                "toolchain_status": "TOOLCHAIN_MISMATCH",
            }
        extracted = output_dir / "runtime" / "xact_archive"
        extracted.mkdir(parents=True, exist_ok=True)
        try:
            with tarfile.open(archive, mode="r:*") as bundle:
                members = bundle.getmembers()
                for member in members:
                    member_path = Path(member.name)
                    if (
                        member_path.is_absolute()
                        or ".." in member_path.parts
                        or member.issym()
                        or member.islnk()
                    ):
                        raise ContractError(
                            f"unsafe path/link in xAct archive: {member.name!r}"
                        )
                bundle.extractall(extracted, members=members, filter="data")
        except (OSError, tarfile.TarError, ContractError) as exc:
            return {
                "archive_sha256": archive_sha256,
                "copied": False,
                "reason": f"xAct archive extraction failed: {exc}",
                "toolchain_status": "TOOLCHAIN_MISMATCH",
            }
        extracted_candidates = [
            path for path in extracted.rglob("xAct") if path.is_dir() and (path / "xTensor").is_dir()
        ]
        if len(extracted_candidates) != 1:
            return {
                "archive_sha256": archive_sha256,
                "copied": False,
                "reason": "verified xAct archive did not contain one unambiguous xAct/xTensor tree",
                "toolchain_status": "TOOLCHAIN_MISMATCH",
            }
        candidates.append(extracted_candidates[0])
        archive_verified = True
    explicit = os.environ.get("REC_NEXT03_XACT_SOURCE_DIR")
    if explicit:
        candidates.append(Path(explicit).expanduser())
    original_home_raw = os.environ.get("HOME")
    if original_home_raw:
        original_home = Path(original_home_raw).expanduser()
        candidates.extend(
            (
                original_home / ".WolframEngine" / "Applications" / "xAct",
                original_home / ".Mathematica" / "Applications" / "xAct",
                original_home / ".Wolfram" / "Applications" / "xAct",
                original_home / "Applications" / "xAct",
            )
        )
    source = next((candidate.resolve() for candidate in candidates if candidate.is_dir()), None)
    if source is None:
        return {
            "copied": False,
            "reason": (
                "no xAct directory found in REC_NEXT03_XACT_SOURCE_DIR or standard user paths"
            ),
            "toolchain_status": "ENVIRONMENT_GAP",
        }
    targets = (
        output_dir / "runtime" / "home" / ".WolframEngine" / "Applications" / "xAct",
        output_dir / "runtime" / "home" / ".Mathematica" / "Applications" / "xAct",
    )
    for target in targets:
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(source, target, symlinks=False)
    return {
        "archive_sha256": archive_sha256,
        "archive_verified": archive_verified,
        "copied": True,
        "source": str(source),
        "targets": [target.relative_to(output_dir).as_posix() for target in targets],
        "toolchain_status": "PASS" if archive_verified else "TOOLCHAIN_MISMATCH",
    }


def _run_command(
    *,
    label: str,
    command: Sequence[str],
    cwd: Path,
    env: Mapping[str, str],
    isolation: Mapping[str, Any],
    logs_dir: Path,
    timeout_seconds: int,
) -> dict[str, Any]:
    """Run one tool beneath the already-verified network namespace boundary.

    The isolation token is passed directly by ``run_all``; no environment
    variable or caller-controlled default can disable the prefix.  A small
    Python trampoline re-checks the namespace inode, live socket interface
    index, and routes *inside every new namespace* before replacing itself
    with the requested executable.  It does not use an inherited sysfs mount
    as the authority for the current network namespace.
    """

    stdout_path = logs_dir / f"{label}.stdout.log"
    stderr_path = logs_dir / f"{label}.stderr.log"
    logs_dir.mkdir(parents=True, exist_ok=True)
    prefix = isolation.get("prefix")
    if isolation.get("verified") is not True or not isinstance(prefix, tuple):
        raise ContractError("tool subprocess refused without verified network isolation")
    parent_namespace = isolation.get("parent_net_namespace")
    if not isinstance(parent_namespace, str):
        raise ContractError("tool subprocess refused without parent network namespace identity")
    expected_prefix = (str(isolation.get("executable")), *NETWORK_PREFIX_ARGUMENTS)
    if prefix != expected_prefix or not Path(prefix[0]).is_absolute():
        raise ContractError("tool subprocess refused for noncanonical network prefix")
    if not command:
        raise ContractError("empty tool command")
    resolved_tool = (
        Path(command[0]).resolve()
        if Path(command[0]).is_absolute()
        else Path(shutil.which(command[0]) or "").resolve()
    )
    if not resolved_tool.is_file():
        raise ContractError(f"tool executable is not a regular file: {command[0]!r}")
    logical_command = [str(resolved_tool), *command[1:]]
    marker_name = re.sub(r"[^A-Za-z0-9_.-]+", "_", label) + ".namespace-entry.json"
    marker_path = logs_dir / marker_name
    if marker_path.exists() or marker_path.is_symlink():
        raise ContractError(f"namespace-entry marker already exists: {marker_path}")
    trampoline = (
        "import json,os,socket,sys;"
        "parent=sys.argv[1];"
        "interfaces=sorted(name for _,name in socket.if_nameindex());"
        "routes=[fields[0] for line in open('/proc/net/route',encoding='ascii').read().splitlines()[1:] "
        "if len(fields:=line.split())>=1 and fields[0]!='lo'];"
        "payload={'interfaces':interfaces,'net_namespace':os.readlink('/proc/self/ns/net'),'non_loopback_routes':routes};"
        "(payload['net_namespace']!=parent and interfaces==['lo'] and routes==[]) or sys.exit(78);"
        "fd=os.open(sys.argv[2],os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600);"
        "os.write(fd,(json.dumps(payload,separators=(',',':'))+'\\n').encode());"
        "os.close(fd);"
        "os.execv(sys.argv[3],sys.argv[3:])"
    )
    actual_command = [
        *prefix,
        sys.executable,
        "-I",
        "-S",
        "-c",
        trampoline,
        parent_namespace,
        str(marker_path),
        *logical_command,
    ]
    process_env = _clear_search_overrides(env)
    process_env.update(
        {
            "LAKE_NO_CACHE": "1",
            "LAKE_ARTIFACT_CACHE": "false",
            "LAKE_RESTORE_ARTIFACTS": "0",
        }
    )
    try:
        process = subprocess.Popen(
            actual_command,
            cwd=cwd,
            env=process_env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            start_new_session=True,
        )
        try:
            stdout, stderr = process.communicate(timeout=timeout_seconds)
            timed_out = False
        except subprocess.TimeoutExpired as exc:
            stdout = exc.stdout or b""
            stderr = exc.stderr or b""
            timed_out = True
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            final_stdout, final_stderr = process.communicate()
            if final_stdout:
                stdout = final_stdout
            if final_stderr:
                stderr = final_stderr
        result = {
            "command": actual_command,
            "exit_code": None if timed_out else process.returncode,
            "logical_command": logical_command,
            "namespace_entry_marker": marker_path.relative_to(logs_dir.parent).as_posix(),
            "network_namespace_applied": True,
            "stderr_log": stderr_path.relative_to(logs_dir.parent).as_posix(),
            "stdout_log": stdout_path.relative_to(logs_dir.parent).as_posix(),
            "timed_out": timed_out,
        }
    except OSError as exc:
        stdout = b""
        stderr = str(exc).encode("utf-8", errors="replace")
        result = {
            "command": actual_command,
            "exit_code": 127,
            "logical_command": logical_command,
            "namespace_entry_marker": marker_path.relative_to(logs_dir.parent).as_posix(),
            "network_namespace_applied": True,
            "stderr_log": stderr_path.relative_to(logs_dir.parent).as_posix(),
            "stdout_log": stdout_path.relative_to(logs_dir.parent).as_posix(),
            "timed_out": False,
        }
    _write_bytes(stdout_path, stdout)
    _write_bytes(stderr_path, stderr)
    marker_valid = False
    if marker_path.is_file() and not marker_path.is_symlink():
        try:
            marker_payload = _load_json_text(
                marker_path.read_text(encoding="utf-8"), source=str(marker_path)
            )
            marker_valid = isinstance(marker_payload, dict) and _network_namespace_isolated(
                marker_payload, parent_namespace=parent_namespace
            )
        except (OSError, ContractError):
            marker_valid = False
    result["network_namespace_entry_verified"] = marker_valid
    if not marker_valid:
        result["raw_exit_code"] = result["exit_code"]
        if result["exit_code"] == 0:
            result["exit_code"] = 78
        result["execution_boundary_status"] = NETWORK_GAP_REASON
    return result


def _probe_network_isolation(
    *, output_dir: Path, env: Mapping[str, str], timeout_seconds: int
) -> tuple[dict[str, Any], dict[str, Any] | None]:
    network_dir = output_dir / "network"
    stdout_path = network_dir / "network-isolation.stdout.log"
    stderr_path = network_dir / "network-isolation.stderr.log"
    unshare_found = shutil.which("unshare")
    unshare = str(Path(unshare_found).resolve()) if unshare_found is not None else None
    display_executable = unshare or "unshare"
    prefix = [display_executable, *NETWORK_PREFIX_ARGUMENTS]
    try:
        parent_net_namespace = os.readlink("/proc/self/ns/net")
    except OSError:
        parent_net_namespace = None
    probe_script = (
        "import json,os,socket; "
        "interfaces=sorted(name for _,name in socket.if_nameindex()); "
        "routes=[fields[0] for line in open('/proc/net/route',encoding='ascii').read().splitlines()[1:] "
        "if len(fields:=line.split())>=1 and fields[0]!='lo']; "
        "payload={'interfaces':interfaces,'net_namespace':os.readlink('/proc/self/ns/net'),'non_loopback_routes':routes,"
        "'sysfs_interfaces':sorted(os.listdir('/sys/class/net'))}; "
        "print(json.dumps(payload,separators=(',',':')))"
    )
    command = [*prefix, sys.executable, "-I", "-S", "-c", probe_script]
    stdout = b""
    stderr = b""
    exit_code: int | None = 127
    timed_out = False
    if unshare is not None:
        try:
            process = subprocess.Popen(
                command,
                cwd=output_dir,
                env=_clear_search_overrides(env),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                start_new_session=True,
            )
            try:
                stdout, stderr = process.communicate(timeout=min(timeout_seconds, 60))
                exit_code = process.returncode
            except subprocess.TimeoutExpired as exc:
                stdout = exc.stdout or b""
                stderr = exc.stderr or b""
                exit_code = None
                timed_out = True
                try:
                    os.killpg(process.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
                final_stdout, final_stderr = process.communicate()
                if final_stdout:
                    stdout = final_stdout
                if final_stderr:
                    stderr = final_stderr
        except OSError as exc:
            stderr = str(exc).encode("utf-8", errors="replace")
    _write_bytes(stdout_path, stdout)
    _write_bytes(stderr_path, stderr)
    observation: dict[str, Any] = {}
    if exit_code == 0:
        try:
            decoded = json.loads(stdout.decode("utf-8"))
            if isinstance(decoded, dict):
                observation = decoded
        except (UnicodeDecodeError, json.JSONDecodeError):
            observation = {}
    verified = (
        exit_code == 0
        and not timed_out
        and _network_namespace_isolated(
            observation, parent_namespace=parent_net_namespace
        )
    )
    reason = (
        "isolated namespace has a distinct inode, loopback-only socket interfaces, and no non-loopback route"
        if verified
        else NETWORK_GAP_REASON
    )
    receipt = {
        "executable": unshare,
        "interfaces": observation.get("interfaces", []),
        "mechanism": "LINUX_USER_NETWORK_NAMESPACE",
        "parent_net_namespace": parent_net_namespace,
        "probe": {
            "command": command,
            "exit_code": exit_code,
            "stderr_log": stderr_path.relative_to(output_dir).as_posix(),
            "stdout_log": stdout_path.relative_to(output_dir).as_posix(),
            "timed_out": timed_out,
        },
        "net_namespace": observation.get("net_namespace"),
        "non_loopback_routes": observation.get("non_loopback_routes", []),
        "reason": reason,
        "sysfs_interfaces_diagnostic": observation.get("sysfs_interfaces", []),
        "verified": verified,
    }
    isolation = (
        {
            "executable": unshare,
            "parent_net_namespace": parent_net_namespace,
            "prefix": (unshare, *NETWORK_PREFIX_ARGUMENTS),
            "verified": True,
        }
        if verified and unshare is not None
        else None
    )
    return receipt, isolation


def _base_backend_result(name: str, *, status: str, reason: str) -> dict[str, Any]:
    return {
        "admission_allowed": False,
        "authority": AUTHORITY,
        "backend": name,
        "blockers_resolved": [],
        "physical_authority_status": PHYSICAL_AUTHORITY_STATUS,
        "reason": reason,
        "source_authority_status": SOURCE_AUTHORITY_STATUS,
        "status": status,
    }


def _combined_output(step: Mapping[str, Any], logs_dir: Path) -> str:
    chunks: list[str] = []
    for key in ("stdout_log", "stderr_log"):
        relative = step.get(key)
        if not isinstance(relative, str):
            continue
        path = logs_dir.parent / relative
        try:
            chunks.append(path.read_text(encoding="utf-8", errors="replace"))
        except OSError:
            pass
    return "\n".join(chunks)


def _wolfram_license_availability_state(output: str) -> str | None:
    """Classify an external Wolfram license boundary without inferring a proof result.

    A local license slot held by another job is neither a false theorem nor an
    executable formal counterexample. The caller may wait only for this
    externally observable class; activation/relicensing is never attempted.
    """

    normalized = output.lower()
    if any(pattern in normalized for pattern in WOLFRAM_LICENSE_SLOT_BUSY_PATTERNS):
        return "SLOT_BUSY"
    if any(marker in normalized for marker in WOLFRAM_LICENSE_AVAILABILITY_MARKERS):
        return "LICENSE_OR_ACTIVATION_UNAVAILABLE"
    return None


def _wolfram_license_availability_state_for_step(
    step: Mapping[str, Any], logs_dir: Path
) -> str | None:
    if step.get("exit_code") == 0:
        return None
    return _wolfram_license_availability_state(_combined_output(step, logs_dir))


def _classify_nonzero(step: Mapping[str, Any], logs_dir: Path) -> str:
    if step.get("network_namespace_entry_verified") is not True:
        return "ENVIRONMENT_GAP"
    if step.get("timed_out"):
        return "ENVIRONMENT_GAP"
    if step.get("exit_code") in ENVIRONMENT_GAP_EXIT_CODES:
        return "ENVIRONMENT_GAP"
    combined = _combined_output(step, logs_dir).lower()
    if any(pattern in combined for pattern in ENVIRONMENT_GAP_PATTERNS):
        return "ENVIRONMENT_GAP"
    return "FAIL"


def _step_has_environment_gap(step: Mapping[str, Any], logs_dir: Path) -> bool:
    return step.get("exit_code") != 0 and _classify_nonzero(step, logs_dir) == "ENVIRONMENT_GAP"


def _probe_contains(probe: Mapping[str, Any], logs_dir: Path, expected: str) -> bool:
    return probe.get("exit_code") == 0 and expected in _combined_output(probe, logs_dir)


def _probe(
    *,
    backend: str,
    executable: str,
    arguments: Sequence[str],
    cwd: Path,
    env: Mapping[str, str],
    isolation: Mapping[str, Any],
    logs_dir: Path,
    timeout_seconds: int,
) -> dict[str, Any]:
    return _run_command(
        label=f"{backend}.version",
        command=(executable, *arguments),
        cwd=cwd,
        env=env,
        isolation=isolation,
        logs_dir=logs_dir,
        timeout_seconds=min(timeout_seconds, 60),
    )


def _parse_report(path: Path, *, source: str) -> tuple[dict[str, Any] | None, str | None]:
    try:
        payload = _load_json_text(path.read_text(encoding="utf-8"), source=source)
    except (OSError, ContractError) as exc:
        return None, str(exc)
    if not isinstance(payload, dict):
        return None, f"{source}: report root must be an object"
    claim_errors: list[str] = []
    _audit_json_claims(payload, location=source, errors=claim_errors)
    if claim_errors:
        return None, "; ".join(claim_errors)
    return payload, None


def _prompt_payload(snapshot: Path, tool: str) -> dict[str, Any]:
    path = snapshot / "prompts" / f"{tool}.json"
    payload = _load_json_text(path.read_text(encoding="utf-8"), source=path.as_posix())
    if not isinstance(payload, dict):
        raise ContractError(f"{path}: prompt root must be an object")
    return payload


def _strip_ansi(text: str) -> str:
    return re.sub(r"\x1b\[[0-?]*[ -/]*[@-~]", "", text)


def _parse_lean_assumption_audit(
    output: str, *, expected: Sequence[str], allowed_axioms: Sequence[str]
) -> dict[str, Any]:
    clean = _strip_ansi(output)
    pattern = re.compile(
        r"['`]([^'`]+)['`]\s+(?:"
        r"does not depend on any axioms|depends on axioms:\s*\[([^\]]*)\])",
        re.DOTALL,
    )
    records: list[dict[str, Any]] = []
    for match in pattern.finditer(clean):
        raw_axioms = match.group(2)
        axioms = (
            []
            if raw_axioms is None or not raw_axioms.strip()
            else [item.strip() for item in raw_axioms.split(",") if item.strip()]
        )
        records.append({"theorem": match.group(1), "axioms": axioms})
    errors: list[str] = []
    names = [record["theorem"] for record in records]
    if names != list(expected):
        errors.append("Lean printed-axiom theorem sequence is missing, duplicated, extra, or reordered")
    allowed = set(allowed_axioms)
    for record in records:
        outside = sorted(set(record["axioms"]) - allowed)
        if outside:
            errors.append(
                f"Lean theorem {record['theorem']} reported forbidden axioms {outside!r}"
            )
    return {
        "allowed_foundation_axioms": list(allowed_axioms),
        "errors": errors,
        "expected_theorem_count": len(expected),
        "records": records,
        "status": "PASS" if not errors else "FAIL",
    }


def _rocq_assumption_origin(
    name: str, allowed_foundations: Sequence[Mapping[str, Any]]
) -> str | None:
    matches: list[str] = []
    for rule in allowed_foundations:
        exact = rule.get("exact_name")
        prefix = rule.get("name_prefix")
        if (isinstance(exact, str) and name == exact) or (
            isinstance(prefix, str) and name.startswith(prefix)
        ):
            origin = rule.get("required_origin")
            if isinstance(origin, str):
                matches.append(origin)
    return matches[0] if len(matches) == 1 else None


def _parse_rocq_assumption_block(block: str) -> tuple[list[str], list[str]]:
    if "Closed under the global context" in block and "Axioms:" not in block:
        return [], []
    if "Axioms:" not in block:
        return [], ["Rocq assumption block had neither Closed nor Axioms marker"]
    assumptions: list[str] = []
    unknown_lines: list[str] = []
    after_axioms = block.split("Axioms:", 1)[1]
    for line in after_axioms.splitlines():
        if not line or line[0].isspace():
            continue
        stripped = line.strip()
        match = re.match(r"^([A-Za-z_][A-Za-z0-9_.']*)(?:\s*:)?$", stripped)
        if match is None:
            match = re.match(r"^([A-Za-z_][A-Za-z0-9_.']*)\s*:", stripped)
        if match is None:
            unknown_lines.append(stripped)
        else:
            assumptions.append(match.group(1))
    return assumptions, [f"unparsed Rocq assumption line: {line}" for line in unknown_lines]


def _parse_rocq_assumption_audit(
    output: str,
    *,
    expected: Sequence[str],
    allowed_foundations: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    clean = _strip_ansi(output)
    records: list[dict[str, Any]] = []
    errors: list[str] = []
    cursor = 0
    for theorem in expected:
        begin = f"REC_NEXT03_AUDIT_BEGIN__{theorem}"
        end = f"REC_NEXT03_AUDIT_END__{theorem}"
        begin_at = clean.find(begin, cursor)
        if begin_at < 0 or clean.count(begin) != 1:
            errors.append(f"Rocq begin marker missing/duplicated for {theorem}")
            continue
        end_at = clean.find(end, begin_at + len(begin))
        if end_at < 0 or clean.count(end) != 1:
            errors.append(f"Rocq end marker missing/duplicated for {theorem}")
            continue
        if begin_at < cursor:
            errors.append(f"Rocq audit marker order invalid at {theorem}")
        block = clean[begin_at + len(begin) : end_at]
        assumptions, block_errors = _parse_rocq_assumption_block(block)
        errors.extend(f"{theorem}: {error}" for error in block_errors)
        resolved: list[dict[str, str]] = []
        for assumption in assumptions:
            origin = _rocq_assumption_origin(assumption, allowed_foundations)
            if origin is None:
                errors.append(f"Rocq theorem {theorem} reported forbidden assumption {assumption}")
            else:
                resolved.append({"name": assumption, "origin": origin})
        records.append({"theorem": theorem, "assumptions": resolved})
        cursor = end_at + len(end)
    if len(records) != len(expected):
        errors.append("Rocq assumption audit did not yield exactly the expected theorem count")
    return {
        "allowed_foundation_axioms": [dict(rule) for rule in allowed_foundations],
        "errors": errors,
        "expected_theorem_count": len(expected),
        "records": records,
        "status": "PASS" if not errors else "FAIL",
    }


def _command_stdout(step: Mapping[str, Any], logs_dir: Path) -> str:
    relative = step.get("stdout_log")
    if not isinstance(relative, str):
        return ""
    path = logs_dir.parent / relative
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def _git_checkout_identity(
    *,
    label: str,
    repository: Path,
    expected_head: str,
    env: Mapping[str, str],
    isolation: Mapping[str, Any],
    logs_dir: Path,
    timeout_seconds: int,
) -> dict[str, Any]:
    git = shutil.which("git")
    if git is None:
        return {"errors": ["git executable not found"], "status": "ENVIRONMENT_GAP"}
    git_dir = repository / ".git"
    if not git_dir.is_dir() or git_dir.is_symlink():
        return {
            "errors": ["mathlib checkout must have a self-contained regular .git directory"],
            "git_executable": git,
            "status": "TOOLCHAIN_MISMATCH",
        }
    forbidden_indirections = (
        git_dir / "commondir",
        git_dir / "objects" / "info" / "alternates",
    )
    if any(path.exists() or path.is_symlink() for path in forbidden_indirections):
        return {
            "errors": ["mathlib checkout uses forbidden external Git object/worktree indirection"],
            "git_executable": git,
            "status": "TOOLCHAIN_MISMATCH",
        }
    commands = {
        "head": (git, "rev-parse", "HEAD"),
        "head_tree": (git, "rev-parse", "HEAD^{tree}"),
        "remote_origin": (git, "config", "--get", "remote.origin.url"),
        "status": (git, "status", "--porcelain=v1", "--untracked-files=all"),
    }
    steps: dict[str, Any] = {}
    for command_id, command in commands.items():
        steps[command_id] = _run_command(
            label=f"{label}.{command_id}",
            command=command,
            cwd=repository,
            env=env,
            isolation=isolation,
            logs_dir=logs_dir,
            timeout_seconds=min(timeout_seconds, 120),
        )
    outputs = {key: _command_stdout(step, logs_dir).strip() for key, step in steps.items()}
    errors: list[str] = []
    for key, step in steps.items():
        if step.get("exit_code") != 0:
            errors.append(f"git {key} command failed")
    if outputs["head"] != expected_head:
        errors.append("Git HEAD does not match locked mathlib commit")
    if not re.fullmatch(r"[0-9a-f]{40}", outputs["head_tree"]):
        errors.append("Git HEAD tree was not captured as a 40-hex object")
    if outputs["status"]:
        errors.append("mathlib package Git checkout is not clean")
    if not outputs["remote_origin"]:
        errors.append("mathlib package remote.origin.url was not captured")
    environment_gap = any(_step_has_environment_gap(step, logs_dir) for step in steps.values())
    return {
        "errors": errors,
        "git_executable": git,
        "head": outputs["head"],
        "head_tree": outputs["head_tree"],
        "remote_origin_url": outputs["remote_origin"],
        "status": "PASS" if not errors else ("ENVIRONMENT_GAP" if environment_gap else "TOOLCHAIN_MISMATCH"),
        "status_porcelain": outputs["status"],
        "steps": steps,
    }


def _lean_source_identity(root: Path) -> dict[str, str] | None:
    relative_paths = (
        "RecNext03.lean",
        "RecNext03/All.lean",
        "RecNext03/Contracts.lean",
        "lakefile.toml",
        "lean-toolchain",
    )
    if any(not (root / relative).is_file() for relative in relative_paths):
        return None
    return {relative: _sha256(root / relative) for relative in relative_paths}


def _manifest_package_build_dirs(workspace: Path, payload: Any) -> tuple[list[Path], list[str]]:
    errors: list[str] = []
    directories = [workspace / ".lake" / "build"]
    packages = payload.get("packages") if isinstance(payload, dict) else None
    if not isinstance(packages, list):
        return directories, ["lake manifest packages must be an array"]
    seen: set[str] = set()
    for package in packages:
        if not isinstance(package, dict):
            errors.append("lake manifest package entry must be an object")
            continue
        name = package.get("name")
        if not isinstance(name, str) or not re.fullmatch(r"[A-Za-z0-9_.-]+", name):
            errors.append(f"unsafe/missing lake package name: {name!r}")
            continue
        if name in seen:
            errors.append(f"duplicate lake package name: {name}")
            continue
        seen.add(name)
        subdir = package.get("subDir")
        subpath = Path(subdir) if isinstance(subdir, str) and subdir else Path()
        if subpath.is_absolute() or ".." in subpath.parts:
            errors.append(f"unsafe lake package subDir for {name}: {subdir!r}")
            continue
        directories.append(workspace / ".lake" / "packages" / name / subpath / ".lake" / "build")
    return directories, errors


def _has_symlink_component(path: Path, *, stop: Path) -> bool:
    stop = stop.resolve()
    try:
        relative = path.relative_to(stop)
    except ValueError:
        return True
    cursor = stop
    for component in relative.parts:
        cursor = cursor / component
        if cursor.is_symlink():
            return True
    return False


def _workspace_symlink_errors(workspace: Path) -> list[str]:
    root = workspace.resolve()
    errors: list[str] = []
    for path in sorted(workspace.rglob("*")):
        if not path.is_symlink():
            continue
        try:
            target = path.resolve(strict=True)
        except (OSError, RuntimeError) as exc:
            errors.append(f"broken/unresolvable workspace symlink {path}: {exc}")
            continue
        if not _is_within(target, root):
            errors.append(f"workspace symlink escapes source root: {path}")
    return errors


def _purge_lean_build_artifacts(workspace: Path, manifest_payload: Any) -> dict[str, Any]:
    build_dirs, errors = _manifest_package_build_dirs(workspace, manifest_payload)
    removed: list[str] = []
    for build_dir in build_dirs:
        if _has_symlink_component(build_dir, stop=workspace):
            errors.append(f"refusing symlink component in build directory: {build_dir}")
            continue
        resolved = build_dir.resolve()
        if not _is_within(resolved, workspace.resolve()):
            errors.append(f"refusing non-descendant build directory: {build_dir}")
            continue
        if build_dir.exists():
            if not build_dir.is_dir():
                errors.append(f"build path is not a directory: {build_dir}")
                continue
            shutil.rmtree(build_dir)
            removed.append(build_dir.relative_to(workspace).as_posix())
    remaining = sorted(
        path.relative_to(workspace).as_posix()
        for path in workspace.rglob("*")
        if path.is_file()
        and path.suffix.lower() in {".ilean", ".olean", ".trace", ".volean"}
    )
    if remaining:
        errors.append("Lean build artifacts remain outside validated build directories")
    return {
        "errors": errors,
        "remaining_artifacts": remaining,
        "removed_build_directories": removed,
        "status": "PASS" if not errors else "FAIL",
    }


def _lean_artifact_inventory(workspace: Path) -> dict[str, Any]:
    artifacts = {
        path.relative_to(workspace).as_posix(): _sha256(path)
        for path in sorted(workspace.rglob("*"))
        if path.is_file()
        and path.suffix.lower() in {".ilean", ".olean", ".trace", ".volean"}
    }
    return {"count": len(artifacts), "sha256_by_path": artifacts}


def _lean_cache_reuse_findings(steps: Sequence[Mapping[str, Any]], logs_dir: Path) -> list[str]:
    patterns = (
        re.compile(r"\b(?:cache hit|artifact cache hit)\b", re.IGNORECASE),
        re.compile(r"\b(?:restore|restored|restoring|reuse|reused|reusing)\b[^\n]*\.(?:o|i|vo)lean\b", re.IGNORECASE),
        re.compile(r"\b(?:download|downloaded|downloading|unpack|unpacked|unpacking)\b[^\n]*(?:artifact|\.olean|\.ilean|\.volean)", re.IGNORECASE),
    )
    findings: list[str] = []
    for step in steps:
        label = " ".join(str(item) for item in step.get("logical_command", []))
        for line in _combined_output(step, logs_dir).splitlines():
            if any(pattern.search(line) for pattern in patterns):
                findings.append(f"{label}: {line.strip()}")
    return findings


def _rocq_audit_source(expected: Sequence[str]) -> bytes:
    lines = ["Require Import RecNext03Contracts.", ""]
    for theorem in expected:
        if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_']*", theorem):
            raise ContractError(f"unsafe Rocq theorem name in audit policy: {theorem!r}")
        lines.extend(
            (
                "Goal True.",
                f'  idtac "REC_NEXT03_AUDIT_BEGIN__{theorem}".',
                "  exact I.",
                "Qed.",
                f"Print Assumptions {theorem}.",
                "Goal True.",
                f'  idtac "REC_NEXT03_AUDIT_END__{theorem}".',
                "  exact I.",
                "Qed.",
                "",
            )
        )
    return ("\n".join(lines) + "\n").encode("utf-8")


def _rocq_stdlib_identity(root: Path, required_origins: Sequence[str]) -> dict[str, Any]:
    if not root.is_absolute() or not root.is_dir():
        return {"errors": ["Rocq -where result is not an absolute directory"], "status": "FAIL"}
    module_files: dict[str, dict[str, str]] = {}
    errors: list[str] = []
    for origin in sorted(set(required_origins)):
        filename = origin.rsplit(".", 1)[-1] + ".vo"
        logical_parts = origin.split(".")[1:-1]
        matches = [
            path
            for path in root.rglob(filename)
            if path.is_file() and all(part in path.parts for part in logical_parts)
        ]
        if len(matches) != 1:
            errors.append(f"Rocq Stdlib origin {origin} resolved to {len(matches)} files")
            continue
        path = matches[0].resolve()
        if not _is_within(path, root.resolve()):
            errors.append(f"Rocq Stdlib origin escaped canonical root: {origin}")
            continue
        module_files[origin] = {
            "path": path.relative_to(root.resolve()).as_posix(),
            "sha256": _sha256(path),
        }
    return {
        "canonical_root": str(root.resolve()),
        "errors": errors,
        "module_files": module_files,
        "status": "PASS" if not errors else "FAIL",
    }


def _run_wolfram(
    *, snapshot: Path, output_dir: Path, env: Mapping[str, str],
    isolation: Mapping[str, Any], timeout_seconds: int,
    license_wait_seconds: int, license_poll_seconds: int,
) -> dict[str, Any]:
    name = "wolfram_xact"
    backend_dir = output_dir / "backends" / name
    logs_dir = backend_dir / "logs"
    backend_dir.mkdir(parents=True, exist_ok=True)
    executable = shutil.which("wolframscript")
    if executable is None:
        return _base_backend_result(name, status="ENVIRONMENT_GAP", reason="wolframscript not found")
    xact_materialization = _copy_xact_into_isolated_home(output_dir)
    wait_started = time.monotonic()
    deadline = wait_started + license_wait_seconds
    attempts: list[dict[str, Any]] = []
    execution: dict[str, Any] | None = None
    report_path: Path | None = None
    version: dict[str, Any] | None = None
    wait_deadline_exhausted = False

    while True:
        # A prior retryable execution is preserved in ``attempts``. Do not
        # attach it to a later, different version-probe outcome.
        execution = None
        report_path = None
        attempt_number = len(attempts) + 1
        version = _run_command(
            label=f"{name}.version.attempt_{attempt_number:03d}",
            command=(executable, "-code", "$Version"),
            cwd=backend_dir,
            env=env,
            isolation=isolation,
            logs_dir=logs_dir,
            timeout_seconds=min(timeout_seconds, 60),
        )
        version_license_state = _wolfram_license_availability_state_for_step(version, logs_dir)
        if version_license_state is not None:
            attempts.append(
                {
                    "attempt": attempt_number,
                    "exit_code": version.get("exit_code"),
                    "license_availability_state": version_license_state,
                    "phase": "version_probe",
                    "stderr_log": version.get("stderr_log"),
                    "stdout_log": version.get("stdout_log"),
                }
            )
        elif _step_has_environment_gap(version, logs_dir):
            result = _base_backend_result(
                name,
                status="ENVIRONMENT_GAP",
                reason="Wolfram version probe lost the verified namespace boundary",
            )
            break
        elif version.get("exit_code") != 0 or not _combined_output(version, logs_dir).strip():
            result = _base_backend_result(
                name,
                status="TOOLCHAIN_MISMATCH",
                reason="Wolfram runtime version could not be captured exactly",
            )
            break
        else:
            report_path = backend_dir / f"report.attempt_{attempt_number:03d}.json"
            execution = _run_command(
                label=f"{name}.execute.attempt_{attempt_number:03d}",
                command=(
                    executable,
                    "-file",
                    str(snapshot / "wolfram" / "verify_frame_face_event.wls"),
                    "--output",
                    str(report_path),
                ),
                cwd=backend_dir,
                env=env,
                isolation=isolation,
                logs_dir=logs_dir,
                timeout_seconds=timeout_seconds,
            )
            execution_license_state = _wolfram_license_availability_state_for_step(
                execution, logs_dir
            )
            if execution_license_state is not None:
                attempts.append(
                    {
                        "attempt": attempt_number,
                        "exit_code": execution.get("exit_code"),
                        "license_availability_state": execution_license_state,
                        "phase": "formal_execution",
                        "report_path": report_path.relative_to(output_dir).as_posix(),
                        "stderr_log": execution.get("stderr_log"),
                        "stdout_log": execution.get("stdout_log"),
                    }
                )
            elif execution.get("exit_code") != 0:
                status = _classify_nonzero(execution, logs_dir)
                result = _base_backend_result(
                    name, status=status, reason="formal command did not succeed"
                )
                break
            else:
                break

        remaining_seconds = deadline - time.monotonic()
        if remaining_seconds <= 0:
            wait_deadline_exhausted = True
            result = _base_backend_result(
                name,
                status="ENVIRONMENT_GAP",
                reason=(
                    "Wolfram license/activation availability did not recover before the "
                    "configured bounded wait deadline"
                ),
            )
            break
        sleep_seconds = min(float(license_poll_seconds), remaining_seconds)
        attempts[-1]["sleep_seconds_before_retry"] = round(sleep_seconds, 3)
        time.sleep(sleep_seconds)

    waited_seconds = round(time.monotonic() - wait_started, 3)
    license_wait = {
        "attempts": attempts,
        "configured_poll_seconds": license_poll_seconds,
        "configured_wait_seconds": license_wait_seconds,
        "no_activation_or_relicensing_attempted": True,
        "status": (
            "NOT_NEEDED"
            if not attempts
            else "ENVIRONMENT_GAP"
            if wait_deadline_exhausted
            else "WAITED_AND_CONTINUED"
        ),
        "waited_seconds": waited_seconds,
    }
    if execution is None or execution.get("exit_code") != 0:
        result.update(
            {
                "executable": executable,
                "execution": execution,
                "license_slot_wait": license_wait,
                "version_probe": version,
                "xact_isolated_materialization": xact_materialization,
            }
        )
        return result

    assert report_path is not None
    if _step_has_environment_gap(version, logs_dir):
        result = _base_backend_result(
            name,
            status="ENVIRONMENT_GAP",
            reason="Wolfram version probe lost the verified namespace boundary",
        )
    else:
        report, report_error = _parse_report(report_path, source="wolfram report")
        prompt = _prompt_payload(snapshot, "wolfram")
        expected_count = prompt.get("required_checks", {}).get("expected_check_count")
        checks = report.get("checks") if report is not None else None
        declared_check_ids = re.findall(
            r'AddCheck\["([^"]+)"',
            (snapshot / "wolfram" / "verify_frame_face_event.wls").read_text(
                encoding="utf-8"
            ),
        )
        reported_check_ids = (
            [item.get("id") for item in checks if isinstance(item, dict)]
            if isinstance(checks, list)
            else []
        )
        toolchain = report.get("toolchain") if report is not None else None
        valid = (
            report_error is None
            and report is not None
            and version.get("exit_code") == 0
            and bool(_combined_output(version, logs_dir).strip())
            and report.get("status") == "PASS"
            and "NONAUTHORITATIVE" in str(report.get("authority", "")).upper()
            and isinstance(toolchain, dict)
            and bool(toolchain.get("wolfram"))
            and toolchain.get("xact_xtensor_loaded") is True
            and isinstance(checks, list)
            and isinstance(expected_count, int)
            and len(checks) == expected_count
            and reported_check_ids == declared_check_ids
            and all(item.get("passed") is True for item in checks if isinstance(item, dict))
            and all(isinstance(item, dict) for item in checks)
            and report.get("failed_check_ids") == []
            and report.get("event_surfaces")
            == ["CHARACTERISTIC_R_H_ZERO", "RED_FACE_V_X_ZERO", "BLUE_FACE_V_X_ZERO"]
            and report.get("formula_package", {}).get("sha256")
            == "15f0d1af469f333d14488900b6ef031aaba071643efecdc850f4720aa7155e12"
        )
        if valid and xact_materialization.get("toolchain_status") != "PASS":
            result = _base_backend_result(
                name,
                status="TOOLCHAIN_MISMATCH",
                reason=(
                    "xAct loaded, but its runtime bytes are not bound to the exact locked archive"
                ),
            )
        else:
            result = _base_backend_result(
                name,
                status="PASS" if valid else "FAIL",
                reason="all exact checks held" if valid else (report_error or "invalid Wolfram report"),
            )
    result.update(
        {
            "executable": executable,
            "execution": execution,
            "license_slot_wait": license_wait,
            "version_probe": version,
            "xact_isolated_materialization": xact_materialization,
        }
    )
    return result

def _run_sage_singular(
    *, snapshot: Path, output_dir: Path, env: Mapping[str, str],
    isolation: Mapping[str, Any], timeout_seconds: int
) -> dict[str, Any]:
    name = "sage_singular"
    backend_dir = output_dir / "backends" / name
    logs_dir = backend_dir / "logs"
    backend_dir.mkdir(parents=True, exist_ok=True)
    sage = shutil.which("sage")
    singular = shutil.which("Singular")
    if sage is None:
        result = _base_backend_result(name, status="ENVIRONMENT_GAP", reason="sage not found")
        result["standalone_singular_executable"] = singular
        return result
    sage_version = _probe(
        backend=f"{name}.sage",
        executable=sage,
        arguments=("--version",),
        cwd=backend_dir,
        env=env,
        isolation=isolation,
        logs_dir=logs_dir,
        timeout_seconds=timeout_seconds,
    )
    singular_version = None
    if singular is not None:
        singular_version = _probe(
            backend=f"{name}.singular",
            executable=singular,
            arguments=("--version",),
            cwd=backend_dir,
            env=env,
            isolation=isolation,
            logs_dir=logs_dir,
            timeout_seconds=timeout_seconds,
        )
    execution = _run_command(
        label=f"{name}.execute",
        command=(sage, str(snapshot / "sage" / "verify_remap_event.sage")),
        cwd=backend_dir,
        env=env,
        isolation=isolation,
        logs_dir=logs_dir,
        timeout_seconds=timeout_seconds,
    )
    if execution.get("exit_code") != 0:
        status = _classify_nonzero(execution, logs_dir)
        result = _base_backend_result(name, status=status, reason="formal command did not succeed")
    elif _step_has_environment_gap(sage_version, logs_dir) or (
        singular_version is not None
        and _step_has_environment_gap(singular_version, logs_dir)
    ):
        result = _base_backend_result(
            name,
            status="ENVIRONMENT_GAP",
            reason="Sage/Singular version probe lost the verified namespace boundary",
        )
    elif sage_version.get("exit_code") != 0 or not _combined_output(
        sage_version, logs_dir
    ).strip():
        result = _base_backend_result(
            name,
            status="TOOLCHAIN_MISMATCH",
            reason="Sage runtime version could not be captured exactly",
        )
    else:
        stdout_path = logs_dir.parent / str(execution["stdout_log"])
        report, report_error = _parse_report(stdout_path, source="Sage stdout report")
        prompt = _prompt_payload(snapshot, "sage")
        expected_count = prompt.get("receipt_contract", {}).get(
            "successful_path_expected_check_count"
        )
        checks = report.get("checks") if report is not None else None
        toolchain = report.get("toolchain") if report is not None else None
        valid = (
            report_error is None
            and report is not None
            and sage_version.get("exit_code") == 0
            and bool(_combined_output(sage_version, logs_dir).strip())
            and "NONAUTHORITATIVE" in str(report.get("authority", "")).upper()
            and report.get("physical_authority_status") == PHYSICAL_AUTHORITY_STATUS
            and report.get("implementation_parity_status") == "NOT_ESTABLISHED"
            and report.get("status") == "FORMAL_IDENTITIES_HOLD_NONAUTHORITATIVE"
            and report.get("exit_code") == 0
            and isinstance(toolchain, dict)
            and bool(toolchain.get("sage"))
            and toolchain.get("polynomial_backend") == "libSingular"
            and isinstance(checks, list)
            and isinstance(expected_count, int)
            and len(checks) == expected_count
            and all(isinstance(item, dict) and item.get("holds") is True for item in checks)
            and report.get("failed_check_ids") == []
        )
        if valid and report is not None:
            _write_json(backend_dir / "report.json", report)
        if valid and singular is None:
            result = _base_backend_result(
                name,
                status="ENVIRONMENT_GAP",
                reason="standalone Singular version executable not found; receipt is uncomparable",
            )
        elif valid and singular_version is not None and (
            singular_version.get("exit_code") != 0
            or not _combined_output(singular_version, logs_dir).strip()
        ):
            result = _base_backend_result(
                name,
                status="TOOLCHAIN_MISMATCH",
                reason="standalone Singular version could not be captured",
            )
        else:
            result = _base_backend_result(
                name,
                status="PASS" if valid else "FAIL",
                reason="all exact checks held" if valid else (report_error or "invalid Sage report"),
            )
    result.update(
        {
            "executable": sage,
            "execution": execution,
            "sage_version_probe": sage_version,
            "standalone_singular_executable": singular,
            "singular_version_probe": singular_version,
        }
    )
    return result


def _run_lean(
    *, snapshot: Path, output_dir: Path, env: Mapping[str, str],
    isolation: Mapping[str, Any], timeout_seconds: int
) -> dict[str, Any]:
    name = "lean_mathlib"
    backend_dir = output_dir / "backends" / name
    logs_dir = backend_dir / "logs"
    backend_dir.mkdir(parents=True, exist_ok=True)
    lake = shutil.which("lake")
    lean = shutil.which("lean")
    executables = {"lake": lake, "lean": lean}

    def finish(status: str, reason: str, **details: Any) -> dict[str, Any]:
        result = _base_backend_result(name, status=status, reason=reason)
        result.update({"executables": executables, **details})
        return result

    if lake is None or lean is None:
        return finish(
            "ENVIRONMENT_GAP",
            "lean and lake executables are both required for the pinned rebuild lane",
        )
    source_raw = os.environ.get("REC_NEXT03_LEAN_WORKSPACE")
    rebuild_raw = os.environ.get("REC_NEXT03_LEAN_REBUILD_WORKSPACE")
    if not source_raw or not rebuild_raw:
        return finish(
            "ENVIRONMENT_GAP",
            "REC_NEXT03_LEAN_WORKSPACE and REC_NEXT03_LEAN_REBUILD_WORKSPACE are required",
        )
    source_path = Path(source_raw).expanduser()
    rebuild_path = Path(rebuild_raw).expanduser()
    if not source_path.is_absolute() or not rebuild_path.is_absolute():
        return finish("ENVIRONMENT_GAP", "Lean source and rebuild paths must be absolute")
    source = source_path.resolve()
    rebuild = rebuild_path.resolve()
    if source == rebuild:
        return finish("ENVIRONMENT_GAP", "Lean rebuild workspace must differ from source")
    if _is_within(rebuild, source) or _is_within(source, rebuild):
        return finish("ENVIRONMENT_GAP", "Lean source and rebuild workspaces must be disjoint")
    if _is_within(rebuild, source) or _is_within(source, rebuild):
        return finish("ENVIRONMENT_GAP", "Lean source and rebuild workspaces must be disjoint")
    if _git_container(rebuild) is not None:
        return finish("ENVIRONMENT_GAP", "Lean rebuild workspace must be outside every Git worktree")
    if not _is_within(rebuild, output_dir.resolve()):
        return finish(
            "ENVIRONMENT_GAP",
            "Lean rebuild workspace must be confined to the selected output directory",
        )
    if not source.is_dir():
        return finish("ENVIRONMENT_GAP", "Lean source workspace is not an existing directory")
    if rebuild.exists() and (not rebuild.is_dir() or any(rebuild.iterdir())):
        return finish("ENVIRONMENT_GAP", "Lean rebuild workspace must be new or empty")
    source_symlink_errors = _workspace_symlink_errors(source)
    if source_symlink_errors:
        return finish(
            "TOOLCHAIN_MISMATCH",
            "Lean source workspace contains unsafe symlinks",
            source_symlink_errors=source_symlink_errors,
        )

    snapshot_identity = _lean_source_identity(snapshot / "lean")
    source_identity = _lean_source_identity(source)
    if snapshot_identity is None or source_identity != snapshot_identity:
        return finish(
            "TOOLCHAIN_MISMATCH",
            "Lean source workspace formal sources are not byte-identical to checked input",
            snapshot_source_sha256=snapshot_identity,
            source_workspace_sha256=source_identity,
        )
    manifest_path = source / "lake-manifest.json"
    mathlib_path = source / ".lake" / "packages" / "mathlib"
    if not manifest_path.is_file() or not mathlib_path.is_dir():
        return finish(
            "ENVIRONMENT_GAP",
            "Lean source workspace lacks lake-manifest.json or materialized mathlib checkout",
        )
    try:
        manifest_payload = _load_json_text(
            manifest_path.read_text(encoding="utf-8"), source=str(manifest_path)
        )
        manifest_entry, manifest_error = _manifest_mathlib_entry(manifest_payload)
        lakefile_entry, lakefile_error = _lakefile_mathlib_requirement(
            (source / "lakefile.toml").read_text(encoding="utf-8")
        )
    except (OSError, ContractError) as exc:
        return finish("TOOLCHAIN_MISMATCH", f"invalid materialized Lake identity: {exc}")
    if manifest_error or lakefile_error:
        return finish(
            "TOOLCHAIN_MISMATCH",
            "Lean dependency identity contract did not validate",
            lakefile_error=lakefile_error,
            manifest_error=manifest_error,
        )
    source_tree_before = _collect_tree_hashes(source)
    source_git_identity = _git_checkout_identity(
        label=f"{name}.source_mathlib",
        repository=mathlib_path,
        expected_head=MATHLIB_COMMIT,
        env=env,
        isolation=isolation,
        logs_dir=logs_dir,
        timeout_seconds=timeout_seconds,
    )
    if source_git_identity.get("status") != "PASS":
        return finish(
            str(source_git_identity.get("status", "TOOLCHAIN_MISMATCH")),
            "materialized mathlib checkout identity did not validate",
            source_git_identity=source_git_identity,
        )

    rebuild.parent.mkdir(parents=True, exist_ok=True)
    if rebuild.exists():
        rebuild.rmdir()
    source_canonical = source.resolve()

    def ignore_source_root_git(directory: str, names: list[str]) -> set[str]:
        return {".git"} if Path(directory).resolve() == source_canonical and ".git" in names else set()

    shutil.copytree(source, rebuild, symlinks=True, ignore=ignore_source_root_git)
    if _git_container(rebuild) is not None:
        return finish(
            "FAIL",
            "Lean rebuild copy unexpectedly became a Git worktree",
        )
    rebuild_identity = _lean_source_identity(rebuild)
    rebuild_manifest_path = rebuild / "lake-manifest.json"
    rebuild_mathlib_path = rebuild / ".lake" / "packages" / "mathlib"
    try:
        rebuild_manifest_payload = _load_json_text(
            rebuild_manifest_path.read_text(encoding="utf-8"),
            source=str(rebuild_manifest_path),
        )
        copied_manifest_entry, copied_manifest_error = _manifest_mathlib_entry(
            rebuild_manifest_payload
        )
        copied_lakefile_entry, copied_lakefile_error = _lakefile_mathlib_requirement(
            (rebuild / "lakefile.toml").read_text(encoding="utf-8")
        )
    except (OSError, ContractError) as exc:
        return finish("TOOLCHAIN_MISMATCH", f"copied Lake identity invalid: {exc}")
    rebuild_git_identity_before = _git_checkout_identity(
        label=f"{name}.rebuild_mathlib_before",
        repository=rebuild_mathlib_path,
        expected_head=MATHLIB_COMMIT,
        env=env,
        isolation=isolation,
        logs_dir=logs_dir,
        timeout_seconds=timeout_seconds,
    )
    copy_errors = _workspace_symlink_errors(rebuild)
    if rebuild_identity != snapshot_identity:
        copy_errors.append("copied formal source identity differs from checked input")
    if _sha256(rebuild_manifest_path) != _sha256(manifest_path):
        copy_errors.append("copied manifest differs from source manifest")
    if copied_manifest_error or copied_lakefile_error:
        copy_errors.extend(
            error for error in (copied_manifest_error, copied_lakefile_error) if error
        )
    if copied_manifest_entry != manifest_entry or copied_lakefile_entry != lakefile_entry:
        copy_errors.append("copied structured dependency identity differs from source")
    if rebuild_git_identity_before.get("status") != "PASS":
        copy_errors.extend(str(item) for item in rebuild_git_identity_before.get("errors", []))
    if copy_errors:
        return finish(
            "TOOLCHAIN_MISMATCH",
            "output-only Lean rebuild copy failed identity validation",
            copy_errors=copy_errors,
            rebuild_git_identity_before=rebuild_git_identity_before,
        )

    version_probes = {
        "lean": _probe(
            backend=f"{name}.lean",
            executable=lean,
            arguments=("--version",),
            cwd=rebuild,
            env=env,
            isolation=isolation,
            logs_dir=logs_dir,
            timeout_seconds=timeout_seconds,
        ),
        "lake": _probe(
            backend=f"{name}.lake",
            executable=lake,
            arguments=("--version",),
            cwd=rebuild,
            env=env,
            isolation=isolation,
            logs_dir=logs_dir,
            timeout_seconds=timeout_seconds,
        ),
        "lake_env_lean": _run_command(
            label=f"{name}.lake_env_lean.version",
            command=(lake, "env", "lean", "--version"),
            cwd=rebuild,
            env=env,
            isolation=isolation,
            logs_dir=logs_dir,
            timeout_seconds=min(timeout_seconds, 60),
        ),
    }
    if any(_step_has_environment_gap(step, logs_dir) for step in version_probes.values()):
        return finish(
            "ENVIRONMENT_GAP",
            "Lean version probe lost the verified namespace boundary",
            version_probes=version_probes,
        )
    if (
        not _probe_contains(version_probes["lean"], logs_dir, "4.33.0")
        or not _probe_contains(version_probes["lake_env_lean"], logs_dir, "4.33.0")
        or version_probes["lake"].get("exit_code") != 0
    ):
        return finish(
            "TOOLCHAIN_MISMATCH",
            "Lean/Lake runtime version does not match the 4.33.0 lane",
            version_probes=version_probes,
        )

    clean_step = _run_command(
        label=f"{name}.lake_clean",
        command=(lake, "clean"),
        cwd=rebuild,
        env=env,
        isolation=isolation,
        logs_dir=logs_dir,
        timeout_seconds=timeout_seconds,
    )
    if clean_step.get("exit_code") != 0:
        return finish(
            _classify_nonzero(clean_step, logs_dir),
            "lake clean did not complete in the rebuild workspace",
            clean_step=clean_step,
        )
    reset = _purge_lean_build_artifacts(rebuild, rebuild_manifest_payload)
    if reset.get("status") != "PASS":
        return finish(
            "FAIL",
            "pre-materialized Lean artifacts could not be purged fail-closed",
            clean_step=clean_step,
            reset=reset,
        )

    dependency_step = _run_command(
        label=f"{name}.build_mathlib",
        command=(lake, "build", "@mathlib"),
        cwd=rebuild,
        env=env,
        isolation=isolation,
        logs_dir=logs_dir,
        timeout_seconds=timeout_seconds,
    )
    if dependency_step.get("exit_code") != 0:
        return finish(
            _classify_nonzero(dependency_step, logs_dir),
            "bounded clean mathlib rebuild did not complete",
            dependency_step=dependency_step,
            reset=reset,
        )
    dependency_inventory = _lean_artifact_inventory(rebuild)
    if dependency_inventory["count"] == 0:
        return finish(
            "FAIL",
            "mathlib rebuild produced no auditable Lean compiled artifacts",
            dependency_step=dependency_step,
            dependency_inventory=dependency_inventory,
        )

    aggregate_step = _run_command(
        label=f"{name}.build_aggregate",
        command=(lake, "build", "@/RecNext03"),
        cwd=rebuild,
        env=env,
        isolation=isolation,
        logs_dir=logs_dir,
        timeout_seconds=timeout_seconds,
    )
    if aggregate_step.get("exit_code") != 0:
        return finish(
            _classify_nonzero(aggregate_step, logs_dir),
            "bounded RecNext03 aggregate rebuild did not complete",
            aggregate_step=aggregate_step,
            dependency_step=dependency_step,
            dependency_inventory=dependency_inventory,
            reset=reset,
        )
    cache_findings = _lean_cache_reuse_findings(
        (clean_step, dependency_step, aggregate_step), logs_dir
    )
    if cache_findings:
        return finish(
            "FAIL",
            "Lean build logs indicate forbidden artifact-cache restore/reuse",
            cache_findings=cache_findings,
        )
    aggregate_inventory = _lean_artifact_inventory(rebuild / ".lake" / "build")
    if aggregate_inventory["count"] == 0:
        return finish(
            "FAIL",
            "aggregate build produced no root-package compiled artifacts",
            aggregate_step=aggregate_step,
            aggregate_inventory=aggregate_inventory,
        )

    prompt = _prompt_payload(snapshot, "lean")
    audit_policy = _audit_policy(prompt)
    expected = audit_policy.get("expected_theorems", [])
    allowed = audit_policy.get("allowed_foundation_axioms", [])
    audit = _parse_lean_assumption_audit(
        _combined_output(aggregate_step, logs_dir), expected=expected, allowed_axioms=allowed
    )
    rebuild_git_identity_after = _git_checkout_identity(
        label=f"{name}.rebuild_mathlib_after",
        repository=rebuild_mathlib_path,
        expected_head=MATHLIB_COMMIT,
        env=env,
        isolation=isolation,
        logs_dir=logs_dir,
        timeout_seconds=timeout_seconds,
    )
    source_unchanged = source_tree_before == _collect_tree_hashes(source)
    identities_unchanged = (
        rebuild_git_identity_after.get("status") == "PASS"
        and _sha256(rebuild_manifest_path) == _sha256(manifest_path)
        and _lean_source_identity(rebuild) == snapshot_identity
    )
    status = (
        "PASS"
        if audit.get("status") == "PASS" and source_unchanged and identities_unchanged
        else "FAIL"
    )
    reason = (
        "clean source rebuild and exact 25-theorem Lean assumption audit held"
        if status == "PASS"
        else "Lean rebuild, source immutability, or exact assumption audit failed"
    )
    return finish(
        status,
        reason,
        aggregate_artifact_inventory=aggregate_inventory,
        aggregate_step=aggregate_step,
        assumption_audit=audit,
        cache_policy={
            "build_log_cache_reuse_findings": cache_findings,
            "cleared_inherited": list(CLEARED_LEAN_CACHE_OVERRIDES),
            "effective": {
                "LAKE_ARTIFACT_CACHE": "false",
                "LAKE_NO_CACHE": "1",
                "LAKE_RESTORE_ARTIFACTS": "0",
            },
        },
        dependency_artifact_inventory=dependency_inventory,
        dependency_step=dependency_step,
        lakefile_requirement=lakefile_entry,
        manifest_entry=manifest_entry,
        manifest_sha256=_sha256(manifest_path),
        rebuild_git_identity_after=rebuild_git_identity_after,
        rebuild_git_identity_before=rebuild_git_identity_before,
        rebuild_workspace=str(rebuild),
        reset=reset,
        source_git_identity=source_git_identity,
        source_unchanged=source_unchanged,
        source_workspace=str(source),
        source_workspace_sha256=source_identity,
        version_probes=version_probes,
    )


def _version_has_exact_lane(output: str, lane: str) -> bool:
    return re.search(rf"(?<![0-9.]){re.escape(lane)}(?![0-9.])", output) is not None


def _run_rocq(
    *, snapshot: Path, output_dir: Path, env: Mapping[str, str],
    isolation: Mapping[str, Any], timeout_seconds: int
) -> dict[str, Any]:
    name = "rocq"
    backend_dir = output_dir / "backends" / name
    logs_dir = backend_dir / "logs"
    work_dir = backend_dir / "work"
    backend_dir.mkdir(parents=True, exist_ok=True)
    candidates = {
        "rocq_compile": shutil.which("rocq"),
        "rocqc": shutil.which("rocqc"),
        "coqc": shutil.which("coqc"),
    }

    def finish(status: str, reason: str, **details: Any) -> dict[str, Any]:
        result = _base_backend_result(name, status=status, reason=reason)
        result.update({"candidate_executables": candidates, **details})
        return result

    installed = [(frontend, executable) for frontend, executable in candidates.items() if executable]
    if not installed:
        return finish("ENVIRONMENT_GAP", "rocq, rocqc, and coqc are all unavailable")
    if work_dir.exists():
        return finish("FAIL", "disposable Rocq work directory unexpectedly exists")
    shutil.copytree(snapshot / "rocq", work_dir, symlinks=True)
    if _workspace_symlink_errors(work_dir):
        return finish("FAIL", "Rocq disposable copy contains unsafe symlinks")

    frontend_receipts: dict[str, Any] = {}
    valid_frontends: list[tuple[str, str, str]] = []
    for frontend, executable_value in installed:
        assert executable_value is not None
        where_arguments = ("compile", "-where") if frontend == "rocq_compile" else ("-where",)
        version = _probe(
            backend=f"{name}.{frontend}",
            executable=executable_value,
            arguments=("--version",),
            cwd=work_dir,
            env=env,
            isolation=isolation,
            logs_dir=logs_dir,
            timeout_seconds=timeout_seconds,
        )
        where = _run_command(
            label=f"{name}.{frontend}.where",
            command=(executable_value, *where_arguments),
            cwd=work_dir,
            env=env,
            isolation=isolation,
            logs_dir=logs_dir,
            timeout_seconds=min(timeout_seconds, 60),
        )
        version_output = _combined_output(version, logs_dir).strip()
        where_lines = [line.strip() for line in _command_stdout(where, logs_dir).splitlines() if line.strip()]
        root_value = where_lines[0] if len(where_lines) == 1 else ""
        root = Path(root_value).resolve() if root_value and Path(root_value).is_absolute() else None
        valid = (
            version.get("exit_code") == 0
            and _version_has_exact_lane(version_output, "9.2.0")
            and where.get("exit_code") == 0
            and len(where_lines) == 1
            and root is not None
            and root.is_dir()
        )
        frontend_receipts[frontend] = {
            "executable": str(Path(executable_value).resolve()),
            "root": str(root) if root is not None else None,
            "valid_9_2_lane": valid,
            "version_probe": version,
            "version_stdout": version_output,
            "where_probe": where,
            "where_stdout_lines": where_lines,
        }
        if valid and root is not None:
            valid_frontends.append((frontend, executable_value, str(root)))

    selected_name = "rocq_compile" if candidates["rocq_compile"] else (
        "rocqc" if candidates["rocqc"] else "coqc"
    )
    if any(
        _step_has_environment_gap(receipt["version_probe"], logs_dir)
        or _step_has_environment_gap(receipt["where_probe"], logs_dir)
        for receipt in frontend_receipts.values()
    ):
        return finish(
            "ENVIRONMENT_GAP",
            "Rocq frontend discovery lost the verified namespace boundary",
            frontend_receipts=frontend_receipts,
        )
    selected_receipt = frontend_receipts[selected_name]
    if not selected_receipt["valid_9_2_lane"]:
        return finish(
            "TOOLCHAIN_MISMATCH",
            "selected Rocq frontend did not establish the exact 9.2.0 -where lane",
            frontend_receipts=frontend_receipts,
            selected_frontend=selected_name,
        )
    successful_roots = {root for _, _, root in valid_frontends}
    if len(successful_roots) != 1:
        return finish(
            "TOOLCHAIN_MISMATCH",
            "successful Rocq 9.2 frontends disagree on the canonical Stdlib root",
            frontend_receipts=frontend_receipts,
            successful_roots=sorted(successful_roots),
        )
    selected_executable = candidates[selected_name]
    assert selected_executable is not None
    stdlib_root = Path(next(iter(successful_roots)))
    prompt = _prompt_payload(snapshot, "rocq")
    audit_policy = _audit_policy(prompt)
    expected = audit_policy.get("expected_theorems", [])
    allowed_foundations = audit_policy.get("allowed_foundation_axioms", [])
    required_origins = [
        "Stdlib.Init.Prelude",
        "Stdlib.Reals.Rdefinitions",
        "Stdlib.Reals.Raxioms",
        "Stdlib.Logic.Classical_Prop",
    ]
    for rule in allowed_foundations:
        if isinstance(rule, dict) and isinstance(rule.get("required_origin"), str):
            required_origins.append(rule["required_origin"])
    stdlib_identity = _rocq_stdlib_identity(stdlib_root, required_origins)
    if stdlib_identity.get("status") != "PASS":
        return finish(
            "TOOLCHAIN_MISMATCH",
            "Rocq Stdlib root or allowed foundation origin identity did not validate",
            frontend_receipts=frontend_receipts,
            stdlib_identity=stdlib_identity,
        )
    rocq_multicall = candidates["rocq_compile"]
    make = shutil.which("make")
    if rocq_multicall is None or make is None:
        return finish(
            "ENVIRONMENT_GAP",
            "contracted rocq makefile and make executables are both required",
            frontend_receipts=frontend_receipts,
            stdlib_identity=stdlib_identity,
        )
    makefile_step = _run_command(
        label=f"{name}.makefile",
        command=(rocq_multicall, "makefile", "-f", "_CoqProject", "-o", "Makefile.rec-next03"),
        cwd=work_dir,
        env=env,
        isolation=isolation,
        logs_dir=logs_dir,
        timeout_seconds=timeout_seconds,
    )
    if makefile_step.get("exit_code") != 0:
        return finish(
            _classify_nonzero(makefile_step, logs_dir),
            "rocq makefile generation failed",
            makefile_step=makefile_step,
        )
    build_step = _run_command(
        label=f"{name}.build",
        command=(make, "-f", "Makefile.rec-next03"),
        cwd=work_dir,
        env=env,
        isolation=isolation,
        logs_dir=logs_dir,
        timeout_seconds=timeout_seconds,
    )
    if build_step.get("exit_code") != 0:
        return finish(
            _classify_nonzero(build_step, logs_dir),
            "Rocq project build failed",
            build_step=build_step,
            makefile_step=makefile_step,
        )
    audit_source = work_dir / "RunnerAssumptionAudit.v"
    _write_bytes(audit_source, _rocq_audit_source(expected))
    audit_command = (
        (selected_executable, "compile", audit_source.name)
        if selected_name == "rocq_compile"
        else (selected_executable, audit_source.name)
    )
    audit_step = _run_command(
        label=f"{name}.assumption_audit",
        command=audit_command,
        cwd=work_dir,
        env=env,
        isolation=isolation,
        logs_dir=logs_dir,
        timeout_seconds=timeout_seconds,
    )
    if audit_step.get("exit_code") != 0:
        return finish(
            _classify_nonzero(audit_step, logs_dir),
            "Rocq exact assumption audit compilation failed",
            audit_step=audit_step,
            build_step=build_step,
        )
    audit = _parse_rocq_assumption_audit(
        _combined_output(audit_step, logs_dir),
        expected=expected,
        allowed_foundations=allowed_foundations,
    )
    referenced_origins = {
        assumption["origin"]
        for record in audit.get("records", [])
        for assumption in record.get("assumptions", [])
    }
    unresolved_origins = sorted(
        referenced_origins - set(stdlib_identity.get("module_files", {}))
    )
    status = "PASS" if audit.get("status") == "PASS" and not unresolved_origins else "FAIL"
    reason = (
        "Rocq build and exact 25-theorem assumption-origin audit held"
        if status == "PASS"
        else "Rocq exact theorem assumption/origin audit failed"
    )
    return finish(
        status,
        reason,
        assumption_audit=audit,
        audit_step=audit_step,
        build_step=build_step,
        disposable_work_directory=str(work_dir),
        frontend_receipts=frontend_receipts,
        makefile_step=makefile_step,
        selected_frontend=selected_name,
        selected_frontend_executable=str(Path(selected_executable).resolve()),
        stdlib_identity=stdlib_identity,
        unresolved_origins=unresolved_origins,
    )


def _prepare_output_dir(raw: str) -> Path:
    output_dir = Path(raw).expanduser().resolve()
    if _is_within(output_dir, REPOSITORY_ROOT):
        raise ContractError("--output-dir must be outside this Git worktree")
    git_container = _git_container(output_dir)
    if git_container is not None:
        raise ContractError(
            f"--output-dir must not be inside any Git worktree/repository: {git_container}"
        )
    if output_dir.exists():
        if not output_dir.is_dir():
            raise ContractError("--output-dir exists and is not a directory")
        if any(output_dir.iterdir()):
            raise ContractError("--output-dir must be new or empty")
    else:
        output_dir.mkdir(parents=True)
    return output_dir


def run_all(
    *, output_dir: Path, timeout_seconds: int,
    wolfram_license_wait_seconds: int = WOLFRAM_LICENSE_WAIT_DEFAULT_SECONDS,
    wolfram_license_poll_seconds: int = WOLFRAM_LICENSE_POLL_DEFAULT_SECONDS,
) -> dict[str, Any]:
    contract = check_contract()
    if contract["status"] != "PASS":
        report = {
            "admission_allowed": False,
            "authority": AUTHORITY,
            "backends": {},
            "blockers_resolved": [],
            "contract": contract,
            "mode": "RUN_ALL",
            "physical_authority_status": PHYSICAL_AUTHORITY_STATUS,
            "schema": "rec-next03-formal-runner/v1",
            "scientific_claim": SCIENTIFIC_CLAIM,
            "scientific_terminal": SCIENTIFIC_TERMINAL,
            "source_authority_status": SOURCE_AUTHORITY_STATUS,
            "status": "FAIL",
        }
        _write_json(output_dir / "formal-run.json", report)
        return report

    before_hashes = _collect_tree_hashes(FORMAL_ROOT)
    snapshot = output_dir / "input" / "formal" / "rec_next03"
    snapshot.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(FORMAL_ROOT, snapshot, symlinks=True)
    env = _isolated_environment(output_dir)
    network_isolation, isolation = _probe_network_isolation(
        output_dir=output_dir,
        env=env,
        timeout_seconds=timeout_seconds,
    )
    environment_boundary = {
        "cleared_lean_cache_overrides": list(CLEARED_LEAN_CACHE_OVERRIDES),
        "cleared_search_overrides": list(CLEARED_SEARCH_OVERRIDES),
        "effective_lean_cache_controls": {
            "LAKE_ARTIFACT_CACHE": "false",
            "LAKE_NO_CACHE": "1",
            "LAKE_RESTORE_ARTIFACTS": "0",
        },
        "effective_search_overrides": {
            variable: None for variable in CLEARED_SEARCH_OVERRIDES
        },
        "runner_controlled_paths_only": True,
    }
    if isolation is None:
        reason = NETWORK_GAP_REASON
        backends = {
            backend: _base_backend_result(backend, status="ENVIRONMENT_GAP", reason=reason)
            for backend in ("wolfram_xact", "sage_singular", "lean_mathlib", "rocq")
        }
        for backend, result in backends.items():
            _write_json(output_dir / "backends" / backend / "result.json", result)
        after_hashes = _collect_tree_hashes(FORMAL_ROOT)
        report = {
            "admission_allowed": False,
            "authority": AUTHORITY,
            "backends": backends,
            "blockers_resolved": [],
            "contract": contract,
            "environment_boundary": environment_boundary,
            "formal_tree_unchanged": before_hashes == after_hashes,
            "mode": "RUN_ALL",
            "network_isolation": network_isolation,
            "physical_authority_status": PHYSICAL_AUTHORITY_STATUS,
            "schema": "rec-next03-formal-runner/v1",
            "scientific_claim": SCIENTIFIC_CLAIM,
            "scientific_terminal": SCIENTIFIC_TERMINAL,
            "source_authority_status": SOURCE_AUTHORITY_STATUS,
            "status": "ENVIRONMENT_GAP",
        }
        _write_json(output_dir / "formal-run.json", report)
        return report
    backends: dict[str, Any] = {}
    result = _run_wolfram(
        snapshot=snapshot,
        output_dir=output_dir,
        env=env,
        isolation=isolation,
        timeout_seconds=timeout_seconds,
        license_wait_seconds=wolfram_license_wait_seconds,
        license_poll_seconds=wolfram_license_poll_seconds,
    )
    backends[str(result["backend"])] = result
    _write_json(output_dir / "backends" / str(result["backend"]) / "result.json", result)
    for run_backend in (_run_sage_singular, _run_lean, _run_rocq):
        result = run_backend(
            snapshot=snapshot,
            output_dir=output_dir,
            env=env,
            isolation=isolation,
            timeout_seconds=timeout_seconds,
        )
        backends[str(result["backend"])] = result
        _write_json(output_dir / "backends" / str(result["backend"]) / "result.json", result)

    after_hashes = _collect_tree_hashes(FORMAL_ROOT)
    repository_unchanged = before_hashes == after_hashes
    statuses = [str(result["status"]) for result in backends.values()]
    if not repository_unchanged or "FAIL" in statuses:
        overall = "FAIL"
    elif "TOOLCHAIN_MISMATCH" in statuses:
        overall = "TOOLCHAIN_MISMATCH"
    elif "ENVIRONMENT_GAP" in statuses:
        overall = "ENVIRONMENT_GAP"
    elif statuses and all(status == "PASS" for status in statuses):
        overall = "PASS"
    else:
        overall = "FAIL"
    report = {
        "admission_allowed": False,
        "authority": AUTHORITY,
        "backends": backends,
        "blockers_resolved": [],
        "contract": contract,
        "environment_boundary": environment_boundary,
        "formal_tree_unchanged": repository_unchanged,
        "mode": "RUN_ALL",
        "network_isolation": network_isolation,
        "physical_authority_status": PHYSICAL_AUTHORITY_STATUS,
        "schema": "rec-next03-formal-runner/v1",
        "scientific_claim": SCIENTIFIC_CLAIM,
        "scientific_terminal": SCIENTIFIC_TERMINAL,
        "source_authority_status": SOURCE_AUTHORITY_STATUS,
        "status": overall,
    }
    _write_json(output_dir / "formal-run.json", report)
    return report


def _argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check-contract", action="store_true")
    mode.add_argument("--run-all", action="store_true")
    parser.add_argument("--output-dir")
    parser.add_argument("--timeout-seconds", type=int, default=3600)
    parser.add_argument(
        "--wolfram-license-wait-seconds",
        type=int,
        default=WOLFRAM_LICENSE_WAIT_DEFAULT_SECONDS,
    )
    parser.add_argument(
        "--wolfram-license-poll-seconds",
        type=int,
        default=WOLFRAM_LICENSE_POLL_DEFAULT_SECONDS,
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = _argument_parser()
    args = parser.parse_args(argv)
    if args.timeout_seconds <= 0:
        parser.error("--timeout-seconds must be positive")
    if args.wolfram_license_wait_seconds < 0:
        parser.error("--wolfram-license-wait-seconds must be nonnegative")
    if args.wolfram_license_poll_seconds <= 0:
        parser.error("--wolfram-license-poll-seconds must be positive")
    if args.check_contract:
        if args.output_dir is not None:
            parser.error("--output-dir is valid only with --run-all")
        report = check_contract()
        sys.stdout.write(_canonical_json(report))
        return 0 if report["status"] == "PASS" else 1
    if args.output_dir is None:
        parser.error("--run-all requires --output-dir")
    try:
        output_dir = _prepare_output_dir(args.output_dir)
        report = run_all(
            output_dir=output_dir,
            timeout_seconds=args.timeout_seconds,
            wolfram_license_wait_seconds=args.wolfram_license_wait_seconds,
            wolfram_license_poll_seconds=args.wolfram_license_poll_seconds,
        )
    except (ContractError, OSError) as exc:
        report = {
            "admission_allowed": False,
            "authority": AUTHORITY,
            "blockers_resolved": [],
            "errors": [str(exc)],
            "mode": "RUN_ALL",
            "physical_authority_status": PHYSICAL_AUTHORITY_STATUS,
            "schema": "rec-next03-formal-runner/v1",
            "scientific_claim": SCIENTIFIC_CLAIM,
            "scientific_terminal": SCIENTIFIC_TERMINAL,
            "source_authority_status": SOURCE_AUTHORITY_STATUS,
            "status": "FAIL",
        }
    sys.stdout.write(_canonical_json(report))
    if report["status"] == "PASS":
        return 0
    if report["status"] == "ENVIRONMENT_GAP":
        return 69
    if report["status"] == "TOOLCHAIN_MISMATCH":
        return 65
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
