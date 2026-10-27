#!/usr/bin/env python3
"""Prepare the exact parent-authorized central delta; no science or publication."""
import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import re
import time

WORKSPACE = Path('/workspace/scratch/6104ad84b826')
REPO = WORKSPACE / 'rec_bianchi'
UNIT = REPO / 'research/rec_source_synthesis_20261027'
SURVEY = WORKSPACE / 'survey_repo'
CENTRAL = 'research/orchestration_expansion_20261025'
BASE = '5abe0d19df95db730e3e33bae0373c81ba37ce89'
WORKING = 'ee94bef85b56d879dc38f184856a5c613575e9e1'
HD_H5 = 'e18b4349f2a2da3ef7caf5ec73c8787d03894620'
GEO = 'eb3b390eb59a4c48b5aa2d3bec928465b9c35f2e'
REC_REPO = 'cosmosapjw-quantum/rec_bianchi'
DAG_INPUTS = [
    ('central_DAG_5abe0d19.json', '007b79e22a52c3701b9dd8a6cf8dfee62f3a7a3cb50367e56e998ece9dfec8b0'),
    ('central_DAG_ee94bef8.json', 'e4c30609e737318724877a10c1acb7f139b6dc521e3b207a9455cfe632613b1d'),
    ('central_DAG_e18b4349.json', 'bb05523325ee14659e326f315eb4d3948b918f0566f478fe27cd44640dccbb58'),
]
WORKING_KEYS = {node: ['current_status', 'status_observation'] for node in ['HE-EXP-SPECIES', 'REC-EXP-SPECIES', 'REC-EXP-EXTERNAL', 'REC-EXP-SPECTRAL', 'REC-FIELD']}
WORKING_KEYS['REC-COUPLED'] = ['current_status', 'status_observation', 'selectedRuntimeContract']
HD_H5_KEYS = {node: ['current_status', 'pass_next_action', 'budget_status', 'current_execution_observation'] for node in ['REC-HD-ADAPTER', 'REC-H5-DEFECT-BOUND01']}
SOURCE_RETURN = CENTRAL + '/returns/REC_SOURCE_SYNTHESIS_20261027.json'
GEO_RETURN = CENTRAL + '/returns/REC_GEO01_RECOVERED_20261027.json'
ADOPTION_RETURN = CENTRAL + '/returns/REC_SOURCE_SYNTHESIS_ADOPTION_20261027.json'
STATUS_RETURN = CENTRAL + '/status/REC_SOURCE_SYNTHESIS_20261027.json'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def encoded(value):
    return (json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n').encode('utf-8')


def load(path, expected_sha=None):
    data = path.read_bytes()
    if expected_sha and sha(data) != expected_sha:
        raise ValueError('IMMUTABLE_SOURCE_BYTE_MISMATCH: ' + str(path))
    return json.loads(data)


def pin(path, commit):
    local = REPO / path
    data = local.read_bytes()
    return {'repository': REC_REPO, 'commit': commit, 'path': path, 'bytes': len(data), 'sha256': sha(data)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--science-commit', required=True, help='actual ACKed C9 science commit; supplied by parent after GO')
    parser.add_argument('--decision', type=Path, required=True, help='actual parent ROOT_DECISION.json, never a predicted decision')
    args = parser.parse_args()
    if not re.fullmatch('[0-9a-f]{40}', args.science_commit):
        parser.error('--science-commit must be an exact 40-character SHA')
    cpu_start, wall_start = time.process_time(), time.perf_counter()
    decision_path = args.decision.resolve()
    decision_relative = decision_path.relative_to(REPO).as_posix()
    decision = load(decision_path)
    if not isinstance(decision, dict) or not decision:
        parser.error('actual parent decision must be a nonempty JSON document')
    analysis = load(SURVEY / 'CENTRAL_INTEGRATION_SOURCE_ANALYSIS.json')
    recovery = load(SURVEY / 'CENTRAL_DIRECT_SOURCE_RECOVERY.json')
    if analysis['fixed_inputs'] != {'base': BASE, 'six_working_wrappers': WORKING, 'two_HD_H5_wrappers': HD_H5} or recovery['base_commit'] != BASE:
        raise ValueError('fixed central source authority mismatch')
    base, working, historical_hd = [load(SURVEY / name, expected) for name, expected in DAG_INPUTS]
    bnodes, wnodes, hnodes = ({node['id']: node for node in doc['nodes']} for doc in [base, working, historical_hd])
    if len(bnodes) != 88 or len(base['authorities']) != 15 or len(base['integration_edges']) != 17:
        raise ValueError('fixed central source shape mismatch')
    assembled = deepcopy(base)
    anodes = {node['id']: node for node in assembled['nodes']}
    allowed = {node: set(keys) for node, keys in {**WORKING_KEYS, **HD_H5_KEYS}.items()}
    for changes, source_nodes in [(WORKING_KEYS, wnodes), (HD_H5_KEYS, hnodes)]:
        for node_id, keys in changes.items():
            for key in keys:
                anodes[node_id][key] = deepcopy(source_nodes[node_id][key])
    new_owner_pointer = {'source_file': 'returns/REC_SOURCE_SYNTHESIS_20261027.json', 'source_repository': REC_REPO, 'source_commit': args.science_commit, 'adoption_envelope': 'returns/REC_SOURCE_SYNTHESIS_ADOPTION_20261027.json', 'count_increment': 0}
    for node_id in ['REC-HD-ADAPTER', 'REC-H5-DEFECT-BOUND01', 'REC-HISTORY']:
        anodes[node_id]['owner_return_source_synthesis_20261027'] = deepcopy(new_owner_pointer)
        allowed.setdefault(node_id, set()).add('owner_return_source_synthesis_20261027')
    anodes['REC-HISTORY']['owner_return_geo01_recovered_20261027'] = {'source_file': 'returns/REC_GEO01_RECOVERED_20261027.json', 'source_repository': REC_REPO, 'source_commit': GEO, 'count_increment': 0}
    allowed['REC-HISTORY'].add('owner_return_geo01_recovered_20261027')

    ledger_path = UNIT / 'survey/repositories/DAG_COUNT_RECONCILIATION.json'
    ledger = load(ledger_path)
    completed_ids = ledger['working_count']['completion_ids']
    shared_ids = ledger['central_shared_count']['completion_ids']
    if len(set(completed_ids)) != 32 or len(set(shared_ids)) != 27 or not set(completed_ids) <= set(bnodes) or not set(shared_ids) <= set(completed_ids):
        raise ValueError('existing original-node count ledger mismatch')
    counts = {'shared_base_commit': BASE, 'shared_authority_completed': 27, 'shared_authority_total': 88, 'assembled_working_completed': 32, 'total': 88, 'new_unit_increment': 0, 'shared_merge_state': 'UNMERGED_AT_PREPARATION', 'completed_original_node_ids': completed_ids, 'shared_completed_original_node_ids': shared_ids, 'count_rule_source': pin(ledger_path.relative_to(REPO).as_posix(), args.science_commit), 'global_physical_completion': None, 'L4_ready': False}

    geo_paths = ['research/rec_history_geometry_response_20261026/ROOT_DECISION.json', 'research/rec_history_geometry_response_20261026/evidence/independent_review/FINAL_DECISION.json', 'research/rec_history_geometry_response_20261026/delivery/CENTRAL_GEO01_OBSERVATION.json', 'research/rec_source_synthesis_20261027/delivery/GEO01_RECOVERED_DELIVERY.json']
    geo_decision = load(REPO / geo_paths[0])
    geo_delivery = load(REPO / geo_paths[3])
    geo_return = {'schema': 'REC_GEO01_RECOVERED_OWNER_RETURN_20261027_V1', 'parent_node': 'REC-HISTORY', 'source_predicate': geo_decision['decision'], 'source_repository': REC_REPO, 'source_commit': GEO, 'evidence': [pin(path, GEO) for path in geo_paths], 'actual_recovery_delivery_document': geo_delivery, 'historical_preimages': 'Original ROOT_DECISION and CENTRAL_GEO01_OBSERVATION remain immutable, including historical pending Git/Drive status. This sibling return records later recovery.', 'count_increment': 0, 'physical_epsilon': None, 'H5_continuous_bound_coverage': '0/313', 'H6': 'OPEN', 'H7': 'OPEN', 'parent_REC_HISTORY': 'PARTIAL', 'new_scientific_runs': 0}
    evidence_paths = [decision_relative, 'research/rec_source_synthesis_20261027/hd_joint/raw/primary001/DIAGNOSTICS.json', 'research/rec_source_synthesis_20261027/hd_joint/raw/primary001/SUMMARY.json', 'research/rec_source_synthesis_20261027/hd_joint/raw/primary001/TARGETED_CONTROLS.json', 'research/rec_source_synthesis_20261027/hd_joint/raw/primary001/EXECUTION.json', 'research/rec_source_synthesis_20261027/hd_joint/raw/primary001/joint_thermal_diagnostics.png', 'research/rec_source_synthesis_20261027/hd_joint/raw/primary001/joint_thermal_diagnostics.pdf', 'research/rec_source_synthesis_20261027/history_remainder/results/primary001/summary.json', 'research/rec_source_synthesis_20261027/history_remainder/evidence/primary001.receipt.json', 'research/rec_source_synthesis_20261027/history_remainder/evidence/plot001.receipt.json', 'research/rec_source_synthesis_20261027/history_remainder/figures/history_remainders.png', 'research/rec_source_synthesis_20261027/history_remainder/figures/history_remainders.pdf']
    evidence_paths.extend(path.relative_to(REPO).as_posix() for path in sorted((UNIT / 'review').rglob('*')) if path.is_file() and path.suffix in {'.json', '.md'})
    evidence_paths = list(dict.fromkeys(evidence_paths))
    source_return = {'schema': 'REC_SOURCE_SYNTHESIS_OWNER_RETURN_20261027_V1', 'owner_repository': REC_REPO, 'source_commit': args.science_commit, 'source_root': 'research/rec_source_synthesis_20261027/', 'parent_nodes': ['REC-HD-ADAPTER', 'REC-H5-DEFECT-BOUND01', 'REC-HISTORY'], 'parent_root_decision': decision, 'parent_root_decision_evidence': pin(decision_relative, args.science_commit), 'evidence': [pin(path, args.science_commit) for path in evidence_paths], 'saved_HD_summary': load(REPO / 'research/rec_source_synthesis_20261027/hd_joint/raw/primary001/SUMMARY.json'), 'saved_history_summary': load(REPO / 'research/rec_source_synthesis_20261027/history_remainder/results/primary001/summary.json'), 'new_physical_approval': False, 'original_HD_gate': '35_Hz; seven of eight source lines remain unqualified', 'physical_epsilon': None, 'H5_continuous_bound_coverage': '0/313', 'H6': 'OPEN', 'H7': 'OPEN', 'count_increment': 0, 'counts': counts, 'historical_results_and_budgets': 'Reused without replay, reset or transfer; original current_status and nested frozen preimages remain separate from this sibling observation.'}

    files = recovery['files']
    if len(files) != 26 or len({f['path'] for f in files}) != 26:
        raise ValueError('expected 26 exact direct source files')
    direct_payloads, copied_sources = {}, []
    for source in files:
        relative = source['path']
        if not relative.startswith('research/') or '..' in Path(relative).parts:
            raise ValueError('invalid source path in fixed recovery receipt')
        data = Path(source['local_path']).read_bytes()
        git_sha = hashlib.sha1(b'blob ' + str(len(data)).encode('ascii') + b'\0' + data).hexdigest()
        if len(data) != source['bytes'] or sha(data) != source['sha256'] or git_sha != source['git_blob_sha1']:
            raise ValueError('direct source byte identity mismatch: ' + relative)
        direct_payloads[relative] = data
        copied_sources.append({key: source[key] for key in ['commit', 'path', 'bytes', 'sha256', 'git_blob_sha1']})
    adoption = {'schema': 'REC_SOURCE_SYNTHESIS_CENTRAL_ADOPTION_ENVELOPE_V1', 'base_shared_commit': BASE, 'six_selected_wrappers_original_commit': WORKING, 'HD_H5_selected_wrappers_original_commit': HD_H5, 'new_science_repository': REC_REPO, 'new_science_commit': args.science_commit, 'new_parent_decision': pin(decision_relative, args.science_commit), 'copied_direct_sources': copied_sources, 'reference_resolution': {'research_prefixed_paths': 'repository-root-relative at each recorded original source commit', 'returns_and_observations_source_files': 'relative to research/orchestration_expansion_20261025 at each recorded original source commit', 'nested_relative_references': 'interpret at the original ee94/e18 commits and original source-unit directory; copied preimages are not rewritten', 'REC_COUPLED_domain_and_limits': 'theory/CONTRACT.md relative to research/rei_expanded_event_consumer/coupled_source_20261027 at ee94bef85b56d879dc38f184856a5c613575e9e1'}, 'historical_preimages_preserved': ['species source_commit:null', 'PENDING_ACTUAL_PUBLICATION_ACK', 'original failed execution/check records', 'original own-unit closed-budget descriptions'], 'claim': 'Adopt named owner observations with pinned provenance, preserving original contract scopes and all unrelated shared returns.', 'counts': counts}
    status = {'schema': 'REC_SOURCE_SYNTHESIS_CENTRAL_SCOPED_STATUS_V1', 'base_shared_commit': BASE, 'science_commit': args.science_commit, 'source_return': 'returns/REC_SOURCE_SYNTHESIS_20261027.json', 'GEO_recovered_return': 'returns/REC_GEO01_RECOVERED_20261027.json', 'adoption_envelope': 'returns/REC_SOURCE_SYNTHESIS_ADOPTION_20261027.json', 'counts': counts, 'parent_root_decision': decision, 'existing_CURRENT_STATUS': 'NOT_MODIFIED', 'physical_epsilon': None, 'physical_bound_coverage': '0/313', 'global_physical_completion': None, 'L4_ready': False}

    changes = []
    for node_id, old in bnodes.items():
        new = anodes[node_id]
        changed = {key for key in set(old) | set(new) if old.get(key) != new.get(key) or (key in old) != (key in new)}
        if changed - allowed.get(node_id, set()):
            raise ValueError('out-of-scope node change: ' + node_id + ': ' + str(changed))
        if old['contract'] != new['contract'] or old.get('dependencies') != new.get('dependencies') or old.get('conditional_dependencies') != new.get('conditional_dependencies'):
            raise ValueError('original contract/dependency changed: ' + node_id)
        if node_id not in HD_H5_KEYS and old.get('budget_status') != new.get('budget_status'):
            raise ValueError('foreign budget changed: ' + node_id)
        if changed:
            changes.append({'node_id': node_id, 'changed_top_level_keys': sorted(changed)})
    non_nodes_preserved = all(value == assembled[key] for key, value in base.items() if key != 'nodes')
    ids_order_preserved = [n['id'] for n in base['nodes']] == [n['id'] for n in assembled['nodes']]
    if not non_nodes_preserved or not ids_order_preserved:
        raise ValueError('central non-node fields or original node order changed')
    comparison = {'schema': 'REC_SOURCE_SYNTHESIS_CENTRAL_MECHANICAL_COMPARISON_V1', 'status': 'PASS_MECHANICAL_SCOPE_ONLY', 'base_commit': BASE, 'original_node_count': 88, 'original_node_ids_and_order_preserved': ids_order_preserved, 'all_88_original_contracts_and_normal_conditional_dependencies': 'STRUCTURALLY_IDENTICAL', 'all_15_authorities_and_17_integration_edges': 'STRUCTURALLY_IDENTICAL', 'all_non_node_top_level_fields': 'STRUCTURALLY_IDENTICAL', 'foreign_budget_status': 'UNCHANGED', 'unchanged_nodes': [node_id for node_id in bnodes if node_id not in allowed], 'changed_nodes': changes, 'direct_source_files_byte_identical': len(copied_sources), 'base_BASS_and_CR_returns': 'All unaffected wrappers and non-node objects preserved from fixed5abe, including newer shared BASS/CR observations; no whole-DAG replacement.', 'existing_CURRENT_STATUS': 'NOT_MODIFIED', 'scientific_runs': 0, 'publication': 'NOT_ATTEMPTED'}
    new_checks = {'schema': 'REC_SOURCE_SYNTHESIS_NEW_RETURN_CHECKS_V1', 'status': 'PASS_MECHANICAL_SOURCE_BINDING_ONLY', 'science_commit': args.science_commit, 'parent_decision_sha256': sha(decision_path.read_bytes()), 'parent_decision_document_copied_without_interpretation': source_return['parent_root_decision'] == decision, 'GEO_source_predicate_from_original_root': geo_return['source_predicate'], 'GEO_historical_commit': GEO, 'copied_direct_files': len(copied_sources), 'source_return_attached_to': ['REC-HD-ADAPTER', 'REC-H5-DEFECT-BOUND01', 'REC-HISTORY'], 'GEO_return_attached_to': ['REC-HISTORY'], 'count_increment': 0, 'physical_epsilon': None, 'H5coverage': '0/313', 'H6': 'OPEN', 'H7': 'OPEN', 'no_scientific_decision_inferred': True}

    out = UNIT / 'delivery/central'
    tree = out / 'patch_tree'
    tree.mkdir(parents=True, exist_ok=False)
    payloads = {**direct_payloads, CENTRAL + '/DAG.json': encoded(assembled), SOURCE_RETURN: encoded(source_return), GEO_RETURN: encoded(geo_return), ADOPTION_RETURN: encoded(adoption), STATUS_RETURN: encoded(status)}
    entries, manifest = [], []
    for relative, data in sorted(payloads.items()):
        target = tree / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        entries.append({'path': relative, 'mode': '100644', 'type': 'blob', 'content': data.decode('utf-8')})
        manifest.append({'path': relative, 'bytes': len(data), 'sha256': sha(data)})
    for path, value in [('CENTRAL_TREE_ENTRIES.json', entries), ('CENTRAL_PATCH_MANIFEST.json', manifest), ('MECHANICAL_COMPARISON.json', comparison), ('NEW_RETURN_CHECKS.json', new_checks)]:
        (out / path).write_bytes(encoded(value))
    report = {'schema': 'REC_SOURCE_SYNTHESIS_CENTRAL_ASSEMBLY_RECEIPT_V1', 'status': 'PREPARED_ONLY_NO_PUBLICATION_ACK', 'expected_central_base': BASE, 'science_commit': args.science_commit, 'decision_path': str(decision_path), 'patch_tree': str(tree), 'publication_payload': str(out / 'CENTRAL_TREE_ENTRIES.json'), 'files': len(entries), 'metadata_io_cpu_s': time.process_time() - cpu_start, 'metadata_io_wall_s': time.perf_counter() - wall_start, 'scientific_runs': 0, 'unmeasured_tail': 'Final receipt serialization metadata UNKNOWN_NOT_ZERO', 'live_central_head_assessment': 'Parent-owned; this assembly uses the accepted fixed5abe snapshot.'}
    (out / 'ASSEMBLY_RECEIPT.json').write_bytes(encoded(report))
    print(json.dumps(report))


if __name__ == '__main__':
    main()
