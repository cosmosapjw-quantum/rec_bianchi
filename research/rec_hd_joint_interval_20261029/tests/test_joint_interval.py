from __future__ import annotations
import copy
from decimal import Decimal
from fractions import Fraction as F
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from joint_interval import (decimal_token, exact, extract_pinned_lamda, half_quantum,
                            reachability, segment_certificate, source_certificate,
                            source_model, SOURCE_SHA256)
FIXTURE = json.loads((ROOT / 'source_literals.json').read_text())


class JointIntervalTests(unittest.TestCase):
    def assertWitness(self, d, r, s, out):
        self.assertTrue(out['feasible'])
        lam, x, y = out['scale'], out['x'], out['y']
        self.assertTrue(all(abs(v) <= lam * radius for v, radius in zip(x, r)))
        self.assertTrue(all(abs(v) <= lam * radius for v, radius in zip(y, s)))
        self.assertTrue(all(d[j] + x[j+1] - x[j] == y[j] for j in range(len(d))))

    def test_local_pass_global_fail(self):
        d, r, s = [F(1), F(1)], [F(1, 2)] * 3, [F(0)] * 2
        self.assertTrue(all(abs(d[j]) <= r[j] + r[j+1] + s[j] for j in range(2)))
        self.assertFalse(reachability(d, r, s)['feasible'])
        cert = segment_certificate(d, r, s)
        self.assertEqual(cert['lambda_min'], F(2))
        self.assertEqual([(x['p'], x['q']) for x in cert['maximizing_segments']], [(0, 2)])
        self.assertWitness(d, r, s, reachability(d, r, s, cert['lambda_min']))

    def test_cancellation_and_closed_boundary(self):
        d, r, s = [F(1), F(-1)], [F(1, 2)] * 3, [F(0)] * 2
        self.assertWitness(d, r, s, reachability(d, r, s))
        self.assertEqual(segment_certificate(d, r, s)['lambda_min'], 1)
        self.assertFalse(reachability(d, r, s, F(999, 1000))['feasible'])

    def test_zero_denominator_obstruction(self):
        self.assertFalse(reachability([1], [0, 0], [0])['feasible'])
        cert = segment_certificate([1], [0, 0], [0])
        self.assertEqual(cert['minimum_scale_kind'], 'INFINITE')
        self.assertIsNone(cert['lambda_min'])
        self.assertFalse(reachability([1], [0, 0], [0], 10**10)['feasible'])

    def test_zero_defect_zero_radius(self):
        self.assertWitness([F(0)], [F(0), F(0)], [F(0)], reachability([0], [0, 0], [0], 0))
        self.assertEqual(segment_certificate([0], [0, 0], [0])['lambda_min'], 0)

    def test_zero_edge_model(self):
        out = reachability([], [2], [], 0)
        self.assertEqual(out['x'], [F(0)])
        self.assertEqual(segment_certificate([], [2], [])['lambda_min'], 0)
        self.assertEqual(segment_certificate([], [2], [])['segment_count'], 0)

    def test_unrounded_line_interval_can_absorb_defect(self):
        d, r, s = [F(3)], [F(0), F(0)], [F(3)]
        self.assertWitness(d, r, s, reachability(d, r, s))
        self.assertEqual(segment_certificate(d, r, s)['lambda_min'], 1)

    def test_actual_fixed_literals(self):
        d, r, s = source_model(FIXTURE)
        self.assertEqual(d[5], F('-1827572.5607572'))
        self.assertEqual(r[0] + r[1] + s[0], F('34.9792458'))
        nominal = reachability(d, r, s)
        self.assertFalse(nominal['feasible'])
        self.assertEqual(nominal['first_empty_level'], 2)
        cert = segment_certificate(d, r, s)
        self.assertEqual(cert['segment_count'], 36)
        self.assertEqual(cert['lambda_min'], F(9137862803786, 174896229))
        self.assertEqual([(v['p'], v['q']) for v in cert['maximizing_segments']], [(5, 6)])
        self.assertWitness(d, r, s, reachability(d, r, s, cert['lambda_min']))
        self.assertFalse(reachability(d, r, s, cert['lambda_min'] - F(1, 10**9))['feasible'])

    def test_default_fixture_does_not_claim_raw_execution(self):
        c = source_certificate(FIXTURE)
        self.assertFalse(c['source_identity']['raw_verified_this_execution'])
        self.assertEqual(c['source_identity']['input_mode'], 'EXTRACTED_LITERAL_FIXTURE_ONLY')
        self.assertFalse(c['physical_admission'])
        self.assertEqual(c['rowwise_fail_count'], 7)
        self.assertTrue(all(v == 0 for v in c['minimum_scale_witness']['equality_residuals']))

    def test_raw_hash_rejects_changed_byte(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / 'wrong.dat'
            path.write_bytes(b'not the pinned source')
            with self.assertRaisesRegex(ValueError, 'size/SHA256'):
                extract_pinned_lamda(path)

    def test_fixture_pin_and_labels_rejected(self):
        for key, value in [('source_sha256', '0'*64), ('source_bytes', 2288)]:
            fixture = copy.deepcopy(FIXTURE); fixture[key] = value
            with self.assertRaises(ValueError): source_certificate(fixture)
        fixture = copy.deepcopy(FIXTURE);fixture['levels'][2]['J'] = 3
        with self.assertRaises(ValueError): source_model(fixture)
        fixture = copy.deepcopy(FIXTURE);fixture['radiative_lines'][0]['nu_GHz'] = '-1.00'
        with self.assertRaises(ValueError): source_model(fixture)

    def test_decimal_precision_keeps_trailing_zeros(self):
        self.assertEqual(half_quantum('123.4500'), F(1, 20000))
        self.assertEqual(half_quantum('1.20e3'), F(5))
        self.assertEqual(exact('1/3'), F(1, 3))
        self.assertEqual(exact(Decimal('0.1')), F(1, 10))

    def test_nonfinite_malformed_and_inexact_rejected(self):
        for value in ('Infinity', '-Infinity', 'NaN', 'sNaN', 'abc', ' 1.00', '', '1_000'):
            with self.subTest(value=value):
                with self.assertRaises(ValueError): decimal_token(value)
        for value in (float('inf'), .1, True, Decimal('NaN'), '1/0'):
            with self.subTest(value=repr(value)):
                with self.assertRaises(ValueError): exact(value)
        for func in (reachability, segment_certificate):
            with self.assertRaises(ValueError): func([0], [1, 1], [1], -1)
            with self.assertRaises(ValueError): func([0], [1, -1], [1])
            with self.assertRaises(ValueError): func([0], [1], [1])

    def test_cli_fresh_output_directory(self):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / 'fresh' / 'certificate.json'
            p = subprocess.run([sys.executable, str(ROOT/'joint_interval.py'), '--output', str(out)], capture_output=True, text=True)
            self.assertEqual(p.returncode, 0, p.stderr)
            c = json.loads(out.read_text())
            self.assertEqual(c['all_segments']['lambda_min'], '9137862803786/174896229')
            self.assertFalse(c['source_identity']['raw_verified_this_execution'])

if __name__ == '__main__': unittest.main()
