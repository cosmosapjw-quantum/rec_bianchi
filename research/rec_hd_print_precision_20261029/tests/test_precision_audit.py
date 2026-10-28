import copy
import hashlib
from decimal import Decimal
import json
from pathlib import Path
import sys
import tempfile
import unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from precision_audit import audit, half_quantum, parse_spcat_line, verify_cdms_file

S=json.loads((ROOT/'public_print_transcription.json').read_text())

class TestConditionalPrintedPrecision(unittest.TestCase):
    def test_original_eight_gate(self):
        r=audit(S['levels'],S['radiative_lines'])
        self.assertEqual(r['rounding_only_fail_count'],7)
        self.assertTrue(r['print_rows'][0]['classification'].startswith('PASS'))
        self.assertEqual([x['j_up'] for x in r['print_rows'] if x['classification'].startswith('FAIL')],list(range(2,9)))
        self.assertEqual(r['print_rows'][0]['delta_Hz'],'-8.241016200')
    def test_exact_row_6(self):
        r=audit(S['levels'],S['radiative_lines'])
        self.assertEqual(r['print_rows'][5]['delta_Hz'],'-1827572.560757200')
    def test_row8_minimum_excess(self):
        r=audit(S['levels'],S['radiative_lines'])
        self.assertEqual(Decimal(r['print_rows'][7]['minimum_nonrounding_excess_Hz']),Decimal('6830.010377'))
    def test_bound_from_decimals(self):
        r=audit(S['levels'],S['radiative_lines'])
        self.assertEqual(Decimal(r['print_rows'][3]['nearest_rounding_bound_Hz']),Decimal('34.9792458'))
        self.assertEqual(str(half_quantum('123.4500')),'0.00005')
    def test_wrong_j_rejected(self):
        x=copy.deepcopy(S)
        x['radiative_lines'][2]['J_up']=8
        with self.assertRaises(ValueError): audit(x['levels'],x['radiative_lines'])
    def test_frequency_sign_mutation_detected(self):
        x=copy.deepcopy(S)
        x['radiative_lines'][0]['nu_GHz']='-2674.98609400'
        with self.assertRaises(ValueError): audit(x['levels'],x['radiative_lines'])
    def test_truncation_adversarial_control(self):
        r=audit(S['levels'],S['radiative_lines'])
        self.assertEqual(sum(Decimal(x['minimum_nontruncation_excess_Hz'])>0 for x in r['print_rows']),7)
        self.assertGreater(Decimal(r['print_rows'][7]['minimum_nontruncation_excess_Hz']),Decimal(6000))
    def test_cdms_format_measured_tag(self):
        def cat_row(tag):
            # SPCAT F13.4 2F8.4 I2 F10.4 I3 I7 I4 plus qn text
            return f'{2674986.0000:13.4f}{0.0300:8.4f}{-9.1234:8.4f}{2:2d}{0.0:10.4f}{3:3d}{tag:7d}{101:4d}'+('  1  0'.ljust(24))
        self.assertTrue(parse_spcat_line(cat_row(-3501))['measured_tag'])
        self.assertFalse(parse_spcat_line(cat_row(3501))['measured_tag'])
        with self.assertRaises(ValueError): parse_spcat_line('short')
    def test_affinity_sign_intervals(self):
        r=audit(S['levels'],S['radiative_lines'])
        for row in r['print_rows']:
            a,b=map(Decimal,row['formal_source_affinity_intervals']['50'])
            self.assertLess(a,b)
            if row['classification'].startswith('FAIL'):
                self.assertTrue(a*b>0)
    def test_source_hash_gate(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'test.cat'
            path.write_text('  not a catalog\n')
            with self.assertRaises(ValueError): verify_cdms_file(path,None)
            with self.assertRaises(ValueError): verify_cdms_file(path,'a'*64)

if __name__=='__main__': unittest.main()
