#!/usr/bin/env python3
"""Restore the unchanged F08 source and build a separate REC stdio receiver.

The existing REC199 source-inclusive backup is an input, not a new scenario.
No source file in the original Rust tree is modified.  The copied bridge
module has the exact original paired_runtime bytes; only its public module
surface is supplied by the separate executable.
"""
from __future__ import annotations
import argparse
import hashlib
import io
import json
from pathlib import Path
import shutil
import subprocess
import zipfile

BASE = Path(__file__).resolve().parent
ARCHIVE_SHA = "ba557fd45fe643f42c5dffc793b237e311c1db1260b4f1d3c9b4068e7f91f93f"
INNER_SHA = "dc48688e734838a0933fabe97025d7c354ccd972a03ecb8ca6e33be5460e0673"
PAIR_RS_SHA = "b6c1d2a07ab51ff02318139ae18387b77f61859c08037347f788524df770ebe7"
PAIR_INPUT_SHA = "0a2bec874a5aa1b12f882033a08497b913b44447148b50b6082093bb354868e8"
GROUPS = (
    ("S0", "bass_rei_f08_s0_source_photon_thomson_20261101/source_inputs", "ORIGIN_SHA256SUMS.txt", 12),
    ("Rust", "bass_rei_f08_native_hhe_firststage_20261101/original_rei_rust", "original_source_sha256.txt", 51),
    ("photon", "bass_rei_f08_s0_remap_support_20261101/source_inputs", "LOCKED_CHECKPOINT_SHA256SUMS.txt", 4),
)

def sha(value):
    return hashlib.sha256(value if isinstance(value, bytes) else Path(value).read_bytes()).hexdigest()

def require(ok, reason):
    if not ok:
        raise ValueError(reason)

def prepare(archive: Path, work: Path):
    require(not work.exists(), "new work directory required; preserve prior runs")
    require(sha(archive) == ARCHIVE_SHA, "original REC199 source-full backup SHA")
    with zipfile.ZipFile(archive) as rec:
        recovery = rec.read("upstream/ORIGINAL_BASS_F08_S0_RECOVERY_20261103.zip")
    with zipfile.ZipFile(io.BytesIO(recovery)) as middle:
        inner = middle.read("payload/BASS_REI_F08_S0_CONTINUOUS_NATIVE_HHE_20261102.zip")
    require(sha(inner) == INNER_SHA, "original 106-member BASS source SHA")
    with zipfile.ZipFile(io.BytesIO(inner)) as z:
        require(len(z.namelist()) == 106 and z.testzip() is None, "original source archive members/CRC")
        work.mkdir(parents=True)
        original = work / "original_bass"
        z.extractall(original)
    identities = {}
    counts = {}
    for label, relative, manifest, count in GROUPS:
        root = original / "research" / relative
        lines = (root / manifest).read_text().splitlines()
        require(len(lines) == count, "original source manifest count: " + label)
        for line in lines:
            digest, name = line.split(maxsplit=1)
            require(sha(root / name) == digest, "source byte lock: " + name)
            identities[str((root / name).relative_to(original))] = digest
        counts[label] = count
    owner = original / "research/bass_rei_f08_native_hhe_firststage_20261101/original_rei_rust"
    paired = owner / "src/paired_runtime.rs"
    require(sha(paired) == PAIR_RS_SHA, "live original owner paired_runtime source identity")
    bridge = work / "bridge"
    (bridge / "src").mkdir(parents=True)
    shutil.copyfile(paired, bridge / "src/paired_runtime.rs")
    shutil.copyfile(BASE / "paired_bridge.rs", bridge / "src/main.rs")
    relative_owner = "../original_bass/research/bass_rei_f08_native_hhe_firststage_20261101/original_rei_rust"
    (bridge / "Cargo.toml").write_text(
        '[package]\nname = "rec_f08_polarized_bridge"\nversion = "0.1.0"\nedition = "2021"\npublish = false\n'
        '[dependencies]\nrei_microphysics = { path = "' + relative_owner + '" }\n[workspace]\n'
    )
    commands = [["cargo", "generate-lockfile", "--offline"],
                ["cargo", "build", "--release", "--locked", "--offline"]]
    logs = []
    for command in commands:
        p = subprocess.run(command, cwd=bridge, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        logs.append("$ " + " ".join(command) + "\n" + p.stdout)
        (work / "BUILD.log").write_text("\n".join(logs))
        require(p.returncode == 0, "bridge build failed; see BUILD.log")
    binary = bridge / "target/release/rec_f08_polarized_bridge"
    # Verify the owner files again after compilation.  This is not a replay.
    for name, digest in identities.items():
        require(sha(original / name) == digest, "build altered original source: " + name)
    receipt = {
        "schema": "REC_F08_POLARIZED_RECEIVER_BUILD_V1",
        "REC199_source_archive_sha256": ARCHIVE_SHA,
        "BASS_original_106_member_source_sha256": INNER_SHA,
        "source_locks": counts,
        "original_source_files": identities,
        "paired_runtime_sha256": PAIR_RS_SHA,
        "original_F08_pair_input_sha256": PAIR_INPUT_SHA,
        "original_source_modified": False,
        "bridge_source_sha256": sha(BASE / "paired_bridge.rs"),
        "binary_sha256": sha(binary), "binary": str(binary),
        "rustc": subprocess.check_output(["rustc", "--version"], text=True).strip(),
        "commands": commands,
        "historical_640_stage_replay": "REUSED_EXISTING_EVIDENCE_NOT_RERUN",
        "new_receiver_execution": "NOT_RUN", "production": "HOLD",
    }
    (work / "BUILD_RECEIPT.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps({"status": "BUILT_ORIGINAL_SOURCE_LOCKS_VERIFIED", "binary": str(binary), "locks": counts}))
    return receipt

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--archive", type=Path, required=True)
    p.add_argument("--work", type=Path, required=True)
    a = p.parse_args()
    prepare(a.archive, a.work)
