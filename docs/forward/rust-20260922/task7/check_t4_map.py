#!/usr/bin/env python3
"""Validate Task7 static traceability only. Never certify a Rust or T4 PASS.

The authored snapshot remains NOT_RUN. Actual local execution receipts belong
in a separate return, bound to the tested commit and source/acceptance identity.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
from typing import Any

CONSUMER_ONLY = {'T4L04', 'T4L05', 'T4L06', 'T4L07'}
SPLIT = {'T4L08', 'T4L09'}
AUDIT = {'T4L02', 'T4L03', 'T4L12', 'T4L13', 'T4L14'}
COMMANDS = [
    ['cargo', 'fmt', '--manifest-path', 'rust/rec_microphysics/Cargo.toml', '--', '--check'],
    ['cargo', 'test', '--manifest-path', 'rust/rec_microphysics/Cargo.toml', '--locked'],
    ['python', 'scripts/check_rust_forward_parity.py'],
]
CURRENT = {
    'gate_p': 'NOT_RUN', 'gate_i': 'DEFERRED_CONSUMER',
    'full_original_t4': 'NOT_RUN', 'candidate_commit_sha': None,
    'tested_commit_sha': None, 'delivery_commit_sha': None,
    'allow_consumer_integration': False,
}
HOLDS = {
    'S3': 'accepted', 'S4': 'partial', 'S5': 'gated', 'G10': 'open',
    'G11_G13': 'gated', 'D86': 'canonical', 'P0_physical': 'OPEN',
    'HOST4_physical': 'HOLD', 'HH_propagation': 'unauthorized',
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def validate_documents(mapping: dict[str, Any], policy: dict[str, Any],
                       registry: dict[str, Any], repo_root: Path) -> list[str]:
    """Check pinned definitions, source/test references, and non-promotion state."""
    errors: list[str] = []
    cache: dict[str, bytes] = {}
    root = Path(repo_root).resolve()

    def require(condition: bool, message: str) -> None:
        if not condition:
            errors.append(message)

    def raw(relative: str) -> bytes:
        if relative not in cache:
            p = Path(relative)
            if p.is_absolute() or '..' in p.parts:
                raise ValueError(f'unsafe source path: {relative}')
            resolved = (root / p).resolve()
            if not resolved.is_relative_to(root):
                raise ValueError(f'path leaves root: {relative}')
            cache[relative] = resolved.read_bytes()
        return cache[relative]

    def check_ref(item: dict[str, Any]) -> None:
        b = raw(item['path'])
        require(sha256(b) == item['sha256'], f"hash mismatch: {item['path']}")
        require(len(b) == item['size_bytes'], f"size mismatch: {item['path']}")
        if 'lines' in item:
            a, z = item['lines']
            lines = b.decode('utf-8-sig').splitlines()
            require(isinstance(a, int) and isinstance(z, int) and 1 <= a <= z <= len(lines),
                    f"invalid line span: {item['path']}")
            selected = lines[a-1:z]
            require(bool(selected) and item['anchor'] in selected[0],
                    f"anchor mismatch: {item['path']}:{a}")
            section = ('\n'.join(selected) + '\n').encode()
            require(sha256(section) == item['section_sha256'],
                    f"section mismatch: {item['path']}:{a}-{z}")

    try:
        require(mapping['schema'] == 'REC_HE_T4_COVERAGE_MAP_TASK7_V1', 'map schema')
        require(policy['schema'] == 'REC_HE_GATE_P_I_POLICY_V1', 'policy schema')
        require(registry['schema'] == 'REC_HE_T4_STATIC_FIXTURE_REGISTRY_V1', 'registry schema')
        for name in ['original_matrix', 'authority_audit', 'rust_test_file']:
            check_ref(mapping[name])
        for item in mapping['supplement_acceptance']:
            check_ref(item)
        original = json.loads(raw(mapping['original_matrix']['path']))
        require([x['original'] for x in mapping['rows']] == original['tests'],
                'original IDs/classes/descriptions/order must match all 15 source entries')
        original_ids = [x['id'] for x in original['tests']]
        require(original_ids == [f'T4L{i:02d}' for i in range(1, 16)], 'source matrix IDs')
        require(policy['required_gate_p_ids'] == [i for i in original_ids if i not in CONSUMER_ONLY], 'Gate P IDs')
        require(set(policy['consumer_only_ids']) == CONSUMER_ONLY, 'consumer-only scope')
        require(set(policy['split_ids']) == SPLIT, 'split scope')
        require(policy['required_commands'] == COMMANDS, 'required command contract changed')
        require(policy['current'] == CURRENT, 'authored state must not claim execution/promotion')
        require(policy['scientific_state_unchanged'] == HOLDS, 'scientific HOLD changed')
        require(registry['meaning'] == 'REFERENCE_EXPECTATIONS_NOT_OBSERVED_RUST', 'reference/observation conflated')

        for key in ['inputs', 'reference', 'reference_lock']:
            check_ref(registry[key])
        inputs = json.loads(raw(registry['inputs']['path']))['cases']
        reference = json.loads(raw(registry['reference']['path']))['records']
        inputs_by_id = {x['id']: x for x in inputs}
        refs = {x['id']: x for x in reference}
        require(len(inputs_by_id) == len(inputs), 'duplicate input ID')
        require([x['id'] for x in inputs] == [x['id'] for x in reference], 'input/reference ID order')
        require(registry['reference_records_expected'] == len(inputs), 'fixture count mismatch')
        expected_records = [
            {'id': x['id'], 'op': x['op'], 'expected_status': refs[x['id']]['status'],
             'observable_keys': list(refs[x['id']]['values']), 'tags': refs[x['id']]['tags']}
            for x in inputs
        ]
        require(registry['records'] == expected_records, 'fixture statuses/observables changed')
        lock = json.loads(raw(registry['reference_lock']['path']))
        base = str(Path(registry['reference_lock']['path']).parent)
        for name, expected in lock['sha256'].items():
            require(sha256(raw(base + '/' + name)) == expected, 'frozen fixture changed: ' + name)
        for group, ids in registry['groups'].items():
            require(bool(ids) and len(ids) == len(set(ids)), 'empty/duplicate fixture group: ' + group)
            require(all(i in refs for i in ids), 'unknown fixture record in group: ' + group)

        test_text = raw(mapping['rust_test_file']['path']).decode()
        test_symbols = re.findall(r'#\[test\]\s*fn\s+(\w+)\s*\(', test_text)
        require(len(test_symbols) == len(set(test_symbols)), 'duplicate Rust test symbol')
        for row in mapping['rows']:
            ident = row['original']['id']
            consumer = ident in CONSUMER_ONLY
            split = ident in SPLIT
            require(type(row['gate_p_required']) is bool and row['gate_p_required'] is (not consumer), ident + ' Gate P scope')
            require(type(row['gate_i_required']) is bool and row['gate_i_required'] is (consumer or split), ident + ' Gate I scope')
            scope = 'CONSUMER_ONLY' if consumer else ('MATERIAL_SUBCHECK_PLUS_CONSUMER' if split else 'MATERIAL_LIBRARY')
            require(row['scope'] == scope, ident + ' scope label')
            require(row['material_execution'] == ('NOT_APPLICABLE' if consumer else 'NOT_RUN'), ident + ' material execution')
            require(row['original_full_execution'] == ('DEFERRED_CONSUMER' if consumer or split else 'NOT_RUN'), ident + ' original execution')
            require(row['local_audit_required'] is (ident in AUDIT), ident + ' review obligation')
            require(row['local_audit_status'] == ('PENDING' if ident in AUDIT else 'NOT_APPLICABLE'), ident + ' review state')
            require(row['authorship_status'] == ('DEFERRED_CONSUMER' if consumer else 'WRITTEN_NOT_EXECUTED'), ident + ' authorship state')
            if consumer:
                require(row['material_requirement'] is None and not row['rust_tests'] and not row['parity_groups'], ident + ' false material coverage')
            else:
                require(bool(row['material_requirement']) and bool(row['rust_tests']) and bool(row['parity_groups']), ident + ' missing material coverage')
            keys: set[str] = set()
            for group in row['parity_groups']:
                if group not in registry['groups']:
                    errors.append(ident + ' nonexistent group: ' + group)
                    continue
                for name in registry['groups'][group]:
                    if name in refs:
                        keys.update(refs[name]['values'])
            require(set(row['observable_keys']).issubset(keys), ident + ' nonexistent observable')
            for item in row['rust_tests']:
                check_ref(item)
                require(item['symbol'] in test_symbols, ident + ' non-test symbol: ' + item['symbol'])
                require(item['anchor'] == 'fn ' + item['symbol'] + '(', ident + ' test/anchor mismatch')
                require(item['execution'] == 'NOT_RUN', ident + ' false test execution')
            for item in row['source_refs']:
                check_ref(item)
            require(bool(row['limits']), ident + ' missing claim limit')
    except (OSError, ValueError, KeyError, TypeError, IndexError) as exc:
        errors.append(f'invalid map/reference structure: {type(exc).__name__}: {exc}')
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[4])
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    here = args.root / 'docs/forward/rust-20260922/task7'
    try:
        mapping, policy, registry = [json.loads((here / n).read_text()) for n in
            ['T4_COVERAGE_MAP.json', 'GATE_P_I_POLICY.json', 'FIXTURE_REGISTRY.json']]
        errors = validate_documents(mapping, policy, registry, args.root)
        report = {
            'status': 'STATIC_MAP_VALID_NOT_T4_PASS' if not errors else 'STATIC_MAP_INVALID',
            'errors': errors, 'original_rows': len(mapping.get('rows', [])),
            'gate_p_obligations': len(policy.get('required_gate_p_ids', [])),
            'gate_p': 'NOT_RUN', 'gate_i': 'DEFERRED_CONSUMER',
            'rust_execution_performed': False, 'allow_consumer_integration': False,
        }
    except (OSError, ValueError) as exc:
        report = {'status': 'STATIC_MAP_INVALID', 'errors': [str(exc)],
                  'rust_execution_performed': False, 'allow_consumer_integration': False}
    payload = json.dumps(report, ensure_ascii=False, indent=2) + '\n'
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload)
    print(payload, end='')
    return 0 if not report['errors'] else 1

if __name__ == '__main__':
    raise SystemExit(main())
