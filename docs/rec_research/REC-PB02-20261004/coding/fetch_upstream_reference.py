#!/usr/bin/env python3
"""Fetch exact author-source bytes into an external cache and build the TLA probe.

No upstream files belong in this research packet or its redistributed archive.
The pinned upstream tree has no explicit license identified by the source review;
this helper neither supplies a license nor vendors the source. It retrieves only
five named public reference files, validates their identity, and builds locally.

Use --dry-run for a read-only plan, or --offline to use already verified cache
files without network calls. GNU11 is required by the upstream use of M_PI.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import urllib.request

COMMIT = "09e8243d0e08edd3603a94dfbc445ae06cafe139"
BASE = f"https://raw.githubusercontent.com/nanoomlee/HYREC-2/{COMMIT}/"
FILES = {
    "hydrogen.c": (46627, "734800ccd69b41d60b519f200003ce27c3b7640f76a70353499424842ba19616"),
    "hydrogen.h": (11868, "1b2c64d108078722dd546f4e8b9bddca2cbe6abdf4b63e44e76fe0e9d58f4e52"),
    "hyrectools.c": (8529, "868a4f5104e90c18b84948843cb2090b22732e54d88b5f658323a38394275ce4"),
    "hyrectools.h": (1341, "00e71fdbaef4831f41822e00750a24e03c9954175b6a9680c67fb0ffc1be5715"),
    "energy_injection.h": (1175, "e2f0603b2bfe730814bdd57d46eff9f53d8bb1e10315524b395aa4dde97de2ea"),
}


def checked_bytes(name: str, data: bytes) -> dict:
    size, expected = FILES[name]
    actual = hashlib.sha256(data).hexdigest()
    if len(data) != size or actual != expected:
        raise ValueError(f"identity mismatch for {name}: bytes={len(data)}, sha256={actual}")
    return {"path": name, "bytes": len(data), "sha256": actual}


def check_metadata(source_lock: Path, build_evidence: Path) -> dict:
    """Fail closed if packet provenance contradicts the literal exact-source lock."""
    lock = json.loads(source_lock.read_text())
    candidates = [s for s in lock["sources"] if s.get("id") == "HYREC2_CODE"]
    if len(candidates) != 1 or candidates[0].get("commit") != COMMIT:
        raise ValueError("SOURCE_LOCK HYREC2_CODE commit mismatch")
    for row in candidates[0]["files"]:
        if row["path"] in FILES:
            size, sha = FILES[row["path"]]
            if row["bytes"] != size or row["sha256"] != sha:
                raise ValueError(f"SOURCE_LOCK file mismatch: {row['path']}")
    covered = {r["path"] for r in candidates[0]["files"]}
    if not {"hydrogen.c", "hydrogen.h"}.issubset(covered):
        raise ValueError("SOURCE_LOCK must cover hydrogen.c and hydrogen.h")
    evidence = json.loads(build_evidence.read_text())
    observed = {r["path"]: (r["bytes"], r["sha256"]) for r in evidence["upstream_files"]}
    if any(observed.get(name) != pair for name, pair in FILES.items()):
        raise ValueError("UPSTREAM_C_BUILD upstream_files identity mismatch")
    return {"source_lock": str(source_lock), "build_evidence": str(build_evidence),
            "status": "MATCHED_EXACT_SOURCE_IDENTITIES"}


def main() -> int:
    here = Path(__file__).resolve().parent
    packet = here.parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cache", type=Path,
                        default=Path(tempfile.gettempdir()) / "rec-bianchi-hyrec2-09e8243")
    parser.add_argument("--output", type=Path, help="binary path; default CACHE/hyrec_tla_probe")
    parser.add_argument("--cc", default="cc", help="compiler executable, not a shell command")
    parser.add_argument("--source-lock", type=Path, default=packet / "theory_reference/SOURCE_LOCK.json")
    parser.add_argument("--build-evidence", type=Path, default=packet / "evidence/UPSTREAM_C_BUILD.json")
    parser.add_argument("--driver", type=Path, default=here / "upstream_tla_driver.c")
    parser.add_argument("--report", type=Path, help="optional JSON report (not written in dry-run)")
    parser.add_argument("--offline", action="store_true", help="never fetch; require every cache file")
    parser.add_argument("--dry-run", action="store_true", help="print plan; no downloads/builds/writes")
    args = parser.parse_args()
    cache = args.cache.resolve()
    binary = (args.output or (cache / "hyrec_tla_probe")).resolve()
    driver = args.driver.resolve()
    report = {"schema_version": "1.0", "commit": COMMIT,
              "mode": "DRY_RUN" if args.dry_run else ("OFFLINE_BUILD" if args.offline else "FETCH_OR_CACHE_BUILD"),
              "upstream_sources_vendored": False, "cache": str(cache), "binary": str(binary)}
    try:
        report["metadata_check"] = check_metadata(args.source_lock, args.build_evidence)
        if not driver.is_file():
            raise ValueError(f"driver missing: {driver}")
        protected = {driver, args.source_lock.resolve(), args.build_evidence.resolve()}
        protected.update(cache / name for name in FILES)
        if binary in protected:
            raise ValueError("output binary must not overwrite source or provenance files")
        command = [args.cc, "-O2", "-std=gnu11", "-ffunction-sections", "-fdata-sections",
                   "-I" + str(cache), str(cache / "hydrogen.c"), str(cache / "hyrectools.c"),
                   str(driver), "-Wl,--gc-sections", "-lm", "-o", str(binary)]
        report["command"] = command
        if args.dry_run:
            report["planned_sources"] = [
                {"path": n, "url": BASE + n, "bytes": p[0], "sha256": p[1]}
                for n, p in FILES.items()]
            report["status"] = "PLAN_ONLY_NO_EXECUTION"
        else:
            cache.mkdir(parents=True, exist_ok=True)
            records = []
            for name in FILES:
                target = cache / name
                if target.exists():
                    row = checked_bytes(name, target.read_bytes())
                    row["acquisition"] = "EXISTING_CACHE_VALIDATED"
                else:
                    if args.offline:
                        raise ValueError(f"offline cache missing {name}")
                    request = urllib.request.Request(BASE + name,
                        headers={"User-Agent": "rec-bianchi-pinned-reference-replay/1.0"})
                    with urllib.request.urlopen(request, timeout=30) as response:
                        data = response.read(2 * 1024 * 1024 + 1)
                    row = checked_bytes(name, data)
                    with tempfile.NamedTemporaryFile(dir=cache, prefix=name + ".", delete=False) as tmp:
                        tmp.write(data)
                        temporary = Path(tmp.name)
                    try:
                        # Atomic no-clobber publication of verified bytes.
                        try:
                            os.link(temporary, target)
                        except FileExistsError:
                            checked_bytes(name, target.read_bytes())
                    finally:
                        if temporary.exists():
                            temporary.unlink()
                    row["acquisition"] = "DOWNLOADED_AND_HASH_VERIFIED"
                records.append(row)
            report["upstream_files"] = records
            binary.parent.mkdir(parents=True, exist_ok=True)
            result = subprocess.run(command, capture_output=True, text=True, timeout=60, check=False)
            report.update(exit_code=result.returncode, stdout=result.stdout, stderr=result.stderr)
            if result.returncode:
                raise RuntimeError(f"C build failed, exit {result.returncode}")
            report["binary_sha256"] = hashlib.sha256(binary.read_bytes()).hexdigest()
            report["driver_sha256"] = hashlib.sha256(driver.read_bytes()).hexdigest()
            report["status"] = "SOURCE_IDENTITY_AND_LOCAL_BUILD_VERIFIED"
            report["parity_or_scientific_admission"] = "NOT_PERFORMED_BY_THIS_SCRIPT"
        code = 0
    except (OSError, ValueError, KeyError, RuntimeError, subprocess.SubprocessError) as error:
        report.update(status="ERROR", error_type=type(error).__name__, error=str(error))
        code = 1
    rendered = json.dumps(report, indent=2) + "\n"
    if args.report is not None and not args.dry_run:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(rendered)
    sys.stdout.write(rendered)
    return code


if __name__ == "__main__":
    raise SystemExit(main())
