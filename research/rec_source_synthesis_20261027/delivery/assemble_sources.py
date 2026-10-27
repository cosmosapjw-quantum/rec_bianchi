#!/usr/bin/env python3
"""Mechanically assemble selected survey evidence and immutable GEO01 text payload."""
import hashlib
import json
from pathlib import Path
import shutil
import time

W = Path('/workspace/scratch/6104ad84b826')
REPO = W / 'rec_bianchi'
OWN = REPO / 'research/rec_source_synthesis_20261027'
HIST = 'research/rec_history_geometry_response_20261026/'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def main():
    cpu, wall = time.process_time(), time.perf_counter()
    assembly = []
    def copy(source, target):
        src, dst = W / source, OWN / target
        dst.parent.mkdir(parents=True, exist_ok=True)
        data = src.read_bytes()
        dst.write_bytes(data)
        assembly.append({'source': source, 'target': dst.relative_to(REPO).as_posix(), 'bytes': len(data), 'sha256': sha(data), 'operation': 'EXACT_BYTE_COPY'})

    repo_files = ['SURVEY_SUMMARY.json', 'DAG_COUNT_RECONCILIATION.json', 'SOURCE_IDENTITY_READBACK.json', 'BEFORE_NODE_LEDGER.json', 'central_DAG_a5db4bac.json', 'central_DAG_e18b4349.json', 'central_DAG_ee94bef8.json', 'ROOT_SCOPE_AND_ASSEMBLY_CONTRACT.md', 'GIT_BLOB_EXPECTATIONS.json', 'SELECTED_RECOVERY.json', 'AGENTS_rei_bianchi_latest.md']
    for name in repo_files:
        copy('survey_repo/' + name, 'survey/repositories/' + name)
    for src in sorted((W / 'survey_repo/selected').iterdir()):
        if src.is_file():
            copy(src.relative_to(W).as_posix(), 'survey/repositories/selected/' + src.name)
    inv = json.loads((W / 'survey_repo/BRANCH_INVENTORY.json').read_text())
    branches = {name: [{'name': b['name'], 'sha': b['commit']['sha']} for b in rows] for name, rows in inv['branches'].items()}
    save(OWN / 'survey/repositories/TASK_BRANCH_INVENTORY.json', {'as_of': inv['as_of'], 'coverage': {k: v for k, v in inv['coverage'].items() if k != 'repo_count'}, 'branches': branches, 'scope': 'Ten task-related repositories only; unrelated owner repository list omitted.'})
    prs = json.loads((W / 'survey_repo/OPEN_PR_INVENTORY.json').read_text())
    keys = ['number', 'title', 'updated_at', 'head_sha', 'head_ref', 'base_sha', 'base_ref', 'draft', 'html_url']
    save(OWN / 'survey/repositories/TASK_OPEN_PR_INVENTORY.json', {'as_of': prs['as_of'], 'open_prs': {name: [{k: row[k] for k in keys if k in row} for row in rows] for name, rows in prs['open_prs'].items()}, 'scope': 'Task-related repository PR metadata; full PR bodies retained only in scratch source survey.'})
    for name in ['SURVEY.md', 'SURVEY.json', 'ACCESS_AND_COVERAGE_LIMITS.json']:
        copy('survey_backup_context/' + name, 'survey/backup_context/' + name)
    for name in ['SURVEY_FINDINGS_KO.md', 'DERIVATION_CANDIDATES.md', 'SOURCE_REFERENCES.json', 'QUERY_PROVENANCE.json', 'FILE_MANIFEST.json', 'DIRECT_DOWNLOAD_RECEIPT.json', 'DIRECT_DOWNLOAD_RECEIPT_ESCALATED.json', 'CDMS_ARCHIVE_DOWNLOAD_RECEIPT.json']:
        copy('survey_literature/' + name, 'survey/literature/' + name)

    manifest_checks = []
    for relative in ['survey_backup_context/recovered/GEO01_S2', 'survey_backup_context/GEO01_S3']:
        root = W / relative
        mpath = root / 'MANIFEST.json'
        manifest = json.loads(mpath.read_text())
        for f in manifest['files']:
            data = (root / f['path']).read_bytes()
            if len(data) != f['bytes'] or sha(data) != f['sha256']:
                raise ValueError('SOURCE_MANIFEST_MISMATCH: ' + relative + '/' + f['path'])
        manifest_checks.append({'source': relative + '/MANIFEST.json', 'sha256': sha(mpath.read_bytes()), 'file_count': len(manifest['files']), 'size_and_sha256': 'PASS'})
    source = W / 'survey_backup_context/GEO01_S3/delivery/GIT_PUBLICATION_FINAL_TEXT_ONLY/TEXT_ONLY_TREE_ENTRIES.json'
    entries = json.loads(source.read_text())
    if len(entries) != 111 or len({e['path'] for e in entries}) != 111:
        raise ValueError('GEO01 expected exact 111 unique text entries')
    records = []
    for e in entries:
        if not e['path'].startswith(HIST) or '..' in Path(e['path']).parts or e['type'] != 'blob' or e['mode'] != '100644':
            raise ValueError('GEO01 source path/type outside frozen recovery scope')
        if 'content' in e:
            data = e['content'].encode('utf-8')
        else:
            binary_source = W / 'survey_backup_context/recovered/GEO01_S2' / e['path']
            data = binary_source.read_bytes()
            blob_sha = hashlib.sha1(b'blob ' + str(len(data)).encode('ascii') + b'\0' + data).hexdigest()
            if blob_sha != e.get('sha'):
                raise ValueError('GEO01 frozen binary Git blob identity mismatch')
        p = REPO / e['path']
        if p.exists() and p.read_bytes() != data:
            raise ValueError('GEO01 existing file differs: ' + e['path'])
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(data)
        if p.read_bytes() != data:
            raise ValueError('GEO01 byte readback failed: ' + e['path'])
        records.append({'path': e['path'], 'bytes': len(data), 'sha256': sha(data)})
    frozen_payload = W / 'publication_payload/GEO01_EXACT_TREE_ENTRIES.json'
    frozen_payload.parent.mkdir(parents=True, exist_ok=True)
    frozen_payload.write_bytes(source.read_bytes())
    recovery = {'schema': 'REC_SYNTHESIS_GEO01_EXACT_TEXT_RECOVERY_V1', 'source_payload': source.relative_to(W).as_posix(), 'source_payload_sha256': sha(source.read_bytes()), 'manifest_checks': manifest_checks, 'restored_count': len(records), 'inline_UTF8_entries': 110, 'existing_binary_Git_blob_references': 1, 'binary_blob_sha': 'de43b1a2642fa0aa049abbfd1b0a7d775d684b1b', 'restored_files': records, 'exact_source_bytes_readback': 'PASS', 'historical_receipts': 'PRESERVED_VERBATIM_INCLUDING_FAILURES_AND_PENDING_DELIVERY', 'new_scientific_execution': 'NONE', 'provider_ack': 'PENDING_ROOT_PUBLICATION', 'binary_primary_inputs': 'Sole frozen history.npz blob materialized from S2 with exact SHA256 and Git blob SHA; not duplicated into new publication ZIP. No historical solver/roots/matvec/test replay.'}
    save(OWN / 'delivery/GEO01_EXACT_TEXT_RECOVERY.json', recovery)
    save(OWN / 'survey/SOURCE_ASSEMBLY_MANIFEST.json', {'schema': 'REC_SYNTHESIS_SELECTED_SURVEY_ASSEMBLY_V1', 'exact_copies': assembly, 'generated_task_inventories': ['survey/repositories/TASK_BRANCH_INVENTORY.json', 'survey/repositories/TASK_OPEN_PR_INVENTORY.json'], 'excluded': ['51-repository unrelated account inventory', 'raw LAMDA data', 'primary PDFs', 'large binary archives'], 'new_scientific_execution': 'NONE'})
    report = {'survey_exact_copy_files': len(assembly), 'task_branch_refs': sum(map(len, branches.values())), 'recovered_GEO01_files': len(records), 'source_manifest_checks': manifest_checks, 'metadata_io_cpu_s': time.process_time() - cpu, 'metadata_io_wall_s': time.perf_counter() - wall, 'new_scientific_execution': 'NONE'}
    save(OWN / 'delivery/SOURCE_ASSEMBLY_RECEIPT.json', report)
    print(json.dumps(report))


if __name__ == '__main__':
    main()
