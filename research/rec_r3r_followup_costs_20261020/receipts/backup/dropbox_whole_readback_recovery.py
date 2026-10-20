"""One GET per connector-issued Dropbox link; preserve bytes and safe receipts."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import platform
import resource
import sys
import time
import urllib.request


def main():
    cfg = json.load(sys.stdin)
    stage = cfg["stage"]
    link = cfg["link"]
    root = Path(cfg["destination_directory"])
    root.mkdir(parents=True, exist_ok=True)
    destination = root / link["name"]
    temporary = root / (link["name"] + ".partial")
    if destination.exists() or temporary.exists():
        raise FileExistsError("Refusing to overwrite readback destination")
    started = datetime.datetime.now(datetime.timezone.utc).isoformat()
    wall0 = time.perf_counter()
    cpu0 = time.process_time()
    source_meta = {k: v for k, v in link.items() if k != "download_url"}
    rec = {
        "schema": "rec-r3r-dropbox-recovery-whole-readback-v1",
        "stage": stage,
        "started_at_utc": started,
        "provider": "Dropbox",
        "metadata": source_meta,
        "expected_archive_bytes": cfg["expected_bytes"],
        "expected_archive_sha256": cfg["expected_sha256"],
        "download_method": "Single GET of current connector-issued temporary download link; no HEAD, preview, or range preflight",
        "download_link_record": "Sensitive single-use URL deliberately not retained",
        "command": [sys.executable, str(Path(__file__).resolve()), "<complete transfer plus pinned expectations on stdin; URL not retained>"],
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "environment": {"python": sys.version, "platform": platform.platform(), "executable": sys.executable},
        "output_path": str(destination),
        "scope": "New archival readback only; no upload and no scientific execution",
    }
    code = 1
    try:
        count = 0
        streamed = hashlib.sha256()
        with urllib.request.urlopen(link["download_url"], timeout=25) as response:
            rec["http_status"] = response.status
            with temporary.open("xb") as output:
                while chunk := response.read(1024 * 1024):
                    output.write(chunk)
                    streamed.update(chunk)
                    count += len(chunk)
                    if count > cfg["expected_bytes"]:
                        raise ValueError("Readback larger than pinned archive size")
        with temporary.open("rb") as stream:
            disk_hash = hashlib.file_digest(stream, "sha256").hexdigest()
        block_hashes = hashlib.sha256()
        with temporary.open("rb") as stream:
            while block := stream.read(4 * 1024 * 1024):
                block_hashes.update(hashlib.sha256(block).digest())
        rec.update({"bytes": count, "sha256": disk_hash, "streamed_sha256": streamed.hexdigest(),
                    "dropbox_content_hash_computed": block_hashes.hexdigest()})
        if count != cfg["expected_bytes"] or count != link["size"]:
            raise ValueError("Readback size mismatch")
        if disk_hash != cfg["expected_sha256"] or disk_hash != streamed.hexdigest():
            raise ValueError("Readback SHA256 mismatch")
        if block_hashes.hexdigest() != link["content_hash"]:
            raise ValueError("Dropbox block content hash mismatch")
        os.rename(temporary, destination)
        rec.update({"whole_readback": "PASS", "content_hash_check": "PASS", "status": "PASS_CURRENT_WHOLE_REMOTE_READBACK", "exit_code": 0})
        code = 0
    except Exception as error:
        rec.update({"whole_readback": "FAIL", "status": "FAIL_CURRENT_READBACK", "exit_code": 1,
                    "error_type": type(error).__name__, "error_detail": "Message omitted to avoid retaining sensitive temporary URL"})
    rec.update({"finished_at_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                "wall_seconds": time.perf_counter() - wall0,
                "cpu_seconds": time.process_time() - cpu0,
                "maxrss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss})
    receipt = root / f"STAGE{stage}_DROPBOX_CURRENT_READBACK.json"
    receipt.write_text(json.dumps(rec, indent=2) + "\n")
    print(json.dumps({"stage": stage, "status": rec["status"], "receipt": str(receipt),
                      "bytes": rec.get("bytes"), "sha256": rec.get("sha256"), "exit_code": code}))
    raise SystemExit(code)


if __name__ == "__main__":
    main()
