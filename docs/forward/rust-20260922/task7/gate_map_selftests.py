"""Tests for the STATIC coverage-map checker. Not scientific/Rust tests."""
from pathlib import Path
import copy
import json
import unittest
import check_t4_map as checker

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]

class MapContractTests(unittest.TestCase):
    def setUp(self):
        self.mapping = json.loads((HERE / 'T4_COVERAGE_MAP.json').read_text())
        self.policy = json.loads((HERE / 'GATE_P_I_POLICY.json').read_text())
        self.registry = json.loads((HERE / 'FIXTURE_REGISTRY.json').read_text())

    def errors(self):
        return checker.validate_documents(self.mapping, self.policy, self.registry, ROOT)

    def test_valid_authored_map_is_not_scientific_pass(self):
        self.assertEqual(self.errors(), [])
        self.assertEqual(self.policy['current']['gate_p'], 'NOT_RUN')
        self.assertFalse(self.policy['current']['allow_consumer_integration'])

    def test_missing_original_id_rejected(self):
        self.mapping['rows'].pop()
        self.assertTrue(self.errors())

    def test_duplicate_original_id_rejected(self):
        self.mapping['rows'][1] = copy.deepcopy(self.mapping['rows'][0])
        self.assertTrue(self.errors())

    def test_rewritten_source_description_rejected(self):
        self.mapping['rows'][7]['original']['test'] = 'material threshold only, ignore Doppler'
        self.assertTrue(self.errors())

    def test_consumer_scope_relabeled_material_rejected(self):
        self.mapping['rows'][3]['scope'] = 'MATERIAL_LIBRARY'
        self.mapping['rows'][3]['gate_p_required'] = True
        self.assertTrue(self.errors())

    def test_material_subcheck_cannot_pass_full_original(self):
        self.mapping['rows'][7]['original_full_execution'] = 'PASS'
        self.assertTrue(self.errors())

    def test_false_gate_p_pass_without_execution_rejected(self):
        self.policy['current']['gate_p'] = 'PASS'
        self.assertTrue(self.errors())

    def test_false_tested_sha_rejected(self):
        self.policy['current']['tested_commit_sha'] = 'f' * 40
        self.assertTrue(self.errors())

    def test_premature_consumer_permission_rejected(self):
        self.policy['current']['allow_consumer_integration'] = True
        self.assertTrue(self.errors())

    def test_invented_test_symbol_rejected(self):
        self.mapping['rows'][0]['rust_tests'][0]['symbol'] = 'this_test_was_not_written'
        self.assertTrue(self.errors())

    def test_invented_fixture_group_rejected(self):
        self.mapping['rows'][0]['parity_groups'].append('nonexistent_fixture_group')
        self.assertTrue(self.errors())

    def test_invented_observable_rejected(self):
        self.mapping['rows'][1]['observable_keys'].append('nonexistent_quantum_observable')
        self.assertTrue(self.errors())

    def test_invented_fixture_id_rejected(self):
        self.registry['groups']['signed_event_columns'].append('nonexistent_record')
        self.assertTrue(self.errors())

    def test_source_identity_mismatch_rejected(self):
        self.mapping['rows'][0]['source_refs'][0]['sha256'] = '0' * 64
        self.assertTrue(self.errors())

    def test_wrong_target_command_rejected(self):
        self.policy['required_commands'][1][3] = 'rust/bianchi_rustcore/Cargo.toml'
        self.assertTrue(self.errors())

    def test_recorded_reference_error_cannot_become_zero(self):
        item = next(x for x in self.registry['records'] if x['expected_status'] == 'MissingAuthority')
        item['expected_status'] = 'ok'
        self.assertTrue(self.errors())

    def test_missing_review_gate_rejected(self):
        self.mapping['rows'][12]['local_audit_required'] = False
        self.assertTrue(self.errors())

    def test_helper_is_not_an_executed_rust_test(self):
        self.mapping['rows'][0]['rust_tests'][0]['symbol'] = 't5_state'
        self.assertTrue(self.errors())

if __name__ == '__main__':
    unittest.main(verbosity=2)
