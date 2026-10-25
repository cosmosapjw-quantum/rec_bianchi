#!/usr/bin/env python3
"""Prepare four additive central paths from an actual committed REC delivery.

This is a mechanical preservation check, not physical approval. No network calls,
Git writes, solver calls, or input-data mutation occur. Output paths are create-only.
"""
from __future__ import annotations
import argparse
import copy
import hashlib
import json
from pathlib import Path
import re
import subprocess

BASE = Path('/workspace/scratch/6104ad84b826')
CENTRAL_PREFIX = 'research/orchestration_expansion_20261025'
REC_PREFIX = 'research/program_expansion_20261025'
OBSERVATION = 'observations/REC_HD_H5_20261025.json'
TARGETS = ('REC-HD-ADAPTER', 'REC-H5-DEFECT-BOUND01')
ALLOWED_FIELDS = {'current_status', 'pass_next_action', 'budget_status', 'current_execution_observation'}
DECODER = json.JSONDecoder()


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical(value) -> bytes:
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(',', ':'), allow_nan=False).encode()


def git_blob_sha1(data: bytes) -> str:
    return hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()


def whitespace(text: str, i: int) -> int:
    while i < len(text) and text[i].isspace():
        i += 1
    return i


def object_spans(text: str) -> dict[str, tuple[int, int]]:
    """Return direct-value spans; nested source documents remain opaque bytes."""
    i = whitespace(text, 0)
    if text[i] != '{':
        raise ValueError('JSON object required')
    i += 1
    result = {}
    while True:
        i = whitespace(text, i)
        if text[i] == '}':
            return result
        key, i = DECODER.raw_decode(text, i)
        if not isinstance(key, str) or key in result:
            raise ValueError('Nonstring or duplicate direct JSON key')
        i = whitespace(text, i)
        if text[i] != ':':
            raise ValueError('Missing JSON colon')
        start = whitespace(text, i + 1)
        _, end = DECODER.raw_decode(text, start)
        result[key] = (start, end)
        i = whitespace(text, end)
        if text[i] == ',':
            i += 1
        elif text[i] != '}':
            raise ValueError('Malformed JSON object separator')


def node_spans(text: str) -> dict[str, tuple[int, int]]:
    start, end = object_spans(text)['nodes']
    i = whitespace(text, start)
    if text[i] != '[':
        raise ValueError('nodes must be an array')
    i += 1
    result = {}
    while True:
        i = whitespace(text, i)
        if text[i] == ']':
            break
        node, after = DECODER.raw_decode(text, i)
        if not isinstance(node, dict) or node.get('id') in result:
            raise ValueError('Invalid or duplicate node')
        result[node['id']] = (i, after)
        i = whitespace(text, after)
        if text[i] == ',':
            i += 1
        elif text[i] != ']':
            raise ValueError('Malformed node separator')
    if i + 1 != end:
        raise ValueError('Node-array span mismatch')
    return result


def patch_wrapper(text: str, replacements: dict) -> str:
    spans = object_spans(text)
    if 'current_execution_observation' in spans:
        raise ValueError('Existing execution observation requires reconciliation; no overwrite')
    edits = [(spans[key][0], spans[key][1], json.dumps(value, ensure_ascii=False, allow_nan=False))
             for key, value in replacements.items() if key != 'current_execution_observation']
    for start, end, value in sorted(edits, reverse=True):
        text = text[:start] + value + text[end:]
    # Preserve every prior key/value span, including the historical observation.
    closing = text.rfind('}')
    content_end = len(text[:closing].rstrip())
    indentation = text[text.rfind('\n', 0, closing) + 1:closing]
    new_field = json.dumps(replacements['current_execution_observation'], ensure_ascii=False, allow_nan=False)
    return (text[:content_end] + ',\n' + indentation + '  "current_execution_observation": '
            + new_field + '\n' + indentation + '}')


def graph(dag: dict, conditional: bool) -> set[tuple[str, str]]:
    ids = {n['id'] for n in dag['nodes']}
    edges = set()
    for node in dag['nodes']:
        fields = ('dependencies', 'conditional_dependencies') if conditional else ('dependencies',)
        for field in fields:
            for dep in node.get(field, []):
                if dep.get('type') == 'internal' and dep.get('id') in ids:
                    edges.add((dep['id'], node['id']))
    if conditional:
        edges |= {(e['from'], e['to']) for e in dag['integration_edges'] if e['from'] in ids and e['to'] in ids}
    return edges


def cyclic_nodes(ids: set[str], edges: set[tuple[str, str]]) -> list[str]:
    indegree = {node: 0 for node in ids}
    outgoing = {node: [] for node in ids}
    for left, right in edges:
        indegree[right] += 1
        outgoing[left].append(right)
    ready = [node for node in ids if indegree[node] == 0]
    while ready:
        node = ready.pop()
        for successor in outgoing[node]:
            indegree[successor] -= 1
            if indegree[successor] == 0:
                ready.append(successor)
    # Remaining nodes are cycle-affected (cycles plus their downstream nodes).
    return sorted(node for node, degree in indegree.items() if degree)


def require(condition: bool, reason: str):
    if not condition:
        raise ValueError(reason)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--rec-commit', required=True, help='Actual committed40hex REC source; must exist in local Git')
    parser.add_argument('--rec-repo', type=Path, default=BASE / 'rec_bianchi')
    parser.add_argument('--base-dag', type=Path, default=BASE / 'central_inputs_latest/DAG.current.json')
    parser.add_argument('--central-base-commit', default='ad9c0e29453fcb6d66637413b51bf42f08688cf1')
    parser.add_argument('--central-base-tree', default=None)
    parser.add_argument('--expected-dag-sha256', default='0565402991c3597946279330594a914e638f483dde48813dd8d15ea00c77c3c3')
    parser.add_argument('--output-root', type=Path, default=BASE / 'central_update_latest')
    args = parser.parse_args()
    for value in (args.rec_commit, args.central_base_commit, args.central_base_tree):
        if value is not None:
            require(bool(re.fullmatch(r'[0-9a-f]{40}', value)) and value != '0' * 40, 'Actual40hex commit/tree identity required')
    subprocess.run(['git', '-C', str(args.rec_repo), 'cat-file', '-e', args.rec_commit + '^{commit}'], check=True)
    inputs = {}
    def committed(relative: str) -> dict:
        path = REC_PREFIX + '/' + relative
        data = subprocess.run(['git', '-C', str(args.rec_repo), 'show', args.rec_commit + ':' + path],
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True).stdout
        inputs[path] = {'sha256': sha256(data), 'bytes': len(data), 'git_blob_sha1': git_blob_sha1(data),
                        'url': f'https://github.com/cosmosapjw-quantum/rec_bianchi/blob/{args.rec_commit}/{path}'}
        return json.loads(data)
    def committed_code_hash(relative: str) -> str:
        data = subprocess.run(['git', '-C', str(args.rec_repo), 'show', args.rec_commit + ':' + REC_PREFIX + '/' + relative],
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True).stdout
        return sha256(data)

    hd = committed('hd_adapter/RESULT.json')
    h5 = committed('h5_input_binding/IMPLEMENTATION_RESULT.json')
    review = committed('review/INDEPENDENT_DECISION.json')
    freeze = committed('EXECUTION_FREEZE_HD_H5.json')
    hd_code = committed_code_hash('hd_adapter/lamda_hd.py')
    h5_code = committed_code_hash('h5_input_binding/code/h5_bounds.py')
    review_sha = inputs[REC_PREFIX + '/review/INDEPENDENT_DECISION.json']['sha256']
    require(hd['independent_review']['record_sha256'] == review_sha, 'HD result points to stale review bytes')
    require(h5['independent_review']['receipt_sha256'] == review_sha, 'H5 result points to stale review bytes')
    require(review['implementation_blocking_findings_open'] == 0, 'Independent implementation findings remain open')
    require(review['HD']['current_code_sha256'] == hd_code == hd['current_code_sha256']['lamda_hd.py'], 'HD current code/review identity mismatch')
    require(review['H5']['current_code_sha256'] == h5_code == h5['identities']['code/h5_bounds.py']['sha256'], 'H5 current code/review identity mismatch; complete repair/review first')
    require(hd['original_full_contract_admission'] == 'HOLD_SOURCE_DISCREPANCY_UNQUALIFIED', 'Original HD gate disposition changed')
    require(hd['line_ids_source_discrepancy'] == [2, 3, 4, 5, 6, 7, 8] and hd['line_ids_pass'] == [1], 'Unexpected HD source-gate result')
    require(hd['original_tolerances_unchanged'] is True and hd['input_source_unchanged'] is True, 'HD source/tolerance preservation required')
    binding = h5['source_binding']
    require(binding['actual_queries'] == 313 and binding['actual_distinct_endpoint_slots'] == 626, 'H5 source binding identity/count changed')
    require(binding['actual_query_bound_input_coverage'] == 0, 'New physical proof coverage requires a separate admission')
    require(h5['physical_epsilon'] is None and h5['physical_outgoing_bound'] is None, 'Physical epsilon/outgoing admission is outside this update')
    require(h5['global_physical_completion'] is None and hd['global_physical_completion'] is None, 'Global physical completion must remain null')
    require(hd['production_approved'] is False and hd['REI_activation'] is False, 'Production/activation are outside this update')
    require(freeze['budgets']['HD']['cpu_seconds'] == 90 and freeze['budgets']['H5']['cpu_seconds'] == 90, 'Unexpected newly frozen budgets')
    for role, expected in [('HD', (hd['source_bytes'], hd['source_sha256'])), ('H5', (binding['source_history_recovered']['bytes'], binding['source_history_recovered']['sha256']))]:
        prefix = 'lamda_hd' if role == 'HD' else None
        actual = ((freeze['source_pins']['lamda_hd_bytes'], freeze['source_pins']['lamda_hd_sha256']) if prefix
                  else (freeze['H5_contract']['source_history_bytes'], freeze['H5_contract']['source_history_sha256']))
        require(actual == expected, role + ' source pin mismatch')

    base_bytes = args.base_dag.read_bytes()
    if args.expected_dag_sha256:
        require(sha256(base_bytes) == args.expected_dag_sha256, 'Central baseline DAG byte identity mismatch')
    original = base_bytes.decode('utf-8')
    dag = json.loads(original)
    before = {n['id']: n for n in dag['nodes']}
    require(len(before) == len(dag['nodes']) == 88, 'Expected88unique baseline nodes')
    require(len(dag['authorities']) == 15 and len(dag['integration_edges']) == 17, 'Central authority/edge census changed')
    require(dag['global_physical_completion'] is None and dag['L4_ready'] is False, 'Central physical/L4 hold changed')
    spans = node_spans(original)
    nodes = copy.deepcopy(before)
    statuses = {'REC-HD-ADAPTER': 'IMPLEMENTATION_VERIFIED_SOURCE_FREQUENCY_GATE_HOLD',
                'REC-H5-DEFECT-BOUND01': 'PASS_DERIVED_IMPLEMENTATION_BOUND_INPUTS_PENDING'}
    next_actions = {'REC-HD-ADAPTER': 'Resolve original LAMDA/CDMS provenance for source lines2-8 under the unchanged35Hz gate; retain literal source columns and physical uncertainty gaps.',
                    'REC-H5-DEFECT-BOUND01': 'Obtain and independently review an actual source-matched continuous defect/tube/stability/curvature/reference proof packet; bind it to the313queries and626endpoints before any physical epsilon admission.'}
    patches = []
    for node_id in TARGETS:
        replacements = {'current_status': statuses[node_id], 'pass_next_action': next_actions[node_id],
            'budget_status': 'Separate new90CPU-second/600execution-wall-second bounded implementation unit completed; original historical allowances preserved; unused allowance transfer0CPU seconds; no borrowing/reset.',
            'current_execution_observation': {'source_file': OBSERVATION, 'json_pointer': '/' + node_id,
                                               'REC_repository': 'cosmosapjw-quantum/rec_bianchi', 'REC_commit': args.rec_commit}}
        nodes[node_id].update(replacements)
        start, end = spans[node_id]
        changed_text = patch_wrapper(original[start:end], replacements)
        require(json.loads(changed_text) == nodes[node_id], 'Wrapper textual patch semantic mismatch')
        patches.append((start, end, changed_text))
    updated = original
    for start, end, replacement in sorted(patches, reverse=True):
        updated = updated[:start] + replacement + updated[end:]
    result_dag = json.loads(updated)
    after = {n['id']: n for n in result_dag['nodes']}
    after_spans = node_spans(updated)
    before_root = object_spans(original)
    after_root = object_spans(updated)
    require(set(dag) == set(result_dag), 'Root fields added or deleted')
    for key in dag:
        if key != 'nodes':
            require(dag[key] == result_dag[key], 'Root field changed: ' + key)
            a, b = before_root[key]; c, d = after_root[key]
            require(original[a:b] == updated[c:d], 'Root field bytes changed: ' + key)
    changed_fields = {}
    for node_id in before:
        old, new = before[node_id], after[node_id]
        start, end = spans[node_id]; nstart, nend = after_spans[node_id]
        if node_id not in TARGETS:
            require(old == new and original[start:end] == updated[nstart:nend], 'Unrelated node changed: ' + node_id)
            continue
        changes = {key for key in old.keys() | new.keys() if old.get(key) != new.get(key)}
        require(changes == ALLOWED_FIELDS and not (old.keys() - new.keys()), 'Nonminimal target wrapper change: ' + node_id)
        changed_fields[node_id] = sorted(changes)
        old_spans, new_spans = object_spans(original[start:end]), object_spans(updated[nstart:nend])
        for key in old:
            if key not in ALLOWED_FIELDS:
                require(old[key] == new[key], 'Protected target field changed: ' + node_id + '/' + key)
                a,b = old_spans[key]; c,d = new_spans[key]
                require(original[start:end][a:b] == updated[nstart:nend][c:d], 'Protected target field bytes changed: ' + key)
    cycle_checks = {}
    for conditional in (False, True):
        g0, g1 = graph(dag, conditional), graph(result_dag, conditional)
        require(g0 == g1, 'Dependency graph changed')
        cyc0, cyc1 = cyclic_nodes(set(before), g0), cyclic_nodes(set(after), g1)
        require(cyc0 == cyc1, 'Cycle structure changed')
        if not conditional:
            require(not cyc1, 'Baseline mandatory graph is cyclic; stop for reconciliation')
        cycle_checks['conditional_union' if conditional else 'mandatory'] = {
            'edges': len(g1), 'cycle_affected_nodes': cyc1, 'graph_exactly_preserved': True,
            'parent_containment_treated_as_dependency': False}

    observed = {
        'schema': 'REC_HD_H5_CENTRAL_EXECUTION_OBSERVATION_V1',
        'source_repository': 'cosmosapjw-quantum/rec_bianchi', 'source_commit': args.rec_commit,
        'central_base_commit': args.central_base_commit, 'central_base_tree': args.central_base_tree,
        'central_base_DAG_sha256': sha256(base_bytes), 'source_artifacts': inputs,
        'qualification': 'Actual committed scoped implementation/source binding; no physical approval from structural validation',
        'new_execution_limits': freeze['budgets'], 'science_scope_limits': freeze['scope_limits'],
        'REC-HD-ADAPTER': {'current_status': statuses[TARGETS[0]], 'original_full_claim_gate_pass': False,
            'source_bytes': hd['source_bytes'], 'source_sha256': hd['source_sha256'],
            'implementation_result': hd, 'independent_review': review['HD'],
            'new_bounded_execution': {'cpu_limit_seconds': 90, 'execution_wall_limit_seconds': 600,
                'known_sampled_CPU_seconds': hd['known_sampled_process_tree_CPU_seconds'],
                'unused_allowance_transfer_CPU_seconds': 0, 'historical_allowances_preserved': True}},
        'REC-H5-DEFECT-BOUND01': {'current_status': statuses[TARGETS[1]], 'physical_claim_gate_pass': False,
            'actual_continuous_bound_input_coverage': 0, 'physical_epsilon': None, 'physical_outgoing_bound': None,
            'source_bytes': binding['source_history_recovered']['bytes'], 'source_sha256': binding['source_history_recovered']['sha256'],
            'implementation_result': h5, 'independent_review': review['H5'],
            'new_bounded_execution': {'cpu_limit_seconds': 90, 'execution_wall_limit_seconds': 600,
                'budget_evidence': h5['budget'], 'unused_allowance_transfer_CPU_seconds': 0,
                'historical_allowances_preserved': True}},
        'global_physical_completion': None, 'L4_ready': False, 'production_approved': False, 'REI_activation': False,
        'historical_contracts_and_status_observations_preserved': True, 'new_scientific_execution_by_assembly': 0}
    outputs = {CENTRAL_PREFIX + '/DAG.json': updated.encode(),
               CENTRAL_PREFIX + '/' + OBSERVATION: (json.dumps(observed, ensure_ascii=False, indent=2, allow_nan=False) + '\n').encode()}
    for node_id in TARGETS:
        start, end = after_spans[node_id]
        outputs[CENTRAL_PREFIX + '/contracts/' + node_id + '.json'] = (updated[start:end] + '\n').encode()
        require(json.loads(outputs[CENTRAL_PREFIX + '/contracts/' + node_id + '.json']) == after[node_id], 'Standalone wrapper differs from DAG node')
    require(len(outputs) == 4, 'Exactly four central output paths required')
    for path in outputs:
        require(not (args.output_root / path).exists(), 'Create-only output already exists: ' + path)
    receipt_path = args.output_root / 'VALIDATION_RECEIPT.json'
    require(not receipt_path.exists(), 'Validation receipt already exists; use a fresh output root')
    receipt = {'schema': 'REC_HD_H5_CENTRAL_MECHANICAL_VALIDATION_V1', 'status': 'PASS_SCOPED_STRUCTURE_AND_PRESERVATION',
        'source_commit': args.rec_commit, 'central_base_commit': args.central_base_commit, 'central_base_tree': args.central_base_tree,
        'base_DAG_sha256': sha256(base_bytes), 'node_count_before_after': [88,88], 'nodes_added': 0, 'nodes_deleted': 0,
        'other_nodes_byte_and_semantic_equal': 86, 'authorities_byte_and_semantic_equal': 15,
        'integration_edges_byte_and_semantic_equal': 17, 'root_fields_outside_nodes_byte_equal': True,
        'historical_snapshot_byte_and_semantic_equal': True, 'all88_nested_contracts_unchanged': True,
        'target_old_status_observation_and_source_fields_byte_equal': True, 'changed_wrapper_fields': changed_fields,
        'cycle_checks': cycle_checks, 'global_physical_completion': None, 'L4_ready': False,
        'physical_approval_from_this_check': False, 'new_scientific_execution': 0,
        'output_paths': {path: {'bytes': len(data), 'sha256': sha256(data), 'git_blob_sha1': git_blob_sha1(data)} for path,data in outputs.items()},
        'assembly_script_sha256': sha256(Path(__file__).read_bytes()), 'source_artifacts': inputs}
    # Validation above is complete before any output mutation. Files are additive.
    for relative, data in outputs.items():
        path = args.output_root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open('xb') as stream:
            stream.write(data)
    with receipt_path.open('x', encoding='utf-8') as stream:
        json.dump(receipt, stream, ensure_ascii=False, indent=2, allow_nan=False)
        stream.write('\n')
    print(json.dumps({'status': receipt['status'], 'source_commit': args.rec_commit,
                      'outputs': list(outputs), 'receipt': str(receipt_path)}, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
