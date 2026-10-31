#!/usr/bin/env python3
"""Check a noncanonical REC/REI prioritization overlay (not physics admission)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

DEFAULT = Path(__file__).resolve().parents[1] / "docs" / "REI_IGM_PRIORITY_OVERLAY_20261101.json"


def validate(data: dict) -> list[str]:
    issues: list[str] = []
    if data.get("schema") != "rec-rei-igm-priority-overlay.v1":
        issues.append("schema: wrong version")
    if data.get("authority_class") != "NONCANONICAL_PROCESS_OVERLAY":
        issues.append("authority: attempted canonical substitution")
    interp = data.get("interpretation", {})
    if interp.get("no_canonical_mutation") is not True:
        issues.append("authority: canonical mutation claimed")
    if interp.get("newly_admitted_central_nodes") != 0 or interp.get("newly_admitted_physical_cells") != 0:
        issues.append("admission: unsupported positive delta")
    counts = data.get("unchanged_reported_counts", {})
    for k, total in [("canonical", 88), ("rei_working", 88), ("rec_physical_H5", 313), ("rei_physical_fast", 7)]:
        row = counts.get(k, {})
        if row.get("total") != total or row.get("delta") != 0 or not isinstance(row.get("complete"), int):
            issues.append(f"count: {k} is not a frozen zero-delta snapshot")
    ctl = data.get("preserved_controls", {})
    required_true = ["no_merge", "no_owner_source_switch", "no_35hz_relaxation", "no_budget_reset"]
    required_false = ["auto_next_node", "rei_activation"]
    for k in required_true:
        if ctl.get(k) is not True:
            issues.append(f"control: {k} not preserved")
    for k in required_false:
        if ctl.get(k) is not False:
            issues.append(f"control: {k} not preserved")
    if ctl.get("production") != "HOLD" or ctl.get("original_35hz") != "FAIL7/8":
        issues.append("control: production or original HD source fail altered")
    if ctl.get("rei_no_more_ivps_at_inherited_budget") is not True:
        issues.append("control: inherited REI IVP allocation omitted")
    src = data.get("observed_sources", {})
    for s in ["rec_pr182_head", "rei_canonical_20261028_commit", "rei_canonical_20261028_sha256", "rei_program_source_commit"]:
        if not isinstance(src.get(s), str) or len(src[s]) not in (40, 64):
            issues.append(f"source: {s} missing immutable identity")
    nodes = data.get("nodes", [])
    if not isinstance(nodes, list) or not nodes:
        return issues + ["graph: no nodes"]
    ids = [n.get("id") for n in nodes]
    if len(set(ids)) != len(ids) or any(not isinstance(i, str) for i in ids):
        issues.append("graph: duplicate or invalid id")
    by_id = {n.get("id"): n for n in nodes if isinstance(n, dict)}
    for n in nodes:
        nid = n.get("id")
        if n.get("canonical_credit") != 0 or n.get("science_exec") is not False:
            issues.append(f"admission: {nid} claims unsupported completion/execution")
        for dep in n.get("requires", []):
            if dep not in by_id:
                issues.append(f"graph: {nid} has missing dependency {dep}")
    # Positive dependency graph cycle check.
    visit: dict[str, int] = {}
    def dfs(nid: str) -> None:
        old = visit.get(nid, 0)
        if old == 1:
            issues.append(f"graph: dependency cycle at {nid}")
            return
        if old == 2:
            return
        visit[nid] = 1
        for dep in by_id[nid].get("requires", []):
            if dep in by_id:
                dfs(dep)
        visit[nid] = 2
    for nid in by_id:
        dfs(nid)
    next_id = data.get("next_candidate_only")
    if next_id != "REC_REI_HISTORY_CONSUMER_BINDING" or next_id not in by_id:
        issues.append("priority: REC read-only consumer bridge not selected")
    if any("REC_HD_SPECTROSCOPY_AUX" in n.get("requires", []) for n in nodes if n.get("lane") == "DIRECT_IGM"):
        issues.append("priority: HD incorrectly made a universal EoR dependency")
    if by_id.get("REI_FIRST_COUPLED_INTERVAL", {}).get("requires"):
        issues.append("priority: first H/He interval has manufactured hard prerequisites")
    if "REC_REI_HISTORY_CONSUMER_BINDING" not in by_id.get("REI_FIRST_COUPLED_INTERVAL", {}).get("optional_input_from", []):
        issues.append("priority: optional REC bridge not explicitly distinguished")
    if by_id.get("REC_HD_SPECTROSCOPY_AUX", {}).get("lane") != "AUXILIARY_SCIENCE":
        issues.append("priority: HD task is falsely on critical lane")
    if by_id.get("REI_F08_PAIRED_S0_HISTORY", {}).get("requires") != ["REI_FIRST_COUPLED_INTERVAL"]:
        issues.append("priority: paired history missing actual interval dependency")
    return issues


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) > 1:
        print("usage: verify_rei_igm_priority_overlay.py [path.json]", file=sys.stderr)
        return 2
    path = Path(argv[0]) if argv else DEFAULT
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        errors = validate(data)
    except (OSError, ValueError, TypeError) as exc:
        print(f"INVALID_INPUT: {exc}", file=sys.stderr)
        return 2
    for error in errors:
        print(f"FAIL: {error}", file=sys.stderr)
    if errors:
        return 1
    print("PASS: noncanonical overlay, preserved gates, no invented dependency, 0 science/canonical admission")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
