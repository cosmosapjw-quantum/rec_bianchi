"""Recover pinned archival bytes, rejecting unsafe entries; never execute content."""
import datetime
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import platform
import resource
import sys
import tarfile
import time


def sha(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def main():
    wall0 = time.perf_counter()
    cpu0 = time.process_time()
    cfg_path = Path(__file__).with_name("recovery_input_backup_agent.json")
    cfg = json.loads(cfg_path.read_text())
    base = Path(cfg["root"])
    manifest = {
        "schema": "rec-r3r-runtime-recovery-v1",
        "started_at_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "scope": "Restore archival bytes and inspect/extract only; no research result rerun or new scientific verdict",
        "command": [sys.executable, str(Path(__file__).resolve())],
        "script_sha256": sha(Path(__file__)),
        "input_sha256": sha(cfg_path),
        "environment": {"python": sys.version, "executable": sys.executable, "platform": platform.platform()},
        "materialize_history": cfg["materialize_history"],
        "provider_recovery": cfg["provider_recovery"],
        "policy": cfg["policy"],
        "archives": [],
    }
    for item in cfg["stages"]:
        source = Path(cfg["archive_dir"]) / item["file_name"]
        actual_size = source.stat().st_size
        actual_hash = sha(source)
        if actual_size != item["expected_bytes"] or actual_hash != item["expected_sha256"]:
            raise ValueError(f"Archive identity mismatch: stage {item['stage']}")
        xattrs = {key: os.getxattr(source, key).decode() for key in os.listxattr(source)}
        if xattrs.get("user.library-file-id") != item["library_file_id"]:
            raise ValueError("Library identity xattr mismatch")
        for attr in item["xattrs"]:
            if xattrs.get(attr["name"]) != attr["value"]:
                raise ValueError("Library version xattr mismatch")
        target = base / f"recovered_stage{item['stage']}"
        if target.exists():
            raise FileExistsError(f"Refusing to overwrite existing extraction: {target}")
        entries = []
        with tarfile.open(source, "r:gz") as archive:
            members = archive.getmembers()
            seen = set()
            for member in members:
                path = PurePosixPath(member.name)
                if (path.is_absolute() or not path.parts or ".." in path.parts
                        or "\\" in member.name or "\x00" in member.name
                        or str(path) != member.name.rstrip("/")
                        or not (member.isfile() or member.isdir())):
                    raise ValueError(f"Unsafe archive entry: {member.name!r}")
                if path in seen:
                    raise ValueError(f"Duplicate entry: {member.name!r}")
                seen.add(path)
            if sum(m.size for m in members) > 512 * 1024 * 1024:
                raise ValueError("Unexpected expanded archive size")
            target.mkdir(mode=0o700)
            for member in members:
                destination = target.joinpath(*PurePosixPath(member.name).parts)
                if member.isdir():
                    destination.mkdir(parents=True, exist_ok=True, mode=0o700)
                    entries.append({"path": member.name, "kind": "directory"})
                    continue
                destination.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
                digest = hashlib.sha256()
                count = 0
                with archive.extractfile(member) as input_stream, destination.open("xb") as output_stream:
                    while chunk := input_stream.read(1024 * 1024):
                        output_stream.write(chunk)
                        digest.update(chunk)
                        count += len(chunk)
                os.chmod(destination, 0o600)
                if count != member.size:
                    raise ValueError(f"Extracted size mismatch: {member.name}")
                if sha(destination) != digest.hexdigest():
                    raise ValueError(f"Extracted independent disk readback mismatch: {member.name}")
                entries.append({"path": member.name, "kind": "regular_file", "bytes": count,
                                "sha256": digest.hexdigest(), "original_tar_mode": oct(member.mode)})
        record = {**item, "actual_archive_path": str(source), "actual_bytes": actual_size,
                  "actual_sha256": actual_hash, "archive_full_readback": "PASS",
                  "xattrs": xattrs, "xattrs_verification": "PASS",
                  "extraction_directory": str(target), "member_count": len(entries),
                  "regular_file_count": sum(e["kind"] == "regular_file" for e in entries),
                  "expanded_file_bytes": sum(e.get("bytes", 0) for e in entries),
                  "safe_entry_validation": "PASS", "extracted_independent_disk_readback": "PASS",
                  "entries": entries}
        manifest["archives"].append(record)
        print(json.dumps({k: record[k] for k in ("stage", "actual_bytes", "actual_sha256", "member_count", "expanded_file_bytes", "extraction_directory", "safe_entry_validation")}))
    manifest.update({"status": "PASS_ARCHIVAL_RECOVERY_ONLY", "exit_code": 0,
                     "finished_at_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                     "cpu_seconds": time.process_time() - cpu0,
                     "wall_seconds": time.perf_counter() - wall0,
                     "maxrss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss})
    output = base / "R3R_STAGE123_RECOVERY_MANIFEST.json"
    output.write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps({"manifest": str(output), "sha256": sha(output), "status": manifest["status"]}))


if __name__ == "__main__":
    main()
