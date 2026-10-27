#!/usr/bin/env python3
"""Prepare only the current C10 closeout companion after explicit ROOTREADY."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import resource
import time
import zipfile

UNIT = Path('research/rec_h5_native_producer_20261027')
FINAL_FILES = [
    'FINAL_REPORT_KO.md', 'HANDOFF_KO.md', 'README.md', 'BUDGET_LEDGER.json',
    'delivery/FINAL_DELIVERY.json', 'delivery/PUBLICATION_INDEX.json',
    'delivery/SOURCE_BACKUP_RECEIPT.json', 'delivery/CENTRAL_PUBLICATION.json',
    'delivery/FINAL_SHARED_STATE.json', 'delivery/CI_OBSERVATION.json',
    'delivery/PR_PUBLICATION.json',
]
HELPER = 'delivery/assembly/prepare_companion.py'
ARCHIVE = 'REC_H5_NATIVE_REFERENCE01_COMPANION_20261028.zip'
OUTPUTS = [ARCHIVE, 'GIT_COMPANION_ENTRIES.json', 'COMPANION_MANIFEST.json',
           'PREPARED_COMPANION_RECEIPT.json']


def sha(data):
    return hashlib.sha256(data).hexdigest()


def encoded(value):
    return (json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False)+'\n').encode('utf-8')


def write_new(path, data):
    with path.open('xb') as stream:
        stream.write(data)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--repo', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--root-ready', action='store_true', required=True,
                    help='root confirms final metadata are ready; no scientific admission inferred')
    ap.add_argument('--prior-packaging-cpu', type=float, required=True)
    ap.add_argument('--file', action='append', default=[],
                    help='additional explicit small UTF8 owned closeout file; never replaces required files')
    args = ap.parse_args()
    cpu0, wall0 = time.process_time(), time.perf_counter()
    prior = args.prior_packaging_cpu
    if not math.isfinite(prior) or not 0 <= prior < 60:
        ap.error('prior cumulative packaging CPU must be finite in[0,60); no reset')
    remaining = 60-prior
    resource.setrlimit(resource.RLIMIT_CPU, (max(1, math.ceil(remaining)),)*2)
    repo, out = args.repo.resolve(), args.out.resolve()
    unit = repo/UNIT
    if out.is_relative_to(repo):
        ap.error('companion output must be outside repository')
    if any((out/name).exists() for name in OUTPUTS):
        ap.error('unique companion output already exists; preserve it and do not overwrite/repack')
    receipt_dir = unit/'delivery/stage_receipts'
    expected = {f'{track}{i}.json' for track in ('R','C') for i in range(1,11)}
    observed = {p.name for p in receipt_dir.iterdir() if p.is_file()}
    if observed != expected:
        ap.error('all exact20 stage receipts required; no invented stage or normalized rewrite')
    names = FINAL_FILES+[HELPER]+['delivery/stage_receipts/'+name for name in sorted(expected)]
    for rel in args.file:
        p = Path(rel)
        if p.is_absolute() or '..' in p.parts or any(k in p.parts for k in ('survey','results','figures','recovered','patch_tree')):
            ap.error('extra file must be an explicit owned closeout file, without raw/large scientific payloads')
        names.append(p.as_posix())
    names = list(dict.fromkeys(names))
    snapshot, manifests, entries = {}, [], []
    for name in names:
        p = unit/name
        if p.is_symlink() or not p.resolve().is_relative_to(unit) or not p.is_file():
            raise ValueError('missing or unsupported explicit closeout file: '+name)
        data = p.read_bytes()
        if len(data)>2*1024*1024 or b'\0' in data:
            raise ValueError('closeout file must be small UTF8: '+name)
        text = data.decode('utf-8')
        rel = (UNIT/name).as_posix()
        snapshot[rel] = data
        manifests.append({'path':rel,'bytes':len(data),'sha256':sha(data),
                          'git_blob_sha1':hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()})
        entries.append({'path':rel,'mode':'100644','type':'blob','content':text})
    manifest = {
        'schema':'REC_H5_NATIVE_REFERENCE01_FINAL_COMPANION_V1',
        'purpose':'Current C10 metadata closure only; no new research or stage execution',
        'selected_source_files':len(manifests),'stage_receipt_files':20,'files':manifests,
        'source_ZIP':'Already frozen; never read, changed, rebuilt or embedded by this helper',
        'original_stage_receipts':'Byte-preserved; normalization belongs only in root publication index',
        'receipt_rule':'This companion is immutable before its own later provider ACK. Actual ACK belongs in a separate external final receipt.',
        'compression':'DEFLATE level1','science_runs':0,'stage_replays':0,
        'provider_ack':'NOT_IN_FROZEN_COMPANION',
    }
    out.mkdir(parents=True, exist_ok=True)
    archive = out/ARCHIVE
    with zipfile.ZipFile(archive, 'x', compression=zipfile.ZIP_DEFLATED, compresslevel=1) as z:
        for name, data in snapshot.items():
            z.writestr(name, data, compress_type=zipfile.ZIP_DEFLATED, compresslevel=1)
        z.writestr('COMPANION_SNAPSHOT_MANIFEST.json', encoded(manifest), compresslevel=1)
    with zipfile.ZipFile(archive) as z:
        bad = z.testzip()
        if bad:
            raise ValueError('companion CRC failed: '+bad)
        if set(z.namelist()) != set(snapshot)|{'COMPANION_SNAPSHOT_MANIFEST.json'}:
            raise ValueError('companion member coverage mismatch')
        for record in manifests:
            got = z.read(record['path'])
            if len(got)!=record['bytes'] or sha(got)!=record['sha256']:
                raise ValueError('companion exact byte readback failed: '+record['path'])
    write_new(out/'GIT_COMPANION_ENTRIES.json', encoded(entries))
    write_new(out/'COMPANION_MANIFEST.json', encoded(manifest))
    archive_data = archive.read_bytes()
    elapsed = time.process_time()-cpu0
    report = {
        'schema':'REC_H5_NATIVE_COMPANION_PREPARATION_RECEIPT_V1',
        'archive':str(archive),'archive_bytes':len(archive_data),'archive_sha256':sha(archive_data),
        'selected_files':len(manifests),'archive_members':len(manifests)+1,
        'all20_stage_receipts':'INCLUDED_EXACT_BYTES','CRC_SHA_member_readback':'PASS',
        'packaging_CPU_s':elapsed,'packaging_wall_s':time.perf_counter()-wall0,
        'prior_packaging_CPU_s':prior,'cumulative_packaging_CPU_s':prior+elapsed,
        'cumulative_packaging_ceiling_CPU_s':60,'within_known_CPU_ceiling':prior+elapsed<=60,
        'startup_final_receipt_tool_network_LLM_CPU':'UNKNOWN_NOT_ZERO',
        'source_archive_changed':False,'scientific_runs':0,'tests':0,'stage_replays':0,
        'Git_writes':0,'provider_writes':0,'provider_ACK':'PENDING_ROOT_DELIVERY',
        'future_ACK_repack':False,
    }
    write_new(out/'PREPARED_COMPANION_RECEIPT.json', encoded(report))
    print(json.dumps(report, ensure_ascii=False))
    if not report['within_known_CPU_ceiling']:
        raise RuntimeError('companion packaging cumulative budget exceeded; preserve failure, no automatic rerun')


if __name__=='__main__':
    main()
