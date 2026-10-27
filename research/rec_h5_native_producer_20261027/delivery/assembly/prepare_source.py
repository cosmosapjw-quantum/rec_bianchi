#!/usr/bin/env python3
"""Package frozen bytes after root C9 release. No imports of scientific code."""
import argparse
import base64
import hashlib
import json
import math
from pathlib import Path
import re
import resource
import time
import zipfile

UNIT = Path('research/rec_h5_native_producer_20261027')
LOCKS = {
    'research/program_expansion_20261025/h5_input_binding/inputs/SOURCE_CONTEXT.json': '5ccd8955bc9ea7484ddc1fca1dcf8b5a0a789e07c36ce0af3e692b959f002fe8',
    'research/rec_history_geometry_response_20261026/inputs/target_native_snapshot.csv': '3a95862b9cd4f924d63020f39fc537b371133af6160e88c3409d8c69fc0c34b7',
    'research/rec_history_geometry_response_20261026/inputs/history.npz': 'd4f82542e13fed4ff0bb60b17865d8b9de5e090a2366108169c3da7a21fcb4b1',
    'research/rec_history_thermo_20261024/vendor/hydrogen.h': 'e89a3a447928cbe31dc273c11c4a8bc7f7a8e297be4a11270e453c101f96ccba',
    'research/rec_history_thermo_20261024/vendor/original_hyrec_native.py': 'd7bc38346281951fdd5f2677e25f3b558333124a2319786b9b7afb0ab1f7a89c',
}
CACHE_PARTS = {'__pycache__', '.mplconfig', 'mplconfig', 'mpl_config', 'fontcache', 'font_cache'}
FIGURES = {'.png', '.pdf', '.svg', '.jpg', '.jpeg'}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def encoded(value):
    return (json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n').encode()


def private_or_raw(relative):
    low = relative.lower()
    # Remote surveys contain account backup inventories and are archive-only.
    return '/survey/remote/' in low or 'lamda' in low and low.endswith('.dat') or any(
        token in low for token in ('account_metadata', 'private_backup', 'credential', 'token_cache'))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--repo', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True, help='new directory outside repository')
    ap.add_argument('--science-commit', required=True)
    ap.add_argument('--decision', type=Path, required=True)
    ap.add_argument('--decision-sha256', required=True)
    ap.add_argument('--release-after-c9', action='store_true', required=True,
                    help='root attests C9 admission; helper never decides scientific admission')
    ap.add_argument('--prior-packaging-cpu', type=float, required=True)
    args = ap.parse_args()
    cpu0, wall0 = time.process_time(), time.perf_counter()
    if not re.fullmatch('[0-9a-f]{40}', args.science_commit):
        ap.error('science commit must be actual 40-character ACKed SHA')
    if not math.isfinite(args.prior_packaging_cpu) or not 0 <= args.prior_packaging_cpu < 60:
        ap.error('preserve cumulative prior packaging CPU; available total must be below60')
    # Absolute process CPU includes interpreter startup; prior debit is never reset.
    resource.setrlimit(resource.RLIMIT_CPU, (max(1, math.ceil(60-args.prior_packaging_cpu)),)*2)
    repo, out = args.repo.resolve(), args.out.resolve()
    if out.is_relative_to(repo):
        ap.error('output must be outside repository to prevent recursive archive inclusion')
    decision = args.decision.resolve()
    if not decision.is_relative_to(repo/UNIT):
        ap.error('root C9 decision must be an existing owned unit file')
    decision_bytes = decision.read_bytes()
    if sha(decision_bytes) != args.decision_sha256 or not json.loads(decision_bytes):
        ap.error('root-supplied decision bytes mismatch or empty document')
    selected = {p for p in (repo/UNIT).rglob('*') if p.is_file()}
    selected.update(repo/p for p in LOCKS)
    vendor = repo/'research/rec_history_thermo_20261024/vendor'
    selected.update(p for p in vendor.iterdir() if p.is_file() and p.suffix in {'.py','.c','.h'})
    snapshot, rows, omissions, text_entries, binaries, excluded = {}, [], [], [], [], []
    for p in sorted(selected):
        rel = p.relative_to(repo).as_posix()
        if p.is_symlink():
            raise ValueError('selected source symlink requires explicit owner resolution: '+rel)
        if CACHE_PARTS.intersection(p.parts) or p.suffix == '.pyc' or p.name.startswith('fontlist-v'):
            omissions.append({'path':rel,'reason':'runtime cache'})
            continue
        data = p.read_bytes()
        digest = sha(data)
        if rel in LOCKS and digest != LOCKS[rel]:
            raise ValueError('immutable input mismatch: '+rel)
        snapshot[rel] = data
        record = {'path':rel,'bytes':len(data),'sha256':digest,
                  'git_blob_sha1':hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()}
        rows.append(record)
        if not rel.startswith(UNIT.as_posix()+'/'):
            excluded.append({**record,'reason':'unchanged original dependency; archive only'})
            continue
        if private_or_raw(rel):
            excluded.append({**record,'reason':'private survey/account metadata or rawLAMDA; archive only'})
            continue
        if p.suffix.lower() in FIGURES:
            binaries.append({**record,'mode':'100644','type':'blob','encoding':'base64',
                             'content':base64.b64encode(data).decode('ascii')})
            continue
        try:
            text = data.decode('utf-8')
        except UnicodeDecodeError:
            text = None
        if text is None or '\x00' in text or len(data)>2*1024*1024 or p.suffix.lower() in {'.zip','.npz','.npy','.gz','.xz','.tar'}:
            excluded.append({**record,'reason':'binary/archive or large text; archive only'})
        else:
            text_entries.append({'path':rel,'mode':'100644','type':'blob','content':text})
    if set(LOCKS)-set(snapshot):
        raise ValueError('locked source dependency absent')
    manifest = {'schema':'REC_H5_NATIVE_FINAL_SOURCE_SNAPSHOT_V1','source_commit':args.science_commit,
                'root_decision':{'path':decision.relative_to(repo).as_posix(),'sha256':sha(decision_bytes)},
                'files':rows,'omitted_runtime_caches':omissions,
                'archive_only':excluded,'science_execution':0,
                'receipt_rule':'ZIP is frozen before upload. Its future ACK and archive hash belong only in an external companion.',
                'compression':'DEFLATE level1','own_provider_ack':'NOT_IN_SNAPSHOT'}
    out.mkdir(parents=True, exist_ok=False)
    archive=out/'REC_H5_NATIVE_REFERENCE01_SOURCE_20261027.zip'
    with zipfile.ZipFile(archive,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=1) as z:
        for name,data in snapshot.items():
            z.writestr(name,data,compress_type=zipfile.ZIP_DEFLATED,compresslevel=1)
        z.writestr('SOURCE_SNAPSHOT_MANIFEST.json',encoded(manifest),compresslevel=1)
    with zipfile.ZipFile(archive) as z:
        bad=z.testzip()
        if bad: raise ValueError('CRC failed: '+bad)
        if set(z.namelist()) != set(snapshot)|{'SOURCE_SNAPSHOT_MANIFEST.json'}:
            raise ValueError('archive member coverage mismatch')
        for row in rows:
            if sha(z.read(row['path'])) != row['sha256']:
                raise ValueError('archive byte readback mismatch: '+row['path'])
    for name,value in [('SOURCE_MANIFEST.json',manifest),('GIT_TEXT_ENTRIES.json',text_entries),
                       ('GIT_BINARY_BLOBS.json',binaries),('GIT_EXCLUSIONS.json',excluded)]:
        (out/name).write_bytes(encoded(value))
    debit=time.process_time()-cpu0
    report={'schema':'REC_H5_NATIVE_SOURCE_PREPARATION_RECEIPT_V1','archive':str(archive),
            'bytes':archive.stat().st_size,'sha256':sha(archive.read_bytes()),'files':len(rows),
            'CRC_SHA_member_readback':'PASS','source_commit':args.science_commit,
            'known_process_cpu_s':time.process_time()-cpu0,'wall_s':time.perf_counter()-wall0,
            'prior_packaging_cpu_s':args.prior_packaging_cpu,
            'packaging_cumulative_cpu_s':args.prior_packaging_cpu+time.process_time()-cpu0,
            'packaging_ceiling_cpu_s':60,'science_runs':0,
            'startup_final_receipt_network_LLM_CPU':'UNKNOWN_NOT_ZERO',
            'provider_ack':'PENDING_ROOT_PUBLICATION','final_archive_repack_for_own_ack':False}
    if args.prior_packaging_cpu+debit>60: raise RuntimeError('packaging cumulative budget exceeded')
    (out/'PREPARED_SOURCE_RECEIPT.json').write_bytes(encoded(report))
    print(json.dumps(report))


if __name__=='__main__':
    main()
