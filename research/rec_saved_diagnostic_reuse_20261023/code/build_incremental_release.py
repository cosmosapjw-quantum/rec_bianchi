"""Create and freshly extract an immutable, explicitly incremental C2 archive.

No scientific code is imported. The dependency on the already backed-up parent
is part of the archive contract; this is not advertised as a standalone repo.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path, PurePosixPath
import subprocess
import tempfile
import time
import zipfile

UNIT = Path(__file__).resolve().parents[1]
REPO = UNIT.parents[1]
PREFIX = str(UNIT.relative_to(REPO))+"/"
BASE = "40f7cf12b509377350e9a16da461e8ef97cdcb62"
PARENT_TREE = "a136dea6c4ade8c6be442843800d0eb1458caa5f"
PARENT_ARCHIVE = dict(filename="REC_COMPTON_COUPLED_20261022.zip",bytes=123401773,
    sha256="4795d75c9f3992b3433f59a6a20464accc66533d95b344fb607c42b4df0c4668")


def git(*args):
    return subprocess.check_output(["git","-C",str(REPO),*args])


def digest(data):
    return hashlib.sha256(data).hexdigest()


def json_bytes(value):
    return (json.dumps(value,indent=2,sort_keys=True,ensure_ascii=False)+"\n").encode()


def save_json(path,value):
    with path.open("xb") as stream:
        stream.write(json_bytes(value))


def main(out, branch):
    start = time.perf_counter()
    out.mkdir(parents=True,exist_ok=True)
    release = git("rev-parse",branch).decode().strip()
    tree = git("rev-parse",release+"^{tree}").decode().strip()
    if git("rev-parse",BASE+"^{tree}").decode().strip() != PARENT_TREE:
        raise ValueError("PARENT_TREE_CHANGED")
    changes = git("diff","--name-status",BASE,release).decode().splitlines()
    if not changes or any(not line.startswith("A\t"+PREFIX) for line in changes):
        raise ValueError("RELEASE_MUST_ONLY_ADD_NEW_STAGE_FILES")
    payloads, records = {}, []
    for line in git("ls-tree","-rl",release,"--",PREFIX).decode().splitlines():
        meta,path = line.split("\t")
        mode,kind,blob,size = meta.split()
        data = git("cat-file","blob",blob)
        if kind != "blob" or len(data) != int(size):
            raise ValueError("INVALID_RELEASE_ENTRY")
        payloads[path] = data
        records.append(dict(path=path,bytes=len(data),sha256=digest(data),git_blob=blob,mode=mode,role="new_stage_file"))
    bundle_name = "REC_DIAGNOSTIC_C2_LOCAL_COMMITS_20261023.bundle"
    bundle = out/bundle_name
    if bundle.exists():
        raise FileExistsError(bundle)
    bundle_command = ["git","-C",str(REPO),"bundle","create",str(bundle),branch,"^"+BASE]
    created = subprocess.run(bundle_command,capture_output=True,text=True,check=True)
    verified = subprocess.run(["git","-C",str(REPO),"bundle","verify",str(bundle)],capture_output=True,text=True,check=True)
    heads = git("bundle","list-heads",str(bundle)).decode()
    if release not in heads:
        raise ValueError("BUNDLE_RELEASE_HEAD_MISSING")
    payloads[bundle_name] = bundle.read_bytes()
    readme = f"""# C2 incremental checkpoint

This archive adds only `{PREFIX}` to the exact parent below.
It contains no new IVP and does not claim optimized-candidate equivalence.

- Parent local commit: `{BASE}`
- Parent whole tree: `{PARENT_TREE}`
- New local commit: `{release}`
- New whole tree: `{tree}`
- Required preceding archive: `{PARENT_ARCHIVE['filename']}`
- Preceding archive SHA256: `{PARENT_ARCHIVE['sha256']}`

Restore the preceding archive or a repository at the parent first, then extract
these new stage files at that repository root. The incremental Git bundle also
requires the parent commit object; `git bundle verify` checks that prerequisite.
All payload hashes and Git blob identities are in MANIFEST.json.

Read REPORT_KO.md, C2_SCOPE.md and NEXT_STAGE_C3.md in the stage directory before
running code. Existing profile outputs are create-only. Resume from C3; do not
replay completed profiles or preceding IVPs as a restoration step.

The fresh extraction audit verifies these new archive bytes and bundle structure.
It is not a fresh full-repository reconstruction or a repeat of scientific tests.
""".encode()
    payloads["ARCHIVE_README.md"] = readme
    for path in (bundle_name,"ARCHIVE_README.md"):
        records.append(dict(path=path,bytes=len(payloads[path]),sha256=digest(payloads[path]),role="incremental_bundle" if path.endswith(".bundle") else "restore_instructions"))
    manifest = dict(schema=1,kind="incremental_research_stage",created_utc=datetime.now(timezone.utc).isoformat(),
        base_local_commit=BASE,base_tree=PARENT_TREE,release_local_commit=release,release_tree=tree,
        unit=PREFIX.rstrip("/"),requires_parent_archive=PARENT_ARCHIVE,files=records,
        bundle_creation=dict(command=bundle_command,exit_code=created.returncode),
        bundle_verification=dict(exit_code=verified.returncode,stdout=verified.stdout,stderr=verified.stderr,heads=heads),
        scientific_scope="C2 saved-state mapping/profile only; candidate implementation NOT_RUN, new IVPs 0")
    payloads["MANIFEST.json"] = json_bytes(manifest)
    archive = out/"REC_DIAGNOSTIC_C2_20261023.zip"
    with zipfile.ZipFile(archive,"x",compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for name,data in sorted(payloads.items()):
            z.writestr(name,data)
    archive_sha = digest(archive.read_bytes())
    restored = Path(tempfile.mkdtemp(prefix="rec_diagnostic_c2_restore_",dir=out.parent))
    with zipfile.ZipFile(archive) as z:
        if z.testzip() is not None or set(z.namelist()) != set(payloads):
            raise ValueError("ARCHIVE_CRC_OR_INVENTORY_FAILURE")
        for name in z.namelist():
            p = PurePosixPath(name)
            if p.is_absolute() or ".." in p.parts:
                raise ValueError("UNSAFE_ARCHIVE_PATH")
            target = restored/name
            target.parent.mkdir(parents=True,exist_ok=True)
            with target.open("xb") as stream:
                stream.write(z.read(name))
    mismatches = []
    for row in records:
        data = (restored/row["path"]).read_bytes()
        if len(data) != row["bytes"] or digest(data) != row["sha256"]:
            mismatches.append(row["path"])
        if "git_blob" in row and hashlib.sha1(b"blob "+str(len(data)).encode()+b"\0"+data).hexdigest()!=row["git_blob"]:
            mismatches.append(row["path"]+":git_blob")
    if mismatches or (restored/"MANIFEST.json").read_bytes()!=payloads["MANIFEST.json"]:
        raise ValueError("FRESH_RESTORE_CONTENT_MISMATCH:"+str(mismatches))
    restored_bundle = subprocess.run(["git","-C",str(REPO),"bundle","verify",str(restored/bundle_name)],capture_output=True,text=True,check=True)
    integrity = dict(schema=1,status="BUILT_AND_INCREMENTAL_CONTENT_RESTORE_VERIFIED",archive=str(archive),
        bytes=archive.stat().st_size,sha256=archive_sha,release_local_commit=release,release_tree=tree,
        parent_local_commit=BASE,parent_tree=PARENT_TREE,requires_parent_archive=PARENT_ARCHIVE,
        stage_files=sum(r["role"]=="new_stage_file" for r in records),archive_entries=len(payloads),
        manifest_sha256=digest(payloads["MANIFEST.json"]),new_IVPs=0)
    audit = dict(schema=1,status="PASS_INCREMENTAL_CONTENT_RESTORE",scope="New stage only, requires exact previously verified parent; no full-repo or scientific replay claim.",
        archive_sha256=archive_sha,restored_root=str(restored),files_verified=len(records),
        all_payload_sizes_and_sha256=True,all_stage_git_blob_identities=True,all_zip_crc=True,
        exact_inventory=True,bundle_verified_against_existing_parent=True,
        restored_bundle_verification=dict(exit_code=restored_bundle.returncode,stdout=restored_bundle.stdout,stderr=restored_bundle.stderr),
        source_local_commit=release,source_tree=tree,old_sources_modified=False,
        new_IVPs=0,old_IVP_reruns=0,scientific_tests_run=0,wall_seconds=time.perf_counter()-start)
    save_json(out/"REC_DIAGNOSTIC_C2_20261023_INTEGRITY.json",integrity)
    save_json(out/"REC_DIAGNOSTIC_C2_RESTORE_AUDIT_20261023.json",audit)
    print(json.dumps(integrity))


if __name__ == "__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--output-dir",type=Path,required=True)
    parser.add_argument("--branch",required=True)
    args=parser.parse_args()
    main(args.output_dir.resolve(),args.branch)
