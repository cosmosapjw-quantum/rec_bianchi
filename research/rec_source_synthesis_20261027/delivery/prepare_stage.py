#!/usr/bin/env python3
"""Prepare one parent-authored checkpoint; never commit, publish, or infer ACKs."""
import argparse
import fnmatch
import hashlib
import json
from pathlib import Path
import re
import sys
import time
import zipfile

OWNED = 'research/rec_source_synthesis_20261027'
HISTORY = 'research/rec_history_geometry_response_20261026'
EXCLUDED_SUFFIXES = {'.zip', '.pdf', '.png', '.jpg', '.jpeg', '.npz', '.npy', '.pyc', '.gz', '.tar', '.xz', '.sqlite', '.db'}
RAW_EXTERNAL_NAMES = {'lamda_hd_live.dat'}
ARTIFACT_SUFFIXES = {'.png', '.pdf', '.jpg', '.jpeg'}
RUNTIME_CACHE_PARTS = {'__pycache__', 'mplconfig', 'mpl_config', '.mplconfig', '.mpl_config', 'fontcache', 'font_cache', '.fontcache'}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def encode_json(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode('utf-8')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('stage', help='R1 through R10 or C1 through C10')
    parser.add_argument('paths', nargs='+', help='explicit repository-relative owned files/directories')
    parser.add_argument('--source-head', required=True, help='parent-maintained expected remote commit SHA')
    parser.add_argument('--git-exclude', action='append', default=[], metavar='GLOB', help='omit matching repository-relative files only from Git entries; ZIP and exact-byte manifest remain complete')
    parser.add_argument('--include-artifacts', action='store_true', help='include saved PNG/PDF/images and large UTF8 results in ZIP+manifest; keep Git entries limited to transferable text')
    parser.add_argument('--repo', type=Path, default=Path(__file__).resolve().parents[3])
    parser.add_argument('--workspace', type=Path, default=Path('/workspace/scratch/6104ad84b826'))
    args = parser.parse_args()
    start_wall, start_cpu = time.perf_counter(), time.process_time()
    if not re.fullmatch(r'[RC](?:[1-9]|10)', args.stage):
        parser.error('stage must be R1-R10 or C1-C10')
    if not re.fullmatch(r'[0-9a-f]{40}', args.source_head):
        parser.error('--source-head requires exact 40-character SHA')
    repo = args.repo.resolve()
    stage_path = repo / OWNED / 'stages' / (args.stage + '.json')
    stage_record = json.loads(stage_path.read_text(encoding='utf-8'))
    if not isinstance(stage_record, dict) or not stage_record:
        parser.error('parent-authored stage record must be a nonempty JSON object')
    selected = {stage_path}
    for requested in args.paths:
        p = Path(requested)
        if p.is_absolute() or '..' in p.parts:
            parser.error('paths must be relative without parent traversal')
        p = repo / p
        if not p.exists():
            parser.error('missing requested path: ' + requested)
        selected.update(p.rglob('*') if p.is_dir() else [p])
    entries, manifests, omitted = [], [], []
    snapshot_bytes, artifact_git_exclusions, binary_artifacts = {}, [], []
    for p in sorted(selected):
        if not p.is_file():
            continue
        rel = p.relative_to(repo).as_posix()
        if not (rel.startswith(OWNED + '/') or rel.startswith(HISTORY + '/')):
            parser.error('file outside owned paths: ' + rel)
        is_runtime_cache = bool(RUNTIME_CACHE_PARTS.intersection(p.parts)) or p.suffix.lower() == '.pyc' or p.name.startswith('fontlist-v')
        artifact_allowed = args.include_artifacts and p.suffix.lower() in ARTIFACT_SUFFIXES
        if is_runtime_cache or (p.suffix.lower() in EXCLUDED_SUFFIXES and not artifact_allowed) or p.name in RAW_EXTERNAL_NAMES:
            omitted.append({'path': rel, 'reason': 'runtime cache excluded' if is_runtime_cache and args.include_artifacts else 'binary/archive/raw external input excluded'})
            continue
        data = p.read_bytes()
        oversized = len(data) > 2 * 1024 * 1024
        if oversized and not args.include_artifacts:
            omitted.append({'path': rel, 'reason': 'file over 2 MiB excluded'})
            continue
        try:
            content = data.decode('utf-8')
        except UnicodeDecodeError:
            content = None
        binary_reason = 'non-UTF8 binary excluded' if content is None else ('binary NUL excluded' if '\x00' in content else None)
        if binary_reason and not artifact_allowed:
            omitted.append({'path': rel, 'reason': binary_reason})
            continue
        snapshot_bytes[rel] = data
        identity = {'path': rel, 'bytes': len(data), 'sha256': digest(data)}
        manifests.append(identity)
        if artifact_allowed:
            artifact_git_exclusions.append({'path': rel, 'reason': 'saved binary artifact is ZIP-only; publish separately through Git blob API', 'matching_globs': [pattern for pattern in args.git_exclude if fnmatch.fnmatchcase(rel, pattern)]})
            binary_artifacts.append({**identity, 'local_path': str(p.resolve()), 'mode': '100644', 'type': 'blob'})
        elif oversized:
            artifact_git_exclusions.append({'path': rel, 'reason': 'UTF8 result over 2 MiB retained in ZIP; excluded from transferable Git text entries', 'matching_globs': [pattern for pattern in args.git_exclude if fnmatch.fnmatchcase(rel, pattern)]})
        else:
            entries.append({'path': rel, 'mode': '100644', 'type': 'blob', 'content': content})
    if not entries:
        parser.error('empty file table is not a checkpoint')
    snapshot_entries = entries
    git_exclusions = [{'path': entry['path'], 'matching_globs': [pattern for pattern in args.git_exclude if fnmatch.fnmatchcase(entry['path'], pattern)]} for entry in snapshot_entries if any(fnmatch.fnmatchcase(entry['path'], pattern) for pattern in args.git_exclude)]
    git_exclusions.extend(artifact_git_exclusions)
    excluded_paths = {row['path'] for row in git_exclusions}
    entries = [entry for entry in snapshot_entries if entry['path'] not in excluded_paths]
    if not entries:
        parser.error('empty Git file table is not a checkpoint')
    manifest = {
        'schema': 'REC_SYNTHESIS_IMMUTABLE_STAGE_SNAPSHOT_V1',
        'stage': args.stage,
        'expected_source_head': args.source_head,
        'stage_record_path': stage_path.relative_to(repo).as_posix(),
        'stage_record_sha256': digest(stage_path.read_bytes()),
        'file_count': len(snapshot_bytes),
        'git_file_count': len(entries),
        'git_exclusions': git_exclusions,
        'git_exclusion_globs': args.git_exclude,
        'files': manifests,
        'omitted': omitted,
        'provider_status': 'PREPARED_ONLY_NO_ACK_INFERRED',
        'receipt_rule': 'Root appends actual provider ACKs to a separate file after publication; a later checkpoint includes that file. This archive is never repacked to include its own ACK.',
    }
    if args.include_artifacts:
        manifest['include_artifacts'] = True
        manifest['binary_artifacts'] = binary_artifacts
    outdir = args.workspace / 'publication_payload'
    zipdir = args.workspace / 'deliverables'
    outdir.mkdir(parents=True, exist_ok=True)
    zipdir.mkdir(parents=True, exist_ok=True)
    payload = outdir / (args.stage + '.json')
    payload.write_bytes(encode_json(entries))
    manifest_path = outdir / (args.stage + '.manifest.json')
    manifest_path.write_bytes(encode_json(manifest))
    binary_manifest_path = None
    if args.include_artifacts:
        binary_manifest_path = outdir / (args.stage + '.binary-manifest.json')
        binary_manifest_path.write_bytes(encode_json({'schema': 'REC_SYNTHESIS_BINARY_ARTIFACT_MANIFEST_V1', 'stage': args.stage, 'files': binary_artifacts, 'publication_status': 'PREPARED_LOCAL_PATHS_ONLY_NO_BLOB_ACK_INFERRED'}))
    archive = zipdir / ('REC_SYNTHESIS_20261027_' + args.stage + '.zip')
    with zipfile.ZipFile(archive, 'w', compression=zipfile.ZIP_DEFLATED) as z:
        for relative_path, data in snapshot_bytes.items():
            info = zipfile.ZipInfo(relative_path, date_time=(2026, 10, 27, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            z.writestr(info, data)
        info = zipfile.ZipInfo('SNAPSHOT_MANIFEST.json', date_time=(2026, 10, 27, 0, 0, 0))
        info.compress_type = zipfile.ZIP_DEFLATED
        z.writestr(info, encode_json(manifest))
    with zipfile.ZipFile(archive) as z:
        bad = z.testzip()
        if bad:
            raise ValueError('ZIP CRC failed: ' + bad)
        for record in manifests:
            if digest(z.read(record['path'])) != record['sha256']:
                raise ValueError('snapshot SHA mismatch: ' + record['path'])
    report = {
        'stage': args.stage, 'payload': str(payload), 'manifest': str(manifest_path),
        'archive': str(archive), 'archive_bytes': archive.stat().st_size,
        'archive_sha256': digest(archive.read_bytes()), 'files': len(snapshot_bytes), 'git_files': len(entries), 'git_exclusions': git_exclusions,
        'omitted_count': len(omitted), 'zip_crc_and_manifest_sha': 'PASS',
        'expected_source_head': args.source_head,
        'packaging_cpu_s': time.process_time() - start_cpu,
        'packaging_wall_s': time.perf_counter() - start_wall,
        'science_execution': 'NONE', 'provider_ack': 'PENDING_ROOT_PUBLICATION'
    }
    if args.include_artifacts:
        report['binary_manifest'] = str(binary_manifest_path)
        report['binary_artifact_count'] = len(binary_artifacts)
    receipt_path = outdir / (args.stage + '.prepared.json')
    receipt_path.write_bytes(encode_json(report))
    print(json.dumps(report, ensure_ascii=False))


if __name__ == '__main__':
    main()
