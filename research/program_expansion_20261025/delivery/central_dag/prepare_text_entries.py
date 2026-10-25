#!/usr/bin/env python3
"""Package reviewed text bytes and predict the resulting Git tree without writes to Git."""
import argparse
import hashlib
import json
from pathlib import Path

BASE = Path('/workspace/scratch/6104ad84b826')
DEFAULT_OUTPUT = BASE / 'central_update_final'
DEFAULT_INPUT = BASE / 'central_inputs_final'
PREFIX = 'research/orchestration_expansion_20261025'


def object_sha(kind, data):
    return hashlib.sha1(kind.encode() + b' ' + str(len(data)).encode() + b'\0' + data).hexdigest()


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def tree_bytes(entries):
    def key(row):
        return row['path'].encode('utf-8') + (b'/' if row['type'] == 'tree' else b'')
    chunks = []
    for row in sorted(entries, key=key):
        mode = format(int(row['mode'], 8), 'o').encode()
        chunks.append(mode + b' ' + row['path'].encode('utf-8') + b'\0' + bytes.fromhex(row['sha']))
    return b''.join(chunks)


def update(entries, replacements):
    copied = {row['path']: dict(row) for row in entries}
    for name, value in replacements.items():
        copied[name] = {'path': name, **value}
    return list(copied.values())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input-root', type=Path, default=DEFAULT_INPUT)
    parser.add_argument('--output-root', type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument('--expected-base-commit', required=True)
    parser.add_argument('--expected-base-tree', required=True)
    args = parser.parse_args()
    INPUT, OUTPUT = args.input_root, args.output_root
    receipt_bytes = (OUTPUT / 'VALIDATION_RECEIPT.json').read_bytes()
    receipt = json.loads(receipt_bytes)
    source_receipt = json.loads((INPUT / 'SOURCE_RECEIPT.json').read_bytes())
    tree_payload_bytes = (INPUT / 'TREE_RECURSIVE.json').read_bytes()
    tree_payload = json.loads(tree_payload_bytes)
    assert receipt['status'] == 'PASS_SCOPED_STRUCTURE_AND_PRESERVATION'
    assert receipt['central_base_commit'] == source_receipt['commit'] == args.expected_base_commit
    assert receipt['central_base_tree'] == source_receipt['tree'] == tree_payload['sha'] == args.expected_base_tree
    assert tree_payload['truncated'] is False
    paths = sorted(receipt['output_paths'])
    assert paths == sorted([PREFIX + '/DAG.json', PREFIX + '/contracts/REC-HD-ADAPTER.json',
                            PREFIX + '/contracts/REC-H5-DEFECT-BOUND01.json', PREFIX + '/observations/REC_HD_H5_20261025.json'])
    source_blobs = {row['path']: row for row in tree_payload['tree']}
    text_entries, blobs = [], {}
    for relative in paths:
        data = (OUTPUT / relative).read_bytes()
        expected = receipt['output_paths'][relative]
        blob = object_sha('blob', data)
        assert len(data) == expected['bytes'] and sha256(data) == expected['sha256'] and blob == expected['git_blob_sha1']
        content = data.decode('utf-8')
        assert content.encode('utf-8') == data
        text_entries.append({'path': relative, 'mode': '100644', 'type': 'blob', 'content': content})
        prior = source_blobs.get(relative)
        if prior:
            assert prior['type'] == 'blob' and prior['mode'] == '100644'
        blobs[relative] = {'bytes': len(data), 'sha256': sha256(data), 'expected_git_blob_sha1': blob,
                           'base_git_blob_sha1': prior['sha'] if prior else None,
                           'change': 'replace' if prior else 'create'}
    folders = ['', 'research', PREFIX, PREFIX + '/contracts', PREFIX + '/observations']
    base_trees = {}
    for folder in folders:
        entries = []
        for row in tree_payload['tree']:
            parent, separator, name = row['path'].rpartition('/')
            if parent == folder:
                entries.append({'path': name, 'mode': row['mode'], 'type': row['type'], 'sha': row['sha']})
        expected = tree_payload['sha'] if folder == '' else source_blobs.get(folder, {}).get('sha')
        if expected:
            assert object_sha('tree', tree_bytes(entries)) == expected, 'Base tree reconstruction mismatch: ' + folder
        else:
            assert not entries, 'Unrecorded nonempty base directory'
        base_trees[folder] = {'entries': entries, 'sha': expected}
    changes = {}
    contracts = PREFIX + '/contracts'
    observations = PREFIX + '/observations'
    changes[contracts] = update(base_trees[contracts]['entries'], {
        name: {'mode': '100644', 'type': 'blob', 'sha': blobs[contracts + '/' + name]['expected_git_blob_sha1']}
        for name in ('REC-HD-ADAPTER.json', 'REC-H5-DEFECT-BOUND01.json')})
    changes[observations] = update(base_trees[observations]['entries'], {
        'REC_HD_H5_20261025.json': {'mode': '100644', 'type': 'blob', 'sha': blobs[observations + '/REC_HD_H5_20261025.json']['expected_git_blob_sha1']}})
    predicted = {folder: object_sha('tree', tree_bytes(changes[folder])) for folder in (contracts, observations)}
    changes[PREFIX] = update(base_trees[PREFIX]['entries'], {
        'DAG.json': {'mode': '100644', 'type': 'blob', 'sha': blobs[PREFIX + '/DAG.json']['expected_git_blob_sha1']},
        'contracts': {'mode': '040000', 'type': 'tree', 'sha': predicted[contracts]},
        'observations': {'mode': '040000', 'type': 'tree', 'sha': predicted[observations]}})
    predicted[PREFIX] = object_sha('tree', tree_bytes(changes[PREFIX]))
    changes['research'] = update(base_trees['research']['entries'], {
        'orchestration_expansion_20261025': {'mode': '040000', 'type': 'tree', 'sha': predicted[PREFIX]}})
    predicted['research'] = object_sha('tree', tree_bytes(changes['research']))
    changes[''] = update(base_trees['']['entries'], {'research': {'mode': '040000', 'type': 'tree', 'sha': predicted['research']}})
    predicted[''] = object_sha('tree', tree_bytes(changes['']))
    payload = (json.dumps(text_entries, ensure_ascii=False, indent=2, allow_nan=False) + '\n').encode('utf-8')
    # Validate the file transport itself, including all LF and Unicode content.
    for row in json.loads(payload):
        assert object_sha('blob', row['content'].encode()) == blobs[row['path']]['expected_git_blob_sha1']
    metadata = {'schema': 'REC_HD_H5_GIT_PUBLICATION_OBJECTS_V1',
        'repository': 'cosmosapjw-quantum/rei_bianchi', 'base_commit': receipt['central_base_commit'],
        'base_tree_sha': receipt['central_base_tree'], 'REC_source_commit': receipt['source_commit'],
        'tree_elements_file': 'text_entries.json', 'tree_elements_shape': 'Top-level4-element array: path/mode/type/content',
        'text_entries_bytes': len(payload), 'text_entries_sha256': sha256(payload),
        'expected_result_root_tree_sha': predicted[''], 'expected_blobs': blobs,
        'predicted_trees': {folder or '/': {'base_sha': base_trees[folder]['sha'], 'expected_sha': sha,
                           'base_entries': len(base_trees[folder]['entries']), 'result_entries': len(changes[folder])}
                           for folder, sha in predicted.items()},
        'verification': {'all_existing_ancestor_trees_reconstructed_to_exact_base_SHA': True,
                         'all4reviewed_outputs_byte_identical_to_validation_receipt': True,
                         'UTF8_JSON_roundtrip_matches_all4Git_blob_SHAs': True,
                         'only4declared_blob_paths_changed': True, 'new_scientific_execution': 0,
                         'Git_or_GitHub_mutations_performed': 0},
        'validation_receipt_sha256': sha256(receipt_bytes),
        'base_recursive_tree_SHA256': sha256(tree_payload_bytes),
        'base_AGENTS_SHA256': sha256((INPUT / 'AGENTS.md').read_bytes()),
        'packaging_script_sha256': sha256(Path(__file__).read_bytes()),
        'publication_strategy': 'Fixed snapshot; dedicated new branch and PR; moving main is not followed recursively',
        'root_publication_check': 'Compare create_tree returned SHA to expected_result_root_tree_sha; create commit with the frozen base parent, publish to the owned branch using its expected SHA or create-only absence check, and open PR. Read current HEAD but preserve this frozen snapshot instead of repeatedly rebasing to moving main.'}
    for name, data in [('text_entries.json', payload), ('GIT_OBJECT_VERIFICATION.json', (json.dumps(metadata, ensure_ascii=False, indent=2) + '\n').encode())]:
        with (OUTPUT / name).open('xb') as stream:
            stream.write(data)
    print(json.dumps({'payload': str(OUTPUT / 'text_entries.json'),
                      'metadata': str(OUTPUT / 'GIT_OBJECT_VERIFICATION.json'),
                      'expected_result_root_tree_sha': predicted[''], 'entries': len(text_entries),
                      'bytes': len(payload)}, indent=2))


if __name__ == '__main__':
    main()
