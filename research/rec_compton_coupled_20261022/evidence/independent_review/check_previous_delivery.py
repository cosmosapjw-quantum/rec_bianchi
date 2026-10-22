"""Read-only reuse audit of the prior unit's completed delivery evidence.

This checks retained receipts and local/downloaded bytes. It does not contact
GitHub/Dropbox, restore an archive, import the scientific model, or rerun work.
"""
from pathlib import Path
import hashlib
import json

ROOT = Path('/workspace/scratch/4389c03f19a6')
D = ROOT / 'deliverables'
PARENT = '3a5a853abb2eb0f67650288aa1cee82c576f9ffc'
TREE = '712f2c0ba224fbb902ec8b38f1fa1f53b4c5b4b7'
NAMES = {
    'github': 'REC_THERMAL_OMITTED_PUBLICATION_GITHUB_COMPLETED_20261022.json',
    'dropbox': 'REC_THERMAL_OMITTED_PUBLICATION_DROPBOX_20261022.json',
    'restore': 'REC_THERMAL_OMITTED_RESTORE_AUDIT_20261022.json',
    'integrity': 'REC_THERMAL_OMITTED_BUDGET_20261022_INTEGRITY.json',
}


def hashes(path):
    standard, blocks = hashlib.sha256(), hashlib.sha256()
    n = 0
    with Path(path).open('rb') as stream:
        while chunk := stream.read(4 * 1024 * 1024):
            n += len(chunk)
            standard.update(chunk)
            blocks.update(hashlib.sha256(chunk).digest())
    return dict(bytes=n, sha256=standard.hexdigest(), dropbox_content_hash=blocks.hexdigest())


def main():
    records = {k: json.loads((D / n).read_text()) for k, n in NAMES.items()}
    gh, db, audit, integrity = (records[k] for k in ('github', 'dropbox', 'restore', 'integrity'))
    pr = gh['draft_pr_acknowledgment']['structuredContent']
    assert gh['status'] == 'COMPLETE_EXACT_TREE_DRAFT_PR'
    assert gh['local_final_commit'] == db['source_commit'] == audit['source_commit'] == integrity['source_commit'] == PARENT
    assert gh['exact_root_tree'] == db['source_tree'] == integrity['source_tree'] == TREE
    assert pr['number'] == 122 and pr['draft'] and not pr['merged']
    assert gh['remote_final_commit'] == pr['head_sha'] == '04c0b10c1f1ec38d57c751369c553b638979e453'
    assert gh['dropbox_receipt']['sha256'] == hashes(D / NAMES['dropbox'])['sha256']
    assert integrity['restoration_audit']['sha256'] == hashes(D / NAMES['restore'])['sha256']
    assert audit['status'] == 'PASS' and len(audit['checks']) == 23
    assert all(v['passed'] is True for v in audit['checks'].values())
    assert db['status'] == 'COMPLETE_FULL_READBACK_VERIFIED' and db['all_three_artifacts_verified']
    assert db['publication_mode'] == 'create-only' and not db['shared_links_created']
    for name in ('new_ODE_integrations', 'old_IVP_reruns', 'test_suites_run', 'numerical_postprocess_runs'):
        assert audit[name] == db[name] == 0
    assert integrity['source_identity'] == audit['source_identity'] == '88edf8e7e5ccff94509e03ff2979b3b93e5e988641c5dbd4a5d64f4583bca02c'
    assert integrity['thermal_source_identity'] == audit['thermal_source_identity'] == 'dfd2ca42b7fb768f3e31e5a7cc3ab64a4aa8b422ef0c5b79b8852043b197ff2e'
    artifacts = []
    for item in db['artifacts']:
        local = hashes(item['local_path'])
        saved = hashes(item['full_readback']['saved_readback_path'])
        readback = item['full_readback']
        assert local == saved
        assert local == dict(bytes=item['size_bytes'], sha256=item['sha256'], dropbox_content_hash=item['dropbox_content_hash'])
        assert item['upload_completed_response']['status'] == 'completed'
        assert readback['status'] == 'PASS_FULL_BYTE_READBACK' and readback['http_status'] == 200 and readback['eof_reached']
        assert readback['bytes_received'] == local['bytes'] and readback['sha256'] == local['sha256'] and readback['dropbox_content_hash'] == local['dropbox_content_hash']
        assert item['provider_metadata']['size'] == local['bytes']
        artifacts.append(dict(name=item['name'], current_local_and_saved_readback=local,
                              retained_provider_id=item['provider_metadata']['id'], retained_provider_rev=item['provider_metadata']['rev'],
                              retained_full_readback_status=readback['status']))
    archive = artifacts[0]['current_local_and_saved_readback']
    assert archive['sha256'] == gh['archive']['sha256'] == audit['archive_sha256'] == integrity['archive_sha256']
    assert archive['bytes'] == gh['archive']['bytes'] == audit['archive_bytes'] == integrity['archive_bytes'] == 44847883
    assert integrity['payload_count'] == db['archive_payload_count'] == 888
    assert integrity['archive_entry_count'] == db['archive_entry_count'] == 889
    print(json.dumps(dict(
        schema='rec.compton.independent.prior_delivery_reuse.v1', status='PASS_REUSED_DELIVERY_EVIDENCE',
        prior_local_commit=PARENT, prior_remote_commit=gh['remote_final_commit'], exact_root_tree=TREE,
        prior_draft_pr=pr['url'], prior_restore_checks_passed=23,
        receipt_sha256={n: hashes(D / n)['sha256'] for n in NAMES.values()}, artifacts=artifacts,
        new_network_reads=0, new_restores=0, new_ODE_runs=0, old_suite_reruns=0,
        confirmed='Retained publication, full readback and restoration receipts are mutually bound; all three current local files and saved downloaded files still have their recorded size, SHA-256 and Dropbox content hash.',
        limits='This review reuses the recorded remote acknowledgments and prior fresh-directory restoration. It does not assert current live remote state or perform a new restore. The prior restore author also authored the collision provider/archive builder; its receipt is restoration evidence, not independent physics approval.'
    ), indent=2))


if __name__ == '__main__':
    main()
