"""Prepare one byte-spliced electron-field backlink; no remote operations.

Run only after root binds the actual fresh DAG, owner C10 source commit and
published central return commit. This helper never changes its input file.
"""
from pathlib import Path
import argparse
import copy
import difflib
import hashlib
import json
import re

REPOSITORY = 'cosmosapjw-quantum/rei_bianchi'
BRANCH = 'research/orchestration-sandbox-20261022'
DAG_PATH = 'research/orchestration_expansion_20261025/DAG.json'
NODE_ID = 'REC-H5-DEFECT-BOUND01'
KEY = 'owner_return_electron_field01_20261028'
ANCHOR_KEY = 'owner_return_native_path01_20261028'
RETURN_FILE = 'returns/REC_H5_ELECTRON_FIELD01_20261028.json'

def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('DUPLICATE_JSON_KEY:' + key)
        result[key] = value
    return result

def require(condition, message):
    if not condition:
        raise ValueError(message)

def git_blob(data):
    return hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()

def identity(data):
    return {'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest(),
            'git_blob': git_blob(data)}

def prepare(args):
    for name in ('base_head', 'owner_c10_source_commit', 'central_return_commit'):
        require(re.fullmatch(r'[0-9a-f]{40}', getattr(args, name)) is not None,
                'ACTUAL_40_HEX_COMMIT_REQUIRED:' + name)
    require(re.fullmatch(r'[0-9a-f]{64}', args.expected_sha256) is not None,
            'EXPECTED_SHA256_REQUIRED')
    require(args.expected_bytes > 0, 'EXPECTED_POSITIVE_BYTE_COUNT_REQUIRED')
    data = args.input_dag.read_bytes()
    require(len(data) == args.expected_bytes, 'BASE_BYTES_MISMATCH')
    require(hashlib.sha256(data).hexdigest() == args.expected_sha256,
            'BASE_SHA256_MISMATCH')
    raw = data.decode('utf-8')
    before = json.loads(raw, object_pairs_hook=unique_object)
    require(isinstance(before, dict), 'TOP_LEVEL_OBJECT_REQUIRED')
    require(isinstance(before.get('nodes'), list), 'TOP_LEVEL_NODES_ARRAY_REQUIRED')
    indices = [i for i, node in enumerate(before['nodes'])
               if isinstance(node, dict) and node.get('id') == NODE_ID]
    require(len(indices) == 1, 'TARGET_NODE_NOT_UNIQUE')
    index = indices[0]
    target = before['nodes'][index]
    require(KEY not in target, 'BACKLINK_ALREADY_PRESENT')
    require(data.count(('"' + KEY + '"').encode()) == 0,
            'NEW_BACKLINK_KEY_ALREADY_PRESENT_ELSEWHERE')
    require(ANCHOR_KEY in target, 'NATIVE_BACKLINK_ANCHOR_MISSING')

    # Reuse the previous native backlink's top-level decoding algorithm. This
    # selects nodes, not an embedded authority/contract copy of the node id.
    decoder = json.JSONDecoder()
    position = raw.index('{') + 1
    nodes_start = None
    while True:
        while raw[position].isspace() or raw[position] == ',':
            position += 1
        if raw[position] == '}':
            break
        name, position = decoder.raw_decode(raw, position)
        while raw[position].isspace() or raw[position] == ':':
            position += 1
        if name == 'nodes':
            nodes_start = position
            break
        _, position = decoder.raw_decode(raw, position)
    require(nodes_start is not None and raw[nodes_start] == '[',
            'TOP_LEVEL_NODES_BYTE_LOCATION_MISSING')
    position = nodes_start + 1
    for current in range(index + 1):
        while raw[position].isspace() or raw[position] == ',':
            position += 1
        start = position
        node, position = decoder.raw_decode(raw, position)
    require(node == target, 'TARGET_BYTE_SPAN_SEMANTIC_MISMATCH')
    target_raw = raw[start:position]
    anchor = '      "' + ANCHOR_KEY + '": {'
    require(target_raw.count(anchor) == 1, 'EXACT_NATIVE_ANCHOR_NOT_UNIQUE')
    insertion_char_offset = start + target_raw.index(anchor)
    require(insertion_char_offset == 0 or raw[insertion_char_offset - 1] == '\n',
            'ANCHOR_NOT_AT_EXPECTED_LINE_START')
    value = {
        'count_increment': 0,
        'return_commit': args.central_return_commit,
        'return_url': 'https://github.com/' + REPOSITORY + '/blob/'
                      + args.central_return_commit
                      + '/research/orchestration_expansion_20261025/' + RETURN_FILE,
        'source_commit': args.owner_c10_source_commit,
        'source_file': RETURN_FILE,
        'source_repository': 'cosmosapjw-quantum/rec_bianchi',
    }
    # Only the new property's bytes are serialized. The complete DAG is never
    # serialized: both sides of the insertion are exact slices of the input.
    lines = ['      "' + KEY + '": {']
    for n, (key, item) in enumerate(value.items()):
        lines.append('        ' + json.dumps(key) + ': ' + json.dumps(item)
                     + (',' if n < len(value) - 1 else ''))
    lines.append('      },')
    insertion = ('\n'.join(lines) + '\n').encode('utf-8')
    offset = len(raw[:insertion_char_offset].encode('utf-8'))
    candidate = data[:offset] + insertion + data[offset:]
    after = json.loads(candidate, object_pairs_hook=unique_object)
    expected = copy.deepcopy(before)
    expected['nodes'][index][KEY] = value
    require(after == expected, 'MORE_THAN_THE_SINGLE_ALLOWED_PROPERTY_CHANGED')
    restored_json = copy.deepcopy(after)
    del restored_json['nodes'][index][KEY]
    require(restored_json == before, 'PRIOR_JSON_NOT_RESTORED')
    require(candidate[:offset] + candidate[offset + len(insertion):] == data,
            'PRIOR_RAW_BYTES_NOT_RESTORED')
    require(len(after['nodes']) == len(before['nodes']), 'NODE_COUNT_CHANGED')
    require(after.get('integration_edges') == before.get('integration_edges'),
            'INTEGRATION_EDGES_CHANGED')
    require(after.get('edges') == before.get('edges'), 'EDGES_CHANGED')
    require(candidate.count(('"' + KEY + '"').encode()) == 1,
            'NEW_PROPERTY_COUNT_NOT_ONE')
    require(after['nodes'][index][ANCHOR_KEY] == target[ANCHOR_KEY],
            'NATIVE_BACKLINK_CHANGED')
    patch = ''.join(difflib.unified_diff(
        raw.splitlines(keepends=True), candidate.decode('utf-8').splitlines(keepends=True),
        fromfile='a/' + DAG_PATH, tofile='b/' + DAG_PATH, n=4))
    receipt = {
        'schema': 'REC_H5_ELECTRON_FIELD01_CENTRAL_BACKLINK_PREPARATION_V1',
        'phase': 'PREPARED_LOCAL_CANDIDATE_ONLY_NOT_PUBLISHED',
        'repository': REPOSITORY, 'branch': BRANCH, 'path': DAG_PATH,
        'expected_sha': args.base_head, 'force': False,
        'before': {'path': str(args.input_dag.resolve()), **identity(data)},
        'after': {'path': str((args.output_dir / 'DAG_candidate.json').resolve()),
                  **identity(candidate)},
        'target': {'node_id': NODE_ID, 'node_index': index,
                   'json_pointer': '/nodes/' + str(index) + '/' + KEY,
                   'value': value},
        'insertion': {'byte_offset': offset, **identity(insertion),
                      'lines_added': insertion.count(b'\n'), 'lines_removed': 0},
        'proof': {
            'base_bytes_sha256_verified': True,
            'all_duplicate_json_keys_rejected': True,
            'unique_top_level_matching_node': True,
            'one_new_property_only': True,
            'all_prior_JSON_equal_after_new_key_removal': True,
            'all_prior_raw_bytes_equal_after_insertion_removal': True,
            'native_backlink_unchanged': True,
            'all_prior_counters_statuses_nulls_contracts_unchanged': True,
            'no_top_level_updated_at_added': 'updated_at' not in after or 'updated_at' in before,
            'nodes_preserved': len(before['nodes']),
            'integration_edges_preserved': len(before.get('integration_edges', [])),
            'input_file_modified': False,
        },
        'remote_mutations': 0, 'scientific_executions': 0,
        'pending': 'Root fresh-HEAD lease, independent actual-candidate review, '
                   'authorized publication and exact post-update readback',
    }
    outputs = {
        'DAG_candidate.json': candidate,
        'DAG_backlink.diff': patch.encode('utf-8'),
        'insertion.txt': insertion,
        'VALIDATION_RECEIPT.json': (json.dumps(receipt, indent=2) + '\n').encode('utf-8'),
    }
    require(all(not (args.output_dir / name).exists() for name in outputs),
            'REFUSE_OVERWRITE_EXISTING_CANDIDATE_OUTPUT')
    args.output_dir.mkdir(parents=True, exist_ok=True)
    for name, content in outputs.items():
        with (args.output_dir / name).open('xb') as output:
            output.write(content)
    return {'before': receipt['before'], 'after': receipt['after'],
            'insertion': receipt['insertion'], 'proof': receipt['proof'],
            'pending_lease': {'expected_sha': args.base_head, 'force': False}}

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input-dag', type=Path, required=True)
    parser.add_argument('--expected-bytes', type=int, required=True)
    parser.add_argument('--expected-sha256', required=True)
    parser.add_argument('--base-head', required=True)
    parser.add_argument('--owner-c10-source-commit', required=True)
    parser.add_argument('--central-return-commit', required=True)
    parser.add_argument('--output-dir', type=Path, required=True)
    print(json.dumps(prepare(parser.parse_args()), indent=2))
